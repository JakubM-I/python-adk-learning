import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import repository
from app.main import app
from app.models import ModuleProgress, ModuleSummary, ProgressPayload, ReviewContext, ReviewContextItem, ReviewResult, ReviewResultItem
from app.review import MockReviewAdapter, OllamaReviewClient, OpenAICompatibleReviewClient, ReviewService, create_review_adapter
from app.review_profiles import ActiveReviewProfile, ReviewProfile, load_review_profiles, require_profile_api_key, review_profiles_payload
from app.review_prompts import build_review_payload, load_review_prompt, review_messages
from app.review import REVIEW_RESULT_JSON_SCHEMA


MODULE_ID = "module-01-python-foundations"


class FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class FakeChoice:
    def __init__(self, content: str) -> None:
        self.message = FakeMessage(content)


class FakeChatResponse:
    def __init__(self, content: str) -> None:
        self.choices = [FakeChoice(content)]


class StaticReviewAdapter:
    def __init__(self, result: ReviewResult) -> None:
        self.result = result

    def review(self, _context):
        return self.result


class ReviewServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.progress_file = Path(self.temp_dir.name) / "progress.json"
        self.data_dir = Path(self.temp_dir.name)
        self.progress_patch = patch.object(repository, "PROGRESS_FILE", self.progress_file)
        self.data_patch = patch.object(repository, "DATA_DIR", self.data_dir)
        self.progress_patch.start()
        self.data_patch.start()

    def tearDown(self) -> None:
        self.data_patch.stop()
        self.progress_patch.stop()
        self.temp_dir.cleanup()

    def write_progress(self, module_progress: ModuleProgress) -> None:
        payload = ProgressPayload(modules={MODULE_ID: module_progress})
        self.progress_file.write_text(json.dumps(payload.model_dump()), encoding="utf-8")

    def read_progress_json(self) -> dict:
        return json.loads(self.progress_file.read_text(encoding="utf-8"))

    def test_mock_adapter_returns_review_result(self) -> None:
        context = ReviewContext(
            segment="material",
            module=ModuleSummary(id=MODULE_ID, number=1, title="Python foundations"),
            source_context_markdown="## Intuicja\nPrzyklad.",
            items=[
                ReviewContextItem(
                    id="material",
                    title="Pytanie sprawdzajace",
                    prompt_markdown="Wyjasnij sens.",
                    student_answer="Rozumiem sens i potrafie podac maly przyklad.",
                )
            ],
            review_instructions="Ocen po polsku.",
            expected_response_schema={},
        )
        result = MockReviewAdapter().review(context)

        self.assertEqual(result.segment, "material")
        self.assertEqual(result.results[0].item_id, "material")
        self.assertEqual(result.results[0].status, "solved")

    def test_service_maps_review_result_to_existing_feedback_shape(self) -> None:
        self.write_progress(ModuleProgress(part_answers={"material": "Rozumiem mechanike i umiem podac przyklad."}))
        adapter = StaticReviewAdapter(
            ReviewResult(
                segment="material",
                results=[
                    ReviewResultItem(
                        item_id="material",
                        status="solved",
                        summary="Odpowiedz jest konkretna.",
                        comments=["Jest przyklad i uzasadnienie."],
                        next_step="Sprobuj porownac to z JavaScriptem.",
                    )
                ],
                overall_summary="Segment zaliczony.",
            )
        )

        result = ReviewService(adapter=adapter).review_segment(MODULE_ID, "material")
        feedback = result.modules[MODULE_ID].part_feedback["material"]

        self.assertEqual(feedback.status, "solved")
        self.assertEqual(feedback.summary, "Odpowiedz jest konkretna.")
        self.assertEqual(feedback.comments, ["Jest przyklad i uzasadnienie."])
        self.assertTrue(feedback.checked_at)

    def test_missing_item_id_does_not_update_progress(self) -> None:
        module_progress = ModuleProgress(part_answers={"material": "To jest wystarczajaco dluga odpowiedz."})
        self.write_progress(module_progress)
        before = self.read_progress_json()
        adapter = StaticReviewAdapter(
            ReviewResult.model_construct(segment="material", results=[], overall_summary="brak")
        )

        with self.assertRaises(HTTPException):
            ReviewService(adapter=adapter).review_segment(MODULE_ID, "material")

        self.assertEqual(self.read_progress_json(), before)

    def test_unknown_item_id_does_not_update_progress(self) -> None:
        module_progress = ModuleProgress(part_answers={"material": "To jest wystarczajaco dluga odpowiedz."})
        self.write_progress(module_progress)
        before = self.read_progress_json()
        adapter = StaticReviewAdapter(
            ReviewResult(
                segment="material",
                results=[
                    ReviewResultItem(
                        item_id="other",
                        status="solved",
                        summary="ok",
                        comments=[],
                        next_step="dalej",
                    )
                ],
                overall_summary="ok",
            )
        )

        with self.assertRaises(HTTPException):
            ReviewService(adapter=adapter).review_segment(MODULE_ID, "material")

        self.assertEqual(self.read_progress_json(), before)

    def test_invalid_status_does_not_update_progress(self) -> None:
        module_progress = ModuleProgress(part_answers={"material": "To jest wystarczajaco dluga odpowiedz."})
        self.write_progress(module_progress)
        before = self.read_progress_json()
        invalid_item = ReviewResultItem.model_construct(
            item_id="material",
            status="done",
            summary="ok",
            comments=[],
            next_step="dalej",
        )
        adapter = StaticReviewAdapter(
            ReviewResult.model_construct(segment="material", results=[invalid_item], overall_summary="ok")
        )

        with self.assertRaises(HTTPException):
            ReviewService(adapter=adapter).review_segment(MODULE_ID, "material")

        self.assertEqual(self.read_progress_json(), before)

    def test_mock_adapter_does_not_require_openai_api_key(self) -> None:
        active_profile = ActiveReviewProfile(
            name="mock",
            profile=ReviewProfile(provider="mock", model="mock"),
            profiles={"mock": ReviewProfile(provider="mock", model="mock")},
        )

        with patch("app.review.load_review_profiles", return_value=active_profile):
            self.assertIsInstance(create_review_adapter(), MockReviewAdapter)

    def test_profile_api_key_env_is_required(self) -> None:
        profile = ReviewProfile(
            provider="openai_compatible",
            model="gpt-5",
            base_url="https://api.openai.com/v1",
            api_key_env="OPENAI_API_KEY",
        )

        with self.assertRaises(HTTPException) as context:
            require_profile_api_key(profile, env={})

        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("OPENAI_API_KEY", context.exception.detail)

    def test_profile_api_key_file_is_used_when_env_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "openrouter_api_key.txt"
            key_file.write_text("sk-or-file-key\n", encoding="utf-8")
            profile = ReviewProfile(
                provider="openai_compatible",
                model="~openai/gpt-latest",
                base_url="https://openrouter.ai/api/v1",
                api_key_env="OPENROUTER_API_KEY",
                api_key_file=str(key_file),
            )

            api_key = require_profile_api_key(profile, env={})

        self.assertEqual(api_key, "sk-or-file-key")

    def test_profile_api_key_env_takes_precedence_over_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "openrouter_api_key.txt"
            key_file.write_text("sk-or-file-key", encoding="utf-8")
            profile = ReviewProfile(
                provider="openai_compatible",
                model="~openai/gpt-latest",
                base_url="https://openrouter.ai/api/v1",
                api_key_env="OPENROUTER_API_KEY",
                api_key_file=str(key_file),
            )

            api_key = require_profile_api_key(profile, env={"OPENROUTER_API_KEY": "sk-or-env-key"})

        self.assertEqual(api_key, "sk-or-env-key")

    def test_missing_profile_api_key_file_raises_configuration_error(self) -> None:
        profile = ReviewProfile(
            provider="openai_compatible",
            model="~openai/gpt-latest",
            base_url="https://openrouter.ai/api/v1",
            api_key_env="OPENROUTER_API_KEY",
            api_key_file="/tmp/missing-openrouter-key.txt",
        )

        with self.assertRaises(HTTPException) as context:
            require_profile_api_key(profile, env={})

        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("OPENROUTER_API_KEY", context.exception.detail)
        self.assertIn("missing-openrouter-key.txt", context.exception.detail)

    def test_empty_profile_api_key_file_raises_configuration_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "openrouter_api_key.txt"
            key_file.write_text("\n", encoding="utf-8")
            profile = ReviewProfile(
                provider="openai_compatible",
                model="~openai/gpt-latest",
                base_url="https://openrouter.ai/api/v1",
                api_key_file=str(key_file),
            )

            with self.assertRaises(HTTPException) as context:
                require_profile_api_key(profile, env={})

        self.assertEqual(context.exception.status_code, 500)

    def test_active_profile_missing_api_key_raises_configuration_error(self) -> None:
        active_profile = ActiveReviewProfile(
            name="openai_gpt5",
            profile=ReviewProfile(
                provider="openai_compatible",
                model="gpt-5",
                base_url="https://api.openai.com/v1",
                api_key_env="OPENAI_API_KEY",
            ),
            profiles={},
        )

        with patch("app.review.load_review_profiles", return_value=active_profile), patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(HTTPException) as context:
                create_review_adapter()

        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("OPENAI_API_KEY", context.exception.detail)

    def test_openai_compatible_client_sends_json_schema_response_format(self) -> None:
        profile = ReviewProfile(
            provider="openai_compatible",
            model="test-model",
            base_url="http://127.0.0.1:1234/v1",
            temperature=0,
        )
        client = OpenAICompatibleReviewClient.__new__(OpenAICompatibleReviewClient)
        client.profile = profile
        client.api_error = Exception
        client.client = MagicMock()
        client.client.chat.completions.create.return_value = FakeChatResponse('{"segment":"material","results":[],"overall_summary":"ok"}')
        context = self.review_context()

        content = client.complete_review_json(context)

        self.assertIn('"segment":"material"', content)
        request = client.client.chat.completions.create.call_args.kwargs
        self.assertEqual(request["model"], "test-model")
        self.assertEqual(request["response_format"]["type"], "json_schema")
        self.assertEqual(request["response_format"]["json_schema"]["name"], "ReviewResult")
        self.assertEqual(request["response_format"]["json_schema"]["schema"]["properties"]["results"]["type"], "array")

    def test_openai_compatible_client_passes_openrouter_base_url_and_headers(self) -> None:
        profile = ReviewProfile(
            provider="openai_compatible",
            model="~openai/gpt-latest",
            base_url="https://openrouter.ai/api/v1",
            api_key_env="OPENROUTER_API_KEY",
            api_key_file="platform/backend/.secrets/openrouter_api_key.txt",
            headers={
                "HTTP-Referer": "http://127.0.0.1:5173",
                "X-OpenRouter-Title": "Python ADK Learning Platform",
            },
            temperature=0,
        )

        with patch("app.review.require_profile_api_key", return_value="sk-or-test"), patch("openai.OpenAI") as openai_class:
            OpenAICompatibleReviewClient(profile)

        request = openai_class.call_args.kwargs
        self.assertEqual(request["api_key"], "sk-or-test")
        self.assertEqual(request["base_url"], "https://openrouter.ai/api/v1")
        self.assertEqual(request["default_headers"]["HTTP-Referer"], "http://127.0.0.1:5173")
        self.assertEqual(request["default_headers"]["X-OpenRouter-Title"], "Python ADK Learning Platform")

    def test_ollama_client_sends_format_as_json_schema(self) -> None:
        profile = ReviewProfile(
            provider="ollama",
            model="llama3.1",
            base_url="http://127.0.0.1:11434",
            temperature=0,
        )
        fake_response = MagicMock()
        fake_response.json.return_value = {"message": {"content": '{"segment":"material","results":[],"overall_summary":"ok"}'}}
        context = self.review_context()

        with patch("httpx.post", return_value=fake_response) as post:
            content = OllamaReviewClient(profile).complete_review_json(context)

        self.assertIn('"segment":"material"', content)
        url = post.call_args.args[0]
        request_body = post.call_args.kwargs["json"]
        self.assertEqual(url, "http://127.0.0.1:11434/api/chat")
        self.assertEqual(request_body["model"], "llama3.1")
        self.assertFalse(request_body["stream"])
        self.assertEqual(request_body["format"]["properties"]["results"]["type"], "array")

    def review_context(self) -> ReviewContext:
        return ReviewContext(
            segment="material",
            module=ModuleSummary(id=MODULE_ID, number=1, title="Python foundations"),
            source_context_markdown="## Intuicja\nPrzyklad.",
            items=[
                ReviewContextItem(
                    id="material",
                    title="Pytanie sprawdzajace",
                    prompt_markdown="Wyjasnij sens.",
                    student_answer="Rozumiem sens i potrafie podac maly przyklad.",
                )
            ],
            review_instructions="Ocen po polsku.",
            expected_response_schema={},
        )


class ReviewProfilesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.default_path = Path(self.temp_dir.name) / "review_profiles.json"
        self.local_path = Path(self.temp_dir.name) / "review_profiles.local.json"
        self.default_path.write_text(
            json.dumps(
                {
                    "active_profile": "mock",
                    "profiles": {
                        "mock": {"provider": "mock", "model": "mock"},
                        "openai_gpt5": {
                            "provider": "openai_compatible",
                            "model": "gpt-5",
                            "base_url": "https://api.openai.com/v1",
                            "api_key_env": "OPENAI_API_KEY",
                            "api_key_file": "platform/backend/.secrets/openai_api_key.txt",
                        },
                        "openrouter_openai_latest": {
                            "provider": "openai_compatible",
                            "model": "~openai/gpt-latest",
                            "base_url": "https://openrouter.ai/api/v1",
                            "api_key_env": "OPENROUTER_API_KEY",
                            "api_key_file": "platform/backend/.secrets/openrouter_api_key.txt",
                            "headers": {
                                "HTTP-Referer": "http://127.0.0.1:5173",
                                "X-OpenRouter-Title": "Python ADK Learning Platform",
                            },
                        },
                    },
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_loader_uses_mock_by_default(self) -> None:
        active_profile = load_review_profiles(self.default_path, self.local_path, env={})

        self.assertEqual(active_profile.name, "mock")
        self.assertEqual(active_profile.profile.provider, "mock")

    def test_review_profile_env_overrides_active_profile(self) -> None:
        active_profile = load_review_profiles(
            self.default_path,
            self.local_path,
            env={"REVIEW_PROFILE": "openai_gpt5"},
        )

        self.assertEqual(active_profile.name, "openai_gpt5")
        self.assertEqual(active_profile.profile.model, "gpt-5")

    def test_local_config_extends_and_overrides_default_config(self) -> None:
        self.local_path.write_text(
            json.dumps(
                {
                    "active_profile": "ollama_local",
                    "profiles": {
                        "openai_gpt5": {
                            "model": "gpt-5-mini",
                        },
                        "ollama_local": {
                            "provider": "ollama",
                            "model": "llama3.1",
                            "base_url": "http://127.0.0.1:11434",
                        },
                    },
                }
            ),
            encoding="utf-8",
        )

        active_profile = load_review_profiles(self.default_path, self.local_path, env={})

        self.assertEqual(active_profile.name, "ollama_local")
        self.assertEqual(active_profile.profiles["openai_gpt5"].model, "gpt-5-mini")
        self.assertEqual(active_profile.profiles["openai_gpt5"].api_key_env, "OPENAI_API_KEY")
        self.assertIn("mock", active_profile.profiles)

    def test_profiles_payload_does_not_expose_api_key_env_name(self) -> None:
        active_profile = load_review_profiles(self.default_path, self.local_path, env={"REVIEW_PROFILE": "openai_gpt5"})
        payload = review_profiles_payload(active_profile)
        openai_profile = next(profile for profile in payload["profiles"] if profile["name"] == "openai_gpt5")
        openrouter_profile = next(profile for profile in payload["profiles"] if profile["name"] == "openrouter_openai_latest")

        self.assertTrue(openai_profile["requires_api_key"])
        self.assertTrue(openrouter_profile["requires_api_key"])
        self.assertNotIn("api_key_env", openai_profile)
        self.assertNotIn("api_key_file", openai_profile)
        self.assertNotIn("api_key_env", openrouter_profile)
        self.assertNotIn("api_key_file", openrouter_profile)
        self.assertNotIn("headers", openrouter_profile)
        self.assertNotIn("openai_api_key.txt", json.dumps(payload))
        self.assertNotIn("openrouter_api_key.txt", json.dumps(payload))
        self.assertNotIn("OPENAI_API_KEY", json.dumps(payload))
        self.assertNotIn("OPENROUTER_API_KEY", json.dumps(payload))


class ReviewProfilesEndpointTest(unittest.TestCase):
    def test_review_profiles_endpoint_returns_sanitized_profiles(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            response = TestClient(app).get("/api/review-profiles")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("active_profile", payload)
        self.assertIn("profiles", payload)
        self.assertNotIn("OPENAI_API_KEY", json.dumps(payload))


class ReviewPromptsTest(unittest.TestCase):
    def test_loader_uses_default_prompt_variant(self) -> None:
        prompt = load_review_prompt("material", "default")

        self.assertEqual(prompt.segment, "material")
        self.assertEqual(prompt.variant, "default")
        self.assertEqual(prompt.filename, "material.default.md")
        self.assertIn("Material Review Prompt", prompt.content)

    def test_loader_uses_compact_prompt_variant(self) -> None:
        prompt = load_review_prompt("material", "compact")

        self.assertEqual(prompt.variant, "compact")
        self.assertEqual(prompt.filename, "material.compact.md")
        self.assertIn("Compact", prompt.content)

    def test_missing_prompt_file_raises_configuration_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(HTTPException) as context:
                load_review_prompt("material", "default", prompts_dir=Path(temp_dir))

        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Review prompt not found", context.exception.detail)

    def test_review_messages_use_profile_prompt_variant(self) -> None:
        profile = ReviewProfile(provider="mock", model="mock", prompt_variant="compact")
        messages = review_messages(self.review_context(), profile, REVIEW_RESULT_JSON_SCHEMA)

        self.assertIn("Material Review Prompt Compact", messages[0]["content"])
        self.assertIn("Review payload", messages[1]["content"])

    def test_compact_payload_is_smaller_than_full_review_context_dump(self) -> None:
        context = self.review_context()
        context.source_context_markdown = "abc " * 2000
        profile = ReviewProfile(provider="mock", model="mock", prompt_variant="compact")
        messages = review_messages(context, profile, REVIEW_RESULT_JSON_SCHEMA)
        full_dump = json.dumps(context.model_dump(), ensure_ascii=False)

        self.assertLess(len(messages[1]["content"]), len(full_dump))

    def test_review_prompt_info_endpoint_does_not_expose_student_answer(self) -> None:
        response = TestClient(app).get("/api/review-prompt-info/material")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        serialized = json.dumps(payload)
        self.assertFalse(payload["contains_private_data"])
        self.assertFalse(payload["contains_prompt_content"])
        self.assertNotIn("student_answer", serialized)

    def review_context(self) -> ReviewContext:
        return ReviewContext(
            segment="material",
            module=ModuleSummary(id=MODULE_ID, number=1, title="Python foundations"),
            source_context_markdown="## Intuicja\nPrzyklad.",
            items=[
                ReviewContextItem(
                    id="material",
                    title="Pytanie sprawdzajace",
                    prompt_markdown="Wyjasnij sens.",
                    student_answer="Rozumiem sens i potrafie podac maly przyklad.",
                )
            ],
            review_instructions="Ocen po polsku.",
            expected_response_schema={},
        )


if __name__ == "__main__":
    unittest.main()
