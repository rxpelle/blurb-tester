# Book 2: Genesis Protocol - Special Notes

**Book 2 has a DIFFERENT file structure from other books!**

---

## File Structure

### Book 2 (Single Manuscript File):
```
book_2_genesis_protocol/
├── BOOK_2_REVISION_v11.md          ← CURRENT MANUSCRIPT (single file)
├── manuscript/chapters/           ← Working drafts & revision history
│   ├── chapter_1_PHASE1_REWRITE.md
│   ├── chapter_2_PHASE1_MAYA.md
│   └── [various other versions]
└── [no BOOK_BASELINE.md yet]
```

### Other Books (Individual Chapter Files):
```
book_1_aethelred_cipher/
├── BOOK_BASELINE.md               ← Generated summary
└── manuscript/chapters/           ← Individual chapter files (CANONICAL)
    ├── chapter_01_prologue.md
    ├── chapter_02_discovery.md
    └── [etc.]
```

---

## Working with Book 2

### Reading the Manuscript:
```bash
# Book 2 is in a SINGLE file:
cat book_2_genesis_protocol/BOOK_2_REVISION_v11.md

# NOT in individual chapters like other books
```

### Current Status (as of 2026-01-27):
- **Version:** v11
- **Status:** Emotional depth enhanced - opening hook 9/10, personal stakes added, climax strengthened
- **Structure:** Single manuscript file (not broken into chapters)
- **Word count:** ~50,000 words
- **Chapters:** Prologue + Chapters 1-21 (renumbered from decimal system)

### Version 11 (Latest) Changes:
- Opening hook: Sharpened first 3 pages, added Morrison's doubt, fixed Emily continuity
- Emotional grounding: Added Linda Hwang (Sarah's mentor killed by Order), Melissa confrontation
- Climax effectiveness: Morrison's trial breakdown - raw emotional collapse vs. clinical admission
- Scores: Opening 9/10, Emotional grounding 9.5/10, Climax 9.75/10

### Version 10 Changes:
- Dialogue efficiency: Tightened Morrison exposition, compressed internal monologues
- Concept accessibility: Improved "genetic predisposition" explanation for clarity
- Genre alignment: Achieved 9/10 for Intellectual Historical Thriller standards
- Removed exposition tennis and emotional annotations

### Version 9 Changes:
- All dates corrected from 2025 → 2019
- Character ages aligned with 2019 timeline
- Chapter reordering: Chapter 4 moved before Chapter 3
- All chapters renumbered sequentially (removed decimals like 1.5, 3.5)
- Morrison timeline fixed
- Timeline: November 14, 2019 (Prologue) → December 2019 (climax)

---

## Why Book 2 is Different

Book 2 went through extensive commercial revision ("NYT BESTSELLER REVISION") which resulted in a consolidated manuscript file rather than individual chapters. The `manuscript/chapters/` directory contains:
- Working drafts from revision phases
- Alternative versions (PHASE1, PHASE2, ACCESSIBLE, etc.)
- Enhancement attempts
- Revision history

**The CANONICAL version is:** `BOOK_2_REVISION_v11.md`

---

## Generating Book 2 Baseline

**IMPORTANT:** Book 2 currently has NO baseline file. The baseline system expects individual chapter files, but Book 2 is a single file.

### Options:

1. **Split Book 2 into individual chapters:**
   - Extract each chapter from BOOK_2_REVISION_v11.md
   - Save as individual files: chapter_01_prologue.md, chapter_02_*.md, etc.
   - Then run: `python3 generate_baseline.py book_2_genesis_protocol`

2. **Keep as single file:**
   - Treat BOOK_2_REVISION_v11.md as the "baseline"
   - No auto-generation needed (file IS the truth)
   - May need to manually update series index

---

## Recommended Workflow for Book 2

### Session Start:
```
1. Read _reference/START_HERE.md
2. Read _reference/core/01_SERIES_INDEX.md
3. Read book_2_genesis_protocol/BOOK_2_REVISION_v11.md (entire manuscript)
   OR read specific chapters if working on specific sections
```

### Making Edits:
```
1. Edit BOOK_2_REVISION_v11.md directly
2. Update version number (v10 → v11, etc.)
3. Document changes at top of file
4. Consider: Should Book 2 be split into chapters like other books?
```

### After Edits:
```
If keeping single file format:
- Manually note changes in series index
- No baseline generation needed

If splitting into chapters:
- Extract chapters from v9 file
- Save as individual chapter files
- Run generate_baseline.py
- Run generate_series_index.py
```

---

## For Claude: Book 2 Context Loading

**When user asks to work on Book 2:**

```
# Load the entire manuscript:
cat book_2_genesis_protocol/BOOK_2_REVISION_v11.md

# OR load specific sections (faster):
cat book_2_genesis_protocol/BOOK_2_REVISION_v11.md | head -500  # Prologue + Ch 1
```

**Key info to extract:**
- Current version number (top of file)
- Timeline: November 14, 2019 → December 2019
- Main character: Sarah Chen
- Antagonist: Dr. James Morrison
- Plot: Genesis Protocol activation to stop THRESHOLD deployment
- Structure: Prologue + 21 chapters

---

## Decision Point for User

**Should Book 2 be restructured to match other books?**

### Pros of splitting into chapters:
- ✅ Consistent with Books 1, 4, 5, 6
- ✅ Easier to edit individual chapters
- ✅ Baseline system works automatically
- ✅ Better version control

### Cons:
- ❌ Requires one-time splitting work
- ❌ May disrupt current workflow
- ❌ Need to archive current single-file format

### Recommendation:
Split Book 2 into chapters to match series structure. This creates consistency and allows the baseline system to work properly.

---

**Last Updated:** 2026-01-27 (v11 - emotional depth enhancements complete)
