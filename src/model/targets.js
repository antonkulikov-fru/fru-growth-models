export function getCalibrationConfig(targets) {
  const target2026 = Number(targets[2026] || 0);
  const target2027 = Number(targets[2027] || 0);

  const use2026 = Number.isFinite(target2026) && target2026 > 0;
  const use2027 = Number.isFinite(target2027) && target2027 > 0;

  return {
    target2026,
    target2027,
    use2026,
    use2027,
    useAny: use2026 || use2027,
    scale2026: Math.max(1, Math.abs(target2026)),
    scale2027: Math.max(1, Math.abs(target2027)),
  };
}
