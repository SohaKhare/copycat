/**
 * Proxy fetch to the FastAPI backend with a long timeout.
 *
 * Node's default fetch (undici) times out at 300s, which browser skill runs
 * exceed. Route handlers use this helper instead.
 */

import { Agent, fetch as undiciFetch } from "undici";

const BACKEND_ORIGIN =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** 30 minutes — browser compositions can run several skills sequentially. */
const PROXY_TIMEOUT_MS = 30 * 60 * 1000;

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
