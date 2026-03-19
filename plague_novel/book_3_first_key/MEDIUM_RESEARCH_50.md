# Medium Research: 50 Articles for Self-Publisher Toolkit & Author Business

**Date:** March 14, 2026
**Purpose:** Curated articles grouped by how they apply to my work — tools to enhance, new tools to build, marketing strategies to adopt, and infrastructure to upgrade.

---

## Group A: Claude Agent SDK & AI Agent Architecture (BUILD NEW)

*These articles teach how to build the production AI agents that power my entire tool pipeline. Highest leverage — every tool I build benefits from these patterns.*

### A1. The Definitive Guide to the Claude Agent SDK
**Priority: HIGH** | [Read on Medium](https://datapoetica.medium.com/the-definitive-guide-to-the-claude-agent-sdk-building-the-next-generation-of-ai-69fda0a0530f)
Anthropic's open-source framework for building autonomous AI agents in Python/TypeScript. Production-grade, with built-in tool management and permission controls.
**Action:** Use this as the foundation for all my pipeline tools (Chapter Drafter, Editorial Agent, Continuity Checker). Instead of one-off scripts, build them as proper Claude agents with tool access.

### A2. Claude Agent SDK: Less Boilerplate, More Useful Automation
**Priority: HIGH** | [Read on Medium](https://medium.com/@karishmababu/claude-agent-sdk-less-boilerplate-more-useful-automation-c20dd130f729)
Practical guide to simplifying agent mechanics — tool access, permissions, and safe system interactions.
**Action:** Apply to my existing tools (review-miner, kdp-scout) to make them agent-orchestratable rather than standalone CLIs.

### A3. How to Run Claude Agents in Production
**Priority: HIGH** | [Read on Medium](https://medium.com/@hugolu87/how-to-run-claude-agents-in-production-using-the-claude-sdk-756f9d3c93d8)
Covers reliability, error handling, and monitoring for Claude agents running unattended.
**Action:** Essential reading before deploying any scheduled agents (Launch Day Dashboard, Review Monitor, Price Optimizer).

### A4. 10 Must-Have Skills for Claude (and Any Coding Agent) in 2026
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@unicodeveloper/10-must-have-skills-for-claude-and-any-coding-agent-in-2026-b5451b013051)
Community library of 1,234+ agentic skills for Claude Code, Cursor, etc.
**Action:** Browse for marketing/SEO/copywriting skills that could enhance my Blog Post Generator and Ad Copy Generator.

### A5. Claude Code Agent Skills 2.0: From Custom Instructions to Programmable Agents
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@richardhightower/claude-code-agent-skills-2-0-from-custom-instructions-to-programmable-agents-ab6e4563c176)
How to create reusable agent skills — turning custom instructions into programmable, shareable modules.
**Action:** Package my best Claude Code workflows (novel editing, book formatting, market research) as reusable skills.

### A6. Building Claude Code from Scratch: A Simple Journey into AI Agents
**Priority: LOW** | [Read on Medium](https://medium.com/@yashv6655/building-claude-code-from-scratch-a-simple-journey-into-ai-agents-2ca43eccad6e)
How to build a working AI coding agent in ~300 lines of Python using just the Claude API.
**Action:** Reference for understanding Claude Code's internals. Useful if I ever need a custom agent host.

### A7. Build Your First AI Agent: Connecting FastAPI to Claude with MCP & LangGraph
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@harshmehta6711/build-your-first-ai-agent-connecting-fastapi-to-claude-with-mcp-langgraph-0cafd8d7d5e2)
Combines FastAPI (web server), Claude (reasoning), and MCP (tool protocol) into a single agent architecture.
**Action:** Pattern for turning my CLI tools into web-accessible APIs — e.g., Review Miner as a web service.

---

## Group B: MCP (Model Context Protocol) & Tool Integration (BUILD NEW)

*MCP is "USB-C for AI tools" — a standard way for Claude to connect to databases, APIs, and local tools. This could unify my entire tool pipeline.*

### B1. The Model Context Protocol: The Missing Standard for the AI Agent Era
**Priority: HIGH** | [Read on Medium](https://medium.com/@divyamangla01/the-model-context-protocol-mcp-the-missing-standard-for-the-ai-agent-era-a28c7e086d4c)
MCP as the standardized way for AI to discover and use external tools. Thousands of MCP servers now exist.
**Action:** Build MCP servers for my tools (KDP data access, review database, royalty data). Claude could then query "how are my books performing?" and get answers from all platforms at once.

### B2. From REST to MCP: Why Developers Should Embrace the Model Context Protocol
**Priority: MEDIUM** | [Read on Medium](https://bytebridge.medium.com/from-rest-to-mcp-why-developers-should-embrace-the-model-context-protocol-003e3806874a)
Migration guide from traditional REST APIs to MCP. Explains when MCP is better and when REST is still fine.
**Action:** Decide which of my tools should become MCP servers (most value: royalty data, review data, BSR tracking).

### B3. What It Takes to Run MCP in Production
**Priority: MEDIUM** | [Read on Medium](https://bytebridge.medium.com/what-it-takes-to-run-mcp-model-context-protocol-in-production-3bbf19413f69)
Production concerns: reliability, security, monitoring for MCP servers.
**Action:** Read before deploying any MCP servers. Security is critical since these expose my data to AI.

### B4. Developing a Model Context Protocol Server and Client
**Priority: LOW** | [Read on Medium](https://medium.com/@manojjahgirdar/developing-a-model-context-protocol-mcp-server-and-client-for-your-agent-tool-interoperability-e55ad8a8f004)
Step-by-step tutorial for building MCP servers from scratch.
**Action:** Hands-on reference when building my first MCP server.

---

## Group C: API Cost Optimization (ENHANCE EXISTING)

*Every tool I build uses the Claude API. These articles directly reduce my operating costs.*

### C1. Anthropic Just Fixed the Biggest Hidden Cost in AI Agents (Automatic Prompt Caching)
**Priority: HIGH** | [Read on Medium](https://medium.com/ai-software-engineer/anthropic-just-fixed-the-biggest-hidden-cost-in-ai-agents-using-automatic-prompt-caching-9d47c95903c5)
Auto-caching cuts API costs by 90%. Already in my reading notes — the 5 rules for prompt ordering.
**Action:** Apply to every tool. Static-to-dynamic prompt ordering in all API calls.

### C2. Prompt Caching: How I Went From $720 to $72 Monthly
**Priority: HIGH** | [Read on Medium](https://medium.com/@labeveryday/prompt-caching-is-a-must-how-i-went-from-spending-720-to-72-monthly-on-api-costs-3086f3635d63)
Real-world cost reduction story with specific implementation details.
**Action:** Benchmark my current API spend. Apply caching to Review Miner and KDP Scout first (highest API usage).

### C3. How I Reduced LLM Token Costs by 90% Building AI Agents
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@ravityuval/how-i-reduced-llm-token-costs-by-90-using-prompt-rag-and-ai-agent-optimization-f64bd1b56d9f)
Combines prompt caching, RAG, and agent optimization for maximum cost reduction.
**Action:** Consider RAG approach for tools with large reference data (Series Bible lookups, Review Miner corpus).

### C4. Building Production Apps with Claude API: Complete Technical Guide
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@reliabledataengineering/building-production-apps-with-claude-api-the-complete-technical-guide-to-prompts-tokens-and-8a740b9bab3a)
Comprehensive guide covering prompts, tokens, cost optimization, and production patterns.
**Action:** Reference guide for all future API development.

### C5. How to Use Claude Opus 4 Efficiently: Cut Costs by 90%
**Priority: LOW** | [Read on Medium](https://medium.com/@asimsultan2/how-to-use-claude-opus-4-efficiently-cut-costs-by-90-with-prompt-caching-batch-processing-f06708ae7467)
Opus-specific: batch processing + prompt caching for expensive model usage.
**Action:** Apply batch processing for non-urgent tasks (weekly reports, bulk review analysis).

---

## Group D: Web Scraping & Data Collection (BUILD NEW / ENHANCE EXISTING)

*The backbone of all monitoring tools — BSR tracking, competitor prices, review scraping.*

### D1. Web Scraping for Data Engineers: Production Pipelines with Scrapling
**Priority: HIGH** | [Read on Medium](https://htrixe.medium.com/web-scraping-for-data-engineers-architecture-robustness-and-production-pipelines-with-scrapling-c327278222f7)
Production-grade scraping architecture: retry logic, rate limiting, monitoring, structured logging.
**Action:** Apply this architecture to Launch Day Dashboard, Category Spy, and Comp Title Decay Tracker scrapers.

### D2. Stop Getting Blocked: Python Web Scraping Tools That Actually Work in 2026
**Priority: HIGH** | [Read on Medium](https://medium.com/@inprogrammer/best-python-web-scraping-tools-2026-updated-87ef4a0b21ff)
Current state of anti-bot detection and how to work around it (Playwright, stealth plugins, rotating proxies).
**Action:** Critical for Amazon scraping. My tools that scrape Amazon product pages need to stay undetected.

### D3. Automate Web Scraping with Docker: Schedule Python Selenium on Cron
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@thoren.lederer/automate-your-web-scraping-with-docker-schedule-python-selenium-scripts-on-cron-and-watch-the-a15511701a75)
Containerized scheduled scraping with automatic retries.
**Action:** Pattern for running my monitoring agents (Review Miner weekly mode, BSR tracker) reliably.

### D4. There's a New Sheriff in Web Scraping: Meet Crawl4AI
**Priority: MEDIUM** | [Read on Medium](https://sebastien-sime.medium.com/theres-a-new-sheriff-in-web-scraping-meet-crawl4ai-4f2cc4e4e434)
AI-native web scraper — uses LLMs to understand page structure instead of brittle CSS selectors.
**Action:** Evaluate for Amazon product page scraping. If it handles layout changes automatically, it's more resilient than my current Playwright selectors.

### D5. How AI Agents Are Changing the Future of Web Scraping
**Priority: LOW** | [Read on Medium](https://medium.com/@davidfagb/how-ai-agents-are-changing-the-future-of-web-scraping-a19f836ae803)
Single autonomous agents handling varied scraping tasks with AI reasoning.
**Action:** Long-term vision: one agent that can scrape any book-related page without custom selectors.

---

## Group E: Amazon KDP Marketing & Ads (ENHANCE EXISTING TOOLS)

*Direct revenue impact. These feed into Ad Copy Generator, Launch Orchestrator, and Price Optimizer.*

### E1. Amazon KDP 2026 Survival Guide: A10 Algorithm
**Priority: HIGH** | [Read on Medium](https://medium.com/@neilcaley/amazon-kdp-is-changing-fast-the-2026-survival-guide-to-ranking-royalties-and-the-a10-algorithm-bac40eda3dd7)
A10 algorithm prioritizes semantic relevance (not just keywords) and external traffic quality. Rufus AI shopping assistant changes discovery.
**Action:** Update KDP Scout keyword logic to account for semantic matching. Update Blog Post Generator to drive external traffic.

### E2. I Spent $166.66 on Amazon Ads — Here's What I Learned
**Priority: HIGH** | [Read on Medium](https://medium.com/@gilianortillan/i-spent-166-66-on-amazon-ads-for-my-first-book-heres-what-i-ve-learned-8701025a5e1e)
First-time advertiser's data: 0.5% CTR is excellent, top keywords that convert, budget allocation.
**Action:** Feed benchmarks into Ad Copy Generator — score generated ads against these CTR/conversion baselines.

### E3. Mastering KDP Ads: Tips from a $2.5M Expert
**Priority: HIGH** | [Read on Medium](https://medium.com/@nickvannello/mastering-amazon-kdp-ads-tips-from-a-2-5m-expert-198cce2b9439)
Expert-level ad optimization: bid strategies, keyword harvesting, campaign structure.
**Action:** Incorporate expert bid strategies into Ad Copy Generator. Add campaign structure templates to Launch Orchestrator.

### E4. The BEST Low-Budget Ad Strategy for Amazon KDP
**Priority: MEDIUM** | [Read on Medium](https://medium.com/the-side-hustle-club/the-best-low-budget-ad-strategy-for-amazon-kdp-ba0982ce42a)
"Lottery Ad" strategy: multiple books in one campaign, minimum CPC.
**Action:** Add as a campaign template in Ad Copy Generator for backlist titles.

### E5. 5 Free Marketing Strategies to Boost Amazon KDP Book Sales
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@stickleycreations/5-free-marketing-strategies-to-boost-your-amazon-kdp-book-sales-d4acb9350f26)
Free promotion tactics: KDP promotions, countdown deals, Kindle deals nominations.
**Action:** Add promotional calendar features to Launch Orchestrator — schedule KDP Select promos and countdown deals.

### E6. Top 6 KDP Niches to Sell in 2026 Without Paid Ads
**Priority: LOW** | [Read on Medium](https://medium.com/write-a-catalyst/top-6-amazon-kdp-niches-to-sell-in-2026-without-paid-ads-9390c31555f8)
Niche identification for organic discovery.
**Action:** Feed niche patterns into Concept Generator for future book ideas.

---

## Group F: Substack & Newsletter Growth (MARKETING STRATEGY)

*Grows my email list and reader platform. Feeds into welcome email sequence and reader magnet funnel.*

### F1. The Only Substack Strategy That Still Works in 2026
**Priority: HIGH** | [Read on Medium](https://medium.com/new-writers-welcome/the-only-substack-strategy-that-still-works-in-2026-ccc1c813da67)
Substack runs on trust, not hacks. The platform algorithm actually helps new writers. Notes feature drives follower growth.
**Action:** Commit to daily Substack Notes. Use as discovery engine to feed my welcome email sequence.

### F2. Substack for Beginners: The Complete 2026 Tutorial
**Priority: MEDIUM** | [Read on Medium](https://sinemgnel.medium.com/substack-for-beginners-the-complete-2026-tutorial-6867a22834d6)
Comprehensive setup guide — understand the three platforms in one (newsletter, Notes, podcast).
**Action:** Audit my Substack setup against this guide. Am I using all three components?

### F3. The LinkedIn + Substack Strategy for 2026
**Priority: MEDIUM** | [Read on Medium](https://medium.com/online-writing-101/the-linkedin-substack-strategy-for-2026-get-seen-and-paid-81cb0c70f9f7)
Cross-platform strategy using LinkedIn for discovery and Substack for conversion.
**Action:** Consider whether LinkedIn is worth adding to my platform (historical fiction + tech intersection could play well there).

### F4. Case Studies of Successful Writers on Medium and Substack (Early 2026)
**Priority: MEDIUM** | [Read on Medium](https://medium.com/illumination/case-studies-of-successful-writers-on-medium-and-substack-as-of-early-2026-5c3d4ac17736)
Real writer revenue data and growth patterns for both platforms.
**Action:** Benchmark my Medium/Substack performance against these case studies. Identify gaps.

### F5. 5 Ways to Grow Your Email Newsletter in 2026
**Priority: LOW** | [Read on Medium](https://medium.com/@iampaulrose/5-ways-to-grow-your-email-newsletter-in-2026-07b447729f9c)
Tactical newsletter growth tips.
**Action:** Quick-scan for any tactics I'm not using.

---

## Group G: Book Launch & Pre-Order Strategy (MARKETING STRATEGY)

*Directly applicable to Book 3 launch.*

### G1. Why Pre-Orders Matter: Successful Book Marketing Campaign
**Priority: HIGH** | [Read on Medium](https://author-marketer.medium.com/why-pre-orders-matter-and-how-to-run-a-successful-book-marketing-campaign-13aaa791b565)
3-6 month pre-order window, exclusive content drops at different stages, email marketing during pre-order phase.
**Action:** Set up Book 3 pre-order NOW. Build a content calendar into Launch Orchestrator: chapter sneak peeks, author Q&A, countdown emails.

### G2. This Is How to Create a Pre-Launch Strategy for Your Book
**Priority: HIGH** | [Read on Medium](https://medium.com/the-1000-day-mfa/this-is-how-to-create-a-pre-launch-strategy-for-your-book-a7810ed0da6b)
Step-by-step pre-launch blueprint — ARC timeline, review solicitation, launch team building.
**Action:** Feed this blueprint into Launch Orchestrator as a configurable template.

### G3. eBook Pre-orders: Strategies for Maximizing Launch Success
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@geekpublishers/ebook-pre-orders-strategies-for-maximizing-your-launch-success-e3857a51f2e8)
KDP-specific pre-order tactics and timing.
**Action:** Review KDP pre-order requirements and add to KDP Publisher tool spec.

### G4. Why Now Is the Perfect Time to Set Up Your Next Book's Pre-Sale
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@arkhem.j.cain/why-now-is-the-perfect-time-to-set-up-your-next-books-pre-sale-even-if-you-re-still-writing-it-8aa25091d806)
Set up pre-sale even while still writing — validates demand and builds anticipation.
**Action:** Consider setting up Book 3 pre-order with a placeholder cover while finishing the manuscript.

---

## Group H: Content Repurposing & Social Media (MARKETING STRATEGY)

*Turn one piece of content into many. Multiplies the value of every blog post and article.*

### H1. The Rising Demand for Video Content in 2026: Why Every Creator Needs to Repurpose Articles into Videos
**Priority: HIGH** | [Read on Medium](https://medium.com/@aboda.bob7/the-rising-demand-for-video-content-in-2026-why-every-creator-needs-to-repurpose-articles-into-f6fe993db5b0)
Video dominates discovery in 2026. Articles → short video clips is the highest-ROI repurposing path.
**Action:** Build a Content Repurposer tool: takes blog posts → generates TikTok/Reels scripts, tweet threads, newsletter excerpts. Add to pipeline as Tool #32.

### H2. How AI Helps in Repurposing Content Seamlessly Across Platforms
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@ihimanshukumar/how-ai-helps-in-repurposing-content-seamlessly-across-social-media-platforms-1e02e15f7c89)
AI-powered content adaptation: tone, length, format adjusted per platform automatically.
**Action:** Feed implementation patterns into Content Repurposer tool spec.

### H3. Top AI-Powered Creativity Tools for Content Creators in 2026
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@neovise/top-ai-powered-creativity-tools-for-content-creators-in-2026-c618aadd485f)
Opus Clip for video repurposing, other tools for cross-platform content.
**Action:** Evaluate Opus Clip for turning blog posts or book readings into short-form video.

### H4. How BookTok Turned a 19th-Century Novella into a Bestseller
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@canselturker12/how-booktok-turned-a-19th-century-novella-into-a-bestseller-0ac83a3b5dbe)
BookTok still drives massive sales. Emotional authenticity > polish. Medieval/historical fiction has BookTok potential.
**Action:** My historical plague fiction IS the kind of content BookTok amplifies. Create a BookTok strategy: atmospheric scenes, historical reveals, "did you know" hooks about the Black Death.

### H5. The Evolution of Book Marketing: From Bookstores to BookTok
**Priority: LOW** | [Read on Medium](https://medium.com/@publiwrite/the-evolution-of-book-marketing-from-bookstores-to-booktok-b2b5b9ed50ba)
Overview of how book marketing has shifted to creator-driven discovery.
**Action:** Background context. Reinforces the need for authentic social presence.

---

## Group I: Competitive Intelligence & Monitoring (ENHANCE EXISTING TOOLS)

*Feed into Price Optimizer, Comp Title Decay Tracker, and Launch Day Dashboard.*

### I1. Let's Build AI Agent System for Real-Time Pricing Alert Pipeline
**Priority: HIGH** | [Read on Medium](https://medium.com/@learn-simplified/lets-build-ai-agent-system-for-real-time-event-driven-pricing-alert-pipeline-b484465be730)
Event-driven pricing alert architecture with AI analysis.
**Action:** Direct blueprint for Price Optimizer (#25). Adapt the event-driven pipeline: price change detected → AI analysis → alert email.

### I2. How to Automate Competitor Monitoring Using AI
**Priority: HIGH** | [Read on Medium](https://medium.com/@jesse.henson/how-to-automate-competitor-monitoring-using-ai-eadf7e11fe33)
Full competitor monitoring pipeline: data collection → AI analysis → actionable alerts.
**Action:** Apply to Comp Title Decay Tracker. Add automated competitor monitoring mode with weekly AI-analyzed reports.

### I3. AI Tools That Analyze Your Competitors and Tell You How to Win
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@milanpatel01/ai-tools-that-analyze-your-competitors-and-tell-you-how-to-win-i-tested-8-tools-and-heres-what-810836b855e7)
Review of 8 competitive intelligence tools — features, pricing, what actually gives an edge.
**Action:** Identify which features to replicate in my own tools (free) vs. which tools are worth paying for.

### I4. Complete Guide to Price Monitoring
**Priority: LOW** | [Read on Medium](https://medium.com/@pintelguru/guide-to-price-monitoring-50299783eea1)
Comprehensive overview of price monitoring methodology.
**Action:** Reference for Price Optimizer implementation.

---

## Group J: Google Apps Script & Automation (ENHANCE EXISTING PA)

*I already run a 24/7 Apps Script PA. These articles can enhance it.*

### J1. Google Workspace CLI (gws) — New in 2026
**Priority: HIGH** | [Read on Medium](https://medium.com/ai-software-engineer/i-tested-new-google-workspace-cli-and-uncovered-the-hacks-you-should-know-9f4126105985)
Google's new CLI for Workspace, written in Rust. Could replace some of my clasp-based workflows.
**Action:** Test `gws` CLI. If it's faster/better than `clasp`, migrate my Apps Script deployment workflow.

### J2. Organize Your Gmail Like a Pro: 6 Apps Script Hacks
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@yoloshe302/organize-your-gmail-like-a-pro-6-google-apps-script-hacks-to-save-you-time-6cd015ca9ee0)
Gmail automation patterns: auto-delete, snooze, daily summaries to Slack.
**Action:** Compare against my current email triage function. Any patterns I'm missing?

### J3. A New Era for Google Apps Script: Natural Language Automation
**Priority: MEDIUM** | [Read on Medium](https://medium.com/google-cloud/a-new-era-for-google-apps-script-unlocking-the-future-of-google-workspace-automation-with-natural-a9cecf87b4c6)
Using natural language to generate Apps Script code — AI-assisted automation building.
**Action:** Evaluate for quickly prototyping new PA features.

### J4. Enhancing Work Productivity with OpenAI API and Google Apps Script
**Priority: LOW** | [Read on Medium](https://medium.com/@sangjinn/enhancing-work-productivity-with-the-openai-api-and-gas-google-apps-script-a2896f51a514)
Connecting LLMs to Apps Script for AI-powered workflows.
**Action:** I already do this with Claude — but check if there are patterns I haven't considered.

---

## Group K: Author Website & SEO (MARKETING STRATEGY)

*My website has known issues (404s, missing pages). These articles help fix and optimize it.*

### K1. From SEO to GEO: What Actually Changes in 2026
**Priority: HIGH** | [Read on Medium](https://medium.com/@stahl950/from-seo-to-geo-what-actually-changes-for-you-in-2026-e4050e82538b)
SEO is shifting to GEO (Generative Engine Optimization) — optimizing for AI search results, not just Google rankings.
**Action:** Update Blog Post Generator to optimize for AI discovery (structured data, clear answers, authoritative sourcing).

### K2. How Authors Can Use SEO for Book Marketing
**Priority: MEDIUM** | [Read on Medium](https://aditi-ws.medium.com/how-authors-can-use-seo-for-book-marketing-c4412dc58286)
Author-specific SEO: targeting reader search queries, not author queries.
**Action:** Feed these keyword strategies into Blog Post Generator. Target "books about the Black Death" not "Randy Pellegrini author."

### K3. How to Design Landing Pages That Boost SEO & Maximize Conversions
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@marklevisebook/how-to-design-landing-pages-that-boost-seo-maximize-conversions-925a227ab31e)
Landing page best practices: headline, CTA, testimonials, long-tail keywords.
**Action:** Apply to my book landing pages on randypellegrini.com. Fix the 404s and optimize for conversion.

### K4. I Created a Landing Page That Pays Me $1K/Month
**Priority: LOW** | [Read on Medium](https://medium.com/@ayomiposij0/i-created-a-landing-page-that-pays-me-1k-month-step-by-step-no-tech-panic-required-45531af60593)
Step-by-step landing page monetization.
**Action:** Quick-scan for landing page patterns I'm not using.

---

## Group L: Book Cover & A/B Testing (ENHANCE EXISTING TOOLS)

### L1. How to A/B Test Your Cover Design
**Priority: HIGH** | [Read on Medium](https://medium.com/swlh/how-to-a-b-test-your-cover-design-b2fb111cdcd0)
A/B testing methodology for book covers — specifically targets potential customers, more reliable than social polls.
**Action:** Add A/B testing workflow to Cover Comp Analyzer. Generate multiple cover variants → run Facebook/Amazon ad tests → measure CTR per variant.

### L2. A/B Testing Book Covers on Pinterest (Free)
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@iwan-ross/trusting-your-vision-how-a-b-testing-book-covers-on-pinterest-changed-my-journey-e7060808f6e2)
Free A/B testing using Pinterest — no ad spend required.
**Action:** Add Pinterest A/B testing as a free alternative in Cover Comp Analyzer workflow.

---

## Group M: Goodreads & Review Strategy (MARKETING STRATEGY)

### M1. How to Promote Your Book on Goodreads
**Priority: MEDIUM** | [Read on Medium](https://medium.com/writing101/how-to-promote-your-book-on-goodreads-93e1ffebbba9)
Goodreads-specific marketing: giveaways, lists, groups, author page optimization.
**Action:** Add Goodreads promotion tasks to Launch Orchestrator timeline.

### M2. Goodreads Giveaway Strategies for Authors
**Priority: MEDIUM** | [Read on Medium](https://astridvawabreo.medium.com/goodreads-giveaway-strategies-for-authors-in-summer-2025-5dcb7cc86666)
Standard giveaway ($119) vs Premium ($599). Run for 7-30 days. 40,000+ readers enter daily.
**Action:** Budget a Goodreads giveaway into Book 3 launch plan. Add as a phase in Launch Orchestrator.

### M3. I Ranked 5 Paid Book Review Sites for New Authors
**Priority: MEDIUM** | [Read on Medium](https://catrinaprager.medium.com/i-ranked-5-paid-book-review-sites-for-new-authors-ede71fe1bb33)
Comparison of paid review services: Kirkus, BookLife, Reedsy Discovery, etc.
**Action:** Evaluate which service gives best ROI for historical fiction. Add to ARC Manager as an alternative review source.

---

## Group N: Analytics & Dashboards (BUILD NEW)

### N1. Building an Interactive Analytics Dashboard Using Python
**Priority: MEDIUM** | [Read on Medium](https://odendavid.medium.com/building-an-interactive-analytics-dashboard-using-python-0cf6750e3ad6)
Streamlit + Pandas + Plotly for interactive dashboards.
**Action:** Use this stack for Launch Day Dashboard (#23). Streamlit is the fastest path to a visual dashboard.

### N2. Python for Real-Time Analytics Dashboards with WebSockets
**Priority: LOW** | [Read on Medium](https://medium.com/@sweetabdulrehman01/python-for-real-time-analytics-dashboards-with-websockets-and-plotly-42554a759860)
Real-time auto-refreshing dashboards.
**Action:** Apply WebSocket pattern if Launch Day Dashboard needs live updates during launch week.

---

## Group O: Self-Publishing Industry & Strategy (GENERAL KNOWLEDGE)

### O1. Self-Publishing in 2026: What Actually Works Now
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@Info_89985/self-publishing-in-2026-what-actually-works-now-65e46c17ea77)
The real gap is between authors who have a system and authors who are hoping a single upload will change their life.
**Action:** Validates my entire tool pipeline approach. I AM building the system.

### O2. Publishing in an AI-Saturated World
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@Jamesroha/publishing-in-an-ai-saturated-world-f93cf2663c11)
How to differentiate human-crafted work in an AI-flooded marketplace.
**Action:** Informs my marketing angle: emphasize the research, the craft, the human story behind the books.

### O3. Self-Publishing Your Book? 5 Legit Ways to Use AI
**Priority: LOW** | [Read on Medium](https://medium.com/illumination/self-publishing-your-book-here-are-5-legit-ways-to-use-ai-cddb03233973)
Ethical AI use in self-publishing.
**Action:** Quick-scan for ideas I haven't considered.

### O4. Where to Publish and Buy Books in 2026
**Priority: LOW** | [Read on Medium](https://tc-mill.medium.com/where-to-publish-and-buy-books-in-2026-options-for-indie-authors-small-publishers-and-their-fans-3e21f9514a27)
Platform landscape beyond KDP.
**Action:** Reference for Wide vs KU Simulator (#29) — data on platform market share.

---

## Group P: Cloudflare & Infrastructure (BUILD NEW)

### P1. Cloudflare Workers: The Complete Serverless Edge Computing Platform
**Priority: LOW** | [Read on Medium](https://medium.com/@ltwolfpup/cloudflare-workers-the-complete-serverless-edge-computing-platform-40a113164ab6)
0ms cold starts, 330+ edge locations, free tier generous.
**Action:** Consider migrating my email capture Cloudflare Worker to a more sophisticated setup. Could host lightweight APIs (backmatter link tracker, analytics endpoint) on Workers.

### P2. I Built a Serverless AI Bot with Cloudflare Workers and OpenAI
**Priority: LOW** | [Read on Medium](https://medium.com/@connect.hashblock/i-built-a-serverless-ai-bot-with-cloudflare-workers-and-openai-no-backend-required-fa608d14335c)
AI bot running entirely on Cloudflare Workers — no backend server.
**Action:** Pattern for lightweight AI-powered endpoints. Could power Backmatter Link Tracker (#27) or reader analytics.

---

## Group Q: Solo Creator Business (STRATEGY)

### Q1. How I Built SaaS-Powered Passive Income as a Solo Developer
**Priority: MEDIUM** | [Read on Medium](https://medium.com/@IncomeAIcademy/how-i-built-saas-powered-passive-income-as-a-solo-developer-without-burning-out-f77e6c8f32af)
Solo dev SaaS: find repeated complaints in communities, build hyper-niche solutions, automate billing and support.
**Action:** My self-publisher tools ARE a potential SaaS product. Other indie authors would pay for Review Miner, Category Spy, Comp Tracker as a service.

### Q2. My "Passive Income" Setup for February 2026
**Priority: LOW** | [Read on Medium](https://medium.com/no-time/my-passive-income-setup-for-february-2026-programming-money-to-work-while-i-sleep-552b90db99b0)
Specific passive income stack and automation setup.
**Action:** Compare against my own automation stack. Any gaps?

---

## Priority Matrix

### IMMEDIATE (Do this week — Book 3 launch prep)
| # | Article | Action | Tool Impact |
|---|---------|--------|-------------|
| G1 | Pre-Orders Matter | Set up Book 3 pre-order on KDP | Launch Orchestrator |
| G2 | Pre-Launch Strategy | Build launch timeline template | Launch Orchestrator |
| E1 | A10 Algorithm Guide | Update keyword strategy | KDP Scout |
| F1 | Substack Strategy 2026 | Start daily Notes | Newsletter growth |
| L1 | A/B Test Cover Design | Test Book 3 cover variants | Cover Comp Analyzer |

### HIGH PRIORITY (Next 2 weeks — infrastructure)
| # | Article | Action | Tool Impact |
|---|---------|--------|-------------|
| A1 | Claude Agent SDK Guide | Learn SDK, refactor tools | All future tools |
| A3 | Agents in Production | Production patterns | All scheduled agents |
| C1 | Prompt Caching | Apply to all API calls | Cost reduction |
| C2 | $720→$72 Cost Reduction | Benchmark + optimize | Cost reduction |
| D1 | Production Scraping | Architecture for scrapers | Dashboard, Category Spy |
| D2 | Anti-Bot Scraping 2026 | Update Amazon scrapers | All scraping tools |
| I1 | Pricing Alert Pipeline | Blueprint for Price Optimizer | Price Optimizer (#25) |
| I2 | Competitor Monitoring | Enhance comp tracking | Comp Tracker (#4) |
| B1 | MCP Standard | Plan MCP server architecture | Unified tool access |
| K1 | SEO → GEO Shift | Update content strategy | Blog Post Generator |
| J1 | Google Workspace CLI | Evaluate for PA deployment | Apps Script PA |

### MEDIUM PRIORITY (Next month — enhancements)
| # | Article | Action | Tool Impact |
|---|---------|--------|-------------|
| E2 | Amazon Ads Benchmarks | Add CTR baselines | Ad Copy Generator |
| E3 | $2.5M KDP Ads Expert | Expert bid strategies | Ad Copy Generator |
| H1 | Video Content 2026 | Plan Content Repurposer tool | NEW tool #32 |
| H4 | BookTok for Historical Fiction | Create BookTok strategy | Marketing strategy |
| M1 | Goodreads Marketing | Add GR tasks to launch | Launch Orchestrator |
| M2 | Goodreads Giveaways | Budget for Book 3 | Launch plan |
| Q1 | Solo SaaS Income | Evaluate tools-as-SaaS | Business strategy |
| N1 | Python Dashboards | Streamlit for Dashboard | Launch Day Dashboard (#23) |

### LOW PRIORITY (Backlog — read when relevant)
| # | Article | Action | Tool Impact |
|---|---------|--------|-------------|
| A4-A6 | Agent skills deep-dives | Reference | Agent development |
| B2-B4 | MCP tutorials | Reference when building | MCP servers |
| C3-C5 | Cost optimization extras | Reference | API costs |
| D3-D5 | Scraping extras | Reference | Scraping tools |
| E4-E6 | KDP marketing extras | Reference | Marketing |
| F2-F5 | Newsletter extras | Reference | Newsletter |
| G3-G4 | Pre-order extras | Reference | Launch plan |
| H2-H3, H5 | Content repurposing extras | Reference | Content strategy |
| K2-K4 | SEO/landing page extras | Reference | Website |
| O1-O4 | Industry strategy | Background reading | General knowledge |
| P1-P2 | Cloudflare extras | Reference | Infrastructure |

---

## New Tools Suggested by This Research

| # | Tool Name | Source Articles | Priority |
|---|-----------|----------------|----------|
| 32 | **Content Repurposer** — Blog → TikTok scripts, tweet threads, newsletter excerpts, video scripts | H1, H2, H3 | Medium |
| 33 | **MCP Book Data Server** — Unified MCP interface to all book data (royalties, reviews, BSR, pricing) | B1, B2, B3 | Medium |
| 34 | **GEO Optimizer** — Optimize content for AI search engines (structured data, authoritative sourcing) | K1 | Medium |
| 35 | **BookTok Script Generator** — Takes book scenes/facts → generates short-form video scripts with hooks | H4, H1 | Low |
| 36 | **Author Tools SaaS** — Package existing tools (Review Miner, Category Spy, etc.) as paid web service | Q1 | Future |
