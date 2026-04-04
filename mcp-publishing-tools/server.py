"""MCP server wrapping 4 publishing tools: kdp_scout, kdp_publisher, book_formatter, launch_orchestrator."""

import json
import traceback
from typing import Optional

import anyio
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-publishing-tools")

# ---------------------------------------------------------------------------
# Lazy imports with graceful fallback
# ---------------------------------------------------------------------------

def _import_kdp_scout():
    """Import kdp_scout modules."""
    from kdp_scout.keyword_engine import mine_keywords, KeywordScorer
    from kdp_scout.competitor_engine import CompetitorEngine
    from kdp_scout.niche_scorer import score_niche
    from kdp_scout.db import init_db
    return {
        'mine_keywords': mine_keywords,
        'KeywordScorer': KeywordScorer,
        'CompetitorEngine': CompetitorEngine,
        'score_niche': score_niche,
        'init_db': init_db,
    }


def _import_kdp_publisher():
    """Import kdp_publisher modules."""
    from kdp_publisher.publisher import validate_all, generate_checklist
    from kdp_publisher.metadata import (
        get_or_create_metadata, set_metadata_field, export_metadata,
    )
    from kdp_publisher.db import get_connection, init_db, get_book_by_id, get_book_by_title
    return {
        'validate_all': validate_all,
        'generate_checklist': generate_checklist,
        'get_or_create_metadata': get_or_create_metadata,
        'set_metadata_field': set_metadata_field,
        'export_metadata': export_metadata,
        'get_connection': get_connection,
        'init_db': init_db,
        'get_book_by_id': get_book_by_id,
        'get_book_by_title': get_book_by_title,
    }


def _import_book_formatter():
    """Import book_formatter modules."""
    from book_formatter.config import load_config
    from book_formatter.parsers.markdown import parse_manuscript
    from book_formatter.generators.epub_standard import StandardEPUBGenerator
    from book_formatter.generators.pdf_paperback import PaperbackPDFGenerator
    return {
        'load_config': load_config,
        'parse_manuscript': parse_manuscript,
        'StandardEPUBGenerator': StandardEPUBGenerator,
        'PaperbackPDFGenerator': PaperbackPDFGenerator,
    }


def _import_launch_orchestrator():
    """Import launch_orchestrator modules."""
    from launch_orchestrator.plan_manager import (
        load_plan, save_plan, mark_task, add_task, get_plan_summary,
    )
    from launch_orchestrator.templates import generate_default_plan
    from launch_orchestrator.alerts import get_alerts
    from launch_orchestrator.models import Task, TaskStatus
    return {
        'load_plan': load_plan,
        'save_plan': save_plan,
        'mark_task': mark_task,
        'add_task': add_task,
        'get_plan_summary': get_plan_summary,
        'generate_default_plan': generate_default_plan,
        'get_alerts': get_alerts,
        'Task': Task,
        'TaskStatus': TaskStatus,
    }


# ---------------------------------------------------------------------------
# Helper: resolve book by id or title for kdp_publisher
# ---------------------------------------------------------------------------

def _resolve_book(pub, conn, book_id: Optional[int] = None,
                  title: Optional[str] = None):
    """Resolve a book by ID or title. Returns (book, book_id)."""
    if book_id:
        book = pub['get_book_by_id'](conn, book_id)
        if not book:
            raise ValueError(f'Book with id {book_id} not found')
        return book, book_id
    elif title:
        book = pub['get_book_by_title'](conn, title)
        if not book:
            raise ValueError(f'Book with title "{title}" not found')
        return book, book.id
    else:
        raise ValueError('Either book_id or title must be provided')


# ---------------------------------------------------------------------------
# Helper: convert sqlite3.Row and dataclass objects to serializable dicts
# ---------------------------------------------------------------------------

def _row_to_dict(row):
    """Convert a sqlite3.Row to a dict."""
    if row is None:
        return None
    if hasattr(row, 'keys'):
        return {k: row[k] for k in row.keys()}
    if hasattr(row, '__dataclass_fields__'):
        return {k: getattr(row, k) for k in row.__dataclass_fields__}
    return str(row)


# ===========================================================================
# KDP Scout tools (1-4): Keyword research, competitor analysis, niche scoring
# ===========================================================================

