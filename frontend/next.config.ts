import type { NextConfig } from "next";

/* Development API target — FRONTEND_SPEC.md Phase 6 (Backend Integration).
 *
 * The FastAPI backend (default port 8000) does not currently enable CORS
 * middleware, so browser requests to http://localhost:8000 would be blocked
 * cross-origin. The frontend therefore calls the same-origin path
 * `/api-backend/...`.
 *
 * The video upload is forwarded by a streaming Route Handler
 * (src/app/api-backend/upload-video/route.ts) instead of this rewrite,
 * because the proxy buffers request bodies in memory. Small JSON calls
 * still use the rewrite below. Override the target with
 * NEXT_PUBLIC_API_URL when pointing at a deployed, CORS-enabled backend.
 */
const backendOrigin =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api-backend/:path*",
        destination: `${backendOrigin}/:path*`,
      },
    ];
  },
};

export default nextConfig;
