from __future__ import annotations

import os
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import edit_image
import generate_image
import image_api_common


class GeminiModelRoutingTests(unittest.TestCase):
    def test_auto_is_not_a_user_visible_profile(self) -> None:
        self.assertEqual(image_api_common.SUPPORTED_PROFILES, (image_api_common.PROFILE_GPT, image_api_common.PROFILE_GEMINI))

    def test_gemini_model_matrix_has_1k_2k_4k_for_31_flash_and_3_pro(self) -> None:
        self.assertEqual(
            image_api_common.GEMINI_31_FLASH_MODELS_BY_RESOLUTION,
            {
                "1K": image_api_common.GEMINI_31_FLASH_MODEL,
                "2K": image_api_common.GEMINI_31_FLASH_HD_MODEL,
                "4K": image_api_common.GEMINI_31_FLASH_4K_MODEL,
            },
        )
        self.assertEqual(
            image_api_common.GEMINI_3_PRO_MODELS_BY_RESOLUTION,
            {
                "1K": image_api_common.GEMINI_3_PRO_MODEL,
                "2K": image_api_common.GEMINI_3_PRO_HD_MODEL,
                "4K": image_api_common.GEMINI_3_PRO_4K_MODEL,
            },
        )

    def test_gemini_25_flash_is_not_available(self) -> None:
        self.assertNotIn("gemini-2.5-flash-image-count", image_api_common.GEMINI_COUNT_MODELS)

    def test_model_family_profiles_route_gpt_and_gemini_keys(self) -> None:
        self.assertEqual(
            image_api_common.resolve_profile(
                None,
                image_api_common.MODEL_COUNT_2K,
            ),
            image_api_common.PROFILE_GPT,
        )
        for model in image_api_common.GEMINI_COUNT_MODELS:
            with self.subTest(model=model):
                self.assertEqual(
                    image_api_common.resolve_profile(None, model),
                    image_api_common.PROFILE_GEMINI,
                )

    def test_profile_defaults_use_gpt_and_gemini_default_models(self) -> None:
        self.assertEqual(
            image_api_common.resolve_model(image_api_common.PROFILE_GPT, None),
            image_api_common.MODEL_COUNT_1K,
        )
        self.assertEqual(
            image_api_common.resolve_model(image_api_common.PROFILE_GEMINI, None),
            image_api_common.GEMINI_31_FLASH_MODEL,
        )

    def test_get_api_key_uses_gpt_or_gemini_env_var_by_model_family(self) -> None:
        env = {
            "ROOTFLOWAI_GPT_API_KEY": "gpt-key",
            "ROOTFLOWAI_GEMINI_API_KEY": "gemini-key",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            gpt_key, gpt_profile, gpt_source = image_api_common.get_api_key(
                None,
                profile=None,
                model=image_api_common.MODEL_COUNT_2K,
            )
            gemini_key, gemini_profile, gemini_source = image_api_common.get_api_key(
                None,
                profile=None,
                model=image_api_common.GEMINI_31_FLASH_MODEL,
            )
        self.assertEqual((gpt_key, gpt_profile, gpt_source), ("gpt-key", image_api_common.PROFILE_GPT, "ROOTFLOWAI_GPT_API_KEY"))
        self.assertEqual((gemini_key, gemini_profile, gemini_source), ("gemini-key", image_api_common.PROFILE_GEMINI, "ROOTFLOWAI_GEMINI_API_KEY"))

    def test_gemini_models_do_not_support_quality_parameter(self) -> None:
        self.assertFalse(
            image_api_common.model_supports_quality(
                image_api_common.GEMINI_31_FLASH_MODEL,
            )
        )
        self.assertTrue(
            image_api_common.model_supports_quality(
                image_api_common.MODEL_COUNT_1K,
            )
        )


class GeminiGeneratePayloadTests(unittest.TestCase):
    def test_generate_image_omits_quality_for_gemini_models(self) -> None:
        captured_payloads: list[dict] = []

        def fake_post_json_request(**kwargs):
            captured_payloads.append(kwargs["payload"])
            return {"data": [{"b64_json": "iVBORw0KGgo="}]}

        with (
            mock.patch.dict(os.environ, {"ROOTFLOWAI_GEMINI_API_KEY": "gemini-key"}, clear=True),
            mock.patch.object(generate_image, "post_json_request", side_effect=fake_post_json_request),
            mock.patch.object(generate_image, "save_response_images", return_value=(["/tmp/img.png"], [], None)),
            mock.patch.object(
                sys,
                "argv",
                [
                    "generate_image.py",
                    "--profile",
                    "gemini",
                    "--model",
                    image_api_common.GEMINI_31_FLASH_MODEL,
                    "--prompt",
                    "A clean product hero image.",
                    "--size",
                    "16:9",
                    "--quality",
                    "high",
                ],
            ),
        ):
            with redirect_stdout(StringIO()):
                self.assertEqual(generate_image.main(), 0)

        self.assertEqual(len(captured_payloads), 1)
        self.assertNotIn("quality", captured_payloads[0])
        self.assertEqual(captured_payloads[0]["model"], image_api_common.GEMINI_31_FLASH_MODEL)
        self.assertEqual(captured_payloads[0]["size"], "16:9")


class GeminiEditPayloadTests(unittest.TestCase):
    def test_edit_image_omits_quality_for_gemini_models(self) -> None:
        captured_fields: list[list[tuple[str, str]]] = []
        image_path = Path(__file__).resolve()

        def fake_post_multipart_request(**kwargs):
            captured_fields.append(kwargs["fields"])
            return {"data": [{"b64_json": "iVBORw0KGgo="}]}

        with (
            mock.patch.dict(os.environ, {"ROOTFLOWAI_GEMINI_API_KEY": "gemini-key"}, clear=True),
            mock.patch.object(edit_image, "post_multipart_request", side_effect=fake_post_multipart_request),
            mock.patch.object(edit_image, "save_response_images", return_value=(["/tmp/edit.png"], [], None)),
            mock.patch.object(
                sys,
                "argv",
                [
                    "edit_image.py",
                    "--profile",
                    "gemini",
                    "--model",
                    image_api_common.GEMINI_31_FLASH_MODEL,
                    "--prompt",
                    "Make this image more cinematic.",
                    "--image",
                    str(image_path),
                    "--size",
                    "16:9",
                    "--quality",
                    "high",
                ],
            ),
        ):
            with redirect_stdout(StringIO()):
                self.assertEqual(edit_image.main(), 0)

        self.assertEqual(len(captured_fields), 1)
        field_names = [name for name, _value in captured_fields[0]]
        self.assertNotIn("quality", field_names)
        self.assertIn(("model", image_api_common.GEMINI_31_FLASH_MODEL), captured_fields[0])


if __name__ == "__main__":
    unittest.main()
