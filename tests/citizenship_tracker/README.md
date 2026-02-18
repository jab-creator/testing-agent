# citizenship_tracker tests

This folder contains E2E tests for the citizenship tracker project.
Tests live in the agent repo and run against a checked-out copy of the target repo.

Suites:
- `smoke`: minimal HTTP startup/page availability check.
- `regression`: deterministic checks for core pages/assets and eligibility calculation scenarios.

Eligibility fixtures:
- `fixtures/eligibility/test-data.json`
- `fixtures/eligibility/test-data-simple-mode.json`
- `fixtures/eligibility/test-data-complex-absences.json`
- extra scenarios can be added in the same folder and parametrized in `test_regression_eligibility.py`.
