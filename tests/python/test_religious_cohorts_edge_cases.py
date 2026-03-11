import csv
import io
import importlib.util
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "build_religious_cohorts_data.py"


def load_script_module():
    spec = importlib.util.spec_from_file_location("build_religious_cohorts_data", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ReligiousCohortsEdgeCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_script_module()

    def test_handles_empty_effective_inputs_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            in_2024 = tdir / "2024.tsv"
            in_2025 = tdir / "2025.csv"
            out_csv = tdir / "out.csv"
            out_summary = tdir / "summary.json"

            # UTF-16 TSV with only Total row should yield zero distinct 2024 accounts.
            in_2024.write_text(
                "Account Name\tAccount ID\tTotal Donations Volume $\n"
                "All accounts\tTotal\t$1,000.00\n",
                encoding="utf-16",
            )
            # Missing Account ID row should be counted in quality checks, but not produce accounts.
            in_2025.write_text(
                "Account Name,Account ID,Account Tier (Volume File),TIER (Religious Subset),"
                "Total Donation Volume $,Matched Volume Account Name,Match Type,Religious Match Reason\n"
                "Example Org,,Tier 2,TIER 2,$100.00,Example Org,exact,name match\n",
                encoding="utf-8",
            )

            with redirect_stdout(io.StringIO()):
                self.mod.build_religious_cohorts(
                    input_2024=in_2024,
                    input_2025=in_2025,
                    out_csv=out_csv,
                    out_summary=out_summary,
                )

            self.assertTrue(out_csv.exists())
            self.assertTrue(out_summary.exists())

            with out_csv.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            self.assertEqual(rows, [])
            self.assertEqual(reader.fieldnames, self.mod.OUTPUT_FIELDS)

            summary = json.loads(out_summary.read_text(encoding="utf-8"))
            self.assertEqual(summary["cohorts"]["legacy_2024_base"]["accounts"], 0)
            self.assertEqual(summary["cohorts"]["new_2025"]["accounts"], 0)
            self.assertEqual(summary["cohorts"]["total_religious_2025"]["accounts"], 0)
            self.assertEqual(summary["quality_checks"]["rows_with_missing_account_id_in_2025_report"], 1)


if __name__ == "__main__":
    unittest.main()
