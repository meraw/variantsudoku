# Verification report — Twelve Pieces

Generated 2026-11-19 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.70s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, the law of leftovers on jigsaw grids (run 9), whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column; entropic/modular lines: every fill of the line, or for long lines the class pattern that repeats every three cells; battlefields (run 13): every pair of end digits with every set of digits for the overlap or gap, the rest of the row/column checked as perfect matchings); polydivisible lines (run 13): every fill of the line, pruned prefix by prefix; median clues (run 14): every ordered triple of the first three cells; counting circles (run 15): every set of digits the circles could use (its digits add up to the number of circles, and each digit d in it has d circles that could hold it with no two in one row, column or box), then a matching of circles to digits with exactly d circles per digit d; fifths lines (run 15, invented): every fill of the line, as for other neighbour-relation lines; double arrows (run 16): every pair of circle digits with every fill of the cells between, as for bridges with a sum in place of the product; innies/outies (run 16, the 45 rule, tried only when every other step is stuck): for a union of whole houses (k consecutive rows or columns, a box, two neighbouring boxes, a 2x2 block of boxes) take the totals of the killer cages inside it off 45 per house, optionally add whole cages that stick out (their outside cells then count negatively), and list the fills of the resulting virtual cage of at most 5 cells; tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 41, 2: 63, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 30
- whole-constraint consistency: 23
- locked candidates: 12
- pointing (general): 11
- hidden single: 11
- subsets: 10
- innies/outies: 7

Whole-constraint steps that made progress: 30. Steps after the first placed digit that enumerated more than 500 combinations: 4 — killer (750 combos, 4 cells solved), killer (10584 combos, 9 cells solved), killer (960 combos, 23 cells solved), killer (800 combos, 36 cells solved).
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 152 steps, of which non-single steps by kind: Pointing 34, Tuple 13, Sum re-evaluated 13, Killer Cage (constraint step) 11

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** — My method says 5 (63 tier-2 rounds, just over the 60 line), but every step is a standard killer move: cage combinations, the anti-king rule and innies/outies. Rangsk's solver finishes with pointing, tuples, cage steps and five innie/outie sums, with no wings, chains or contradiction tests, so I took one step off, as for 016. The innies/outies step is essential: without it my solver stalls at 620 candidates.

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
- 019-unlucky-for-some: rated 3/5, solved, tier rounds {1: 33, 2: 25, 3: 0}
- 020-leapfrog: rated 4/5, solved, tier rounds {1: 35, 2: 39, 3: 0}
- 021-watchtowers: rated 4/5, solved, tier rounds {1: 34, 2: 45, 3: 0}
- 022-mind-the-gap: rated 3/5, solved, tier rounds {1: 54, 2: 11, 3: 0}
- 023-trail-map: rated 3/5, solved, tier rounds {1: 73, 2: 37, 3: 0}
- 024-combination-lock: rated 4/5, solved, tier rounds {1: 31, 2: 48, 3: 0}
- 025-tartan: rated 3/5, solved, tier rounds {1: 28, 2: 24, 3: 0}
- 026-crossed-swords: rated 3/5, solved, tier rounds {1: 60, 2: 25, 3: 0}
- 027-long-division: rated 3/5, solved, tier rounds {1: 35, 2: 35, 3: 0}
- 028-happy-medium: rated 3/5, solved, tier rounds {1: 45, 2: 23, 3: 0}
- 029-counting-stars: rated 4/5, solved, tier rounds {1: 40, 2: 53, 3: 0}
- 030-tuning-fork: rated 3/5, solved, tier rounds {1: 53, 2: 31, 3: 0}

## Extra checks for this puzzle

- **The set is complete.** Each cage was matched against the 63 fixed orientations of the 12 free pentominoes
  (`tools/open_pento.py` asserts this before writing): F, I, L, N, P, T, U, V, W, X, Y and Z each appear exactly once.
  The cages cover 60 cells; 21 cells are uncaged.
- **Every cage is needed.** Remove any one of the twelve and CP-SAT finds a second solution (2+ solutions in all twelve
  cases), and my solver stalls at 133-575 candidates. So the set is minimal as well as complete.
- **The 45 rule is essential.** With the new innies/outies step switched off, my solver stalls at 620 candidates (it
  finishes only with 26 tier-3 contradiction tests). With it, it uses 7 innies/outies rounds and no contradiction tests.
  Rangsk's solver also needs its innie/outie sums: 5 of its steps are "Innie Sum" / "Innie/Outie" steps (the package
  summary above counts them under "Sum re-evaluated").
- **Soundness of the new step** (`soundness_run16.py`): on 30 random grids (every second one anti-king) with 8-20 random
  disjoint cages each, every 45-rule equation my solver built held on the true grid, and the solve never removed a true
  digit. The calibration counts of puzzles 001-030 are unchanged, because the step only runs when everything else is
  stuck (see the table above).
- **Anti-king export:** f-puzzles `antiking: true`, read natively by Rangsk; the cage colours are exported as cell colours.

## Solution

```
451269738
398571426
276483915
145392687
637814592
829657143
763148259
584926371
912735864
```
