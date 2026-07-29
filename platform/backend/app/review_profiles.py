import json
import os
from pathlib import Path
from typing import Any, Literal

from fastapi import HTTPException
from pydantic import BaseModel, Field

from .config import REVIEW_PROFILES_FILE, REVIEW_PROFILES_LOCAL_FILE


ReviewProvider = Literal["mock", "openai_compatible", "ollama"]


class ReviewProfile(BaseModel):
    provider: ReviewProvider
    model: str
    base_url: str = ""
    api_key_env: str = ""
    temperature: float = 0


class ReviewProfilesConfig(BaseModel):
    active_profile: str = "mock"
    profiles: dict[str, ReviewProfile] = Field(default_factory=dict)


class ActiveReviewProfile(BaseModel):
    name: str
    profile: ReviewProfile
    profiles: dict[str, ReviewProfile]


def load_review_profiles(
    default_path: Path = REVIEW_PROFILES_FILE,
    local_path: Path = REVIEW_PROFILES_LOCAL_FILE,
    env: dict[str, str] | None = None,
) -> ActiveReviewProfile:
    env_values = env if env is not None else os.environ
    raw_config = _read_config(default_path, required=True)
    local_config = _read_config(local_path, required=False)

    if local_config:
        raw_config = _merge_config(raw_config, local_config)

    active_profile = env_values.get("REVIEW_PROFILE", "").strip() or raw_config.get("active_profile", "mock")
    raw_config["active_profile"] = active_profile

    try:
        config = ReviewProfilesConfig.model_validate(raw_config)
    except ValueError as error:
        raise HTTPException(status_code=500, detail="Review profiles config is invalid") from error

    profile = config.profiles.get(config.active_profile)

    if profile is None:
        raise HTTPException(status_code=500, detail=f"Review profile not found: {config.active_profile}")

    return ActiveReviewProfile(name=config.active_profile, profile=profile, profiles=config.profiles)


def review_profiles_payload(active_profile: ActiveReviewProfile | None = None) -> dict[str, Any]:
    selected = active_profile or load_review_profiles()

    return {
        "active_profile": selected.name,
        "profiles": [
            {
                "name": name,
                "provider": profile.provider,
                "model": profile.model,
                "base_url": profile.base_url,
                "temperature": profile.temperature,
                "requires_api_key": bool(profile.api_key_env),
                "active": name == selected.name,
            }
            for name, profile in sorted(selected.profiles.items())
        ],
    }


def require_profile_api_key(profile: ReviewProfile, env: dict[str, str] | None = None) -> str:
    if not profile.api_key_env:
        return "local"

    env_values = env if env is not None else os.environ
    api_key = env_values.get(profile.api_key_env, "")

    if not api_key:
        raise HTTPException(status_code=500, detail=f"{profile.api_key_env} is required for the active review profile")

    return api_key


def _read_config(path: Path, required: bool) -> dict[str, Any]:
    if not path.exists():
        if required:
            raise HTTPException(status_code=500, detail=f"Review profiles config not found: {path.name}")

        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise HTTPException(status_code=500, detail=f"Review profiles config is unreadable: {path.name}") from error


def _merge_config(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = {
        **base,
        "profiles": {
            **base.get("profiles", {}),
            **override.get("profiles", {}),
        },
    }

    if "active_profile" in override:
        merged["active_profile"] = override["active_profile"]

    return merged
