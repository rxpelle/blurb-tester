"""MCP Marketing Tools Server — wraps 6 marketing tool packages."""

import json
from typing import Optional

import anyio
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-marketing-tools")

# ---------------------------------------------------------------------------
# Lazy imports with graceful fallback
# ---------------------------------------------------------------------------

try:
    from ad_copy_gen.generator import Generator as AdGenerator
    from ad_copy_gen.models import BookMeta, AdCampaign
    from ad_copy_gen.benchmarks import get_benchmarks
except ImportError:
    AdGenerator = None
    BookMeta = None
    AdCampaign = None
    get_benchmarks = None

try:
    from blurb_tester.analyzer import analyze_blurb, generate_variants, compare_blurbs
    from blurb_tester.scorer import score_blurb
except ImportError:
    analyze_blurb = None
    generate_variants = None
    compare_blurbs = None
    score_blurb = None

try:
    from booktok_gen.generator import generate_script, generate_batch
except ImportError:
    generate_script = None
    generate_batch = None

try:
    from blog_post_gen.generator import generate as blog_generate
    from blog_post_gen.seo import analyze as seo_analyze
except ImportError:
    blog_generate = None
    seo_analyze = None

try:
    from content_repurposer.repurposer import repurpose, repurpose_single
    from content_repurposer.platforms import get_all_platforms
except ImportError:
    repurpose = None
    repurpose_single = None
    get_all_platforms = None

try:
    from newsletter_swap_finder.db import get_db
    from newsletter_swap_finder.scorer import score_partner
    from newsletter_swap_finder.outreach import generate_all_templates
    from newsletter_swap_finder.models import Partner
except ImportError:
    get_db = None
    score_partner = None
    generate_all_templates = None
    Partner = None


def _serialize(obj: object) -> str:
    """Best-effort JSON serialization of tool return values."""
    if isinstance(obj, str):
        return obj
    try:
        return json.dumps(obj, indent=2, default=str)
    except TypeError:
        return str(obj)


# ===== Ad Copy Gen tools ====================================================

@mcp.tool()
async def marketing_generate_ads(
    title: str,
    author: str,
    genre: str,
    blurb: str,
    series_name: Optional[str] = None,
    asin: Optional[str] = None,
    comp_titles: Optional[str] = None,
) -> str:
    """Generate a full ad campaign with headlines, custom text, and keywords.

    Args:
        title: Book title
        author: Author name
        genre: Book genre
        blurb: Book blurb/description
        series_name: Optional series name
        asin: Optional Amazon ASIN
        comp_titles: Optional comma-separated comp titles
    """
    if AdGenerator is None:
        return "Error: ad_copy_gen package is not installed."
    meta = BookMeta(
        title=title,
        author=author,
        genre=genre,
        blurb=blurb,
        series_name=series_name or "",
        asin=asin or "",
        comp_titles=[t.strip() for t in comp_titles.split(",")] if comp_titles else [],
    )
    gen = AdGenerator(meta)
    result = await anyio.to_thread.run_sync(gen.generate_campaign)
    return _serialize(result)


@mcp.tool()
async def marketing_generate_headlines(
    title: str,
    author: str,
    genre: str,
    blurb: str,
    count: int = 10,
) -> str:
    """Generate ad headlines only.

    Args:
        title: Book title
        author: Author name
        genre: Book genre
        blurb: Book blurb/description
        count: Number of headlines to generate
    """
    if AdGenerator is None:
        return "Error: ad_copy_gen package is not installed."
    meta = BookMeta(
        title=title,
        author=author,
        genre=genre,
        blurb=blurb,
    )
    gen = AdGenerator(meta)
    result = await anyio.to_thread.run_sync(lambda: gen.generate_headlines(count=count))
    return _serialize(result)


