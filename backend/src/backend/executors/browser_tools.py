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

from backend.logging_setup import log

DEFAULT_PROFILE_DIR = os.path.expanduser("~/.cache/copycat-browser-profile")
DEFAULT_MCP_VERSION = "0.0.79"
DEFAULT_MCP_CONNECT_TIMEOUT = 60

STEALTH_INIT_SCRIPT = str(Path(__file__).parent / "stealth_init.js")

# Headless Chromium's default UA string self-reports as "HeadlessChrome" on
# some versions - a realistic desktop Chrome UA removes that specific tell.
REALISTIC_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def _mcp_connect_timeout() -> float:
    raw = os.environ.get("PLAYWRIGHT_MCP_CONNECT_TIMEOUT", "").strip()
    if not raw:
        return DEFAULT_MCP_CONNECT_TIMEOUT
    try:
        return float(raw)
    except ValueError:
        log.warning(
            "invalid PLAYWRIGHT_MCP_CONNECT_TIMEOUT=%r; using %ss",
            raw,
            DEFAULT_MCP_CONNECT_TIMEOUT,
        )
        return DEFAULT_MCP_CONNECT_TIMEOUT


def build_browser_toolset() -> McpToolset:
    cdp_endpoint = os.environ.get("BROWSER_CDP_ENDPOINT")

    # SHOW_BROWSER=true -> visible window (demos). false/unset -> headless,
    # runs in the background. Named for the outcome you want, not the
    # underlying flag, so it can't get read backwards before a demo.
    show_browser = os.environ.get("SHOW_BROWSER", "false").lower() == "true"
    mcp_version = os.environ.get("PLAYWRIGHT_MCP_VERSION", DEFAULT_MCP_VERSION)
    connect_timeout = _mcp_connect_timeout()

    args = [
        "--yes",
        f"@playwright/mcp@{mcp_version}",
        "--grant-permissions",
        "clipboard-read",
        "clipboard-write",
    ]

    mode = "cdp" if cdp_endpoint else ("headed" if show_browser else "headless")
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

    log.info(
        "starting Playwright MCP: mode=%s version=%s connect_timeout=%ss cmd=npx %s",
        mode,
        mcp_version,
        connect_timeout,
        " ".join(args),
    )

    # Fewer tools = smaller Gemini schema + fewer wasted explore turns.
    # Cache the list so get_tools() is not a second MCP round-trip.
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(command="npx", args=args),
            timeout=connect_timeout,
        ),
        tool_filter=[
            "browser_navigate",
            "browser_navigate_back",
            "browser_snapshot",
            "browser_click",
            "browser_type",
            "browser_fill_form",
            "browser_press_key",
            "browser_wait_for",
            "browser_tabs",
            "browser_select_option",
            "browser_evaluate",
        ],
        tool_list_cache_ttl_seconds=3600,
    )
