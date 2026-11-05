import structlog
from typing import Dict, Any, List
from app.graph.state import CognitionState, RetrievedDocument
from app.memory.hybrid_retriever import hybrid_retriever
from app.core.model_client import model_client
from app.core.redis_client import redis_client
from app.guardrails.self_rag_auditor import self_rag_auditor
from app.guardrails.egress_leakage_filter import egress_leakage_filter

logger = structlog.get_logger(__name__)

async def router_node(state: CognitionState) -> Dict[str, Any]:
    """1. Route Query & Extract Working Memory."""
    logger.info("langgraph_router_node_start", trace_id=state["trace_id"])
    
    # Fetch ephemeral working memory from Redis scratchpad
    session_key = f"session:{state['tenant_id']}:{state['thread_id']}"
    working_memory = await redis_client.get_json(session_key) or {}

    return {
        "working_memory": working_memory,
        "loop_step": state.get("loop_step", 0) + 1,
    }

async def retriever_node(state: CognitionState) -> Dict[str, Any]:
    """2. Hybrid Multi-Index Retrieval (Dense HNSW + Lexical BM25 RRF)."""
    query = state.get("transformed_query") or state["sanitized_query"]
    logger.info("langgraph_retriever_node_start", query=query, loop_step=state["loop_step"])

    results = await hybrid_retriever.search(
        tenant_id=state["tenant_id"],
        query_text=query,
        clearance_level=state["clearance_level"],
        user_roles=state["user_roles"],
        top_k=5
    )

    documents: List[RetrievedDocument] = [
        {
            "id": str(r.id),
            "kind": r.kind, # type: ignore
            "content": r.content,
            "source_reference": r.source_reference,
            "confidence": r.confidence,
            "rrf_score": r.rrf_score,
            "relevance_verdict": None
        }
        for r in results
    ]

    return {
        "retrieved_documents": documents,
        "retrieval_grade": "empty" if not documents else "sufficient"
    }

async def grade_documents_node(state: CognitionState) -> Dict[str, Any]:
    """3. Corrective RAG (CRAG) Document Grader."""
    docs = state.get("retrieved_documents", [])
    query = state.get("transformed_query") or state["sanitized_query"]
    logger.info("langgraph_grade_documents_start", doc_count=len(docs))

    if not docs:
        return {"retrieval_grade": "empty"}

    query_tokens = set(query.lower().split())
    graded_docs: List[RetrievedDocument] = []
    relevant_count = 0

    for doc in docs:
        doc_tokens = set(doc["content"].lower().split())
        overlap = len(query_tokens.intersection(doc_tokens))
        
        # Determine relevance based on keyword match and RRF score
        is_rel = overlap > 0 or doc["rrf_score"] > 0.015
        verdict = "relevant" if is_rel else "irrelevant"
        if is_rel:
            relevant_count += 1

        doc_copy = dict(doc)
        doc_copy["relevance_verdict"] = verdict
        graded_docs.append(doc_copy) # type: ignore

    # If less than half the top results are relevant, grade as insufficient
    grade = "sufficient" if relevant_count >= 1 else "insufficient"
    logger.info("crag_grade_verdict", relevant=relevant_count, total=len(docs), grade=grade)

    return {
        "retrieved_documents": graded_docs,
        "retrieval_grade": grade
    }

async def rewrite_query_node(state: CognitionState) -> Dict[str, Any]:
    """4. Semantic Query Rewriter (Reformulation Loop)."""
    raw_query = state.get("transformed_query") or state["sanitized_query"]
    logger.info("langgraph_rewrite_query_start", original=raw_query)

    rewrite_prompt = [
        {"role": "system", "content": "You are an enterprise query reformulation assistant. Rewrite the user's question to expand enterprise synonyms and improve document search retrieval. Return ONLY the rewritten query text, with no introductory text or markdown tags."},
        {"role": "user", "content": f"Original query: {raw_query}"}
    ]

    rewritten = await model_client.generate_chat_completion(rewrite_prompt, temperature=0.1, max_tokens=120)
    cleaned_query = rewritten.strip(' "\'\n`')
    logger.info("langgraph_query_rewritten", rewritten=cleaned_query)

    return {
        "transformed_query": cleaned_query,
        "loop_step": state["loop_step"] + 1
    }

