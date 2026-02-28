import json
import os
import re
from typing import List, Dict, Optional

import config

_client = None


def _resolve_secret(key: str) -> str:
    """Read a secret at runtime: env vars first, then st.secrets (Streamlit Cloud)."""
    # 1. os.environ is always fresh (Streamlit Cloud injects secrets as env vars)
    val = os.environ.get(key, "")
    if val:
        return val
    # 2. st.secrets — explicit Streamlit secrets store
    try:
        import streamlit as st
        val = st.secrets.get(key, "")
        if val:
            return val
    except Exception:
        pass
    # 3. Fall back to whatever config parsed at startup
    return getattr(config, key, "") or ""


def get_client():
    global _client
    # Re-resolve every call so a newly added secret is picked up without restart
    provider = _resolve_secret("LLM_PROVIDER") or config.LLM_PROVIDER

    # If we already have a client for this provider, reuse it
    if _client is not None:
        return _client

    if provider == "groq":
        api_key = _resolve_secret("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not set. "
                "Add it to Streamlit Cloud Secrets (Manage app → Settings → Secrets) "
                "or to a local .env file. Free key at https://console.groq.com"
            )
        try:
            from groq import Groq
            _client = Groq(api_key=api_key)
        except ImportError:
            raise ImportError("Run: pip install groq")

    elif provider == "deepseek":
        api_key = _resolve_secret("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY not set. "
                "Add it to Streamlit Cloud Secrets or a local .env file. "
                "Free key at https://platform.deepseek.com"
            )
        try:
            from openai import OpenAI
            _client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1",
            )
        except ImportError:
            raise ImportError("Run: pip install openai")
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}. Use 'groq' or 'deepseek'.")

    return _client


def chat_completion(
    messages: List[Dict],
    model: str = None,
    temperature: float = 0.2,
    max_tokens: int = 2000,
    response_format: Optional[str] = None,
) -> str:
    client = get_client()
    active_model = model or config.LLM_MODEL

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