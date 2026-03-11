export const fmtM = (n) => `$${Number(n).toLocaleString(undefined, { maximumFractionDigits: 1 })}`;

export const fmt = (n) => Number(n).toLocaleString(undefined, { maximumFractionDigits: 2 });

export const fmtLogo = (n) => {
  const v = Number(n);
  if (!Number.isFinite(v) || v === 0) return "0";
  const a = Math.abs(v);
  if (a >= 1) return v.toLocaleString(undefined, { maximumFractionDigits: 2 });
  if (a >= 0.1) return v.toLocaleString(undefined, { maximumFractionDigits: 3 });
  if (a >= 0.01) return v.toLocaleString(undefined, { maximumFractionDigits: 4 });
  if (a >= 0.001) return v.toLocaleString(undefined, { maximumFractionDigits: 5 });
  return v.toLocaleString(undefined, { maximumFractionDigits: 6 });
};

export const pct = (n) => `${(n * 100).toFixed(1)}%`;

export const fmtSharePct = (n) => {
  const p = Number(n) * 100;
  if (!Number.isFinite(p)) return "-";
  return `${(Math.abs(p) >= 1 ? p.toFixed(2) : p.toFixed(3))}%`;
};

export const fmtDeltaPp = (n) => {
  const v = Number(n);
  if (!Number.isFinite(v)) return "-";
  return `${v >= 0 ? "+" : ""}${v.toFixed(3)}pp`;
};
