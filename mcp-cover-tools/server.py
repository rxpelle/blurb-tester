"""MCP server wrapping the cover-generator and cover-comp-analyzer CLI tools."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime

import anyio
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy imports — wrapped in try/except so the server can start even if a
# dependency is temporarily missing.  Errors are surfaced at call time.
# ---------------------------------------------------------------------------

_import_errors: list[str] = []

try:
    from cover_generator.designer import get_design_params
    from cover_generator.renderer import render_cover, render_front_only, create_thumbnail
    from cover_generator.config import Config as CoverConfig
    from cover_generator.genres import list_genres as cg_list_genres, GENRE_PROFILES as CG_GENRES
    from cover_generator.fonts import list_available_fonts
    from cover_generator.backgrounds import generate_dalle_background, create_gradient_background
except ImportError as exc:
    _import_errors.append(f"cover_generator: {exc}")
    logger.error("Failed to import cover_generator: %s", exc)

try:
    from cover_comp_analyzer.analyzer import (
        analyze_cover,
        analyze_thumbnail,
        analyze_comps_batch,
    )
    from cover_comp_analyzer.comparator import CoverComparator
    from cover_comp_analyzer.scorer import score_cover
    from cover_comp_analyzer.images import load_image, load_comp_folder
    from cover_comp_analyzer.genres import list_genres as ca_list_genres
except ImportError as exc:
    _import_errors.append(f"cover_comp_analyzer: {exc}")
    logger.error("Failed to import cover_comp_analyzer: %s", exc)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_OUTPUT_DIR = "/Users/randypellegrini/Documents/antigravity/cover-generator/output"

mcp = FastMCP("mcp-cover-tools")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_generator_imports() -> str | None:
    """Return an error message if cover_generator is not available."""
    for err in _import_errors:
        if "cover_generator" in err:
            return f"cover_generator is not available: {err}"
    return None


def _check_analyzer_imports() -> str | None:
    """Return an error message if cover_comp_analyzer is not available."""
    for err in _import_errors:
        if "cover_comp_analyzer" in err:
            return f"cover_comp_analyzer is not available: {err}"
    return None


def _slug(title: str) -> str:
    return title.lower().replace(" ", "-").replace("'", "")[:40]


def _save_cover_outputs(cover_img, output_dir: str, slug: str, suffix: str = "") -> list[str]:
    """Save a cover image as PNG, PDF, and thumbnail.  Returns list of paths."""
    os.makedirs(output_dir, exist_ok=True)
    paths: list[str] = []

    cover_path = os.path.join(output_dir, f"{slug}-cover{suffix}.png")
    cover_img.save(cover_path, "PNG", dpi=(300, 300))
    paths.append(cover_path)

    pdf_path = os.path.join(output_dir, f"{slug}-cover{suffix}.pdf")
    cover_img.convert("RGB").save(pdf_path, "PDF", resolution=300)
    paths.append(pdf_path)

    thumb = create_thumbnail(cover_img, size=400)
    thumb_path = os.path.join(output_dir, f"{slug}-thumbnail{suffix}.png")
    thumb.save(thumb_path, "PNG")
    paths.append(thumb_path)

    return paths


def _save_ebook_outputs(cover_img, output_dir: str, slug: str, suffix: str = "") -> list[str]:
    """Save an ebook cover image as PNG + thumbnails.  Returns list of paths."""
    os.makedirs(output_dir, exist_ok=True)
    paths: list[str] = []

    cover_path = os.path.join(output_dir, f"{slug}-ebook{suffix}.png")
    cover_img.save(cover_path, "PNG", dpi=(300, 300))
    paths.append(cover_path)

    thumb = create_thumbnail(cover_img, size=300)
    thumb_path = os.path.join(output_dir, f"{slug}-ebook-thumb{suffix}.png")
    thumb.save(thumb_path, "PNG")
    paths.append(thumb_path)

    amazon_thumb = create_thumbnail(cover_img, size=150)
    amazon_path = os.path.join(output_dir, f"{slug}-amazon-thumb{suffix}.png")
    amazon_thumb.save(amazon_path, "PNG")
    paths.append(amazon_path)

    return paths


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def cover_generate(
    title: str,
    subtitle: str = "",
    author: str = "Randy Pellegrini",
    genre: str = "thriller",
    blurb: str = "",
    pages: int = 300,
    trim_size: str = "5.5x8.5",
    use_dalle: bool = False,
    description: str = "",
    series: str = "",
    paper: str = "cream",
    output_dir: str = "",
) -> str:
    """Generate a full paperback cover (front + spine + back) for KDP.

    Produces PNG, PDF, and thumbnail files in the output directory.
    Uses Claude AI to choose genre-appropriate design parameters and
    optionally DALL-E 3 for background art.

    Args:
        title: Book title.
        subtitle: Book subtitle.
        author: Author name.
        genre: Genre key (thriller, historical, scifi, mystery, literary, romance, fantasy, horror).
        blurb: Back cover blurb text.
        pages: Page count (determines spine width).
        trim_size: KDP trim size (5x8, 5.25x8, 5.5x8.5, 6x9).
        use_dalle: Whether to generate a DALL-E 3 background image.
        description: Book description to help AI choose design direction.
        series: Series name (e.g., "Book Three of The Architecture of Survival").
        paper: Paper type (cream, white, color).
        output_dir: Output directory (defaults to cover-generator/output/).
    """
    err = _check_generator_imports()
    if err:
        return f"Error: {err}"

    out = output_dir or DEFAULT_OUTPUT_DIR
    book = {
        "title": title,
        "subtitle": subtitle,
        "author": author,
        "series": series,
        "blurb": blurb,
    }

    try:
        dims = CoverConfig.calculate_cover_dimensions(
            trim=trim_size, page_count=pages, paper=paper,
        )

        # Get design params (calls Claude API — blocking)
        design = await anyio.to_thread.run_sync(
            lambda: get_design_params(
                title=title, subtitle=subtitle, author=author,
                series=series, genre=genre, description=description,
            )
        )

        # Render cover (CPU-heavy — blocking)
        cover_img = await anyio.to_thread.run_sync(
            lambda: render_cover(
                book=book,
                design_params=design,
                dims=dims,
                genre_name=genre,
                use_dalle=use_dalle,
            )
        )

        # Save outputs
        slug = _slug(title)
        paths = await anyio.to_thread.run_sync(
            lambda: _save_cover_outputs(cover_img, out, slug)
        )

        # Save design params JSON
        params_path = os.path.join(out, f"{slug}-design.json")
        with open(params_path, "w") as f:
            json.dump(design, f, indent=2)
        paths.append(params_path)

        result = {
            "status": "success",
            "title": title,
            "genre": genre,
            "dimensions": f"{dims['width_px']}x{dims['height_px']}px",
            "spine_width": f"{dims['spine_w_in']:.3f}\"",
            "design_rationale": design.get("design_rationale", ""),
            "files": paths,
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error("cover_generate failed: %s", e, exc_info=True)
        return f"Error generating cover: {type(e).__name__}: {e}"


@mcp.tool()
async def cover_ebook(
    title: str,
    subtitle: str = "",
    author: str = "Randy Pellegrini",
    genre: str = "thriller",
    series: str = "",
    use_dalle: bool = False,
    variants: int = 1,
    description: str = "",
    output_dir: str = "",
) -> str:
    """Generate an ebook cover (1600x2560, front only).

    Produces PNG and thumbnail files. Generate multiple variants for A/B
    comparison by setting variants > 1.

    Args:
        title: Book title.
        subtitle: Book subtitle.
        author: Author name.
        genre: Genre key (thriller, historical, scifi, mystery, literary, romance, fantasy, horror).
        series: Series name.
        use_dalle: Whether to generate a DALL-E 3 background image.
        variants: Number of design variants to generate (1-5).
        description: Book description to help AI choose design direction.
        output_dir: Output directory (defaults to cover-generator/output/).
    """
    err = _check_generator_imports()
    if err:
        return f"Error: {err}"

    out = output_dir or DEFAULT_OUTPUT_DIR
    variants = max(1, min(variants, 5))
    book = {
        "title": title,
        "subtitle": subtitle,
        "author": author,
        "series": series,
    }

    try:
        all_paths: list[str] = []

        for i in range(variants):
            suffix = f"-v{i + 1}" if variants > 1 else ""

            design = await anyio.to_thread.run_sync(
                lambda: get_design_params(
                    title=title, subtitle=subtitle, author=author,
                    series=series, genre=genre, description=description,
                )
            )

            cover_img = await anyio.to_thread.run_sync(
                lambda: render_front_only(
                    book=book,
                    design_params=design,
                    genre_name=genre,
                    use_dalle=use_dalle,
                )
            )

            slug = _slug(title)
            paths = await anyio.to_thread.run_sync(
                lambda: _save_ebook_outputs(cover_img, out, slug, suffix)
            )

            params_path = os.path.join(out, f"{slug}-ebook-design{suffix}.json")
            with open(params_path, "w") as f:
                json.dump(design, f, indent=2)
            paths.append(params_path)

            all_paths.extend(paths)

        result = {
            "status": "success",
            "title": title,
            "genre": genre,
            "variants": variants,
            "dimensions": "1600x2560px",
            "files": all_paths,
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error("cover_ebook failed: %s", e, exc_info=True)
        return f"Error generating ebook cover: {type(e).__name__}: {e}"


@mcp.tool()
async def cover_design(
    title: str,
    subtitle: str = "",
    author: str = "Randy Pellegrini",
    genre: str = "thriller",
    series: str = "",
    description: str = "",
) -> str:
    """Preview AI-generated design parameters without rendering any images.

    Returns the design JSON that Claude would use for font choices, color
    palette, layout variant, decorative elements, and DALL-E prompt.
    Useful for reviewing design direction before committing to a render.

    Args:
        title: Book title.
        subtitle: Book subtitle.
        author: Author name.
        genre: Genre key (thriller, historical, scifi, mystery, literary, romance, fantasy, horror).
        series: Series name.
        description: Book description to help AI choose design direction.
    """
    err = _check_generator_imports()
    if err:
        return f"Error: {err}"

    try:
        params = await anyio.to_thread.run_sync(
            lambda: get_design_params(
                title=title, subtitle=subtitle, author=author,
                series=series, genre=genre, description=description,
            )
        )
        return json.dumps(params, indent=2)

    except Exception as e:
        logger.error("cover_design failed: %s", e, exc_info=True)
        return f"Error generating design params: {type(e).__name__}: {e}"


@mcp.tool()
async def cover_genres() -> str:
    """List all available genre profiles for both cover generation and analysis.

    Returns genre keys, display names, and basic style info for the
    cover-generator and cover-comp-analyzer genre systems.
    """
    result: dict = {"generator_genres": [], "analyzer_genres": []}

    # Cover generator genres
    gen_err = _check_generator_imports()
    if gen_err:
        result["generator_error"] = gen_err
    else:
        for key, name in cg_list_genres():
            profile = CG_GENRES.get(key, {})
            result["generator_genres"].append({
                "key": key,
                "name": name,
                "title_weight": profile.get("title_weight", ""),
                "title_case": profile.get("title_case", ""),
                "palettes": len(profile.get("palettes", [])),
                "mood": profile.get("mood_keywords", []),
            })

    # Cover comp analyzer genres
    ana_err = _check_analyzer_imports()
    if ana_err:
        result["analyzer_error"] = ana_err
    else:
        for key, name in ca_list_genres():
            result["analyzer_genres"].append({"key": key, "name": name})

    return json.dumps(result, indent=2)


@mcp.tool()
async def cover_analyze(
    cover_path: str,
    comp_paths: str = "",
    genre: str = "thriller",
) -> str:
    """Analyze a cover image against optional competitor covers.

    Uses Claude Vision to evaluate typography, color palette, layout,
    genre signaling, thumbnail readability, and professional quality.
    If comp_paths are provided, also scores competitive differentiation.

    Args:
        cover_path: Absolute path to the cover image to analyze.
        comp_paths: Comma-separated paths to competitor cover images, or
                    path to a directory containing comp covers.
        genre: Genre key for scoring conventions.
    """
    ana_err = _check_analyzer_imports()
    if ana_err:
        return f"Error: {ana_err}"

    try:
        # Load the cover
        img = await anyio.to_thread.run_sync(lambda: load_image(cover_path))

        # Full analysis
        full_analysis = await anyio.to_thread.run_sync(
            lambda: analyze_cover(img, genre=genre)
        )

        # Thumbnail analysis
        thumb_analysis = await anyio.to_thread.run_sync(
            lambda: analyze_thumbnail(img, genre=genre)
        )

        # Comp analysis (optional)
        comp_data = None
        if comp_paths:
            comp_paths_stripped = comp_paths.strip()
            # Check if it's a directory
            if os.path.isdir(comp_paths_stripped):
                comps = await anyio.to_thread.run_sync(
                    lambda: load_comp_folder(comp_paths_stripped)
                )
                if comps:
                    comp_data = await anyio.to_thread.run_sync(
                        lambda: analyze_comps_batch(comps, genre=genre)
                    )
            else:
                # Comma-separated file paths
                paths = [p.strip() for p in comp_paths_stripped.split(",") if p.strip()]
                if paths:
                    comps = []
                    for p in paths:
                        try:
                            comp_img = await anyio.to_thread.run_sync(lambda p=p: load_image(p))
                            comps.append((os.path.basename(p), comp_img))
                        except Exception as e:
                            logger.warning("Skipping comp %s: %s", p, e)
                    if comps:
                        comp_data = await anyio.to_thread.run_sync(
                            lambda: analyze_comps_batch(comps, genre=genre)
                        )

        # Score
        scorecard = await anyio.to_thread.run_sync(
            lambda: score_cover(full_analysis, thumb_analysis, genre=genre, comp_data=comp_data)
        )

        result = {
            "status": "success",
            "cover_path": cover_path,
            "genre": genre,
            "full_analysis": full_analysis,
            "thumbnail_analysis": thumb_analysis,
            "score": {
                "overall": scorecard.overall_score,
                "grade": scorecard.grade,
                "grade_description": scorecard.grade_description,
                "dimensions": {d.name: {"score": d.score, "weight": d.weight, "details": d.details}
                               for d in scorecard.dimensions},
                "critical_flags": scorecard.critical_flags,
                "warning_flags": scorecard.warning_flags,
                "tip_flags": scorecard.tip_flags,
            },
        }
        if comp_data:
            result["comp_summary"] = comp_data.get("category_trends", {})
            result["comp_count"] = comp_data.get("comp_count", 0)

        return json.dumps(result, indent=2)

    except FileNotFoundError as e:
        return f"Error: File not found: {e}"
    except Exception as e:
        logger.error("cover_analyze failed: %s", e, exc_info=True)
        return f"Error analyzing cover: {type(e).__name__}: {e}"


@mcp.tool()
async def cover_quick_check(
    cover_path: str,
    genre: str = "thriller",
) -> str:
    """Quick single cover analysis without competitor comparison.

    Runs full-size and thumbnail analysis, returns a scorecard with
    grade, dimensional scores, and actionable flags. Faster and cheaper
    than cover_analyze with comps.

    Args:
        cover_path: Absolute path to the cover image.
        genre: Genre key for scoring conventions.
    """
    ana_err = _check_analyzer_imports()
    if ana_err:
        return f"Error: {ana_err}"

    try:
        img = await anyio.to_thread.run_sync(lambda: load_image(cover_path))

        full_analysis = await anyio.to_thread.run_sync(
            lambda: analyze_cover(img, genre=genre)
        )

        thumb_analysis = await anyio.to_thread.run_sync(
            lambda: analyze_thumbnail(img, genre=genre)
        )

        scorecard = await anyio.to_thread.run_sync(
            lambda: score_cover(full_analysis, thumb_analysis, genre=genre)
        )

        result = {
            "status": "success",
            "cover_path": cover_path,
            "genre": genre,
            "overall_score": scorecard.overall_score,
            "grade": scorecard.grade,
            "grade_description": scorecard.grade_description,
            "dimensions": {
                d.display_name: {"score": d.score, "details": d.details}
                for d in scorecard.dimensions
            },
            "critical_flags": scorecard.critical_flags,
            "warning_flags": scorecard.warning_flags,
            "tips": scorecard.tip_flags,
            "full_analysis": full_analysis,
            "thumbnail_analysis": thumb_analysis,
        }
        return json.dumps(result, indent=2)

    except FileNotFoundError as e:
        return f"Error: File not found: {e}"
    except Exception as e:
        logger.error("cover_quick_check failed: %s", e, exc_info=True)
        return f"Error checking cover: {type(e).__name__}: {e}"


@mcp.tool()
async def cover_compare(
    cover_paths: str,
    genre: str = "thriller",
    comps_dir: str = "",
) -> str:
    """Compare multiple cover variants and rank them.

    Analyzes each variant independently (full + thumbnail analysis),
    scores them, then produces a ranked comparison with per-dimension
    winners and a recommendation. Optionally includes competitor covers
    for differentiation scoring.

    Args:
        cover_paths: Comma-separated absolute paths to cover variant images.
        genre: Genre key for scoring conventions.
        comps_dir: Optional path to a directory of competitor cover images.
    """
    ana_err = _check_analyzer_imports()
    if ana_err:
        return f"Error: {ana_err}"

    paths = [p.strip() for p in cover_paths.split(",") if p.strip()]
    if len(paths) < 2:
        return "Error: Provide at least 2 comma-separated cover paths to compare."

    try:
        comparator = CoverComparator()

        comparison = await anyio.to_thread.run_sync(
            lambda: comparator.compare_variants(
                variant_paths=paths,
                genre=genre,
                comps_dir=comps_dir if comps_dir else None,
            )
        )

        variants_data = []
        for v in comparison.variants:
            variants_data.append({
                "label": v.label,
                "path": v.path,
                "overall_score": v.overall_score,
                "grade": v.grade,
                "dimensions": v.dimension_scores,
                "critical_flags": v.critical_flags,
                "strengths": v.strengths,
                "weaknesses": v.weaknesses,
            })

        result = {
            "status": "success",
            "genre": genre,
            "variant_count": len(paths),
            "variants": variants_data,
            "winner": {
                "label": comparison.winner.label if comparison.winner else None,
                "path": comparison.winner.path if comparison.winner else None,
                "score": comparison.winner.overall_score if comparison.winner else None,
                "grade": comparison.winner.grade if comparison.winner else None,
            },
            "dimension_winners": comparison.dimension_winners,
            "recommendation": comparison.recommendation,
        }
        return json.dumps(result, indent=2)

    except FileNotFoundError as e:
        return f"Error: File not found: {e}"
    except Exception as e:
        logger.error("cover_compare failed: %s", e, exc_info=True)
        return f"Error comparing covers: {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main():
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
