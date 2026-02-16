# Session Start Protocol for Plague Novel Series

**Purpose**: Ensure every new AI session starts with accurate, up-to-date information from actual manuscript files rather than stale outlines or memory.

---

## 🚨 CRITICAL: Read This First in Every New Session

This series uses a **two-tier baseline system** to maintain canonical source of truth:

1. **BOOK_BASELINE.md** (in each book directory) - Generated from actual chapters
2. **CANONICAL_SERIES_INDEX.md** (root) - Synced from all book baselines

**NEVER trust**:
- Old outline files
- Previous session memory
- Summary documents without verification checksums
- Any document contradicting a BOOK_BASELINE.md file

---

## Step 1: Session Initialization (ALWAYS DO THIS FIRST)

### When Starting ANY New Session:

```bash
# 1. Read the series index first
cat CANONICAL_SERIES_INDEX.md

# 2. Check baseline dates - are they current?
grep "Last Updated" CANONICAL_SERIES_INDEX.md

# 3. If working on a specific book, read its baseline
cat book_1_aethelred_cipher/BOOK_BASELINE.md

# 4. Note the verification checksum
grep "Checksum" book_1_aethelred_cipher/BOOK_BASELINE.md
```

### Quick Verification Checklist:

- [ ] Read CANONICAL_SERIES_INDEX.md
- [ ] Check "Last Updated" date on relevant BOOK_BASELINE.md
- [ ] If baseline is >7 days old during active editing, regenerate it
- [ ] Note verification checksums
- [ ] Understand which book(s) you'll be working on

---

## Step 2: Before Making Any Changes

### Working on a Specific Book:

```bash
# 1. Read the book's baseline
cat book_X_name/BOOK_BASELINE.md

# 2. If you need specific details, read actual chapters
cat book_X_name/manuscript/chapters/chapter_3_*.md

# 3. NEVER assume - always verify from source files
```

### Key Questions to Ask Yourself:

- ❓ What does the BOOK_BASELINE.md say about this?
- ❓ When was this baseline last generated?
- ❓ Do I need to read the actual chapter to verify?
- ❓ Have I checked for contradictions with the series index?

---

## Step 3: After Making Changes

### Always Regenerate Baselines:

```bash
# 1. Regenerate the specific book's baseline
python3 generate_baseline.py book_X_name

# 2. Update the series index
python3 generate_series_index.py

# 3. Verify checksums changed
grep "Checksum" book_X_name/BOOK_BASELINE.md
```

### What Changed:

Document your changes in the session:
- Which chapters were modified?
- What continuity impacts exist?
- Which other books might be affected?

---

## Source of Truth Hierarchy

**Use this hierarchy when researching or verifying information:**

### 1️⃣ HIGHEST AUTHORITY: Actual Chapter Files
- Location: `book_X_name/manuscript/chapters/*.md`
- These are the ultimate source of truth
- Everything else derives from these

### 2️⃣ SECOND: Individual BOOK_BASELINE.md
- Location: `book_X_name/BOOK_BASELINE.md`
- Auto-generated from chapters
- Includes verification checksum
- Check "Last Updated" date

### 3️⃣ THIRD: CANONICAL_SERIES_INDEX.md
- Location: Root directory
- Synced from all book baselines
- Good for cross-book continuity
- Check "Last Updated" date

### ❌ DO NOT TRUST:
- `BOOK_X_OUTLINE_*.md` files (outdated)
- `SERIES_BIBLE_*.md` files (unless dated after baselines)
- Summary documents without checksums
- Your memory of previous sessions
- Any document contradicting a baseline

---

## Common Scenarios

### Scenario 1: "Which book contains the Pattern Eye discovery?"

```bash
# Check series index first
grep -A 5 "Pattern Eye" CANONICAL_SERIES_INDEX.md

# Then read specific book baseline
cat book_1_aethelred_cipher/BOOK_BASELINE.md | grep -A 3 "Pattern Eye"

# If still uncertain, read actual chapter
cat book_1_aethelred_cipher/manuscript/chapters/chapter_3_*.md
```

### Scenario 2: "What happens in Book 2, Chapter 5?"

```bash
# Read book baseline chapter summary
cat book_2_genesis_protocol/BOOK_BASELINE.md | grep -A 20 "Chapter 5"

# For full detail, read the actual chapter
cat book_2_genesis_protocol/manuscript/chapters/chapter_5_*.md
```

### Scenario 3: "Is there a continuity conflict between Books 1 and 3?"

```bash
# Check series index for cross-book info
cat CANONICAL_SERIES_INDEX.md

# Read both book baselines
cat book_1_aethelred_cipher/BOOK_BASELINE.md | grep "Seven Keys"
cat book_3_first_key/BOOK_BASELINE.md | grep "Seven Keys"

# Read actual chapters if baseline summaries unclear
```

### Scenario 4: "I'm starting a new session after 2 weeks"

