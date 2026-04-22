"""Authenticated httpx client for Amazon/KDP backend endpoints.

Loads cookies harvested by `harvester.harvest()` into an httpx.Client.
Pure backend — no browser at runtime.
"""

import httpx

from .harvester import DEFAULT_AUTH_FILE, load_auth

DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": DEFAULT_UA,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def build_client(
    host: str = "kdpreports.amazon.com",
    auth_file=DEFAULT_AUTH_FILE,
    timeout: float = 30.0,
) -> httpx.Client:
    cookies = _cookies_for_host(load_auth(auth_file), host)
    if not cookies.get("at-main") and not cookies.get("session-token"):
        raise RuntimeError(
            f"No session cookies for {host}. Re-run `kdp-fetch harvest`."
        )
    return httpx.Client(
        base_url=f"https://{host}",
        headers={**DEFAULT_HEADERS, "Referer": f"https://{host}/"},
        cookies=cookies,
        timeout=timeout,
        follow_redirects=False,
    )


def _cookies_for_host(all_cookies: list[dict], host: str) -> dict[str, str]:
    """Select cookies whose domain applies to `host`."""
    out: dict[str, str] = {}
    for c in all_cookies:
        dom = c["domain"].lstrip(".")
        if host == dom or host.endswith("." + dom):
            out[c["name"]] = c["value"]
    return out


def probe_auth(host: str = "www.amazon.com", path: str = "/gp/yourstore/home") -> dict:
    """Confirm the session is live. Returns {status, note, signed_in_marker}."""
    client = build_client(host=host)
    try:
        r = client.get(path)
        body = r.text[:200_000] if r.status_code == 200 else ""
        signed_in = any(
            marker in body for marker in (
                'id="nav-link-accountList-nav-line-1"',
                "Hello, ",
                "yourstore",
                "Your Account",
            )
        )
        return {
            "status": r.status_code,
            "signed_in": signed_in,
            "location": r.headers.get("location"),
            "body_len": len(r.text),
        }
    finally:
        client.close()