@mcp.tool()
async def marketing_generate_keywords(
    title: str,
    author: str,
    genre: str,
    blurb: str,
    comp_titles: Optional[str] = None,
) -> str:
    """Generate keywords grouped by match type (broad, phrase, exact).

    Args:
        title: Book title
        author: Author name
        genre: Book genre
        blurb: Book blurb/description
        comp_titles: Optional comma-separated comp titles
    """
    if AdGenerator is None:
        return "Error: ad_copy_gen package is not installed."
    meta = BookMeta(
        title=title,
        author=author,
        genre=genre,
        blurb=blurb,
        comp_titles=[t.strip() for t in comp_titles.split(",")] if comp_titles else [],
    )
    gen = AdGenerator(meta)
    result = await anyio.to_thread.run_sync(gen.generate_keywords)
    return _serialize(result)


@mcp.tool()
async def marketing_ad_benchmarks() -> str:
    """Show industry benchmarks for book advertising (CTR, CPC, ACOS data)."""
    if get_benchmarks is None:
        return "Error: ad_copy_gen package is not installed."
    result = await anyio.to_thread.run_sync(get_benchmarks)
    return _serialize(result)


# ===== Blurb Tester tools ===================================================

@mcp.tool()
async def marketing_analyze_blurb(
    blurb: str,
    genre: str,
) -> str:
    """Analyze blurb quality with scores and feedback.

    Args:
        blurb: The book blurb to analyze
        genre: Book genre for genre-specific analysis
    """
    if analyze_blurb is None:
        return "Error: blurb_tester package is not installed."
    result = await anyio.to_thread.run_sync(lambda: analyze_blurb(blurb, genre=genre))
    return _serialize(result)


@mcp.tool()
async def marketing_generate_blurbs(
    blurb: str,
    genre: str,
    count: int = 3,
    guidance: Optional[str] = None,
) -> str:
    """Generate improved blurb variants.

    Args:
        blurb: The original blurb to improve
        genre: Book genre
        count: Number of variants to generate
        guidance: Optional guidance for variant generation
    """
    if generate_variants is None:
        return "Error: blurb_tester package is not installed."
    kwargs = {"blurb": blurb, "genre": genre, "count": count}
    if guidance:
        kwargs["guidance"] = guidance
    result = await anyio.to_thread.run_sync(lambda: generate_variants(**kwargs))
    return _serialize(result)


@mcp.tool()
async def marketing_compare_blurbs(
    blurbs: str,
    genre: str,
) -> str:
    """Compare multiple blurbs head-to-head.

    Args:
        blurbs: JSON array of blurb strings to compare, e.g. '["blurb1", "blurb2"]'
        genre: Book genre
    """
    if compare_blurbs is None:
        return "Error: blurb_tester package is not installed."
    blurb_list = json.loads(blurbs)
    result = await anyio.to_thread.run_sync(lambda: compare_blurbs(blurb_list, genre=genre))
    return _serialize(result)


# ===== BookTok Gen tools ====================================================

@mcp.tool()
async def marketing_booktok_script(
    input_text: str,
    input_type: str = "scene",
    genre: Optional[str] = None,
    book_title: Optional[str] = None,
    duration: int = 30,
    style: Optional[str] = None,
) -> str:
    """Generate a BookTok/Reels video script.

    Args:
        input_text: The source text (scene, fact, or hook)
        input_type: Type of input — 'scene', 'fact', or 'hook'
        genre: Optional book genre
        book_title: Optional book title
        duration: Target duration in seconds
        style: Optional style hint
    """
    if generate_script is None:
        return "Error: booktok_gen package is not installed."
    kwargs = {
        "input_text": input_text,
        "input_type": input_type,
        "duration": duration,
    }
    if genre:
        kwargs["genre"] = genre
    if book_title:
        kwargs["book_title"] = book_title
    if style:
        kwargs["style"] = style
    result = await anyio.to_thread.run_sync(lambda: generate_script(**kwargs))
    return _serialize(result)


# ===== Blog Post Gen tools ==================================================

@mcp.tool()
async def marketing_generate_blog_post(
    topic: Optional[str] = None,
    keywords: Optional[str] = None,
    audience: Optional[str] = None,
    brief_path: Optional[str] = None,
) -> str:
    """Generate a blog post from a brief or topic/keywords/audience.

    Args:
        topic: Blog post topic (used if brief_path not provided)
        keywords: Comma-separated keywords for SEO
        audience: Target audience description
        brief_path: Path to a brief file (overrides topic/keywords/audience)
    """
    if blog_generate is None:
        return "Error: blog_post_gen package is not installed."
    kwargs = {}
    if brief_path:
        kwargs["brief_path"] = brief_path
    else:
        if topic:
            kwargs["topic"] = topic
        if keywords:
            kwargs["keywords"] = [k.strip() for k in keywords.split(",")]
        if audience:
            kwargs["audience"] = audience
    result = await anyio.to_thread.run_sync(lambda: blog_generate(**kwargs))
    return _serialize(result)


