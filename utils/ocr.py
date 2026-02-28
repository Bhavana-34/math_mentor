from typing import Tuple

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

from config import OCR_CONFIDENCE_THRESHOLD


def ocr_with_tesseract(image_path: str) -> Tuple[str, float]:
    if not TESSERACT_AVAILABLE or not PIL_AVAILABLE:
        return "", 0.0
    try:
        image = Image.open(image_path)
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        words = [w for w, c in zip(data["text"], data["conf"]) if int(c) > 0 and w.strip()]
        confs = [int(c) for c in data["conf"] if int(c) > 0]
        text = " ".join(words)
        avg_conf = sum(confs) / len(confs) / 100.0 if confs else 0.0
        return text, avg_conf
    except Exception as e:
        return f"Tesseract error: {e}", 0.0


def ocr_with_easyocr(image_path: str) -> Tuple[str, float]:
    if not EASYOCR_AVAILABLE:
        return "", 0.0
    try:
        reader = easyocr.Reader(["en"], gpu=False)
        results = reader.readtext(image_path)
        if not results:
            return "", 0.0
        texts = [r[1] for r in results]
        confs = [r[2] for r in results]
        text = " ".join(texts)
        avg_conf = sum(confs) / len(confs) if confs else 0.0
        return text, avg_conf
    except Exception as e:
        return f"EasyOCR error: {e}", 0.0


def extract_text_from_image(image_path: str) -> Tuple[str, float, bool]:
    if not TESSERACT_AVAILABLE and not EASYOCR_AVAILABLE:
        return (
            "OCR not available. Install pytesseract or easyocr, then retry. "
            "You can also type the problem manually below.",
            0.0,
            True,
        )

    text, conf = ocr_with_tesseract(image_path)
    if not text or conf < 0.3:
        text2, conf2 = ocr_with_easyocr(image_path)
        if conf2 > conf:
            text, conf = text2, conf2

    needs_hitl = conf < OCR_CONFIDENCE_THRESHOLD
    return text, conf, needs_hitl