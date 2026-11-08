# Contributing to AtlasTech

Thanks for your interest in contributing to AtlasTech.

## Prerequisites

- Docker Desktop v24+
- Node.js 22+
- Python 3.11+

## Setup

```bash
git clone https://github.com/ZAKARIAXXX/atlastech.git
cd atlastech
make up
```

See README.md for the full Quick Start (manual start, service URLs, telemetry collector).

## Commit convention

All commits follow [Conventional Commits](.github/COMMIT_CONVENTION.md) (e.g. `feat(api): ...`, `fix(web): ...`, `docs: ...`).

Configure the commit template locally:

```bash
git config --local commit.template .gitmessage
```

## Development

```bash
make help       # Show all commands
make dev        # Start in development mode
make test       # Run all tests
make lint       # Lint all code
make typecheck  # Type-check all code
make build      # Build production artifacts
```

## Pull requests

- Keep changes focused and small.
- Make sure `make test` and `make lint` pass before opening a PR.
- Describe what changed and why in the PR description.
