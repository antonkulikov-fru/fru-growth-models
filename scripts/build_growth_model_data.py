#!/usr/bin/env python3
import csv
import json
import math
import re
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "_inputs" / "fru"
OUT = ROOT / "model" / "growth_model.data.json"
OUT_JS = ROOT / "model" / "growth_model.data.js"
OUT_COVERAGE = ROOT / "model" / "coverage_2024_enrichment.csv"


def money(value: str) -> Decimal:
    s = (value or "").strip().replace("$", "").replace(",", "")
    return Decimal(s) if s else Decimal("0")


def q2(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def norm_name(value: str) -> str:
    s = (value or "").lower().strip()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def norm_domain(value: str) -> str:
    s = (value or "").strip().lower()
    s = re.sub(r"^https?://", "", s)
    s = s.split("/")[0]
    s = re.sub(r"^www\.", "", s)
    return s


def percentile(values, p):
    if not values:
        return 0.0
    vals = sorted(values)
    k = (len(vals) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return vals[int(k)]
    return vals[f] * (c - k) + vals[c] * (k - f)


# 2024 all accounts (UTF-16 TSV)
accounts_2024 = {}
with (INPUTS / "2024_all_accounts_donations.csv").open("r", encoding="utf-16") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        account_id = (row.get("Account ID") or "").strip()
        if not account_id or account_id == "Total":
            continue
        entry = accounts_2024.setdefault(
            account_id,
            {
                "account_name": (row.get("Account Name") or "").strip(),
                "website": (row.get("Website") or "").strip(),
                "gpv_total": Decimal("0"),
                "gpv_one_time": Decimal("0"),
                "gpv_recurring": Decimal("0"),
            },
        )
        entry["gpv_total"] += money(row.get("Total Donations Volume $"))
        entry["gpv_one_time"] += money(row.get("Totals, One-time #"))
        entry["gpv_recurring"] += money(row.get("Totals, Recurring #"))

# 2025 enriched totals and metadata
accounts_2025 = {}
with (INPUTS / "2025_all_orgs_dontations__fru_enriched.csv").open("r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        account_id = (row.get("Account ID") or "").strip()
        if not account_id:
            continue
        entry = accounts_2025.setdefault(
            account_id,
            {
                "account_name": (row.get("Account Name") or "").strip(),
                "gpv_total": Decimal("0"),
                "ntee_code": (row.get("NTEE code") or "").strip(),
                "fru_sector": (row.get("FRU - Sector") or "").strip(),
                "fru_subsector": (row.get("FRU - Subsector") or "").strip(),
            },
        )
        entry["gpv_total"] += money(row.get("Total Donations Amount"))

# 2025 one-time/recurring split
with (INPUTS / "All Accounts Volume by Source & Frequency (2025).csv").open("r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        account_id = (row.get("Account ID") or "").strip()
        if not account_id or account_id == "Total":
            continue
        if account_id not in accounts_2025:
            accounts_2025[account_id] = {
                "account_name": (row.get("Account Name") or "").strip(),
                "gpv_total": Decimal("0"),
                "ntee_code": "",
                "fru_sector": "",
                "fru_subsector": "",
            }
        accounts_2025[account_id]["gpv_one_time"] = accounts_2025[account_id].get("gpv_one_time", Decimal("0")) + money(
            row.get("Totals, One-time #")
        )
        accounts_2025[account_id]["gpv_recurring"] = accounts_2025[account_id].get("gpv_recurring", Decimal("0")) + money(
            row.get("Totals, Recurring #")
        )

# Faith accounts list and 2025 official total
faith_account_ids = set()
faith_2025_report_total = Decimal("0")
with (INPUTS / "religious_accounts_donation_volume_report.csv").open("r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        account_id = (row.get("Account ID") or "").strip()
        if not account_id:
            continue
        faith_account_ids.add(account_id)
        faith_2025_report_total += money(row.get("Total Donation Volume $"))

# Sector master mapping (for FRU + NTEE fallback)
master_by_domain = {}
master_by_name = {}
with (INPUTS / "FUNDRAISEUP sectors.csv").open("r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        sector = (row.get("FRU - Sector") or "").strip()
        subsector = (row.get("FRU - Subsector") or "").strip()
        ntee = (row.get("NTEE Code (Map to Sub Sectors)") or "").strip()
        domain = norm_domain((row.get("Account Domain") or "").strip())
        name = norm_name((row.get("Account Name") or "").strip())
        mapped = {
            "ntee_code": ntee,
            "fru_sector": sector,
            "fru_subsector": subsector,
        }
        if domain:
            master_by_domain.setdefault(domain, mapped)
        if name:
            master_by_name.setdefault(name, mapped)

# Coverage check for 2024 known accounts
coverage = {
    "total_2024_accounts": len(accounts_2024),
    "covered_by_2025_id": 0,
    "covered_by_sector_domain": 0,
    "covered_by_sector_name": 0,
    "unclassified": 0,
    "with_ntee_code": 0,
    "with_fru_sector": 0,
    "with_fru_subsector": 0,
}
coverage_rows = []

for account_id, account in accounts_2024.items():
    got = None
    mapped = None
    if account_id in accounts_2025 and (
        accounts_2025[account_id].get("ntee_code")
        or accounts_2025[account_id].get("fru_sector")
        or accounts_2025[account_id].get("fru_subsector")
    ):
        got = "id"
        mapped = {
            "ntee_code": accounts_2025[account_id].get("ntee_code", ""),
            "fru_sector": accounts_2025[account_id].get("fru_sector", ""),
            "fru_subsector": accounts_2025[account_id].get("fru_subsector", ""),
        }
    else:
        website_domain = norm_domain(account.get("website") or "")
        if website_domain and website_domain in master_by_domain:
            got = "domain"
            mapped = master_by_domain[website_domain]
        else:
            nname = norm_name(account.get("account_name") or "")
            if nname and nname in master_by_name:
                got = "name"
                mapped = master_by_name[nname]

    if got == "id":
        coverage["covered_by_2025_id"] += 1
    elif got == "domain":
        coverage["covered_by_sector_domain"] += 1
    elif got == "name":
        coverage["covered_by_sector_name"] += 1
    else:
        coverage["unclassified"] += 1

    if mapped:
        if mapped.get("ntee_code"):
            coverage["with_ntee_code"] += 1
        if mapped.get("fru_sector"):
            coverage["with_fru_sector"] += 1
        if mapped.get("fru_subsector"):
            coverage["with_fru_subsector"] += 1

    coverage_rows.append(
        {
            "account_id": account_id,
            "account_name": account.get("account_name", ""),
            "match_source": got or "unclassified",
            "ntee_code": (mapped or {}).get("ntee_code", ""),
            "fru_sector": (mapped or {}).get("fru_sector", ""),
            "fru_subsector": (mapped or {}).get("fru_subsector", ""),
        }
    )

coverage["covered_total"] = (
    coverage["covered_by_2025_id"]
    + coverage["covered_by_sector_domain"]
    + coverage["covered_by_sector_name"]
)
coverage["coverage_pct"] = round(coverage["covered_total"] / coverage["total_2024_accounts"] * 100.0, 2)
coverage["ntee_coverage_pct"] = round(coverage["with_ntee_code"] / coverage["total_2024_accounts"] * 100.0, 2)
coverage["fru_sector_coverage_pct"] = round(coverage["with_fru_sector"] / coverage["total_2024_accounts"] * 100.0, 2)
coverage["fru_subsector_coverage_pct"] = round(coverage["with_fru_subsector"] / coverage["total_2024_accounts"] * 100.0, 2)

# Totals
all_2024_total = sum((x["gpv_total"] for x in accounts_2024.values()), Decimal("0"))
all_2025_total = sum((x["gpv_total"] for x in accounts_2025.values()), Decimal("0"))

faith_2024_total = sum((accounts_2024[a]["gpv_total"] for a in faith_account_ids if a in accounts_2024), Decimal("0"))
# align 2025 faith to official report total
faith_2025_total = faith_2025_report_total

cc_2024_total = all_2024_total - faith_2024_total
cc_2025_total = all_2025_total - faith_2025_total

# legacy/new split for 2025 C&C
ids_2024 = set(accounts_2024)
ids_2025 = set(accounts_2025)
legacy_ids_2025 = (ids_2025 & ids_2024) - faith_account_ids
new_ids_2025 = (ids_2025 - ids_2024) - faith_account_ids

legacy_2025_gpv = sum((accounts_2025[a]["gpv_total"] for a in legacy_ids_2025), Decimal("0"))
new_2025_gpv = sum((accounts_2025[a]["gpv_total"] for a in new_ids_2025), Decimal("0"))

# one-time/recurring C&C totals
cc_2024_ot = sum((x["gpv_one_time"] for aid, x in accounts_2024.items() if aid not in faith_account_ids), Decimal("0"))
cc_2024_rec = sum((x["gpv_recurring"] for aid, x in accounts_2024.items() if aid not in faith_account_ids), Decimal("0"))
cc_2025_ot = sum((accounts_2025[aid].get("gpv_one_time", Decimal("0")) for aid in ids_2025 if aid not in faith_account_ids), Decimal("0"))
cc_2025_rec = sum((accounts_2025[aid].get("gpv_recurring", Decimal("0")) for aid in ids_2025 if aid not in faith_account_ids), Decimal("0"))
legacy_2025_ot = sum(
    (accounts_2025[aid].get("gpv_one_time", Decimal("0")) for aid in legacy_ids_2025),
    Decimal("0"),
)
legacy_2025_rec = sum(
    (accounts_2025[aid].get("gpv_recurring", Decimal("0")) for aid in legacy_ids_2025),
    Decimal("0"),
)
new_2025_ot = sum(
    (accounts_2025[aid].get("gpv_one_time", Decimal("0")) for aid in new_ids_2025),
    Decimal("0"),
)
new_2025_rec = sum(
    (accounts_2025[aid].get("gpv_recurring", Decimal("0")) for aid in new_ids_2025),
    Decimal("0"),
)

# Brackets for analytical targeting
brackets = [
    {"id": "lt_100k", "label": "<0.1M", "min": 0, "max": 100000},
    {"id": "100k_500k", "label": "0.1-0.5M", "min": 100000, "max": 500000},
    {"id": "500k_1m", "label": "0.5-1M", "min": 500000, "max": 1000000},
    {"id": "1m_5m", "label": "1-5M", "min": 1000000, "max": 5000000},
    {"id": "5m_10m", "label": "5-10M", "min": 5000000, "max": 10000000},
    {"id": "10m_plus", "label": "10M+", "min": 10000000, "max": None},
]


def in_bucket(v: float, b):
    upper = b["max"]
    return v >= b["min"] and (upper is None or v < upper)


cc_2025_values = [float(accounts_2025[aid]["gpv_total"]) for aid in ids_2025 if aid not in faith_account_ids]
cc_new_2025_values = [float(accounts_2025[aid]["gpv_total"]) for aid in new_ids_2025]

all_bracket_stats = []
new_bracket_stats = []

for b in brackets:
    all_vals = [v for v in cc_2025_values if in_bucket(v, b)]
    new_vals = [v for v in cc_new_2025_values if in_bucket(v, b)]
    all_bracket_stats.append(
        {
            "id": b["id"],
            "label": b["label"],
            "account_count": len(all_vals),
            "gpv_total": round(sum(all_vals), 2),
            "share_of_accounts": round((len(all_vals) / len(cc_2025_values) * 100.0) if cc_2025_values else 0.0, 2),
            "share_of_gpv": round((sum(all_vals) / sum(cc_2025_values) * 100.0) if cc_2025_values else 0.0, 2),
        }
    )
    new_bracket_stats.append(
        {
            "id": b["id"],
            "label": b["label"],
            "account_count": len(new_vals),
            "gpv_total": round(sum(new_vals), 2),
            "share_of_accounts": round((len(new_vals) / len(cc_new_2025_values) * 100.0) if cc_new_2025_values else 0.0, 2),
            "share_of_gpv": round((sum(new_vals) / sum(cc_new_2025_values) * 100.0) if cc_new_2025_values else 0.0, 2),
            "avg_year1_gpv": round((sum(new_vals) / len(new_vals)) if new_vals else 0.0, 2),
            "median_year1_gpv": round(percentile(new_vals, 50), 2),
        }
    )

# initial assumptions per discussion
monthly_retention = Decimal("1") - (Decimal("1") / Decimal("16"))
annual_recurring_carryover = monthly_retention ** Decimal("12")
one_time_repeat_rate = Decimal("0.4")
new_donor_recurring_share = Decimal("0.3")

# Calibrate existing-account expansion from observed 2024 legacy -> 2025 legacy KPI.
observed_legacy_nrr = (legacy_2025_gpv / cc_2024_total) if cc_2024_total else Decimal("0")
carryover_component_ratio = (
    ((cc_2024_ot * one_time_repeat_rate) + (cc_2024_rec * annual_recurring_carryover)) / cc_2024_total
    if cc_2024_total
    else Decimal("0")
)
implied_existing_expansion_rate = observed_legacy_nrr - carryover_component_ratio
if implied_existing_expansion_rate < 0:
    implied_existing_expansion_rate = Decimal("0")

model = {
    "metadata": {
        "title": "Cause&Cure Growth Model",
        "description": "C&C model built as Total FRU GPV minus Faith-based GPV.",
        "currency": "USD",
        "unit": "M",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_files": [
            str(INPUTS / "2024_all_accounts_donations.csv"),
            str(INPUTS / "2025_all_orgs_dontations__fru_enriched.csv"),
            str(INPUTS / "All Accounts Volume by Source & Frequency (2025).csv"),
            str(INPUTS / "religious_accounts_donation_volume_report.csv"),
            str(INPUTS / "FUNDRAISEUP sectors.csv"),
        ],
    },
    "targets": {
        "cc_gpv_m": {
            "2024": q2(cc_2024_total / Decimal("1000000")),
            "2025": q2(cc_2025_total / Decimal("1000000")),
            "2026": 2300.0,
            "2027": 3900.0,
            "2028": 6840.0,
        },
        "take_rate": 0.03,
    },
    "historical": {
        "all_gpv": {
            "2024": q2(all_2024_total),
            "2025": q2(all_2025_total),
        },
        "faith_gpv": {
            "2024": q2(faith_2024_total),
            "2025": q2(faith_2025_total),
        },
        "cc_gpv": {
            "2024": q2(cc_2024_total),
            "2025": q2(cc_2025_total),
        },
        "cohort_anchor_2025": {
            "legacy_contribution": q2(legacy_2025_gpv),
            "new_2025_contribution": q2(new_2025_gpv),
            "legacy_one_time": q2(legacy_2025_ot),
            "legacy_recurring": q2(legacy_2025_rec),
            "new_one_time": q2(new_2025_ot),
            "new_recurring": q2(new_2025_rec),
        },
        "cc_one_time_recurring": {
            "2024": {
                "one_time": q2(cc_2024_ot),
                "recurring": q2(cc_2024_rec),
                "recurring_share": q2((cc_2024_rec / (cc_2024_ot + cc_2024_rec)) if (cc_2024_ot + cc_2024_rec) else Decimal("0")),
            },
            "2025": {
                "one_time": q2(cc_2025_ot),
                "recurring": q2(cc_2025_rec),
                "recurring_share": q2((cc_2025_rec / (cc_2025_ot + cc_2025_rec)) if (cc_2025_ot + cc_2025_rec) else Decimal("0")),
            },
        },
        "legacy_observed_kpis": {
            "nrr_2024_to_2025": q2(observed_legacy_nrr),
            "carryover_component_ratio": q2(carryover_component_ratio),
            "implied_existing_account_expansion_rate": q2(implied_existing_expansion_rate),
        },
    },
    "segmentation": {
        "taxonomy": {
            "primary": "FRU Sector/Subsector",
            "secondary": "NTEE",
        },
        "coverage_2024_known_accounts": coverage,
        "analytical_brackets": brackets,
        "cc_2025_distribution": all_bracket_stats,
        "cc_2025_new_accounts_distribution": new_bracket_stats,
    },
    "assumptions": {
        "recurring_donor_lifetime_months": 16,
        "annual_recurring_carryover": q2(annual_recurring_carryover),
        "new_donor_year1_split": {"one_time": q2(Decimal("1") - new_donor_recurring_share), "recurring": q2(new_donor_recurring_share)},
        "one_time_donor_year2_repeat_rate": q2(one_time_repeat_rate),
        "existing_account_expansion_rate": q2(implied_existing_expansion_rate),
        "cohort_year2_nrr": 1.35,
        "new_account_year1_to_year2_gpv_ratio": q2(Decimal("1") / Decimal("1.35")),
        "max_new_whales_per_year": 2,
        "bracket_mix_shift_2026_2028": "none",
    },
    "notes": [
        "2024 is treated as Legacy cohort because pre-2024 data is unavailable.",
        "Detailed phase-2 modeling will be by FRU Sector/Subsector.",
        "NTEE is retained for validation and reconciliation.",
    ],
}

OUT.write_text(json.dumps(model, indent=2), encoding="utf-8")
OUT_JS.write_text("window.GROWTH_MODEL_DATA = " + json.dumps(model, indent=2) + ";\n", encoding="utf-8")
with OUT_COVERAGE.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "account_id",
            "account_name",
            "match_source",
            "ntee_code",
            "fru_sector",
            "fru_subsector",
        ],
    )
    writer.writeheader()
    writer.writerows(coverage_rows)
print(f"Wrote {OUT}")
print(f"Wrote {OUT_JS}")
print(f"Wrote {OUT_COVERAGE}")
