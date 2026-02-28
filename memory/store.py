import json
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from config import MEMORY_DB_PATH


class MemoryStore:
    def __init__(self):
        self.db_path = Path(MEMORY_DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.records: List[Dict] = []
        self._load()

    def _load(self):
        if self.db_path.exists():
            with open(self.db_path, "r", encoding="utf-8") as f:
                self.records = json.load(f)
        else:
            self.records = []

    def _save(self):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=2, ensure_ascii=False)

    def store(
        self,
        input_type: str,
        raw_input: str,
        parsed_question: Dict,
        retrieved_context: List[Dict],
        final_answer: str,
        explanation: str,
        verifier_outcome: Dict,
        user_feedback: Optional[str] = None,
        reviewer_comment: Optional[str] = None,
    ) -> str:
        record_id = str(uuid.uuid4())
        record = {
            "id": record_id,
            "timestamp": datetime.utcnow().isoformat(),
            "input_type": input_type,
            "raw_input": raw_input,
            "parsed_question": parsed_question,
            "retrieved_context": retrieved_context,
            "final_answer": final_answer,
            "explanation": explanation,
            "verifier_outcome": verifier_outcome,
            "user_feedback": user_feedback,
            "reviewer_comment": reviewer_comment,
        }
        self.records.append(record)
        self._save()
        return record_id

    def update_feedback(self, record_id: str, feedback: str, comment: str = ""):
        for record in self.records:
            if record["id"] == record_id:
                record["user_feedback"] = feedback
                record["reviewer_comment"] = comment
                self._save()
                return True
        return False

    def find_similar(self, problem_text: str, topic: str, top_k: int = 3) -> List[Dict]:
        scored = []
        problem_words = set(problem_text.lower().split())
        for record in self.records:
            if record.get("user_feedback") == "incorrect":
                continue
            rec_topic = record.get("parsed_question", {}).get("topic", "")
            rec_text = record.get("parsed_question", {}).get("problem_text", "")
            rec_words = set(rec_text.lower().split())
            if not rec_words:
                continue
            intersection = problem_words & rec_words
            union = problem_words | rec_words
            jaccard = len(intersection) / len(union) if union else 0
            topic_bonus = 0.2 if rec_topic == topic else 0
            score = jaccard + topic_bonus
            if score > 0.15:
                scored.append((score, record))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:top_k]]

    def get_correction_patterns(self, input_type: str) -> List[Dict]:
        patterns = []
        for record in self.records:
            if record.get("input_type") == input_type and record.get("reviewer_comment"):
                patterns.append({
                    "original": record.get("raw_input", ""),
                    "correction": record.get("reviewer_comment", ""),
                    "parsed": record.get("parsed_question", {}),
                })
        return patterns[-10:]

    def get_all_records(self) -> List[Dict]:
        return self.records

    def get_stats(self) -> Dict:
        total = len(self.records)
        correct = sum(1 for r in self.records if r.get("user_feedback") == "correct")
        incorrect = sum(1 for r in self.records if r.get("user_feedback") == "incorrect")
        return {"total": total, "correct": correct, "incorrect": incorrect, "pending": total - correct - incorrect}