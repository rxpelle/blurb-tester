# AI-Powered Book Production Pipeline

*Updated 2026-03-24 — 26 of 37 tools built. Reorganized as a full lifecycle pipeline. Each tool is a CLI that AI agents can orchestrate end-to-end: from market research through published, marketed book. Tools marked ✅ are built. Remaining: 11 tools across analytics, publishing automation, and discovery.*

---

## Stage 1: Market Research & Opportunity Discovery

*What should I write? What's selling? Where are the gaps?*

### 1. Indie Bestseller Scout ✅
Import Amazon bestseller lists (via paste or snapshot) → scores authors by indie potential (catalog size, BSR, review velocity, recency, KU signal, publisher detection). Identifies successful indie authors with small catalogs who are winning in your genre. Surfaces the patterns: pricing, page counts, KU enrollment, category placement.

**Agent use**: Feeds market gaps and genre conventions into the Concept Generator.

**Blog post**: "I Reverse-Engineered the Top 100 in My Genre — Here's Who's Actually Winning"

### 2. Review Miner ✅
Import reviews from any book → AI sentiment analysis + keyword extraction. Shows what readers love/hate about competitor books, common praise phrases (for ad copy), and unmet reader desires (gaps you can write into). Export as ad copy seeds.

**Agent use**: Reader gaps feed directly into the Concept Generator. Praise phrases feed into the Ad Copy Generator and Blurb Tester.

**Blog post**: "What 10,000 Reviews Reveal About What Readers Actually Want"

**Enhancement notes (from Costco Scanner weekly agent pattern):**
- Add a **scheduled review monitoring mode**: weekly agent checks for new reviews on tracked ASINs (your books + competitors), runs sentiment analysis on new reviews only, emails a digest
- Alert on: negative reviews (respond quickly), reviews mentioning specific issues (continuity errors, formatting problems — fix in next upload), reviews praising specific elements (feed into ad copy)
- Track review velocity over time: `{asin, date, total_reviews, avg_rating, new_this_week}` — detect when a competitor gets a review surge (possible promo) or when your book's review velocity stalls

