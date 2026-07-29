import json
from datetime import UTC, datetime
from typing import Any, Protocol

from fastapi import HTTPException
from pydantic import ValidationError

from .config import MODULE_PART_FILES, REVIEW_SEGMENT_ALIASES
from .models import ModuleSummary, ProgressPayload, ReviewContext, ReviewContextItem, ReviewFeedback, ReviewResult, ReviewResultItem
from .parsers import extract_markdown_section, parse_exercises_markdown, parse_knowledge_check_markdown
from .repository import (
    build_module_payload,
    get_module_progress,
    load_progress,
    module_context_markdown,
    module_path_for,
    read_markdown_file,
    save_progress,
    set_module_progress,
)
from .review_profiles import ReviewProfile, load_review_profiles, require_profile_api_key


EXPECTED_RESPONSE_SCHEMA = {
    "segment": "Segment review: material | mini_project | exercises | knowledge_check.",
    "results": [
        {
            "item_id": "Id elementu z ReviewContext.items.",
            "status": "solved | needs_revision",
            "summary": "Krotka ocena odpowiedzi ucznia.",
            "comments": ["Lista konkretnych uwag."],
            "next_step": "Jedno pytanie, wskazowka albo zadanie doprecyzowujace.",
        }
    ],
    "overall_summary": "Krotkie podsumowanie calego segmentu.",
}


REVIEW_RESULT_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["segment", "results", "overall_summary"],
    "properties": {
        "segment": {
            "type": "string",
            "enum": ["material", "mini_project", "exercises", "knowledge_check"],
        },
        "results": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["item_id", "status", "summary", "comments", "next_step"],
                "properties": {
                    "item_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["solved", "needs_revision"]},
                    "summary": {"type": "string"},
                    "comments": {"type": "array", "items": {"type": "string"}},
                    "next_step": {"type": "string"},
                },
            },
        },
        "overall_summary": {"type": "string"},
    },
}


REVIEW_INSTRUCTIONS = {
    "material": (
        "Ocen odpowiedz ucznia po polsku. Skup sie na tym, czy odpowiedz pokazuje "
        "intuicje z materialu, rozumienie mechaniki i praktyczny sens w kontekscie ADK. "
        "Nie przepisuj calej sekcji materialu."
    ),
    "mini_project": (
        "Ocen rozwiazanie mini-projektu i odpowiedz na pytanie sprawdzajace po polsku. "
        "Sprawdz, czy uczen pokazuje decyzje projektowe, ograniczenia i rozumienie przeplywu. "
        "Nie pokazuj pelnego wzorcowego rozwiazania, jesli wystarczy wskazowka."
    ),
    "exercises": (
        "Ocen kazde cwiczenie po polsku. Najpierw sprawdz samodzielna probe, potem "
        "konkretnosc rozwiazania, typowe bledy i zgodnosc z oczekiwanym efektem."
    ),
    "knowledge_check": (
        "Ocen odpowiedzi sprawdzenia wiedzy po polsku. Skup sie na zrozumieniu, brakujacych "
        "elementach, mylnych skojarzeniach i jednym kolejnym kroku dla ucznia."
    ),
}


SYSTEM_REVIEW_PROMPT = (
    "Jestes dydaktycznym agentem sprawdzajacym odpowiedzi w lokalnej platformie nauki "
    "Pythona pod Google ADK. Oceniaj po polsku. Dawaj konkretne wskazowki, ale nie podawaj "
    "pelnego rozwiazania, jesli wystarczy naprowadzenie. Dla odpowiedzi blednych, niepelnych "
    "albo zbyt ogolnych ustaw status needs_revision. Zwroc wylacznie JSON zgodny ze schematem ReviewResult."
)


def normalize_review_segment(segment: str) -> str:
    normalized = REVIEW_SEGMENT_ALIASES.get(segment)

    if normalized is None:
        raise HTTPException(status_code=404, detail="Review segment not found")

    return normalized


