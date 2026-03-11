import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "scripts"


def run_script(script_name: str, args: list[str] | None = None, env: dict[str, str] | None = None) -> str:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script_name), *(args or [])],
        cwd=ROOT,
        check=True,
        env=merged_env,
        capture_output=True,
        text=True,
    )
    return result.stdout


class ReligiousCohortsBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.csv_path = Path(cls.tempdir.name) / "religious_cohorts_2024_2025.csv"
        cls.summary_path = Path(cls.tempdir.name) / "religious_cohorts_2024_2025.summary.json"
        cls.stdout = run_script(
            "build_religious_cohorts_data.py",
            args=[
                "--out-csv",
                str(cls.csv_path),
                "--out-summary",
                str(cls.summary_path),
            ],
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tempdir.cleanup()

    def test_output_files_are_generated(self) -> None:
        self.assertIn("Wrote", self.stdout)
        self.assertTrue(self.csv_path.exists())
        self.assertTrue(self.summary_path.exists())

    def test_summary_snapshot_values(self) -> None:
        summary = json.loads(self.summary_path.read_text(encoding="utf-8"))

        self.assertEqual(summary["cohorts"]["legacy_2024_base"]["accounts"], 185)
        self.assertAlmostEqual(summary["cohorts"]["legacy_2024_base"]["gpv_2024_usd"], 235_556_682.00, places=2)
        self.assertAlmostEqual(summary["cohorts"]["legacy_2024_base"]["gpv_2025_usd"], 281_942_508.00, places=2)
        self.assertEqual(summary["cohorts"]["new_2025"]["accounts"], 61)
        self.assertAlmostEqual(summary["cohorts"]["new_2025"]["gpv_2025_usd"], 50_202_336.00, places=2)
        self.assertEqual(summary["cohorts"]["total_religious_2025"]["accounts"], 246)
        self.assertAlmostEqual(summary["cohorts"]["total_religious_2025"]["gpv_2025_usd"], 332_144_844.00, places=2)

    def test_csv_columns_and_row_count(self) -> None:
        with self.csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        expected_columns = [
            "account_id",
            "account_name_2025",
            "account_name_2024",
            "cohort_2025",
            "in_2024_all_accounts",
            "gpv_2024_usd",
            "gpv_2025_usd",
            "delta_2025_vs_2024_usd",
            "yoy_2025_vs_2024_pct",
            "account_tier_2025",
            "religious_tier_2025",
            "match_type",
            "religious_match_reason",
        ]
        self.assertEqual(reader.fieldnames, expected_columns)
        self.assertEqual(len(rows), 246)
        self.assertEqual(rows[0]["account_id"], "AFLRJKTK")
        self.assertEqual(rows[0]["gpv_2025_usd"], "116904951.00")


class GrowthModelBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.json_path = Path(cls.tempdir.name) / "growth_model.data.json"
        cls.js_path = Path(cls.tempdir.name) / "growth_model.data.js"
        cls.coverage_path = Path(cls.tempdir.name) / "coverage_2024_enrichment.csv"
        cls.stdout = run_script(
            "build_growth_model_data.py",
            env={
                "GROWTH_MODEL_OUT_JSON": str(cls.json_path),
                "GROWTH_MODEL_OUT_JS": str(cls.js_path),
                "GROWTH_MODEL_OUT_COVERAGE": str(cls.coverage_path),
            },
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tempdir.cleanup()

    def test_output_files_are_generated(self) -> None:
        self.assertIn("Wrote", self.stdout)
        self.assertTrue(self.json_path.exists())
        self.assertTrue(self.js_path.exists())
        self.assertTrue(self.coverage_path.exists())

    def test_model_snapshot_values(self) -> None:
        model = json.loads(self.json_path.read_text(encoding="utf-8"))

        self.assertEqual(model["metadata"]["currency"], "USD")
        self.assertEqual(model["metadata"]["unit"], "M")

        self.assertAlmostEqual(model["historical"]["all_gpv"]["2024"], 1_130_397_714.00, places=2)
        self.assertAlmostEqual(model["historical"]["all_gpv"]["2025"], 1_718_195_933.00, places=2)
        self.assertAlmostEqual(model["historical"]["cc_gpv"]["2025"], 1_386_051_089.00, places=2)
        self.assertAlmostEqual(model["historical"]["faith_gpv"]["2025"], 332_144_844.00, places=2)
        self.assertEqual(model["targets"]["take_rate"], 0.03)
        self.assertEqual(model["targets"]["cc_gpv_m"]["2028"], 6840.0)
        self.assertEqual(model["segmentation"]["coverage_2024_known_accounts"]["total_2024_accounts"], 3799)
        self.assertEqual(model["segmentation"]["coverage_2024_known_accounts"]["coverage_pct"], 59.86)

        self.assertCountEqual(model["verticals"].keys(), ["all", "cc", "faith"])
        self.assertGreater(len(model["market"]["personal_giving"]["sources"]), 0)

    def test_js_wrapper_contains_window_assignment(self) -> None:
        wrapped = self.js_path.read_text(encoding="utf-8")
        self.assertTrue(wrapped.startswith("window.GROWTH_MODEL_DATA = "))
        self.assertTrue(wrapped.rstrip().endswith(";"))


if __name__ == "__main__":
    unittest.main()
