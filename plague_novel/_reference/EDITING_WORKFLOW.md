# Book Editing Workflow
**Step-by-step guide for editing chapters with full context**

---

## 🎯 Goal

Ensure Claude has complete context before editing, maintains consistency during editing, and updates all references after editing.

---

## 📋 Complete Workflow

### Phase 1: Session Initialization (Every Session)

**Your command to Claude:**
```
"Read _reference/START_HERE.md and _reference/core/01_SERIES_INDEX.md.
I want to work on Book 2 today."
```

**What Claude will do:**
1. Read the master guide and series index
2. Confirm current status of Book 2
3. Note last update dates

**Estimated time:** 1-2 minutes

---

### Phase 2: Load Book-Specific Context

**Your command to Claude:**
```
"Read book_2_genesis_protocol/BOOK_BASELINE.md, then read chapters [X, Y, Z]
that we'll be editing."
```

**Example:**
```
"Read book_2_genesis_protocol/BOOK_BASELINE.md, then read:
- chapter_03_the_hunt.md
- chapter_04_new_hampshire.md
- chapter_05_activation.md"
```

**What Claude will do:**
1. Load the book's current canonical state (baseline)
2. Read the specific chapters for detailed context
3. Understand current plot, characters, continuity

**Estimated time:** 2-3 minutes (depending on chapter count)

---

### Phase 3: Reference Check (If Needed)

**If editing involves cross-book continuity:**

```
"Also read _reference/core/03_BLOODLINE_TRACKER.md to verify
Sarah's generation number."
```

**Common references to check:**
- **Bloodline questions:** `_reference/core/03_BLOODLINE_TRACKER.md`
- **Timeline questions:** `_reference/core/02_MASTER_TIMELINE.md`
- **Keys locations:** `_reference/core/04_SEVEN_KEYS_TRACKER.md`
- **Network details:** `_reference/core/05_NETWORK_EVOLUTION.md`
- **Terms/concepts:** `_reference/core/06_TERMINOLOGY_GLOSSARY.md`

**Estimated time:** 1-2 minutes per reference

---

### Phase 4: Make Your Edits

**Your instruction to Claude:**
```
"Edit Chapter 3 to [specific changes you want]."
```

**Tips:**
- Be specific about changes
- Reference specific paragraphs or scenes
- Ask Claude to check continuity if uncertain
- Use AskUserQuestion if Claude needs clarification

**What Claude will do:**
1. Use Edit tool to make precise changes
2. Preserve existing style and voice
3. Flag any continuity concerns
4. Ask questions if unclear

---

### Phase 5: Verify Changes

**Your command to Claude:**
```
"Show me what you changed in Chapter 3."
```

**What Claude will do:**
1. Summarize changes made
2. Highlight any continuity impacts
3. Note if other chapters need updates

**Review checklist:**
- [ ] Changes match your intent
- [ ] Voice/style consistent
- [ ] No new continuity errors
- [ ] Character details correct

---

### Phase 6: Update Baselines (Critical!)

**Your command to Claude:**
```
"Regenerate the baseline for Book 2 and update the series index."
```

**What Claude will do:**
```bash
# Execute these commands:
python3 generate_baseline.py book_2_genesis_protocol
python3 generate_series_index.py
```

**Result:**
- Book 2 baseline updated with new chapter content
- Checksum changed (proof of update)
- Series index reflects changes
- Next session will have accurate context

**Estimated time:** 30-60 seconds

---

### Phase 7: Verify Baseline Updated

**Your command to Claude:**
```
"Check that the Book 2 baseline checksum changed."
```

**What Claude will do:**
```bash
grep "Checksum" book_2_genesis_protocol/BOOK_BASELINE.md
grep "Last Updated" book_2_genesis_protocol/BOOK_BASELINE.md
```

**Expected result:**
- New checksum (different from before)
- Today's date in "Last Updated"

---

### Phase 8: Session End Documentation (Optional but Recommended)

**Your command to Claude:**
```
"Summarize what we changed today and any follow-up tasks."
```

**What Claude will do:**
1. List chapters modified
2. Summarize key changes
3. Note any continuity impacts
4. Suggest follow-up work if needed

**Save this summary** for your own reference between sessions!

---

## 🔄 Quick Reference: Minimal Workflow

**For experienced users who know the system:**

```bash
# 1. Session start
"Read START_HERE.md and 01_SERIES_INDEX.md"

# 2. Load book context
"Read book_2_genesis_protocol/BOOK_BASELINE.md and chapter_03_*.md"

# 3. Make edits
"Edit Chapter 3 to [changes]"

# 4. Update baselines
"Regen Book 2 baseline and update series index"

# Done!
```

---

## 📊 Example Full Session

**User:**
```
Read _reference/START_HERE.md and _reference/core/01_SERIES_INDEX.md.
I want to edit Chapter 3 of Book 2 to make Morrison more threatening
in his first appearance.
```

**Claude:**
```
[Reads files]

I've reviewed the series index - Book 2 was last updated 2026-01-21
(6 days ago) and shows ~50,000 words, NYT Bestseller revision complete.

Ready to work on Chapter 3. Let me read the Book 2 baseline and
Chapter 3 file now.
```

**User:**
```
Great. Read book_2_genesis_protocol/BOOK_BASELINE.md and
book_2_genesis_protocol/manuscript/chapters/chapter_03_*.md
```

