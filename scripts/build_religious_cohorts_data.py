#!/usr/bin/env python3
import csv
import json
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "_inputs" / "fru"
INPUT_2024 = INPUTS / "2024_all_accounts_donations.csv"
INPUT_2025 = INPUTS / "2025_religious_accounts_donation_volume_report.csv"
OUT_CSV = ROOT / "model" / "religious_cohorts_2024_2025.csv"
OUT_SUMMARY = ROOT / "model" / "religious_cohorts_2024_2025.summary.json"


def money(value: str) -> Decimal:
    s = (value or "").strip().replace("$", "").replace(",", "")
    return Decimal(s) if s else Decimal("0")


def q2(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


accounts_2024 = {}
with INPUT_2024.open("r", encoding="utf-16") as f:
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

accounts_2025 = {}
missing_account_id_rows = 0
with INPUT_2025.open("r", encoding="utf-8-sig", newline="") as f:
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

ids_2024 = set(accounts_2024)
ids_2025 = set(accounts_2025)
legacy_ids = ids_2025 & ids_2024
new_ids = ids_2025 - ids_2024

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

with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

legacy_2024_total = sum((accounts_2024[aid]["gpv_2024"] for aid in legacy_ids), Decimal("0"))
legacy_2025_total = sum((accounts_2025[aid]["gpv_2025"] for aid in legacy_ids), Decimal("0"))
new_2025_total = sum((accounts_2025[aid]["gpv_2025"] for aid in new_ids), Decimal("0"))
total_2025 = legacy_2025_total + new_2025_total

summary = {
    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "source_files": [str(INPUT_2024), str(INPUT_2025)],
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

OUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(f"Wrote {OUT_CSV}")
print(f"Wrote {OUT_SUMMARY}")
