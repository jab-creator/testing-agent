# testing-agent

Standalone test agent that can test multiple repos by reading a small `.qa-agent.yml` in each target repo.

## Goals (MVP)
- Clone a repo + checkout a branch/PR ref
- Read `.qa-agent.yml`
- Select an adapter (static_web first)
- Start the app
- Run tests stored in this agent repo under `tests/<target_folder>/`
