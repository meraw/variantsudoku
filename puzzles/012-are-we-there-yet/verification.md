# Verification report — Are We There Yet?

Generated 2026-11-09 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.19s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 52, 2: 35, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 32
- whole-constraint consistency: 29
- hidden single: 20
- locked candidates: 6

Whole-constraint steps that made progress: 29. Steps after the first placed digit that enumerated more than 500 combinations: 1 — odometer (706 combos, 6 cells solved).
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 223 steps, of which non-single steps by kind: contradiction test 105, line check (constraint step) 20, Pointing 10, Tuple 3, AIC 1, Unorthodox Tuple (6) 1, Unorthodox Tuple (5) 1, VWXYZ-Wing 1
- note: invented line rules reach this solver as NFA constraints (tools/nfa.py). Its NFA filter checks each line against the candidates but ignores that cells of a line sharing a house must differ, so it falls back on contradiction tests far more often than a human (or my solver) would need to.
- note: the Rangsk path uses advanced techniques (listed above).

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** — 35 tier-2 rounds with my solver (method says 4), no contradiction tests. One step after the first placed digit lists 706 fills. With every odometer step capped at 300 fills, the solve still finishes (33 tier-2 rounds), so the big step can be avoided. Rangsk's solver needs many contradiction tests here, but its NFA encoding ignores repeats within a line, so I don't use it for the rating. New rule; no adjustment. 4.

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

## Extra checks for this puzzle

How the lines were placed (run 6, `tools/open_lines.py base.json out.json 4 odometer 0 5 8 --givens`): there was no target grid.
At each step the script drew random king-move paths of 5–8 cells, with the circle at the first cell, on cells not yet used.
It kept the paths that at least one sampled grid satisfies, scored them by how many candidates my logical solver then
removes, and committed one of the best three after a CP-SAT feasibility check. Givens were allowed as a fallback, but none
was needed. Nine lines in, the logical solver finished, which also proves uniqueness. Pruning found nothing removable.

Each line removed in turn (CP-SAT, limit 2; logical solver up to tier 2):

| line removed (circle) | cells | solutions |
|---|---|---|
| r3c8 | 7 | 2+ |
| r8c9 | 7 | 2+ |
| r1c9 | 5 | 2+ |
| r1c1 | 5 | 2+ |
| r1c5 | 7 | 2+ |
| r9c2 | 5 | 2+ |
| r4c2 | 5 | 2+ |
| r6c6 | 6 | 2+ |
| r6c8 | 5 | 2+ |

Every line is needed for uniqueness.

Case-list sizes. The default solve below has one step after the first placed digit with more than 500 fills (706, on the r6c6 line).
To check that a solver doesn't need such big case lists, I capped every odometer step at 300 surviving fills (bigger steps
are skipped, as a human would skip them): the puzzle is still **solved** at tier 2 (33 tier-2 rounds, no contradiction
tests). With a cap of 200 the solver can't start at all. The opening steps are case lists of 200–300 fills, and they
establish the general facts below.

The rule's general facts, as a human would use them (proved in the setter's note; checked by enumeration over all
digit sequences):
- the tip (last cell) of every odometer is even, because the total distance has the parity of (circle − tip);
- a two-cell odometer has tip = 2 × circle; a three-cell odometer c–x–e has e = 2x if x < c, and e = 2c or 2(x − c) if x > c;
- a line whose cells all see each other: 9 cells → only 9-8-7-6-5-4-3-1-2; 8 cells → circle 8 or 9 (15 sequences).

Symmetry: replacing every digit d by 10 − d keeps all differences but changes the circle, so unlike Fibonacci lines or
renban/kropki there is no built-in twin solution, and no given is needed to break one.

## Solution

```
752198346
913456287
468372195
286547913
379821564
145639872
834965721
521784639
697213458
```
