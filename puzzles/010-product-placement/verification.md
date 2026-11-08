# Verification report — Product Placement

Generated 2026-11-08 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.01s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 40, 2: 44, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 32
- whole-constraint consistency: 28
- locked candidates: 10
- hidden single: 8
- subsets: 6

Whole-constraint steps that made progress: 28. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** — 44 tier-2 rounds with the current solver (method says 4). Most steps are short case lists on three-cell bridges (each is a×b = middle, or 1 – x – x); the two six-cell bridges need the biggest case analysis (54 and 106 fills), and the serpentine is a one-line 45-rule observation. No contradiction tests. New rule, so no adjustment downwards. 4.

Method (run 3 onwards; the solver now applies one whole-constraint step per round, easiest first, so round counts are higher than in runs 1-2): 1 = singles + pairwise only; 2 = up to 8 tier-2 rounds; 3 = 9-30 tier-2 rounds; 4 = 31-60 tier-2 rounds or 1-3 tier-3 tests; 5 = more, or not solved logically. Adjusted by at most one step for rule novelty / setter judgement (stated above).

Calibration against the earlier puzzles, re-solved with the same solver version:

- 001-speed-dial: rated 3/5, solved, tier rounds {1: 48, 2: 14, 3: 0}
- 002-pinwheel-whispers: rated 4/5, solved, tier rounds {1: 72, 2: 51, 3: 0}
- 003-knight-calls: rated 3/5, solved, tier rounds {1: 27, 2: 15, 3: 0}
- 004-picture-frame: rated 3/5, solved, tier rounds {1: 43, 2: 23, 3: 0}
- 005-centre-of-gravity: rated 4/5, solved, tier rounds {1: 43, 2: 38, 3: 0}
- 006-which-way-up: rated 2/5, solved, tier rounds {1: 41, 2: 6, 3: 0}
- 007-liber-abaci: rated 4/5, solved, tier rounds {1: 35, 2: 34, 3: 0}
- 008-good-fences: rated 3/5, solved, tier rounds {1: 62, 2: 14, 3: 0}

## Extra checks for this puzzle

- The twelve bridges without the two givens: 50+ solutions (cap 50, status `FEASIBLE`).
- Without the bridge r5c3–r5c7 (11 cells): 2+ solution(s) (`FEASIBLE`).
- Without the bridge r5c1–r4c3 (3 cells): 2+ solution(s) (`FEASIBLE`).
- Without the bridge r5c9–r6c7 (3 cells): 2+ solution(s) (`FEASIBLE`).
- Without the bridge r6c8–r6c9 (3 cells): 2+ solution(s) (`FEASIBLE`).
- Without the bridge r4c2–r4c1 (3 cells): 2+ solution(s) (`FEASIBLE`).
- Without the bridge r8c1–r6c2 (3 cells): 2+ solution(s) (`FEASIBLE`).
- Without the bridge r9c8–r7c9 (3 cells): 1 solution(s) (`OPTIMAL`); my logical solver: solved, tier rounds {1: 46, 2: 38, 3: 3}.
- Without the bridge r1c2–r3c1 (3 cells): 2+ solution(s) (`FEASIBLE`).
- Without the bridge r9c6–r8c5 (3 cells): 2+ solution(s) (`FEASIBLE`).
- Without the bridge r1c4–r2c5 (3 cells): 2+ solution(s) (`FEASIBLE`).
- Without the bridge r7c3–r9c3 (6 cells): 2+ solution(s) (`OPTIMAL`).
- Without the bridge r3c7–r1c7 (6 cells): 2+ solution(s) (`FEASIBLE`).
- Without the given r4c3 = 4: 2+ solution(s) (`FEASIBLE`).
- Without the given r9c9 = 5: 2+ solution(s) (`FEASIBLE`).

## Solution

```
926481357
875623491
431579628
314256789
289147563
567398214
693715842
152834976
748962135
```
