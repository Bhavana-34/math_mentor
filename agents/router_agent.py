from typing import Dict, List
from utils.llm import chat_completion, parse_json_response

ROUTER_SYSTEM = """You are an intent router for a math problem solving system.
Given a structured math problem, classify it and decide the solution strategy.

Output ONLY valid JSON:
{
  "topic": "algebra|probability|calculus|linear_algebra|other",
  "subtopic": "specific subtopic",
  "solution_strategy": "describe the approach to solve this",
  "tools_needed": ["python_calculator", "symbolic_solver"],
  "difficulty": "easy|medium|hard",
  "estimated_steps": 4,
  "special_considerations": ["any edge cases or tricky parts to watch for"]
}
"""


class IntentRouterAgent:
    def route(self, parsed_problem: Dict) -> Dict:
        messages = [
            {"role": "system", "content": ROUTER_SYSTEM},
            {
                "role": "user",
                "content": f"Parsed problem:\n{parsed_problem}\n\nRoute and plan the solution strategy."
            }
        ]

        response = chat_completion(messages, temperature=0.1, response_format="json")
        result = parse_json_response(response)

        if not result:
            result = {
                "topic": parsed_problem.get("topic", "other"),
                "subtopic": parsed_problem.get("subtopic", ""),
                "solution_strategy": "Direct computation",
                "tools_needed": [],
                "difficulty": "medium",
                "estimated_steps": 4,
                "special_considerations": [],
            }

        return result