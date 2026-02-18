# citizenship_tracker tests

This folder contains E2E tests for the citizenship tracker project.
Tests live in the agent repo and run against a checked-out copy of the target repo.

Suites:
- `smoke`: minimal HTTP startup/page availability check.
- `regression`: deterministic HTTP checks for core pages, assets, and settings form rendering.
