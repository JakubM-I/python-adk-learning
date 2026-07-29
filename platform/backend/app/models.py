from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ReviewFeedback(BaseModel):
    status: str
    summary: str
    comments: list[str] = Field(default_factory=list)
    next_step: str = ""
    checked_at: str


class ModuleProgress(BaseModel):
    completed_parts: list[str] = Field(default_factory=list)
    current_exercise: str | None = None
    current_knowledge_check: str | None = None
    completed_exercises: list[str] = Field(default_factory=list)
    exercise_statuses: dict[str, str] = Field(default_factory=dict)
    knowledge_check_statuses: dict[str, str] = Field(default_factory=dict)
    notes: str = ""
    part_answers: dict[str, str] = Field(default_factory=dict)
    mini_project_submission: str = ""
    answers: dict[str, str] = Field(default_factory=dict)
    knowledge_check_answers: dict[str, str] = Field(default_factory=dict)
    part_feedback: dict[str, ReviewFeedback] = Field(default_factory=dict)
    mini_project_feedback: dict[str, ReviewFeedback] = Field(default_factory=dict)
    exercise_feedback: dict[str, ReviewFeedback] = Field(default_factory=dict)
    knowledge_check_feedback: dict[str, ReviewFeedback] = Field(default_factory=dict)

    @field_validator(
        "part_feedback",
        "mini_project_feedback",
        "exercise_feedback",
        "knowledge_check_feedback",
        mode="before",
    )
    @classmethod
    def normalize_feedback_map(cls, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {}

        normalized: dict[str, Any] = {}

        for key, item in value.items():
            if isinstance(item, str):
                if item.strip():
                    normalized[key] = {
                        "status": "needs_revision",
                        "summary": item,
                        "comments": [],
                        "next_step": "",
                        "checked_at": datetime.now(UTC).isoformat(),
                    }
                continue

            normalized[key] = item

        return normalized


class ProgressPayload(BaseModel):
    modules: dict[str, ModuleProgress] = Field(default_factory=dict)


class ModuleSummary(BaseModel):
    id: str
    number: int
    title: str


class ReviewContextItem(BaseModel):
    id: str
    title: str
    prompt_markdown: str
    student_answer: str
    expected_markdown: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReviewContext(BaseModel):
    segment: str
    module: ModuleSummary
    source_context_markdown: str
    items: list[ReviewContextItem]
    review_instructions: str
    expected_response_schema: dict[str, Any]
