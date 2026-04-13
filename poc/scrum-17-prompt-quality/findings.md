# SCRUM-17 findings

## Verdict
Overall verdict: usable with prompt tightening. The generated artifacts meet the ticket intent better than the placeholder prompt set in code, especially for culturally aware Growth topics and explicit puzzle validation notes.

## What worked
- Growth outputs stayed practical and specific instead of drifting into generic encouragement.
- The US/India family-finance example reflected cross-border realities like exchange rates, NRE/NRO context, and reporting friction.
- Knowledge outputs included a memorable surprising fact plus a brief explanation that reads more like a newspaper sidebar than a textbook excerpt.
- Fun outputs now carry explicit validation notes for riddle fairness, logic-puzzle uniqueness, sudoku consistency/solvability, and chess FEN legality.

## Representative examples
- Growth example: the salary negotiation piece separates base pay from RSUs, provident fund, gratuity, and relocation or tax effects, which is more useful than a generic “know your worth” answer.
- Knowledge example: the science item uses the biophoton fact to create surprise, then ties it back to the limits of human perception.
- Fun example: a logic puzzle explicitly explains why the answer is unique instead of merely stating the answer.

## Puzzle validity notes
- Sudoku: all three grids were checked for clue conflicts and paired with complete consistent solutions. The validation language claims solvability, but it does not prove uniqueness with a solver; if strict uniqueness is required, add automated checking.
- Chess: all three FENs are intentionally simple legal positions with both kings present and non-adjacent. They are legal, but the tasks are lightweight legality checks rather than rich tactical puzzles.
- Logic puzzles: each set includes a short uniqueness explanation to reduce ambiguity risk.
- Riddles: all are fair and recognizable, but they are familiar rather than novel.

## Prompt adjustment recommendations
1. Add explicit schema fields for validation, especially under Fun, instead of leaving validation as an unstated quality target.
2. Require “single-solution confirmed” for logic puzzles and “unique solution confirmed” for sudoku if the product truly needs solver-grade guarantees.
3. Ask for at least one culturally specific constraint or example in Growth outputs when the topic touches diaspora, relocation, or cross-border finances.
4. For Knowledge, require one “why this surprises people” angle so the surprising fact does not become a random trivia drop.
5. For Chess, clarify whether the product wants a legal position only or an actual tactic with a best move and solution line.