def require_answer(answer: str, detail: str = "Answer is required before review") -> None:
    if not answer.strip():
        raise HTTPException(status_code=400, detail=detail)


def module_summary_for(module_id: str) -> ModuleSummary:
    module_payload = build_module_payload(module_path_for(module_id))

    return ModuleSummary(
        id=str(module_payload["id"]),
        number=int(module_payload["number"]),
        title=str(module_payload["title"]),
    )


def build_review_context(module_id: str, segment: str) -> ReviewContext:
    normalized_segment = normalize_review_segment(segment)

    if normalized_segment == "material":
        return build_material_review_context(module_id)

    if normalized_segment == "mini_project":
        return build_mini_project_review_context(module_id)

    if normalized_segment == "exercises":
        return build_exercises_review_context(module_id)

    return build_knowledge_check_review_context(module_id)


def build_material_review_context(module_id: str) -> ReviewContext:
    module_path = module_path_for(module_id)
    markdown = read_markdown_file(module_path / MODULE_PART_FILES["material"])
    progress = load_progress()
    module_progress = get_module_progress(progress, module_id)
    answer = module_progress.part_answers.get("material", "")
    require_answer(answer, "Material answer is required before review")
    prompt_markdown = extract_markdown_section(markdown, "Pytanie sprawdzające") or "Pytanie sprawdzajace z materialu."

    return ReviewContext(
        segment="material",
        module=module_summary_for(module_id),
        source_context_markdown=module_context_markdown(module_path),
        items=[
            ReviewContextItem(
                id="material",
                title="Pytanie sprawdzajace z materialu",
                prompt_markdown=prompt_markdown,
                student_answer=answer,
            )
        ],
        review_instructions=REVIEW_INSTRUCTIONS["material"],
        expected_response_schema=EXPECTED_RESPONSE_SCHEMA,
    )


def build_mini_project_review_context(module_id: str) -> ReviewContext:
    module_path = module_path_for(module_id)
    markdown = read_markdown_file(module_path / MODULE_PART_FILES["mini_project"])
    progress = load_progress()
    module_progress = get_module_progress(progress, module_id)
    submission = module_progress.mini_project_submission
    answer = module_progress.part_answers.get("mini_project", "")
    require_answer(submission, "Mini-project submission is required before review")
    require_answer(answer, "Mini-project check answer is required before review")

    return ReviewContext(
        segment="mini_project",
        module=module_summary_for(module_id),
        source_context_markdown=markdown,
        items=[
            ReviewContextItem(
                id="submission",
                title="Rozwiazanie mini-projektu",
                prompt_markdown=markdown,
                student_answer=submission,
                metadata={"kind": "mini_project_submission"},
            ),
            ReviewContextItem(
                id="mini_project",
                title="Pytanie sprawdzajace z mini-projektu",
                prompt_markdown=extract_markdown_section(markdown, "Pytanie sprawdzające") or markdown,
                student_answer=answer,
                metadata={"kind": "check_answer"},
            ),
        ],
        review_instructions=REVIEW_INSTRUCTIONS["mini_project"],
        expected_response_schema=EXPECTED_RESPONSE_SCHEMA,
    )


