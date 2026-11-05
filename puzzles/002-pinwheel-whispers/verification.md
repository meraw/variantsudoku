# Verification report — Pinwheel Whispers

Generated 2026-11-04 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.01s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), whole-constraint consistency (enumerate fills of one cage/line against current candidates); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 50, 2: 18, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 31
- pair consistency: 10
- hidden single: 9
- locked candidates: 8
- whole-constraint consistency: 6
- subsets: 4

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** (revised 2026-11-05, run 2). Originally rated 3/5: "18 tier-2 rounds (method says 4), but most are routine cage-combination and whisper high/low steps on familiar rules; adjusted down one step to 3."

Revision: the owner's test-solve needed a few forcing chains, and the sudokucoach solver could not finish it. Looking back at the
trace, mid-solve whole-whisper enumerations of 1,000–6,000 combinations against partly-filled candidates did work that a human
does with chains. So the downward adjustment was wrong, and the rating goes back to what the method said: 4.

Method: 1 = singles + pairwise only; 2 = up to 5 tier-2 rounds; 3 = 6-15 tier-2 rounds; 4 = more than 15 tier-2 rounds or 1-3 tier-3 tests; 5 = many tier-3 tests or not solved logically. Adjusted by at most one step for rule novelty / setter judgement (stated above).

## Solution

```
549721638
723896154
618435729
285674391
936152487
174983562
392547816
867319245
451268973
```
