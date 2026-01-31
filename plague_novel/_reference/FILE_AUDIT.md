# Root Files Audit & Organization Plan

**Created:** 2026-01-27
**Purpose:** Categorize loose root-level files and organize them properly

---

## 📊 File Categories

### ✅ KEEP & MOVE TO _reference/

#### **Concept Definitions (Move to _reference/concepts/)**
- [x] `THE_ORDER_EXPLAINED.md` → Explains offensive network across all eras
- [x] `SYSTEMS_THINKING_ACROSS_SERIES.md` → Core defensive methodology
- [ ] `SERIES_ENCODING_EVOLUTION.md` → How genetic memory evolves (check if useful)
- [ ] `SERIES_CONTINUITY_MASTER.md` → May duplicate timeline info (review)

#### **Writing Guidelines (Move to _reference/writing/)**
- [x] `comprehensive_editorial_prompt_INTELLECTUAL_THRILLER.md` → Genre/style guide

#### **Outlines & Planning (Move to _reference/planning/)**
- [ ] `BOOKS_9-12_OUTLINES.md` → Future book outlines
- [ ] `BOOKS_5-12_FINAL_STATUS.md` → Status of later books
- [ ] `BOOK_8_RECOMMENDATION.md` → Recommendations for Book 8

---

### 🗄️ ARCHIVE (Move to _reference/archive/status_reports/)

**Completion Reports (Jan 14-17, 2026):**
- `BASELINE_COMPARISON_FIXES_COMPLETE_2026-01-15.md`
- `BOOK_1_BASELINE_COMPARISON_COMPLETE.md`
- `CONTINUITY_ANALYSIS_COMPLETE.md`
- `ENCODING_TIMELINE_RECONCILIATION_COMPLETE.md`
- `FINAL_CONTINUITY_STATUS_2026-01-15.md`
- `FIXES_APPLIED_2026-01-15.md`
- `IMPLEMENTATION_COMPLETE.md`
- `IMPLEMENTATION_SUMMARY.md`
- `PATTERN_EYE_CUSTODY_COMPLETE.md`

**Verification Reports:**
- `BOOKS_5-12_VERIFICATION_SUMMARY.md`
- `CROSS_BOOK_CONTINUITY_REVIEW.md`
- `DISCREPANCIES_REPORT_BOOKS_1-11.md`

**Reconciliation Reports:**
- `GENERATION_RECONCILIATION_book1_backward.md`

---

### ⚠️ REVIEW NEEDED (Determine if useful or outdated)

- `SERIES_BASELINE.md` - Compare with CANONICAL_SERIES_INDEX.md
- `SERIES_INDEX.md` - Compare with CANONICAL_SERIES_INDEX.md (may be old version)
- `SERIES_CHRONOLOGICAL_FRAMEWORK.md` - Compare with master_timeline.md
- `MASTER_CONTINUITY_TIMELINE.md` - Compare with master_timeline.md
- `BOOK_2_FINAL_MANUSCRIPT.md` - Check if pointer or actual content
- `NAMING_CONVENTION_DECISION.md` - May be useful documentation

---

### 🎯 Already Organized

**In _reference/core/ (via symlinks):**
- `CANONICAL_SERIES_INDEX.md`
- `SERIES_BIBLE_master_timeline.md`
- `SERIES_BIBLE_bloodline_tracker.md`
- `SERIES_BIBLE_seven_keys_tracker.md`
- `SERIES_BIBLE_network_evolution.md`
- `SERIES_BIBLE_terminology_glossary.md`

**In _reference/tools/ (via symlinks):**
- `SESSION_START_PROTOCOL.md`
- `BASELINE_SYSTEM_README.md`

---

## 📁 Proposed New Directory Structure