```bash
# 1. Check if baselines are stale
ls -l book_*/BOOK_BASELINE.md

# 2. If edited recently, regenerate all
python3 generate_baseline.py --all
python3 generate_series_index.py

# 3. Read the updated series index
cat CANONICAL_SERIES_INDEX.md
```

---

## Baseline Regeneration Guide

### When to Regenerate:

**ALWAYS regenerate after:**
- Modifying any chapter file
- Adding new chapters
- Fixing continuity issues
- Merging changes from another session

**CONSIDER regenerating if:**
- Baseline is >7 days old during active editing
- Checksum seems wrong
- Summary doesn't match your memory of the text

### How to Regenerate:

```bash
# Single book (fastest)
python3 generate_baseline.py book_1_aethelred_cipher

# Multiple specific books
python3 generate_baseline.py book_1_aethelred_cipher
python3 generate_baseline.py book_2_genesis_protocol

# All books (slow, use when many books changed)
python3 generate_baseline.py --all

# Always update series index after
python3 generate_series_index.py
```

---

## Metadata Headers (Optional Enhancement)

Some chapters have YAML frontmatter metadata:

```yaml
---
book: 1
chapter: 3
title: "The Pattern Eye"
date_written: 1002 CE
pov_character: Godric
key_events:
  - Pattern Eye discovered in Cretan ruins
  - Godric realizes connection to larger system
seven_keys:
  - Pattern Eye
continuity_tags:
  - seven_keys:pattern_eye:discovered
  - character:godric:revelation_moment
---
```

### Adding Metadata to a Chapter:

```bash
python3 add_metadata_header.py \
  book_1_aethelred_cipher/manuscript/chapters/chapter_3_medieval_REVISED.md \
  --chapter 3 \
  --title "The Pattern Eye" \
  --date "1002 CE" \
  --pov "Godric" \
  --key-events "Pattern Eye discovered" "Connection to larger system revealed"
```

**Note**: Metadata is optional but helpful. The baseline generator will extract it automatically if present.

---

## Quick Reference Commands

```bash
# Read series index
cat CANONICAL_SERIES_INDEX.md

# Read specific book baseline
cat book_1_aethelred_cipher/BOOK_BASELINE.md

# Regenerate single book baseline
python3 generate_baseline.py book_1_aethelred_cipher

# Regenerate all book baselines
python3 generate_baseline.py --all

# Update series index
python3 generate_series_index.py

# Add metadata to chapter
python3 add_metadata_header.py path/to/chapter.md --chapter N --title "Title"

# Search for Seven Keys across series
grep -r "Pattern Eye" book_*/BOOK_BASELINE.md

# Find which chapters are most recent
ls -lt book_*/manuscript/chapters/*.md | head -10

# Verify baseline checksums
grep "Checksum" book_*/BOOK_BASELINE.md
```

---

## Session End Checklist

Before ending a session:

- [ ] Regenerated baselines for all modified books
- [ ] Updated CANONICAL_SERIES_INDEX.md
- [ ] Documented major changes in session notes
- [ ] Verified no contradictions introduced
- [ ] Committed changes with clear commit message

---

## Files Overview

```
plague_novel/
├── CANONICAL_SERIES_INDEX.md          ← Series-level index (READ FIRST)
├── SESSION_START_PROTOCOL.md          ← This file
├── generate_baseline.py               ← Generate book baselines
├── generate_series_index.py           ← Generate series index
├── add_metadata_header.py             ← Add YAML metadata to chapters
│
├── book_1_aethelred_cipher/
│   ├── BOOK_BASELINE.md               ← Book 1 canonical baseline
│   ├── .baseline_config.json          ← Book 1 metadata
│   ├── BOOK_1_OUTLINE_*.md            ← OLD (don't trust)
│   └── manuscript/chapters/           ← ACTUAL SOURCE OF TRUTH
│
├── book_2_genesis_protocol/
│   ├── BOOK_BASELINE.md               ← Book 2 canonical baseline
│   ├── .baseline_config.json          ← Book 2 metadata
│   └── manuscript/chapters/           ← ACTUAL SOURCE OF TRUTH
│
[... more books ...]
```

---

## Emergency: Baseline Seems Wrong

If a baseline seems incorrect:

1. **Don't panic** - baselines are auto-generated, easy to fix
2. **Read the actual chapter** to verify truth
3. **Regenerate the baseline**: `python3 generate_baseline.py book_X_name`
4. **Check if chapter was recently modified**: `ls -l book_X_name/manuscript/chapters/`
5. **Report the issue** in session notes

---

## Tips for Success

✅ **DO:**
- Always read CANONICAL_SERIES_INDEX.md first
- Verify with baselines before making changes
- Regenerate baselines after every chapter edit
- Read actual chapters when in doubt
- Document your changes

❌ **DON'T:**
- Trust old outline files
- Rely on memory from previous sessions
- Skip baseline regeneration
- Assume continuity without checking
- Make changes without reading baselines first

---

**Last Updated**: 2026-01-17
**Version**: 1.0
**Maintenance**: Update this protocol if baseline system changes
