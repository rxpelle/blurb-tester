# Medium Feed Reading Notes — March 14, 2026

8 curated articles from my Medium "For You" feed, analyzed for adoption potential and implementation.

---

## 1. I've Been a Costco Member for 25 Years. Last Month I Built an AI Agent to Get My Money Back

**By:** Vivek V | **603 claps** | [Read on Medium](https://medium.com/aws-in-plain-english/ive-been-a-costco-member-for-25-years-last-month-i-built-an-ai-agent-to-get-my-money-back-09ed903751b0)

### What It Is
An AI-powered Costco receipt scanner that uploads receipt PDFs, parses them with Amazon Nova AI, scrapes current deals, cross-references purchases, and emails a weekly price-adjustment report. Runs serverless on AWS for under $1/month.

### Why It Matters for Me
This is the exact pattern I already use with my PA — automated agents that run on schedules and email results. But the execution is sharper: receipt OCR → deal scraping → AI cross-referencing → formatted HTML email. The "scan-compare-notify" pattern applies to many things beyond Costco.

**Applicable ideas:**
- **Amazon price tracking for my books.** Same architecture: scrape my book's price/rank periodically, compare against historical data, email me alerts when something changes (BSR spike, review milestone, price drop by competitors).
- **KDP royalty monitoring.** Weekly agent that checks KDP reports and emails formatted summaries — better than logging into the dashboard manually.
- **Review monitoring.** Scrape new reviews, run sentiment analysis, email digest.

### How I'd Implement It
I don't need AWS — my Google Apps Script PA already handles scheduled tasks and email. The pattern translates:

1. **Apps Script trigger** (daily/weekly) calls a function
2. Function scrapes target data (KDP dashboard via Playwright, Amazon product page, Goodreads)
3. Formats results as HTML email
4. Sends via GmailApp

**Or** for heavier processing: a simple Node.js script on my Mac that runs via cron, uses Claude API for analysis, and sends results through my existing email service (`personal_assistant/scripts/email-service.js`).

**Effort:** Low — I already have 90% of the infrastructure. Just need to write the scraping/comparison logic.

---

## 2. Anthropic Just Added Auto-Memory to Claude Code — MEMORY.md (I Tested It)

**By:** Joe Njenga | **599 claps** | [Read on Medium](https://medium.com/@joe.njenga/anthropic-just-added-auto-memory-to-claude-code-memory-md-i-tested-it-0ab8422754d2)

### What It Is
Deep dive into Claude Code's auto-memory feature — the MEMORY.md file and topic-based memory files that Claude writes for itself during sessions.

### Why It Matters for Me
I'm already using this heavily (my MEMORY.md is extensive). But the article surfaces details I should optimize:

- **The 200-line rule:** Only the first 200 lines of MEMORY.md load at session start. My MEMORY.md is getting long — I should audit it and ensure the most important stuff is in the first 200 lines.
- **Topic files are loaded on demand**, not at startup. Heavy details should move to topic files.
- **CLAUDE.local.md** for private preferences (auto-added to .gitignore). I haven't been using this — could be useful for local paths, sandbox URLs, test data.

### How I'd Implement It
1. **Audit my MEMORY.md** — check line count, reorganize by priority (most-used project context at top, reference links at bottom)
2. **Create topic files** for detailed knowledge that doesn't need to load every session (e.g., `memory/book_marketing_strategy.md`, `memory/apps_script_architecture.md`)
3. **Start using CLAUDE.local.md** for machine-specific paths and credentials references
4. **Review memory every few weeks** — stale architecture decisions from months ago can mislead Claude

**Effort:** 30 minutes of cleanup. High ROI.

---

## 3. Anthropic Just Killed My $200/Month OpenClaw Setup. So I Rebuilt It for $15.

**By:** Phil | Rentier Digital Automation | **1.1K claps** | [Read on Medium](https://medium.com/@rentierdigital/anthropic-just-killed-my-200-month-openclaw-setup-so-i-rebuilt-it-for-15-9cab6814c556)

### What It Is
After Anthropic banned Claude Pro/Max OAuth tokens in third-party tools, the author rebuilt his personal AI agent system using two cheap VPS instances ($5-7/mo each) and open-source Chinese LLMs (Kimi K2.5, MiniMax M2.5, GLM-4.7-Flash) for ~$15/month total.

### Why It Matters for Me
Two key lessons, even though I'm not using OpenClaw:

**1. Model routing by task complexity.** The author uses expensive models only for complex reasoning and free/cheap models for heartbeats, calendar checks, and routine tasks. I should apply this same principle:
- My Apps Script PA uses Claude Haiku for morning briefings — good, that's already cheap
- But any future Claude API work should route by complexity, not default to Opus for everything

**2. He replaced 20 n8n workflows with one-paragraph English prompts.** His argument: when APIs change, n8n breaks silently with a red node. An LLM-based agent reads the error and adapts. This validates my approach of using Apps Script + Claude rather than a visual workflow tool.

**3. Security warnings worth noting:**
- Never connect real email to AI agents (prompt injection via email is a real attack vector)
- 135,000+ OpenClaw instances found publicly exposed with no auth
- Keep everything behind VPN/Tailscale

### How I'd Implement It
I don't need to switch to OpenClaw — my Claude Code + Apps Script setup is already more robust for my use case. But I should:

1. **Audit my API costs** when I use Claude API directly. Am I defaulting to Opus when Haiku would suffice?
2. **Consider model fallback chains** for any future API-based tools: Opus for complex tasks → Sonnet for medium → Haiku for simple
3. **Keep the security lessons in mind** — my Apps Script PA sends email, so prompt injection through incoming email is a real concern. My email triage function should sanitize/limit what it passes to Claude.

**Effort:** Mental model shift, no immediate code changes needed. Security audit of email triage worth doing.

---

## 4. Claude Cowork: The Complete Guide for PMs

**By:** Pawel Huryn | **262 claps** | [Read on Medium](https://medium.com/@huryn/claude-cowork-the-complete-guide-for-pms-e45e7cf0f52d)

### What It Is
Comprehensive guide to Claude's desktop agent (Cowork tab in Claude Desktop). It gets a sandboxed Linux VM, can create real files (.docx, .pptx, .xlsx, .pdf), connects to Gmail/GitHub/Slack/Drive via MCP servers, and spawns parallel sub-agents.

### Why It Matters for Me
Three things I should adopt:

**1. Desktop Commander (1-minute setup, highest ROI).** Install it in Claude Desktop → gives Claude full file system access with permission controls. Can install other MCP servers, access any file, reorganize desktop.

**2. Cross-compatible skills.** Business/marketing plugins from Cowork's marketplace can be loaded into Claude Code. The `skills.sh` ecosystem has marketing, SEO, and copywriting skills that could help with book promotion.

**3. Cowork for document generation.** When I need formatted .docx or .pdf output (book manuscripts, marketing materials, query letters), Cowork can generate real files — not just text I have to copy-paste.

### How I'd Implement It
1. **Install Desktop Commander** in Claude Desktop (Settings → Connectors → Browse → Desktop Commander). 1 minute.
2. **Browse skills.sh** for marketing/author-relevant skills: `npx skills add` to install
3. **Use Cowork for next book formatting task** instead of my manual pandoc workflow — test if it can generate a properly formatted .docx from markdown
4. **Note:** My Apps Script scheduled tasks are MORE reliable than Cowork's scheduling (Chrome extension scheduling is unreliable per the author). Keep using Apps Script for automation.

**Effort:** Desktop Commander install is 1 minute. Skills browsing is 30 minutes. Cowork testing is an hour.

---

## 5. Don't Use LLMs as OCR: Lessons Learned from Extracting Complex Documents

**By:** Marta Fernandez Garcia | **967 claps** | [Read on Medium](https://medium.com/@martia_es/dont-use-llms-as-ocr-lessons-learned-from-extracting-complex-documents-db2d1fafcdfb)

### What It Is
LLMs accessed via API do NOT apply the same preprocessing as consumer ChatGPT. Text extraction is usually fine; numbers are frequently wrong. The solution: use traditional OCR (AWS Textract) for extraction, convert to markdown, then use LLMs only for reasoning/transformation.

### Why It Matters for Me
I process documents in several contexts:
- **KDP reports** (PDFs with numbers — royalties, page reads, units sold)
- **Book manuscripts** (format conversion between .md, .docx, .pdf)
- **Research materials** for novel writing

The core lesson: **OCR for extraction, LLMs for reasoning.** When I'm pulling numbers from KDP reports or financial documents, I should NOT just send screenshots to Claude and ask it to read the numbers. The API will get numbers wrong.

### How I'd Implement It
1. **For KDP report extraction:** Use a dedicated OCR step first (even just a PDF text extraction library like `pdf-parse` in Node.js), then feed the extracted text to Claude for analysis
2. **For any future document processing tool:** Always separate the extraction pipeline (OCR/text extraction) from the reasoning pipeline (Claude)
3. **Rule of thumb:** If numbers matter, never trust LLM vision alone

**Effort:** Low — this is a principle to apply going forward, not an immediate code change.

---

## 6. We Fired Jira and Slack

**By:** Jari Mattlar | **1.2K claps** | [Read on Medium](https://medium.com/@mattlar.jari/we-fired-jira-and-slack-8febdc0a5843)

### What It Is
A team replaced Jira with Linear and Slack with Float. Results after 90 days: PR cycle time down 34%, deep work hours up from 8 to 14/week, after-hours messages down 67%, zero voluntary turnover (was 23% annualized).

### Why It Matters for Me
As a solo creator, I don't have a team — but the core insight applies to my own workflow:

**"Tools architect behavior."** The tools I use 8 hours a day shape what I produce more than any intention or plan. This is worth examining:

- My writing tool (VS Code + markdown) shapes how I draft — technical, structured, version-controlled. Good for novels? Maybe. It keeps me focused on text rather than formatting.
- My communication tools (email + Substack) are async by design — no Slack-style presence prison. Good.
- My task management (Claude Code tasks + Google Tasks) is lightweight. No Jira-style overhead.

**The "work about work" tax:** Knowledge workers spend 60% of their day on meta-work. As a solo author-developer, I should audit this. How much time do I spend managing tools vs. doing actual work (writing, coding, marketing)?

### How I'd Implement It
1. **Run an interruption audit** on myself for one day — how many times do I context-switch between writing, coding, email, marketing? Multiply interruptions by 23 minutes.
2. **Audit my tool stack** — am I using anything that creates "work about work"? Anything I could drop or simplify?
3. **Protect deep work blocks** — write in the morning, code in the afternoon, marketing in defined windows. Don't let tools blur the boundaries.

**Effort:** One day of self-observation. Could reshape my daily schedule.

---

## 7. Anthropic Just Fixed the Biggest Hidden Cost in AI Agents (Automatic Prompt Caching)

**By:** Joe Njenga | **924 claps** | [Read on Medium](https://medium.com/ai-software-engineer/anthropic-just-fixed-the-biggest-hidden-cost-in-ai-agents-using-automatic-prompt-caching-9d47c95903c5)

### What It Is
The Claude API now automatically caches static prompt prefixes (system instructions, tool definitions, context) and reuses them across turns. Cache hits cost 10% of standard input token pricing. A 40-turn agent session with 15,000 tokens of static context goes from 600,000 billed tokens to 73,500.

### Why It Matters for Me
If I ever build API-based tools (which I'm likely to do for kdp-scout, review-miner, or other author tools), this is the difference between viable and bankrupting.

**The 5 rules from the Claude Code team:**

1. **Order prompts static-to-dynamic:** System instructions → tool definitions → project memory → session state → conversation messages. Static stuff first = maximum cache hits.

2. **Never change tools mid-session:** Adding/removing a tool breaks the entire cache prefix. Define all tools upfront.

3. **Use system messages, not prompt edits:** Every system prompt change breaks the hash. Pass updates as `<system-reminder>` tags in user messages instead.

4. **Don't switch models mid-conversation:** Caches are model-specific. Switching to "cheaper" Haiku mid-session actually costs MORE because you rebuild full context from scratch. Use subagents instead.

5. **Cache-safe compaction:** When hitting context limits, use the exact same system prompt/tools/context for compaction. Don't change anything or the cache breaks.

### How I'd Implement It
1. **For any Claude API tool I build:** Add `cache_control` at the top level of API requests. This single field enables auto-caching.
2. **Structure prompts static-to-dynamic.** Put stable instructions first, dynamic content last.
3. **Pre-define all tools at session start.** Never add/remove mid-session.
4. **When building multi-turn agents:** Stick with one model per conversation. Spawn subagents for different model needs.
5. **Keep this article bookmarked** as a reference when I start building API tools.

**Effort:** No immediate action. Critical reference for future API work.

---

## 8. The File That Made the Creator of Claude Code Go Viral

**By:** Ayesha Mughal | **77 claps** | [Read on Medium](https://medium.com/@ayeshamughal21/the-file-that-made-the-creator-of-claude-code-go-viral-e01b039e5602)

*Note: This article was taken down or redirected. Summary based on available context.*

### What It Is
About Boris Cherny's viral thread on his CLAUDE.md-driven development workflow — how a single markdown file of instructions to Claude transformed his productivity with Claude Code.

### Why It Matters for Me
I'm already living this workflow. My CLAUDE.md and MEMORY.md files are extensive and actively maintained. But the viral reception tells me something about **content opportunity:**

- There's massive appetite for "how I actually use Claude Code" content
- My setup (novelist + developer using Claude Code for both creative writing and tool building) is unusual and would stand out
- A Medium article about my workflow could drive traffic to my books and author platform

### How I'd Implement It
1. **Write a Medium article** about my Claude Code setup — the intersection of novel writing and software development. Title ideas:
   - "I Write Novels and Code with the Same AI Tool. Here's My Setup."
   - "How CLAUDE.md Turned Me into a One-Person Publishing House"
   - "The File That Runs My Entire Author Business"
2. **Include specifics:** CLAUDE.md structure, memory system, Apps Script PA, how Claude helped write/edit two novels, the tools I've built (kdp-scout, book-formatter, idea-capture)
3. **Cross-promote:** Link to books, Substack, website
4. **Timing:** This topic is hot right now (Boris's thread, multiple Medium articles about it). Strike while interest is high.

**Effort:** 2-3 hours to write. High potential ROI for platform growth.

---

## Priority Actions (Ranked by Impact/Effort)

| Priority | Action | Effort | Impact |
|---|---|---|---|
| 1 | Write "How I Use Claude Code" Medium article | 2-3 hrs | High — platform growth, book sales |
| 2 | Audit & optimize MEMORY.md (200-line rule) | 30 min | High — every future session benefits |
| 3 | Install Desktop Commander in Claude Desktop | 1 min | Medium — unlocks Cowork capabilities |
| 4 | Build Amazon book monitoring agent | 2-3 hrs | Medium — automated BSR/review tracking |
| 5 | Security audit of email triage function | 1 hr | Medium — prevent prompt injection |
| 6 | Run interruption/deep-work audit on myself | 1 day | Medium — reshape daily schedule |
| 7 | Apply prompt caching rules to future API tools | 0 (reference) | High when applicable |
| 8 | Apply OCR-first principle to document processing | 0 (principle) | Medium when applicable |
