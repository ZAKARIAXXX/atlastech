/**
 * Request correlation ids for logs and API responses.
 * Uses the platform UUID generator; no external dependency.
 */

export function newRequestId(): string {
  return crypto.randomUUID();
}

export function getRequestId(headers: Headers): string {
  return headers.get("x-request-id") ?? newRequestId();
}
