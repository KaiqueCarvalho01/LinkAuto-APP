from __future__ import annotations

import re
import secrets
import unicodedata


def slugify(text: str) -> str:
    """Normalize text into an ASCII, lowercase, hyphen-separated slug."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def generate_profile_slug(
    full_name: str | None,
    city: str | None = None,
    default_prefix: str = "usuario",
    suffix_length: int = 4,
) -> str:
    """Generate a unique human-friendly slug with random entropy suffix."""
    parts: list[str] = []
    if full_name and full_name.strip():
        parts.append(full_name.strip())
    if city and city.strip():
        parts.append(city.strip())

    base = slugify(" ".join(parts)) if parts else default_prefix
    if not base:
        base = default_prefix

    entropy = secrets.token_hex(max(2, suffix_length // 2))
    return f"{base}-{entropy}"
