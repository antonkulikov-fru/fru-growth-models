#!/usr/bin/env python3
import argparse
import csv
import json
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "_inputs" / "fru"
DEFAULT_INPUT_2024 = INPUTS / "2024_all_accounts_donations.csv"
DEFAULT_INPUT_2025 = INPUTS / "2025_religious_accounts_donation_volume_report.csv"
DEFAULT_OUT_CSV = ROOT / "model" / "religious_cohorts_2024_2025.csv"
DEFAULT_OUT_SUMMARY = ROOT / "model" / "religious_cohorts_2024_2025.summary.json"

OUTPUT_FIELDS = [
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


def money(value: str) -> Decimal:
    s = (value or "").strip().replace("$", "").replace(",", "")
    return Decimal(s) if s else Decimal("0")


def q2(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def load_2024_accounts(input_2024: Path) -> dict[str, dict]:
    accounts_2024 = {}
    with input_2024.open("r", encoding="utf-16") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            account_id = (row.get("Account ID") or "").strip()
            if not account_id or account_id == "Total":
                continue
            entry = accounts_2024.setdefault(
                account_id,
                {
                    "account_name": (row.get("Account Name") or "").strip(),
                    "gpv_2024": Decimal("0"),
                },
            )
            entry["gpv_2024"] += money(row.get("Total Donations Volume $"))
    return accounts_2024


def load_2025_accounts(input_2025: Path) -> tuple[dict[str, dict], int]:
    accounts_2025 = {}
    missing_account_id_rows = 0
    with input_2025.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            account_id = (row.get("Account ID") or "").strip()
            if not account_id:
                missing_account_id_rows += 1
                continue
            entry = accounts_2025.setdefault(
                account_id,
                {
                    "account_name_2025": (row.get("Account Name") or "").strip(),
                    "account_tier_2025": (row.get("Account Tier (Volume File)") or "").strip(),
                    "religious_tier_2025": (row.get("TIER (Religious Subset)") or "").strip(),
                    "match_type": (row.get("Match Type") or "").strip(),
                    "religious_match_reason": (row.get("Religious Match Reason") or "").strip(),
                    "gpv_2025": Decimal("0"),
                },
            )
            entry["gpv_2025"] += money(row.get("Total Donation Volume $"))
    return accounts_2025, missing_account_id_rows


def build_rows(accounts_2024: dict[str, dict], accounts_2025: dict[str, dict]) -> tuple[list[dict], set[str], set[str]]:
    ids_2024 = set(accounts_2024)
    ids_2025 = set(accounts_2025)
    legacy_ids = ids_2025 & ids_2024

    rows = []
    for account_id in sorted(ids_2025, key=lambda aid: (accounts_2025[aid]["gpv_2025"], aid), reverse=True):
        r2025 = accounts_2025[account_id]
        r2024 = accounts_2024.get(account_id, {})
        gpv_2024 = r2024.get("gpv_2024", Decimal("0"))
        gpv_2025 = r2025["gpv_2025"]
        delta = gpv_2025 - gpv_2024
        yoy = (delta / gpv_2024) if gpv_2024 > 0 else None
        rows.append(
            {
                "account_id": account_id,
                "account_name_2025": r2025["account_name_2025"],
                "account_name_2024": r2024.get("account_name", ""),
                "cohort_2025": "legacy_2025" if account_id in legacy_ids else "new_2025",
                "in_2024_all_accounts": "yes" if account_id in legacy_ids else "no",
                "gpv_2024_usd": q2(gpv_2024),
                "gpv_2025_usd": q2(gpv_2025),
                "delta_2025_vs_2024_usd": q2(delta),
                "yoy_2025_vs_2024_pct": "" if yoy is None else q2(yoy * Decimal("100")),
                "account_tier_2025": r2025["account_tier_2025"],
                "religious_tier_2025": r2025["religious_tier_2025"],
                "match_type": r2025["match_type"],
                "religious_match_reason": r2025["religious_match_reason"],
            }
        )

    return rows, ids_2024, ids_2025


def build_religious_cohorts(input_2024: Path, input_2025: Path, out_csv: Path, out_summary: Path) -> None:
    accounts_2024 = load_2024_accounts(input_2024)
    accounts_2025, missing_account_id_rows = load_2025_accounts(input_2025)
    rows, ids_2024, ids_2025 = build_rows(accounts_2024, accounts_2025)

    legacy_ids = ids_2025 & ids_2024
    new_ids = ids_2025 - ids_2024

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    legacy_2024_total = sum((accounts_2024[aid]["gpv_2024"] for aid in legacy_ids), Decimal("0"))
    legacy_2025_total = sum((accounts_2025[aid]["gpv_2025"] for aid in legacy_ids), Decimal("0"))
    new_2025_total = sum((accounts_2025[aid]["gpv_2025"] for aid in new_ids), Decimal("0"))
    total_2025 = legacy_2025_total + new_2025_total

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_files": [str(input_2024), str(input_2025)],
        "cohorts": {
            "legacy_2024_base": {
                "accounts": len(legacy_ids),
                "gpv_2024_usd": float(legacy_2024_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                "gpv_2025_usd": float(legacy_2025_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            },
            "new_2025": {
                "accounts": len(new_ids),
                "gpv_2025_usd": float(new_2025_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            },
            "total_religious_2025": {
                "accounts": len(ids_2025),
                "gpv_2025_usd": float(total_2025.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            },
        },
        "quality_checks": {
            "rows_with_missing_account_id_in_2025_report": missing_account_id_rows,
            "distinct_2024_accounts": len(ids_2024),
            "distinct_2025_religious_accounts_with_id": len(ids_2025),
        },
    }

    out_summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_csv}")
    print(f"Wrote {out_summary}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build religious cohorts outputs for 2024/2025.")
    parser.add_argument("--input-2024", type=Path, default=DEFAULT_INPUT_2024)
    parser.add_argument("--input-2025", type=Path, default=DEFAULT_INPUT_2025)
    parser.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    parser.add_argument("--out-summary", type=Path, default=DEFAULT_OUT_SUMMARY)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_religious_cohorts(
        input_2024=args.input_2024,
        input_2025=args.input_2025,
        out_csv=args.out_csv,
        out_summary=args.out_summary,
    )


if __name__ == "__main__":
    main()
