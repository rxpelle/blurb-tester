# Plague Novel Series - CANONICAL SERIES INDEX

**Last Updated**: 2026-01-27 07:58:20
**Auto-Synced From**: Individual BOOK_BASELINE.md files
**Total Books**: 15
**Completed Books with Baselines**: 5
**Total Word Count**: 318,916 words

---

## ⚠️ SOURCE OF TRUTH HIERARCHY

When working on this series, **ALWAYS follow this verification order**:

### 1. Individual Book Baselines (HIGHEST AUTHORITY)
Check the specific book's `BOOK_BASELINE.md` file first:
- Contains actual chapter summaries extracted from manuscript
- Includes verification checksums
- Updated automatically when chapters change

### 2. This Series Index (SERIES-LEVEL OVERVIEW)
Use this file for:
- Cross-book continuity (Seven Keys custody chain, timeline events)
- Understanding the big picture
- Finding which book contains what information

### 3. Actual Chapter Files (ULTIMATE SOURCE)
If baseline seems wrong or outdated:
- Read the actual chapter markdown files
- They are the ultimate source of truth
- Then regenerate the baseline

### ❌ DO NOT TRUST
- Old outline files (unless explicitly marked as "synced with baseline")
- SERIES_BIBLE files older than baseline generation dates
- Summary documents without verification checksums
- Your memory from previous sessions
- Any document that contradicts a BOOK_BASELINE.md file

---

## Book Status Overview