def build_exercises_review_context(module_id: str) -> ReviewContext:
    module_path = module_path_for(module_id)
    markdown = read_markdown_file(module_path / MODULE_PART_FILES["exercises"])
    exercises = parse_exercises_markdown(markdown)
    progress = load_progress()
    module_progress = get_module_progress(progress, module_id)
    items: list[ReviewContextItem] = []

    for exercise in exercises:
        exercise_id = str(exercise["id"])

        if module_progress.exercise_statuses.get(exercise_id, "draft") != "review":
            continue

        answer = module_progress.answers.get(exercise_id, "")
        require_answer(answer, f"Answer is required before reviewing {exercise_id}")
        items.append(
            ReviewContextItem(
                id=exercise_id,
                title=str(exercise["title"]),
                prompt_markdown=str(exercise["description_markdown"]),
                student_answer=answer,
                expected_markdown=str(exercise["expected_effect_markdown"]),
                metadata={
                    "number": exercise["number"],
                    "level": exercise["level"],
                    "level_label": exercise["level_label"],
                    "goal": exercise["goal"],
                    "constraints_markdown": exercise["constraints_markdown"],
                },
            )
        )

    if not items:
        raise HTTPException(status_code=400, detail="No exercises are marked for review")

    return ReviewContext(
        segment="exercises",
        module=module_summary_for(module_id),
        source_context_markdown=module_context_markdown(module_path),
        items=items,
        review_instructions=REVIEW_INSTRUCTIONS["exercises"],
        expected_response_schema=EXPECTED_RESPONSE_SCHEMA,
    )


def build_knowledge_check_review_context(module_id: str) -> ReviewContext:
    module_path = module_path_for(module_id)
    markdown = read_markdown_file(module_path / MODULE_PART_FILES["knowledge_check"])
    knowledge_check_items = parse_knowledge_check_markdown(markdown)
    progress = load_progress()
    module_progress = get_module_progress(progress, module_id)
    items: list[ReviewContextItem] = []

    for item in knowledge_check_items:
        item_id = str(item["id"])

        if module_progress.knowledge_check_statuses.get(item_id, "draft") != "review":
            continue

        answer = module_progress.knowledge_check_answers.get(item_id, "")
        require_answer(answer, f"Answer is required before reviewing {item_id}")
        items.append(
            ReviewContextItem(
                id=item_id,
                title=str(item["category_label"]),
                prompt_markdown=str(item["prompt_markdown"]),
                student_answer=answer,
                metadata={
                    "number": item["number"],
                    "category": item["category"],
                    "category_label": item["category_label"],
                },
            )
        )

    if not items:
        raise HTTPException(status_code=400, detail="No knowledge check items are marked for review")

    return ReviewContext(
        segment="knowledge_check",
        module=module_summary_for(module_id),
        source_context_markdown=module_context_markdown(module_path),
        items=items,
        review_instructions=REVIEW_INSTRUCTIONS["knowledge_check"],
        expected_response_schema=EXPECTED_RESPONSE_SCHEMA,
    )


class ReviewAdapter(Protocol):
    def review(self, context: ReviewContext) -> ReviewResult:
        pass


class ReviewProviderClient(Protocol):
    def complete_review_json(self, context: ReviewContext) -> str:
        pass


class MockReviewAdapter:
    def review(self, context: ReviewContext) -> ReviewResult:
        return ReviewResult(
            segment=context.segment,
            results=[self._review_item(item) for item in context.items],
            overall_summary="Mockowy adapter sprawdzil komplet elementow w segmencie.",
        )

    def _review_item(self, item: ReviewContextItem) -> ReviewResultItem:
        normalized_answer = item.student_answer.strip()

        if len(normalized_answer) < 12:
            return ReviewResultItem(
                item_id=item.id,
                status="needs_revision",
                summary=f"{item.title}: odpowiedz jest jeszcze za krotka, zeby rzetelnie ocenic zrozumienie.",
                comments=[
                    "Dopisz konkret: co robisz, dlaczego tak i jaki efekt powinien powstac.",
                    "Sama deklaracja albo pojedyncze slowo nie daje agentowi wystarczajacego kontekstu do oceny.",
                ],
                next_step="Rozwin odpowiedz o 2-3 zdania albo dopisz fragment kodu, ktory pokazuje Twoje rozumowanie.",
            )

        return ReviewResultItem(
            item_id=item.id,
            status="solved",
            summary=f"{item.title}: odpowiedz wyglada na wystarczajaca w mockowym sprawdzeniu.",
            comments=[
                "W prawdziwej integracji agent porowna odpowiedz z trescia zadania i kryteriami z modulu.",
                "Na tym etapie platforma sprawdza tylko minimalna kompletnosc odpowiedzi oraz zapisuje docelowy format feedbacku.",
            ],
            next_step="Przed przejsciem dalej upewnij sie, ze potrafisz wyjasnic swoje rozwiazanie prostszym przykladem.",
        )


