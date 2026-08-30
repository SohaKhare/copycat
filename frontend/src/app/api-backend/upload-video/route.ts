/**
 * Streaming upload proxy — FRONTEND_SPEC.md Phase 6 (Backend Integration).
 *
 * `POST /api-backend/upload-video` forwards the request body to the FastAPI
 * backend byte-for-byte without buffering it in the Next.js server. The
 * rewrite-based proxy buffers request bodies (capped by
 * proxyClientMaxBodySize), which is wasteful for large screen recordings;
 * this handler streams instead and is not affected by body-size limits.
 *
 * The backend contract is untouched: multipart field "file", JSON responses
 * including FastAPI's { detail } errors (see src/lib/api.ts).
 */

import { fetchBackend } from "@/lib/backend-fetch";

export const runtime = "nodejs";
/** Vercel Hobby max; proxy is fallback when NEXT_PUBLIC_API_URL is unset. */
export const maxDuration = 300;

export async function POST(request: Request): Promise<Response> {
  const contentType = request.headers.get("content-type");

  const init = {
    method: "POST",
    headers: contentType ? { "content-type": contentType } : undefined,
    body: request.body,
    duplex: "half",
    signal: request.signal,
  } as unknown as RequestInit;

  let upstream: Response;
  try {
    upstream = await fetchBackend("/upload-video", init);
  } catch {
    return Response.json(
      { detail: "CopyCat couldn't reach the backend server." },
      { status: 502 },
    );
  }

  // The backend always answers with JSON (success or { detail } errors).
  const body = await upstream.text();

  return new Response(body, {
    status: upstream.status,
    headers: { "content-type": "application/json" },
  });
}