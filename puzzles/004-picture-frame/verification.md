# Verification report — Picture Frame

Generated 2026-11-05 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.02s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), whole-constraint consistency (enumerate fills of one cage/line against current candidates); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 37, 2: 11, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 23
- hidden single: 8
- pair consistency: 6
- whole-constraint consistency: 4
- subsets: 4
- locked candidates: 3

Whole-constraint steps that made progress: 14. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**3 / 5** — 11 tier-2 rounds (method says 3), with no heavy enumerations. The key loop facts (every third cell of the frame has the same class, and the cells just outside each side are forced) are human-friendly, but my solver reaches them via pairwise steps and a large subset step, so a human may need some colouring of classes. 3.

Method: 1 = singles + pairwise only; 2 = up to 5 tier-2 rounds; 3 = 6-15 tier-2 rounds; 4 = more than 15 tier-2 rounds or 1-3 tier-3 tests; 5 = many tier-3 tests or not solved logically. Adjusted by at most one step for rule novelty / setter judgement (stated above).

## Solution

```
627159834
185374296
439862751
752486319
894531672
316927548
968745123
271693485
543218967
```
