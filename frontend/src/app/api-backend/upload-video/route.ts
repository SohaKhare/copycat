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

const BACKEND_ORIGIN =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const runtime = "nodejs";

export async function POST(request: Request): Promise<Response> {
  const contentType = request.headers.get("content-type");

  const init = {
    method: "POST",
    // The multipart boundary lives in the content-type header — it must be
    // forwarded verbatim or the backend cannot parse the form fields.
    headers: contentType ? { "content-type": contentType } : undefined,
    body: request.body,
    // Required when forwarding a ReadableStream as a request body.
    duplex: "half",
    // If the browser upload is cancelled, abort the upstream request too.
    signal: request.signal,
  } as unknown as RequestInit;

  let upstream: Response;
  try {
    upstream = await fetch(`${BACKEND_ORIGIN}/upload-video`, init);
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