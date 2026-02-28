import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)
except ImportError:
    pass


def _get(key: str, default: str = "") -> str:
    # 1. Check environment variables first
    val = os.environ.get(key, "")
    if val:
        return val
    # 2. Check Streamlit secrets
    try:
        import streamlit as st
        val = st.secrets.get(key, "")
        if val:
            return str(val)
    except Exception:
        pass
    return default


LLM_PROVIDER = _get("LLM_PROVIDER", "groq")
GROQ_API_KEY = _get("GROQ_API_KEY", "")
DEEPSEEK_API_KEY = _get("DEEPSEEK_API_KEY", "")
GROQ_MODEL = _get("GROQ_MODEL", "llama-3.3-70b-versatile")
DEEPSEEK_MODEL = _get("DEEPSEEK_MODEL", "deepseek-chat")
LLM_MODEL = GROQ_MODEL if LLM_PROVIDER == "groq" else DEEPSEEK_MODEL
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OCR_CONFIDENCE_THRESHOLD = float(_get("OCR_CONFIDENCE_THRESHOLD", "0.6"))
ASR_CONFIDENCE_THRESHOLD = float(_get("ASR_CONFIDENCE_THRESHOLD", "0.7"))
VERIFIER_CONFIDENCE_THRESHOLD = float(_get("VERIFIER_CONFIDENCE_THRESHOLD", "0.75"))
MEMORY_DB_PATH = _get("MEMORY_DB_PATH", "./memory/memory.json")
VECTOR_STORE_PATH = _get("VECTOR_STORE_PATH", "./rag/vector_store")
KNOWLEDGE_BASE_PATH = _get("KNOWLEDGE_BASE_PATH", "./knowledge_base")
TOP_K_RETRIEVAL = 5

Path(MEMORY_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
Path(VECTOR_STORE_PATH).mkdir(parents=True, exist_ok=True)