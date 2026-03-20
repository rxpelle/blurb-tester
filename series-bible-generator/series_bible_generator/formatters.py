"""Rich console and text output formatting."""

import json
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from .models import (
    ComplianceReport, ExtractionResult, QueryResult,
    ValidationIssue,
)


SEVERITY_COLORS = {
    "error": "red",
    "warning": "yellow",
    "info": "blue",
}

SEVERITY_ICONS = {
    "error": "X",
    "warning": "!",
    "info": "i",
}


def format_compliance_rich(
    report: ComplianceReport,
    min_severity: str = "info",
    console: Optional[Console] = None,
):
    """Display compliance report with Rich formatting."""
    console = console or Console()

    # Header
    grade_color = "green" if report.score >= 90 else "yellow" if report.score >= 70 else "red"
    console.print(Panel(
        f"[bold {grade_color}]Score: {report.score}/100[/bold {grade_color}]\n"
        f"Checks: {report.passed_checks}/{report.total_checks} passed\n"
        f"Chapters: {len(report.chapters_validated)}",
        title="[bold]Series Bible Compliance Report[/bold]",
        subtitle=report.manuscript_path,
    ))

    if report.summary:
        console.print(f"\n{report.summary}\n")

    # Issues table
    severity_order = {"info": 0, "warning": 1, "error": 2}
    min_level = severity_order.get(min_severity, 0)
    filtered = [i for i in report.issues if severity_order.get(i.severity, 0) >= min_level]

    if filtered:
        table = Table(title="Issues", show_lines=True)
        table.add_column("Sev", width=5)
        table.add_column("Category", width=12)
        table.add_column("Description", min_width=30)
        table.add_column("Location", width=20)
        table.add_column("Suggestion", min_width=20)

        for issue in sorted(filtered, key=lambda x: -severity_order.get(x.severity, 0)):
            color = SEVERITY_COLORS.get(issue.severity, "white")
            icon = SEVERITY_ICONS.get(issue.severity, "?")
            table.add_row(
                f"[{color}]{icon}[/{color}]",
                issue.category,
                issue.description,
                issue.location,
                issue.suggestion or "",
            )

        console.print(table)
    else:
        console.print("[green]No issues found at this severity level.[/green]")


def format_extraction_rich(
    result: ExtractionResult,
    console: Optional[Console] = None,
):
    """Display extraction results with Rich formatting."""
    console = console or Console()

    console.print(Panel(
        f"Chapters processed: {result.chapters_processed}\n"
        f"Total entities: {result.total_entities}\n"
        f"  Characters: {len(result.characters)}\n"
        f"  Events: {len(result.events)}\n"
        f"  Terms: {len(result.terms)}\n"
        f"  Locations: {len(result.locations)}\n"
        f"  Artifacts: {len(result.artifacts)}",
        title="[bold]Extraction Results[/bold]",
    ))

    if result.characters:
        table = Table(title="Characters")
        table.add_column("Name", min_width=15)
        table.add_column("Role", width=12)
        table.add_column("Network", width=10)
        table.add_column("Description", min_width=30)

        for c in result.characters[:50]:
            table.add_row(c.name, c.role or "-", c.network or "-", c.description[:60] or "-")

        console.print(table)

    if result.events:
        table = Table(title="Timeline Events")
        table.add_column("Date", width=15)
        table.add_column("Description", min_width=30)
        table.add_column("Significance", width=12)

        for e in result.events[:30]:
            table.add_row(e.date or "-", e.description[:60], e.significance or "-")

        console.print(table)

    if result.terms:
        table = Table(title="Terminology")
        table.add_column("Term", min_width=15)
        table.add_column("Definition", min_width=40)

        for t in result.terms[:20]:
            table.add_row(t.term, t.definition[:60] or "-")

        console.print(table)


def format_query_rich(
    result: QueryResult,
    console: Optional[Console] = None,
):
    """Display query results with Rich formatting."""
    console = console or Console()

    console.print(f"\n[bold]Query:[/bold] {result.query}")
    console.print(f"[dim]Results: {len(result.results)} | Type: {result.result_type}[/dim]\n")

    has_answer = any(r.get("type") == "answer" for r in result.results)
    if has_answer:
        for r in result.results:
            if r.get("type") == "answer":
                console.print(Panel(r["content"], title="Answer"))
                break
    else:
        for r in result.results:
            rtype = r.get("type", "unknown")
            if rtype == "character":
                console.print(
                    f"  [bold cyan]{r['name']}[/bold cyan] "
                    f"(Gen {r.get('generation', '?')}, {r.get('network', '?')}): "
                    f"{r.get('description', '')[:80]}"
                )
            elif rtype == "event":
                console.print(
                    f"  [bold yellow]{r.get('date', '?')}[/bold yellow]: "
                    f"{r.get('description', '')[:80]}"
                )
            elif rtype == "term":
                console.print(
                    f"  [bold green]{r.get('term', '?')}[/bold green]: "
                    f"{r.get('definition', '')[:80]}"
                )
            elif rtype == "artifact":
                console.print(
                    f"  [bold magenta]{r.get('name', '?')}[/bold magenta]: "
                    f"{r.get('description', '')[:80]}"
                )
            elif rtype == "location":
                console.print(
                    f"  [bold blue]{r.get('name', '?')}[/bold blue]: "
                    f"{r.get('description', '')[:80]}"
                )

    if result.sources:
        console.print(f"\n[dim]Sources: {', '.join(result.sources)}[/dim]")


def format_stats_rich(stats: dict, console: Optional[Console] = None):
    """Display database statistics with Rich formatting."""
    console = console or Console()

    table = Table(title="Series Bible Database")
    table.add_column("Entity Type", min_width=15)
    table.add_column("Count", justify="right", width=10)

    for key in ["characters", "events", "terms", "artifacts", "locations"]:
        table.add_row(key.title(), str(stats.get(key, 0)))

    table.add_row("[bold]Total[/bold]", f"[bold]{stats.get('total', 0)}[/bold]")
    console.print(table)

    ingested = stats.get("ingested_files", [])
    if ingested:
        console.print(f"\n[bold]Ingested Bible Files ({len(ingested)}):[/bold]")
        for f in ingested:
            console.print(f"  {f['doc_type']}: {f['file_path']} (last: {f['last_ingested']})")
    else:
        console.print("\n[yellow]No bible files ingested yet. Run 'series-bible ingest' first.[/yellow]")


def format_compliance_text(report: ComplianceReport, min_severity: str = "info") -> str:
    """Format compliance report as plain text."""
    from .generator import generate_compliance_markdown
    return generate_compliance_markdown(report)


def format_extraction_text(result: ExtractionResult) -> str:
    """Format extraction results as plain text."""
    lines = [
        f"Extraction Results",
        f"==================",
        f"Chapters: {result.chapters_processed}",
        f"Total entities: {result.total_entities}",
        f"",
    ]

    if result.characters:
        lines.append("Characters:")
        for c in result.characters:
            lines.append(f"  - {c.name} ({c.role or '?'}): {c.description}")
    if result.events:
        lines.append("\nEvents:")
        for e in result.events:
            lines.append(f"  - {e.date}: {e.description}")
    if result.terms:
        lines.append("\nTerms:")
        for t in result.terms:
            lines.append(f"  - {t.term}: {t.definition}")

    return "\n".join(lines)
