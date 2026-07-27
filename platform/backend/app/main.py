from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULES_DIR = PROJECT_ROOT / "modules"

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
