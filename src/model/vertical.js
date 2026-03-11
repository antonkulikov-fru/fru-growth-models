import { clamp01 } from "./overrides.js";

export const verticalOptions = [
  { id: "all", label: "All" },
  { id: "cc", label: "C&C" },
  { id: "faith", label: "Faith" },
];

export const verticalDefinitionById = {
  all: "All GPV = Total FRU GPV.",
  cc: "C&C GPV = Total FRU GPV - Faith-based GPV.",
  faith: "Faith GPV = Faith-based GPV.",
};

export function getFaithShareSplitByYear({ data, faithShareOverridesByYear, faithShareTarget2028 }) {
  const allTargets = (((data.verticals || {}).all || {}).targets_gpv_m || {});
  const faithTargets = (((data.verticals || {}).faith || {}).targets_gpv_m || {});
  const all2025 = Number(allTargets["2025"] || 0);
  const faith2025 = Number(faithTargets["2025"] || 0);

  let faithShare2025 = 0;
  if (all2025 > 0) {
    faithShare2025 = clamp01(faith2025 / all2025);
  } else {
    const histAll2025 = Number((((data.historical || {}).all_gpv || {})["2025"] || 0)) / 1_000_000;
    const histFaith2025 = Number((((data.historical || {}).faith_gpv || {})["2025"] || 0)) / 1_000_000;
    faithShare2025 = histAll2025 > 0 ? clamp01(histFaith2025 / histAll2025) : 0;
  }

  const defaults = {
    2026: faithShare2025,
    2027: clamp01(faithShare2025 + ((faithShareTarget2028 - faithShare2025) * 0.5)),
    2028: clamp01(faithShareTarget2028),
  };

  return {
    2026: clamp01(faithShareOverridesByYear["2026"] ?? defaults["2026"]),
    2027: clamp01(faithShareOverridesByYear["2027"] ?? defaults["2027"]),
    2028: clamp01(faithShareOverridesByYear["2028"] ?? defaults["2028"]),
  };
}

export function getFallbackTargetsGpvM(data, verticalId) {
  const ccTargets = data.targets.cc_gpv_m || {};
  const cc2025 = Number(ccTargets["2025"] || 0);
  const scale2026 = cc2025 > 0 ? Number(ccTargets["2026"] || 0) / cc2025 : 1;
  const scale2027 = cc2025 > 0 ? Number(ccTargets["2027"] || 0) / cc2025 : 1;
  const scale2028 = cc2025 > 0 ? Number(ccTargets["2028"] || 0) / cc2025 : 1;

  if (verticalId === "cc") return ccTargets;

  const hist = data.historical || {};
  const gpv = verticalId === "faith" ? (hist.faith_gpv || {}) : (hist.all_gpv || {});
  const y2025 = Number(gpv["2025"] || 0) / 1_000_000;
  return {
    "2024": Number(gpv["2024"] || 0) / 1_000_000,
    "2025": y2025,
    "2026": y2025 * scale2026,
    "2027": y2025 * scale2027,
    "2028": y2025 * scale2028,
  };
}

export function getVerticalData(data, verticalId) {
  const v = (data.verticals || {})[verticalId];
  if (v) {
    return {
      id: verticalId,
      label: v.label || verticalId,
      targetsGpvM: v.targets_gpv_m || {},
      cohortAnchor2025: ((v.historical || {}).cohort_anchor_2025) || {},
      oneTimeRecurring: ((v.historical || {}).one_time_recurring) || {},
      legacyObservedKpis: ((v.historical || {}).legacy_observed_kpis) || {},
      distribution2025: ((v.segmentation || {}).distribution_2025) || [],
      newAccountsDistribution2025: ((v.segmentation || {}).new_accounts_distribution_2025) || [],
    };
  }

  const hist = data.historical || {};
  if (verticalId === "cc") {
    return {
      id: "cc",
      label: "C&C",
      targetsGpvM: data.targets.cc_gpv_m || {},
      cohortAnchor2025: hist.cohort_anchor_2025 || {},
      oneTimeRecurring: hist.cc_one_time_recurring || {},
      legacyObservedKpis: hist.legacy_observed_kpis || {},
      distribution2025: (data.segmentation || {}).cc_2025_distribution || [],
      newAccountsDistribution2025: (data.segmentation || {}).cc_2025_new_accounts_distribution || [],
    };
  }

  return {
    id: verticalId,
    label: verticalId === "all" ? "All" : "Faith",
    targetsGpvM: getFallbackTargetsGpvM(data, verticalId),
    cohortAnchor2025: {},
    oneTimeRecurring: {},
    legacyObservedKpis: {},
    distribution2025: [],
    newAccountsDistribution2025: [],
  };
}

export function buildMixBaselines(vertical) {
  const defaultWeightsById = {};
  const legacyBaselineById = {};
  const dist = vertical.newAccountsDistribution2025 || [];
  const allDist = vertical.distribution2025 || [];
  const newDistById = {};
  dist.forEach((b) => {
    newDistById[b.id] = b;
  });

  let newTotalGpv = 0;
  dist.forEach((b) => {
    newTotalGpv += Number(b.gpv_total || 0);
  });
  dist.forEach((b) => {
    defaultWeightsById[b.id] = newTotalGpv > 0
      ? Number(b.gpv_total || 0) / newTotalGpv
      : (1 / Math.max(1, dist.length));
  });

  let legacyTotalGpv = 0;
  const legacyShareById = {};
  allDist.forEach((b) => {
    const newPart = Number((newDistById[b.id] || {}).gpv_total || 0);
    const legacyGpv = Math.max(0, Number(b.gpv_total || 0) - newPart);
    legacyShareById[b.id] = { gpv: legacyGpv };
    legacyTotalGpv += legacyGpv;
  });
  Object.keys(legacyShareById).forEach((id) => {
    legacyShareById[id].sharePct = legacyTotalGpv > 0 ? (legacyShareById[id].gpv / legacyTotalGpv) * 100 : 0;
  });

  dist.forEach((b) => {
    const baselinePct = (legacyShareById[b.id] || {}).sharePct ?? Number(b.share_of_gpv || 0);
    legacyBaselineById[b.id] = baselinePct;
  });

  return { defaultWeightsById, legacyBaselineById };
}
