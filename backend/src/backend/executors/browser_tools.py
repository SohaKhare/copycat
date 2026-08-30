"""
Playwright MCP toolset wiring for the browser executor.

Two modes, picked by environment variable:

- BROWSER_CDP_ENDPOINT set: attach to an already-running, visible Chrome
  (start it with --remote-debugging-port=9222). Best for live demos - the
  automation is visible on screen instead of hidden in a background process.
- Not set (default): launch our own browser against a persistent profile
  directory, so logins survive across runs without needing a manually
  pre-launched Chrome. Better for running as an unattended service.
"""

import os
from pathlib import Path

from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters

DEFAULT_PROFILE_DIR = os.path.expanduser("~/.cache/copycat-browser-profile")

STEALTH_INIT_SCRIPT = str(Path(__file__).parent / "stealth_init.js")

# Headless Chromium's default UA string self-reports as "HeadlessChrome" on
# some versions - a realistic desktop Chrome UA removes that specific tell.
REALISTIC_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def build_browser_toolset() -> McpToolset:
    cdp_endpoint = os.environ.get("BROWSER_CDP_ENDPOINT")

    # SHOW_BROWSER=true -> visible window (demos). false/unset -> headless,
    # runs in the background. Named for the outcome you want, not the
    # underlying flag, so it can't get read backwards before a demo.
    show_browser = os.environ.get("SHOW_BROWSER", "false").lower() == "true"

    args = [
        "@playwright/mcp@latest",
        "--grant-permissions",
        "clipboard-read",
        "clipboard-write",
    ]

    if cdp_endpoint:
        args += [f"--cdp-endpoint={cdp_endpoint}"]
    else:
        profile_dir = os.environ.get("BROWSER_PROFILE_DIR", DEFAULT_PROFILE_DIR)
        args += ["--user-data-dir", profile_dir]
        if not show_browser:
            # Headless is what triggers bot detection on real sites - patch
            # the common fingerprint tells rather than accepting the block.
            # Not a guaranteed bypass (TLS/behavioral detection is out of
            # scope here), but covers the JS-detectable checks.
            args += ["--init-script", STEALTH_INIT_SCRIPT]
            args += ["--user-agent", REALISTIC_USER_AGENT]
            args.append("--headless")

    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(command="npx", args=args),
            timeout=60,
        ),
    )
