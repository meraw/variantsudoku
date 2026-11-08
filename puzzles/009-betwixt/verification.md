# Verification report — Betwixt

Generated 2026-11-08 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.71s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 34, 2: 39, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 27
- whole-constraint consistency: 26
- locked candidates: 8
- hidden single: 7
- subsets: 5

Whole-constraint steps that made progress: 26. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 112 steps, of which non-single steps by kind: Sandwich (constraint step) 13, Tuple 7, Pointing 6, Between Line (constraint step) 5

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** — 39 tier-2 rounds with my solver (method says 4), no contradiction tests. Rangsk's solver finishes it with tuples, pointing and constraint steps only (no fish, wings, chains), so the individual steps are not exotic; the work is in combining sandwich case lists (where can the 1 and 9 go, which digits can fill the gap) with the four lines. My ratings have historically run low (002), so no adjustment downwards. 4.

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
- 010-product-placement: rated 4/5, solved, tier rounds {1: 40, 2: 44, 3: 0}

## Extra checks for this puzzle

- The four between lines alone: at least 1000 solutions (search capped at 1000, status `FEASIBLE`).
- The ten sandwich clues alone (no lines): 20+ solutions (cap 20, status `FEASIBLE`). Both rules are needed.
- Without the between line r1c1–r4c4: 2+ solution(s) (`FEASIBLE`); my logical solver: stuck, tier rounds {1: 27, 2: 43, 3: 3}.
- Without the between line r9c9–r6c6: 2+ solution(s) (`FEASIBLE`); my logical solver: stuck, tier rounds {1: 26, 2: 35, 3: 20}.
- Without the between line r1c9–r3c7: 2+ solution(s) (`FEASIBLE`); my logical solver: stuck, tier rounds {1: 18, 2: 39, 3: 12}.
- Without the between line r4c6–r6c4: 2+ solution(s) (`FEASIBLE`); my logical solver: stuck, tier rounds {1: 34, 2: 38, 3: 0}.
- Without the sandwich 32 at r0c1: 1 solution(s) (`OPTIMAL`); my logical solver: solved, tier rounds {1: 50, 2: 57, 3: 5}; Rangsk logical: solved with 29 contradiction steps.
- Without the sandwich 8 at r0c4: 2+ solution(s) (`FEASIBLE`); my logical solver: stuck, tier rounds {1: 20, 2: 39, 3: 5}.
- Without the sandwich 4 at r0c6: 2+ solution(s) (`FEASIBLE`); my logical solver: stuck, tier rounds {1: 15, 2: 33, 3: 21}.
- Without the sandwich 31 at r0c7: 2+ solution(s) (`FEASIBLE`); my logical solver: stuck, tier rounds {1: 3, 2: 20, 3: 65}.
- Without the sandwich 15 at r0c8: 2+ solution(s) (`FEASIBLE`); my logical solver: stuck, tier rounds {1: 16, 2: 36, 3: 9}.
- Without the sandwich 25 at r1c0: 2+ solution(s) (`FEASIBLE`); my logical solver: stuck, tier rounds {1: 18, 2: 34, 3: 15}.
- Without the sandwich 21 at r2c0: 2+ solution(s) (`FEASIBLE`); my logical solver: stuck, tier rounds {1: 18, 2: 42, 3: 14}.
- Without the sandwich 22 at r5c0: 2+ solution(s) (`FEASIBLE`); my logical solver: stuck, tier rounds {1: 28, 2: 38, 3: 0}.
- Without the sandwich 16 at r8c0: 2+ solution(s) (`FEASIBLE`); my logical solver: stuck, tier rounds {1: 22, 2: 34, 3: 18}.
- Without the sandwich 33 at r9c0: 2+ solution(s) (`FEASIBLE`) (logical run skipped: not unique).
- Rangsk's logical solver is far stronger than mine on sandwich/between rules (fish, wings, AIC, forcing). The only clue it can do without is column 1's 32, and only with 29 contradiction steps, so that version was rejected.

## Solution

```
394768125
168529374
725314869
472981653
516243798
839657241
643192587
281475936
957836412
```
