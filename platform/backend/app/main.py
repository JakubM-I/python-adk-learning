from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULES_DIR = PROJECT_ROOT / "modules"


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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
