# growth-modeling Test Documentation

## Test Framework Configuration

Frameworks:
- JavaScript: Node built-in test runner (`node:test`)
- Python: standard `unittest`

Commands:
- JS tests: `npm run test:js`
- Python tests: `npm run test:py`
- Full suite: `npm test`

## Test Suites

### PIPELINE-TEST-001: Religious cohort build outputs
- Status: ✅ COMPLETED
- Test file: `tests/python/test_data_pipeline_outputs.py`
- Scope:
  - `scripts/build_religious_cohorts_data.py` runs successfully
  - output files are generated
  - schema-critical CSV columns are present
  - key cohort totals match locked snapshot values

### PIPELINE-TEST-002: Growth model build outputs
- Status: ✅ COMPLETED
- Test file: `tests/python/test_data_pipeline_outputs.py`
- Scope:
  - `scripts/build_growth_model_data.py` runs successfully
  - output files are generated (`.json`, `.js`, coverage CSV)
  - top-level model integrity and key numerical anchors are validated

### FRONTEND-TEST-001: HTML logic extraction guard
- Status: ✅ COMPLETED
- Test file: `tests/js/frontend_structure.test.js`
- Scope:
  - `growth_model.html` loads model data script + module script only
  - no inline logic block remains in HTML
  - extracted app module is syntactically valid (`node --check`)

### FRONTEND-TEST-002: Extracted model module unit tests
- Status: ✅ COMPLETED
- Test file: `tests/js/model_modules.test.js`
- Scope:
  - formatter outputs and percentage rendering helpers
  - target/faith override normalization and storage behavior
  - vertical helper behavior (`getFaithShareSplitByYear`, `getVerticalData`, mix baselines)

### PIPELINE-TEST-003: Religious cohorts edge-case behavior
- Status: ✅ COMPLETED
- Test file: `tests/python/test_religious_cohorts_edge_cases.py`
- Scope:
  - handles empty effective input without crashes
  - writes CSV headers even when no rows exist
  - records missing-account-id quality checks correctly

## Coverage Goals (Phase 1)

- Python data pipeline characterization coverage: lock current output behavior.
- Frontend structure guard coverage: prevent logic regression into HTML.
- Frontend model helper unit coverage is now in place for extracted modules.
- Next phase: continue splitting `src/app.js` into compute/state/render modules with parity tests.

## Notes

This repository currently uses snapshot-style characterization tests first to protect behavior during refactoring.
