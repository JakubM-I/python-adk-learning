import json
import os
from pathlib import Path
from typing import Any, Literal

from fastapi import HTTPException
from pydantic import BaseModel, Field

from .config import PROJECT_ROOT, REVIEW_PROFILES_FILE, REVIEW_PROFILES_LOCAL_FILE


ReviewProvider = Literal["mock", "openai_compatible", "ollama"]
PromptVariant = Literal["default", "compact"]


class ReviewProfile(BaseModel):
    provider: ReviewProvider
    model: str
    base_url: str = ""
    api_key_env: str = ""
    api_key_file: str = ""
    headers: dict[str, str] = Field(default_factory=dict)
    temperature: float = 0
    prompt_variant: PromptVariant = "default"


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
                "prompt_variant": profile.prompt_variant,
                "requires_api_key": bool(profile.api_key_env or profile.api_key_file),
                "active": name == selected.name,
            }
            for name, profile in sorted(selected.profiles.items())
        ],
    }


def require_profile_api_key(profile: ReviewProfile, env: dict[str, str] | None = None) -> str:
    if not profile.api_key_env and not profile.api_key_file:
        return "local"

    env_values = env if env is not None else os.environ
    api_key = env_values.get(profile.api_key_env, "").strip() if profile.api_key_env else ""

    if api_key:
        return api_key

    if profile.api_key_file:
        key_path = _resolve_local_path(profile.api_key_file)

        try:
            file_api_key = key_path.read_text(encoding="utf-8").strip()
        except OSError as error:
            raise HTTPException(
                status_code=500,
                detail=f"{_api_key_source_label(profile)} is required for the active review profile",
            ) from error

        if file_api_key:
            return file_api_key

    raise HTTPException(
        status_code=500,
        detail=f"{_api_key_source_label(profile)} is required for the active review profile",
    )


def _api_key_source_label(profile: ReviewProfile) -> str:
    sources = [source for source in [profile.api_key_env, profile.api_key_file] if source]

    return " or ".join(sources) if sources else "API key"


def _resolve_local_path(path_value: str) -> Path:
    path = Path(path_value)

    if path.is_absolute():
        return path

    return PROJECT_ROOT / path


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
    base_profiles = base.get("profiles", {})
    override_profiles = override.get("profiles", {})
    merged_profiles = dict(base_profiles)

    for name, profile_override in override_profiles.items():
        if isinstance(merged_profiles.get(name), dict) and isinstance(profile_override, dict):
            merged_profiles[name] = {
                **merged_profiles[name],
                **profile_override,
            }
        else:
            merged_profiles[name] = profile_override

    merged = {
        **base,
        "profiles": merged_profiles,
    }

    if "active_profile" in override:
        merged["active_profile"] = override["active_profile"]

    return merged