@mcp.tool()
async def publishing_mine_keywords(seed_keyword: str, depth: int = 1) -> str:
    """Mine keywords from Amazon autocomplete for KDP keyword research.

    Args:
        seed_keyword: Seed keyword to mine (e.g. "historical fiction").
        depth: Mining depth (1 = seed + a-z expansions, 2 = recursive). Default 1.

    Returns:
        JSON with mined keywords, new/existing counts, and scores.
    """
    try:
        scout = _import_kdp_scout()
    except ImportError as e:
        return json.dumps({'error': f'kdp_scout not installed: {e}'})

    try:
        result = await anyio.to_thread.run_sync(
            lambda: scout['mine_keywords'](seed_keyword, depth=depth)
        )
        # Convert keywords tuples to serializable format
        keywords_list = [
            {'keyword': kw, 'position': pos, 'is_new': is_new}
            for kw, pos, is_new in result.get('keywords', [])
        ]
        return json.dumps({
            'seed': result['seed'],
            'depth': result['depth'],
            'new_count': result['new_count'],
            'existing_count': result['existing_count'],
            'total_mined': result['total_mined'],
            'keywords': keywords_list,
        }, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e), 'traceback': traceback.format_exc()})


@mcp.tool()
async def publishing_keyword_report(genre: str, limit: int = 50) -> str:
    """Generate a keyword research report with top-scored keywords.

    Args:
        genre: Genre or category to filter by (used as context).
        limit: Maximum keywords to return. Default 50.

    Returns:
        JSON with ranked keywords and their scores.
    """
    try:
        scout = _import_kdp_scout()
    except ImportError as e:
        return json.dumps({'error': f'kdp_scout not installed: {e}'})

    def _run():
        scorer = scout['KeywordScorer']()
        try:
            # Score any unscored keywords first
            scorer.score_all_keywords()
            top = scorer.get_top_keywords(limit=limit)
            results = []
            for kw in top:
                row = _row_to_dict(kw)
                results.append(row)
            return results
        finally:
            scorer.close()

    try:
        keywords = await anyio.to_thread.run_sync(_run)
        return json.dumps({
            'genre': genre,
            'count': len(keywords),
            'keywords': keywords,
        }, indent=2, default=str)
    except Exception as e:
        return json.dumps({'error': str(e), 'traceback': traceback.format_exc()})


@mcp.tool()
async def publishing_competitor_analyze(asin: str) -> str:
    """Analyze a competitor book by ASIN. Scrapes BSR, pricing, ratings, and estimates sales.

    Args:
        asin: Amazon ASIN of the competitor book to analyze.

    Returns:
        JSON with BSR, pricing, review count, rating, estimated sales/revenue.
    """
    try:
        scout = _import_kdp_scout()
    except ImportError as e:
        return json.dumps({'error': f'kdp_scout not installed: {e}'})

    def _run():
        engine = scout['CompetitorEngine']()
        try:
            result = engine.add_book(asin)
            if result is None:
                return {'error': f'Failed to scrape ASIN {asin}'}
            # Convert snapshot data
            output = {
                'asin': result['asin'],
                'title': result['title'],
                'author': result['author'],
                'is_new': result['is_new'],
            }
            if result.get('snapshot'):
                output['snapshot'] = result['snapshot']
            if result.get('scraped'):
                output['scraped_data'] = result['scraped']
            return output
        finally:
            engine.close()

    try:
        data = await anyio.to_thread.run_sync(_run)
        return json.dumps(data, indent=2, default=str)
    except Exception as e:
        return json.dumps({'error': str(e), 'traceback': traceback.format_exc()})


@mcp.tool()
async def publishing_niche_score(category_name: str) -> str:
    """Score a niche/category for opportunity by analyzing Amazon search results.

    Args:
        category_name: Keyword or category name to analyze (e.g. "cozy mystery").

    Returns:
        JSON with opportunity_score (0-100), metrics, and recommendation.
    """
    try:
        scout = _import_kdp_scout()
    except ImportError as e:
        return json.dumps({'error': f'kdp_scout not installed: {e}'})

    try:
        result = await anyio.to_thread.run_sync(
            lambda: scout['score_niche'](category_name)
        )
        if result is None:
            return json.dumps({'error': f'Could not analyze niche "{category_name}". Search may have failed or returned a CAPTCHA.'})

        # Simplify results (don't send full HTML-parsed result objects)
        output = {
            'keyword': result['keyword'],
            'opportunity_score': result['opportunity_score'],
            'metrics': result['metrics'],
            'recommendation': result['recommendation'],
            'top_results': [
                {
                    'asin': r.get('asin'),
                    'title': r.get('title'),
                    'price': r.get('price'),
                    'review_count': r.get('review_count'),
                    'avg_rating': r.get('avg_rating'),
                    'bsr': r.get('bsr'),
                }
                for r in result.get('results', [])[:10]
            ],
        }
        return json.dumps(output, indent=2, default=str)
    except Exception as e:
        return json.dumps({'error': str(e), 'traceback': traceback.format_exc()})


