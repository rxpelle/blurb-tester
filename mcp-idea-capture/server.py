"""MCP server wrapping the idea-capture tool — CRUD operations on ideas JSON store."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import anyio
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-idea-capture")

IDEAS_FILE = os.path.join(
    os.path.dirname(__file__), "..", "idea-capture", "data", "ideas.json"
)


def _read_ideas() -> list[dict]:
    path = Path(IDEAS_FILE)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("[]")
        return []
    return json.loads(path.read_text())


def _write_ideas(ideas: list[dict]) -> None:
    Path(IDEAS_FILE).write_text(json.dumps(ideas, indent=2))


@mcp.tool()
async def idea_list(status: Optional[str] = None) -> str:
    """List all captured ideas, optionally filtered by status.

    Args:
        status: Filter by status — new, reviewed, or acted_on. Omit for all.
    """
    def _run():
        ideas = _read_ideas()
        if status:
            ideas = [i for i in ideas if i.get("status") == status]
        return json.dumps(ideas, indent=2)

    return await anyio.to_thread.run_sync(_run)


@mcp.tool()
async def idea_add(text: str, source: str = "mcp", tags: Optional[str] = None) -> str:
    """Capture a new idea.

    Args:
        text: The idea text.
        source: Where the idea came from (default: mcp). E.g., voice, text, conversation.
        tags: Comma-separated tags (optional).
    """
    def _run():
        ideas = _read_ideas()
        idea = {
            "id": uuid.uuid4().hex[:8],
            "text": text,
            "source": source,
            "status": "new",
            "tags": [t.strip() for t in tags.split(",")] if tags else [],
            "notes": "",
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
        }
        ideas.append(idea)
        _write_ideas(ideas)
        return json.dumps(idea, indent=2)

    return await anyio.to_thread.run_sync(_run)


@mcp.tool()
async def idea_update(
    idea_id: str,
    status: Optional[str] = None,
    tags: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """Update an existing idea's status, tags, or notes.

    Args:
        idea_id: The idea ID to update.
        status: New status — new, reviewed, or acted_on.
        tags: Comma-separated tags (replaces existing).
        notes: Additional notes to append.
    """
    def _run():
        ideas = _read_ideas()
        for idea in ideas:
            if idea["id"] == idea_id:
                if status:
                    idea["status"] = status
                if tags is not None:
                    idea["tags"] = [t.strip() for t in tags.split(",")]
                if notes:
                    idea["notes"] = notes
                idea["updatedAt"] = datetime.now().isoformat()
                _write_ideas(ideas)
                return json.dumps(idea, indent=2)
        return json.dumps({"error": f"Idea {idea_id} not found"})

    return await anyio.to_thread.run_sync(_run)


@mcp.tool()
async def idea_delete(idea_id: str) -> str:
    """Delete an idea by ID.

    Args:
        idea_id: The idea ID to delete.
    """
    def _run():
        ideas = _read_ideas()
        before = len(ideas)
        ideas = [i for i in ideas if i["id"] != idea_id]
        if len(ideas) == before:
            return json.dumps({"error": f"Idea {idea_id} not found"})
        _write_ideas(ideas)
        return json.dumps({"deleted": True, "id": idea_id})

    return await anyio.to_thread.run_sync(_run)


if __name__ == "__main__":
    mcp.run()
