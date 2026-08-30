import os

from supabase import Client, create_client

from backend.env_config import ensure_env_loaded

ensure_env_loaded()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")


if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_SECRET_KEY must be set in the .env file."
    )


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
)