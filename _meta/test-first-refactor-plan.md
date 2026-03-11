# Test-First Refactor Plan

## Findings (ordered by risk)

1. Core business logic is tightly coupled inside one inline script, which makes safe refactoring difficult without characterization tests first.
   - References: `growth_model.html` lines 943, 1633, 1870.
2. Coverage percentage math can divide by zero when `total_2024_accounts == 0`, which can crash the data build.
   - Reference: `scripts/build_growth_model_data.py` line 264.
3. Religious cohort export assumes at least one row (`rows[0]`), causing `IndexError` when the source is empty.
   - Reference: `scripts/build_religious_cohorts_data.py` line 95.
4. Model numeric inputs are not runtime-clamped in JS compute paths; invalid values (for example `ltMonths=0`) can propagate `Infinity/NaN`.
   - References: `growth_model.html` lines 979, 988.
5. Ontology parsing errors are silently swallowed, hiding bad config/data quality issues.
   - Reference: `scripts/build_growth_model_data.py` line 271.

## Assumptions

1. Comprehensive coverage means unit + integration + browser-level characterization tests, with CI gates.
2. Phase 1 goal is behavior lock-in (golden tests), then module extraction with no formula changes.
3. Adding Node-based JS test tooling is acceptable.

## Execution Plan

1. Establish test harness and CI gates first.
   - Python: `pytest + coverage`.
   - JS/HTML: `vitest + playwright`.
   - Add minimum thresholds and fail CI below thresholds.
2. Add characterization tests for current HTML behavior before any refactor.
   - Default scenario outputs.
   - Vertical switch behavior.
   - Target split overrides and localStorage persistence.
   - Whale-cap redistribution behavior.
   - Market-share table outputs.
3. Add data-pipeline integration tests with small fixtures for both Python scripts.
   - Assert output files are generated.
   - Validate JSON output against schema.
   - Snapshot/aggregate checks while ignoring timestamp fields.
4. Add edge-case tests for known fragility points.
   - Zero 2024 accounts.
   - Empty religious rows.
   - Missing/invalid ontology.
   - Invalid numeric UI inputs.
5. Refactor only after tests are green: extract pure model logic from HTML.
   - Suggested modules: `src/model/engine.js`, `src/model/targets.js`, `src/model/acquisition.js`.
   - Keep behavior parity enforced by characterization tests.
6. Split UI concerns into dedicated modules.
   - DOM rendering.
   - Control wiring and event handling.
   - Storage adapter for local overrides.
7. Refactor Python scripts into importable modules with thin CLI wrappers.
   - Separate parsing, transforms, and output writers.
8. Harden and stabilize.
   - Replace silent fallbacks with explicit validation/reporting.
   - Add deterministic test mode for date/time dependent fields.
   - Ratchet coverage thresholds upward over time.
