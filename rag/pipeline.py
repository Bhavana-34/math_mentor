import os
import pickle
from typing import List, Tuple
from pathlib import Path

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from config import KNOWLEDGE_BASE_PATH, VECTOR_STORE_PATH, TOP_K_RETRIEVAL, EMBEDDING_MODEL

_embed_model = None


def get_embed_model():
    global _embed_model
    if _embed_model is None:
        if not ST_AVAILABLE:
            raise ImportError("Run: pip install sentence-transformers")
        _embed_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embed_model


class RAGPipeline:
    def __init__(self):
        self.chunks: List[dict] = []
        self.embeddings: np.ndarray = None
        self.index = None
        self.store_path = Path(VECTOR_STORE_PATH)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self._load_or_build()

    def _load_knowledge_base(self) -> List[dict]:
        docs = []
        kb_path = Path(KNOWLEDGE_BASE_PATH)
        if not kb_path.exists():
            return docs
        for file_path in sorted(kb_path.glob("*.txt")):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            chunks = self._chunk_text(content, source=file_path.name)
            docs.extend(chunks)
        return docs

    def _chunk_text(self, text: str, source: str, chunk_size: int = 500, overlap_lines: int = 3) -> List[dict]:
        chunks = []
        lines = text.split("\n")
        current: List[str] = []
        current_len = 0
        for line in lines:
            if current_len + len(line) > chunk_size and current:
                chunk_text = "\n".join(current).strip()
                if chunk_text:
                    chunks.append({"text": chunk_text, "source": source})
                current = current[-overlap_lines:] + [line]
                current_len = sum(len(l) for l in current)
            else:
                current.append(line)
                current_len += len(line)
        if current:
            chunk_text = "\n".join(current).strip()
            if chunk_text:
                chunks.append({"text": chunk_text, "source": source})
        return chunks

    def _embed(self, texts: List[str]) -> np.ndarray:
        model = get_embed_model()
        return model.encode(texts, convert_to_numpy=True, show_progress_bar=False).astype(np.float32)

    def _build_index(self):
        self.chunks = self._load_knowledge_base()
        if not self.chunks:
            self.index = None
            return
        texts = [c["text"] for c in self.chunks]
        self.embeddings = self._embed(texts)
        if FAISS_AVAILABLE:
            dim = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)
            self.index.add(self.embeddings)
        self._save_index()

    def _save_index(self):
        with open(self.store_path / "chunks.pkl", "wb") as f:
            pickle.dump(self.chunks, f)
        if self.embeddings is not None:
            np.save(str(self.store_path / "embeddings.npy"), self.embeddings)
        if self.index is not None and FAISS_AVAILABLE:
            faiss.write_index(self.index, str(self.store_path / "index.faiss"))

    def _load_or_build(self):
        chunks_path = self.store_path / "chunks.pkl"
        embeddings_path = self.store_path / "embeddings.npy"
        index_path = self.store_path / "index.faiss"
        if chunks_path.exists() and embeddings_path.exists():
            with open(chunks_path, "rb") as f:
                self.chunks = pickle.load(f)
            self.embeddings = np.load(str(embeddings_path))
            if index_path.exists() and FAISS_AVAILABLE:
                self.index = faiss.read_index(str(index_path))
        else:
            self._build_index()

    def rebuild_index(self):
        self._build_index()

    def retrieve(self, query: str, top_k: int = TOP_K_RETRIEVAL) -> List[dict]:
        if not self.chunks:
            return []
        query_emb = self._embed([query])
        if self.index is not None and FAISS_AVAILABLE:
            distances, indices = self.index.search(query_emb, min(top_k, len(self.chunks)))
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if 0 <= idx < len(self.chunks):
                    chunk = self.chunks[idx].copy()
                    chunk["score"] = float(1 / (1 + dist))
                    results.append(chunk)
            return results
        else:
            if self.embeddings is None:
                return []
            scores = np.dot(self.embeddings, query_emb.T).flatten()
            top_indices = np.argsort(scores)[::-1][:top_k]
            results = []
            for idx in top_indices:
                chunk = self.chunks[idx].copy()
                chunk["score"] = float(scores[idx])
                results.append(chunk)
            return results

    def get_context_string(self, query: str, top_k: int = TOP_K_RETRIEVAL) -> Tuple[str, List[dict]]:
        chunks = self.retrieve(query, top_k)
        if not chunks:
            return "", []
        context = "\n\n---\n\n".join(
            f"[Source: {c['source']}]\n{c['text']}" for c in chunks
        )
        return context, chunks