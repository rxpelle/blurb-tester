"""Query the series bible across all documents and database."""

import json
from pathlib import Path
from typing import Optional

from anthropic import Anthropic

from .config import Config
from .db import (
    get_connection, CharacterRepository, EventRepository,
    TermRepository, ArtifactRepository, LocationRepository,
)
from .models import QueryResult


QUERY_PROMPT = """You are a series bible query engine. Answer the question below using ONLY the provided series bible data. Be precise and cite which document/section your answer comes from.

If the data doesn't contain enough information, say so clearly.

QUESTION: {query}

SERIES BIBLE DATA:
{context}
"""


def query_database(query: str, config: Config) -> QueryResult:
    """Search across all database tables for matching entities."""
    conn = get_connection(config)

    characters = CharacterRepository(conn).search(query)
    events = EventRepository(conn).search(query)
    terms = TermRepository(conn).search(query)
    artifacts = ArtifactRepository(conn).search(query)
    locations = LocationRepository(conn).search(query)

    conn.close()

    all_results = []
    sources = set()

    for c in characters:
        all_results.append({
            "type": "character",
            "name": c["name"],
            "description": c["description"],
            "network": c["network"],
            "generation": c["generation_absolute"],
            "era": c["era"],
        })
        if c["source_file"]:
            sources.add(c["source_file"])

    for e in events:
        all_results.append({
            "type": "event",
            "date": e["date"],
            "description": e["description"],
            "location": e["location"],
        })
        if e["source_file"]:
            sources.add(e["source_file"])

    for t in terms:
        all_results.append({
            "type": "term",
            "term": t["term"],
            "definition": t["definition"],
            "usage": t["correct_usage"],
        })
        if t["source_file"]:
            sources.add(t["source_file"])

    for a in artifacts:
        all_results.append({
            "type": "artifact",
            "name": a["name"],
            "description": a["description"],
        })
        if a["source_file"]:
            sources.add(a["source_file"])

    for loc in locations:
        all_results.append({
            "type": "location",
            "name": loc["name"],
            "description": loc["description"],
        })
        if loc["source_file"]:
            sources.add(loc["source_file"])

    result_type = "general"
    if characters and not events and not terms:
        result_type = "character"
    elif events and not characters:
        result_type = "event"
    elif terms and not characters:
        result_type = "term"

    return QueryResult(
        query=query,
        result_type=result_type,
        results=all_results,
        sources=list(sources),
    )


def query_bible_files(
    query: str,
    bible_dir: Path,
    config: Config,
) -> QueryResult:
    """Search bible markdown files directly using AI."""
    from .parser import find_bible_files

    files = find_bible_files(bible_dir, config.bible_prefix)
    context_parts = []

    for doc_type, file_path in files.items():
        content = file_path.read_text(encoding="utf-8")
        # Only include relevant sections (search for query terms)
        query_terms = query.lower().split()
        relevant_sections = []
        for section in content.split("\n###"):
            if any(term in section.lower() for term in query_terms):
                relevant_sections.append("###" + section if not section.startswith("#") else section)

        if relevant_sections:
            context_parts.append(f"--- {doc_type.upper()} ({file_path.name}) ---")
            context_parts.append("\n".join(relevant_sections[:5]))  # Limit sections

    if not context_parts:
        return QueryResult(
            query=query,
            result_type="general",
            results=[],
            context="No matching content found in bible files.",
        )

    context = "\n\n".join(context_parts)

    if not config.has_api_key:
        return QueryResult(
            query=query,
            result_type="general",
            results=[{"type": "raw", "content": context[:5000]}],
            context=context[:5000],
            sources=[str(f) for f in files.values()],
        )

    client = Anthropic(api_key=config.anthropic_api_key)
    response = client.messages.create(
        model=config.model,
        max_tokens=config.max_tokens,
        messages=[{
            "role": "user",
            "content": QUERY_PROMPT.format(query=query, context=context[:30000]),
        }],
    )

    answer = response.content[0].text

    return QueryResult(
        query=query,
        result_type="general",
        results=[{"type": "answer", "content": answer}],
        context=answer,
        sources=[str(f) for f in files.values()],
    )


def get_stats(config: Config) -> dict:
    """Get database statistics."""
    conn = get_connection(config)
    stats = {
        "characters": CharacterRepository(conn).count(),
        "events": EventRepository(conn).count(),
        "terms": TermRepository(conn).count(),
        "artifacts": ArtifactRepository(conn).count(),
        "locations": LocationRepository(conn).count(),
    }
    stats["total"] = sum(stats.values())

    from .db import BibleFileRepository
    ingested = BibleFileRepository(conn).get_ingested()
    stats["bible_files_ingested"] = len(ingested)
    stats["ingested_files"] = ingested

    conn.close()
    return stats
