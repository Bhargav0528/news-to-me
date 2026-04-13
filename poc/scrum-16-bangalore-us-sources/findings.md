# SCRUM-16 findings

## Verdict

Yes, we now have working sources for both Bangalore/Karnataka local coverage and US general coverage.

Best result:
- **Bangalore/Karnataka:** Deccan Herald plus The New Indian Express Bengaluru/Karnataka
- **US general:** The Guardian US

## Evidence

### Bangalore/Karnataka

**Deccan Herald**
- The feed endpoint `https://prod-qt-images.s3.amazonaws.com/production/deccanherald/feed.xml` is valid.
- It is an **Atom** feed, not classic RSS, which is why the first parser check was wrong.
- Sample entries included both `Bengaluru` and `Karnataka` categories.
- Sampled article fetching worked with `trafilatura`.

**The New Indian Express Bengaluru**
- Feed is live and populated.
- Sampled article fetching worked on Bengaluru story URLs.

**The New Indian Express Karnataka**
- Feed is live and populated.
- Useful as state-level supplement.

### US general

**The Guardian US**
- Feed is live and high-volume.
- Sampled article fetching worked on multiple links.
- This is the cleanest US general winner from this POC run.

**Washington Post National**
- Feed is live.
- Sampled fetch reliability was weaker, so it should not be the primary choice.

## Recommendation

Use this source strategy:
1. **Primary Bangalore/Karnataka:** Deccan Herald
2. **Supplement Bangalore/Karnataka:** The New Indian Express Bengaluru + Karnataka
3. **Primary US general:** The Guardian US
4. **Do not rely on:** guessed Deccan Herald section RSS URLs, Bangalore Mirror candidate feed, Politico candidate feed, or Washington Post as the main US source

## Can Bangalore provide 5 to 10 stories per day?

Yes, likely.

Why:
- Deccan Herald feed had 20 current entries with local/state mix visible in the sample.
- The New Indian Express Bengaluru feed had 40 entries.
- The New Indian Express Karnataka feed had 40 entries.

That is enough inventory to support a daily local section.

## Risk notes

- Deccan Herald requires Atom parsing support, not just RSS item parsing.
- Washington Post is a backup at best because fetch reliability looked weaker.
- Some Deccan Herald stories may still vary in extractable text length, so excerpt fallback remains important.

## Bottom line

SCRUM-16 passes.

We now have viable local Bangalore/Karnataka coverage and at least one working US general source with both feed access and full-text extraction confirmed.
