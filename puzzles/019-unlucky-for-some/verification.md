# Verification report — Unlucky for Some

Generated 2026-11-13 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.02s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, the law of leftovers on jigsaw grids (run 9), whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 33, 2: 25, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 27
- whole-constraint consistency: 20
- hidden single: 6
- subsets: 3
- locked candidates: 2

Whole-constraint steps that made progress: 20. Steps after the first placed digit that enumerated more than 500 combinations: 1 — littlekiller (22674816 combos, 4 cells solved).
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 88 steps, of which non-single steps by kind: X-Sum (constraint step) 3, Sum re-evaluated 3, Tuple 1

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**3 / 5** — 25 tier-2 rounds (method: 3). The opening is a single crisp count on the 8-cell diagonal, and Rangsk's path has no fish, wings, chains or contradiction tests, but three X-sum 13s and two more little killers need real case work later.

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
- 009-betwixt: rated 4/5, solved, tier rounds {1: 34, 2: 39, 3: 0}
- 010-product-placement: rated 4/5, solved, tier rounds {1: 40, 2: 44, 3: 0}
- 011-skyline-sums: rated 4/5, solved, tier rounds {1: 34, 2: 35, 3: 0}
- 012-are-we-there-yet: rated 4/5, solved, tier rounds {1: 52, 2: 35, 3: 0}
- 013-zip-it: rated 4/5, solved, tier rounds {1: 51, 2: 35, 3: 0}
- 014-carry-the-one: rated 4/5, solved, tier rounds {1: 27, 2: 35, 3: 0}
- 015-newtons-cradle: rated 3/5, solved, tier rounds {1: 46, 2: 40, 3: 0}
- 016-compass-rose: rated 4/5, solved, tier rounds {1: 43, 2: 62, 3: 0}
- 017-factor-tree: rated 3/5, solved, tier rounds {1: 36, 2: 21, 3: 0}
- 018-flat-pack-city: rated 4/5, solved, tier rounds {1: 47, 2: 51, 3: 0}

## Extra checks for this puzzle

**The flagged little-killer step is a count, not a case list.** The ">500 combinations" figure above is the raw candidate product of the
8-cell diagonal from the top-right corner. A human handles it with one minimum-sum argument: the diagonal crosses boxes 3, 2, 5, 4 and 7
with 2, 1, 2, 1 and 2 cells, so its smallest possible total is (1+2)+1+(1+2)+1+(1+2) = 11. The 13 cage forces r2c7 ≥ 4, so the box-3 pair
is at least 1+4 and the minimum rises to exactly 13. Every cell then sits at its minimum: r1c8 = 1, r2c7 = 4 (so r1c7 = 9), r3c6 = 1,
r6c3 = 1, {r4c5, r5c4} = {1, 2}, {r7c2, r8c1} = {1, 2}.

**Every clue is needed for uniqueness** (CP-SAT, each clue removed in turn, up to 50 solutions searched):

| clue removed | solutions without it |
|---|---|
| little killer, top-right corner (8 cells) | ≥50 |
| cage r1c7–r2c7 | ≥50 |
| little killer below column 3 (6 cells) | ≥50 |
| X-sum right of row 6 | ≥50 |
| X-sum below column 1 | ≥50 |
| X-sum above column 4 | ≥50 |
| cage r5c3–r5c5 | ≥50 |
| little killer above column 5 (4 cells) | ≥50 |
| cage r2c5–r3c5 | 3 |

**Design method (run 10, `tools/open_fixed.py`):** every clue value was fixed at 13 in advance. The script only chose *positions*. Each
step scored every still-possible cage (2–3 cells, never touching another cage), little-killer diagonal (3+ cells) and X-sum position by
how many candidates my logical solver then removes, committed one of the top three after a CP-SAT feasibility check, and stopped when the
solver finished. No givens were allowed. Nothing was pruned: all nine clues survived the necessity check above.

## Solution

```
458372916
172689435
936451872
583724691
629138547
741596283
815963724
264817359
397245168
```
