from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import image_api_common


class RootFlowAIGPTOnlyTests(unittest.TestCase):
    def test_only_gpt_profile_is_exposed(self) -> None:
        self.assertEqual(image_api_common.SUPPORTED_PROFILES, (image_api_common.PROFILE_GPT,))
        self.assertFalse(hasattr(image_api_common, "PROFILE_GEMINI"))

    def test_gemini_model_names_are_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            image_api_common.resolve_model(None, "gemini-3.1-flash-image-count")

    def test_get_api_key_uses_only_gpt_env_var(self) -> None:
        with mock.patch.dict(os.environ, {"ROOTFLOWAI_GPT_API_KEY": "gpt-key"}, clear=True):
            key, profile, source = image_api_common.get_api_key(None)

        self.assertEqual((key, profile, source), ("gpt-key", image_api_common.PROFILE_GPT, "ROOTFLOWAI_GPT_API_KEY"))

    def test_gpt_models_support_quality(self) -> None:
        for model in (
            image_api_common.MODEL_COUNT_1K,
            image_api_common.MODEL_COUNT_2K,
            image_api_common.MODEL_COUNT_4K,
        ):
            with self.subTest(model=model):
                self.assertTrue(image_api_common.model_supports_quality(model))


if __name__ == "__main__":
    unittest.main()