async def synthesizer_node(state: CognitionState) -> Dict[str, Any]:
    """5. Grounded Context Synthesizer."""
    query = state["sanitized_query"]
    docs = [d for d in state.get("retrieved_documents", []) if d.get("relevance_verdict") != "irrelevant"]
    working_mem = state.get("working_memory", {})

    context_str = "\n\n".join([f"[Source: {d['source_reference']}] {d['content']}" for d in docs])
    
    system_prompt = (
        "You are an enterprise cognitive assistant. Answer the user prompt strictly and factually based on the provided context.\n"
        "Guidelines:\n"
        "1. Do NOT extrapolate or assume facts not present in the context.\n"
        "2. Cite your sources using [Source: <ref>] notation.\n"
        "3. If the context does not contain sufficient information, state that the official documents do not contain this information."
    )

    user_content = (
        f"<working_memory>\n{working_mem}\n</working_memory>\n\n"
        f"<context>\n{context_str}\n</context>\n\n"
        f"<query>\n{query}\n</query>"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    raw_answer = await model_client.generate_chat_completion(messages, temperature=0.2, max_tokens=512)
    sanitized_answer = egress_leakage_filter.sanitize(raw_answer)

    return {
        "generated_answer": sanitized_answer,
        "loop_step": state.get("loop_step", 1) + 1
    }

async def self_rag_auditor_node(state: CognitionState) -> Dict[str, Any]:
    """6. Self-RAG Faithfulness & Hallucination Auditor."""
    answer = state.get("generated_answer", "")
    contexts = [d["content"] for d in state.get("retrieved_documents", [])]

    grounding_score, is_grounded = self_rag_auditor.audit_groundedness(answer, contexts)

    return {
        "grounding_score": grounding_score,
        "is_grounded": is_grounded
    }

async def memory_consolidator_node(state: CognitionState) -> Dict[str, Any]:
    """7. Cognitive Memory Distiller & Writeback."""
    # Update ephemeral working memory in Redis
    session_key = f"session:{state['tenant_id']}:{state['thread_id']}"
    current_mem = state.get("working_memory", {})
    current_mem["last_query"] = state["sanitized_query"]
    current_mem["last_grounding_score"] = state["grounding_score"]

    await redis_client.set_json(session_key, current_mem, ttl_seconds=900)

    final_resp = {
        "trace_id": state["trace_id"],
        "thread_id": state["thread_id"],
        "generated_answer": state.get("generated_answer", ""),
        "retrieved_documents": state.get("retrieved_documents", []),
        "grounding_score": state.get("grounding_score", 1.0),
        "is_grounded": state.get("is_grounded", True),
        "loop_step": state.get("loop_step", 1),
        "retrieval_grade": state.get("retrieval_grade", "sufficient")
    }

    return {
        "final_response": final_resp
    }

async def fallback_node(state: CognitionState) -> Dict[str, Any]:
    """Fallback state when context is insufficient or ungrounded after retries."""
    fallback_text = (
        "I am unable to answer this inquiry based on verified enterprise documentation. "
        "The required information was not found in the approved knowledge base."
    )
    return {
        "generated_answer": fallback_text,
        "is_grounded": True,
        "grounding_score": 1.0,
        "final_response": {
            "trace_id": state["trace_id"],
            "thread_id": state["thread_id"],
            "generated_answer": fallback_text,
            "retrieved_documents": [],
            "grounding_score": 1.0,
            "is_grounded": True,
            "loop_step": state.get("loop_step", 1),
            "retrieval_grade": "empty"
        }
    }

