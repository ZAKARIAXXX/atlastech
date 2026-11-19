# Runbook — Performance troubleshooting

How to find out why AtlasTech feels slow in the local environment,
from the browser down to the database, without guessing.

## Principle

Measure in order, from the outside in: page, API, database, cache,
containers. Change one thing at a time and re-measure; a fix you
cannot measure did not happen.

## Step 1 — Locate the slowness

- Page slow, API fast → frontend or network path. Check the browser
  devtools network tab: which request is slow, or is the page waiting
  on many small ones?
- One API endpoint slow → go to Step 2.
- Everything slow at once → go to Step 4 (containers/host) before
  touching code.

## Step 2 — The API endpoint

Time it directly, three runs, note the spread:

```bash
curl -s -o /dev/null -w "%{time_total}\n" localhost:8000/api/v1/<path>
```

- Slow on the first run only → cold start or cold cache; measure warm
  before concluding anything.
- Slow every run with a steady time → the work itself: count the
  database queries one request makes (API logs). A request whose
  query count grows with the result size is an N+1 pattern; fix the
  query, not the hardware.
- Time varies wildly between runs → contention: something else is
  using the database or the host (Step 4).

## Step 3 — The database

Use the PostgreSQL operations runbook for the full procedure; the
short version:

- Find the slow statements (slow-query log / `pg_stat_statements`).
- `EXPLAIN ANALYZE` the worst one. A sequential scan on a large table
  behind a filter on an unindexed column is the usual finding; the
  fix is an index or a rewritten filter, in that order of preference.
- Check connection pressure: many idle connections plus slow new ones
  points at pool exhaustion, not query cost.

## Step 4 — Cache and containers

- Redis: `redis-cli --latency` for round-trip health, and check the
  hit rate before blaming the database for work the cache was
  supposed to absorb (see ADR-006 for what may live in Redis).
- Containers: `docker stats` while reproducing the slowness. A
  container pinned at its memory limit or a host out of RAM makes
  every layer above it look guilty.
- Host: the local environment shares the machine with everything
  else. A backup, an update, or a second stack running at the same
  time is a legitimate root cause.

## Failure table

| Symptom | Likely cause | First check |
|---|---|---|
| First load slow, then fine | Cold start / cold cache | Warm timings before changing anything |
| One endpoint degrades as data grows | N+1 queries or missing index | Query count per request; `EXPLAIN ANALYZE` |
| All endpoints slow together | Host or container resource pressure | `docker stats`, host memory/CPU |
| Intermittent spikes | Contention (backups, other stacks, checkpoints) | Correlate spike times with Postgres and host logs |
| Fast locally in curl, slow in browser | Frontend: many requests, big payloads, render cost | Browser network tab, payload sizes |
