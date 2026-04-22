"""kdp-fetch CLI."""

from pathlib import Path

import click

from .backfill import import_xlsx_to_kupf
from .client import probe_auth
from .harvester import DEFAULT_AUTH_FILE, harvest
from .kenp import export_all_asins
from .royalties import export_royalties
from .select_status import enrich_with_titles, fetch_enrollments


@click.group()
def main():
    """Headless KDP backend client. No browser at runtime."""


@main.command("harvest")
@click.option("--auth-file", type=click.Path(path_type=Path), default=DEFAULT_AUTH_FILE)
def cmd_harvest(auth_file):
    """Grab Amazon session cookies from the playwright-persist profile."""
    result = harvest(auth_file=auth_file)
    click.echo(f"Harvested {result['cookie_count']} cookies -> {result['auth_file']}")
    click.echo(f"Critical auth cookies: {', '.join(result['critical'])}")


@main.command("probe")
@click.option("--host", default="www.amazon.com")
@click.option("--path", default="/gp/yourstore/home")
def cmd_probe(host, path):
    """Confirm the harvested session still works."""
    result = probe_auth(host=host, path=path)
    click.echo(result)


@main.command("kenp")
@click.option(
    "--out",
    type=click.Path(path_type=Path),
    default=Path.home() / "kdp-reports",
    help="Output directory — one CSV per ASIN.",
)
@click.option(
    "--import",
    "do_import",
    is_flag=True,
    help="Also upsert rows into ku_page_flip's SQLite DB (idempotent).",
)
def cmd_kenp(out, do_import):
    """Export the last 22 days of KENP reads as ku_page_flip-compatible CSVs."""
    result = export_all_asins(out, import_to_kupf=do_import)
    if not result:
        click.echo("No KENP data returned (no titles with reads in the last 22 days).")
        return
    for asin, meta in result.items():
        title = f" ({meta['title']})" if meta.get("title") else ""
        imp = f"  imported={meta['imported']}" if "imported" in meta else ""
        click.echo(f"  {asin}{title}  rows={meta['rows']:4d}  -> {meta['path']}{imp}")


@main.command("royalties")
@click.option(
    "--out",
    type=click.Path(path_type=Path),
    default=Path.home() / "kdp-reports",
    help="Output directory — one CSV per ASIN plus combined royalties_all.csv.",
)
def cmd_royalties(out):
    """Export last 22 days of sales + royalty amounts (USD) as royalty_reconciler-compatible CSVs."""
    result = export_royalties(out)
    if not result:
        click.echo("No royalty data returned.")
        return
    for asin, meta in result.items():
        if asin == "_combined":
            click.echo(f"\n  ALL: rows={meta['rows']}  total=${meta['total_royalty']}  -> {meta['path']}")
            continue
        title = f" ({meta['title']})" if meta.get("title") else ""
        click.echo(
            f"  {asin}{title}  rows={meta['rows']:4d}  units={meta['total_units']:4d}  "
            f"${meta['total_royalty']:7.2f}  -> {meta['path']}"
        )


@main.command("select")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of the table view.")
def cmd_select(as_json):
    """Show KDP Select enrollment status + term dates for every enrolled title."""
    import json as _json
    from datetime import date

    enrollments = enrich_with_titles(fetch_enrollments())
    if as_json:
        click.echo(_json.dumps([
            {
                "title_id": e.title_id,
                "asin": e.asin,
                "title": e.title,
                "status": e.status,
                "term_start": e.term_start.isoformat() if e.term_start else None,
                "term_end": e.term_end.isoformat() if e.term_end else None,
                "term_start_raw": e.term_start_raw,
                "term_end_raw": e.term_end_raw,
                "days_until_end": e.days_until_end(),
            }
            for e in enrollments
        ], indent=2))
        return
    if not enrollments:
        click.echo("No enrolled titles found.")
        return
    today = date.today()
    for e in enrollments:
        title = (e.title or "(unknown)")[:55]
        start = e.term_start.isoformat() if e.term_start else "?"
        end = e.term_end.isoformat() if e.term_end else "?"
        days = e.days_until_end(today)
        days_str = f"{days:>4}d" if days is not None else "  ? "
        asin = e.asin or "?"
        click.echo(
            f"  {asin:10s}  {title:55s}  {e.status or '?':12s}  "
            f"{start} → {end}  ({days_str} until renewal)"
        )


@main.command("backfill")
@click.argument("xlsx_path", type=click.Path(exists=True, path_type=Path))
def cmd_backfill(xlsx_path):
    """Import a KDP KENP Read XLSX export (downloaded manually from KDP Reports UI).

    Use this to seed historical data beyond the 22-day atAGlance window.
    Idempotent — re-running with the same file is safe.
    """
    result = import_xlsx_to_kupf(xlsx_path)
    click.echo(f"Parsed {result['rows']} rows from {xlsx_path}")
    for asin, count in result.get("books", {}).items():
        title = result.get("titles", {}).get(asin, "")
        suffix = f" ({title})" if title else ""
        click.echo(f"  {asin}{suffix}  rows={count}")
