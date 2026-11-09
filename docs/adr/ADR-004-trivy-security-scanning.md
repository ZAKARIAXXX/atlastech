# ADR-004 — Trivy for CI Security Scanning

## Status

Accepted

## Context

AtlasTech ships a Python API, a TypeScript web dashboard, and shared schemas. The CI pipeline needs an automated filesystem security scan on every push to main and every pull request, to catch vulnerable dependencies and misconfigurations before they reach production. The scan must run fast, fail the build on critical/high findings, and use a maintained action.

## Decision

- **Trivy** via `aquasecurity/trivy-action` for filesystem scanning (`scan-type: fs`, `scan-ref: .`, severity `CRITICAL,HIGH`) in the `security` job of `.github/workflows/ci.yml`.
- Pin the action to **`v0.36.0`** (with the `v` prefix). The older `0.28.0` pin broke on 2026-11-08 because that tag no longer exists: after the March 2026 Trivy supply-chain compromise (CVE-2026-33634), tags `0.0.1`–`0.34.2` were deleted and republished with a `v` prefix.

## Consequences

- The scan runs on every push/PR and blocks on CRITICAL/HIGH findings.
- The action pin must be maintained: if the pinned tag is ever deleted again, CI fails at action resolution before anything runs (see `docs/runbooks/TROUBLESHOOTING.md`, CI section).
- Hardening option for later: SHA-pin the action instead of a tag, so a tag deletion or force-push cannot break the build.
