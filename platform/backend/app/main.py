from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import MODULES_DIR
from .models import ProgressPayload
from .repository import (
    build_module_payload,
    list_module_payloads,
    load_progress,
    module_count,
    module_path_for,
    read_module_exercises,
    read_module_knowledge_check,
    read_module_part,
    save_progress,
)
from .review import ReviewService, build_review_context
from .review_profiles import review_profiles_payload


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

review_service = ReviewService()


@app.get("/api/health")
def health_check() -> dict[str, str | int | bool]:
    return {
        "status": "ok",
        "service": "python-adk-learning-platform",
        "module_count": module_count(),
        "modules_dir_exists": MODULES_DIR.exists(),
        "checked_at": datetime.now(UTC).isoformat(),
    }


@app.get("/api/modules")
def list_modules() -> list[dict[str, str | int | list[str]]]:
    return list_module_payloads()


@app.get("/api/modules/{module_id}")
def get_module(module_id: str) -> dict[str, str | int | list[str]]:
    return build_module_payload(module_path_for(module_id))


@app.get("/api/modules/{module_id}/content/{part}")
def get_module_content(module_id: str, part: str) -> dict[str, str]:
    return read_module_part(module_id, part)


@app.get("/api/modules/{module_id}/exercises")
def get_module_exercises(module_id: str) -> dict[str, str | list[dict[str, str | int]]]:
    return read_module_exercises(module_id)


@app.get("/api/modules/{module_id}/knowledge-check")
def get_module_knowledge_check(module_id: str) -> dict[str, str | list[dict[str, str | int]]]:
    return read_module_knowledge_check(module_id)


@app.get("/api/modules/{module_id}/review-context/{segment}")
def get_review_context(module_id: str, segment: str) -> dict[str, Any]:
    return build_review_context(module_id, segment).model_dump()


@app.get("/api/review-profiles")
def get_review_profiles() -> dict[str, Any]:
    return review_profiles_payload()


@app.post("/api/modules/{module_id}/review/material")
def post_material_review(module_id: str) -> dict[str, Any]:
    return review_service.review_segment(module_id, "material").model_dump()


@app.post("/api/modules/{module_id}/review/mini-project")
def post_mini_project_review(module_id: str) -> dict[str, Any]:
    return review_service.review_segment(module_id, "mini_project").model_dump()


@app.post("/api/modules/{module_id}/review/exercises")
def post_exercises_review(module_id: str) -> dict[str, Any]:
    return review_service.review_segment(module_id, "exercises").model_dump()


@app.post("/api/modules/{module_id}/review/knowledge-check")
def post_knowledge_check_review(module_id: str) -> dict[str, Any]:
    return review_service.review_segment(module_id, "knowledge_check").model_dump()


@app.get("/api/progress")
def get_progress() -> dict[str, Any]:
    return load_progress().model_dump()


@app.put("/api/progress")
def put_progress(progress: ProgressPayload) -> dict[str, Any]:
    save_progress(progress)
    return progress.model_dump()
