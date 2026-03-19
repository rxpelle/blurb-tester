# Author Tool Pipeline — Phase Playbook

*Maps all 36 tools to the natural phases of writing and publishing a book.*
*Updated 2026-03-14*

---

## Phase 0: Always-On Intelligence (continuous background)

**Tools:** mcp-book-data, comp-tracker, category-spy, review-miner (monitoring mode), launch-dashboard

These run 24/7 collecting market data. Everything else pulls from this layer.

**Unbuilt:** Also-Bought Mapper (#5) — enriches market intelligence with Amazon recommendation graph.

---

## Phase 1: Market Discovery (1-2 weeks)

**Tools:** indie-scout, review-miner, kdp-scout + category-spy + comp-tracker data

Find underserved niches, analyze reader pain points from competitor reviews, validate keyword demand.

**Output:** Market brief with genre, audience, and keyword targets.

---

## Phase 2: Concept & Architecture (3-5 days)

**Tools:** concept-gen → series-framework → chapter-outliner

Generate high-concept pitches informed by Phase 1 data, build series structure, then break into chapter-level outlines.

**Human gate:** Concept approval, outline approval.

**Unbuilt:** Series Bible Generator (#8) — **biggest gap**, currently manual series tracking. Series Read-Through Calculator (#24) — validates series economics before committing.

---

## Phase 3: Writing (2-6 months)

**Tools:** chapter-drafter + continuity-checker (iterative loop)

Draft chapters, run continuity checks after each batch. Loop until manuscript complete.

**Human gate:** Manuscript approval.

---

## Phase 4: Editorial (2-4 weeks)

**Tools:** editorial-agent (multi-pass) + final continuity-checker

Developmental edit → line edit → copy edit → proofread. Final continuity sweep.

---

## Phase 5: Production (3-5 days, parallel tracks)

Three tracks run simultaneously:

| Track | Tools |
|---|---|
| Format | book-formatter (ePub, print, PDF) |
| Cover | cover-generator + cover-comp-analyzer (A/B testing) |
| Metadata | blurb-tester, kdp-scout (semantic keywords) |

**Human gate:** Cover approval.

**Unbuilt:** Price Optimizer (#25) — data-driven pricing. GEO Optimizer (#34) — listing optimization for AI search.

---

## Phase 6: Pre-Launch (T-30 to T-1)

**Tools:** launch-orchestrator managing → ad-copy-gen, arc-manager, blog-post-gen, content-repurposer, booktok-gen

Orchestrator sequences all marketing prep: ARCs out, ad copy scored, blog posts GEO-optimized, social content generated.

**Human gate:** Launch go/no-go.

**Unbuilt:** Newsletter Swap Finder (#22) — automated promo partnerships.

---

## Phase 7: Launch & Sustain (T-0 onward)

**Tools:** launch-dashboard, then Phase 0 resumes

Monitor sales, ads, reviews. Comp-tracker and review-miner feed back into the always-on loop for the next book.

**Unbuilt:** Royalty Reconciler (#26) — revenue tracking. KU Page-Flip Detector (#30) — fraud detection.

---

## Data Flow

```
Phase 0 (market data) → Phase 1 (discovery) → Phase 2 (concept) → Phase 3 (writing)
    ↑                                                                      ↓
Phase 7 (sustain) ← Phase 6 (pre-launch) ← Phase 5 (production) ← Phase 4 (editorial)
```

## Unbuilt Tools Summary

| Phase | Tool | Priority |
|---|---|---|
| 0 | Also-Bought Mapper (#5) | Medium |
| 2 | Series Bible Generator (#8) | **High — biggest gap** |
| 2 | Series Read-Through Calculator (#24) | Medium |
| 5 | Price Optimizer (#25) | Medium |
| 5 | GEO Optimizer (#34) | Medium |
| 6 | Newsletter Swap Finder (#22) | Low |
| 7 | Royalty Reconciler (#26) | Low |
| 7 | KU Page-Flip Detector (#30) | Low |
| — | KDP Publisher (#17) | Phase 4+ |
| — | Backmatter Link Tracker (#27) | Phase 4+ |
| — | Reader Magnet Funnel (#28) | Phase 4+ |
| — | Wide vs KU Simulator (#29) | Phase 4+ |
| — | Audiobook Cost Calculator (#31) | Phase 4+ |
| — | Author Tools SaaS (#36) | Phase 5 |

## Orchestrator Design

The future Pipeline Orchestrator is a state machine that moves a "book project" through phases 1→7, calling agents at each step. Five human review gates block progression until approved. Phase 0 runs independently as a background daemon.

## Quick Reference

| Phase | Duration | Tools | Gate |
|---|---|---|---|
| 0 | Always | 5 tools | — |
| 1 | 1-2 weeks | 3 tools + data | — |
| 2 | 3-5 days | 3 tools | Concept + Outline |
| 3 | 2-6 months | 2 tools | Manuscript |
| 4 | 2-4 weeks | 2 tools | — |
| 5 | 3-5 days | 5 tools | Cover |
| 6 | 30 days | 6 tools | Launch go/no-go |
| 7 | Ongoing | 2 tools | — |
