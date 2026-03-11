export const TARGET_OVERRIDES_STORAGE_KEY = "growth-model:target-overrides:v1";
export const FAITH_SHARE_OVERRIDES_STORAGE_KEY = "growth-model:faith-share-overrides:v1";
export const TARGET_OVERRIDE_YEARS = ["2026", "2027", "2028"];
export const FAITH_SHARE_TARGET_2028 = 0.4;

export function clamp01(v) {
  return Math.min(1, Math.max(0, Number(v) || 0));
}

export function normalizeTargetOverrides(raw) {
  if (!raw || typeof raw !== "object") return {};

  const normalizeSeries = (series) => {
    if (!series || typeof series !== "object") return {};
    const out = {};
    TARGET_OVERRIDE_YEARS.forEach((year) => {
      const v = Number(series[year]);
      if (Number.isFinite(v)) out[year] = v;
    });
    return out;
  };

  const direct = normalizeSeries(raw);
  if (Object.keys(direct).length > 0) return direct;

  const legacyCandidates = [raw.all, raw.cc, raw.faith];
  for (const candidate of legacyCandidates) {
    const normalized = normalizeSeries(candidate);
    if (Object.keys(normalized).length > 0) return normalized;
  }
  return {};
}

export function normalizeFaithShareOverrides(raw) {
  if (!raw || typeof raw !== "object") return {};

  const normalized = {};
  TARGET_OVERRIDE_YEARS.forEach((year) => {
    let v = Number(raw[year]);
    if (!Number.isFinite(v)) return;
    if (v > 1 && v <= 100) v = v / 100;
    normalized[year] = clamp01(v);
  });
  return normalized;
}

export function loadTargetOverridesFromStorage(storage = globalThis.localStorage) {
  try {
    if (!storage) return {};
    const raw = storage.getItem(TARGET_OVERRIDES_STORAGE_KEY);
    if (!raw) return {};
    return normalizeTargetOverrides(JSON.parse(raw));
  } catch {
    return {};
  }
}

export function saveTargetOverridesToStorage(overrides, storage = globalThis.localStorage) {
  try {
    if (!storage) return;
    storage.setItem(TARGET_OVERRIDES_STORAGE_KEY, JSON.stringify(normalizeTargetOverrides(overrides)));
  } catch {}
}

export function loadFaithShareOverridesFromStorage(storage = globalThis.localStorage) {
  try {
    if (!storage) return {};
    const raw = storage.getItem(FAITH_SHARE_OVERRIDES_STORAGE_KEY);
    if (!raw) return {};
    return normalizeFaithShareOverrides(JSON.parse(raw));
  } catch {
    return {};
  }
}

export function saveFaithShareOverridesToStorage(overrides, storage = globalThis.localStorage) {
  try {
    if (!storage) return;
    storage.setItem(FAITH_SHARE_OVERRIDES_STORAGE_KEY, JSON.stringify(normalizeFaithShareOverrides(overrides)));
  } catch {}
}

export function formatPercentInputValue(v) {
  const p = clamp01(v) * 100;
  return String(Math.round(p * 100) / 100);
}

export function readFaithShareInputValue(el) {
  if (!el || String(el.value).trim() === "") return null;
  const raw = Number(el.value);
  if (!Number.isFinite(raw)) return null;
  return clamp01(raw / 100);
}
