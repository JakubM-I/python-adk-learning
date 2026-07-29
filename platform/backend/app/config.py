from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULES_DIR = PROJECT_ROOT / "modules"
DATA_DIR = PROJECT_ROOT / "platform" / "data"
PROGRESS_FILE = DATA_DIR / "progress.json"
REVIEW_PROFILES_FILE = PROJECT_ROOT / "platform" / "backend" / "review_profiles.json"
REVIEW_PROFILES_LOCAL_FILE = PROJECT_ROOT / "platform" / "backend" / "review_profiles.local.json"

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