# ===========================================================================
# KDP Publisher tools (5-7): Validation, checklists, metadata
# ===========================================================================

@mcp.tool()
async def publishing_validate_book(book_id: Optional[int] = None,
                                   title: Optional[str] = None) -> str:
    """Validate book files against KDP requirements. Checks manuscript, cover, metadata.

    Args:
        book_id: Database ID of the book. Provide either book_id or title.
        title: Title of the book. Provide either book_id or title.

    Returns:
        JSON with validation results: valid (bool), errors, warnings.
    """
    try:
        pub = _import_kdp_publisher()
    except ImportError as e:
        return json.dumps({'error': f'kdp_publisher not installed: {e}'})

    def _run():
        conn = pub['get_connection']()
        try:
            pub['init_db'](conn)
            _, bid = _resolve_book(pub, conn, book_id, title)
            result = pub['validate_all'](conn, bid)
            return {
                'valid': result.valid,
                'errors': result.errors,
                'warnings': result.warnings,
            }
        finally:
            conn.close()

    try:
        data = await anyio.to_thread.run_sync(_run)
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e), 'traceback': traceback.format_exc()})


@mcp.tool()
async def publishing_checklist(book_id: Optional[int] = None,
                               title: Optional[str] = None) -> str:
    """Generate a publishing readiness checklist for a book.

    Args:
        book_id: Database ID of the book. Provide either book_id or title.
        title: Title of the book. Provide either book_id or title.

    Returns:
        JSON checklist with item name, status (pass/fail), and details.
    """
    try:
        pub = _import_kdp_publisher()
    except ImportError as e:
        return json.dumps({'error': f'kdp_publisher not installed: {e}'})

    def _run():
        conn = pub['get_connection']()
        try:
            pub['init_db'](conn)
            _, bid = _resolve_book(pub, conn, book_id, title)
            checklist = pub['generate_checklist'](conn, bid)
            items = []
            for item in checklist.items:
                items.append({
                    'name': item.name,
                    'status': item.status,
                    'details': item.details,
                })
            return {
                'ready': checklist.ready,
                'items': items,
            }
        finally:
            conn.close()

    try:
        data = await anyio.to_thread.run_sync(_run)
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e), 'traceback': traceback.format_exc()})


@mcp.tool()
async def publishing_book_metadata(book_id: int,
                                   field: Optional[str] = None,
                                   value: Optional[str] = None) -> str:
    """Show or set book metadata. If field and value are provided, sets the field.
    If only field is provided, shows that field. If neither, shows all metadata.

    Args:
        book_id: Database ID of the book.
        field: Optional metadata field to get/set (description, keywords, categories, price, language, etc.).
        value: Optional value to set for the field.

    Returns:
        JSON with current metadata (after any updates).
    """
    try:
        pub = _import_kdp_publisher()
    except ImportError as e:
        return json.dumps({'error': f'kdp_publisher not installed: {e}'})

    def _run():
        conn = pub['get_connection']()
        try:
            pub['init_db'](conn)
            if field and value:
                pub['set_metadata_field'](conn, book_id, field, value)
                conn.commit()
            meta = pub['export_metadata'](conn, book_id)
            if field and not value and meta:
                # Return just the requested field
                if field in meta:
                    return {'field': field, 'value': meta[field]}
                return {'error': f'Field "{field}" not found in metadata'}
            return {'book_id': book_id, 'metadata': meta}
        finally:
            conn.close()

    try:
        data = await anyio.to_thread.run_sync(_run)
        return json.dumps(data, indent=2, default=str)
    except Exception as e:
        return json.dumps({'error': str(e), 'traceback': traceback.format_exc()})


