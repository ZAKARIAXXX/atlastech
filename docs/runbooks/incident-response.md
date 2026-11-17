# Runbook — Incident Response

How an AtlasTech incident is declared, worked, and closed. AtlasTech is
an IT operations platform; its own incidents are handled the way the
platform is designed to handle anyone's: severity first, facts before
theories, everything written down.

## Severity levels

| Level | Meaning | Examples | Response target |
| --- | --- | --- | --- |
| SEV-1 | Platform unusable | API down, database unreachable, data loss suspected | Drop everything, work it now |
| SEV-2 | Major function broken | Login failing, Redis down (degraded mode), CI red on `main` | Same working session |
| SEV-3 | Minor function broken | One page erroring, stale cache, a flaky job | Next planned session |
| SEV-4 | Cosmetic / docs | Broken link, wrong label, typo in a runbook | Batch with other chores |

When in doubt, grade one level higher until the facts say otherwise.

## First 10 minutes (SEV-1 / SEV-2)

1. **Confirm it is real.** Reproduce or find the failing signal
   (`docker compose ps`, API logs, the failing CI run).
2. **Write the first timeline entry** — time, symptom, what changed
   last. The timeline is kept in the incident note (below), not in chat.
3. **Check the obvious layer first:** is the stack up
   (`make up` state), is PostgreSQL healthy, is Redis answering
   (`redis-cli ping`)? Most local incidents are a stopped or unhealthy
   dependency — see the [troubleshooting runbook](TROUBLESHOOTING.md).
4. **Stop the bleeding before finding the cause.** Restart the failing
   service, roll back the last change, or restore from backup
   ([database backup & restore](database-backup-restore.md)) — diagnosis
   comes after the platform is stable.

## Working the incident

- One person drives; every action and observation is appended to the
  timeline with a timestamp.
- Change one thing at a time. A fix you cannot attribute is a fix you
  cannot trust.
- Suspect the most recent change first: last commit, last config edit,
  last dependency bump. `git log` is an incident tool.
- If data loss is possible, **snapshot before you repair** — copy the
  volume or dump the database before any destructive step.

## Closing the incident

An incident is closed when all four exist:

1. The symptom is gone and the platform is verified working end-to-end.
2. The root cause is named — or explicitly recorded as *unknown* with
   the evidence gathered.
3. The fix is committed, and `docs/STATUS.md` / `CHANGELOG.md` reflect
   it when the change is notable.
4. A follow-up action exists for anything the incident exposed
   (a missing healthcheck, an unclear runbook step, a test gap) —
   written as a task, not left as a memory.

## Recurring incident types

| Incident | Runbook |
| --- | --- |
| CI red on `main` | [CI runbook](CI.md) · [API lint & type check](api-lint-typecheck.md) |
| Database lost or corrupted | [Database backup & restore](database-backup-restore.md) |
| Redis down or cache poisoned | [Redis operations](redis-operations.md) |
| Stack will not start locally | [Local development](local-development.md) · [Troubleshooting](TROUBLESHOOTING.md) |
