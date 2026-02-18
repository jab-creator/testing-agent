# .qa-agent.yml schema (draft)

This file lives in the TARGET repo (the app repo). It tells the agent how to run & test the project.

Core keys:
- project.name
- project.type (static_web, flutter, api_python, ...)
- run.command
- run.wait_for
- run.timeout
- test.target_folder (where tests live in THIS repo under /tests)
- test.strategy (selenium, flutter, api)
- test.base_url_env
- test.endpoints (optional list of URL paths to smoke test)
- test.default_suite (optional: smoke, regression/core, all)
- env (env vars to set for the runner)
