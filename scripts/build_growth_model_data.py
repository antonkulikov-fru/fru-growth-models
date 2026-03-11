#!/usr/bin/env python3
import csv
import json
import math
import os
import re
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = Path(os.environ.get("GROWTH_MODEL_INPUTS_DIR", ROOT / "_inputs" / "fru"))
OUT = Path(os.environ.get("GROWTH_MODEL_OUT_JSON", ROOT / "model" / "growth_model.data.json"))
OUT_JS = Path(os.environ.get("GROWTH_MODEL_OUT_JS", ROOT / "model" / "growth_model.data.js"))
OUT_COVERAGE = Path(os.environ.get("GROWTH_MODEL_OUT_COVERAGE", ROOT / "model" / "coverage_2024_enrichment.csv"))
ONTOLOGY = Path(os.environ.get("GROWTH_MODEL_ONTOLOGY", INPUTS / "ontology.json"))
RELIGIOUS_COHORTS = Path(
    os.environ.get("GROWTH_MODEL_RELIGIOUS_COHORTS", ROOT / "model" / "religious_cohorts_2024_2025.csv")
)
RELIGIOUS_REPORT_NEW = Path(
    os.environ.get(
        "GROWTH_MODEL_RELIGIOUS_REPORT_NEW",
        INPUTS / "2025_religious_accounts_donation_volume_report.csv",
    )
)
RELIGIOUS_REPORT_OLD = Path(
    os.environ.get(
        "GROWTH_MODEL_RELIGIOUS_REPORT_OLD",
        INPUTS / "religious_accounts_donation_volume_report.csv",
    )
)
RELIGIOUS_REPORT = RELIGIOUS_REPORT_NEW if RELIGIOUS_REPORT_NEW.exists() else RELIGIOUS_REPORT_OLD

# External market benchmark (US individual charitable giving).
# Source: Giving USA 2025 summary by Indiana University Lilly Family School of Philanthropy.
PERSONAL_GIVING_MARKET_BASE_2024_USD = Decimal("392450000000")  # $392.45B
PERSONAL_GIVING_MARKET_GROWTH_RATE = Decimal("0.05")  # 5.0% nominal growth assumption
RELIGION_SHARE_OF_TOTAL_GIVING_2024 = Decimal("146.54") / Decimal("592.50")  # 24.73% from Giving USA 2025
# Blackbaud channel context:
# 2023 online share: "rose from almost 8% in 2022 to over 12% in 2023" -> use 12.0% conservative baseline.
# 2024: online +2.2% YoY vs overall +1.9% YoY -> infer 2024 online share uplift.
ONLINE_GIVING_SHARE_BASE_2023 = Decimal("0.12")
ONLINE_GIVING_YOY_2024 = Decimal("1.022")
OVERALL_GIVING_YOY_2024 = Decimal("1.019")


def money(value: str) -> Decimal:
    s = (value or "").strip().replace("$", "").replace(",", "")
    return Decimal(s) if s else Decimal("0")


