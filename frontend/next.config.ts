import type { NextConfig } from "next";

/**
 * API proxying is handled by Route Handlers under src/app/api-backend/
 * (see [...path]/route.ts and upload-video/route.ts).
 *
 * Do NOT add a catch-all rewrite here — the dev-server rewrite proxy uses
 * a ~300s timeout and causes ECONNRESET on long browser skill runs.
 */
const nextConfig: NextConfig = {};

export default nextConfig;
