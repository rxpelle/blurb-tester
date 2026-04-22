"""Harvest Amazon session cookies from the playwright-persist Chrome profile.

Launches headless Chrome against a *copy* of the profile (to avoid lock
conflicts with the live MCP), waits for cookies to be sent, and writes
them to a JSON blob the httpx client can consume.

Runs infrequently (sessions last weeks). Everything after harvest is pure httpx.
"""

import json
import shutil
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

DEFAULT_PROFILE = Path.home() / ".playwright-mcp-profile"
DEFAULT_AUTH_FILE = Path.home() / ".kdp-fetch" / "auth.json"


def harvest(
    profile: Path = DEFAULT_PROFILE,
    auth_file: Path = DEFAULT_AUTH_FILE,
    warmup_url: str = "https://www.amazon.com/gp/yourstore/home",
) -> dict:
    """Copy the Chrome profile, launch headless, dump cookies to JSON.

    Returns a summary dict with cookie count and path.
    """
    auth_file.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="kdp-fetch-harvest-") as tmp_root:
        tmp_profile = Path(tmp_root) / "profile"
        _copy_profile_minimal(profile, tmp_profile)

        with sync_playwright() as p:
            ctx = p.chromium.launch_persistent_context(
                user_data_dir=str(tmp_profile),
                channel="chrome",
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )
            try:
                page = ctx.new_page()
                page.goto(warmup_url, wait_until="domcontentloaded", timeout=30_000)
                time.sleep(2)  # let any post-load XHRs fire
                cookies = ctx.cookies()
            finally:
                ctx.close()

    amazon_cookies = [c for c in cookies if "amazon" in c.get("domain", "")]
    payload = {
        "harvested_at": time.time(),
        "warmup_url": warmup_url,
        "cookies": amazon_cookies,
    }
    auth_file.write_text(json.dumps(payload, indent=2))
    auth_file.chmod(0o600)

    return {
        "cookie_count": len(amazon_cookies),
        "auth_file": str(auth_file),
        "critical": [c["name"] for c in amazon_cookies if c["name"] in {
            "at-main", "session-id", "session-token", "ubid-main", "x-main"
        }],
    }


def _copy_profile_minimal(src: Path, dst: Path) -> None:
    """Copy only the files Chrome needs to boot an authenticated session.

    Full profiles are multi-GB and include caches. We copy just the state
    required for auth.
    """
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "Default").mkdir(exist_ok=True)

    default_src = src / "Default"
    whitelist = [
        "Cookies", "Cookies-journal",
        "Login Data", "Login Data-journal",
        "Preferences", "Secure Preferences",
        "Local State",  # actually in profile root, handled separately
        "Web Data", "Web Data-journal",
    ]
    for name in whitelist:
        s = default_src / name
        if s.exists():
            shutil.copy2(s, dst / "Default" / name)

    local_state = src / "Local State"
    if local_state.exists():
        shutil.copy2(local_state, dst / "Local State")


def load_auth(auth_file: Path = DEFAULT_AUTH_FILE) -> list[dict]:
    if not auth_file.exists():
        raise FileNotFoundError(
            f"No auth file at {auth_file}. Run `kdp-fetch harvest` first."
        )
    return json.loads(auth_file.read_text())["cookies"]
