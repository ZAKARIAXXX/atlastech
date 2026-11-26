/**
 * Typed API error used by route handlers.
 * Carries an HTTP status so responses stay consistent.
 */

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(message: string, status = 500, code = "INTERNAL_ERROR") {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }

  static badRequest(message = "Bad request"): ApiError {
    return new ApiError(message, 400, "BAD_REQUEST");
  }

  static notFound(message = "Not found"): ApiError {
    return new ApiError(message, 404, "NOT_FOUND");
  }
}
