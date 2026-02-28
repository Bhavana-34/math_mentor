from typing import Dict
from utils.llm import chat_completion

EXPLAINER_SYSTEM = """You are a friendly and patient math tutor explaining JEE problems to students.
Given a problem and its verified solution, create a clear, student-friendly explanation.

Your explanation should:
1. Start with a brief overview of the approach
2. Walk through each step clearly in plain English
3. Highlight key formulas or identities used
4. Point out common pitfalls to avoid
5. End with a summary and the final answer

Use simple language. Avoid jargon. Use analogies where helpful.
Format with clear sections and numbered steps.
"""


class ExplainerAgent:
    def explain(self, parsed_problem: Dict, solution: Dict, verifier: Dict) -> str:
        user_content = f"""Problem: {parsed_problem.get('problem_text', '')}
Topic: {parsed_problem.get('topic', '')}

Solution:
Answer: {solution.get('answer', '')}
Steps: {solution.get('solution_steps', [])}
Method: {solution.get('method_used', '')}
Alternative approaches: {solution.get('alternative_approaches', [])}

Verification notes: {verifier.get('verification_steps', [])}
Issues (if any): {verifier.get('issues_found', [])}

Create a clear, student-friendly explanation of this solution."""

        messages = [
            {"role": "system", "content": EXPLAINER_SYSTEM},
            {"role": "user", "content": user_content}
        ]

        explanation = chat_completion(messages, temperature=0.3, max_tokens=2000)
        return explanation