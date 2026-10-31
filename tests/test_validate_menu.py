import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_menu", ROOT / "scripts" / "validate_menu.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class MenuValidationTest(unittest.TestCase):
    def test_week_one_passes(self):
        self.assertEqual(VALIDATOR.validate_file(ROOT / "site" / "menus" / "week-01.json"), [])

    def test_template_starts_on_sunday(self):
        data = json.loads((ROOT / "site" / "menus" / "_template.json").read_text(encoding="utf-8"))
        self.assertEqual(data["start"], "2026-11-01")
        self.assertEqual(data["days"][0]["date"], data["start"])


if __name__ == "__main__":
    unittest.main()