def q2(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def q4(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


def pretty_surface_name(surface_id: str) -> str:
    if surface_id == "api":
        return "API"
    return surface_id.replace("_", " ").title()


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

# Faith accounts list and totals.
faith_account_ids = set()
faith_2025_report_total = Decimal("0")
faith_2024_cohort_total = Decimal("0")
faith_2025_cohort_total = Decimal("0")
religious_source_files = []

if RELIGIOUS_COHORTS.exists():
    with RELIGIOUS_COHORTS.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            account_id = (row.get("account_id") or "").strip()
            if not account_id:
                continue
            faith_account_ids.add(account_id)
            faith_2024_cohort_total += money(row.get("gpv_2024_usd"))
            faith_2025_cohort_total += money(row.get("gpv_2025_usd"))
    religious_source_files.append(str(RELIGIOUS_COHORTS))
else:
    with RELIGIOUS_REPORT.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            account_id = (row.get("Account ID") or "").strip()
            if not account_id:
                continue
            faith_account_ids.add(account_id)
            faith_2025_report_total += money(row.get("Total Donation Volume $"))
    religious_source_files.append(str(RELIGIOUS_REPORT))

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
coverage_base = coverage["total_2024_accounts"]
if coverage_base > 0:
    coverage["coverage_pct"] = round(coverage["covered_total"] / coverage_base * 100.0, 2)
    coverage["ntee_coverage_pct"] = round(coverage["with_ntee_code"] / coverage_base * 100.0, 2)
    coverage["fru_sector_coverage_pct"] = round(coverage["with_fru_sector"] / coverage_base * 100.0, 2)
    coverage["fru_subsector_coverage_pct"] = round(coverage["with_fru_subsector"] / coverage_base * 100.0, 2)
else:
    coverage["coverage_pct"] = 0.0
    coverage["ntee_coverage_pct"] = 0.0
    coverage["fru_sector_coverage_pct"] = 0.0
    coverage["fru_subsector_coverage_pct"] = 0.0

# Ontology: execution surfaces
surface_types = ["website", "donor_portal", "mobile_app", "virtual_terminal", "api"]
if ONTOLOGY.exists():
    try:
        ontology = json.loads(ONTOLOGY.read_text(encoding="utf-8"))
        surface_types_raw = (
            (((ontology or {}).get("domain_model") or {}).get("execution_surfaces") or {}).get("types")
            or []
        )
        parsed_surface_types = [str(s).strip() for s in surface_types_raw if str(s).strip()]
        if parsed_surface_types:
            surface_types = parsed_surface_types
    except Exception:
        pass


def aggregate_surface_totals_from_report(path: Path, encoding: str, delimiter: str):
    # Surface mapping from raw source export columns to ontology execution surfaces.
    source_columns_by_surface = {
        "website": [
            "Website with Elements, Onetime #",
            "Website with Elements, Recurring #",
            "Website without Elements, One-time #",
            "Website without Elements, Recurring #",
        ],
        "donor_portal": [
            "Campaign Pages, One-time #",
            "Campaign Pages, Recurring #",
            "P2P, One-time #",
            "P2P, Recurring #",
            "Recurring Migrations, #",
        ],
        "mobile_app": [],
        "virtual_terminal": [
            "Virtual Terminal, One-time #",
            "Virtual Terminal, Recurring #",
        ],
        "api": [
            "API, One-time #",
            "API, Recurring #",
        ],
    }
    totals_by_surface = {s: Decimal("0") for s in surface_types}
    total_gpv = Decimal("0")
    with path.open("r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            account_id = (row.get("Account ID") or "").strip()
            if not account_id or account_id == "Total":
                continue
            total_gpv += money(row.get("Total Donations Volume $"))
            for s in surface_types:
                for col in source_columns_by_surface.get(s, []):
                    totals_by_surface[s] += money(row.get(col))

    mapped_total = sum(totals_by_surface.values(), Decimal("0"))
    if mapped_total > 0 and total_gpv > 0:
        # Normalize to total GPV to absorb tiny source rounding drift.
        scale = total_gpv / mapped_total
        totals_by_surface = {k: v * scale for k, v in totals_by_surface.items()}
    return total_gpv, totals_by_surface


surface_totals_2024_total, surface_totals_2024 = aggregate_surface_totals_from_report(
    INPUTS / "2024_all_accounts_donations.csv", "utf-16", "\t"
)
surface_totals_2025_total, surface_totals_2025 = aggregate_surface_totals_from_report(
    INPUTS / "All Accounts Volume by Source & Frequency (2025).csv", "utf-8-sig", ","
)

surface_share_2024 = {
    s: (surface_totals_2024[s] / surface_totals_2024_total) if surface_totals_2024_total > 0 else Decimal("0")
    for s in surface_types
}
surface_share_2025 = {
    s: (surface_totals_2025[s] / surface_totals_2025_total) if surface_totals_2025_total > 0 else Decimal("0")
    for s in surface_types
}

# Totals
ids_2024 = set(accounts_2024)
ids_2025 = set(accounts_2025)

all_2024_total = sum((x["gpv_total"] for x in accounts_2024.values()), Decimal("0"))
all_2025_total = sum((x["gpv_total"] for x in accounts_2025.values()), Decimal("0"))

faith_2024_total = (
    faith_2024_cohort_total
    if faith_2024_cohort_total > 0
    else sum((accounts_2024[a]["gpv_total"] for a in faith_account_ids if a in accounts_2024), Decimal("0"))
)
faith_2025_total = faith_2025_cohort_total if faith_2025_cohort_total > 0 else faith_2025_report_total

cc_2024_total = all_2024_total - faith_2024_total
cc_2025_total = all_2025_total - faith_2025_total

vertical_labels = {
    "all": "All",
    "cc": "C&C",
    "faith": "Faith",
}

vertical_ids = {
    "all": {
        "2024": set(ids_2024),
        "2025": set(ids_2025),
    },
    "cc": {
        "2024": {aid for aid in ids_2024 if aid not in faith_account_ids},
        "2025": {aid for aid in ids_2025 if aid not in faith_account_ids},
    },
    "faith": {
        "2024": {aid for aid in ids_2024 if aid in faith_account_ids},
        "2025": {aid for aid in ids_2025 if aid in faith_account_ids},
    },
}
for k in vertical_ids:
    vertical_ids[k]["legacy_2025"] = vertical_ids[k]["2025"] & vertical_ids[k]["2024"]
    vertical_ids[k]["new_2025"] = vertical_ids[k]["2025"] - vertical_ids[k]["2024"]

totals_by_vertical = {
    "all": {"2024": all_2024_total, "2025": all_2025_total},
    "cc": {"2024": cc_2024_total, "2025": cc_2025_total},
    "faith": {"2024": faith_2024_total, "2025": faith_2025_total},
}

one_time_recurring_by_vertical = {}
cohort_anchor_by_vertical = {}
for k in ("all", "cc", "faith"):
    ids24 = vertical_ids[k]["2024"]
    ids25 = vertical_ids[k]["2025"]
    legacy_ids_2025 = vertical_ids[k]["legacy_2025"]
    new_ids_2025 = vertical_ids[k]["new_2025"]

    y24_ot = sum((accounts_2024[aid]["gpv_one_time"] for aid in ids24), Decimal("0"))
    y24_rec = sum((accounts_2024[aid]["gpv_recurring"] for aid in ids24), Decimal("0"))
    y25_ot = sum((accounts_2025[aid].get("gpv_one_time", Decimal("0")) for aid in ids25), Decimal("0"))
    y25_rec = sum((accounts_2025[aid].get("gpv_recurring", Decimal("0")) for aid in ids25), Decimal("0"))

    one_time_recurring_by_vertical[k] = {
        "2024": {"one_time": y24_ot, "recurring": y24_rec},
        "2025": {"one_time": y25_ot, "recurring": y25_rec},
    }

    legacy_2025_gpv = sum((accounts_2025[aid]["gpv_total"] for aid in legacy_ids_2025), Decimal("0"))
    new_2025_gpv = sum((accounts_2025[aid]["gpv_total"] for aid in new_ids_2025), Decimal("0"))
    legacy_2025_ot = sum((accounts_2025[aid].get("gpv_one_time", Decimal("0")) for aid in legacy_ids_2025), Decimal("0"))
    legacy_2025_rec = sum((accounts_2025[aid].get("gpv_recurring", Decimal("0")) for aid in legacy_ids_2025), Decimal("0"))
    new_2025_ot = sum((accounts_2025[aid].get("gpv_one_time", Decimal("0")) for aid in new_ids_2025), Decimal("0"))
    new_2025_rec = sum((accounts_2025[aid].get("gpv_recurring", Decimal("0")) for aid in new_ids_2025), Decimal("0"))
    cohort_anchor_by_vertical[k] = {
        "legacy_contribution": legacy_2025_gpv,
        "new_2025_contribution": new_2025_gpv,
        "legacy_one_time": legacy_2025_ot,
        "legacy_recurring": legacy_2025_rec,
        "new_one_time": new_2025_ot,
        "new_recurring": new_2025_rec,
    }

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


def build_bracket_stats(values_2025, new_values_2025):
    all_bracket_stats = []
    new_bracket_stats = []
    for b in brackets:
        all_vals = [v for v in values_2025 if in_bucket(v, b)]
        new_vals = [v for v in new_values_2025 if in_bucket(v, b)]
        all_bracket_stats.append(
            {
                "id": b["id"],
                "label": b["label"],
                "account_count": len(all_vals),
                "gpv_total": round(sum(all_vals), 2),
                "share_of_accounts": round((len(all_vals) / len(values_2025) * 100.0) if values_2025 else 0.0, 2),
                "share_of_gpv": round((sum(all_vals) / sum(values_2025) * 100.0) if values_2025 else 0.0, 2),
            }
        )
        new_bracket_stats.append(
            {
                "id": b["id"],
                "label": b["label"],
                "account_count": len(new_vals),
                "gpv_total": round(sum(new_vals), 2),
                "share_of_accounts": round((len(new_vals) / len(new_values_2025) * 100.0) if new_values_2025 else 0.0, 2),
                "share_of_gpv": round((sum(new_vals) / sum(new_values_2025) * 100.0) if new_values_2025 else 0.0, 2),
                "avg_year1_gpv": round((sum(new_vals) / len(new_vals)) if new_vals else 0.0, 2),
                "median_year1_gpv": round(percentile(new_vals, 50), 2),
            }
        )
    return all_bracket_stats, new_bracket_stats


segmentation_by_vertical = {}
for k in ("all", "cc", "faith"):
    ids25 = vertical_ids[k]["2025"]
    new25 = vertical_ids[k]["new_2025"]
    values_2025 = [float(accounts_2025[aid]["gpv_total"]) for aid in ids25]
    new_values_2025 = [float(accounts_2025[aid]["gpv_total"]) for aid in new25]
    all_stats, new_stats = build_bracket_stats(values_2025, new_values_2025)
    segmentation_by_vertical[k] = {
        "distribution_2025": all_stats,
        "new_accounts_distribution_2025": new_stats,
    }

# initial assumptions per discussion
monthly_retention = Decimal("1") - (Decimal("1") / Decimal("16"))
annual_recurring_carryover = monthly_retention ** Decimal("12")
one_time_repeat_rate = Decimal("0.4")
new_donor_recurring_share = Decimal("0.3")
faith_cohort_nrr_override = Decimal("1.35")

# Calibrate existing-account expansion per vertical from observed 2024 legacy -> 2025 legacy KPI.
vertical_kpis = {}
for k in ("all", "cc", "faith"):
    t2024 = totals_by_vertical[k]["2024"]
    y24_ot = one_time_recurring_by_vertical[k]["2024"]["one_time"]
    y24_rec = one_time_recurring_by_vertical[k]["2024"]["recurring"]
    legacy_2025_gpv = cohort_anchor_by_vertical[k]["legacy_contribution"]

    observed_legacy_nrr = (legacy_2025_gpv / t2024) if t2024 else Decimal("0")
    if k == "faith":
        observed_legacy_nrr = faith_cohort_nrr_override
    carryover_component_ratio = (
        ((y24_ot * one_time_repeat_rate) + (y24_rec * annual_recurring_carryover)) / t2024
        if t2024
        else Decimal("0")
    )
    implied_existing_expansion_rate = observed_legacy_nrr - carryover_component_ratio
    if implied_existing_expansion_rate < 0:
        implied_existing_expansion_rate = Decimal("0")

    vertical_kpis[k] = {
        "nrr_2024_to_2025": q2(observed_legacy_nrr),
        "carryover_component_ratio": q2(carryover_component_ratio),
        "implied_existing_account_expansion_rate": q2(implied_existing_expansion_rate),
    }

cc_target_defaults = {
    "2026": 2300.0,
    "2027": 3900.0,
    "2028": 6840.0,
}
faith_target_defaults = {
    "2026": 502.0,
    "2027": 860.0,
    "2028": 1480.0,
}
cc_2025_m = q2(cc_2025_total / Decimal("1000000"))
growth_multipliers = {
    y: (cc_target_defaults[y] / cc_2025_m if cc_2025_m else 1.0)
    for y in ("2026", "2027", "2028")
}


def build_targets_gpv_m(vertical_key: str):
    t2024 = totals_by_vertical[vertical_key]["2024"] / Decimal("1000000")
    t2025 = totals_by_vertical[vertical_key]["2025"] / Decimal("1000000")
    out = {
        "2024": q2(t2024),
        "2025": q2(t2025),
    }
    if vertical_key == "cc":
        out.update(cc_target_defaults)
    elif vertical_key == "faith":
        out.update(faith_target_defaults)
    else:
        for y in ("2026", "2027", "2028"):
            out[y] = q2(t2025 * Decimal(str(growth_multipliers[y])))
    return out


verticals = {}
for k in ("all", "cc", "faith"):
    y24_ot = one_time_recurring_by_vertical[k]["2024"]["one_time"]
    y24_rec = one_time_recurring_by_vertical[k]["2024"]["recurring"]
    y25_ot = one_time_recurring_by_vertical[k]["2025"]["one_time"]
    y25_rec = one_time_recurring_by_vertical[k]["2025"]["recurring"]

    verticals[k] = {
        "id": k,
        "label": vertical_labels[k],
        "targets_gpv_m": build_targets_gpv_m(k),
        "historical": {
            "gpv": {
                "2024": q2(totals_by_vertical[k]["2024"]),
                "2025": q2(totals_by_vertical[k]["2025"]),
            },
            "cohort_anchor_2025": {
                kk: q2(vv) for kk, vv in cohort_anchor_by_vertical[k].items()
            },
            "one_time_recurring": {
                "2024": {
                    "one_time": q2(y24_ot),
                    "recurring": q2(y24_rec),
                    "recurring_share": q2((y24_rec / (y24_ot + y24_rec)) if (y24_ot + y24_rec) else Decimal("0")),
                },
                "2025": {
                    "one_time": q2(y25_ot),
                    "recurring": q2(y25_rec),
                    "recurring_share": q2((y25_rec / (y25_ot + y25_rec)) if (y25_ot + y25_rec) else Decimal("0")),
                },
            },
            "legacy_observed_kpis": vertical_kpis[k],
        },
        "segmentation": {
            "distribution_2025": segmentation_by_vertical[k]["distribution_2025"],
            "new_accounts_distribution_2025": segmentation_by_vertical[k]["new_accounts_distribution_2025"],
        },
    }

personal_giving_market_years = {}
personal_giving_segments = {"faith": {"years": {}}, "cc": {"years": {}}}
personal_giving_surfaces = {
    s: {
        "name": pretty_surface_name(s),
        "years": {},
    }
    for s in surface_types
}
online_share_2024 = ONLINE_GIVING_SHARE_BASE_2023 * (ONLINE_GIVING_YOY_2024 / OVERALL_GIVING_YOY_2024)
if online_share_2024 < 0:
    online_share_2024 = Decimal("0")
if online_share_2024 > 1:
    online_share_2024 = Decimal("1")
offline_share_2024 = Decimal("1") - online_share_2024
personal_giving_channels = {
    "online": {"name": "Online", "years": {}},
    "offline": {"name": "Offline", "years": {}},
}
market_size = PERSONAL_GIVING_MARKET_BASE_2024_USD
current_year = datetime.now(timezone.utc).year
for year in (2024, 2025, 2026, 2027, 2028):
    year_key = str(year)
    state = "past" if year < current_year else ("present" if year == current_year else "future")
    faith_market_size = market_size * RELIGION_SHARE_OF_TOTAL_GIVING_2024
    cc_market_size = market_size - faith_market_size
    personal_giving_market_years[year_key] = {
        "state": state,
        "market_size_usd": q2(market_size),
        "is_actual": year == 2024,
    }
    personal_giving_segments["faith"]["years"][year_key] = {
        "share_of_total": q4(RELIGION_SHARE_OF_TOTAL_GIVING_2024),
        "market_size_usd": q2(faith_market_size),
    }
    personal_giving_segments["cc"]["years"][year_key] = {
        "share_of_total": q4(Decimal("1") - RELIGION_SHARE_OF_TOTAL_GIVING_2024),
        "market_size_usd": q2(cc_market_size),
    }
    for s in surface_types:
        if year == 2024:
            share = surface_share_2024.get(s, Decimal("0"))
            observed_volume = surface_totals_2024.get(s, Decimal("0"))
            is_observed = True
        elif year == 2025:
            share = surface_share_2025.get(s, Decimal("0"))
            observed_volume = surface_totals_2025.get(s, Decimal("0"))
            is_observed = True
        else:
            share = surface_share_2025.get(s, Decimal("0"))
            observed_volume = None
            is_observed = False
        personal_giving_surfaces[s]["years"][year_key] = {
            "share_of_total": q4(share),
            "market_size_usd": q2(market_size * share),
            "is_observed": is_observed,
            "observed_volume_usd": q2(observed_volume) if observed_volume is not None else None,
        }
    if year == 2024:
        channel_evidence = "inferred"
    else:
        channel_evidence = "projected"
    personal_giving_channels["online"]["years"][year_key] = {
        "share_of_total": q4(online_share_2024),
        "market_size_usd": q2(market_size * online_share_2024),
        "evidence": channel_evidence,
    }
    personal_giving_channels["offline"]["years"][year_key] = {
        "share_of_total": q4(offline_share_2024),
        "market_size_usd": q2(market_size * offline_share_2024),
        "evidence": channel_evidence,
    }
    market_size = market_size * (Decimal("1") + PERSONAL_GIVING_MARKET_GROWTH_RATE)

model = {
    "metadata": {
        "title": "Growth Model",
        "description": "Global growth model with vertical switch for All, C&C, and Faith.",
        "currency": "USD",
        "unit": "M",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_files": [
            str(INPUTS / "2024_all_accounts_donations.csv"),
            str(INPUTS / "2025_all_orgs_dontations__fru_enriched.csv"),
            str(INPUTS / "All Accounts Volume by Source & Frequency (2025).csv"),
            *religious_source_files,
            str(INPUTS / "FUNDRAISEUP sectors.csv"),
            str(ONTOLOGY),
        ],
    },
    "verticals": verticals,
    "market": {
        "personal_giving": {
            "name": "US personal charitable giving (individuals)",
            "currency": "USD",
            "assumed_nominal_growth_rate": q4(PERSONAL_GIVING_MARKET_GROWTH_RATE),
            "projection_method": (
                "2024 is actual from Giving USA 2025. "
                "2025-2028 are projected at 5.0% nominal annual growth, aligned to "
                "Giving USA's 40-year average total giving growth in current dollars."
            ),
            "split_method": (
                "Faith market is proxied using Giving USA 2025 recipient split: "
                "Religion received $146.54B out of $592.50B total giving in 2024 (24.73%). "
                "This 24.73% share is applied to the personal giving market in 2024-2028; "
                "C&C market is the residual non-religious share."
            ),
            "surface_split_method": (
                "Execution surfaces are from ontology.json. 2024 and 2025 surface shares are estimated "
                "from FRU source columns: website=(with+without elements), donor_portal=(campaign pages+p2p+recurring migrations), "
                "virtual_terminal, api, mobile_app (no explicit export column). "
                "2026-2028 keep 2025 surface mix constant."
            ),
            "channel_split_method": (
                "Online/offline split uses Blackbaud public benchmarks. "
                "2023 online share baseline is 12.0% ('over 12%'). "
                "2024 online share is inferred by applying Blackbaud 2024 relative growth "
                "(online +2.2% vs overall +1.9%) to the 2023 baseline. "
                "2025-2028 hold 2024 inferred online share constant."
            ),
            "sources": [
                {
                    "name": "Giving USA 2025 summary (Indiana University Lilly Family School of Philanthropy)",
                    "url": "https://philanthropy.indianapolis.iu.edu/news-events/news/_news/2025/giving-usa-2025.html",
                    "published_at": "2025-06-24",
                },
                {
                    "name": "Blackbaud Institute 2024 Spotlight: online giving grew 2.2% (overall 1.9%)",
                    "url": "https://www.blackbaud.com/newsroom/article/blackbaud-institute-releases-2024-spotlight-on-trends-in-us-charitable-giving",
                    "published_at": "2025-02-11",
                },
                {
                    "name": "Blackbaud Institute 2023 Spotlight: online share rose to over 12% in 2023",
                    "url": "https://www.blackbaud.com/newsroom/article/blackbaud-institute-releases-2023-spotlight-on-trends-in-us-charitable-giving",
                    "published_at": "2024-02-20",
                }
            ],
            "years": personal_giving_market_years,
            "segments": {
                "faith": {
                    "name": "Religious market",
                    **personal_giving_segments["faith"],
                },
                "cc": {
                    "name": "Cause & Cure market (non-religious)",
                    **personal_giving_segments["cc"],
                },
            },
            "surfaces": personal_giving_surfaces,
            "channels": personal_giving_channels,
        }
    },
    "targets": {
        "cc_gpv_m": verticals["cc"]["targets_gpv_m"],
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
        "cohort_anchor_2025": verticals["cc"]["historical"]["cohort_anchor_2025"],
        "cc_one_time_recurring": verticals["cc"]["historical"]["one_time_recurring"],
        "legacy_observed_kpis": verticals["cc"]["historical"]["legacy_observed_kpis"],
    },
    "segmentation": {
        "taxonomy": {
            "primary": "FRU Sector/Subsector",
            "secondary": "NTEE",
        },
        "coverage_2024_known_accounts": coverage,
        "analytical_brackets": brackets,
        "cc_2025_distribution": verticals["cc"]["segmentation"]["distribution_2025"],
        "cc_2025_new_accounts_distribution": verticals["cc"]["segmentation"]["new_accounts_distribution_2025"],
        "by_vertical": {
            "all": verticals["all"]["segmentation"],
            "cc": verticals["cc"]["segmentation"],
            "faith": verticals["faith"]["segmentation"],
        },
    },
    "assumptions": {
        "recurring_donor_lifetime_months": 16,
        "annual_recurring_carryover": q2(annual_recurring_carryover),
        "new_donor_year1_split": {"one_time": q2(Decimal("1") - new_donor_recurring_share), "recurring": q2(new_donor_recurring_share)},
        "one_time_donor_year2_repeat_rate": q2(one_time_repeat_rate),
        "existing_account_expansion_rate": verticals["cc"]["historical"]["legacy_observed_kpis"]["implied_existing_account_expansion_rate"],
        "cohort_year1_nrr": 1.8,
        "cohort_year2plus_nrr": 1.15,
        "cohort_year2_nrr": 1.15,
        "new_account_year1_to_year2_gpv_ratio": 1.0,
        "lt_100k_year1_gpv_per_logo_override_m": 0.05,
        "max_new_whales_per_year": 2,
        "bracket_mix_shift_2026_2028": "none",
    },
    "notes": [
        "2024 is treated as Legacy cohort because pre-2024 data is unavailable.",
        "Model supports vertical switch: All, C&C, Faith.",
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