```
_reference/
├── core/                    ← Already done (6 files)
├── tools/                   ← Already done (2 files)
├── concepts/                ← NEW - Core world concepts
│   ├── THE_ORDER.md
│   ├── SYSTEMS_THINKING.md
│   └── GENETIC_ENCODING.md (if extracted)
├── writing/                 ← NEW - Writing guidelines
│   └── GENRE_GUIDE.md
├── planning/                ← NEW - Future books planning
│   ├── BOOKS_5-8_STATUS.md
│   └── BOOKS_9-12_OUTLINES.md
└── archive/                 ← Already exists
    ├── status_reports/      ← NEW - Old completion reports
    └── continuity_checks/   ← NEW - Old verification reports
```

---

## 🔧 Action Plan

### Phase 1: Create New Directories
```bash
mkdir -p _reference/concepts
mkdir -p _reference/writing
mkdir -p _reference/planning
mkdir -p _reference/archive/status_reports
mkdir -p _reference/archive/continuity_checks
```

### Phase 2: Move Concept Files
```bash
# Move (or symlink) concept files
mv THE_ORDER_EXPLAINED.md _reference/concepts/THE_ORDER.md
mv SYSTEMS_THINKING_ACROSS_SERIES.md _reference/concepts/SYSTEMS_THINKING.md
mv comprehensive_editorial_prompt_INTELLECTUAL_THRILLER.md _reference/writing/GENRE_GUIDE.md
```

### Phase 3: Archive Status Reports
```bash
# Move old completion reports
mv *_COMPLETE*.md _reference/archive/status_reports/
mv FIXES_APPLIED_2026-01-15.md _reference/archive/status_reports/
mv IMPLEMENTATION_*.md _reference/archive/status_reports/

# Move verification reports
mv *_VERIFICATION_*.md _reference/archive/continuity_checks/
mv *_REVIEW*.md _reference/archive/continuity_checks/
mv DISCREPANCIES_*.md _reference/archive/continuity_checks/
mv *_RECONCILIATION_*.md _reference/archive/continuity_checks/
```

### Phase 4: Move Planning Files
```bash
mv BOOKS_*_OUTLINES.md _reference/planning/
mv BOOKS_*_STATUS.md _reference/planning/
mv BOOK_*_RECOMMENDATION.md _reference/planning/
```

### Phase 5: Review Duplicates
```bash
# Compare these files to determine which is canonical:
# - SERIES_INDEX.md vs CANONICAL_SERIES_INDEX.md
# - SERIES_BASELINE.md vs CANONICAL_SERIES_INDEX.md
# - SERIES_CHRONOLOGICAL_FRAMEWORK.md vs SERIES_BIBLE_master_timeline.md
# - MASTER_CONTINUITY_TIMELINE.md vs SERIES_BIBLE_master_timeline.md

# Delete outdated versions after verification
```

---

## 📝 Benefits of This Organization

**Before:**
- 40+ loose files at root level
- Hard to distinguish current from outdated
- Status reports mixed with reference docs
- Concept definitions hard to find

**After:**
- Clean root directory (only essential files)
- Concepts organized in _reference/concepts/
- Writing guidelines in _reference/writing/
- Old status reports archived (searchable but out of the way)
- Clear separation: reference vs. history

---

## ⚡ Quick Access After Organization

**For concept questions:**
```bash
cat _reference/concepts/THE_ORDER.md
cat _reference/concepts/SYSTEMS_THINKING.md
```

**For writing guidance:**
```bash
cat _reference/writing/GENRE_GUIDE.md
```

**For future book planning:**
```bash
cat _reference/planning/BOOKS_9-12_OUTLINES.md
```

**To check old status reports (if needed):**
```bash
ls _reference/archive/status_reports/
cat _reference/archive/status_reports/CONTINUITY_ANALYSIS_COMPLETE.md
```

---

## 🎯 Update START_HERE.md After

Add these sections to START_HERE.md:

```markdown
### [concepts/](concepts/)
Core world-building concepts explained:
- THE_ORDER.md - Offensive network across all eras
- SYSTEMS_THINKING.md - Defensive methodology

### [writing/](writing/)
Writing guidelines and genre approach:
- GENRE_GUIDE.md - Intellectual thriller editorial philosophy

### [planning/](planning/)
Future book outlines and status:
- BOOKS_9-12_OUTLINES.md - Later books planning
```

---

**Ready to execute this plan?**
