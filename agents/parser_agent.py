import json
from typing import Dict, List
from utils.llm import chat_completion, parse_json_response

PARSER_SYSTEM = """You are a math problem parser for JEE-level problems.
Your job is to take raw text (possibly from OCR or speech) and output a clean structured JSON.

Output ONLY valid JSON with these fields:
{
  "problem_text": "cleaned and formatted problem statement",
  "topic": "one of: algebra, probability, calculus, linear_algebra, other",
  "subtopic": "specific subtopic e.g. quadratic, AP/GP, limits, determinants",
  "variables": ["list of variables used"],
  "constraints": ["list of constraints or conditions"],
  "given": ["list of given information"],
  "asked": "what the problem is asking for",
  "needs_clarification": false,
  "clarification_reason": "",
  "confidence": 0.9
}

If the input is ambiguous or incomplete set needs_clarification to true and explain why.
Fix obvious OCR/ASR errors (e.g. '0' vs 'o', '1' vs 'l', 'tind' vs 'find').
"""


class ParserAgent:
    def __init__(self, correction_patterns: List[Dict] = None):
        self.correction_patterns = correction_patterns or []

    def _apply_correction_patterns(self, text: str) -> str:
        for pattern in self.correction_patterns:
            original = pattern.get("original", "")
            correction = pattern.get("correction", "")
            if original and correction and original in text:
                text = text.replace(original, correction)
        return text

    def parse(self, raw_text: str, input_type: str = "text") -> Dict:
        corrected_text = self._apply_correction_patterns(raw_text)

        messages = [
            {"role": "system", "content": PARSER_SYSTEM},
            {
                "role": "user",
                "content": f"Input type: {input_type}\nRaw input:\n{corrected_text}\n\nParse this into structured JSON."
            }
        ]

        response = chat_completion(messages, temperature=0.1, response_format="json")
        result = parse_json_response(response)

        if not result:
            result = {
                "problem_text": corrected_text,
                "topic": "other",
                "subtopic": "",
                "variables": [],
                "constraints": [],
                "given": [],
                "asked": "",
                "needs_clarification": True,
                "clarification_reason": "Failed to parse structure",
                "confidence": 0.3,
            }

        return result