from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULES_DIR = PROJECT_ROOT / "modules"
DATA_DIR = PROJECT_ROOT / "platform" / "data"
PROGRESS_FILE = DATA_DIR / "progress.json"

MODULE_PART_FILES = {
    "material": "module.md",
    "exercises": "exercises.md",
    "mini_project": "mini_project.md",
    "knowledge_check": "knowledge_check.md",
    "summary": "summary.md",
}
PART_ALIASES = {
    "module": "material",
}


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
    part_feedback: dict[str, "ReviewFeedback"] = Field(default_factory=dict)
    mini_project_feedback: dict[str, "ReviewFeedback"] = Field(default_factory=dict)
    exercise_feedback: dict[str, "ReviewFeedback"] = Field(default_factory=dict)
    knowledge_check_feedback: dict[str, "ReviewFeedback"] = Field(default_factory=dict)

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


class ReviewFeedback(BaseModel):
    status: str
    summary: str
    comments: list[str] = Field(default_factory=list)
    next_step: str = ""
    checked_at: str


class AgentFeedbackPayload(BaseModel):
    feedback: str = ""


ModuleProgress.model_rebuild()
ProgressPayload.model_rebuild()


app = FastAPI(
    title="Python ADK Learning Platform",
    version="0.1.0",
    description="Local learning platform for Python ADK modules.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_origin_regex=r"^http://(127\.0\.0\.1|localhost):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_module_number(module_id: str) -> int:
    parts = module_id.split("-")

    if len(parts) < 2:
        return 0

    try:
        return int(parts[1])
    except ValueError:
        return 0


def extract_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        stripped = line.strip()

        if stripped.startswith("# "):
            return stripped.removeprefix("# ").strip()

    return fallback


def slugify_heading(value: str) -> str:
    return (
        value.lower()
        .replace("ą", "a")
        .replace("ć", "c")
        .replace("ę", "e")
        .replace("ł", "l")
        .replace("ń", "n")
        .replace("ó", "o")
        .replace("ś", "s")
        .replace("ź", "z")
        .replace("ż", "z")
    )


def normalize_exercise_level(heading: str) -> str:
    normalized = slugify_heading(heading)

    if "rozgrzew" in normalized:
        return "warmup"

    if "sred" in normalized:
        return "medium"

    if "prakty" in normalized:
        return "practical"

    return "general"


def level_label(level: str) -> str:
    labels = {
        "warmup": "Rozgrzewka",
        "medium": "Srednie",
        "practical": "Praktyczne",
        "general": "Ogolne",
    }

    return labels.get(level, "Ogolne")


def split_exercise_sections(markdown: str) -> dict[str, str]:
    section_aliases = {
        "cel": "goal",
        "opis": "description_markdown",
        "ograniczenia / wskazowki": "constraints_markdown",
        "ograniczenia": "constraints_markdown",
        "wskazowki": "constraints_markdown",
        "oczekiwany efekt": "expected_effect_markdown",
    }
    sections = {
        "goal": "",
        "description_markdown": "",
        "constraints_markdown": "",
        "expected_effect_markdown": "",
    }
    current_section: str | None = None
    current_lines: list[str] = []

    def flush_section() -> None:
        if current_section is not None:
            sections[current_section] = "\n".join(current_lines).strip()

    for line in markdown.splitlines():
        stripped = line.strip()
        section_name = stripped.removesuffix(":")
        inline_value = ""

        if ":" in stripped:
            possible_name, possible_value = stripped.split(":", maxsplit=1)
            section_name = possible_name
            inline_value = possible_value.strip()

        section_key = section_aliases.get(slugify_heading(section_name))

        if section_key is not None:
            flush_section()
            current_section = section_key
            current_lines = [inline_value] if inline_value else []
            continue

        if current_section is None:
            current_section = "description_markdown"

        current_lines.append(line)

    flush_section()

    return sections


def parse_exercises_markdown(markdown: str) -> list[dict[str, str | int]]:
    exercises: list[dict[str, str | int]] = []
    current_level = "general"
    current_level_label = level_label(current_level)
    current_exercise: dict[str, Any] | None = None
    current_lines: list[str] = []

    def flush_exercise() -> None:
        if current_exercise is None:
            return

        sections = split_exercise_sections("\n".join(current_lines).strip())
        exercises.append({**current_exercise, **sections})

    for line in markdown.splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            flush_exercise()
            current_exercise = None
            current_lines = []
            current_level_label = line.removeprefix("## ").strip()
            current_level = normalize_exercise_level(current_level_label)
            continue

        if line.startswith("### Ćwiczenie ") or line.startswith("### Cwiczenie "):
            flush_exercise()
            heading = line.removeprefix("### ").strip()
            title = heading
            exercise_number = len(exercises) + 1

            if ":" in heading:
                number_part, title_part = heading.split(":", maxsplit=1)
                title = title_part.strip()
                digits = "".join(character for character in number_part if character.isdigit())

                if digits:
                    exercise_number = int(digits)

            current_exercise = {
                "id": f"exercise-{exercise_number}",
                "number": exercise_number,
                "title": title,
                "level": current_level,
                "level_label": current_level_label,
            }
            current_lines = []
            continue

        if current_exercise is not None:
            current_lines.append(line)

    flush_exercise()

    return exercises


def normalize_knowledge_check_category(heading: str) -> str:
    normalized = slugify_heading(heading)

    if "pytania otwarte" in normalized:
        return "open_questions"

    if "krotkie scenariusze" in normalized:
        return "scenarios"

    if "co by bylo gdyby" in normalized:
        return "what_if"

    if "typowe bledy" in normalized:
        return "common_mistakes"

    if "samoocena" in normalized:
        return "self_assessment"

    if "mini zadanie" in normalized:
        return "active_task"

    return "general"


def parse_knowledge_check_markdown(markdown: str) -> list[dict[str, str | int]]:
    items: list[dict[str, str | int]] = []
    current_category = "general"
    current_category_label = "Ogolne"
    pending_lines: list[str] = []

    def flush_pending() -> None:
        nonlocal pending_lines

        prompt_markdown = "\n".join(pending_lines).strip()

        if not prompt_markdown:
            pending_lines = []
            return

        item_number = len(items) + 1
        items.append(
            {
                "id": f"knowledge-check-{item_number}",
                "number": item_number,
                "category": current_category,
                "category_label": current_category_label,
                "prompt_markdown": prompt_markdown,
            }
        )
        pending_lines = []

    for line in markdown.splitlines():
        if line.startswith("# "):
            continue

        if line.startswith("## "):
            flush_pending()
            current_category_label = line.removeprefix("## ").strip()
            current_category = normalize_knowledge_check_category(current_category_label)
            continue

        stripped = line.strip()
        starts_numbered_item = bool(stripped) and stripped[0].isdigit() and ". " in stripped[:5]
        starts_bullet_item = stripped.startswith("- ")

        if current_category == "active_task":
            if stripped:
                pending_lines.append(line)
            elif pending_lines:
                pending_lines.append(line)
            continue

        if starts_numbered_item or starts_bullet_item:
            flush_pending()
            if starts_bullet_item:
                pending_lines = [stripped.removeprefix("- ").strip()]
            else:
                _, item_text = stripped.split(". ", maxsplit=1)
                pending_lines = [item_text.strip()]
            continue

        if pending_lines or stripped:
            pending_lines.append(line)

    flush_pending()

    return items


def module_path_for(module_id: str) -> Path:
    module_path = MODULES_DIR / module_id

    if module_path.parent != MODULES_DIR or not module_path.is_dir():
        raise HTTPException(status_code=404, detail="Module not found")

    return module_path


def read_markdown_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Module content not found") from error


def normalize_part(part: str) -> str:
    normalized = PART_ALIASES.get(part, part)

    if normalized not in MODULE_PART_FILES:
        raise HTTPException(status_code=404, detail="Module part not found")

    return normalized


def load_progress() -> ProgressPayload:
    if not PROGRESS_FILE.exists():
        return ProgressPayload()

    try:
        raw_progress = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        return ProgressPayload.model_validate(raw_progress)
    except (json.JSONDecodeError, OSError, ValueError) as error:
        raise HTTPException(status_code=500, detail="Progress data is unreadable") from error


def save_progress(progress: ProgressPayload) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary_file = PROGRESS_FILE.with_suffix(".json.tmp")

    try:
        temporary_file.write_text(
            json.dumps(progress.model_dump(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary_file.replace(PROGRESS_FILE)
    except OSError as error:
        raise HTTPException(status_code=500, detail="Progress data could not be saved") from error


def build_module_payload(module_path: Path) -> dict[str, str | int | list[str]]:
    module_markdown = read_markdown_file(module_path / MODULE_PART_FILES["material"])
    module_id = module_path.name
    available_parts = [
        part
        for part, filename in MODULE_PART_FILES.items()
        if (module_path / filename).is_file()
    ]

    return {
        "id": module_id,
        "number": extract_module_number(module_id),
        "title": extract_title(module_markdown, module_id),
        "path": str(module_path.relative_to(PROJECT_ROOT)),
        "parts": available_parts,
    }


def module_context_markdown(module_path: Path) -> str:
    markdown = read_markdown_file(module_path / MODULE_PART_FILES["material"])
    sections: list[str] = []
    current_heading = ""
    current_lines: list[str] = []
    allowed_headings = {
        "intuicja",
        "wyjasnienie techniczne",
        "typowe pulapki",
        "dlaczego tak, a nie inaczej",
        "kiedy uzywac, a kiedy nie",
    }

    def flush_section() -> None:
        if current_heading and slugify_heading(current_heading) in allowed_headings:
            body = "\n".join(current_lines).strip()
            if body:
                sections.append(f"## {current_heading}\n{body}")

    for line in markdown.splitlines():
        if line.startswith("## "):
            flush_section()
            current_heading = line.removeprefix("## ").strip()
            current_lines = []
            continue

        if current_heading:
            current_lines.append(line)

    flush_section()

    return "\n\n".join(sections)


def get_module_progress(progress: ProgressPayload, module_id: str) -> ModuleProgress:
    return progress.modules.get(module_id, ModuleProgress())


def make_review_feedback(answer: str, review_label: str) -> ReviewFeedback:
    normalized_answer = answer.strip()
    checked_at = datetime.now(UTC).isoformat()

    if len(normalized_answer) < 12:
        return ReviewFeedback(
            status="needs_revision",
            summary=f"{review_label}: odpowiedz jest jeszcze za krotka, zeby rzetelnie ocenic zrozumienie.",
            comments=[
                "Dopisz konkret: co robisz, dlaczego tak i jaki efekt powinien powstac.",
                "Sama deklaracja albo pojedyncze slowo nie daje agentowi wystarczajacego kontekstu do oceny.",
            ],
            next_step="Rozwin odpowiedz o 2-3 zdania albo dopisz fragment kodu, ktory pokazuje Twoje rozumowanie.",
            checked_at=checked_at,
        )

    return ReviewFeedback(
        status="solved",
        summary=f"{review_label}: odpowiedz wyglada na wystarczajaca w mockowym sprawdzeniu.",
        comments=[
            "W prawdziwej integracji agent porowna odpowiedz z trescia zadania i kryteriami z modulu.",
            "Na tym etapie platforma sprawdza tylko minimalna kompletnosc odpowiedzi oraz zapisuje docelowy format feedbacku.",
        ],
        next_step="Przed przejsciem dalej upewnij sie, ze potrafisz wyjasnic swoje rozwiazanie prostszym przykladem.",
        checked_at=checked_at,
    )


def require_answer(answer: str, detail: str = "Answer is required before review") -> None:
    if not answer.strip():
        raise HTTPException(status_code=400, detail=detail)


def set_module_progress(progress: ProgressPayload, module_id: str, module_progress: ModuleProgress) -> ProgressPayload:
    return progress.model_copy(
        update={
            "modules": {
                **progress.modules,
                module_id: module_progress,
            },
        }
    )


def review_material_segment(module_id: str) -> dict[str, Any]:
    module_path = module_path_for(module_id)
    read_markdown_file(module_path / MODULE_PART_FILES["material"])
    progress = load_progress()
    module_progress = get_module_progress(progress, module_id)
    answer = module_progress.part_answers.get("material", "")
    require_answer(answer, "Material answer is required before review")
    feedback = make_review_feedback(answer, "Pytanie sprawdzajace z materialu")
    next_module_progress = module_progress.model_copy(
        update={
            "part_feedback": {
                **module_progress.part_feedback,
                "material": feedback,
            },
        }
    )
    next_progress = set_module_progress(progress, module_id, next_module_progress)
    save_progress(next_progress)

    return next_progress.model_dump()


def review_mini_project_segment(module_id: str) -> dict[str, Any]:
    module_path = module_path_for(module_id)
    read_markdown_file(module_path / MODULE_PART_FILES["mini_project"])
    progress = load_progress()
    module_progress = get_module_progress(progress, module_id)
    submission = module_progress.mini_project_submission
    answer = module_progress.part_answers.get("mini_project", "")
    require_answer(submission, "Mini-project submission is required before review")
    require_answer(answer, "Mini-project check answer is required before review")
    submission_feedback = make_review_feedback(submission, "Rozwiazanie mini-projektu")
    answer_feedback = make_review_feedback(answer, "Pytanie sprawdzajace z mini-projektu")
    next_module_progress = module_progress.model_copy(
        update={
            "mini_project_feedback": {
                **module_progress.mini_project_feedback,
                "submission": submission_feedback,
            },
            "part_feedback": {
                **module_progress.part_feedback,
                "mini_project": answer_feedback,
            },
        }
    )
    next_progress = set_module_progress(progress, module_id, next_module_progress)
    save_progress(next_progress)

    return next_progress.model_dump()


def review_exercises_segment(module_id: str) -> dict[str, Any]:
    module_path = module_path_for(module_id)
    markdown = read_markdown_file(module_path / MODULE_PART_FILES["exercises"])
    exercises = parse_exercises_markdown(markdown)
    progress = load_progress()
    module_progress = get_module_progress(progress, module_id)
    review_items = [
        exercise
        for exercise in exercises
        if module_progress.exercise_statuses.get(str(exercise["id"]), "draft") == "review"
    ]

    if not review_items:
        raise HTTPException(status_code=400, detail="No exercises are marked for review")

    next_feedback = dict(module_progress.exercise_feedback)
    next_statuses = dict(module_progress.exercise_statuses)
    completed_exercises = set(module_progress.completed_exercises)

    for exercise in review_items:
        exercise_id = str(exercise["id"])
        answer = module_progress.answers.get(exercise_id, "")
        require_answer(answer, f"Answer is required before reviewing {exercise_id}")
        feedback = make_review_feedback(answer, f"Cwiczenie {exercise['number']}")
        next_feedback[exercise_id] = feedback
        next_statuses[exercise_id] = feedback.status

        if feedback.status == "solved":
            completed_exercises.add(exercise_id)
        else:
            completed_exercises.discard(exercise_id)

    next_module_progress = module_progress.model_copy(
        update={
            "completed_exercises": sorted(completed_exercises),
            "exercise_statuses": next_statuses,
            "exercise_feedback": next_feedback,
        }
    )
    next_progress = set_module_progress(progress, module_id, next_module_progress)
    save_progress(next_progress)

    return next_progress.model_dump()


def review_knowledge_check_segment(module_id: str) -> dict[str, Any]:
    module_path = module_path_for(module_id)
    markdown = read_markdown_file(module_path / MODULE_PART_FILES["knowledge_check"])
    items = parse_knowledge_check_markdown(markdown)
    progress = load_progress()
    module_progress = get_module_progress(progress, module_id)
    review_items = [
        item
        for item in items
        if module_progress.knowledge_check_statuses.get(str(item["id"]), "draft") == "review"
    ]

    if not review_items:
        raise HTTPException(status_code=400, detail="No knowledge check items are marked for review")

    next_feedback = dict(module_progress.knowledge_check_feedback)
    next_statuses = dict(module_progress.knowledge_check_statuses)

    for item in review_items:
        item_id = str(item["id"])
        answer = module_progress.knowledge_check_answers.get(item_id, "")
        require_answer(answer, f"Answer is required before reviewing {item_id}")
        feedback = make_review_feedback(answer, f"Pytanie {item['number']}")
        next_feedback[item_id] = feedback
        next_statuses[item_id] = feedback.status

    next_module_progress = module_progress.model_copy(
        update={
            "knowledge_check_statuses": next_statuses,
            "knowledge_check_feedback": next_feedback,
        }
    )
    next_progress = set_module_progress(progress, module_id, next_module_progress)
    save_progress(next_progress)

    return next_progress.model_dump()


def build_agent_instructions(review_type: str) -> str:
    if review_type == "exercise":
        return (
            "Ocen odpowiedz ucznia po polsku. Najpierw sprawdz, czy probowal samodzielnie "
            "rozwiazac zadanie. Nie pokazuj pelnego wzorcowego rozwiazania, chyba ze feedback "
            "tego wymaga. Daj krotka diagnoze, 2-4 konkretne wskazowki i jedno pytanie "
            "sprawdzajace na koniec."
        )

    return (
        "Ocen odpowiedz ucznia po polsku. Skup sie na zrozumieniu, brakujacych elementach "
        "i typowych nieporozumieniach. Nie przepisuj calego materialu. Daj zwiezly feedback "
        "i jedno pytanie doprecyzowujace na koniec."
    )


def find_exercise(module_id: str, item_id: str) -> dict[str, str | int]:
    module_path = module_path_for(module_id)
    markdown = read_markdown_file(module_path / MODULE_PART_FILES["exercises"])

    for exercise in parse_exercises_markdown(markdown):
        if exercise["id"] == item_id:
            return exercise

    raise HTTPException(status_code=404, detail="Exercise not found")


def find_knowledge_check_item(module_id: str, item_id: str) -> dict[str, str | int]:
    module_path = module_path_for(module_id)
    markdown = read_markdown_file(module_path / MODULE_PART_FILES["knowledge_check"])

    for item in parse_knowledge_check_markdown(markdown):
        if item["id"] == item_id:
            return item

    raise HTTPException(status_code=404, detail="Knowledge check item not found")


def build_exercise_agent_context(module_id: str, exercise_id: str) -> dict[str, Any]:
    module_path = module_path_for(module_id)
    module_payload = build_module_payload(module_path)
    progress = load_progress()
    module_progress = get_module_progress(progress, module_id)
    exercise = find_exercise(module_id, exercise_id)
    student_answer = module_progress.answers.get(exercise_id, "")

    if not student_answer.strip():
        raise HTTPException(status_code=400, detail="Student answer is required before preparing agent context")

    return {
        "kind": "exercise_review",
        "module": {
            "id": module_payload["id"],
            "number": module_payload["number"],
            "title": module_payload["title"],
        },
        "item": {
            "id": exercise["id"],
            "number": exercise["number"],
            "title": exercise["title"],
            "level": exercise["level"],
            "goal": exercise["goal"],
            "description_markdown": exercise["description_markdown"],
            "constraints_markdown": exercise["constraints_markdown"],
            "expected_effect_markdown": exercise["expected_effect_markdown"],
        },
        "student_answer": student_answer,
        "current_status": module_progress.exercise_statuses.get(exercise_id, "draft"),
        "saved_feedback": module_progress.exercise_feedback.get(exercise_id, ""),
        "module_context_markdown": module_context_markdown(module_path),
        "agent_instructions": build_agent_instructions("exercise"),
    }


def build_knowledge_check_agent_context(module_id: str, item_id: str) -> dict[str, Any]:
    module_path = module_path_for(module_id)
    module_payload = build_module_payload(module_path)
    progress = load_progress()
    module_progress = get_module_progress(progress, module_id)
    item = find_knowledge_check_item(module_id, item_id)
    student_answer = module_progress.knowledge_check_answers.get(item_id, "")

    if not student_answer.strip():
        raise HTTPException(status_code=400, detail="Student answer is required before preparing agent context")

    return {
        "kind": "knowledge_check_review",
        "module": {
            "id": module_payload["id"],
            "number": module_payload["number"],
            "title": module_payload["title"],
        },
        "item": {
            "id": item["id"],
            "number": item["number"],
            "category": item["category"],
            "category_label": item["category_label"],
            "prompt_markdown": item["prompt_markdown"],
        },
        "student_answer": student_answer,
        "current_status": module_progress.knowledge_check_statuses.get(item_id, "draft"),
        "saved_feedback": module_progress.knowledge_check_feedback.get(item_id, ""),
        "module_context_markdown": module_context_markdown(module_path),
        "agent_instructions": build_agent_instructions("knowledge_check"),
    }


def save_agent_feedback(module_id: str, item_id: str, review_type: str, feedback: str) -> dict[str, Any]:
    module_path_for(module_id)
    progress = load_progress()
    module_progress = get_module_progress(progress, module_id)

    if review_type == "exercise":
        find_exercise(module_id, item_id)
        review_feedback = make_review_feedback(feedback, "Reczny feedback cwiczenia")
        next_module_progress = module_progress.model_copy(
            update={
                "exercise_feedback": {
                    **module_progress.exercise_feedback,
                    item_id: review_feedback,
                },
            }
        )
    else:
        find_knowledge_check_item(module_id, item_id)
        review_feedback = make_review_feedback(feedback, "Reczny feedback sprawdzenia wiedzy")
        next_module_progress = module_progress.model_copy(
            update={
                "knowledge_check_feedback": {
                    **module_progress.knowledge_check_feedback,
                    item_id: review_feedback,
                },
            }
        )

    next_progress = progress.model_copy(
        update={
            "modules": {
                **progress.modules,
                module_id: next_module_progress,
            },
        }
    )
    save_progress(next_progress)

    return next_progress.model_dump()


@app.get("/api/health")
def health_check() -> dict[str, str | int | bool]:
    module_count = 0

    if MODULES_DIR.exists():
        module_count = sum(
            1
            for path in MODULES_DIR.iterdir()
            if path.is_dir() and path.name.startswith("module-")
        )

    return {
        "status": "ok",
        "service": "python-adk-learning-platform",
        "module_count": module_count,
        "modules_dir_exists": MODULES_DIR.exists(),
        "checked_at": datetime.now(UTC).isoformat(),
    }


@app.get("/api/modules")
def list_modules() -> list[dict[str, str | int | list[str]]]:
    if not MODULES_DIR.exists():
        return []

    module_paths = [
        path
        for path in MODULES_DIR.iterdir()
        if path.is_dir() and path.name.startswith("module-")
    ]

    return sorted(
        [build_module_payload(path) for path in module_paths],
        key=lambda module: (module["number"], module["id"]),
    )


@app.get("/api/modules/{module_id}")
def get_module(module_id: str) -> dict[str, str | int | list[str]]:
    return build_module_payload(module_path_for(module_id))


@app.get("/api/modules/{module_id}/content/{part}")
def get_module_content(module_id: str, part: str) -> dict[str, str]:
    module_path = module_path_for(module_id)
    normalized_part = normalize_part(part)
    filename = MODULE_PART_FILES[normalized_part]
    markdown = read_markdown_file(module_path / filename)

    return {
        "module_id": module_id,
        "part": normalized_part,
        "filename": filename,
        "markdown": markdown,
    }


@app.get("/api/modules/{module_id}/exercises")
def get_module_exercises(module_id: str) -> dict[str, str | list[dict[str, str | int]]]:
    module_path = module_path_for(module_id)
    filename = MODULE_PART_FILES["exercises"]
    markdown = read_markdown_file(module_path / filename)

    return {
        "module_id": module_id,
        "filename": filename,
        "exercises": parse_exercises_markdown(markdown),
    }


@app.get("/api/modules/{module_id}/knowledge-check")
def get_module_knowledge_check(module_id: str) -> dict[str, str | list[dict[str, str | int]]]:
    module_path = module_path_for(module_id)
    filename = MODULE_PART_FILES["knowledge_check"]
    markdown = read_markdown_file(module_path / filename)

    return {
        "module_id": module_id,
        "filename": filename,
        "items": parse_knowledge_check_markdown(markdown),
    }


@app.post("/api/modules/{module_id}/review/material")
def post_material_review(module_id: str) -> dict[str, Any]:
    return review_material_segment(module_id)


@app.post("/api/modules/{module_id}/review/mini-project")
def post_mini_project_review(module_id: str) -> dict[str, Any]:
    return review_mini_project_segment(module_id)


@app.post("/api/modules/{module_id}/review/exercises")
def post_exercises_review(module_id: str) -> dict[str, Any]:
    return review_exercises_segment(module_id)


@app.post("/api/modules/{module_id}/review/knowledge-check")
def post_knowledge_check_review(module_id: str) -> dict[str, Any]:
    return review_knowledge_check_segment(module_id)


@app.get("/api/modules/{module_id}/exercises/{exercise_id}/agent-context")
def get_exercise_agent_context(module_id: str, exercise_id: str) -> dict[str, Any]:
    return build_exercise_agent_context(module_id, exercise_id)


@app.put("/api/modules/{module_id}/exercises/{exercise_id}/feedback")
def put_exercise_feedback(
    module_id: str,
    exercise_id: str,
    payload: AgentFeedbackPayload,
) -> dict[str, Any]:
    return save_agent_feedback(module_id, exercise_id, "exercise", payload.feedback)


@app.get("/api/modules/{module_id}/knowledge-check/{item_id}/agent-context")
def get_knowledge_check_agent_context(module_id: str, item_id: str) -> dict[str, Any]:
    return build_knowledge_check_agent_context(module_id, item_id)


@app.put("/api/modules/{module_id}/knowledge-check/{item_id}/feedback")
def put_knowledge_check_feedback(
    module_id: str,
    item_id: str,
    payload: AgentFeedbackPayload,
) -> dict[str, Any]:
    return save_agent_feedback(module_id, item_id, "knowledge_check", payload.feedback)


@app.get("/api/progress")
def get_progress() -> dict[str, Any]:
    return load_progress().model_dump()


@app.put("/api/progress")
def put_progress(progress: ProgressPayload) -> dict[str, Any]:
    save_progress(progress)
    return progress.model_dump()
