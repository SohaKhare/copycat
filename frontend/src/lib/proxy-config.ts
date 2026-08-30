/**
 * Serverless proxy limits for /api-backend route handlers.
 *
 * Vercel Hobby caps maxDuration at 300 seconds. Default matches that.
 * On Pro, set BACKEND_PROXY_MAX_DURATION_SEC (e.g. 800) in Vercel env.
 */

export const PROXY_MAX_DURATION_SEC =
  Number(process.env.BACKEND_PROXY_MAX_DURATION_SEC) || 300;

export const PROXY_TIMEOUT_MS =
  Number(process.env.BACKEND_PROXY_TIMEOUT_MS) ||
  PROXY_MAX_DURATION_SEC * 1000;
