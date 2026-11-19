# ADR-008 — API versioning and error format

- Status: Accepted
- Date: 2026-11-19
- Related: ADR-001 (FastAPI backend), ADR-003 (Postgres & Redis data
  layer)

## Context

The web frontend and any future client consume the API over HTTP.
Without a versioning rule, the first breaking change forces a choice
between breaking live clients and freezing the API. Without a uniform
error format, every endpoint invents its own failure shape and the
frontend grows a special case per route.

## Decision

### Versioning

- The API is versioned by URL path prefix with a major version only:
  `/api/v1/...`. No minor or patch versions in the path.
- Within a major version, only backwards-compatible changes are
  allowed: adding endpoints, adding optional request fields, adding
  response fields. Clients must ignore response fields they do not
  know.
- A breaking change (removing or renaming a field, changing a type,
  changing a status code's meaning) ships as a new major version.
  The previous major version keeps running until no supported client
  uses it.

### Error format

Every error response, from every endpoint, uses one envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Human-readable summary, safe to show a user.",
    "details": null
  }
}
```

- `code` is a stable machine-readable string (snake_case). Clients
  branch on `code`, never on `message`.
- `message` is human-readable and contains no internals: no SQL, no
  stack traces, no file paths, no dependency names.
- `details` is optional structured context (for example, per-field
  validation errors) or `null`.
- HTTP status codes keep their standard meaning: 400 malformed, 401
  unauthenticated, 403 authenticated but not allowed, 404 not found,
  409 conflict, 422 validation failed, 500 server fault.
- Framework defaults that bypass the envelope (unhandled 500s,
  default validation responses) are wrapped by exception handlers so
  the contract holds for failures the endpoint did not anticipate.

## Consequences

- The frontend has exactly one error-handling path.
- API changes are reviewed against the compatibility rule before
  merge; "is this breaking?" becomes a yes/no question with a defined
  answer.
- A future `/api/v2` can be introduced without touching v1 clients.
- Cost: maintaining two majors during a migration window, and the
  discipline of wrapping framework error defaults once, centrally.
