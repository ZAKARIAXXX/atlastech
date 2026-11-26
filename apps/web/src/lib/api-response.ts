import { NextResponse } from "next/server";
import { ApiError } from "./errors";

/** Standard success envelope for API routes. */
export function ok<T>(data: T, status = 200): NextResponse {
  return NextResponse.json({ ok: true, data }, { status });
}

/** Standard error envelope; hides internals for unknown errors. */
export function fail(error: unknown): NextResponse {
  if (error instanceof ApiError) {
    return NextResponse.json(
      { ok: false, error: { code: error.code, message: error.message } },
      { status: error.status },
    );
  }
  return NextResponse.json(
    { ok: false, error: { code: "INTERNAL_ERROR", message: "Internal server error" } },
    { status: 500 },
  );
}
