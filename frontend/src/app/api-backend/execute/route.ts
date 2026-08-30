const BACKEND_ORIGIN =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function POST(request: Request): Promise<Response> {
  const bodyText = await request.text();

  let upstream: Response;
  try {
    upstream = await fetch(`${BACKEND_ORIGIN}/execute`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: bodyText,
    });
  } catch {
    return Response.json(
      { detail: "CopyCat couldn't reach the backend server." },
      { status: 502 },
    );
  }

  const body = await upstream.text();
  return new Response(body, {
    status: upstream.status,
    headers: { "content-type": "application/json" },
  });
}
