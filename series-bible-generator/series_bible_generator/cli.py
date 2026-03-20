"""CLI interface for series-bible-generator."""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from .config import Config
from .db import (
    get_connection, CharacterRepository, EventRepository,
    TermRepository, ArtifactRepository, LocationRepository,
    BibleFileRepository,
)
from .extractor import extract_from_manuscript
from .formatters import (
    format_compliance_rich, format_extraction_rich,
    format_query_rich, format_stats_rich,
    format_compliance_text, format_extraction_text,
)
from .generator import generate_bible_entry, update_bible_document, generate_compliance_markdown
from .parser import parse_all_bible_files, find_bible_files, file_checksum
from .query import query_database, query_bible_files, get_stats
from .validator import validate_manuscript


console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Series Bible Generator — generate, query, validate, and maintain series bibles."""
    pass


@main.command()
@click.option("--bible-dir", "-b", required=True, type=click.Path(exists=True),
              help="Directory containing SERIES_BIBLE_*.md files")
@click.option("--force", "-f", is_flag=True, help="Re-ingest even if unchanged")
def ingest(bible_dir, force):
    """Ingest existing series bible files into the database."""
    config = Config.from_env()
    bible_path = Path(bible_dir)

    files = find_bible_files(bible_path, config.bible_prefix)
    if not files:
        console.print(f"[red]No bible files found matching {config.bible_prefix}*.md[/red]")
        return

    conn = get_connection(config)
    bible_repo = BibleFileRepository(conn)
    char_repo = CharacterRepository(conn)
    event_repo = EventRepository(conn)
    term_repo = TermRepository(conn)
    artifact_repo = ArtifactRepository(conn)
    location_repo = LocationRepository(conn)

    with console.status("[bold blue]Ingesting bible files..."):
        documents = parse_all_bible_files(bible_path, config)

    total_entities = 0
    for doc in documents:
        file_path = doc.file_path
        checksum = file_checksum(Path(file_path))

        # Skip if unchanged
        if not force:
            existing_checksum = bible_repo.get_checksum(file_path)
            if existing_checksum == checksum:
                console.print(f"  [dim]Skipping {doc.doc_type} (unchanged)[/dim]")
                continue

        # Clear old data from this source
        char_repo.delete_by_source(file_path)
        event_repo.delete_by_source(file_path)
        term_repo.delete_by_source(file_path)
        artifact_repo.delete_by_source(file_path)
        location_repo.delete_by_source(file_path)

        # Insert new data
        for char in doc.characters:
            char_repo.upsert(char)
            total_entities += 1
        for event in doc.events:
            event_repo.add(event)
            total_entities += 1
        for term in doc.terms:
            term_repo.upsert(term)
            total_entities += 1
        for artifact in doc.artifacts:
            artifact_repo.upsert(artifact)
            total_entities += 1
        for loc in doc.locations:
            location_repo.add(loc)
            total_entities += 1

        bible_repo.record_ingest(file_path, doc.doc_type, doc.title, checksum)
        console.print(f"  [green]Ingested {doc.doc_type}[/green]: "
                       f"{len(doc.characters)} chars, {len(doc.events)} events, "
                       f"{len(doc.terms)} terms, {len(doc.artifacts)} artifacts")

    conn.close()
    console.print(f"\n[bold green]Done.[/bold green] {len(documents)} files, {total_entities} entities ingested.")


@main.command()
@click.option("--manuscript", "-m", required=True, type=click.Path(exists=True),
              help="Path to manuscript directory or file")
@click.option("--book", "-b", default="", help="Book name/number for attribution")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--save/--no-save", default=True, help="Save to database")
def extract(manuscript, book, output, save):
    """Extract entities from a manuscript."""
    config = Config.from_env()
    manuscript_path = Path(manuscript)

    with console.status("[bold blue]Extracting entities..."):
        result = extract_from_manuscript(manuscript_path, book, config)

    if save:
        conn = get_connection(config)
        char_repo = CharacterRepository(conn)
        event_repo = EventRepository(conn)
        term_repo = TermRepository(conn)
        artifact_repo = ArtifactRepository(conn)
        location_repo = LocationRepository(conn)

        for char in result.characters:
            char_repo.upsert(char)
        for event in result.events:
            event_repo.add(event)
        for term in result.terms:
            term_repo.upsert(term)
        for artifact in result.artifacts:
            artifact_repo.upsert(artifact)
        for loc in result.locations:
            location_repo.add(loc)
        conn.close()

    if output:
        Path(output).write_text(format_extraction_text(result), encoding="utf-8")
        console.print(f"[green]Results written to {output}[/green]")
    else:
        format_extraction_rich(result, console=console)


@main.command()
@click.option("--type", "-t", "doc_type", required=True,
              type=click.Choice(["character_index", "timeline", "terminology", "artifact_tracker"]),
              help="Type of bible entry to generate")
@click.option("--manuscript", "-m", required=True, type=click.Path(exists=True),
              help="Source manuscript to generate from")
@click.option("--book", "-b", default="", help="Book name")
@click.option("--existing", "-e", type=click.Path(exists=True),
              help="Existing bible file (for context)")
@click.option("--output", "-o", required=True, type=click.Path(), help="Output file path")
def generate(doc_type, manuscript, book, existing, output):
    """Generate a new series bible entry from a manuscript."""
    config = Config.from_env()

    with console.status("[bold blue]Extracting entities..."):
        extraction = extract_from_manuscript(Path(manuscript), book, config)

    existing_content = ""
    if existing:
        existing_content = Path(existing).read_text(encoding="utf-8")

    with console.status("[bold blue]Generating bible entry..."):
        result = generate_bible_entry(doc_type, extraction, config, book, existing_content)

    Path(output).write_text(result, encoding="utf-8")
    console.print(f"[green]Bible entry written to {output}[/green]")
    console.print(f"  Type: {doc_type}")
    console.print(f"  Entities used: {extraction.total_entities}")


@main.command()
@click.option("--bible-file", "-f", required=True, type=click.Path(exists=True),
              help="Bible file to update")
@click.option("--manuscript", "-m", required=True, type=click.Path(exists=True),
              help="New manuscript to integrate")
@click.option("--book", "-b", default="", help="Book name")
@click.option("--output", "-o", type=click.Path(), help="Output path (default: overwrite)")
def update(bible_file, manuscript, book, output):
    """Update an existing bible file with new manuscript data."""
    config = Config.from_env()
    bible_path = Path(bible_file)

    existing = bible_path.read_text(encoding="utf-8")

    with console.status("[bold blue]Extracting from manuscript..."):
        extraction = extract_from_manuscript(Path(manuscript), book, config)

    with console.status("[bold blue]Updating bible entry..."):
        result = update_bible_document(existing, extraction, config, book)

    out_path = Path(output) if output else bible_path
    out_path.write_text(result, encoding="utf-8")
    console.print(f"[green]Updated bible file: {out_path}[/green]")


@main.command()
@click.argument("query_text")
@click.option("--bible-dir", "-b", type=click.Path(exists=True),
              help="Bible directory for file-based search")
@click.option("--ai/--no-ai", default=False, help="Use AI for semantic search")
def query(query_text, bible_dir, ai):
    """Query the series bible."""
    config = Config.from_env()

    # Search database first
    db_result = query_database(query_text, config)

    if db_result.results:
        format_query_rich(db_result, console=console)
    elif bible_dir and ai:
        # Fall back to file search with AI
        with console.status("[bold blue]Searching bible files..."):
            file_result = query_bible_files(query_text, Path(bible_dir), config)
        format_query_rich(file_result, console=console)
    elif bible_dir:
        # File search without AI
        file_result = query_bible_files(query_text, Path(bible_dir), config)
        format_query_rich(file_result, console=console)
    else:
        console.print("[yellow]No results found in database. Try --bible-dir for file search.[/yellow]")


@main.command()
@click.option("--manuscript", "-m", required=True, type=click.Path(exists=True),
              help="Manuscript to validate")
@click.option("--bible-dir", "-b", required=True, type=click.Path(exists=True),
              help="Series bible directory")
@click.option("--severity", "-s", default="info",
              type=click.Choice(["error", "warning", "info"]),
              help="Minimum severity to report")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--ai/--no-ai", default=False, help="Enable AI-powered validation")
def validate(manuscript, bible_dir, severity, output, ai):
    """Validate a manuscript against the series bible."""
    config = Config.from_env()
    if not ai:
        config.anthropic_api_key = None  # Disable AI checks

    with console.status("[bold blue]Validating manuscript..."):
        report = validate_manuscript(
            Path(manuscript), Path(bible_dir), config,
        )

    if output:
        text = generate_compliance_markdown(report)
        Path(output).write_text(text, encoding="utf-8")
        console.print(f"[green]Report written to {output}[/green]")
    else:
        format_compliance_rich(report, min_severity=severity, console=console)


@main.command()
def status():
    """Show database status and statistics."""
    config = Config.from_env()
    stats = get_stats(config)
    format_stats_rich(stats, console=console)


@main.command()
@click.option("--entity", "-e", type=click.Choice(["characters", "events", "terms", "artifacts", "locations"]),
              help="Entity type to list")
@click.option("--network", "-n", type=click.Choice(["defensive", "offensive", "neutral"]),
              help="Filter characters by network")
@click.option("--book", "-b", help="Filter by book")
@click.option("--limit", "-l", default=50, help="Max results")
def list_entities(entity, network, book, limit):
    """List entities in the database."""
    config = Config.from_env()
    conn = get_connection(config)

    from rich.table import Table

    if entity == "characters" or entity is None:
        if network:
            rows = CharacterRepository(conn).get_by_network(network)
        elif book:
            rows = CharacterRepository(conn).get_by_book(book)
        else:
            rows = CharacterRepository(conn).get_all()

        table = Table(title=f"Characters ({len(rows[:limit])} shown)")
        table.add_column("Name", min_width=15)
        table.add_column("Gen", width=5)
        table.add_column("Network", width=10)
        table.add_column("Era", width=20)
        table.add_column("Description", min_width=30)

        for r in rows[:limit]:
            table.add_row(
                r["name"],
                str(r["generation_absolute"] or "-"),
                r["network"] or "-",
                (r["era"] or "-")[:20],
                (r["description"] or "-")[:40],
            )
        console.print(table)

    elif entity == "events":
        repo = EventRepository(conn)
        rows = repo.get_by_book(book) if book else repo.get_all()

        table = Table(title=f"Timeline Events ({len(rows[:limit])} shown)")
        table.add_column("Date", width=15)
        table.add_column("Description", min_width=30)
        table.add_column("Location", width=20)

        for r in rows[:limit]:
            table.add_row(r["date"], (r["description"] or "-")[:50], (r["location"] or "-")[:20])
        console.print(table)

    elif entity == "terms":
        rows = TermRepository(conn).get_all()

        table = Table(title=f"Glossary Terms ({len(rows[:limit])} shown)")
        table.add_column("Term", min_width=20)
        table.add_column("Definition", min_width=40)

        for r in rows[:limit]:
            table.add_row(r["term"], (r["definition"] or "-")[:60])
        console.print(table)

    elif entity == "artifacts":
        rows = ArtifactRepository(conn).get_all()

        table = Table(title=f"Artifacts ({len(rows[:limit])} shown)")
        table.add_column("Name", min_width=20)
        table.add_column("Type", width=10)
        table.add_column("Description", min_width=30)

        for r in rows[:limit]:
            table.add_row(r["name"], r["artifact_type"] or "-", (r["description"] or "-")[:50])
        console.print(table)

    elif entity == "locations":
        rows = LocationRepository(conn).get_all()

        table = Table(title=f"Locations ({len(rows[:limit])} shown)")
        table.add_column("Name", min_width=20)
        table.add_column("Era", width=15)
        table.add_column("Description", min_width=30)

        for r in rows[:limit]:
            table.add_row(r["name"], (r["era"] or "-")[:15], (r["description"] or "-")[:50])
        console.print(table)

    conn.close()


@main.command()
@click.option("--manuscript", "-m", required=True, type=click.Path(exists=True),
              help="Manuscript path to check history for")
def history(manuscript):
    """Show validation history for a manuscript."""
    config = Config.from_env()
    conn = get_connection(config)

    from .db import ReportRepository
    from rich.table import Table

    reports = ReportRepository(conn).get_history(str(Path(manuscript).resolve()))

    if not reports:
        # Try with the path as given
        reports = ReportRepository(conn).get_history(manuscript)

    if not reports:
        console.print("[yellow]No validation history found for this manuscript.[/yellow]")
        conn.close()
        return

    table = Table(title="Validation History")
    table.add_column("Date", width=20)
    table.add_column("Score", width=8)
    table.add_column("Checks", width=8)
    table.add_column("Issues", width=8)
    table.add_column("Summary", min_width=30)

    for r in reports:
        table.add_row(
            r["report_date"][:19],
            f"{r['score']:.1f}",
            str(r["total_checks"]),
            str(r["total_checks"] - r["passed_checks"]),
            (r["summary"] or "-")[:50],
        )

    console.print(table)
    conn.close()


if __name__ == "__main__":
    main()
