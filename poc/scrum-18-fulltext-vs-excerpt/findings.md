# SCRUM-18 findings

## Verdict

**Yes, article fetching is justified, but selectively.**

Across these 3 articles, full-text input produced better summaries every time. The improvement was **small-to-moderate on simple ceremonial coverage**, and **large on policy/economics and geopolitics**, where excerpts removed the details that make a summary actually useful.

Average score:
- **Excerpt-only:** 4.3/10
- **Full-text:** 8.3/10
- **Average gain:** **+4.0 points**

## Recommendation

Use article fetching in the pipeline, but keep the fallback from SCRUM-13:
1. fetch full text
2. summarize from full text when available
3. fall back to excerpt when extraction fails

My recommendation is **go forward with fetching**. The quality lift is strong enough on consequential stories to justify the extra complexity, as long as the system degrades cleanly to excerpt-only.

## Evidence by article

### 1) The Hindu, Vivekananda statue in Seattle
**Scores:** excerpt 4/10, full text 7/10

**Why full text won:**
- Excerpt only said the unveiling was part of cultural diplomacy.
- Full text added the key news angle: **first life-size statue in the U.S. hosted by a city government**.
- Full text also added location and installation details.

**Take:** Better, but not transformative. This is the kind of story where excerpt-only may be acceptable if fetch fails.

### 2) BusinessLine, March retail inflation
**Scores:** excerpt 5/10, full text 9/10

**Why full text won:**
- Excerpt captured only the broad direction: inflation up from 3.2%.
- Full text added the expected range (**3.5%-4.0%**), the drivers (LPG, kerosene, services), and offsets (softer food prices).
- Full text made the summary more credible by adding analyst attribution and the official release timing.

**Take:** This is a strong argument for full-text fetch. Excerpt-only summary stays too generic.

### 3) BBC World, Hungary election
**Scores:** excerpt 4/10, full text 9/10

**Why full text won:**
- Excerpt only conveyed polling and turnout.
- Full text added the core stakes: **possible end of Orbán’s 16-year rule**, implications for **EU/Nato/Russia**, and reported voting irregularities.
- Full text enabled a real “why it matters” summary rather than a shallow race update.

**Take:** Fetching is clearly worth it for high-stakes international and political stories.

## Overall read

### Where full text matters most
- economics and policy
- elections and geopolitics
- any story where the “why it matters” is in the body, not the headline/excerpt

### Where excerpt-only is often adequate
- simple event or ceremony coverage
- brief corporate or product updates with limited nuance

## Bottom line

**Fetching is justified.**

Not because every story needs it, but because the stories that matter most to summary quality benefit a lot from it. The best production design is:
- **full text when available**
- **excerpt fallback when not**

## Artifacts

- `comparison.json`: side-by-side inputs, summaries, scores, and evidence for all 3 articles
