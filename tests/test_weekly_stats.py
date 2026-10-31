import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "weekly_stats.py"


class WeeklyStatsTest(unittest.TestCase):
    def run_stats(self, rows):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", encoding="utf-8", delete=False) as tmp:
            tmp.write("date,weight_kg,note\n")
            tmp.writelines(rows)
            path = Path(tmp.name)
        try:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                check=True,
                capture_output=True,
                text=True,
            )
        finally:
            path.unlink(missing_ok=True)
        return [line for line in result.stdout.splitlines() if line.startswith("| 20")]

    def test_delta_is_blank_after_incomplete_calendar_week(self):
        lines = self.run_stats([
            "2026-11-01,80.0,утро\n", "2026-11-02,80.0,утро\n",
            "2026-11-03,80.0,утро\n", "2026-11-04,80.0,утро\n",
            "2026-11-08,79.0,утро\n", "2026-11-09,79.0,утро\n",
            "2026-11-10,79.0,утро\n",
            "2026-11-15,78.0,утро\n", "2026-11-16,78.0,утро\n",
            "2026-11-17,78.0,утро\n", "2026-11-18,78.0,утро\n",
        ])
        self.assertEqual([cell.strip() for cell in lines[1].split("|")[1:-1]][3], "")
        self.assertEqual([cell.strip() for cell in lines[2].split("|")[1:-1]][3], "")

    def test_delta_uses_immediately_previous_complete_week(self):
        lines = self.run_stats([
            "2026-11-01,80.0,утро\n", "2026-11-02,80.0,утро\n",
            "2026-11-03,80.0,утро\n", "2026-11-04,80.0,утро\n",
            "2026-11-08,79.5,утро\n", "2026-11-09,79.5,утро\n",
            "2026-11-10,79.5,утро\n", "2026-11-11,79.5,утро\n",
        ])
        self.assertEqual([cell.strip() for cell in lines[1].split("|")[1:-1]][3], "-0.50")


if __name__ == "__main__":
    unittest.main()
