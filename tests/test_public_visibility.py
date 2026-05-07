from __future__ import annotations

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
PUBLIC_FILES = (
    "README.md",
    "SKILL.md",
    "USER_GUIDE.md",
    "WORKFLOW.md",
    "references/api.md",
    "references/VERSION.md",
    "scripts/VERSION.md",
)


def _zh(*codes: int) -> str:
    return "".join(chr(code) for code in codes)


class PublicVisibilityTests(unittest.TestCase):
    def test_old_pdf_guide_is_removed(self) -> None:
        self.assertFalse((ROOT / ("USER_GUIDE" + ".pdf")).exists())

    def test_public_docs_do_not_show_commercial_terms(self) -> None:
        blocked_terms_zh = (
            _zh(36153, 29992),
            _zh(20215, 26684),
            _zh(25104, 26412),
            _zh(26680, 31639),
        )
        blocked_terms_en = (
            "pri" + "ce",
            "pric" + "ing",
            "co" + "st",
            "f" + "ee",
            "b" + "illing",
            "char" + "ge",
            "meter" + "ed",
            "US" + "D",
            "RM" + "B",
            "CN" + "Y",
        )
        blocked_en_pattern = re.compile(r"\b(?:" + "|".join(re.escape(term) for term in blocked_terms_en) + r")\b", re.I)
        for relative_path in PUBLIC_FILES:
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            for term in blocked_terms_zh:
                self.assertNotIn(term, text, relative_path)
            self.assertIsNone(blocked_en_pattern.search(text), relative_path)


if __name__ == "__main__":
    unittest.main()
