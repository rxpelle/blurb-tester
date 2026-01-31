# PLAGUE NOVEL SERIES - START HERE
**Quick Reference Guide for Every New Session**

Last Updated: 2026-01-27 (SIMPLE START method added!)

---

## 🎯 QUICK START: The Simple Way

### Just Tell Claude What You Want!

**No need to memorize file paths.** Just say:

```
"Let's work on Book 2"
"I want to edit Book 1, Chapter 3"
"Help me with Book 4"
```

**That's it!** Claude will automatically:
- Load the series index
- Find your book's manuscript or baseline
- Read relevant context based on your request

**👉 See [SIMPLE_START.md](SIMPLE_START.md) for complete guide**

---

## 📖 Advanced: Manual File Reading (Optional)

If you prefer to specify exactly what to read:

### For EVERY New Session:
1. **Read this file** (you're doing it!)
2. **Read:** [01_SERIES_INDEX.md](core/01_SERIES_INDEX.md) (2-3 min) - Current status of all books
3. **Check date:** Is the series index recent? If >7 days old during active work, regenerate baselines

### Before Working on a Specific Book:
4. **Read:** `book_X_name/BOOK_BASELINE.md` - Current state of that book
5. **Note:** The "Last Updated" date and checksum
6. **If needed:** Read actual chapter files for details

---

## 📚 Reference Structure Overview

```
plague_novel/
├── _reference/                          ← YOU ARE HERE
│   ├── START_HERE.md                    ← This file (master guide)
│   ├── QUICK_COMMANDS.md                ← Command cheat sheet
│   ├── EDITING_WORKFLOW.md              ← Step-by-step editing guide
│   ├── BOOK_2_NOTES.md                  ← Book 2 special structure notes
│   ├── FILE_AUDIT.md                    ← Organization plan documentation
│   │
│   ├── core/                            ← Essential series-wide info
│   │   ├── 01_SERIES_INDEX.md           ← Current status of all books
│   │   ├── 02_MASTER_TIMELINE.md        ← 1177 BCE → 2018 CE complete timeline
│   │   ├── 03_BLOODLINE_TRACKER.md      ← Tausret → Sarah (111 generations)
│   │   ├── 04_SEVEN_KEYS_TRACKER.md     ← Bronze keys locations through time
│   │   ├── 05_NETWORK_EVOLUTION.md      ← Defensive vs Offensive networks
│   │   └── 06_TERMINOLOGY_GLOSSARY.md   ← Consistent terms & concepts
│   │
│   ├── concepts/                        ← World-building concept definitions
│   │   ├── THE_ORDER.md                 ← Offensive network explained (all eras)
│   │   ├── SYSTEMS_THINKING.md          ← Defensive methodology explained
│   │   └── GENETIC_ENCODING.md          ← How genetic memory works
│   │
│   ├── writing/                         ← Writing guidelines & philosophy
│   │   └── GENRE_GUIDE.md               ← Intellectual thriller approach
│   │
│   ├── planning/                        ← Future books planning
│   │   ├── BOOKS_5-12_FINAL_STATUS.md   ← Later books status
│   │   ├── BOOKS_9-12_OUTLINES.md       ← Book outlines
│   │   └── BOOK_8_RECOMMENDATION.md     ← Book 8 recommendations
│   │
│   ├── tools/                           ← How to use the baseline system
│   │   ├── SESSION_START_PROTOCOL.md    ← Detailed workflow instructions
│   │   └── BASELINE_SYSTEM_README.md    ← How baselines work
│   │
│   └── archive/                         ← Historical documentation
│       ├── status_reports/              ← Old completion reports (Jan 2026)
│       ├── continuity_checks/           ← Old verification reports
│       └── [old pointer files]          ← Superseded documents
│
├── book_1_aethelred_cipher/
│   ├── BOOK_BASELINE.md                 ← CANONICAL SOURCE for Book 1
│   └── manuscript/chapters/             ← ACTUAL SOURCE OF TRUTH
│
├── book_2_genesis_protocol/
│   ├── BOOK_BASELINE.md                 ← CANONICAL SOURCE for Book 2
│   └── manuscript/chapters/             ← ACTUAL SOURCE OF TRUTH
│
[... more books ...]
```

---

## 🔥 CRITICAL: Source of Truth Hierarchy

When you need to verify ANY information, use this order:

### 1️⃣ HIGHEST: Actual Chapter Files
- Location: `book_X_name/manuscript/chapters/*.md`
- These are THE TRUTH
- Everything else derives from these

### 2️⃣ SECOND: Book Baselines
- Location: `book_X_name/BOOK_BASELINE.md`
- Auto-generated from chapters (verified by checksum)
- Check "Last Updated" date

### 3️⃣ THIRD: Series Index
- Location: `_reference/core/01_SERIES_INDEX.md`
- Series-level overview and cross-book continuity

### ❌ NEVER TRUST:
- Your memory from previous sessions
- Old outline files (unless dated after baselines)
- Any document contradicting a BOOK_BASELINE.md

---

## 📖 What Each Core Reference Contains

### [01_SERIES_INDEX.md](core/01_SERIES_INDEX.md)
- **Quick overview** of all 13 books
- **Status:** Complete, in-progress, or needs baseline
- **Word counts** and last update dates
- **Seven Keys custody chain** across books
- **Major characters** per book

**When to use:**
- Every session start
- When you need to find which book contains what
- Cross-book continuity checks

---

### [02_MASTER_TIMELINE.md](core/02_MASTER_TIMELINE.md)
- **Complete chronology:** 1177 BCE → 2018 CE (3,195 years)
- **Book-by-book breakdown** of historical periods
- **Major events** that shape the series
- **Networks evolution** through time

**When to use:**
- Understanding how books connect chronologically
- Verifying historical accuracy
- Tracking how the Genesis Protocol evolves

---

### [03_BLOODLINE_TRACKER.md](core/03_BLOODLINE_TRACKER.md)
- **Tausret → Sarah:** Complete genealogy (111 generations)
- **Generation counting:** Absolute vs Local systems explained
- **Key carriers** in each era
- **Bloodline movements** through geography/time

**When to use:**
- Verifying character relationships
- Understanding genetic memory inheritance
- Tracking the "Living Key" (bloodline itself)

---

### [04_SEVEN_KEYS_TRACKER.md](core/04_SEVEN_KEYS_TRACKER.md)
- **All 7 bronze keys** tracked through 3,195 years
- **Current locations** in each book's timeframe
- **Defensive vs Offensive keys** split
- **Key functions** and how they work

**When to use:**
- Tracking key custody/location in any book
- Understanding key mechanics
- Avoiding continuity errors with keys

---

### [05_NETWORK_EVOLUTION.md](core/05_NETWORK_EVOLUTION.md)
- **Defensive network:** How it adapts through time
- **Offensive network (Order):** Institutional forms
- **Battle for control** across centuries

**When to use:**
- Understanding network strategies in each era
- Tracking how networks embed in institutions
- Clarifying defensive vs offensive modes

---

### [06_TERMINOLOGY_GLOSSARY.md](core/06_TERMINOLOGY_GLOSSARY.md)
- **Consistent terms** used across series
- **Concepts explained:** Genesis Protocol, genetic memory, etc.
- **Avoiding confusion** between similar terms

**When to use:**
- Double-checking term usage
- Ensuring consistency in new writing
- Clarifying concepts

---

### [concepts/](concepts/)
World-building concept definitions - deep dives into major series elements:

#### [THE_ORDER.md](concepts/THE_ORDER.md)
- **Complete explanation** of the antagonist organization
- **Evolution across 3,200 years:** From 1177 BCE to modern day
- **Name changes:** Order of the Strong → The Order → GenVault
- **Philosophy:** "Collapse is inevitable, engineer who survives"

**When to use:**
- Understanding the offensive network
- Writing antagonist scenes
- Clarifying The Order's goals and methods

#### [SYSTEMS_THINKING.md](concepts/SYSTEMS_THINKING.md)
- **Core defensive methodology** explained
- **What's real vs. fictional:** Feedback loops, pattern recognition (real); genetic encoding (fiction)
- **Progression through books:** How each book adds complexity
- **Teaching the method:** How characters learn systems thinking

**When to use:**
- Writing defensive network scenes
- Explaining the methodology to readers
- Ensuring character knowledge is appropriate

#### [GENETIC_ENCODING.md](concepts/GENETIC_ENCODING.md)
- **How genetic memory works** in this world
- **Evolution of encoding** across generations
- **Technical mechanics:** What carriers inherit vs. learn

**When to use:**
- Understanding carrier abilities
- Writing genetic memory scenes
- Consistency checks on inheritance

---

### [writing/](writing/)
Writing guidelines and editorial philosophy:

#### [GENRE_GUIDE.md](writing/GENRE_GUIDE.md)
- **Intellectual historical thriller** approach
- **Editor personas:** Developmental, accessibility, historical accuracy
- **Comp titles:** *The Name of the Rose*, *Cloud Atlas*, *Foucault's Pendulum*
- **What readers expect:** Ideas drive plot, efficient prose, smart pacing
- **Target reading level:** 10th grade (accessibility without dumbing down)

**When to use:**
- Before starting new chapters
- During revisions for genre alignment
- When unsure about prose style
- Editorial decision-making

---

### [planning/](planning/)
Future book outlines and status:

#### Planning Files:
- **BOOKS_5-12_FINAL_STATUS.md** - Current state of later books
- **BOOKS_9-12_OUTLINES.md** - Detailed outlines for Books 9-12
- **BOOK_8_RECOMMENDATION.md** - Recommendations for Book 8 approach

**When to use:**
- Planning work on Books 5-13
- Understanding future story arcs
- Cross-book continuity for later books

---

### [archive/](archive/)
Historical documentation (searchable but not for current work):

- **status_reports/** - Old completion reports from January 2026
- **continuity_checks/** - Old verification and reconciliation reports
- **[root files]** - Superseded indices and timelines

**When to use:**
- Rarely - only if investigating past decisions
- Historical context on how series developed
- Finding old analysis if needed

---

## 🛠️ Common Workflows

### Starting a New Session (General):
```bash
1. Read: _reference/START_HERE.md (this file)
2. Read: _reference/core/01_SERIES_INDEX.md
3. Check: Are baselines recent?
4. Ready to work!
```

### Working on Book 2 (or any specific book):
```bash
1. Do "Starting a New Session" steps above
2. Read: book_2_genesis_protocol/BOOK_BASELINE.md
3. Note: Last Updated date and checksum
4. If details needed: Read specific chapter files
5. Make your changes
6. Regenerate: python3 generate_baseline.py book_2_genesis_protocol
7. Update: python3 generate_series_index.py
```

### Finding Information Across Books:
```bash
# Example: "Where is the Pattern Eye mentioned?"

1. Search series index: grep "Pattern Eye" _reference/core/01_SERIES_INDEX.md
2. Found in Book 1, 2, 4, 5, 6
3. For details: grep "Pattern Eye" book_1_aethelred_cipher/BOOK_BASELINE.md
4. If still unclear: Read actual chapter files
```

### Checking Cross-Book Continuity:
```bash
1. Read: _reference/core/02_MASTER_TIMELINE.md (events)
2. Read: _reference/core/03_BLOODLINE_TRACKER.md (characters)
3. Read: _reference/core/04_SEVEN_KEYS_TRACKER.md (artifacts)
4. Cross-reference with book baselines
```

---

## 🚨 Most Common Mistakes to Avoid

### ❌ Don't:
- Trust your memory from previous sessions
- Skip reading the Series Index at session start
- Make changes without reading the book's baseline first
- Forget to regenerate baselines after editing
- Trust old outline files

### ✅ Do:
- Always read the Series Index first
- Verify with baselines before making changes
- Regenerate baselines after ANY chapter edit
- Read actual chapters when in doubt
- Document your changes

---

## 📊 Book Status Quick Reference

| Book | Status | Words | Last Updated |
|------|--------|-------|--------------|
| 1: Aethelred Cipher | ✅ Complete | 78,298 | 2026-01-17 |
| 2: Genesis Protocol | ✅ Complete (BESTSELLER) | ~50,000 | 2026-01-21 |
| 3: First Key | ⚠️ Needs baseline | Unknown | - |
| 4: Nazarene Protocol | ✅ Complete | 109,878 | 2026-01-17 |
| 5: Augustine Protocol | 📝 In progress | 45,411 | 2026-01-17 |
| 6: Monk's Blade | 📝 In progress | 35,164 | 2026-01-17 |
| 7-13 | ⚠️ Needs baseline | Various | - |

*(See [01_SERIES_INDEX.md](core/01_SERIES_INDEX.md) for complete details)*

---

## 🔧 Tool Commands Quick Reference

```bash
# Regenerate single book baseline
python3 generate_baseline.py book_1_aethelred_cipher

# Regenerate ALL book baselines (slow)
python3 generate_baseline.py --all

# Update series index (do this after baseline regeneration)
python3 generate_series_index.py

# Add metadata to a chapter
python3 add_metadata_header.py path/to/chapter.md --chapter N --title "Title"

# Search for something across all baselines
grep -r "Pattern Eye" book_*/BOOK_BASELINE.md

# Check baseline dates
grep "Last Updated" book_*/BOOK_BASELINE.md

# Verify checksums
grep "Checksum" book_*/BOOK_BASELINE.md
```

---

## 💡 Tips for Maximum Context Retention

### When Starting a Session:
1. **Ask me to read multiple files in parallel**
   - Example: *"Read 01_SERIES_INDEX.md, book_2_genesis_protocol/BOOK_BASELINE.md, and 04_SEVEN_KEYS_TRACKER.md"*
   - I can load all at once!

2. **Use the Explore agent for open-ended questions**
   - Example: *"Use the explore agent to map character relationships in Book 2"*
   - This preserves main context for actual work

3. **Point me to specific reference sections**
   - Example: *"Check the bloodline tracker for Sarah Chen's generation number"*
   - Faster than reading entire files

### During Editing:
1. **Keep reference files open** (ask me to read them)
2. **Cross-reference actively** before making changes
3. **Ask questions** if something feels inconsistent
4. **Use AskUserQuestion tool** when uncertain

---

## 📝 Session End Checklist

Before ending a session where you edited chapters:

- [ ] Regenerated baselines for modified books
- [ ] Updated CANONICAL_SERIES_INDEX.md via `generate_series_index.py`
- [ ] Verified checksums changed
- [ ] No contradictions introduced
- [ ] Clear notes about what changed

---

## 🎓 Learning the System

**First time using this?**

1. **Start here:** Read this file (you did it!)
2. **Quick tour:** Skim [01_SERIES_INDEX.md](core/01_SERIES_INDEX.md)
3. **Deep dive:** Read [SESSION_START_PROTOCOL.md](tools/SESSION_START_PROTOCOL.md)
4. **Practice:** Pick a book, read its baseline, ask me questions

**Already familiar?**

1. Read [01_SERIES_INDEX.md](core/01_SERIES_INDEX.md)
2. Read relevant book baseline
3. Start working!

---

## 🤝 How to Use Me (Claude) Effectively

### At Session Start:
*"Read _reference/START_HERE.md and _reference/core/01_SERIES_INDEX.md, then let's work on Book 2."*

### Before Editing:
*"Read book_2_genesis_protocol/BOOK_BASELINE.md and the chapters we're editing."*

### For Continuity Checks:
*"Check the bloodline tracker - is Sarah really 69th generation from Jesus?"*

### For Broad Questions:
*"Use the explore agent to find all mentions of Morrison across Book 2."*

### After Editing:
*"Regenerate the baseline for Book 2 and update the series index."*

---

## 📞 Need More Details?

- **Baseline system:** See [tools/BASELINE_SYSTEM_README.md](tools/BASELINE_SYSTEM_README.md)
- **Session workflow:** See [tools/SESSION_START_PROTOCOL.md](tools/SESSION_START_PROTOCOL.md)
- **All books status:** See [core/01_SERIES_INDEX.md](core/01_SERIES_INDEX.md)

---

**Last Updated:** 2026-01-27
**Maintained by:** Baseline automation + manual updates
**Questions?** Ask Claude to clarify anything in this system!