# ===========================================================================
# Book Formatter tools (8-9): EPUB and PDF generation
# ===========================================================================

@mcp.tool()
async def publishing_format_epub(manuscript_path: str,
                                 config_path: str,
                                 output_dir: Optional[str] = None) -> str:
    """Format a manuscript as EPUB using book-formatter.

    Args:
        manuscript_path: Path to the manuscript directory or file.
        config_path: Path to book.yaml config file.
        output_dir: Optional output directory override.

    Returns:
        JSON with output file path.
    """
    try:
        bf = _import_book_formatter()
    except ImportError as e:
        return json.dumps({'error': f'book_formatter not installed: {e}'})

    def _run():
        config = bf['load_config'](config_path)
        if output_dir:
            config.output = output_dir
        book = bf['parse_manuscript'](config)
        generator = bf['StandardEPUBGenerator'](config, book)
        output_path = generator.build()
        return {'output_path': output_path, 'format': 'epub'}

    try:
        data = await anyio.to_thread.run_sync(_run)
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e), 'traceback': traceback.format_exc()})


@mcp.tool()
async def publishing_format_paperback(manuscript_path: str,
                                      config_path: str,
                                      trim_size: Optional[str] = None,
                                      output_dir: Optional[str] = None) -> str:
    """Format a manuscript as PDF for KDP paperback printing.

    Args:
        manuscript_path: Path to the manuscript directory or file.
        config_path: Path to book.yaml config file.
        trim_size: Optional trim size (e.g. "5.5x8.5", "6x9"). Uses config default if not specified.
        output_dir: Optional output directory override.

    Returns:
        JSON with output file path.
    """
    try:
        bf = _import_book_formatter()
    except ImportError as e:
        return json.dumps({'error': f'book_formatter not installed: {e}'})

    def _run():
        config = bf['load_config'](config_path)
        if output_dir:
            config.output = output_dir
        book = bf['parse_manuscript'](config)
        generator = bf['PaperbackPDFGenerator'](config, book, trim=trim_size)
        output_path = generator.build()
        return {'output_path': output_path, 'format': 'pdf', 'trim_size': trim_size or config.print_settings.trim}

    try:
        data = await anyio.to_thread.run_sync(_run)
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e), 'traceback': traceback.format_exc()})


# ===========================================================================
# Launch Orchestrator tools (10-14): Launch plan management
# ===========================================================================

@mcp.tool()
async def publishing_launch_init(book_title: str,
                                 launch_date: str,
                                 author: str = '',
                                 series: str = '') -> str:
    """Create a new launch plan from the default template.

    Args:
        book_title: Title of the book being launched.
        launch_date: Launch date in YYYY-MM-DD format.
        author: Author name.
        series: Series name (optional).

    Returns:
        JSON with plan path and summary.
    """
    try:
        lo = _import_launch_orchestrator()
    except ImportError as e:
        return json.dumps({'error': f'launch_orchestrator not installed: {e}'})

    def _run():
        plan = lo['generate_default_plan'](
            title=book_title,
            launch_date=launch_date,
            author=author,
            series=series,
        )
        # Save to a file named after the book
        safe_name = book_title.lower().replace(' ', '_').replace(':', '')
        plan_path = f'launch_plans/{safe_name}.yaml'
        lo['save_plan'](plan, plan_path)
        summary = lo['get_plan_summary'](plan)
        return {
            'plan_path': plan_path,
            'book_title': book_title,
            'launch_date': launch_date,
            'summary': summary,
        }

    try:
        data = await anyio.to_thread.run_sync(_run)
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e), 'traceback': traceback.format_exc()})


@mcp.tool()
async def publishing_launch_status(plan_path: str) -> str:
    """Show launch plan dashboard with task statuses and progress.

    Args:
        plan_path: Path to the launch plan YAML file.

    Returns:
        JSON with plan details, phases, tasks, and progress summary.
    """
    try:
        lo = _import_launch_orchestrator()
    except ImportError as e:
        return json.dumps({'error': f'launch_orchestrator not installed: {e}'})

    def _run():
        plan = lo['load_plan'](plan_path)
        summary = lo['get_plan_summary'](plan)
        phases = []
        for phase in plan.phases:
            tasks = []
            for task in phase.tasks:
                tasks.append({
                    'name': task.name,
                    'status': task.status.value,
                    'description': task.description,
                    'tool': task.tool,
                    'notes': task.notes,
                    'completed_date': task.completed_date,
                })
            phases.append({
                'name': phase.name,
                'offset_days': phase.offset_days,
                'date': phase.date,
                'tasks': tasks,
            })
        return {
            'book_title': plan.book_title,
            'launch_date': plan.launch_date,
            'author': plan.author,
            'series': plan.series,
            'status': plan.status,
            'summary': summary,
            'phases': phases,
        }

    try:
        data = await anyio.to_thread.run_sync(_run)
        return json.dumps(data, indent=2, default=str)
    except Exception as e:
        return json.dumps({'error': str(e), 'traceback': traceback.format_exc()})


