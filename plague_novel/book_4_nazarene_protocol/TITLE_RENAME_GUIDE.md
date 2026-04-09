# Book 4 Title Rename: "The Nazarene Protocol" → "Love Remembers in Silence"

**Date:** 2026-04-08
**Decision:** Randy Pellegrini confirmed new title during brainstorming session

---

## Files Requiring Content Changes

### Manuscript Directory
`/Users/randypellegrini/Documents/antigravity/plague_novel/book_4_nazarene_protocol/`

| File | Line(s) | Current Text | New Text |
|------|---------|-------------|----------|
| `README.md` | 1 | `# Book 4: The Nazarene Protocol` | `# Book 4: Love Remembers in Silence` |
| `.baseline_config.json` | 3 | `"book_title": "The Nazarene Protocol"` | `"book_title": "Love Remembers in Silence"` |
| `PROGRESS_SUMMARY.md` | 1+ | References to "The Nazarene Protocol" | "Love Remembers in Silence" |
| `REVISION_PLAN.md` | 1 | `# The Nazarene Protocol — Revision Plan` | `# Love Remembers in Silence — Revision Plan` |
| `ORGANIZATION_GUIDE.md` | 11, 157 | `The Nazarene Protocol` | `Love Remembers in Silence` |
| `CROSS_BOOK_REVIEW_SUMMARY.md` | 10 | `"The Nazarene Protocol"` | `"Love Remembers in Silence"` |
| `EDITORIAL_CHECKLIST.md` | multiple | `The Nazarene Protocol` | `Love Remembers in Silence` |
| `BOOK_BASELINE.md` | 1, 3 | `The Nazarene Protocol` | `Love Remembers in Silence` |
| `nyt_review_scores.md` | 1 | `# The Nazarene Protocol — King-Pass Review Scores` | `# Love Remembers in Silence — King-Pass Review Scores` |

### Review JSON Files (34 files)
`manuscript/chapters/reviews/` and `manuscript/chapters/reviews/king_pass/`
- All chapter review JSON files reference `book_4_nazarene_protocol` in path fields
- These are internal paths and may not need changing unless the directory is renamed

### Planning & Archive Files
| File | Location |
|------|----------|
| `archive/session_notes/NEW_SESSION_PROMPT.md` | Lines 1, 99-116 |
| `archive/session_notes/SESSION_CONTEXT_chapter_10_in_progress.md` | Line 333 |
| `archive/session_notes/REORGANIZATION_COMPLETE.md` | Lines 15, 36-46, 82 |

---

## Agent/Config Files

### Clawd Main
| File | Line(s) | Current Text | New Text |
|------|---------|-------------|----------|
| `/Users/randypellegrini/clawd/DOMAIN-KNOWLEDGE.md` | 17 | `The Nazarene Protocol` | `Love Remembers in Silence` |

### Claude Project Memory
| File | Line(s) | Current Text | New Text |
|------|---------|-------------|----------|
| `~/.claude/projects/-Users-randypellegrini-clawd/memory/MEMORY.md` | 33 | `**Book 4: The Nazarene Protocol**` | `**Book 4: Love Remembers in Silence**` |
| `~/.claude/projects/-Users-randypellegrini-Documents-antigravity/memory/MEMORY.md` | 61, 63 | `The Nazarene Protocol` | `Love Remembers in Silence` |

---

## Website
| File | Notes |
|------|-------|
| `randypellegrini.com` source | Check for any book listing pages referencing the title |
| `_site/the-nazarene-protocol/` | Eleventy-generated cache — will regenerate on next build |

---

## Cover Generator Output
| File | Action |
|------|--------|
| `cover-generator/output/locked/the-nazarene-protocol-ebook-FINAL.png` | Keep file as-is (locked cover art) — regenerate with new title text |
| `cover-generator/output/locked/the-nazarene-protocol-bg-LOCKED.png` | Keep (background image, no title text) |
| All other `the-nazarene-protocol-*` files in output/ | Old variants, can be cleaned up |

---

## Directory Rename (Optional)
The manuscript directory is currently named `book_4_nazarene_protocol`. Renaming to `book_4_love_remembers_in_silence` would:
- Break 34+ JSON review file path references
- Require updating Google Drive sync paths
- Require updating any scripts referencing this path

**Recommendation:** Keep directory name as `book_4_nazarene_protocol` for now. The directory name is internal infrastructure, not reader-facing. Add a note in README.md explaining the rename.

---

## KDP / Amazon
- Update book title in KDP manuscript upload
- Update book title in KDP metadata
- Update any Amazon Ads campaigns referencing the title

---

## Series Title List (Updated)
| Book | Title |
|------|-------|
| Book 1 | The Aethelred Cipher |
| Book 2 | The Genesis Protocol |
| Book 3 | The First Key |
| **Book 4** | **Love Remembers in Silence** |
| Book 5 | The Augustine Protocol |

---

## Notes
- The new title intentionally breaks the "The [X] [Y]" naming pattern of the series — this is appropriate because Book 4 is where the series mythology breaks its own pattern (the first carrier who doesn't need bronze keys)
- The title emphasizes love/spirituality over religion/dogma, which aligns with the book's core thesis
- Directory name `book_4_nazarene_protocol` retained for infrastructure stability