| Book | Title | Status | Words | POV | Time Period | Last Updated |
|------|-------|--------|-------|-----|-------------|-------------|
| 1 | The Aethelred Cipher | ✅ Complete | 78,298 | Godric (monk and ... | 1002-1016 CE (Anglo-Sa... | 2026-01-27 07:58:15 |
| 2 | No Baseline Generated | ⚠️ No baseline | - | - | - | - |
| 3 | The First Key | ✅ Complete | 50,165 | Marcus (Roman sol... | 400-450 CE (Roman Brit... | 2026-01-27 07:39:53 |
| 4 | The Nazarene Protocol | ✅ Complete | 109,878 | Marcus Publius Sc... | 26-70 CE (Roman Judea/... | 2026-01-17 15:28:02 |
| 5 | The Augustine Protocol | 📝 In progress | 45,411 | Helena (Gen 50), ... | 312-430 CE (Late Roman... | 2026-01-17 15:30:47 |
| 6 | The Monk's Blade | 📝 In progress | 35,164 | Ciarán (from age ... | 476-1000 CE (Fall of R... | 2026-01-17 15:41:52 |
| 7 | No Baseline Generated | ⚠️ No baseline | - | - | - | - |
| 7 | No Baseline Generated | ⚠️ No baseline | - | - | - | - |
| 8 | No Baseline Generated | ⚠️ No baseline | - | - | - | - |
| 9 | No Baseline Generated | ⚠️ No baseline | - | - | - | - |
| 10 | No Baseline Generated | ⚠️ No baseline | - | - | - | - |
| 10 | No Baseline Generated | ⚠️ No baseline | - | - | - | - |
| 11 | No Baseline Generated | ⚠️ No baseline | - | - | - | - |
| 12 | No Baseline Generated | ⚠️ No baseline | - | - | - | - |
| 13 | No Baseline Generated | ⚠️ No baseline | - | - | - | - |

**Status Legend**:
- ✅ Complete with baseline
- ⚠️ Needs baseline generation
- 📝 In progress

---

## Seven Keys Custody Chain (FROM BASELINES)

Track the Seven Keys as they appear and transfer across books:

### Pattern Eye

- **Book 3 (The First Key)**: Mentioned in baseline
- **Book 4 (The Nazarene Protocol)**: Mentioned in baseline
- **Book 5 (The Augustine Protocol)**: Mentioned in baseline
- **Book 6 (The Monk's Blade)**: Mentioned in baseline

### Time Key

- No baseline mentions yet (check individual chapters or add to baseline)

### Blood Cipher

- No baseline mentions yet (check individual chapters or add to baseline)

### Memory Matrix

- No baseline mentions yet (check individual chapters or add to baseline)

### Network Seed

- No baseline mentions yet (check individual chapters or add to baseline)

### Synthesis Protocol

- No baseline mentions yet (check individual chapters or add to baseline)

### Final Key

- No baseline mentions yet (check individual chapters or add to baseline)

---

## Major Characters Across Series

Characters that appear prominently in each book (from baselines):

### Book 1: The Aethelred Cipher
- Thomas
- Scene
- Margarethe
- And
- But

### Book 3: The First Key
- Generation
- Genesis Protocol
- Nefertari
- But
- That

### Book 4: The Nazarene Protocol
- Jesus
- Mary
- Generation
- Not
- Capernaum

### Book 5: The Augustine Protocol
- Augustine
- Generation
- Hippo
- North Africa
- Monica

### Book 6: The Monk's Blade
- But
- Clonmacnoise
- And
- His
- Generation

---

## Series Timeline (FROM BASELINES)

- **Book 1** (The Aethelred Cipher): 1002-1016 CE (Anglo-Saxon England)
- **Book 3** (The First Key): 400-450 CE (Roman Britain collapse)
- **Book 4** (The Nazarene Protocol): 26-70 CE (Roman Judea/Galilee)
- **Book 5** (The Augustine Protocol): 312-430 CE (Late Roman Empire collapse)
- **Book 6** (The Monk's Blade): 476-1000 CE (Fall of Rome to Early Medieval Ireland)

---

## Baseline Update Protocol

### When to Regenerate Baselines

Regenerate a book's baseline whenever:
1. You modify any chapter file
2. You add new chapters
3. You fix continuity issues
4. A baseline is more than 7 days old during active editing

### How to Regenerate

```bash
# Single book
python generate_baseline.py book_1_aethelred_cipher

# All books
python generate_baseline.py --all

# Then update this series index
python generate_series_index.py
```

### Verification

Each baseline includes a checksum. If you're unsure if a baseline is current:
1. Check the checksum in BOOK_BASELINE.md
2. Regenerate and compare checksums
3. If different, baseline was out of date

---

## Session Start Protocol

**At the beginning of EVERY new session:**

1. Read `CANONICAL_SERIES_INDEX.md` (this file)
2. If working on a specific book, read that book's `BOOK_BASELINE.md`
3. Note the "Last Updated" dates
4. If baselines are stale (>7 days during active work), regenerate
5. NEVER trust outline files without checking baselines first

**Before making any changes:**

1. Read the relevant `BOOK_BASELINE.md`
2. If uncertain, read the actual chapter files
3. Make your changes
4. Regenerate the baseline: `python generate_baseline.py book_X_name`
5. Update this index: `python generate_series_index.py`

---

## Book Details

### Book 1: The Aethelred Cipher

**Directory**: `book_1_aethelred_cipher`
**Baseline**: `book_1_aethelred_cipher/BOOK_BASELINE.md`
**Word Count**: 78,298
**Chapters**: 11
**POV Character**: Godric (monk and scribe)
**Time Period**: 1002-1016 CE (Anglo-Saxon England)
**Checksum**: `76a73a0e1cf25888`
**Last Updated**: 2026-01-27 07:58:15

### Book 3: The First Key

**Directory**: `book_3_first_key`
**Baseline**: `book_3_first_key/BOOK_BASELINE.md`
**Word Count**: 50,165
**Chapters**: 13
**POV Character**: Marcus (Roman soldier/scholar)
**Time Period**: 400-450 CE (Roman Britain collapse)
**Checksum**: `d38a21815a0ebe48`
**Last Updated**: 2026-01-27 07:39:53
**Seven Keys**: Pattern Eye

### Book 4: The Nazarene Protocol

**Directory**: `book_4_nazarene_protocol`
**Baseline**: `book_4_nazarene_protocol/BOOK_BASELINE.md`
**Word Count**: 109,878
**Chapters**: 14
**POV Character**: Marcus Publius Scipio (Roman centurion), Jesus ben Yosef, Mary of Magdala
**Time Period**: 26-70 CE (Roman Judea/Galilee)
**Checksum**: `cf5bf36200547c8b`
**Last Updated**: 2026-01-17 15:28:02
**Seven Keys**: Pattern Eye

### Book 5: The Augustine Protocol

**Directory**: `book_5_augustine_protocol`
**Baseline**: `book_5_augustine_protocol/BOOK_BASELINE.md`
**Word Count**: 45,411
**Chapters**: 9
**POV Character**: Helena (Gen 50), Augustine of Hippo (Gen 52)
**Time Period**: 312-430 CE (Late Roman Empire collapse)
**Checksum**: `c9c90fb036c08c6c`
**Last Updated**: 2026-01-17 15:30:47
**Seven Keys**: Pattern Eye

### Book 6: The Monk's Blade

**Directory**: `book_6_monks_blade`
**Baseline**: `book_6_monks_blade/BOOK_BASELINE.md`
**Word Count**: 35,164
**Chapters**: 8
**POV Character**: Ciarán (from age 4 to adulthood)
**Time Period**: 476-1000 CE (Fall of Rome to Early Medieval Ireland)
**Checksum**: `7f4431f54864947a`
**Last Updated**: 2026-01-17 15:41:52
**Seven Keys**: Pattern Eye


---

**Generated**: 2026-01-27 07:58:20
**Baselines Found**: 5
**Total Books**: 15
