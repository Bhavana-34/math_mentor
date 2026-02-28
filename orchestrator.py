from typing import Dict, List, Optional, Callable
from agents import ParserAgent, IntentRouterAgent, SolverAgent, VerifierAgent, ExplainerAgent
from rag.pipeline import RAGPipeline
from memory.store import MemoryStore


class AgentTrace:
    def __init__(self):
        self.steps: List[Dict] = []

    def add(self, agent: str, status: str, summary: str, data: Dict = None):
        self.steps.append({
            "agent": agent,
            "status": status,
            "summary": summary,
            "data": data or {},
        })

    def to_list(self) -> List[Dict]:
        return self.steps


class Orchestrator:
    def __init__(self):
        self.rag = RAGPipeline()
        self.memory = MemoryStore()
        self.parser = ParserAgent()
        self.router = IntentRouterAgent()
        self.solver = SolverAgent(rag_pipeline=self.rag)
        self.verifier = VerifierAgent()
        self.explainer = ExplainerAgent()

    def _refresh_parser_corrections(self, input_type: str):
        patterns = self.memory.get_correction_patterns(input_type)
        self.parser.correction_patterns = patterns

    def run(
        self,
        raw_input: str,
        input_type: str = "text",
        hitl_override: Optional[Dict] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Dict:
        trace = AgentTrace()
        result = {
            "trace": [],
            "parsed_problem": {},
            "route_info": {},
            "retrieved_chunks": [],
            "context": "",
            "solution": {},
            "verification": {},
            "explanation": "",
            "final_answer": "",
            "confidence": 0.0,
            "needs_hitl": False,
            "hitl_reason": "",
            "record_id": None,
            "similar_problems": [],
        }

        def progress(msg: str, pct: int = 0):
            if progress_callback:
                progress_callback(msg, pct)

        self._refresh_parser_corrections(input_type)

        progress("🔍 Parsing problem...", 10)
        if hitl_override and hitl_override.get("parsed_problem"):
            parsed = hitl_override["parsed_problem"]
        else:
            parsed = self.parser.parse(raw_input, input_type)

        trace.add("ParserAgent", "✅ done", f"Topic: {parsed.get('topic')}, Needs clarification: {parsed.get('needs_clarification')}", parsed)
        result["parsed_problem"] = parsed

        if parsed.get("needs_clarification") and not hitl_override:
            result["needs_hitl"] = True
            result["hitl_reason"] = f"Parser: {parsed.get('clarification_reason', 'Ambiguous problem')}"
            result["trace"] = trace.to_list()
            return result

        progress("🗂️ Routing to strategy...", 20)
        route_info = self.router.route(parsed)
        trace.add("IntentRouterAgent", "✅ done", f"Strategy: {route_info.get('solution_strategy', '')[:80]}", route_info)
        result["route_info"] = route_info

        progress("📚 Retrieving knowledge...", 35)
        context, chunks = self.rag.get_context_string(parsed.get("problem_text", raw_input))
        trace.add("RAGPipeline", "✅ done", f"Retrieved {len(chunks)} relevant chunks", {"num_chunks": len(chunks)})
        result["retrieved_chunks"] = chunks
        result["context"] = context

        progress("🔎 Finding similar solved problems...", 45)
        similar = self.memory.find_similar(parsed.get("problem_text", raw_input), parsed.get("topic", ""))
        result["similar_problems"] = similar
        if similar:
            trace.add("MemoryStore", "✅ done", f"Found {len(similar)} similar solved problems")
        else:
            trace.add("MemoryStore", "ℹ️ none", "No similar problems found in memory")

        progress("🧮 Solving problem...", 60)
        solution = self.solver.solve(parsed, route_info, context, similar)
        trace.add("SolverAgent", "✅ done", f"Answer: {solution.get('answer', '')[:60]}", solution)
        result["solution"] = solution

        progress("✅ Verifying solution...", 75)
        verification = self.verifier.verify(parsed, solution, context)
        trace.add(
            "VerifierAgent",
            "✅ done" if verification.get("is_correct") else "⚠️ issues",
            f"Correct: {verification.get('is_correct')}, Confidence: {verification.get('confidence', 0):.2f}",
            verification
        )
        result["verification"] = verification

        if verification.get("needs_hitl") and not hitl_override:
            result["needs_hitl"] = True
            result["hitl_reason"] = verification.get("hitl_reason", "Low confidence")

        progress("📝 Generating explanation...", 88)
        explanation = self.explainer.explain(parsed, solution, verification)
        trace.add("ExplainerAgent", "✅ done", "Explanation generated")
        result["explanation"] = explanation
        result["final_answer"] = solution.get("answer", "")
        result["confidence"] = verification.get("confidence", solution.get("confidence", 0.5))

        progress("💾 Saving to memory...", 95)
        record_id = self.memory.store(
            input_type=input_type,
            raw_input=raw_input,
            parsed_question=parsed,
            retrieved_context=chunks,
            final_answer=solution.get("answer", ""),
            explanation=explanation,
            verifier_outcome=verification,
        )
        result["record_id"] = record_id

        result["trace"] = trace.to_list()
        progress("✅ Complete!", 100)
        return result