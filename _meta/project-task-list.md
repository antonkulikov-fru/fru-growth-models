# growth-modeling Project Task List

## Current Tasks

- [x] **TEST-TASK-001: Establish test harness** - ✅ **COMPLETED**
  - Added `npm` test scripts for JS and Python suites.
- [x] **TEST-TASK-002: Add characterization tests for data pipeline** - ✅ **COMPLETED**
  - Added integration/snapshot checks for both build scripts.
- [x] **TEST-TASK-003: Add frontend structure guard tests** - ✅ **COMPLETED**
  - Added checks that logic is loaded via `src/app.js` module and not inline in HTML.
- [ ] **REFACTOR-TASK-001: Extract dedicated frontend modules from `src/app.js`** - 🟡 **IN PROGRESS**
  - Extracted and wired dedicated modules for formatters, overrides, and vertical helpers.
- [x] **REFACTOR-TASK-002: Add JS unit tests for extracted modules** - ✅ **COMPLETED**
  - Added `tests/js/model_modules.test.js` to validate extracted frontend modules.
- [ ] **REFACTOR-TASK-003: Refactor Python scripts into importable modules** - 🟡 **IN PROGRESS**
  - `build_religious_cohorts_data.py` now exposes reusable functions and CLI args.
- [ ] **HARDEN-TASK-001: Add edge-case tests and fix known fragility points** - 🟡 **IN PROGRESS**
  - Added edge-case coverage for empty religious input and fixed coverage divide-by-zero in growth build.

## Task Status Legend

- 🟡 **IN PROGRESS** - Currently being worked on
- ✅ **COMPLETED** - Task finished and verified
- ❌ **BLOCKED** - Task cannot proceed due to dependency or issue
- ⏸️ **ON HOLD** - Task paused for specific reason
- 📋 **NOT STARTED** - Task identified but not yet begun