class LLMReviewAdapter:
    def __init__(self, client: ReviewProviderClient) -> None:
        self.client = client

    def review(self, context: ReviewContext) -> ReviewResult:
        response_text = self.client.complete_review_json(context)

        try:
            return ReviewResult.model_validate(json.loads(response_text))
        except (json.JSONDecodeError, ValidationError) as error:
            raise HTTPException(status_code=502, detail="Review provider response did not match ReviewResult") from error


class OpenAICompatibleReviewClient:
    def __init__(self, profile: ReviewProfile) -> None:
        api_key = require_profile_api_key(profile)

        try:
            from openai import APIError, OpenAI
        except ImportError as error:
            raise HTTPException(status_code=500, detail="OpenAI package is not installed") from error

        self.api_error = APIError
        self.client = OpenAI(
            api_key=api_key,
            base_url=profile.base_url or None,
        )
        self.profile = profile

    def complete_review_json(self, context: ReviewContext) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.profile.model,
                messages=review_messages(context),
                temperature=self.profile.temperature,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "ReviewResult",
                        "description": "Segmentowy wynik sprawdzenia odpowiedzi ucznia.",
                        "schema": REVIEW_RESULT_JSON_SCHEMA,
                        "strict": True,
                    },
                },
            )
        except self.api_error as error:
            raise HTTPException(status_code=502, detail="OpenAI-compatible review request failed") from error
        except Exception as error:
            raise HTTPException(status_code=502, detail="OpenAI-compatible review request failed") from error

        try:
            content = response.choices[0].message.content
        except (AttributeError, IndexError) as error:
            raise HTTPException(status_code=502, detail="OpenAI-compatible review response is empty") from error

        if not content:
            raise HTTPException(status_code=502, detail="OpenAI-compatible review response is empty")

        return content


class OllamaReviewClient:
    def __init__(self, profile: ReviewProfile) -> None:
        self.profile = profile

    def complete_review_json(self, context: ReviewContext) -> str:
        try:
            import httpx
        except ImportError as error:
            raise HTTPException(status_code=500, detail="httpx package is not installed") from error

        base_url = self.profile.base_url.rstrip("/") or "http://127.0.0.1:11434"
        request_body = {
            "model": self.profile.model,
            "messages": review_messages(context),
            "stream": False,
            "format": REVIEW_RESULT_JSON_SCHEMA,
            "options": {
                "temperature": self.profile.temperature,
            },
        }

        try:
            response = httpx.post(f"{base_url}/api/chat", json=request_body, timeout=120)
            response.raise_for_status()
            raw_response = response.json()
            content = raw_response["message"]["content"]
        except (httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError) as error:
            raise HTTPException(status_code=502, detail="Ollama review request failed") from error

        if not content:
            raise HTTPException(status_code=502, detail="Ollama review response is empty")

        return content


def review_messages(context: ReviewContext) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": SYSTEM_REVIEW_PROMPT,
        },
        {
            "role": "user",
            "content": (
                "ReviewContext:\n"
                f"{json.dumps(context.model_dump(), ensure_ascii=False)}\n\n"
                "Wymagany JSON schema ReviewResult:\n"
                f"{json.dumps(REVIEW_RESULT_JSON_SCHEMA, ensure_ascii=False)}"
            ),
        },
    ]


def create_review_adapter() -> ReviewAdapter:
    active_profile = load_review_profiles()
    profile = active_profile.profile

    if profile.provider == "mock":
        return MockReviewAdapter()

    if profile.provider == "openai_compatible":
        return LLMReviewAdapter(OpenAICompatibleReviewClient(profile))

    if profile.provider == "ollama":
        return LLMReviewAdapter(OllamaReviewClient(profile))

    raise HTTPException(status_code=500, detail=f"Unsupported review provider: {profile.provider}")


