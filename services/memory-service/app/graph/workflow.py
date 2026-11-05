from langgraph.graph import StateGraph, START, END
from app.graph.state import CognitionState
from app.graph.nodes import (
    router_node,
    retriever_node,
    grade_documents_node,
    rewrite_query_node,
    synthesizer_node,
    self_rag_auditor_node,
    memory_consolidator_node,
    fallback_node,
)
from app.graph.edges import evaluate_retrieval_adequacy, evaluate_groundedness_verdict
from app.graph.checkpointer import get_checkpointer

def build_agent_graph():
    """Assembles and compiles the Adaptive Corrective RAG (CRAG) StateGraph."""
    workflow = StateGraph(CognitionState)

    # 1. Register Nodes
    workflow.add_node("router", router_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("grade_documents", grade_documents_node)
    workflow.add_node("rewrite_query", rewrite_query_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("self_rag_auditor", self_rag_auditor_node)
    workflow.add_node("consolidate_memory", memory_consolidator_node)
    workflow.add_node("fallback", fallback_node)

    # 2. Build Edge Flow
    workflow.add_edge(START, "router")
    workflow.add_edge("router", "retriever")
    workflow.add_edge("retriever", "grade_documents")

    # Conditional branch after grading documents
    workflow.add_conditional_edges(
        "grade_documents",
        evaluate_retrieval_adequacy,
        {
            "synthesize": "synthesizer",
            "rewrite_query": "rewrite_query",
            "fallback": "fallback"
        }
    )

    workflow.add_edge("rewrite_query", "retriever")
    workflow.add_edge("synthesizer", "self_rag_auditor")

    # Conditional branch after Self-RAG groundedness check
    workflow.add_conditional_edges(
        "self_rag_auditor",
        evaluate_groundedness_verdict,
        {
            "consolidate": "consolidate_memory",
            "synthesize": "synthesizer",
            "fallback": "fallback"
        }
    )

    workflow.add_edge("consolidate_memory", END)
    workflow.add_edge("fallback", END)

    # Compile with thread checkpointer
    return workflow.compile(checkpointer=get_checkpointer())


agent_graph = build_agent_graph()

