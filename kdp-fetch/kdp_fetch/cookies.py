"""Extract and decrypt Chrome cookies from the playwright-persist profile.

Runs pure backend — reads Chrome's SQLite Cookies DB and decrypts values
with the AES key stored in macOS Keychain. No browser at runtime.
"""

import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

DEFAULT_PROFILE = Path.home() / ".playwright-mcp-profile" / "Default"
KEYCHAIN_SERVICE = "Chrome Safe Storage"
KDF_SALT = b"saltysalt"
KDF_ITERATIONS = 1003
AES_IV = b" " * 16


def _safe_storage_password(service: str = KEYCHAIN_SERVICE) -> bytes:
    return subprocess.check_output(
        ["security", "find-generic-password", "-s", service, "-w"]
    ).strip()


def _derive_key(password: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA1(),
        length=16,
        salt=KDF_SALT,
        iterations=KDF_ITERATIONS,
    )
    return kdf.derive(password)


def _decrypt(encrypted: bytes, key: bytes) -> str:
    if not encrypted.startswith(b"v10"):
        return encrypted.decode("utf-8")
    ct = encrypted[3:]
    decryptor = Cipher(algorithms.AES(key), modes.CBC(AES_IV)).decryptor()
    padded = decryptor.update(ct) + decryptor.finalize()
    pad_len = padded[-1]
    return padded[:-pad_len].decode("utf-8")


def load_cookies(
    domain: str = "amazon.com",
    profile: Path = DEFAULT_PROFILE,
) -> dict[str, dict]:
    """Return {name: {value, domain, path, expires}} for the given domain.

    Cookies from multiple hosts are merged by name; the most-specific host wins
    (subdomain beats parent). This matches how a browser sends them to an HTTP
    client scoped to a specific subdomain.
    """
    cookies_db = profile / "Cookies"
    if not cookies_db.exists():
        raise FileNotFoundError(f"No Cookies DB at {cookies_db}")

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        shutil.copy2(cookies_db, tmp.name)
        db_path = tmp.name

    key = _derive_key(_safe_storage_password())
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT host_key, name, encrypted_value, path, expires_utc "
            "FROM cookies WHERE host_key LIKE ?",
            (f"%{domain}%",),
        ).fetchall()
    finally:
        conn.close()

    out: dict[str, dict] = {}
    for host, name, enc, path, expires in rows:
        try:
            value = _decrypt(enc, key)
        except Exception:
            continue
        if not value:
            continue
        existing = out.get(name)
        if existing is None or len(host) > len(existing["domain"]):
            out[name] = {"value": value, "domain": host, "path": path, "expires": expires}
    return out


def as_httpx_cookies(cookies: dict[str, dict], target_host: str) -> dict[str, str]:
    """Flatten extracted cookies into {name: value} for an httpx client.

    Filters to cookies whose domain matches the target host.
    """
    out: dict[str, str] = {}
    for name, meta in cookies.items():
        dom = meta["domain"].lstrip(".")
        if target_host == dom or target_host.endswith("." + dom):
            out[name] = meta["value"]
    return out
