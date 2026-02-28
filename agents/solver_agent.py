import sympy
from sympy import symbols, solve, diff, integrate, limit, simplify, latex
from typing import Dict, List, Tuple, Optional
from utils.llm import chat_completion, parse_json_response

SOLVER_SYSTEM = """You are an expert JEE math solver.
You will receive a structured math problem and relevant context from a knowledge base.
Solve the problem step by step, showing all work clearly.

Output ONLY valid JSON:
{
  "answer": "the final numerical or algebraic answer",
  "answer_latex": "LaTeX format of the answer",
  "solution_steps": [
    {"step": 1, "description": "what we're doing", "computation": "the math", "result": "result of this step"}
  ],
  "method_used": "describe the method",
  "confidence": 0.9,
  "assumptions_made": ["list any assumptions"],
  "alternative_approaches": ["brief description of other methods"]
}
"""


class SolverAgent:
    def __init__(self, rag_pipeline=None):
        self.rag = rag_pipeline

    def _try_symbolic_solve(self, problem_text: str, parsed: Dict) -> Optional[str]:
        try:
            topic = parsed.get("topic", "")
            if topic == "algebra":
                import re
                eq_match = re.search(r"([\w\s\+\-\*\/\^\=]+)\s*=\s*([\w\s\+\-\*\/\^]+)", problem_text)
                if eq_match:
                    x = symbols("x")
                    lhs_str = eq_match.group(1).replace("^", "**")
                    rhs_str = eq_match.group(2).replace("^", "**")
                    try:
                        lhs = sympy.sympify(lhs_str)
                        rhs = sympy.sympify(rhs_str)
                        solutions = solve(lhs - rhs, x)
                        if solutions:
                            return str(solutions)
                    except Exception:
                        pass
        except Exception:
            pass
        return None

    def solve(self, parsed_problem: Dict, route_info: Dict, context: str, similar_problems: List[Dict]) -> Dict:
        similar_context = ""
        if similar_problems:
            examples = []
            for sp in similar_problems[:2]:
                pq = sp.get("parsed_question", {})
                fa = sp.get("final_answer", "")
                if pq and fa:
                    examples.append(f"Similar problem: {pq.get('problem_text', '')}\nAnswer: {fa}")
            if examples:
                similar_context = "\n\nSIMILAR SOLVED PROBLEMS (for pattern reference):\n" + "\n---\n".join(examples)

        user_content = f"""Problem: {parsed_problem.get('problem_text', '')}
Topic: {parsed_problem.get('topic', '')}
Variables: {parsed_problem.get('variables', [])}
Constraints: {parsed_problem.get('constraints', [])}
Solution Strategy: {route_info.get('solution_strategy', '')}
Special Considerations: {route_info.get('special_considerations', [])}

RELEVANT KNOWLEDGE BASE CONTEXT:
{context if context else 'No specific context retrieved.'}
{similar_context}

Solve this problem step by step."""

        messages = [
            {"role": "system", "content": SOLVER_SYSTEM},
            {"role": "user", "content": user_content}
        ]

        response = chat_completion(messages, temperature=0.1, max_tokens=3000, response_format="json")
        result = parse_json_response(response)

        if not result:
            result = {
                "answer": "Unable to solve",
                "answer_latex": "",
                "solution_steps": [],
                "method_used": "N/A",
                "confidence": 0.0,
                "assumptions_made": [],
                "alternative_approaches": [],
            }

        return result