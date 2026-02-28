from typing import Dict, List
from utils.llm import chat_completion, parse_json_response
from config import VERIFIER_CONFIDENCE_THRESHOLD

VERIFIER_SYSTEM = """You are a rigorous math solution verifier for JEE-level problems.
Check the given solution for:
1. Mathematical correctness (verify each step)
2. Units and domain constraints
3. Edge cases
4. Reasonableness of the answer

Output ONLY valid JSON:
{
  "is_correct": true,
  "confidence": 0.9,
  "issues_found": [],
  "corrections": [],
  "domain_check": "passed|failed|N/A",
  "units_check": "passed|failed|N/A",
  "edge_case_check": "passed|failed|N/A",
  "needs_hitl": false,
  "hitl_reason": "",
  "verification_steps": [
    {"check": "what was checked", "result": "pass|fail", "detail": "explanation"}
  ]
}
"""


class VerifierAgent:
    def verify(self, parsed_problem: Dict, solution: Dict, context: str) -> Dict:
        user_content = f"""Problem: {parsed_problem.get('problem_text', '')}
Topic: {parsed_problem.get('topic', '')}
Constraints: {parsed_problem.get('constraints', [])}

Solution to verify:
Answer: {solution.get('answer', '')}
Steps: {solution.get('solution_steps', [])}
Method: {solution.get('method_used', '')}
Solver confidence: {solution.get('confidence', 0)}
Assumptions: {solution.get('assumptions_made', [])}

Relevant context:
{context if context else 'No specific context.'}

Verify this solution rigorously."""

        messages = [
            {"role": "system", "content": VERIFIER_SYSTEM},
            {"role": "user", "content": user_content}
        ]

        response = chat_completion(messages, temperature=0.1, response_format="json")
        result = parse_json_response(response)

        if not result:
            result = {
                "is_correct": False,
                "confidence": 0.0,
                "issues_found": ["Verification failed"],
                "corrections": [],
                "domain_check": "N/A",
                "units_check": "N/A",
                "edge_case_check": "N/A",
                "needs_hitl": True,
                "hitl_reason": "Verification system error",
                "verification_steps": [],
            }

        if result.get("confidence", 0) < VERIFIER_CONFIDENCE_THRESHOLD:
            result["needs_hitl"] = True
            if not result.get("hitl_reason"):
                result["hitl_reason"] = f"Low confidence ({result.get('confidence', 0):.2f})"

        return result