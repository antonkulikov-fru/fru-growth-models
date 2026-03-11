import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { fmt, fmtDeltaPp, fmtLogo, fmtM, fmtSharePct, pct } from "../../src/model/formatters.js";
import {
  clamp01,
  formatPercentInputValue,
  loadFaithShareOverridesFromStorage,
  loadTargetOverridesFromStorage,
  normalizeFaithShareOverrides,
  normalizeTargetOverrides,
  readFaithShareInputValue,
  saveFaithShareOverridesToStorage,
  saveTargetOverridesToStorage,
} from "../../src/model/overrides.js";
import {
  buildMixBaselines,
  getFaithShareSplitByYear,
  getVerticalData,
  verticalDefinitionById,
  verticalOptions,
} from "../../src/model/vertical.js";
import { getCalibrationConfig } from "../../src/model/targets.js";

function makeStorage() {
  const state = new Map();
  return {
    getItem(key) {
      return state.has(key) ? state.get(key) : null;
    },
    setItem(key, value) {
      state.set(key, String(value));
    },
  };
}

describe("model formatters", () => {
  it("formats money, percent, and deltas consistently", () => {
    assert.equal(fmtM(1234.56), "$1,234.6");
    assert.equal(fmt(1234.567), "1,234.57");
    assert.equal(fmtLogo(0), "0");
    assert.equal(pct(0.125), "12.5%");
    assert.equal(fmtSharePct(0.1234), "12.34%");
    assert.equal(fmtDeltaPp(1.2345), "+1.234pp");
  });
});

describe("override normalization and persistence", () => {
  it("normalizes direct and legacy target override shapes", () => {
    assert.deepEqual(normalizeTargetOverrides({ 2026: 100, 2027: 200 }), { 2026: 100, 2027: 200 });
    assert.deepEqual(
      normalizeTargetOverrides({ cc: { 2026: 10, 2028: 40 } }),
      { 2026: 10, 2028: 40 },
    );
  });

  it("normalizes faith share values and clamps into [0, 1]", () => {
    assert.deepEqual(
      normalizeFaithShareOverrides({ 2026: 25, 2027: 0.5, 2028: 120 }),
      { 2026: 0.25, 2027: 0.5, 2028: 1 },
    );
    assert.equal(clamp01(-2), 0);
    assert.equal(clamp01(2), 1);
  });

  it("reads and writes overrides using storage adapter", () => {
    const storage = makeStorage();

    saveTargetOverridesToStorage({ 2026: 1, 2027: 2, 2028: 3 }, storage);
    saveFaithShareOverridesToStorage({ 2026: 20, 2027: 0.3 }, storage);

    assert.deepEqual(loadTargetOverridesFromStorage(storage), { 2026: 1, 2027: 2, 2028: 3 });
    assert.deepEqual(loadFaithShareOverridesFromStorage(storage), { 2026: 0.2, 2027: 0.3 });
  });

  it("handles percent input formatting and parsing", () => {
    assert.equal(formatPercentInputValue(0.12345), "12.35");
    assert.equal(readFaithShareInputValue({ value: "40" }), 0.4);
    assert.equal(readFaithShareInputValue({ value: "" }), null);
  });
});

describe("vertical model helpers", () => {
  const baseData = {
    targets: {
      cc_gpv_m: {
        2024: 100,
        2025: 200,
        2026: 300,
        2027: 450,
        2028: 600,
      },
    },
    historical: {
      all_gpv: { 2024: 300_000_000, 2025: 500_000_000 },
      faith_gpv: { 2024: 90_000_000, 2025: 100_000_000 },
      cohort_anchor_2025: {},
      cc_one_time_recurring: {},
      legacy_observed_kpis: {},
    },
    segmentation: {
      cc_2025_distribution: [],
      cc_2025_new_accounts_distribution: [],
    },
    verticals: {
      all: {
        label: "All",
        targets_gpv_m: { 2024: 300, 2025: 500, 2026: 700, 2027: 900, 2028: 1200 },
        historical: { cohort_anchor_2025: {}, one_time_recurring: {}, legacy_observed_kpis: {} },
        segmentation: { distribution_2025: [], new_accounts_distribution_2025: [] },
      },
      faith: {
        label: "Faith",
        targets_gpv_m: { 2024: 90, 2025: 100, 2026: 180, 2027: 270, 2028: 480 },
        historical: { cohort_anchor_2025: {}, one_time_recurring: {}, legacy_observed_kpis: {} },
        segmentation: { distribution_2025: [], new_accounts_distribution_2025: [] },
      },
    },
  };

  it("exposes vertical metadata constants", () => {
    assert.equal(verticalOptions.length, 3);
    assert.equal(verticalDefinitionById.cc, "C&C GPV = Total FRU GPV - Faith-based GPV.");
  });

  it("computes default and overridden faith share split", () => {
    const splitDefault = getFaithShareSplitByYear({
      data: baseData,
      faithShareOverridesByYear: {},
      faithShareTarget2028: 0.4,
    });
    assert.equal(splitDefault[2026], 0.2);
    assert.equal(splitDefault[2028], 0.4);

    const splitOverride = getFaithShareSplitByYear({
      data: baseData,
      faithShareOverridesByYear: { 2027: 0.33 },
      faithShareTarget2028: 0.4,
    });
    assert.equal(splitOverride[2027], 0.33);
  });

  it("resolves fallback vertical data when vertical is missing", () => {
    const resolved = getVerticalData(baseData, "cc");
    assert.equal(resolved.id, "cc");
    assert.equal(resolved.label, "C&C");
    assert.equal(resolved.targetsGpvM[2028], 600);
  });

  it("builds baseline mix weights from distribution data", () => {
    const baselines = buildMixBaselines({
      distribution2025: [
        { id: "a", gpv_total: 200 },
        { id: "b", gpv_total: 100 },
      ],
      newAccountsDistribution2025: [
        { id: "a", gpv_total: 50 },
        { id: "b", gpv_total: 50 },
      ],
    });

    assert.equal(baselines.defaultWeightsById.a, 0.5);
    assert.equal(baselines.defaultWeightsById.b, 0.5);
    assert.equal(Math.round(baselines.legacyBaselineById.a), 75);
    assert.equal(Math.round(baselines.legacyBaselineById.b), 25);
  });
});

describe("target calibration helpers", () => {
  it("ignores non-positive yearly targets for NRR solving", () => {
    const bothZero = getCalibrationConfig({ 2026: 0, 2027: 0 });
    assert.equal(bothZero.useAny, false);
    assert.equal(bothZero.use2026, false);
    assert.equal(bothZero.use2027, false);

    const only2027 = getCalibrationConfig({ 2026: 0, 2027: 1200 });
    assert.equal(only2027.useAny, true);
    assert.equal(only2027.use2026, false);
    assert.equal(only2027.use2027, true);
    assert.equal(only2027.target2027, 1200);
  });
});