@mcp.tool()
async def marketing_seo_analyze(
    post_path: str,
) -> str:
    """Analyze a blog post for SEO quality.

    Args:
        post_path: Path to the blog post markdown file
    """
    if seo_analyze is None:
        return "Error: blog_post_gen package is not installed."
    result = await anyio.to_thread.run_sync(lambda: seo_analyze(post_path))
    return _serialize(result)


# ===== Content Repurposer tools =============================================

@mcp.tool()
async def marketing_repurpose_content(
    content: str,
    platforms: str = "twitter,linkedin,facebook",
    tone: Optional[str] = None,
) -> str:
    """Repurpose content for multiple social platforms.

    Args:
        content: The source content to repurpose
        platforms: Comma-separated list of target platforms
        tone: Optional tone override (e.g. casual, professional)
    """
    if repurpose is None:
        return "Error: content_repurposer package is not installed."
    platform_list = [p.strip() for p in platforms.split(",")]
    kwargs = {"content": content, "platforms": platform_list}
    if tone:
        kwargs["tone"] = tone
    result = await anyio.to_thread.run_sync(lambda: repurpose(**kwargs))
    return _serialize(result)


@mcp.tool()
async def marketing_list_platforms() -> str:
    """List all supported content repurposing platforms."""
    if get_all_platforms is None:
        return "Error: content_repurposer package is not installed."
    result = await anyio.to_thread.run_sync(get_all_platforms)
    return _serialize(result)


# ===== Newsletter Swap Finder tools =========================================

@mcp.tool()
async def marketing_add_swap_partner(
    name: str,
    email: str,
    website: str,
    genre: str,
    list_size: int,
) -> str:
    """Add a newsletter swap partner to the database.

    Args:
        name: Partner name or newsletter name
        email: Contact email
        website: Partner website URL
        genre: Genre they write in
        list_size: Their email list size
    """
    if Partner is None or get_db is None:
        return "Error: newsletter_swap_finder package is not installed."
    partner = Partner(
        name=name,
        email=email,
        website=website,
        genre=genre,
        list_size=list_size,
    )
    db = get_db()

    def _add():
        db.add_partner(partner)
        return partner

    result = await anyio.to_thread.run_sync(_add)
    return _serialize(result)


@mcp.tool()
async def marketing_find_swap_partners(
    genre: Optional[str] = None,
    min_list_size: Optional[int] = None,
    status: Optional[str] = None,
) -> str:
    """Search for newsletter swap partners.

    Args:
        genre: Filter by genre
        min_list_size: Minimum email list size
        status: Filter by status (e.g. 'active', 'contacted', 'completed')
    """
    if get_db is None:
        return "Error: newsletter_swap_finder package is not installed."
    db = get_db()
    kwargs = {}
    if genre:
        kwargs["genre"] = genre
    if min_list_size is not None:
        kwargs["min_list_size"] = min_list_size
    if status:
        kwargs["status"] = status
    result = await anyio.to_thread.run_sync(lambda: db.find_partners(**kwargs))
    return _serialize(result)


@mcp.tool()
async def marketing_generate_outreach(
    partner_name: str,
    your_series: str,
    your_list_size: int,
) -> str:
    """Generate outreach email templates for a swap partner.

    Args:
        partner_name: Name of the partner to reach out to
        your_series: Your book series name
        your_list_size: Your email list size
    """
    if generate_all_templates is None:
        return "Error: newsletter_swap_finder package is not installed."
    result = await anyio.to_thread.run_sync(
        lambda: generate_all_templates(
            partner_name=partner_name,
            your_series=your_series,
            your_list_size=your_list_size,
        )
    )
    return _serialize(result)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
