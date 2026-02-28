from typing import Tuple

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

from config import ASR_CONFIDENCE_THRESHOLD

_whisper_model = None


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        if not WHISPER_AVAILABLE:
            raise ImportError(
                "openai-whisper not installed. "
                "Run: pip install openai-whisper  (also needs ffmpeg)"
            )
        _whisper_model = whisper.load_model("base")
    return _whisper_model


def transcribe_with_whisper_local(audio_path: str) -> Tuple[str, float]:
    try:
        model = _get_whisper_model()
        result = model.transcribe(audio_path)
        text = result.get("text", "").strip()
        segments = result.get("segments", [])
        if segments:
            avg_logprob = sum(s.get("avg_logprob", -1.0) for s in segments) / len(segments)
            conf = max(0.0, min(1.0, avg_logprob + 1.0))
        else:
            conf = 0.6 if text else 0.0
        return text, conf
    except ImportError as e:
        return str(e), 0.0
    except Exception as e:
        return f"Whisper error: {e}", 0.0


def normalize_math_speech(text: str) -> str:
    replacements = {
        "square root of": "sqrt(",
        "squared": "^2",
        "cubed": "^3",
        "raised to the power of": "^",
        "raised to": "^",
        "divided by": "/",
        "multiplied by": "*",
        "times": "*",
        "plus": "+",
        "minus": "-",
        "equals": "=",
        "pi": "π",
        "infinity": "∞",
        "log base": "log_",
        "natural log": "ln",
        "sine of": "sin(",
        "cosine of": "cos(",
        "tangent of": "tan(",
    }
    result = text.lower()
    for phrase, symbol in replacements.items():
        result = result.replace(phrase, symbol)
    return result


def transcribe_audio(audio_path: str) -> Tuple[str, float, bool]:
    if not WHISPER_AVAILABLE:
        return (
            "Audio transcription not available. "
            "Install with: pip install openai-whisper  (also needs ffmpeg). "
            "You can type the problem manually instead.",
            0.0,
            True,
        )
    text, conf = transcribe_with_whisper_local(audio_path)
    text = normalize_math_speech(text)
    needs_hitl = conf < ASR_CONFIDENCE_THRESHOLD
    return text, conf, needs_hitl