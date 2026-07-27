from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


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
    completed_exercises: list[str] = Field(default_factory=list)
    exercise_statuses: dict[str, str] = Field(default_factory=dict)
    notes: str = ""
    answers: dict[str, str] = Field(default_factory=dict)


class ProgressPayload(BaseModel):
    modules: dict[str, ModuleProgress] = Field(default_factory=dict)


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


@app.get("/api/progress")
def get_progress() -> dict[str, Any]:
    return load_progress().model_dump()


@app.put("/api/progress")
def put_progress(progress: ProgressPayload) -> dict[str, Any]:
    save_progress(progress)
    return progress.model_dump()
