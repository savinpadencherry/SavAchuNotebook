"""
Lightweight Ollama embeddings wrapper compatible with LangChain vector stores.

Uses the local Ollama server to generate embeddings, avoiding
sentence-transformers/Hugging Face dependencies.

Model default: all-minilm:22m (embedding model)
"""

from typing import List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed


class OllamaEmbeddingsLocal:
    """
    Minimal embeddings interface used by LangChain vector stores like Chroma.

    Implements:
    - embed_documents(texts: List[str]) -> List[List[float]]
    - embed_query(text: str) -> List[float]
    """

    def __init__(self, model: str = "all-minilm:22m", base_url: Optional[str] = None, timeout: int = 120, max_workers: int = 4):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.max_workers = max(1, int(max_workers))

        # Lazy import to keep import-time light and provide clear errors
        try:
            import ollama  # noqa: F401
        except Exception as e:
            raise ImportError(
                "Ollama Python package is required. Install with: pip install ollama\n"
                "Also ensure the Ollama server is running: ollama serve\n"
                f"Import error: {e}"
            )

    def _client(self):
        # Create a client each call to respect optional base_url without global state
        from ollama import Client
        return Client(host=self.base_url) if self.base_url else Client()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Parallelize embedding calls for better throughput
        def _embed_one(idx_text: Tuple[int, str]) -> Tuple[int, List[float]]:
            idx, text = idx_text
            client = self._client()
            prompt = text if isinstance(text, str) else ""
            resp = client.embeddings(model=self.model, prompt=prompt)
            return idx, resp.get("embedding", [])

        indices_texts = list(enumerate(texts))
        results: List[Tuple[int, List[float]]] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = [ex.submit(_embed_one, it) for it in indices_texts]
            for fut in as_completed(futures):
                results.append(fut.result())

        # Restore original order
        results.sort(key=lambda x: x[0])
        return [emb for _, emb in results]

    def embed_query(self, text: str) -> List[float]:
        client = self._client()
        prompt = text if isinstance(text, str) else ""
        resp = client.embeddings(model=self.model, prompt=prompt)
        return resp.get("embedding", [])
