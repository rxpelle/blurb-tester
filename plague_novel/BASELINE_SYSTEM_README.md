# Plague Novel Series - Baseline System Documentation

**Version**: 1.0
**Created**: 2026-01-17
**Purpose**: Prevent AI sessions from using stale outlines instead of actual manuscript content

---

## The Problem This Solves

When starting new AI sessions, the assistant would:
- Read old outline files that no longer matched the actual books
- Create continuity errors based on stale information
- Not re-read the actual chapter files
- Make assumptions from previous session memory

**Solution**: A two-tier canonical baseline system that auto-generates documentation directly from manuscript files.

---

## System Overview

### Two-Tier Architecture:

```
ACTUAL CHAPTERS (source of truth)
        ↓
    [extract & analyze]
        ↓
BOOK_BASELINE.md (per book)
        ↓
    [aggregate & cross-reference]
        ↓
CANONICAL_SERIES_INDEX.md (series level)
```

### Key Files:

1. **BOOK_BASELINE.md** (in each book directory)
   - Auto-generated from actual chapter files
   - Contains chapter summaries, character lists, timeline events
   - Includes verification checksum
   - Updated whenever chapters change

2. **CANONICAL_SERIES_INDEX.md** (root directory)
   - Aggregates all book baselines
   - Cross-book continuity tracking
   - Seven Keys custody chain
   - Series timeline

3. **SESSION_START_PROTOCOL.md** (root directory)
   - Instructions for AI assistants
   - How to start each new session correctly
   - Verification procedures

---

## Quick Start

### Generate Baselines for the First Time:

```bash
# 1. Generate individual book baselines
python3 generate_baseline.py book_1_aethelred_cipher
python3 generate_baseline.py book_2_genesis_protocol
python3 generate_baseline.py book_3_first_key

# OR generate all at once (slower)
python3 generate_baseline.py --all

# 2. Generate series index
python3 generate_series_index.py

# 3. Read the results
cat CANONICAL_SERIES_INDEX.md
cat book_1_aethelred_cipher/BOOK_BASELINE.md
```

### Daily Workflow:

```bash
# When you modify a chapter:
# 1. Edit the chapter file
vim book_1_aethelred_cipher/manuscript/chapters/chapter_3_medieval_REVISED.md

# 2. Regenerate that book's baseline
python3 generate_baseline.py book_1_aethelred_cipher

# 3. Update series index
python3 generate_series_index.py

# Done! Baselines are now current.
```

---

## File Structure

```
plague_novel/
│
├── CANONICAL_SERIES_INDEX.md          ← Read this first in every session
├── SESSION_START_PROTOCOL.md          ← How to use this system
├── BASELINE_SYSTEM_README.md          ← This file
│
├── generate_baseline.py               ← Script: Generate book baselines
├── generate_series_index.py           ← Script: Generate series index
├── add_metadata_header.py             ← Script: Add YAML metadata to chapters
│
├── book_1_aethelred_cipher/
│   ├── BOOK_BASELINE.md               ← Generated from chapters (DO NOT EDIT)
│   ├── .baseline_config.json          ← Book metadata (EDIT THIS)
│   ├── BOOK_1_OUTLINE_*.md            ← OLD - Don't trust
│   └── manuscript/
│       └── chapters/
│           ├── chapter_1_medieval_REVISED.md    ← SOURCE OF TRUTH
│           ├── chapter_2_medieval_REVISED.md
│           └── ...
│
├── book_2_genesis_protocol/
│   ├── BOOK_BASELINE.md
│   ├── .baseline_config.json
│   └── manuscript/chapters/
│
└── [more books...]
```

---

## Scripts Documentation

### 1. generate_baseline.py

**Purpose**: Extract information from actual chapter files and create BOOK_BASELINE.md

**Usage**:
```bash
# Single book
python3 generate_baseline.py book_1_aethelred_cipher

# All books
python3 generate_baseline.py --all
```

**What it extracts**:
- Chapter titles and word counts
- Character mentions (names appearing 3+ times)
- Dates mentioned (BCE/CE years)
- Seven Keys references
- Key plot moments (sentences with action keywords)
- YAML metadata (if present in chapter headers)

