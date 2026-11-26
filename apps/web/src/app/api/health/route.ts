import { ok } from "@/lib/api-response";
import { getRequestId } from "@/lib/request-id";
import { logger } from "@/lib/logger";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** GET /api/health — liveness probe for uptime checks. */
export async function GET(request: Request) {
  const requestId = getRequestId(request.headers);
  logger.info("health check", { requestId });
  return ok({
    status: "ok",
    service: "atlastech-web",
    time: new Date().toISOString(),
    requestId,
  });
}
