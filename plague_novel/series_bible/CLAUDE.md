# Series Bible — AI Operating Instructions

You are maintaining the knowledge base for Randy Pellegrini's 12-book series **The Architecture of Survival**. This directory (`series_bible/`) is the wiki layer. It is AI-maintained. The raw layer is everywhere else in `plague_novel/` (chapter drafts, research, editor notes, legacy `SERIES_BIBLE_*.md` files at the repo root).

## Three layers

- **raw/** — every other folder in `plague_novel/`. Read-only from the wiki's perspective. Never rewrite chapter drafts or research docs from this directory.
- **wiki/** — `series_bible/wiki/`. You own this. Markdown only. Update freely during Ingest and Lint.
- **schema** — this file. Rules, operations, and structure.

## Three operations

The user invokes these by name. Respond to the exact verb.

### Ingest

Trigger: "ingest \<path\>" or "I finished \<thing\>, update the wiki".

1. Read the new raw doc (chapter draft, research note, editor pass, cover, launch plan — whatever).
2. Diff against `wiki/index.md` to find entities the doc touches: characters, factions, locations, timeline events, glossary terms, book-level canon.
3. For each touched entity, update its page under `wiki/characters/`, `wiki/factions/`, etc. Create the page if it doesn't exist and add a row to `wiki/index.md`.
4. Update `wiki/overview.md` if book-level status changed (draft complete, published, in edits).
5. Append one line to `wiki/log.md`: `## [YYYY-MM-DD] ingest | <source> → <entities touched>`.
6. Do **not** summarize raw content into the wiki verbatim — extract facts and link back with `raw: <relative path>`.

### Query

Trigger: a question ("when did X happen?", "who knows Y by book 4?", "what's the current status of Z?").

1. Read `wiki/`, not raw. The wiki is the answer layer.
2. If the wiki doesn't know, say so. Then offer to ingest the raw doc that would answer it.
3. If the answer is non-obvious and likely to be asked again, add it as a new page or expand an existing one before responding. Log the addition.

### Lint

Trigger: "lint the wiki" or "find contradictions".

1. Scan every wiki page for: contradictions across entity pages, orphaned pages (not in `index.md`), stale status (book marked "in drafting" when `overview.md` says published), dangling references (page links to an entity that doesn't exist).
2. Output a lint report. Do not auto-fix contradictions — surface them for the user to resolve.
3. Auto-fix safe items only: missing index entries, fixable broken links within the wiki.

## Structure

```
series_bible/
├── CLAUDE.md              (this file)
└── wiki/
    ├── index.md           catalog of every entity; single source of truth for what exists
    ├── log.md             chronological ingest record
    ├── overview.md        12-book arc status, canon vs planned
    ├── glossary.md        cross-book terminology
    ├── characters/<name>.md
    ├── factions/<name>.md
    ├── locations/<name>.md
    └── timeline/<event>.md
```

## Migration from legacy files

The root-level `SERIES_BIBLE_*.md` files predate this system. Treat them as raw sources for the first ingest pass. After ingesting, they should either be (a) moved into `wiki/` as structured pages, or (b) left in place and linked from the wiki as historical reference. Do not delete them.

Legacy files to ingest first:
- `SERIES_BIBLE_master_timeline.md` → `wiki/timeline/`
- `SERIES_BIBLE_terminology_glossary.md` → `wiki/glossary.md`
- `SERIES_BIBLE_bloodline_tracker.md` → `wiki/characters/` (per-bloodline)
- `SERIES_BIBLE_seven_keys_tracker.md` → `wiki/` as `seven_keys.md` or under a new `artifacts/` folder
- `SERIES_BIBLE_network_evolution.md` → `wiki/factions/`
- `SERIES_BIBLE_system_dynamics.md`, `SERIES_BIBLE_collapse_and_rise.md` → `wiki/overview.md` appendices
- `SERIES_BIBLE_continuity_gaps.md` → surface during first Lint run

## Rules

- Markdown only. No JSON, no YAML frontmatter unless a page needs structured fields.
- Link with relative paths: `[Aethelred](characters/aethelred.md)`.
- Every entity page opens with a one-line description, then sections per book it appears in.
- Never invent canon. If raw is silent on a fact, the wiki is silent.
- Date format: `YYYY-MM-DD`. Convert relative dates on ingest.
