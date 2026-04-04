"""MCP server wrapping four research tools for indie publishing."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import anyio
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-research-tools")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy imports — each wrapped in try/except so the server starts even if a
# package isn't installed yet.
# ---------------------------------------------------------------------------

_also_bought_available = False
_geo_available = False
_indie_available = False
_arc_available = False

try:
    from also_bought_mapper.config import load_data, save_data
    from also_bought_mapper.mapper import (
        build_network_from_data,
        find_comps,
        get_clusters,
        get_network_stats,
        import_html_snapshot,
    )
    from also_bought_mapper.scraper import load_html_file
    _also_bought_available = True
except ImportError:
    logger.warning("also_bought_mapper not installed — those tools will be unavailable")

try:
    from geo_optimizer.analyzers import run_all_analyzers
    from geo_optimizer.recommendations import generate_recommendations
    from geo_optimizer.scorer import calculate_geo_score
    _geo_available = True
except ImportError:
    logger.warning("geo_optimizer not installed — those tools will be unavailable")

try:
    from indie_scout.analyzer import generate_report
    from indie_scout.config import Config as IndieConfig
    from indie_scout.db import Database as IndieDB
    from indie_scout.parsers import get_parser
    from indie_scout.scoring import score_indie
    _indie_available = True
except ImportError:
    logger.warning("indie_scout not installed — those tools will be unavailable")

try:
    from arc_manager.config import get_config as arc_config
    from arc_manager.db import (
        BookRepository,
        DistributionRepository,
        ReviewerRepository,
        init_db as arc_init_db,
    )
    from arc_manager.email_templates import (
        download_reminder_email,
        review_reminder_email,
    )
    from arc_manager.models import (
        ARCBook,
        Distribution,
        DistributionStatus,
        Platform,
        Reviewer,
    )
    from arc_manager.tracker import (
        get_overdue_distributions,
        update_reputation_scores,
    )
    from arc_manager.watermark import generate_watermark_id
    _arc_available = True
except ImportError:
    logger.warning("arc_manager not installed — those tools will be unavailable")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require(flag: bool, name: str) -> None:
    if not flag:
        raise RuntimeError(f"{name} package is not installed. pip install it first.")


def _arc_db_path() -> str:
    cfg = arc_config()
    arc_init_db(cfg.db_path)
    return cfg.db_path


def _indie_db() -> "IndieDB":
    path = IndieConfig.get_db_path()
    return IndieDB(path)


# ---------------------------------------------------------------------------
# Also-Bought Mapper tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def research_also_bought_import(asin: str, html_path: str) -> str:
    """Import an also-bought HTML snapshot for a given ASIN.

    Args:
        asin: The Amazon ASIN of the source product page.
        html_path: Absolute path to the saved HTML file.
    """
    _require(_also_bought_available, "also_bought_mapper")

    def _run() -> dict:
        html = load_html_file(html_path)
        data = load_data()
        network, new_count = import_html_snapshot(html, asin, data)
        save_data(data)
        stats = get_network_stats(network)
        return {
            "status": "ok",
            "asin": asin,
            "new_books_found": new_count,
            "network": stats,
        }

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2)


@mcp.tool()
async def research_also_bought_map(seed_asin: str, depth: int = 1) -> str:
    """Map the also-bought network starting from a seed ASIN.

    Args:
        seed_asin: The ASIN to start mapping from.
        depth: How many hops to traverse (1 = direct neighbours only).
    """
    _require(_also_bought_available, "also_bought_mapper")

    def _run() -> dict:
        data = load_data()
        network = build_network_from_data(data)

        if seed_asin not in network.nodes:
            return {"error": f"ASIN {seed_asin} not found in network. Import its page first."}

        # Collect nodes within requested depth via BFS
        visited: set[str] = set()
        queue: list[tuple[str, int]] = [(seed_asin, 0)]
        while queue:
            current, d = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            if d < depth:
                for neighbor in network.get_neighbors(current):
                    if neighbor not in visited:
                        queue.append((neighbor, d + 1))

        nodes = []
        for asin in visited:
            node = network.nodes.get(asin)
            if node:
                nodes.append(asdict(node))

        stats = get_network_stats(network)
        return {
            "seed_asin": seed_asin,
            "depth": depth,
            "nodes_in_subgraph": len(nodes),
            "nodes": nodes,
            "full_network_stats": stats,
        }

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2)


@mcp.tool()
async def research_also_bought_comps(seed_asin: str) -> str:
    """Find top comp titles by centrality for a given ASIN.

    Args:
        seed_asin: The ASIN to find comps for.
    """
    _require(_also_bought_available, "also_bought_mapper")

    def _run() -> dict:
        data = load_data()
        network = build_network_from_data(data)
        if seed_asin not in network.nodes:
            return {"error": f"ASIN {seed_asin} not found in network."}
        comps = find_comps(network, seed_asin, top_n=10)
        return {"seed_asin": seed_asin, "comps": comps}

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2)


@mcp.tool()
async def research_also_bought_clusters() -> str:
    """Show connected clusters in the also-bought network."""
    _require(_also_bought_available, "also_bought_mapper")

    def _run() -> dict:
        data = load_data()
        network = build_network_from_data(data)
        clusters = get_clusters(network)
        cluster_info = []
        for i, cluster in enumerate(clusters):
            titles = []
            for asin in cluster[:10]:  # Cap preview at 10
                node = network.nodes.get(asin)
                titles.append({"asin": asin, "title": node.title if node else "?"})
            cluster_info.append({
                "cluster_id": i,
                "size": len(cluster),
                "sample": titles,
            })
        stats = get_network_stats(network)
        return {
            "total_clusters": len(clusters),
            "clusters": cluster_info,
            "network_stats": stats,
        }

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# GEO Optimizer tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def research_geo_analyze(file_path: str) -> str:
    """Run a full GEO analysis on an HTML or text file.

    Args:
        file_path: Absolute path to the page file (HTML or plain text).
    """
    _require(_geo_available, "geo_optimizer")

    def _run() -> dict:
        p = Path(file_path)
        content = p.read_text(encoding="utf-8", errors="replace")
        html = content if p.suffix.lower() in (".html", ".htm") else None
        is_book = "book" in p.name.lower() or "/book" in str(p).lower()

        results = run_all_analyzers(content, html, is_book_page=is_book)
        geo_score = calculate_geo_score(results, is_book_page=is_book)
        recs = generate_recommendations(results)

        return {
            "file": str(p),
            "overall_score": geo_score.overall_score,
            "grade": geo_score.grade,
            "category_scores": geo_score.category_scores,
            "top_issues": geo_score.top_issues,
            "recommendations": [
                {
                    "priority": r.priority,
                    "category": r.category,
                    "issue": r.issue,
                    "fix": r.fix,
                    "impact": r.impact,
                }
                for r in recs
            ],
        }

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2)


@mcp.tool()
async def research_geo_score(file_path: str) -> str:
    """Quick GEO score (0-100) for a page file.

    Args:
        file_path: Absolute path to the page file.
    """
    _require(_geo_available, "geo_optimizer")

    def _run() -> dict:
        p = Path(file_path)
        content = p.read_text(encoding="utf-8", errors="replace")
        html = content if p.suffix.lower() in (".html", ".htm") else None
        is_book = "book" in p.name.lower() or "/book" in str(p).lower()

        results = run_all_analyzers(content, html, is_book_page=is_book)
        geo_score = calculate_geo_score(results, is_book_page=is_book)

        return {
            "file": str(p),
            "score": geo_score.overall_score,
            "grade": geo_score.grade,
        }

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2)


@mcp.tool()
async def research_geo_compare(file_path_a: str, file_path_b: str) -> str:
    """Compare GEO scores of two pages side by side.

    Args:
        file_path_a: Absolute path to the first page file.
        file_path_b: Absolute path to the second page file.
    """
    _require(_geo_available, "geo_optimizer")

    def _run() -> dict:
        scores = {}
        for label, fp in [("a", file_path_a), ("b", file_path_b)]:
            p = Path(fp)
            content = p.read_text(encoding="utf-8", errors="replace")
            html = content if p.suffix.lower() in (".html", ".htm") else None
            is_book = "book" in p.name.lower() or "/book" in str(p).lower()

            results = run_all_analyzers(content, html, is_book_page=is_book)
            geo_score = calculate_geo_score(results, is_book_page=is_book)
            recs = generate_recommendations(results)

            scores[label] = {
                "file": str(p),
                "overall_score": geo_score.overall_score,
                "grade": geo_score.grade,
                "category_scores": geo_score.category_scores,
                "top_issues": geo_score.top_issues,
                "recommendation_count": len(recs),
            }

        diff = round(scores["a"]["overall_score"] - scores["b"]["overall_score"], 1)
        return {
            "page_a": scores["a"],
            "page_b": scores["b"],
            "score_difference": diff,
            "winner": "a" if diff > 0 else ("b" if diff < 0 else "tie"),
        }

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Indie Scout tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def research_indie_import(source_path: str, format: str = "text") -> str:
    """Import books from a bestseller data file.

    Args:
        source_path: Absolute path to the source file.
        format: File format — text, csv, or json.
    """
    _require(_indie_available, "indie_scout")

    def _run() -> dict:
        p = Path(source_path)
        content = p.read_text(encoding="utf-8", errors="replace")
        parser = get_parser(filename=p.name, content=content)
        books = parser.parse(content)

        db = _indie_db()
        try:
            imported = 0
            for book in books:
                db.add_book(book)
                imported += 1
            return {
                "status": "ok",
                "source": str(p),
                "format_detected": type(parser).__name__,
                "books_parsed": len(books),
                "books_imported": imported,
            }
        finally:
            db.close()

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2)


@mcp.tool()
async def research_indie_scan() -> str:
    """Compute indie scores for all authors in the database."""
    _require(_indie_available, "indie_scout")

    def _run() -> dict:
        db = _indie_db()
        try:
            author_names = db.get_all_author_names()
            scored = []
            for name in author_names:
                books = db.get_books_by_author(name)
                if not books:
                    continue
                from indie_scout.models import Author as IndieAuthor
                author = db.get_author(name) or IndieAuthor(name=name)
                author.book_count = len(books)

                result = score_indie(author, books)
                author.indie_score = result.composite
                author.is_indie = result.composite >= 60
                db.upsert_author(author)

                scored.append({
                    "name": name,
                    "indie_score": result.composite,
                    "books": len(books),
                    "details": result.details,
                })

            scored.sort(key=lambda x: x["indie_score"], reverse=True)
            return {
                "authors_scored": len(scored),
                "authors": scored[:50],
            }
        finally:
            db.close()

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def research_indie_filter(
    min_score: float = 0,
    genre: str = "",
    max_results: int = 25,
) -> str:
    """Filter books by indie score and optional genre.

    Args:
        min_score: Minimum indie score threshold (0-100).
        genre: Genre or category substring to filter by.
        max_results: Maximum number of results to return.
    """
    _require(_indie_available, "indie_scout")

    def _run() -> dict:
        db = _indie_db()
        try:
            rows = db.filter_books(
                min_score=min_score,
                category=genre,
                sort="score",
                limit=max_results,
            )
            results = []
            for r in rows:
                book = r["book"]
                results.append({
                    "title": book.title,
                    "author": book.author_name,
                    "bsr": book.bsr,
                    "rating": book.rating,
                    "review_count": book.review_count,
                    "price": book.price,
                    "ku_enrolled": book.ku_enrolled,
                    "indie_score": r["indie_score"],
                })
            return {
                "filters": {
                    "min_score": min_score,
                    "genre": genre,
                    "max_results": max_results,
                },
                "count": len(results),
                "books": results,
            }
        finally:
            db.close()

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def research_indie_report() -> str:
    """Generate an AI-powered market report from the indie scout database."""
    _require(_indie_available, "indie_scout")

    def _run() -> dict:
        db = _indie_db()
        try:
            books = db.list_books(sort="bsr", limit=50)
            if not books:
                return {"error": "No books in database. Import data first."}
            report = generate_report(books)
            return {"status": "ok", "report": report}
        except Exception as e:
            return {"error": str(e)}
        finally:
            db.close()

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2, default=str)


# ---------------------------------------------------------------------------
# ARC Manager tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def research_arc_add_reviewer(
    name: str,
    email: str,
    platform: str = "amazon",
    genres: str = "",
    avg_rating: float = 0.0,
) -> str:
    """Add an ARC reviewer to the database.

    Args:
        name: Reviewer's display name.
        email: Reviewer's email address.
        platform: Review platform (amazon, goodreads, bookbub, blog, instagram, tiktok).
        genres: Comma-separated genre tags.
        avg_rating: Reviewer's average star rating.
    """
    _require(_arc_available, "arc_manager")

    def _run() -> dict:
        db_path = _arc_db_path()
        repo = ReviewerRepository(db_path)

        existing = repo.find_by_email(email)
        if existing:
            return {"error": f"Reviewer with email {email} already exists (id={existing.id})."}

        tags = [t.strip() for t in genres.split(",") if t.strip()]
        reviewer = Reviewer(
            id=None,
            name=name,
            email=email,
            platform=Platform(platform.lower()),
            tags=tags,
            notes=f"avg_rating={avg_rating}" if avg_rating else "",
        )
        reviewer = repo.add(reviewer)
        return {
            "status": "ok",
            "reviewer_id": reviewer.id,
            "name": reviewer.name,
            "email": reviewer.email,
            "platform": reviewer.platform.value,
        }

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2)


@mcp.tool()
async def research_arc_send(book_title: str, reviewer_name: str) -> str:
    """Create an ARC distribution record for a book and reviewer.

    Args:
        book_title: Title (or partial title) of the book.
        reviewer_name: Name (or partial name) of the reviewer.
    """
    _require(_arc_available, "arc_manager")

    def _run() -> dict:
        db_path = _arc_db_path()
        book_repo = BookRepository(db_path)
        reviewer_repo = ReviewerRepository(db_path)
        dist_repo = DistributionRepository(db_path)

        book = book_repo.find_by_title(book_title)
        if not book:
            return {"error": f"Book '{book_title}' not found. Add it first."}

        matches = reviewer_repo.find_by_name(reviewer_name)
        if not matches:
            return {"error": f"No reviewer matching '{reviewer_name}'."}
        reviewer = matches[0]

        existing = dist_repo.find_by_book_and_reviewer(book.id, reviewer.id)
        if existing:
            return {"error": f"ARC already sent to {reviewer.name} for '{book.title}' (id={existing.id})."}

        wm_id = generate_watermark_id()
        dist = Distribution(
            id=None,
            book_id=book.id,
            reviewer_id=reviewer.id,
            status=DistributionStatus.SENT,
            watermark_id=wm_id,
        )
        dist = dist_repo.add(dist)
        return {
            "status": "ok",
            "distribution_id": dist.id,
            "book": book.title,
            "reviewer": reviewer.name,
            "watermark_id": wm_id,
        }

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2)


@mcp.tool()
async def research_arc_status(book_title: str) -> str:
    """Show the ARC distribution dashboard for a book.

    Args:
        book_title: Title (or partial title) of the book.
    """
    _require(_arc_available, "arc_manager")

    def _run() -> dict:
        db_path = _arc_db_path()
        book_repo = BookRepository(db_path)
        dist_repo = DistributionRepository(db_path)
        reviewer_repo = ReviewerRepository(db_path)

        book = book_repo.find_by_title(book_title)
        if not book:
            return {"error": f"Book '{book_title}' not found."}

        stats = dist_repo.get_stats(book.id)
        dists = dist_repo.get_by_book(book.id)

        rows = []
        for d in dists:
            matches = reviewer_repo.find_by_name("")  # get all
            rev = None
            for r in reviewer_repo.list_all():
                if r.id == d.reviewer_id:
                    rev = r
                    break
            rows.append({
                "reviewer": rev.name if rev else f"id={d.reviewer_id}",
                "status": d.status.value,
                "sent_date": d.sent_date[:10] if d.sent_date else "",
                "review_date": d.review_date[:10] if d.review_date else "",
                "rating": d.review_rating,
                "reminders": d.reminder_count,
            })

        return {
            "book": book.title,
            "stats": asdict(stats),
            "distributions": rows,
        }

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def research_arc_overdue() -> str:
    """Show all overdue ARC distributions (no review after 14+ days)."""
    _require(_arc_available, "arc_manager")

    def _run() -> dict:
        db_path = _arc_db_path()
        overdue = get_overdue_distributions(db_path, days=14)
        reviewer_repo = ReviewerRepository(db_path)
        book_repo = BookRepository(db_path)

        all_reviewers = {r.id: r for r in reviewer_repo.list_all()}
        all_books = {b.id: b for b in book_repo.list_all()}

        rows = []
        for d in overdue:
            rev = all_reviewers.get(d.reviewer_id)
            book = all_books.get(d.book_id)
            rows.append({
                "distribution_id": d.id,
                "book": book.title if book else f"book_id={d.book_id}",
                "reviewer": rev.name if rev else f"reviewer_id={d.reviewer_id}",
                "sent_date": d.sent_date[:10] if d.sent_date else "",
                "status": d.status.value,
                "reminders_sent": d.reminder_count,
            })

        return {"overdue_count": len(rows), "distributions": rows}

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def research_arc_remind(book_title: str) -> str:
    """Generate reminder emails for overdue ARC distributions of a book.

    Args:
        book_title: Title (or partial title) of the book.
    """
    _require(_arc_available, "arc_manager")

    def _run() -> dict:
        db_path = _arc_db_path()
        book_repo = BookRepository(db_path)
        dist_repo = DistributionRepository(db_path)
        reviewer_repo = ReviewerRepository(db_path)

        book = book_repo.find_by_title(book_title)
        if not book:
            return {"error": f"Book '{book_title}' not found."}

        overdue = get_overdue_distributions(db_path, days=14)
        book_overdue = [d for d in overdue if d.book_id == book.id]

        if not book_overdue:
            return {"book": book.title, "message": "No overdue distributions."}

        all_reviewers = {r.id: r for r in reviewer_repo.list_all()}
        emails = []
        for d in book_overdue:
            rev = all_reviewers.get(d.reviewer_id)
            if not rev:
                continue

            if d.status == DistributionStatus.SENT:
                subj, body = download_reminder_email(rev, book, d)
            else:
                subj, body = review_reminder_email(rev, book, d)

            emails.append({
                "reviewer": rev.name,
                "email": rev.email,
                "subject": subj,
                "body": body,
            })

        return {
            "book": book.title,
            "reminders_generated": len(emails),
            "emails": emails,
        }

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def research_arc_reputation() -> str:
    """Recalculate and show reviewer reputation scores, ranked best to worst."""
    _require(_arc_available, "arc_manager")

    def _run() -> dict:
        db_path = _arc_db_path()
        updated = update_reputation_scores(db_path)
        reviewer_repo = ReviewerRepository(db_path)
        reviewers = reviewer_repo.list_all()

        rows = []
        for r in reviewers:
            rows.append({
                "name": r.name,
                "email": r.email,
                "platform": r.platform.value,
                "reputation_score": r.reputation_score,
                "total_arcs": r.total_arcs_sent,
                "reviews_left": r.total_reviews_left,
                "avg_days": r.avg_days_to_review,
            })

        return {
            "reviewers_updated": updated,
            "reviewers": rows,
        }

    result = await anyio.to_thread.run_sync(_run)
    return json.dumps(result, indent=2, default=str)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
