import json
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from .config import DATA_DIR, MODULE_PART_FILES, MODULES_DIR, PART_ALIASES, PROGRESS_FILE, PROJECT_ROOT
from .models import ModuleProgress, ProgressPayload
from .parsers import extract_module_number, extract_title, parse_exercises_markdown, parse_knowledge_check_markdown, slugify_heading


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


def get_module_progress(progress: ProgressPayload, module_id: str) -> ModuleProgress:
    return progress.modules.get(module_id, ModuleProgress())


def set_module_progress(progress: ProgressPayload, module_id: str, module_progress: ModuleProgress) -> ProgressPayload:
    return progress.model_copy(
        update={
            "modules": {
                **progress.modules,
                module_id: module_progress,
            },
        }
    )


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


def list_module_payloads() -> list[dict[str, str | int | list[str]]]:
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


def read_module_part(module_id: str, part: str) -> dict[str, str]:
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


def read_module_exercises(module_id: str) -> dict[str, str | list[dict[str, str | int]]]:
    module_path = module_path_for(module_id)
    filename = MODULE_PART_FILES["exercises"]
    markdown = read_markdown_file(module_path / filename)

    return {
        "module_id": module_id,
        "filename": filename,
        "exercises": parse_exercises_markdown(markdown),
    }


def read_module_knowledge_check(module_id: str) -> dict[str, str | list[dict[str, str | int]]]:
    module_path = module_path_for(module_id)
    filename = MODULE_PART_FILES["knowledge_check"]
    markdown = read_markdown_file(module_path / filename)

    return {
        "module_id": module_id,
        "filename": filename,
        "items": parse_knowledge_check_markdown(markdown),
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


def module_count() -> int:
    if not MODULES_DIR.exists():
        return 0

    return sum(
        1
        for path in MODULES_DIR.iterdir()
        if path.is_dir() and path.name.startswith("module-")
    )
