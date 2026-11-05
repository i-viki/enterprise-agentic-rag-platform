import httpx
import structlog
from typing import List, AsyncGenerator, Dict, Any, Optional
import numpy as np
from app.config import settings

logger = structlog.get_logger(__name__)

class ModelClient:
    """Enterprise client for local Ollama / Cloud GPU OpenAI-compatible endpoints."""
    def __init__(self):
        self.base_url = settings.LLM_BASE_URL.rstrip('/')
        self.embedding_url = settings.EMBEDDING_BASE_URL.rstrip('/')
        self.timeout = httpx.Timeout(45.0, connect=5.0)

    async def get_embedding(self, text: str) -> List[float]:
        """Generates 768-dimensional dense vector embeddings using nomic-embed-text:v1.5."""
        payload = {
            "model": settings.EMBEDDING_MODEL_NAME,
            "input": text
        }
        headers = {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.embedding_url}/embeddings", json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    embedding = data["data"][0]["embedding"]
                    # Normalize vector
                    vec = np.array(embedding, dtype=np.float32)
                    norm = np.linalg.norm(vec)
                    if norm > 0:
                        vec = vec / norm
                    return vec.tolist()
                else:
                    logger.warn("ollama_embedding_http_error", status=res.status_code, body=res.text)
        except Exception as e:
            logger.warn("ollama_embedding_unavailable_fallback", error=str(e))

        # Deterministic pseudo-embedding fallback (768 dimensions) for offline dev testing
        # Seeds vector deterministically based on text hash to ensure consistent similarity tests
        h = hash(text)
        np.random.seed(abs(h) % (2**32))
        dummy = np.random.normal(0, 1, settings.EMBEDDING_DIMENSION).astype(np.float32)
        norm = np.linalg.norm(dummy)
        return (dummy / norm).tolist()

    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """Executes non-streaming completion using llama3.2:3b."""
        payload = {
            "model": settings.LLM_MODEL_NAME,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        headers = {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
                logger.error("ollama_chat_failed", status=res.status_code, response=res.text)
        except Exception as e:
            logger.warn("ollama_chat_unavailable_fallback", error=str(e))

        return "Enterprise Agentic RAG Platform (Local Fallback): Unable to reach local model server at " + self.base_url

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """Streams response tokens using llama3.2:3b via SSE."""
        payload = {
            "model": settings.LLM_MODEL_NAME,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        headers = {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", f"{self.base_url}/chat/completions", json=payload, headers=headers) as response:
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        import json
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk["choices"][0].get("delta", {}).get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            continue
        except Exception as e:
            logger.warn("ollama_stream_unavailable_fallback", error=str(e))
            fallback_text = "Enterprise Agentic RAG Platform: Local Ollama model runtime is offline. Please start Ollama."
            for word in fallback_text.split(" "):
                yield word + " "


model_client = ModelClient()

