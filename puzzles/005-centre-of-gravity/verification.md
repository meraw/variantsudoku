# Verification report — Centre of Gravity

Generated 2026-11-06 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.01s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, whole-constraint consistency (enumerate fills of one cage/line against current candidates); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 43, 2: 38, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 34
- whole-constraint consistency: 13
- seesaw bounds: 11
- hidden single: 9
- subsets: 7
- locked candidates: 7

Whole-constraint steps that made progress: 13. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** — 38 tier-2 rounds with the current solver (method says 4). That puts it between Picture Frame (23) and Pinwheel Whispers (51; Elena needed forcing chains there). Most seesaw progress comes from simple min/max bounds. The rest needs small case lists, at most 56 balancing fills for one line and usually under 20, which feels like working out killer-cage combinations with weights. No contradiction tests. 4.

Method (run 3 onwards; the solver now applies one whole-constraint step per round, easiest first, so round counts are higher than in runs 1-2): 1 = singles + pairwise only; 2 = up to 8 tier-2 rounds; 3 = 9-30 tier-2 rounds; 4 = 31-60 tier-2 rounds or 1-3 tier-3 tests; 5 = more, or not solved logically. Adjusted by at most one step for rule novelty / setter judgement (stated above).

Calibration against the earlier puzzles, re-solved with the same solver version:

- 001-speed-dial: rated 3/5, solved, tier rounds {1: 48, 2: 14, 3: 0}
- 002-pinwheel-whispers: rated 4/5, solved, tier rounds {1: 72, 2: 51, 3: 0}
- 003-knight-calls: rated 3/5, solved, tier rounds {1: 27, 2: 15, 3: 0}
- 004-picture-frame: rated 3/5, solved, tier rounds {1: 43, 2: 23, 3: 0}

## Extra checks for this puzzle

- The nine seesaws without any givens: CP-SAT finds exactly **2** solutions (status `OPTIMAL`). With no givens the logical solver (tiers 1-2) places 0 digits.
- Without the given r2c3: 1 solution(s) found (limit 2, `OPTIMAL`); logical solver (tiers 1-2): stuck.
- Without the given r3c1: 1 solution(s) found (limit 2, `OPTIMAL`); logical solver (tiers 1-2): stuck.
- Without the given r9c6: 1 solution(s) found (limit 2, `OPTIMAL`); logical solver (tiers 1-2): stuck.
- Without the given r5c8: 1 solution(s) found (limit 2, `OPTIMAL`); logical solver (tiers 1-2): stuck.

## Solution

```
895764231
126359874
743128695
312485967
964217358
578693412
287931546
459876123
631542789
```