**Output**: `book_X_name/BOOK_BASELINE.md`

**Verification**: Includes SHA256 checksum of all chapters

---

### 2. generate_series_index.py

**Purpose**: Aggregate all book baselines into series-level index

**Usage**:
```bash
python3 generate_series_index.py
```

**What it creates**:
- Book status table (complete, in progress, missing baseline)
- Seven Keys custody chain across all books
- Major characters per book
- Series timeline
- Cross-references between books

**Output**: `CANONICAL_SERIES_INDEX.md`

**Run after**: Generating or updating any book baseline

---

### 3. add_metadata_header.py

**Purpose**: Add structured YAML metadata to chapter files (optional)

**Usage**:
```bash
python3 add_metadata_header.py \
  book_1_aethelred_cipher/manuscript/chapters/chapter_1_medieval_REVISED.md \
  --chapter 1 \
  --title "The Key" \
  --date "1347 CE" \
  --pov "Thomas (scribe)" \
  --key-events "Brother Hamo murdered" "Thomas finds cipher"
```

**What it does**:
- Adds YAML frontmatter to chapter file
- Creates backup (.md.backup) before modifying
- Metadata gets auto-extracted by baseline generator

**Example metadata**:
```yaml
---
book: 1
chapter: 1
title: The Key
date_written: 1347 CE
pov_character: Thomas (scribe/cipher keeper)
key_events:
  - Brother Hamo murdered
  - Thomas finds grandfather Wilhelm's cipher
  - Meeting with Margarethe (Network contact)
---
```

---

## Configuration Files

### .baseline_config.json

Located in each book directory. Provides metadata for baseline generation.

**Example**:
```json
{
  "book_number": 1,
  "book_title": "The Aethelred Cipher",
  "status": "complete",
  "time_period": "1002-1016 CE (Anglo-Saxon England)",
  "pov_character": "Godric (monk and scribe)",
  "key_themes": [
    "Discovery of the Pattern Eye",
    "Anglo-Saxon collapse",
    "Monastic scholarship"
  ],
  "seven_keys_status": {
    "Pattern Eye": "discovered and acquired by Godric"
  }
}
```

**When to edit**:
- Setting up a new book
- Updating book status
- Changing POV character
- Adding key themes

**When to regenerate baseline after editing**: Always

---

## Workflows

### Workflow 1: Starting a New Session

```bash
# 1. Read series index
cat CANONICAL_SERIES_INDEX.md

# 2. Check when baselines were last generated
grep "Last Updated" book_*/BOOK_BASELINE.md

# 3. If stale (>7 days during active editing), regenerate
python3 generate_baseline.py --all
python3 generate_series_index.py

# 4. Read the baseline for the book you're working on
cat book_1_aethelred_cipher/BOOK_BASELINE.md
```

### Workflow 2: Modifying a Chapter

```bash
# 1. Read the current baseline
cat book_1_aethelred_cipher/BOOK_BASELINE.md | grep -A 20 "Chapter 3"

# 2. Make your changes
vim book_1_aethelred_cipher/manuscript/chapters/chapter_3_medieval_REVISED.md

# 3. Regenerate baseline
python3 generate_baseline.py book_1_aethelred_cipher

# 4. Update series index
python3 generate_series_index.py

# 5. Verify checksum changed
grep "Checksum" book_1_aethelred_cipher/BOOK_BASELINE.md
```

### Workflow 3: Adding a New Chapter

```bash
# 1. Create the chapter file
vim book_1_aethelred_cipher/manuscript/chapters/chapter_12_medieval_REVISED.md

# 2. (Optional) Add metadata header
python3 add_metadata_header.py \
  book_1_aethelred_cipher/manuscript/chapters/chapter_12_medieval_REVISED.md \
  --chapter 12 \
  --title "The Resolution" \
  --date "1348 CE"

# 3. Regenerate baseline (will auto-detect new chapter)
python3 generate_baseline.py book_1_aethelred_cipher

# 4. Update series index
python3 generate_series_index.py
```

