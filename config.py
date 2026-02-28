import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _get(key: str, default: str = "") -> str:
    val = os.getenv(key, default)
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return default


# --- API Keys ---
GROQ_API_KEY = _get("GROQ_API_KEY", "")
DEEPSEEK_API_KEY = _get("DEEPSEEK_API_KEY", "")

# --- Provider selection: "groq" or "deepseek" ---
LLM_PROVIDER = _get("LLM_PROVIDER", "groq")

# --- Models ---
# Groq free models: llama-3.3-70b-versatile, llama3-8b-8192, mixtral-8x7b-32768
# DeepSeek free models: deepseek-chat, deepseek-reasoner
GROQ_MODEL = _get("GROQ_MODEL", "llama-3.3-70b-versatile")
DEEPSEEK_MODEL = _get("DEEPSEEK_MODEL", "deepseek-chat")

# Active model name (used throughout)
LLM_MODEL = GROQ_MODEL if LLM_PROVIDER == "groq" else DEEPSEEK_MODEL

# --- Embeddings: use sentence-transformers locally (no API key needed) ---
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # runs 100% locally, free forever

# --- Thresholds ---
OCR_CONFIDENCE_THRESHOLD = float(_get("OCR_CONFIDENCE_THRESHOLD", "0.6"))
ASR_CONFIDENCE_THRESHOLD = float(_get("ASR_CONFIDENCE_THRESHOLD", "0.7"))
VERIFIER_CONFIDENCE_THRESHOLD = float(_get("VERIFIER_CONFIDENCE_THRESHOLD", "0.75"))

# --- Paths ---
MEMORY_DB_PATH = _get("MEMORY_DB_PATH", "./memory/memory.json")
VECTOR_STORE_PATH = _get("VECTOR_STORE_PATH", "./rag/vector_store")
KNOWLEDGE_BASE_PATH = _get("KNOWLEDGE_BASE_PATH", "./knowledge_base")
TOP_K_RETRIEVAL = 5

Path(MEMORY_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
Path(VECTOR_STORE_PATH).mkdir(parents=True, exist_ok=True)