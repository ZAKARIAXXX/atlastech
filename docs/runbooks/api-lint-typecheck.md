# Runbook — API Lint & Type Check failure

## Symptom

The `API Lint & Type Check` job in `.github/workflows/ci.yml` fails on `main`
(exit 1). As of 2026-11-13 the root cause is not yet identified. The Security
Scan failure (Trivy tag) is separate and already diagnosed in
`docs/STATUS.md`.

## Goal

Reproduce the failure locally, identify the first real error, and record it in
`docs/STATUS.md` so the fix becomes a known, scoped change.

## Procedure

1. Read the job definition in `.github/workflows/ci.yml` (job
   `API Lint & Type Check`) and note the exact commands it runs, in order.
2. From a clean checkout, `cd services/api` and run those same commands
   locally, in the same order, stopping at the first failure.
3. Separate the two halves:
   - Run only the lint step. If it fails, the output names the file and the
     rule — fix it, or record the exact violation.
   - Run only the type-check step. Record the first error verbatim
     (file, line, message) before changing anything.
4. Check for environment drift before touching code: Python version,
   dependency lock state, and whether the failure also occurs after a clean
   install. A failure that only appears in CI is a configuration problem,
   not a code problem.
5. Record the finding in `docs/STATUS.md` under the CI section: date, the
   failing step, the first error, and the chosen fix.

## Done when

- The first failing step and its error are written in `docs/STATUS.md`, or
- the job is green on `main` and `docs/STATUS.md` says so.
