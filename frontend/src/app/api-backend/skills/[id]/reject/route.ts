const BACKEND_ORIGIN =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function POST(
  _request: Request,
  { params }: { params: Promise<{ id: string }> },
): Promise<Response> {
  const { id } = await params;

  let upstream: Response;
  try {
    upstream = await fetch(`${BACKEND_ORIGIN}/skills/${id}/reject`, {
      method: "POST",
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