### Workflow 4: Checking Continuity Across Books

```bash
# 1. Search for a specific element
grep -r "Pattern Eye" book_*/BOOK_BASELINE.md

# 2. Check Seven Keys custody in series index
cat CANONICAL_SERIES_INDEX.md | grep -A 20 "Seven Keys Custody"

# 3. If discrepancy found, read actual chapters
cat book_1_aethelred_cipher/manuscript/chapters/chapter_3_*.md | grep "Pattern Eye"
cat book_2_genesis_protocol/manuscript/chapters/chapter_5_*.md | grep "Pattern Eye"

# 4. After fixing, regenerate both baselines
python3 generate_baseline.py book_1_aethelred_cipher
python3 generate_baseline.py book_2_genesis_protocol
python3 generate_series_index.py
```

---

## Verification & Quality Control

### Checksum Verification

Each baseline includes a SHA256 checksum of all chapters:

```bash
# View current checksum
grep "Checksum" book_1_aethelred_cipher/BOOK_BASELINE.md

# After modifying a chapter, regenerate and compare
python3 generate_baseline.py book_1_aethelred_cipher
grep "Checksum" book_1_aethelred_cipher/BOOK_BASELINE.md

# If checksum didn't change, chapters weren't modified
```

### Baseline Freshness

```bash
# Check when baselines were last generated
ls -l book_*/BOOK_BASELINE.md

# Check specific book
stat book_1_aethelred_cipher/BOOK_BASELINE.md

# If older than chapter files, baseline is stale
ls -lt book_1_aethelred_cipher/manuscript/chapters/*.md | head -1
```

### Manual Verification

```bash
# Compare baseline summary to actual chapter
cat book_1_aethelred_cipher/BOOK_BASELINE.md | grep -A 30 "Chapter 3"
cat book_1_aethelred_cipher/manuscript/chapters/chapter_3_medieval_REVISED.md | head -50

# Count words in baseline vs actual
grep "Word Count" book_1_aethelred_cipher/BOOK_BASELINE.md
wc -w book_1_aethelred_cipher/manuscript/chapters/chapter_3_medieval_REVISED.md
```

---

## Troubleshooting

### Problem: Baseline seems incorrect

**Solution**:
```bash
# 1. Verify chapters haven't changed
ls -lt book_1_aethelred_cipher/manuscript/chapters/

# 2. Regenerate baseline
python3 generate_baseline.py book_1_aethelred_cipher

# 3. Read actual chapter to verify
cat book_1_aethelred_cipher/manuscript/chapters/chapter_X_*.md
```

### Problem: Script fails with "No module named yaml"

**Solution**:
```bash
# Install PyYAML
pip3 install pyyaml

# Or use system package manager
# Mac: brew install pyyaml
# Linux: apt-get install python3-yaml
```

### Problem: Character extraction picking up wrong words

**Solution**:
The script filters out common words (The, Chapter, He, She). To improve:

1. Edit `generate_baseline.py`
2. Add more exclusions to the filter list (around line 88)
3. Regenerate baselines

### Problem: Baseline missing important info

**Solution**:
Add YAML metadata to chapters for better extraction:

```bash
python3 add_metadata_header.py chapter_file.md \
  --chapter N \
  --title "Title" \
  --key-events "Event 1" "Event 2"
```

---

## Best Practices

### ✅ DO:

1. **Regenerate baselines after every chapter edit**
   ```bash
   python3 generate_baseline.py book_X_name
   python3 generate_series_index.py
   ```

2. **Check baselines before making changes**
   ```bash
   cat book_1_aethelred_cipher/BOOK_BASELINE.md
   ```

3. **Verify with actual chapters when uncertain**
   ```bash
   cat book_1_aethelred_cipher/manuscript/chapters/chapter_3_*.md
   ```

4. **Keep .baseline_config.json files updated**
   - Edit when book status changes
   - Update POV character if it changes
   - Add new themes as they emerge

5. **Add metadata to important chapters**
   - Especially chapters with major plot points
   - Chapters where Seven Keys appear
   - Chapters with character introductions

### ❌ DON'T:

1. **Don't manually edit BOOK_BASELINE.md**
   - It will be overwritten on next generation
   - Edit source chapters or .baseline_config.json instead

2. **Don't trust old outline files**
   - They're kept for reference but are outdated
   - Always check baselines first

3. **Don't skip baseline regeneration**
   - Stale baselines lead to continuity errors
   - Regeneration is fast (< 10 seconds per book)

4. **Don't commit without updating baselines**
   - If you modified chapters, update baselines
   - Include baseline updates in the same commit

---

## Integration with Git

### Recommended Git Workflow:

```bash
# 1. Make chapter changes
vim book_1_aethelred_cipher/manuscript/chapters/chapter_3_medieval_REVISED.md

# 2. Regenerate baselines
python3 generate_baseline.py book_1_aethelred_cipher
python3 generate_series_index.py

# 3. Commit everything together
git add book_1_aethelred_cipher/manuscript/chapters/chapter_3_medieval_REVISED.md
git add book_1_aethelred_cipher/BOOK_BASELINE.md
git add CANONICAL_SERIES_INDEX.md
git commit -m "Book 1, Ch 3: [description of changes]

- Modified chapter 3 to [what you changed]
- Regenerated Book 1 baseline (checksum: [new checksum])
- Updated series index"
```

### .gitignore Recommendations:

```gitignore
# Don't ignore baselines - they should be committed
# BOOK_BASELINE.md files track with the repo

# Do ignore backups created by metadata script
*.md.backup

# Do ignore Python cache
__pycache__/
*.pyc
```

---

## Advanced Usage

### Batch Add Metadata to Multiple Chapters:

```bash
# For each chapter in a book
for i in {1..10}; do
  python3 add_metadata_header.py \
    book_1_aethelred_cipher/manuscript/chapters/chapter_${i}_medieval_REVISED.md \
    --chapter $i \
    --title "Chapter $i Title" \
    --date "1347 CE"
done

# Then regenerate baseline to extract all metadata
python3 generate_baseline.py book_1_aethelred_cipher
```

### Generate Baselines for Subset of Books:

```bash
# Books 1-3 only
for book in book_1_aethelred_cipher book_2_genesis_protocol book_3_first_key; do
  python3 generate_baseline.py $book
done

python3 generate_series_index.py
```

### Custom Extraction (modify scripts):

Edit `generate_baseline.py` to extract custom information:
- Line 45-50: Modify keyword lists
- Line 80-150: Add new extraction functions
- Line 200+: Modify output format

---

## Future Enhancements

Potential improvements to the system:

1. **Automated verification**:
   - Script to verify no continuity conflicts
   - Cross-reference Seven Keys custody chain
   - Timeline consistency checker

2. **Better character tracking**:
   - Track character relationships
   - Character arc summaries
   - Character appearances across books

3. **Plot thread tracking**:
   - Extract plot threads from chapters
   - Track thread resolution
   - Find dangling plot threads

4. **Git hooks**:
   - Auto-regenerate baselines on chapter commits
   - Prevent commits without baseline updates
   - Verify checksums before push

5. **Web interface**:
   - Browse baselines in web browser
   - Search across all books
   - Visual timeline

---

## Support & Maintenance

### Reporting Issues:

If scripts fail or baselines seem incorrect:

1. Note which script failed
2. Note the error message
3. Check Python version: `python3 --version`
4. Check dependencies: `pip3 list | grep -i yaml`

### Updating Scripts:

If you modify the generation scripts:

1. Test on one book first
2. Regenerate all baselines with new version
3. Compare old vs new checksums
4. Document changes in git commit

---

## Summary

**The Goal**: Never trust stale documentation again.

**The Method**: Auto-generate baselines from actual source files.

**The Workflow**:
1. Modify chapters
2. Regenerate baselines
3. Update series index
4. Commit everything together

**The Result**: Every new AI session starts with accurate, verified information directly from your manuscript.

---

**Version**: 1.0
**Last Updated**: 2026-01-17
**Maintained By**: User + AI Assistant
**Questions**: Check SESSION_START_PROTOCOL.md