class ReviewService:
    def __init__(self, adapter: ReviewAdapter | None = None) -> None:
        self.adapter = adapter

    def review_segment(self, module_id: str, segment: str) -> ProgressPayload:
        context = build_review_context(module_id, segment)
        adapter = self.adapter or create_review_adapter()
        review_result = adapter.review(context)
        feedback_by_item = self._feedback_by_item(context, review_result)
        progress = load_progress()
        module_progress = get_module_progress(progress, module_id)

        if context.segment == "material":
            next_module_progress = module_progress.model_copy(
                update={
                    "part_feedback": {
                        **module_progress.part_feedback,
                        "material": feedback_by_item["material"],
                    },
                }
            )
        elif context.segment == "mini_project":
            next_module_progress = module_progress.model_copy(
                update={
                    "mini_project_feedback": {
                        **module_progress.mini_project_feedback,
                        "submission": feedback_by_item["submission"],
                    },
                    "part_feedback": {
                        **module_progress.part_feedback,
                        "mini_project": feedback_by_item["mini_project"],
                    },
                }
            )
        elif context.segment == "exercises":
            next_module_progress = self._apply_exercise_feedback(module_progress, feedback_by_item)
        else:
            next_module_progress = self._apply_knowledge_check_feedback(module_progress, feedback_by_item)

        next_progress = set_module_progress(progress, module_id, next_module_progress)
        save_progress(next_progress)

        return next_progress

    def _feedback_by_item(self, context: ReviewContext, review_result: ReviewResult) -> dict[str, ReviewFeedback]:
        if review_result.segment != context.segment:
            raise HTTPException(status_code=502, detail="Review result segment does not match context")

        expected_item_ids = {item.id for item in context.items}
        result_item_ids = {item.item_id for item in review_result.results}

        if len(review_result.results) != len(expected_item_ids) or result_item_ids != expected_item_ids:
            raise HTTPException(status_code=502, detail="Review result item ids do not match context")

        checked_at = datetime.now(UTC).isoformat()

        try:
            return {
                item.item_id: ReviewFeedback(
                    status=item.status,
                    summary=item.summary,
                    comments=item.comments,
                    next_step=item.next_step,
                    checked_at=checked_at,
                )
                for item in review_result.results
            }
        except ValidationError as error:
            raise HTTPException(status_code=502, detail="Review result feedback fields are invalid") from error

    def _apply_exercise_feedback(self, module_progress: Any, feedback_by_item: dict[str, ReviewFeedback]) -> Any:
        next_feedback = dict(module_progress.exercise_feedback)
        next_statuses = dict(module_progress.exercise_statuses)
        completed_exercises = set(module_progress.completed_exercises)

        for item_id, feedback in feedback_by_item.items():
            next_feedback[item_id] = feedback
            next_statuses[item_id] = feedback.status

            if feedback.status == "solved":
                completed_exercises.add(item_id)
            else:
                completed_exercises.discard(item_id)

        return module_progress.model_copy(
            update={
                "completed_exercises": sorted(completed_exercises),
                "exercise_statuses": next_statuses,
                "exercise_feedback": next_feedback,
            }
        )

    def _apply_knowledge_check_feedback(self, module_progress: Any, feedback_by_item: dict[str, ReviewFeedback]) -> Any:
        next_feedback = dict(module_progress.knowledge_check_feedback)
        next_statuses = dict(module_progress.knowledge_check_statuses)

        for item_id, feedback in feedback_by_item.items():
            next_feedback[item_id] = feedback
            next_statuses[item_id] = feedback.status

        return module_progress.model_copy(
            update={
                "knowledge_check_statuses": next_statuses,
                "knowledge_check_feedback": next_feedback,
            }
        )
