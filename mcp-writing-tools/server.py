"""MCP Writing Tools Server — wraps 6 writing packages into 13 MCP tools."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import anyio
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-writing-tools")

# ---------------------------------------------------------------------------
# Lazy imports with graceful fallback
# ---------------------------------------------------------------------------

def _import_chapter_drafter():
    from chapter_drafter.drafter import draft_chapter, revise_draft
    from chapter_drafter.voice import analyze_voice
    from chapter_drafter.models import DraftConfig
    return draft_chapter, revise_draft, analyze_voice, DraftConfig


def _import_chapter_outliner():
    from chapter_outliner.generator import generate_outline, expand_chapter
    from chapter_outliner.analyzer import analyze_pacing, parse_outline_file
    return generate_outline, expand_chapter, analyze_pacing, parse_outline_file


def _import_concept_gen():
    from concept_gen.generator import generate_concepts, expand_concept
    from concept_gen.series import get_position, get_all_positions
    return generate_concepts, expand_concept, get_position, get_all_positions


def _import_series_bible():
    from series_bible_generator.extractor import extract_from_manuscript
    from series_bible_generator.query import query_database
    from series_bible_generator.config import Config as BibleConfig
    return extract_from_manuscript, query_database, BibleConfig


def _import_manuscript_compiler():
    from manuscript_compiler.compiler import (
        compile_manuscript, discover_chapters, validate_chapters,
    )
    from manuscript_compiler.models import BookConfig
    return compile_manuscript, discover_chapters, validate_chapters, BookConfig


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _to_json(obj) -> str:
    """Serialize dataclass / dict / list to JSON string."""
    if hasattr(obj, "__dict__"):
        data = {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        # Handle nested dataclasses and lists of dataclasses
        for k, v in data.items():
            if hasattr(v, "__dict__"):
                data[k] = {kk: vv for kk, vv in v.__dict__.items() if not kk.startswith("_")}
            elif isinstance(v, list):
                data[k] = [
                    {kk: vv for kk, vv in item.__dict__.items() if not kk.startswith("_")}
                    if hasattr(item, "__dict__") else item
                    for item in v
                ]
        return json.dumps(data, indent=2, default=str)
    return json.dumps(obj, indent=2, default=str)


# ===================================================================
# 1. writing_draft_chapter
# ===================================================================

@mcp.tool()
async def writing_draft_chapter(
    outline_text: str,
    chapter_number: int = 1,
    style: str = "default",
    pov_character: str = "",
    era: str = "modern",
    word_target: int = 3500,
) -> str:
    """Draft a chapter from an outline using AI.

    Args:
        outline_text: The chapter outline / beat sheet.
        chapter_number: Chapter number (default 1).
        style: Writing style — default, king, or literary.
        pov_character: POV character name.
        era: Historical era for language register.
        word_target: Approximate word count target.
    """
    try:
        draft_chapter, _, _, DraftConfig = _import_chapter_drafter()
    except ImportError as e:
        return f"Error: chapter_drafter not installed — {e}"

    config = DraftConfig(
        outline=outline_text,
        chapter_number=chapter_number,
        style=style,
        pov_character=pov_character,
        era=era,
        word_target=word_target,
    )

    result = await anyio.to_thread.run_sync(lambda: draft_chapter(config))
    return _to_json(result)


# ===================================================================
# 2. writing_revise_chapter
# ===================================================================

@mcp.tool()
async def writing_revise_chapter(
    draft_path: str,
    focus: str = "voice",
    instructions: str = "",
) -> str:
    """Revise a draft chapter with a specific focus area.

    Args:
        draft_path: Path to the draft file to revise.
        focus: Focus area — voice, pacing, dialogue, sensory, or accessibility.
        instructions: Additional revision instructions.
    """
    try:
        _, revise_draft, _, _ = _import_chapter_drafter()
    except ImportError as e:
        return f"Error: chapter_drafter not installed — {e}"

    path = Path(draft_path)
    if not path.exists():
        return f"Error: File not found — {draft_path}"

    draft_text = await anyio.to_thread.run_sync(lambda: path.read_text(encoding="utf-8"))
    result = await anyio.to_thread.run_sync(lambda: revise_draft(draft_text, focus=focus, instructions=instructions))
    return _to_json(result)


# ===================================================================
# 3. writing_voice_check
# ===================================================================

@mcp.tool()
async def writing_voice_check(
    chapter_path: str,
    pov_character: str = "",
) -> str:
    """Analyze voice consistency of a chapter (non-AI, local analysis).

    Args:
        chapter_path: Path to the chapter file.
        pov_character: POV character name for POV-break detection.
    """
    try:
        _, _, analyze_voice, _ = _import_chapter_drafter()
    except ImportError as e:
        return f"Error: chapter_drafter not installed — {e}"

    path = Path(chapter_path)
    if not path.exists():
        return f"Error: File not found — {chapter_path}"

    text = await anyio.to_thread.run_sync(lambda: path.read_text(encoding="utf-8"))
    analysis = await anyio.to_thread.run_sync(lambda: analyze_voice(text, pov_character=pov_character))

    output = analysis.summary_dict()
    output["suggestions"] = analysis.suggestions
    return json.dumps(output, indent=2, default=str)


# ===================================================================
# 4. writing_generate_outline
# ===================================================================

@mcp.tool()
async def writing_generate_outline(
    concept: str,
    num_chapters: int = 20,
    target_words: int = 75000,
    era: str = "",
    dual_timeline: bool = False,
    series_position: int = 1,
) -> str:
    """Generate a complete book outline using AI.

    Args:
        concept: The book concept / premise.
        num_chapters: Target number of chapters.
        target_words: Target total word count.
        era: Historical era for setting.
        dual_timeline: Whether to use dual modern/historical timelines.
        series_position: Position in 12-book series (1-12).
    """
    try:
        gen_outline, _, _, _ = _import_chapter_outliner()
    except ImportError as e:
        return f"Error: chapter_outliner not installed — {e}"

    result = await anyio.to_thread.run_sync(lambda: gen_outline(
        concept=concept,
        num_chapters=num_chapters,
        target_words=target_words,
        era=era,
        dual_timeline=dual_timeline,
        series_position=series_position,
    ))
    return _to_json(result)


# ===================================================================
# 5. writing_expand_chapter
# ===================================================================

@mcp.tool()
async def writing_expand_chapter(
    outline_path: str,
    chapter_number: int = 1,
    num_scenes: int = 4,
) -> str:
    """Expand a chapter from a book outline into detailed scene breakdowns.

    Args:
        outline_path: Path to the outline file (JSON or markdown).
        chapter_number: Which chapter to expand.
        num_scenes: Target number of scenes per chapter.
    """
    try:
        _, exp_chapter, _, parse_outline_file = _import_chapter_outliner()
    except ImportError as e:
        return f"Error: chapter_outliner not installed — {e}"

    path = Path(outline_path)
    if not path.exists():
        return f"Error: File not found — {outline_path}"

    outline = await anyio.to_thread.run_sync(lambda: parse_outline_file(str(path)))
    scenes = await anyio.to_thread.run_sync(lambda: exp_chapter(outline, chapter_number, num_scenes))
    return _to_json(scenes)


# ===================================================================
# 6. writing_analyze_pacing
# ===================================================================

@mcp.tool()
async def writing_analyze_pacing(
    outline_path: str,
) -> str:
    """Analyze pacing of a book outline based on tension levels.

    Args:
        outline_path: Path to the outline file (JSON or markdown).
    """
    try:
        _, _, analyze_pac, parse_outline_file = _import_chapter_outliner()
    except ImportError as e:
        return f"Error: chapter_outliner not installed — {e}"

    path = Path(outline_path)
    if not path.exists():
        return f"Error: File not found — {outline_path}"

    outline = await anyio.to_thread.run_sync(lambda: parse_outline_file(str(path)))
    result = await anyio.to_thread.run_sync(lambda: analyze_pac(outline))
    return _to_json(result)


# ===================================================================
# 7. writing_generate_concepts
# ===================================================================

@mcp.tool()
async def writing_generate_concepts(
    genre: str = "",
    series_position: Optional[int] = None,
    seed: str = "",
    count: int = 3,
    era: str = "",
) -> str:
    """Generate novel concepts using AI.

    Args:
        genre: Genre description (defaults to series default).
        series_position: Book number in the 12-book series (1-12).
        seed: Topic or theme seed text.
        count: Number of concepts to generate.
        era: Historical era to explore.
    """
    try:
        gen_concepts, _, _, _ = _import_concept_gen()
    except ImportError as e:
        return f"Error: concept_gen not installed — {e}"

    result = await anyio.to_thread.run_sync(lambda: gen_concepts(
        genre=genre,
        series_position=series_position,
        seed=seed,
        count=count,
        era=era,
    ))
    return _to_json(result)


# ===================================================================
# 8. writing_expand_concept
# ===================================================================

@mcp.tool()
async def writing_expand_concept(
    concept_text: str,
    depth: str = "moderate",
    series_position: Optional[int] = None,
) -> str:
    """Expand a concept into a fuller treatment using AI.

    Args:
        concept_text: The concept description text.
        depth: Level of detail — brief, moderate, or detailed.
        series_position: Optional book number for series context (1-12).
    """
    try:
        _, exp_concept, _, _ = _import_concept_gen()
    except ImportError as e:
        return f"Error: concept_gen not installed — {e}"

    result = await anyio.to_thread.run_sync(lambda: exp_concept(
        concept_text=concept_text,
        depth=depth,
        series_position=series_position,
    ))
    return _to_json(result)


# ===================================================================
# 9. writing_series_map
# ===================================================================

@mcp.tool()
async def writing_series_map() -> str:
    """Show the full 12-book series progression map with eras, systems concepts, and complexity layers."""
    try:
        _, _, _, get_all_positions = _import_concept_gen()
    except ImportError as e:
        return f"Error: concept_gen not installed — {e}"

    positions = await anyio.to_thread.run_sync(get_all_positions)
    return _to_json(positions)


# ===================================================================
# 10. writing_extract_bible
# ===================================================================

@mcp.tool()
async def writing_extract_bible(
    manuscript_path: str,
) -> str:
    """Extract entities (characters, events, locations, terms, artifacts) from a manuscript.

    Args:
        manuscript_path: Path to manuscript directory or single file.
    """
    try:
        extract_fn, _, BibleConfig = _import_series_bible()
    except ImportError as e:
        return f"Error: series_bible_generator not installed — {e}"

    path = Path(manuscript_path)
    if not path.exists():
        return f"Error: Path not found — {manuscript_path}"

    config = BibleConfig.from_env()
    book_name = path.stem if path.is_file() else path.name

    result = await anyio.to_thread.run_sync(lambda: extract_fn(path, book_name, config))
    return _to_json(result)


# ===================================================================
# 11. writing_query_bible
# ===================================================================

@mcp.tool()
async def writing_query_bible(
    query: str,
    entity_type: str = "",
) -> str:
    """Query the series bible database for characters, events, terms, artifacts, or locations.

    Args:
        query: Search query text.
        entity_type: Optional filter — character, event, term, artifact, location (empty = all).
    """
    try:
        _, query_db, BibleConfig = _import_series_bible()
    except ImportError as e:
        return f"Error: series_bible_generator not installed — {e}"

    config = BibleConfig.from_env()

    # query_database searches all types; we filter afterward if entity_type given
    result = await anyio.to_thread.run_sync(lambda: query_db(query, config))
    data = json.loads(_to_json(result))

    if entity_type:
        entity_type = entity_type.lower()
        data["results"] = [r for r in data.get("results", []) if r.get("type", "").lower() == entity_type]

    return json.dumps(data, indent=2, default=str)


# ===================================================================
# 12. writing_compile_manuscript
# ===================================================================

@mcp.tool()
async def writing_compile_manuscript(
    chapters_dir: str,
    title: str = "Untitled",
    author: str = "Randy Pellegrini",
    output_format: str = "both",
) -> str:
    """Compile chapter files into a complete manuscript (DOCX-ready and/or PDF-ready markdown).

    Args:
        chapters_dir: Path to directory containing chapter markdown files.
        title: Book title.
        author: Author name.
        output_format: Output format — docx, pdf, or both.
    """
    try:
        compile_fn, _, _, BookConfig = _import_manuscript_compiler()
    except ImportError as e:
        return f"Error: manuscript_compiler not installed — {e}"

    path = Path(chapters_dir)
    if not path.exists():
        return f"Error: Directory not found — {chapters_dir}"

    config = BookConfig(title=title, author=author)
    result = await anyio.to_thread.run_sync(lambda: compile_fn(
        chapters_dir=str(path),
        config=config,
        output_format=output_format,
    ))
    return _to_json(result)


# ===================================================================
# 13. writing_wordcount
# ===================================================================

@mcp.tool()
async def writing_wordcount(
    chapters_dir: str,
) -> str:
    """Get word counts for all chapter files in a directory.

    Args:
        chapters_dir: Path to directory containing chapter markdown files.
    """
    try:
        _, discover_fn, validate_fn, BookConfig = _import_manuscript_compiler()
    except ImportError as e:
        return f"Error: manuscript_compiler not installed — {e}"

    path = Path(chapters_dir)
    if not path.exists():
        return f"Error: Directory not found — {chapters_dir}"

    config = BookConfig()
    chapters = await anyio.to_thread.run_sync(lambda: discover_fn(str(path), config))

    counts = []
    total = 0
    for ch in chapters:
        counts.append({
            "chapter": ch.number,
            "title": ch.title,
            "words": ch.word_count,
            "file": ch.filename,
        })
        total += ch.word_count

    issues = await anyio.to_thread.run_sync(lambda: validate_fn(chapters))

    return json.dumps({
        "chapters": counts,
        "total_words": total,
        "chapter_count": len(counts),
        "issues": issues,
    }, indent=2, default=str)


# ---------------------------------------------------------------------------
# Continuity Checker tools
# ---------------------------------------------------------------------------

def _import_continuity_checker():
    from continuity_checker.scanner import full_scan, cross_reference
    from continuity_checker.character_check import check_characters
    from continuity_checker.timeline_check import check_timeline
    from continuity_checker.baseline import generate_baseline
    return full_scan, cross_reference, check_characters, check_timeline, generate_baseline

@mcp.tool()
async def writing_continuity_scan(
    manuscript_path: str,
    bible_path: Optional[str] = None,
    baseline_path: Optional[str] = None,
    severity: str = "warning",
    use_ai: bool = False,
) -> str:
    """Run a full continuity scan on a manuscript — checks characters, timeline, terminology, and baseline diffs.

    Args:
        manuscript_path: Path to manuscript directory or file.
        bible_path: Path to series bible file/directory (optional).
        baseline_path: Path to baseline file for diff comparison (optional).
        severity: Minimum severity to report: error, warning, or info.
        use_ai: Enable AI-powered semantic checks via Claude (costs API tokens).
    """
    full_scan, *_ = _import_continuity_checker()

    def _run():
        result = full_scan(
            manuscript_path=manuscript_path,
            bible_path=bible_path,
            baseline_path=baseline_path,
            severity=severity,
            use_ai=use_ai,
        )
        if hasattr(result, '__dict__'):
            return json.dumps(result.__dict__, indent=2, default=str)
        return str(result)

    return await anyio.to_thread.run_sync(_run)


@mcp.tool()
async def writing_continuity_cross_ref(
    current_path: str,
    previous_path: str,
    bible_path: Optional[str] = None,
    severity: str = "warning",
    use_ai: bool = False,
) -> str:
    """Cross-reference two manuscripts (e.g. Book 3 vs Book 4) for continuity issues across books.

    Args:
        current_path: Path to current manuscript directory.
        previous_path: Path to previous book's manuscript directory.
        bible_path: Path to series bible (optional).
        severity: Minimum severity: error, warning, or info.
        use_ai: Enable AI-powered semantic checks.
    """
    _, cross_reference, *_ = _import_continuity_checker()

    def _run():
        result = cross_reference(
            current_path=current_path,
            previous_path=previous_path,
            bible_path=bible_path,
            severity=severity,
            use_ai=use_ai,
        )
        if hasattr(result, '__dict__'):
            return json.dumps(result.__dict__, indent=2, default=str)
        return str(result)

    return await anyio.to_thread.run_sync(_run)


@mcp.tool()
async def writing_generate_baseline(
    manuscript_path: str,
    output_path: str,
) -> str:
    """Generate a manuscript baseline for future diff comparisons. Records chapter structure, word counts, and checksums.

    Args:
        manuscript_path: Path to manuscript directory.
        output_path: Path to write the baseline file.
    """
    *_, generate_baseline = _import_continuity_checker()

    def _run():
        result = generate_baseline(manuscript_path=manuscript_path, output_path=output_path)
        if hasattr(result, '__dict__'):
            return json.dumps(result.__dict__, indent=2, default=str)
        return json.dumps({"status": "ok", "output": output_path}, default=str)

    return await anyio.to_thread.run_sync(_run)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
