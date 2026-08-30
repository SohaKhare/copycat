import { fetchBackend } from "@/lib/backend-fetch";

export const runtime = "nodejs";
/** Vercel Hobby max; proxy is fallback when NEXT_PUBLIC_API_URL is unset. */
export const maxDuration = 300;

type RouteContext = { params: Promise<{ path: string[] }> };

async function proxyRequest(
  request: Request,
  context: RouteContext,
): Promise<Response> {
  const { path } = await context.params;
  const backendPath = `/${path.join("/")}`;
  const body =
    request.method === "GET" || request.method === "HEAD"
      ? undefined
      : await request.text();

  const headers: Record<string, string> = {};
  const contentType = request.headers.get("content-type");
  if (contentType && body !== undefined) {
    headers["content-type"] = contentType;
  }

  try {
    const upstream = await fetchBackend(backendPath, {
      method: request.method,
      headers,
      body,
      signal: request.signal,
    });
    const responseBody = await upstream.text();
    return new Response(responseBody, {
      status: upstream.status,
      headers: {
        "content-type":
          upstream.headers.get("content-type") ?? "application/json",
      },
    });
  } catch {
    return Response.json(
      {
        detail:
          "CopyCat couldn't reach the backend, or the request timed out. " +
          "Long browser tasks can take several minutes.",
      },
      { status: 502 },
    );
  }
}

export async function GET(request: Request, context: RouteContext) {
  return proxyRequest(request, context);
}

export async function POST(request: Request, context: RouteContext) {
  return proxyRequest(request, context);
}

export async function PUT(request: Request, context: RouteContext) {
  return proxyRequest(request, context);
}

export async function DELETE(request: Request, context: RouteContext) {
  return proxyRequest(request, context);
}