**Claude:**
```
[Reads files]

I've loaded:
- Book 2 baseline (last updated 2026-01-21, checksum: BESTSELLER_REVISION_2026_01_21)
- Chapter 3: "The Hunt" - Morrison recruits his team

Currently Chapter 3 shows Morrison planning the Sarah Chen capture.
What specific changes would you like to make Morrison more threatening?
```

**User:**
```
Add a scene where Morrison coldly discusses past "acquisitions" -
targets they've captured before. Make it clear he's done this dozens
of times and has never failed.
```

**Claude:**
```
[Uses Edit tool]

I've added a 350-word scene after Morrison's strategic planning
section, where he references past operations:

- Case File 2014-07 (Tehran geneticist, detained 72 hours)
- Case File 2016-12 (Mumbai professor, vanished from university)
- Pattern: 47 acquisitions, 100% containment rate, zero exposure

This establishes Morrison as methodical, experienced, and ruthlessly
efficient. The scene flows naturally into his current plan for Sarah.

Would you like to review the exact changes?
```

**User:**
```
Perfect. Now regenerate the baseline and update the series index.
```

**Claude:**
```
[Runs commands]

✓ Regenerated Book 2 baseline
  - New checksum: BESTSELLER_REVISION_2026_01_27
  - Last Updated: 2026-01-27
  - Word count updated

✓ Updated series index
  - Book 2 now shows today's date
  - Changes reflected in series overview

All baselines updated! Chapter 3 changes are now part of the
canonical baseline.
```

---

## ⚠️ Common Mistakes to Avoid

### ❌ Don't:
1. **Skip reading the baseline** before editing
   - *Why:* You'll miss recent changes from previous sessions
   - *Fix:* Always read the book baseline first

2. **Edit without checking continuity references**
   - *Why:* Risk contradicting other books
   - *Fix:* Read relevant series bible sections

3. **Forget to regenerate baselines after editing**
   - *Why:* Next session will have stale context
   - *Fix:* Always run `generate_baseline.py` after changes

4. **Edit multiple books without regenerating each baseline**
   - *Why:* Baselines get out of sync
   - *Fix:* Regenerate after EACH book's edits

5. **Trust memory instead of files**
   - *Why:* Memory is unreliable across sessions
   - *Fix:* Always verify with baseline/chapters

---

## ✅ Best Practices

### Do:
1. **Read baseline at EVERY session start**
   - Even if you "just worked on this yesterday"
   - Baselines might have been updated

2. **Read multiple chapters in parallel**
   - Claude can read 5-10 chapters at once
   - Faster than sequential reads

3. **Ask questions before making major changes**
   - "Does this contradict the timeline?"
   - "Is Sarah's generation number correct?"
   - Claude can verify with references

4. **Use AskUserQuestion when uncertain**
   - Claude will ask clarifying questions
   - Better than guessing your intent

5. **Document significant changes**
   - Keep notes on what changed per session
   - Helps you track series evolution

---

## 🎓 Advanced Techniques

### Load Context Efficiently

**Instead of:**
```
"Read the baseline."
[wait]
"Now read chapter 3."
[wait]
"Now read chapter 4."
```

**Do this:**
```
"Read book_2_genesis_protocol/BOOK_BASELINE.md, chapter_03_*.md,
and chapter_04_*.md in parallel."
```

Claude reads all files simultaneously - much faster!

---

### Use Explore Agent for Complex Queries

**For questions like:**
- "Find all mentions of Morrison across Book 2"
- "Map character relationships in these chapters"
- "Identify all scenes with the Pattern Eye"

**Command:**
```
"Use the explore agent to find all Morrison scenes in Book 2
and summarize his character arc."
```

This preserves main context for actual editing.

---

### Batch Edits Across Chapters

**If editing multiple chapters in one session:**

```
1. Load all chapters: "Read chapters 3, 4, and 5"
2. Edit in sequence: "Edit Chapter 3 to...", then "Edit Chapter 4 to..."
3. Regenerate once: "Regen baseline" (after all edits)
4. Update index: "Update series index"
```

Regenerating once (at the end) is more efficient than per-chapter.

---

## 📞 Troubleshooting

### "Baseline seems wrong"
1. Check last updated date: `grep "Last Updated" book_*/BOOK_BASELINE.md`
2. If stale (>7 days during active work), regenerate
3. Read actual chapter to verify truth

### "Can't find a reference"
1. Check `_reference/core/01_SERIES_INDEX.md` first
2. Search with grep: `grep -r "keyword" _reference/core/`
3. If not found, might need to add to series bible

### "Continuity conflict between books"
1. Read timeline: `_reference/core/02_MASTER_TIMELINE.md`
2. Read relevant baselines for both books
3. Ask Claude: "Is there a conflict between Book 1 and Book 3?"

### "Claude forgot something from last session"
- This is normal! Claude can't remember across sessions
- Solution: Read the baseline (which captures last session's work)
- The baseline IS your memory system

---

## 🚀 Power User Workflow

**For when you're comfortable with the system:**

```bash
# Morning session start (30 seconds)
"Read START_HERE.md, 01_SERIES_INDEX.md, Book 2 baseline, chapters 3-5"

# Make all your edits (30 minutes)
[Work with Claude on multiple chapters]

# Wrap up session (1 minute)
"Regen Book 2 baseline, update index, summarize changes"

# Done! Baseline ready for next session.
```

---

**Questions? Ask Claude to walk you through any step!**
