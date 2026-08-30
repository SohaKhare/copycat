/**
 * Proxy fetch to the FastAPI backend with a configurable timeout.
 *
 * Defaults to 300s to match Vercel Hobby's serverless limit. For longer local
 * runs, set BACKEND_PROXY_TIMEOUT_MS or point the frontend at the backend
 * directly via NEXT_PUBLIC_API_URL.
 */

import { Agent, fetch as undiciFetch } from "undici";

import { PROXY_TIMEOUT_MS } from "@/lib/proxy-config";

const BACKEND_ORIGIN =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const longRunningAgent = new Agent({
  headersTimeout: PROXY_TIMEOUT_MS,
  bodyTimeout: PROXY_TIMEOUT_MS,
  connectTimeout: 60_000,
});

export function backendUrl(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${BACKEND_ORIGIN}${normalized}`;
}

export async function fetchBackend(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  const url = backendUrl(path);

  return undiciFetch(url, {
    ...init,
    dispatcher: longRunningAgent,
  } as Parameters<typeof undiciFetch>[1]) as unknown as Response;
}
