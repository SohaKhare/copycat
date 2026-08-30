const BACKEND_ORIGIN =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function GET(): Promise<Response> {
  let upstream: Response;
  try {
    upstream = await fetch(`${BACKEND_ORIGIN}/execution-history`, {
      cache: "no-store",
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
