# Verification report — Knight Calls

Generated 2026-11-05 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.02s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), whole-constraint consistency (enumerate fills of one cage/line against current candidates); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 31, 2: 8, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 16
- pair consistency: 11
- hidden single: 4
- locked candidates: 3
- whole-constraint consistency: 2
- pointing (general): 2
- subsets: 1

Whole-constraint steps that made progress: 8. Steps after the first placed digit that enumerated more than 500 combinations: 4 — killer (512 combos, 1 cells solved), killer (512 combos, 1 cells solved), knight (2304 combos, 1 cells solved), knight (2304 combos, 1 cells solved).
(Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**3 / 5** — 8 tier-2 rounds (method says 3). The four heavy enumerations listed above happen with only the centre 5 placed and amount to 'four cells of a line in one box are four consecutive ring digits' plus two cage-sum checks, which is easy once you have drawn the ring. The rule is new and the anti-knight checks are easy to overlook, so I kept it at 3 rather than 2.

Method: 1 = singles + pairwise only; 2 = up to 5 tier-2 rounds; 3 = 6-15 tier-2 rounds; 4 = more than 15 tier-2 rounds or 1-3 tier-3 tests; 5 = many tier-3 tests or not solved logically. Adjusted by at most one step for rule novelty / setter judgement (stated above).

## Solution

```
438569712
761234589
952781634
387492165
216357498
549816327
674923851
125678943
893145276
```
