import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

from app import repository
from app.models import ModuleProgress, ModuleSummary, ProgressPayload, ReviewContext, ReviewContextItem, ReviewResult, ReviewResultItem
from app.review import MockReviewAdapter, OpenAIReviewAdapter, ReviewService, create_review_adapter


MODULE_ID = "module-01-python-foundations"


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
        with patch("app.review.REVIEW_ADAPTER", "mock"):
            self.assertIsInstance(create_review_adapter(), MockReviewAdapter)

    def test_openai_adapter_without_api_key_raises_configuration_error(self) -> None:
        with self.assertRaises(HTTPException) as context:
            OpenAIReviewAdapter(api_key="")

        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("OPENAI_API_KEY", context.exception.detail)


if __name__ == "__main__":
    unittest.main()
