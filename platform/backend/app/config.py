import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULES_DIR = PROJECT_ROOT / "modules"
DATA_DIR = PROJECT_ROOT / "platform" / "data"
PROGRESS_FILE = DATA_DIR / "progress.json"
REVIEW_ADAPTER = os.getenv("REVIEW_ADAPTER", "mock").strip().lower() or "mock"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5").strip() or "gpt-5"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

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

REVIEW_SEGMENT_ALIASES = {
    "material": "material",
    "mini-project": "mini_project",
    "mini_project": "mini_project",
    "exercises": "exercises",
    "knowledge-check": "knowledge_check",
    "knowledge_check": "knowledge_check",
}
