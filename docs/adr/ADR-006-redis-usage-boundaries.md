# ADR-006 — Redis Usage Boundaries

## Status

Accepted

## Context

ADR-003 put PostgreSQL and Redis side by side as the data layer, but did
not state which store owns which kind of data. In an operations
platform that distinction decides what an outage means: if Redis holds
anything irreplaceable, a cache flush becomes data loss, and the
[Redis operations runbook](../runbooks/redis-operations.md) can no
longer treat `FLUSHDB` as a safe recovery step. The boundary needs to
be explicit before more features are built on top of it.

## Decision

- **PostgreSQL is the only source of truth.** Accounts, assets,
  incidents, configuration, and anything a user would expect to still
  exist tomorrow live in PostgreSQL, with migrations as the record of
  their shape.
- **Redis holds only data that can be rebuilt or allowed to expire:**
  response and query caches, rate-limit counters, short-lived session
  and token state, and transient job/queue payloads whose loss is
  recoverable by re-running the job.
- **Every Redis key carries a TTL** unless it is deliberately
  persistent (e.g. a rate-limit window keyed to its own expiry
  semantics). A key with no expiry is a bug until proven otherwise.
- **No business rule may depend on a Redis value being present.** The
  API must degrade to a PostgreSQL read — slower, but correct — when a
  cache entry is missing or Redis is unavailable.
- **Redis is never the transport for secrets.** Credentials and tokens
  at rest belong in the environment (see ADR-005) or PostgreSQL, not in
  cache entries or queue payloads.

## Consequences

- Cache flushes and full Redis restarts are safe, documented recovery
  steps instead of incidents.
- A Redis outage is a SEV-2 degradation (slower platform), never a
  SEV-1 data event — see the
  [incident response runbook](../runbooks/incident-response.md).
- Feature work that wants Redis for something new must name which
  category the data falls into; "it was convenient" is not a category.
- The trade-off is accepted: some reads pay a PostgreSQL round-trip on
  cache miss, and queue payloads must be designed to be re-runnable.
