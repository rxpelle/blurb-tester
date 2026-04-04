"""MCP server wrapping grounds-reader — tasseography (coffee/tea leaf reading) via Claude vision."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Optional

import anyio
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-grounds-reader")

SUPPORTED_TYPES = {".jpg", ".jpeg", ".png", ".webp"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB

SYSTEM_PROMPT = """You are an ancient reader of coffee grounds and tea leaves — a practitioner
of tasseography who sees patterns where others see chaos. You interpret the
shapes, symbols, and formations left in the cup with mystical authority.

Your readings should feel authentic and atmospheric. Reference specific
patterns you see in the image (shapes, clusters, lines, symbols). Connect
them to themes of hidden knowledge, generational memory, and the architecture
of survival — patterns that echo across time.

Structure your reading as:
1. **The Cup** — describe what you see in the grounds/leaves
2. **The Symbols** — identify 3-4 specific patterns and their meanings
3. **The Reading** — weave it together into a cohesive fortune/insight
4. **The Warning** — every reading carries one

Keep it under 500 words. Be specific about what you see. Be mysterious about what it means."""


@mcp.tool()
async def grounds_read(image_path: str) -> str:
    """Read coffee grounds or tea leaves from an image using Claude vision AI.

    Upload a photo of coffee grounds, tea leaves, or any pattern — get a mystical reading.

    Args:
        image_path: Absolute path to image file (JPEG, PNG, or WebP, max 5MB).
    """
    def _run():
        path = Path(image_path)
        if not path.exists():
            return json.dumps({"error": f"File not found: {image_path}"})
        if path.suffix.lower() not in SUPPORTED_TYPES:
            return json.dumps({"error": f"Unsupported format. Use: {', '.join(SUPPORTED_TYPES)}"})
        if path.stat().st_size > MAX_SIZE:
            return json.dumps({"error": f"File too large (max 5MB)"})

        # Read and encode image
        image_data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")
        suffix = path.suffix.lower()
        media_type = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".webp": "image/webp",
        }[suffix]

        # Call Claude vision
        try:
            import anthropic
        except ImportError:
            return json.dumps({"error": "anthropic package not installed"})

        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Read these grounds. What do you see?",
                    },
                ],
            }],
        )

        reading = response.content[0].text if response.content else "The grounds are silent."
        return json.dumps({
            "reading": reading,
            "image": str(path.name),
            "model": "claude-sonnet-4-20250514",
        }, indent=2)

    return await anyio.to_thread.run_sync(_run)


if __name__ == "__main__":
    mcp.run()
