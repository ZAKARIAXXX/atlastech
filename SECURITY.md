# Security Policy

## Reporting a vulnerability

Do not open a public issue for a sensitive finding. Report it privately to
the repository owner through GitHub (private vulnerability reporting on this
repository, or the contact on the owner's GitHub profile) and include:

- What the issue is and where it lives (file, endpoint, or workflow).
- Steps to reproduce, or the evidence you have.
- The impact as you understand it.

You will get a reply before any public disclosure.

## Security posture of this repository

These are properties of the code as it stands today, not aspirations:

- **Localhost-only datastores.** In `docker-compose.yml`, PostgreSQL binds
  `127.0.0.1:5432` and Redis binds `127.0.0.1:6379`. Only the web (3000) and
  API (8000) ports are published more broadly, for local development.
- **Secrets stay out of git.** All secrets are supplied through a local
  `.env` file. `.gitignore` excludes `.env`, `.env.local`, and key material
  (`*.pem`, `*.key`, `*.crt`). The committed `.env.example` carries
  placeholders only.
- **Fail-fast configuration.** `docker-compose.yml` marks required secrets
  with `${VAR:?… is required}`, so the stack refuses to start with a missing
  database password, Redis password, JWT secret, or agent API key instead of
  falling back to a default.
- **Authenticated data stores and API.** Redis runs with `--requirepass`;
  the API expects a JWT secret (at least 32 characters in production, per
  `.env.example`) and a separate API key for agent telemetry ingestion.
- **CI security scanning.** GitHub Actions runs a Trivy filesystem scan that
  blocks on CRITICAL/HIGH findings — see
  [ADR-004](docs/adr/ADR-004-trivy-security-scanning.md). If the scan job is
  red, `docs/STATUS.md` says why.

## Supported versions

AtlasTech is in active development; only the `main` branch is supported.
Fixes land on `main` — there are no maintained release branches.
