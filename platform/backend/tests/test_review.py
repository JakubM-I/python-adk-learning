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
                            "provider": "openai_compatible",
                            "model": "gpt-5-mini",
                            "base_url": "https://api.openai.com/v1",
                            "api_key_env": "OPENAI_API_KEY",
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
        self.assertIn("mock", active_profile.profiles)

    def test_profiles_payload_does_not_expose_api_key_env_name(self) -> None:
        active_profile = load_review_profiles(self.default_path, self.local_path, env={"REVIEW_PROFILE": "openai_gpt5"})
        payload = review_profiles_payload(active_profile)
        openai_profile = next(profile for profile in payload["profiles"] if profile["name"] == "openai_gpt5")

        self.assertTrue(openai_profile["requires_api_key"])
        self.assertNotIn("api_key_env", openai_profile)


class ReviewProfilesEndpointTest(unittest.TestCase):
    def test_review_profiles_endpoint_returns_sanitized_profiles(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            response = TestClient(app).get("/api/review-profiles")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("active_profile", payload)
        self.assertIn("profiles", payload)
        self.assertNotIn("OPENAI_API_KEY", json.dumps(payload))


if __name__ == "__main__":
    unittest.main()