@mcp.tool()
async def publishing_launch_update(plan_path: str,
                                   task_name: str,
                                   status: str,
                                   notes: str = '') -> str:
    """Update a task's status in a launch plan.

    Args:
        plan_path: Path to the launch plan YAML file.
        task_name: Name (or partial name) of the task to update.
        status: New status: "pending", "in-progress", "done", "blocked", "skipped".
        notes: Optional notes about the update.

    Returns:
        JSON with updated task and plan summary.
    """
    try:
        lo = _import_launch_orchestrator()
    except ImportError as e:
        return json.dumps({'error': f'launch_orchestrator not installed: {e}'})

    def _run():
        plan = lo['load_plan'](plan_path)
        task_status = lo['TaskStatus'](status)
        task = lo['mark_task'](plan, task_name, task_status, notes=notes)
        lo['save_plan'](plan, plan_path)
        summary = lo['get_plan_summary'](plan)
        return {
            'updated_task': {
                'name': task.name,
                'status': task.status.value,
                'notes': task.notes,
                'completed_date': task.completed_date,
            },
            'summary': summary,
        }

    try:
        data = await anyio.to_thread.run_sync(_run)
        return json.dumps(data, indent=2, default=str)
    except Exception as e:
        return json.dumps({'error': str(e), 'traceback': traceback.format_exc()})


@mcp.tool()
async def publishing_launch_alerts(plan_path: str) -> str:
    """Show launch plan alerts: overdue, due today, and upcoming tasks.

    Args:
        plan_path: Path to the launch plan YAML file.

    Returns:
        JSON with alerts grouped by severity (overdue, due_today, upcoming).
    """
    try:
        lo = _import_launch_orchestrator()
    except ImportError as e:
        return json.dumps({'error': f'launch_orchestrator not installed: {e}'})

    def _run():
        plan = lo['load_plan'](plan_path)
        alerts = lo['get_alerts'](plan)
        result = {}
        for severity in ('overdue', 'due_today', 'upcoming'):
            items = []
            for phase, task, phase_date in alerts.get(severity, []):
                items.append({
                    'phase': phase.name,
                    'task': task.name,
                    'status': task.status.value,
                    'date': str(phase_date),
                })
            result[severity] = items
        result['total_alerts'] = sum(len(v) for v in result.values())
        return result

    try:
        data = await anyio.to_thread.run_sync(_run)
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e), 'traceback': traceback.format_exc()})


@mcp.tool()
async def publishing_launch_add_task(plan_path: str,
                                     phase: str,
                                     task_name: str,
                                     description: str = '') -> str:
    """Add a new task to a launch plan phase.

    Args:
        plan_path: Path to the launch plan YAML file.
        phase: Name of the phase to add the task to (e.g. "T-30", "Launch Day").
        task_name: Name of the new task.
        description: Optional description of the task.

    Returns:
        JSON with the added task and updated plan summary.
    """
    try:
        lo = _import_launch_orchestrator()
    except ImportError as e:
        return json.dumps({'error': f'launch_orchestrator not installed: {e}'})

    def _run():
        plan = lo['load_plan'](plan_path)
        new_task = lo['Task'](name=task_name, description=description)
        matched_phase = lo['add_task'](plan, phase, new_task)
        lo['save_plan'](plan, plan_path)
        summary = lo['get_plan_summary'](plan)
        return {
            'added_task': {
                'name': new_task.name,
                'description': new_task.description,
                'status': new_task.status.value,
                'phase': matched_phase.name,
            },
            'summary': summary,
        }

    try:
        data = await anyio.to_thread.run_sync(_run)
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e), 'traceback': traceback.format_exc()})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
