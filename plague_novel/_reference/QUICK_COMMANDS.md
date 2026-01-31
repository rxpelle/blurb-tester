# Quick Command Reference

**One-page cheat sheet for common operations**

---

## 🎯 Session Start Commands

```bash
# Read these at the start of EVERY session:
cat _reference/START_HERE.md
cat _reference/core/01_SERIES_INDEX.md

# If working on Book 2:
cat book_2_genesis_protocol/BOOK_BASELINE.md
```

---

## 📝 Baseline Commands

```bash
# Regenerate single book baseline
python3 generate_baseline.py book_2_genesis_protocol

# Regenerate ALL baselines (slow - ~5-10 min)
python3 generate_baseline.py --all

# Update series index (always do after baseline regen)
python3 generate_series_index.py

# Check when baselines were last updated
grep "Last Updated" book_*/BOOK_BASELINE.md

# Verify baseline checksums
grep "Checksum" book_*/BOOK_BASELINE.md
```

---

## 🔍 Search Commands

```bash
# Find something across all baselines
grep -r "Pattern Eye" book_*/BOOK_BASELINE.md

# Find in actual chapters
grep -r "Morrison" book_2_genesis_protocol/manuscript/chapters/*.md

# Find across entire series
grep -r "Seven Keys" book_*/

# Find in series references
grep "Sarah Chen" _reference/core/*.md
```

---

## 📖 Reading Files

```bash
# Read a specific book baseline
cat book_2_genesis_protocol/BOOK_BASELINE.md

# Read a specific chapter
cat book_2_genesis_protocol/manuscript/chapters/chapter_01_*.md

# Read series index
cat _reference/core/01_SERIES_INDEX.md

# Read timeline
cat _reference/core/02_MASTER_TIMELINE.md

# Read bloodline tracker
cat _reference/core/03_BLOODLINE_TRACKER.md
```

---

## 📊 Status Checks

```bash
# List all books
ls -d book_*

# Check book structure
ls -la book_2_genesis_protocol/

# Find all chapter files
find book_2_genesis_protocol/manuscript/chapters -name "*.md"

# Count words in a book (rough estimate)
wc -w book_2_genesis_protocol/manuscript/chapters/*.md
```

---

## 🛠️ Metadata Commands

```bash
# Add metadata to a chapter
python3 add_metadata_header.py \
  book_2_genesis_protocol/manuscript/chapters/chapter_03_*.md \
  --chapter 3 \
  --title "Chapter Title" \
  --date "2020 CE" \
  --pov "Sarah Chen"
```

---

## 🔧 Git Commands (if using version control)

```bash
# Check what changed
git status
git diff

# Commit changes (after regenerating baselines)
git add .
git commit -m "Updated Book 2 Chapter 5: [description]"
git push
```

---

## 💡 Claude-Specific Requests

```bash
# At session start:
"Read _reference/START_HERE.md and _reference/core/01_SERIES_INDEX.md"

# Before editing:
"Read book_2_genesis_protocol/BOOK_BASELINE.md and chapters 3-5"

# For searches:
"Use the explore agent to find all mentions of the Pattern Eye in Book 2"

# For verification:
"Check the bloodline tracker - what generation is Sarah Chen?"

# After editing:
"Regenerate the Book 2 baseline and update the series index"
```

---

## 📁 Directory Structure Reminder

```
plague_novel/
├── _reference/
│   ├── START_HERE.md              ← Read this first
│   ├── QUICK_COMMANDS.md          ← You are here
│   ├── core/                      ← Series-wide references
│   └── tools/                     ← How-to guides
│
├── book_2_genesis_protocol/
│   ├── BOOK_BASELINE.md           ← Canonical summary
│   └── manuscript/chapters/       ← Actual source files
│
├── generate_baseline.py           ← Baseline generator
├── generate_series_index.py       ← Series index generator
└── add_metadata_header.py         ← Metadata tool
```

---

## ⚡ Most Common Operations

### Edit a chapter:
1. Read baseline: `cat book_2_genesis_protocol/BOOK_BASELINE.md`
2. Edit chapter file
3. Regen baseline: `python3 generate_baseline.py book_2_genesis_protocol`
4. Update index: `python3 generate_series_index.py`

### Find information:
1. Check index: `cat _reference/core/01_SERIES_INDEX.md`
2. Check baseline: `cat book_X_name/BOOK_BASELINE.md`
3. If needed: Read actual chapter file

### Verify continuity:
1. Timeline: `cat _reference/core/02_MASTER_TIMELINE.md`
2. Bloodline: `cat _reference/core/03_BLOODLINE_TRACKER.md`
3. Keys: `cat _reference/core/04_SEVEN_KEYS_TRACKER.md`

---

**Keep this file open in a second terminal for quick copy/paste!**