### 3. Category Spy ✅
Monitors BSR thresholds for any Amazon category over time. Alerts when a category gets easier to rank in (BSR #1 drops), tracks seasonal patterns ("cozy mystery spikes in October"), and identifies underserved subcategories where a book at BSR 50K would hit the top 20.

**Agent use**: Identifies optimal category placement and launch timing. Feeds into Launch Orchestrator.

**Blog post**: "I Tracked Every Amazon Book Category for 90 Days — Here's What I Found"

### 4. Comp Title Decay Tracker ✅
Monitors your listed comps' BSR over time. Alerts when they're losing relevance. Suggests replacement comps by finding currently-hot books with similar reader overlap. Tracks when new breakout titles in your genre emerge.

**Agent use**: Keeps ad targeting and book description comps fresh. Feeds into Blurb Tester and Ad Copy Generator.

**Blog post**: "Your Comp Titles Are Expired — Here's How I Track When to Replace Them"

### 5. Also-Bought Mapper
Input a seed ASIN → crawls "Customers also bought" chains 3 levels deep → builds a visual network graph of related books. Reveals hidden comp titles, category placement opportunities, and audience crossover patterns.

**Agent use**: Discovers comp titles for ad targeting and category selection.

**Blog post**: "I Mapped the Hidden Network of Books Amazon Thinks Are Like Mine"

---

## Stage 2: Concept & Framework

*Turn market intelligence into a book plan.*

### 6. Concept Generator ✅
Takes market research outputs (genre trends, reader gaps, comp analysis, pricing data) → generates book concepts with: premise, target reader profile, comp titles, estimated market size, category placement strategy, and differentiation angle. Scores concepts against market data. Outputs a structured concept brief.

**Agent use**: Concept brief feeds into Series Framework Generator and Chapter Outliner.

**Blog post**: "I Let AI Analyze 1,000 Bestsellers and Design My Next Book"

### 7. Series Framework Generator ✅
Input a concept brief or series premise → generates full series architecture: overarching arc, per-book story arcs, character profiles (with relationship maps), world rules, thematic through-lines, planned reveals, and timeline. Outputs a structured YAML/markdown framework that all downstream tools consume.

**Agent use**: The canonical reference document. Feeds into Chapter Outliner, Series Bible Generator, and Continuity Checker.

**Blog post**: "I Built an AI That Architects Entire Book Series"

### 8. Series Bible Generator 🔗
Feed it completed manuscripts (markdown/docx) → AI extracts every character (with physical descriptions, relationships, first appearances), location, timeline event, invented terminology, and plot thread into a structured, searchable series bible. Diffs against previous versions to catch continuity errors. Can also initialize from a Series Framework.

**Agent use**: Living reference document consumed by Chapter Drafter and Continuity Checker.

**Blog post**: "I Fed My Novel to an AI and It Built My Series Bible"

---

## Stage 3: Writing

*Generate the manuscript.*

### 9. Chapter Outliner ✅
Takes a series framework + book-level story arc → generates detailed chapter-by-chapter outlines with: scene beats, POV assignments, tension curves, information reveals, emotional arcs, and word count targets. Validates against series bible for continuity. Outputs structured outline that the Chapter Drafter consumes.

**Agent use**: Creates the roadmap the Chapter Drafter follows. Each chapter outline becomes a self-contained writing prompt.

**Blog post**: "How AI Outlines a Novel — Scene by Scene, Beat by Beat"

### 10. Chapter Drafter ✅
Takes a chapter outline + series bible + voice profile (extracted from author's existing work) → generates a full chapter draft maintaining consistent voice, style, and continuity. Supports iterative refinement: "make the dialogue sharper," "add more sensory detail," "increase tension in the midpoint." Tracks word count against targets.

**Agent use**: Produces raw manuscript chapters. Feeds into Editorial Agent.

**Blog post**: "I Taught AI to Write in My Voice — Here's How Close It Got"

### 11. Continuity Checker ✅
Validates any manuscript chapter against the series bible. Catches: character description contradictions, timeline impossibilities, location errors, terminology inconsistencies, dead characters reappearing, relationship continuity breaks. Outputs a flagged report with specific line references and suggested fixes.

**Agent use**: Runs automatically after every Chapter Drafter output and every Editorial Agent pass.

**Blog post**: "The AI That Catches Plot Holes Before Your Readers Do"

### 12. Editorial Agent ✅
Multi-pass AI editor that runs sequential editorial passes on a manuscript: (1) structural/pacing, (2) character consistency, (3) dialogue naturalization, (4) line-level prose polish, (5) cold read for reader experience. Each pass produces tracked changes with rationale. Author approves/rejects per-change.

**Agent use**: Transforms raw Chapter Drafter output into publication-ready prose.

**Blog post**: "I Ran My Novel Through 5 AI Editing Passes — Here's What Changed"

---

## Stage 4: Production

*Turn manuscript into publishable formats.*

### 13. Manuscript Compiler ✅
Takes a directory of individual chapter markdown files + a book.yaml config → discovers, validates, and assembles them into a complete manuscript. Generates front matter (title page, copyright, about author, table of contents), normalizes chapter headers with anchor links, cleans editorial metadata, standardizes scene breaks, strips end-of-chapter markers, and appends back matter (next-book teaser, author links). Outputs both DOCX-ready and PDF-ready markdown source files. Includes validation (duplicate chapters, gaps, empty files) and word count reporting per chapter.

**Agent use**: Takes Editorial Agent output (polished individual chapter files) and produces the unified manuscript that Book Formatter consumes. The bridge between writing and formatting.

**Blog post**: "I Built a Tool That Assembles My Novel from Chapter Files in One Command"

### 14. Book Formatter ✅
Feed it a markdown or docx manuscript → generates KDP-ready EPUB, paperback interior PDF (with proper trim, bleed, gutter margins), and large-print PDF. Handles front matter, chapter breaks, scene breaks, and consistent formatting. One command, all formats.

**Agent use**: Takes Editorial Agent output and produces all format files needed for publishing.

**Blog post**: "One Command to Format Your Book for Every Platform"

### 15. Cover Generator ✅
Input genre + title + subtitle + author name + optional mood/concept keywords → AI generates cover concepts using genre conventions learned from Cover Comp Analyzer data. Produces multiple variants. Scores each against genre norms (thumbnail readability, color palette, font weight). Outputs print-ready cover files (front, spine, back, full wrap) with correct dimensions for KDP.

**Agent use**: Produces cover files for the Publisher. Can iterate based on Cover Comp Analyzer feedback.

**Blog post**: "I Let AI Design My Book Cover — Then Scored It Against the Bestsellers"

### 16. Cover Comp Analyzer ✅
Upload your book cover + genre → analyzes top 20 BSR covers in that category → uses vision AI to score thumbnail readability, color palette, font weight, layout patterns. Flags issues ("title too small at thumbnail size", "color palette doesn't match thriller conventions").

**Agent use**: Quality gate for Cover Generator output. Reject/iterate until score passes threshold.

**Blog post**: "I Built an AI That Grades Your Book Cover Against the Bestsellers"

### 17. Blurb A/B Tester & Scorer ✅
Paste your book description → AI analyzes against proven copywriting frameworks (hook/stakes/CTA), scores readability, and compares structure to top-selling blurbs in your category. Generates 3 variant blurbs for A/B testing.

**Agent use**: Generates the book description for the Publisher. Takes reader praise phrases from Review Miner for social proof language.

**Blog post**: "I Analyzed 500 Bestselling Blurbs — Here's the Formula"

---

## Stage 5: Publishing

*Get the book live on all platforms.*

### 18. KDP Publisher (NEW) 🔗
Automates KDP book setup: takes manuscript files (EPUB, PDF), cover files, metadata (title, description, keywords, categories, pricing), and creates/updates the KDP listing. Handles both ebook and paperback. Validates all files against KDP requirements before submission. Manages series linking, A+ Content upload, and author page updates.

**Agent use**: Takes all outputs from Stage 4 (formatted files, cover, blurb, keywords from KDP Scout) and publishes with one command.

**Blog post**: "I Automated My Entire KDP Publishing Process"

### 19. ARC Manager ✅
CLI + simple web interface for Advance Reader Copy distribution. Upload EPUB → generates unique watermarked copies → sends personalized emails with download links → tracks who downloaded, who reviewed, who ghosted. Auto-sends gentle reminder emails. Maintains reviewer reputation scores.

**Agent use**: Distributes ARCs before launch. Feeds review status into Launch Orchestrator.

**Blog post**: "How I Automated My ARC Process and Got 40 Reviews on Launch Day"

---

## Stage 6: Launch & Marketing

*Maximize visibility and sales.*

### 20. Launch Orchestrator ✅
Coordinates all launch activities on a timeline: ARC distribution (T-30 days), email sequence scheduling, social media posts, blog post publication, Amazon Ads campaign creation, price promotions, category monitoring. Pulls status from all other tools into a single dashboard. Alerts when action items are due.

**Agent use**: The master controller for launch week. Triggers Ad Copy Generator, email sequences, blog deployment, and price changes on schedule.

**Blog post**: "I Built an AI Launch Manager That Runs My Book Release"

### 21. Ad Copy Generator ✅
Feed it your book + top-performing keywords → generates Amazon Sponsored Brand headlines, product display ad copy, and A+ Content text. Uses praise phrases from Review Miner and reader language patterns. Outputs ready-to-paste campaign copy.

**Agent use**: Creates all ad creative for Launch Orchestrator to deploy.

**Blog post**: "I Built a Tool That Writes My Amazon Ads For Me"

### 22. Blog Post Generator ✅
Takes book themes, research notes, and author expertise → generates "Science Behind the Fiction" style blog posts, reading list articles, and topic explainers that target reader search queries (not author queries). SEO-optimized with proper front matter for the author's site. Includes book CTA sections.

**Agent use**: Creates marketing content that drives organic traffic to the author's website and books.

**Blog post**: "I Automated My Entire Content Marketing Strategy"

### 23. Newsletter Swap Finder
Builds a database of authors in your genre who do newsletter swaps. Scores potential swap partners by: list size, genre overlap, recent activity, and reciprocity reputation. Generates personalized outreach templates.

**Agent use**: Identifies and drafts outreach for cross-promotion opportunities.

**Blog post**: "I Built a Tool That Finds Newsletter Swap Partners So I Don't Have To"

---

## Stage 7: Analytics & Optimization

*Track performance, iterate, improve.*

### 24. Launch Day Dashboard ✅
Real-time CLI dashboard combining KDP sales rank, KENP reads, Amazon Ads spend, and social mentions into one terminal view. Auto-refreshes during launch week.

**Agent use**: Feeds real-time data to Launch Orchestrator for dynamic decisions (increase ad spend, trigger price change, etc.).

**Blog post**: "I Built a Real-Time Book Launch Command Center in My Terminal"

**Implementation notes (from Costco Receipt Scanner article pattern):**
- Use the **scan-compare-notify** architecture: scheduled scraper → AI cross-reference → formatted HTML email report
- Weekly agent runs on a schedule (Apps Script trigger or cron), scrapes KDP dashboard / Amazon product page, compares against historical data stored in a local SQLite or JSON file
- AI analyzes changes: BSR movement, new reviews, KENP velocity trends, ad spend vs. revenue ratio
- Sends formatted HTML email report via existing `personal_assistant/scripts/email-service.js` with two sections: (1) alerts requiring action (BSR spike, negative review, ad overspend), (2) steady-state metrics summary
- Include presigned links or direct URLs to the relevant Amazon/KDP pages for quick verification
- **Two-tier processing**: lightweight scrape for daily checks (just BSR + review count), full AI analysis for weekly deep reports
- **Deduplication**: track review IDs to avoid re-alerting on the same review; track BSR by timestamp to build trend data
- Cost: near-zero using existing PA infrastructure + Claude Haiku for analysis

### 25. Series Read-Through Calculator 🔗
Tracks how many readers who bought/read Book 1 go on to Book 2, Book 3, etc. Calculates true lifetime reader value and optimal Book 1 pricing/promo strategy.

**Agent use**: Informs Price Optimizer and determines when to run Book 1 promotions.

**Blog post**: "The Real Math Behind Series Read-Through (And Why Book 1 Pricing Matters)"

### 26. Price Optimizer 🔗
Tracks BSR + revenue at different price points over time. Runs price experiments and calculates optimal price per format. Factors in KU page rate, royalty tiers (35% vs 70%), and competitor pricing.

**Agent use**: Automatically adjusts pricing based on performance data from Launch Day Dashboard and Series Read-Through Calculator.

**Blog post**: "I Ran 12 Price Experiments on My Book — Here's the Optimal Price"

**Implementation notes (from Costco Price Match pattern):**
- Mirrors the Costco "price adjustment window" concept: track your book's price vs. competitor prices, detect when competitors drop price (your relative value proposition changes)
- Scheduled weekly scrape of competitor ASINs (from Comp Title Decay Tracker data) → compare pricing/BSR against your pricing/BSR → AI identifies pricing opportunities
- Alert types: "Competitor X dropped to $2.99 and jumped 50K BSR spots — consider matching", "Your BSR improved 20% after last price change — hold current price", "KU page rate changed this month — recalculate per-page vs. purchase revenue"
- Store price history in JSON/SQLite: `{asin, date, price, bsr, kenp_rate}` for both your books and tracked competitors

### 27. Royalty Reconciler
Ingests KDP, Apple Books, Kobo, Google Play, D2D, and ACX royalty CSVs into one SQLite database. Normalizes currencies, tracks payment delays, calculates true monthly P&L. Generates Schedule C-ready tax reports.

**Agent use**: Provides the ground truth for all ROI calculations across the pipeline.

**Blog post**: "I Built a Tool That Tells Me If My Books Are Actually Profitable"

**Implementation notes (from Costco Receipt Scanner article pattern):**
- Same receipt-parsing architecture applies: upload royalty CSVs/PDFs → AI parses line items → stores in structured format → cross-references across platforms
- Use traditional OCR/text extraction for PDFs first (NOT LLM vision — numbers get misread per "Don't Use LLMs as OCR" article). Use `pdf-parse` or AWS Textract for extraction, then Claude for reasoning/categorization
- Store in SQLite with schema: `platform, date, title, format, units, royalty_amount, currency, exchange_rate, net_usd`
- Weekly email report via PA email service: formatted P&L table per book, per platform, month-over-month trends
- **Deduplication**: hash each CSV row to prevent double-counting when re-importing overlapping date ranges
- **Tax output**: Generate Schedule C categories (gross receipts, platform fees, ad spend, production costs) with line references to source data

### 28. Backmatter Link Tracker
Generates unique tracking links for every backmatter CTA (newsletter signup, next book, review request). Tracks click-through rates per book, per format. Shows which CTAs convert.

**Agent use**: Data feeds into Reader Magnet Funnel Analyzer.

**Blog post**: "I Tracked Every Link in My Backmatter — Here's What Readers Actually Click"

### 29. Reader Magnet Funnel Analyzer 🔗
Tracks the full funnel: free book downloads → email signups → email opens → clicks to Book 1 → purchases → series read-through. A/B tests different reader magnets. Identifies where readers drop off.

**Agent use**: Optimizes the top of the reader acquisition funnel.

**Blog post**: "I Tracked 1,000 Free Book Downloads to See How Many Became Paying Readers"

### 30. Wide vs. KU Simulator
Input current KDP sales + KENP data → simulates revenue if you went wide. Adjusted for genre. Factors in platform market share, promotional opportunities, and library income. Runs Monte Carlo simulations with confidence intervals.

**Agent use**: Informs the exclusive-vs-wide strategic decision.

**Blog post**: "I Simulated Going Wide vs. Staying in KU — Here's What the Math Says"

---

## Stage 8: Protection & Maintenance

### 31. KU Page-Flip Detector
Monitors KENP reads for anomalous patterns: sudden spikes followed by clawbacks, reads matching exact page count (bot signature), reads from unexpected countries. Flags suspicious activity with evidence for KDP support.

**Blog post**: "I Built a Tool to Detect If Bots Are Reading My Books"

### 32. Audiobook Cost Calculator & ROI Tracker
Input word count, genre, and sales data → estimates ACX production costs, projects audiobook revenue, calculates break-even under different deal structures (royalty share vs. per-hour vs. AI narration).

**Blog post**: "The Math Behind Whether Your Book Should Be an Audiobook"

---

## Stage 9: Content Amplification & Platform Growth

*Multiply the value of every piece of content. Turn one blog post into a week of social media.*

### 33. Content Repurposer ✅
Takes a blog post, Medium article, or book excerpt → generates platform-specific content: TikTok/Reels scripts with hooks, tweet threads, newsletter excerpts, LinkedIn posts, and video scripts. Adapts tone, length, and format per platform automatically. Tracks which repurposed formats drive the most traffic back to books.

**Agent use**: Takes Blog Post Generator output and multiplies it across all platforms. Feeds performance data back to optimize future content.

**Blog post**: "I Wrote One Article and Got a Week of Content — Here's the Tool"

### 34. MCP Book Data Server ✅
A Model Context Protocol server that provides a unified interface to all book data: KDP royalties, Amazon BSR/reviews, Goodreads ratings, ad performance, email subscriber counts, and website analytics. Claude can query "how are my books performing?" and get answers from all platforms through one standardized connection. Exposes tools for: querying sales by date range, comparing books, tracking trends, and triggering alerts.

**Agent use**: The central nervous system — every other tool can query book data through MCP instead of custom integrations. Launch Day Dashboard, Price Optimizer, and Series Read-Through Calculator all consume data from this single source.

**Blog post**: "I Built One AI Interface to All My Book Data"

### 35. GEO Optimizer (NEW)
Optimizes content for AI search engines (Generative Engine Optimization), not just traditional Google SEO. Analyzes blog posts and book landing pages for: structured data markup, clear direct-answer formatting, authoritative sourcing, citation-friendly paragraphs, and entity markup. Scores content on "AI discoverability" — how likely AI assistants are to surface it when readers ask about your topics.

**Agent use**: Post-processes Blog Post Generator output. Audits author website pages. Ensures book-related content appears in AI-generated recommendations.

**Blog post**: "SEO Is Dead. GEO Is How Readers Find Books in 2026."

### 36. BookTok Script Generator ✅
Takes book scenes, historical facts, or "did you know" hooks → generates short-form video scripts (15-60 seconds) optimized for TikTok/Reels. Includes: opening hook (first 3 seconds), atmospheric scene descriptions for visual overlay, text-on-screen prompts, trending audio suggestions, and hashtag sets. Targets emotional authenticity over polish — the style BookTok rewards.

**Agent use**: Takes high-performing excerpts (identified by Review Miner praise phrases) and historical research (from Blog Post Generator) and turns them into video scripts.

**Blog post**: "I Let AI Write My BookTok Scripts — Here's What Went Viral"

### 37. Author Tools SaaS (NEW — Future)
Packages existing tools (Review Miner, Category Spy, Comp Title Decay Tracker, Cover Comp Analyzer, Blurb Tester) as a paid web service for other indie authors. Subscription model with tiered access. Hosted on Cloudflare Workers + managed database. Stripe billing. Each tool exposed via web UI and API.

**Agent use**: Revenue diversification beyond book sales. Validated by the fact that these tools already work for my own publishing.

**Blog post**: "I Built My Author Toolkit — Then Other Authors Asked to Use It"

---

## Already Built

| Tool | Location | Status |
|---|---|---|
| **Indie Bestseller Scout** | `indie-scout/` | ✅ 130 tests, live-tested on thriller bestsellers |
| **Review Miner** | `review-miner/` | ✅ 116 tests, tested on Genesis Protocol reviews |
| **Manuscript Compiler** | `manuscript-compiler/` | ✅ 113 tests, chapter files → unified manuscript with front/back matter |
| **Book Formatter** | `book-formatter/` | ✅ Markdown/docx → EPUB + PDF |
| **KDP Scout** | `kdp-scout/` | ✅ Keyword research |
| **Etsy Scout** | `etsy-scout/` | ✅ Market research |
| **Cover Generator** | `cover-generator/` | ✅ 68 tests, Claude + DALL-E + Pillow |
| **Cover Comp Analyzer** | `cover-comp-analyzer/` | ✅ 128 tests, Claude Vision scoring |
| **Blurb A/B Tester** | `blurb-tester/` | ✅ 53 tests, AI scoring + variant generation |
| **Ad Copy Generator** | `ad-copy-gen/` | ✅ 99 tests, headlines + custom text + A+ + keywords |
| **Launch Orchestrator** | `launch-orchestrator/` | ✅ 74 tests, 8-phase timeline + dashboard + alerts |
| **Category Spy** | `category-spy/` | ✅ 58 tests, BSR tracking + trend analysis + seasonal patterns |
| **Blog Post Generator** | `blog-post-gen/` | ✅ 55 tests, SEO-optimized posts from book themes + research |
| **ARC Manager** | `arc-manager/` | ✅ 69 tests, reviewer tracking + watermarks + email templates |
| **Comp Title Decay Tracker** | `comp-tracker/` | ✅ 86 tests, BSR tracking + alerts + relevance scoring |
| **Grounds Reader** | `grounds-reader/` | ✅ Interactive fiction reader |
| **Concept Generator** | `concept-gen/` | ✅ Market research → scored book concepts |
| **Series Framework Generator** | `series-framework/` | ✅ Concept → full series architecture |
| **Chapter Outliner** | `chapter-outliner/` | ✅ Framework → chapter-by-chapter outlines |
| **Chapter Drafter** | `chapter-drafter/` | ✅ Outline + bible + voice → chapter drafts |
| **Continuity Checker** | `continuity-checker/` | ✅ Validates chapters against series bible |
| **Editorial Agent** | `editorial-agent/` | ✅ Multi-pass AI editor |
| **Content Repurposer** | `content-repurposer/` | ✅ Blog → TikTok/tweets/newsletter/video scripts |
| **BookTok Script Generator** | `booktok-gen/` | ✅ Book scenes → short-form video scripts |
| **Launch Day Dashboard** | `launch-dashboard/` | ✅ Real-time KDP + Amazon + Ads monitoring |
| **MCP Book Data Server** | `mcp-book-data/` | ✅ Unified MCP interface to all book data |

---

## The Agent Pipeline

When fully built, an AI agent can orchestrate the entire lifecycle:

```
market_research    →  concept          →  framework        →  outline
(1-5)                 (6)                 (7-8)               (9)
                                                                ↓
launch & marketing ←  publish          ←  production       ←  writing
(20-23)               (18-19)             (13-17)             (10-12)
        ↓                                                       ↓
content amplification    analytics & optimization (24-30)
(33-36)                              ↓
        ↓                     next book concept (loop)
   SaaS (37)  ←  proven tools from all stages
```

**MCP Book Data Server (#34)** sits beneath all stages — the unified data layer every tool queries.

Each stage's output is the next stage's input. Human review gates at: concept approval, outline approval, final manuscript approval, cover approval, and launch go/no-go.

---

## Build Roadmap

*Vision: A multi-agent system where I feed it an idea and it produces a published, marketed book — with human review gates at key decisions. Each phase below builds toward that, while delivering standalone value immediately.*

### What's Already Built (26 tools)

| Stage | Tools | Gap |
|---|---|---|
| Market Research | Indie Scout, Review Miner, Category Spy, Comp Tracker, KDP Scout | Missing: Also-Bought Mapper (#5) |
| Concept & Framework | Concept Generator, Series Framework Generator | Complete |
| Writing | Chapter Outliner, Chapter Drafter, Continuity Checker, Editorial Agent | Missing: Series Bible Generator (#8) |
| Production | Manuscript Compiler, Book Formatter, Cover Generator, Cover Comp Analyzer, Blurb Tester | Complete |
| Launch & Marketing | Launch Orchestrator, Ad Copy Generator, Blog Post Generator, ARC Manager, Content Repurposer, BookTok Script Generator | Missing: Newsletter Swap Finder (#23) |
| Analytics | Launch Day Dashboard, MCP Book Data Server | Missing: Price Optimizer (#26), Series Read-Through (#25), Royalty Reconciler (#27) |
| Other | Grounds Reader, Etsy Scout | — |

**Remaining gaps**: Analytics/optimization tools (Price Optimizer, Read-Through Calculator, Royalty Reconciler, GEO Optimizer), Publishing automation (KDP Publisher), Series Bible Generator, and network/discovery tools (Also-Bought Mapper, Newsletter Swap Finder).

---

### Phase 1: Book 3 Launch (NOW — April 2026) ✅ COMPLETE
*All 4 tools built. Ready for Book 3 launch.*

| Priority | Build | Status |
|---|---|---|
| 1a | **MCP Book Data Server (#34)** | ✅ Built — `mcp-book-data/` |
| 1b | **Launch Day Dashboard (#24)** | ✅ Built — `launch-dashboard/` |
| 1c | **Content Repurposer (#33)** | ✅ Built — `content-repurposer/` |
| 1d | **BookTok Script Generator (#36)** | ✅ Built — `booktok-gen/` |

**Phase 1 outcome**: All launch tools ready. Focus now shifts to Phase 2 analytics and Phase 3 writing engine.

---

### Phase 2: The Intelligence Layer (May-June 2026)
*Goal: Automated monitoring that runs 24/7 after launch. Your books work for you while you sleep.*

| Priority | Build | Why | Effort |
|---|---|---|---|
| 2a | **Review Miner — monitoring mode** (enhance #2) | Weekly agent scrapes new reviews across all books, runs sentiment analysis, emails digest. Catches problems early, feeds praise into ad copy. | 1-2 days |
| 2b | **Price Optimizer (#26)** | With 3 books live, pricing decisions matter. Tracks BSR at different price points, monitors competitor pricing, recommends changes. | 2-3 days |
| 2c | **Series Read-Through Calculator (#25)** | 3-book series = read-through data. Calculates true reader lifetime value. Tells you whether Book 1 promos are worth it. | 1-2 days |
| 2d | **GEO Optimizer (#35)** | AI search is replacing Google for book discovery. Optimize your website and blog posts now, compound over time. | 1-2 days |
| 2e | **Royalty Reconciler (#27)** | With royalties coming from KDP (ebook + paperback + KU), you need one source of truth. Automated P&L, tax-ready reports. | 2-3 days |

**Phase 2 outcome**: Hands-off intelligence. Agents monitor reviews, track pricing, calculate read-through, optimize for AI search, and reconcile royalties. You get weekly email digests with action items.

---

### Phase 3: The Writing Engine (July-September 2026) — MOSTLY COMPLETE
*6 of 7 tools built. Only Series Bible Generator remains.*

| Priority | Build | Status |
|---|---|---|
| 3a | **Series Bible Generator (#8)** | ❌ NOT BUILT — the one remaining gap |
| 3b | **Continuity Checker (#11)** | ✅ Built — `continuity-checker/` |
| 3c | **Concept Generator (#6)** | ✅ Built — `concept-gen/` |
| 3d | **Series Framework Generator (#7)** | ✅ Built — `series-framework/` |
| 3e | **Chapter Outliner (#9)** | ✅ Built — `chapter-outliner/` |
| 3f | **Chapter Drafter (#10)** | ✅ Built — `chapter-drafter/` |
| 3g | **Editorial Agent (#12)** | ✅ Built — `editorial-agent/` |

**Phase 3 status**: Writing pipeline is functional. Series Bible Generator (#8) is the remaining gap — it creates the canonical reference document consumed by Continuity Checker and Chapter Drafter. Currently the series bible files are maintained manually.

---

### Phase 4: Full Autonomy (October 2026+)
*Goal: Wire everything together. One orchestrator agent manages the entire lifecycle.*

| Priority | Build | Why | Effort |
|---|---|---|---|
| 4a | **KDP Publisher (#18)** | Automates the last manual step: uploading to KDP. Takes formatted files, cover, metadata → creates/updates listings. | 3-4 days |
| 4b | **Also-Bought Mapper (#5)** | Deepens market research — crawls "also bought" chains to find hidden comp titles and audience crossover. | 2-3 days |
| 4c | **Newsletter Swap Finder (#23)** | Automated cross-promotion partner discovery and outreach drafting. | 2 days |
| 4d | **Reader Magnet Funnel Analyzer (#29)** | Full funnel tracking: free download → email → purchase → series read-through. Identifies where readers drop off. | 2-3 days |
| 4e | **Backmatter Link Tracker (#28)** | Tracks which CTAs in your backmatter actually convert. Data feeds into funnel analyzer. | 1-2 days |
| 4f | **Wide vs KU Simulator (#30)** | Monte Carlo simulation of going wide. With 3+ books of KDP data, this becomes meaningful. | 2-3 days |
| 4g | **KU Page-Flip Detector (#31)** | Bot detection for KENP reads. Protects your account. | 1-2 days |
| 4h | **Audiobook Calculator (#32)** | ROI analysis for audiobook production. | 1 day |
| 4i | **Pipeline Orchestrator** (NEW — the master agent) | The conductor. Takes an idea, routes it through all stages, manages human review gates, tracks progress. "Build me a book from this concept." | 5-7 days |

**Agent Migration Strategy:**
- All 25 existing tools are standalone Python CLIs. Phase 4 converts them to **Claude Agent SDK agents**.
- Each agent exposes tool definitions so other agents can call it programmatically.
- New tools built from Phase 2 onward should be **agent-native from day one** (use Claude Agent SDK, not click CLI).
- The Pipeline Orchestrator (#4i) is the master agent that wires everything together.
- Backport existing 25 CLIs to agents as part of building the Orchestrator.

**Phase 4 outcome**: The complete autonomous pipeline. You capture an idea in the Idea Capture PWA → the orchestrator researches the market, generates a concept, builds the framework, outlines and drafts chapters, edits, formats, publishes, launches, markets, monitors, and feeds learnings into the next book. You approve at 5 gates: concept, outline, manuscript, cover, and launch.

---

### Phase 5: Business (2027)
*Goal: Turn proven tools into revenue beyond book sales.*

| Priority | Build | Why |
|---|---|---|
| 5a | **Author Tools SaaS (#37)** | Package the best tools as a paid service. Review Miner, Category Spy, Comp Tracker, Blurb Tester, Cover Analyzer — other indie authors would pay $29-99/mo for these. |

---

### The End State

```
┌─────────────────────────────────────────────────────────┐
│                   PIPELINE ORCHESTRATOR                   │
│              "Build me a book from this idea"             │
├──────────┬──────────┬──────────┬──────────┬──────────────┤
│ RESEARCH │ WRITING  │PRODUCTION│ LAUNCH   │ INTELLIGENCE │
│ Scout    │ Bible    │ Compiler │ Orchestr.│ Dashboard    │
│ Miner    │ Concept  │ Formatter│ Ad Copy  │ Price Opt.   │
│ Cat. Spy │ Framework│ Cover Gen│ Blog Gen │ Read-Through │
│ Comp Trk │ Outliner │ Cover Cmp│ ARC Mgr  │ Rev. Monitor │
│ Also-Bot │ Drafter  │ Blurb    │ Repurpose│ Royalty Rec. │
│          │ Editor   │ KDP Pub  │ BookTok  │ GEO Opt.     │
│          │ Contin.  │          │ NL Swap  │ Funnel Anlz. │
├──────────┴──────────┴──────────┴──────────┴──────────────┤
│              MCP BOOK DATA SERVER (unified data)          │
├───────────────────────────────────────────────────────────┤
│  HUMAN REVIEW GATES: concept │ outline │ manuscript │     │
│                       cover  │ launch go/no-go            │
└───────────────────────────────────────────────────────────┘
```

**37 tools (26 built, 11 remaining). 5 human review gates. One orchestrator. Ideas in, books out.**
