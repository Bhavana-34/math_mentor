import json
import re
from typing import List, Dict, Optional


def _st_secret(key: str) -> str:
    """Safely read one key from st.secrets (Streamlit Cloud secrets store)."""
    try:
        import streamlit as st
        # Use direct key access, not .get(), for full compatibility
        if key in st.secrets:
            return str(st.secrets[key]).strip()
    except Exception:
        pass
    return ""


def _load_config():
    import os
    # 1. Load .env for local development
    try:
        from dotenv import load_dotenv
        from pathlib import Path
        load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=True)
    except ImportError:
        pass

    # 2. os.environ — works locally AND on Streamlit Cloud (secrets are env vars too)
    def _get(key: str, default: str = "") -> str:
        return os.environ.get(key, "").strip() or _st_secret(key) or default

    return {
        "provider":       _get("LLM_PROVIDER", "groq"),
        "groq_key":       _get("GROQ_API_KEY"),
        "groq_model":     _get("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "deepseek_key":   _get("DEEPSEEK_API_KEY"),
        "deepseek_model": _get("DEEPSEEK_MODEL", "deepseek-chat"),
    }


# Do NOT cache globally — re-create each session so a new secret is picked up
# after Streamlit Cloud reboots without needing a code push.
_client = None
_client_key = None   # track which api_key the current client was built with


def get_client():
    global _client, _client_key

    cfg = _load_config()
    provider = cfg["provider"]

    if provider == "groq":
        api_key = cfg["groq_key"]
        if not api_key:
            # List available secret keys (no values) to help diagnose typos
            hint = ""
            try:
                import streamlit as st
                hint = f" (secrets present: {list(st.secrets.keys())})"
            except Exception:
                pass
            raise ValueError(
                f"GROQ_API_KEY is not set{hint}.\n"
                "Fix: Streamlit Cloud → Manage app → Settings → Secrets → add:\n"
                "  GROQ_API_KEY = \"gsk_...\"\n"
                "Free key at https://console.groq.com"
            )
        # Rebuild client only when the key actually changes
        if _client is None or _client_key != api_key:
            from groq import Groq
            _client = Groq(api_key=api_key)
            _client_key = api_key

    elif provider == "deepseek":
        api_key = cfg["deepseek_key"]
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY is not set.\n"
                "Fix: Streamlit Cloud → Manage app → Settings → Secrets → add:\n"
                "  DEEPSEEK_API_KEY = \"sk_...\"\n"
                "Free key at https://platform.deepseek.com"
            )
        if _client is None or _client_key != api_key:
            from openai import OpenAI
            _client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
            _client_key = api_key
    else:
        raise ValueError(f"Unknown LLM_PROVIDER '{provider}'. Use 'groq' or 'deepseek'.")

    return _client


def get_model() -> str:
    cfg = _load_config()
    if cfg["provider"] == "groq":
        return cfg["groq_model"]
    return cfg["deepseek_model"]


def chat_completion(
    messages: List[Dict],
    model: str = None,
    temperature: float = 0.2,
    max_tokens: int = 2000,
    response_format: Optional[str] = None,
) -> str:
    client = get_client()
    active_model = model or get_model()

    kwargs = {
        "model": active_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    if response_format == "json":
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    except Exception as e:
        err = str(e).lower()
        if "response_format" in err or "json_object" in err:
            kwargs.pop("response_format", None)
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        raise


def parse_json_response(text: str) -> Dict:
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    cleaned = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}