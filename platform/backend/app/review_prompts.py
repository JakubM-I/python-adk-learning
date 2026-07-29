import json
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel

from .config import REVIEW_PROMPTS_DIR, REVIEW_SEGMENT_ALIASES
from .models import ReviewContext, ReviewContextItem
from .review_profiles import PromptVariant, ReviewProfile, load_review_profiles


COMMON_REVIEW_SYSTEM_PROMPT = (
    "Jestes dydaktycznym agentem sprawdzajacym odpowiedzi w lokalnej platformie nauki "
    "Pythona pod Google ADK. Zwroc wylacznie JSON zgodny ze schematem ReviewResult. "
    "Nie dodawaj markdowna, komentarzy poza JSON ani tekstu przed/po JSON. "
    "Dopuszczalne statusy to tylko solved albo needs_revision."
)


class ReviewPrompt(BaseModel):
    segment: str
    variant: PromptVariant
    filename: str
    content: str


def load_review_prompt(segment: str, variant: PromptVariant = "default", prompts_dir: Path = REVIEW_PROMPTS_DIR) -> ReviewPrompt:
    normalized_segment = REVIEW_SEGMENT_ALIASES.get(segment, segment)
    filename = f"{normalized_segment}.{variant}.md"
    prompt_path = prompts_dir / filename

    try:
        content = prompt_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=f"Review prompt not found: {filename}") from error
    except OSError as error:
        raise HTTPException(status_code=500, detail=f"Review prompt is unreadable: {filename}") from error

    if not content:
        raise HTTPException(status_code=500, detail=f"Review prompt is empty: {filename}")

    return ReviewPrompt(segment=normalized_segment, variant=variant, filename=filename, content=content)


def prompt_for_profile(segment: str, profile: ReviewProfile) -> ReviewPrompt:
    return load_review_prompt(segment, profile.prompt_variant)


def build_review_payload(context: ReviewContext, variant: PromptVariant) -> dict[str, Any]:
    base_payload: dict[str, Any] = {
        "segment": context.segment,
        "module": context.module.model_dump(),
        "items": [_item_payload(item, context.segment) for item in context.items],
    }

    if context.segment in {"material", "exercises"}:
        base_payload["source_context_markdown"] = _compact_markdown(context.source_context_markdown, variant)
    elif context.segment == "mini_project":
        base_payload["source_context_markdown"] = context.source_context_markdown

    return base_payload


def review_messages(context: ReviewContext, profile: ReviewProfile, schema: dict[str, Any]) -> list[dict[str, str]]:
    prompt = prompt_for_profile(context.segment, profile)
    payload = build_review_payload(context, prompt.variant)

    return [
        {
            "role": "system",
            "content": f"{COMMON_REVIEW_SYSTEM_PROMPT}\n\n{prompt.content}",
        },
        {
            "role": "user",
            "content": (
                "Review payload:\n"
                f"{json.dumps(payload, ensure_ascii=False)}\n\n"
                "Wymagany JSON schema ReviewResult:\n"
                f"{json.dumps(schema, ensure_ascii=False)}"
            ),
        },
    ]


def review_prompt_info_payload(segment: str) -> dict[str, Any]:
    normalized_segment = REVIEW_SEGMENT_ALIASES.get(segment)

    if normalized_segment is None:
        raise HTTPException(status_code=404, detail="Review segment not found")

    active_profile = load_review_profiles()
    prompt = prompt_for_profile(normalized_segment, active_profile.profile)
    estimated_messages = [
        {"role": "system", "content": f"{COMMON_REVIEW_SYSTEM_PROMPT}\n\n{prompt.content}"},
        {"role": "user", "content": f"Review payload for segment {normalized_segment}. JSON schema omitted in diagnostics."},
    ]

    return {
        "segment": normalized_segment,
        "active_profile": active_profile.name,
        "prompt_variant": prompt.variant,
        "prompt_filename": prompt.filename,
        "system_prompt_chars": len(estimated_messages[0]["content"]),
        "estimated_message_chars": sum(len(message["content"]) for message in estimated_messages),
        "contains_private_data": False,
        "contains_prompt_content": False,
    }


def _item_payload(item: ReviewContextItem, segment: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "item_id": item.id,
        "title": item.title,
        "prompt_markdown": item.prompt_markdown,
        "student_answer": item.student_answer,
    }

    if item.expected_markdown:
        payload["expected_markdown"] = item.expected_markdown

    if segment == "exercises":
        payload["goal"] = item.metadata.get("goal", "")
        payload["constraints_markdown"] = item.metadata.get("constraints_markdown", "")
        payload["level"] = item.metadata.get("level", "")
    elif segment == "knowledge_check":
        payload["category"] = item.metadata.get("category", "")
    elif segment == "mini_project":
        payload["kind"] = item.metadata.get("kind", "")

    return payload


def _compact_markdown(markdown: str, variant: PromptVariant) -> str:
    normalized = markdown.strip()

    if variant == "default":
        return normalized

    max_chars = 1800

    if len(normalized) <= max_chars:
        return normalized

    return normalized[:max_chars].rstrip() + "\n\n[Context truncated for compact review.]"
