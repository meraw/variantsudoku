# Verification report — Factor Tree

Generated 2026-11-12 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.01s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, the law of leftovers on jigsaw grids (run 9), whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 36, 2: 21, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 27
- whole-constraint consistency: 13
- subsets: 5
- hidden single: 5
- pair consistency: 4
- locked candidates: 3

Whole-constraint steps that made progress: 13. Steps after the first placed digit that enumerated more than 500 combinations: 4 — factor (18600435 combos, 5 cells solved), littlekiller (1152 combos, 8 cells solved), littlekiller (1200 combos, 12 cells solved), littlekiller (2304 combos, 29 cells solved).
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 107 steps, of which non-single steps by kind: Tuple 10, Pointing 7, Little Killer (constraint step) 5, Sum re-evaluated 4
- note (run 9): factor lines reach this solver as one binary-lookup constraint per neighbouring pair plus one NFA per line that accepts exactly the valid fills of that line (repeats ruled out where its cells see each other), so it can reason about a whole line the way a human lists its fills. Eliminations made by that line filter are not always written to the log.

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**3 / 5** — 21 tier-2 rounds (method: 3), no contradiction tests. The opening is a short case list on the 8-cell trunk and two 3-cell diagonal sums in boxes 1 and 3; Rangsk's solver also needs only tuples, pointing and sum checks.

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
- 018-flat-pack-city: rated 4/5, solved, tier rounds {1: 47, 2: 51, 3: 0}

## Extra checks for this puzzle

**Facts about factor lines used in setting** (enumerated by script, `tools/` style brute force over all digit sequences):
- Neighbour pairs allowed: 1 with anything; 2–4, 2–6, 2–8, 4–8, 3–6, 3–9. So 5 and 7 can only sit next to a 1, and 9 only next to 1 or 3.
- Lines of different digits (all cells in one house): 28 / 94 / 182 / 232 / 196 / 104 / 16 sequences for 2–8 cells, and none for 9.
- The 16 sequences of 8 cells are exactly: {5 or 7}, 1, then 9-3-6-2-{4,8}-{8,4}; or {5 or 7}, 1, then {4,8}-{8,4}-2-6-3-9; and reversals. The ninth digit of the house is the other of 5/7.
  So the trunk (column 5, rows 2–9) forces r1c5 ∈ {5, 7}: the star on top of the tree is a "lonely prime".
- Swapping 5↔7 or 4↔8 everywhere preserves every factor line, so factor lines alone can never be unique; the little killers break both symmetries.
- The large "factor (18600435 combos)" figure above is the raw candidate product of the trunk before its first step. Only 16 sequences
  are valid, and the step that used it (r4c5 ≤ 5 from the 14 diagonal) needs no enumeration from a human who knows the list above.

**Is every mark needed?** (each one removed in turn; CP-SAT for uniqueness, my solver for the tier-2 logic)

| removed | uniqueness | logic without it |
|---|---|---|
| trunk r2c5–r9c5 | 2+ solutions | stuck |
| branch r2c5–r4c3 | unique | stuck (27 tier-2 rounds) |
| branch r2c5–r4c7 | unique | solved (22 rounds) |
| branch r4c5–r7c2 | unique | solved (21 rounds) |
| branch r4c5–r7c8 | 2+ solutions | stuck |
| branch r6c5–r9c2 | 2+ solutions | stuck |
| branch r6c5–r9c8 | 2+ solutions | stuck |
| each of the six little killers | 2+ solutions | stuck |

Two branches (r2c5–r4c7 and r4c5–r7c2) are not needed at all, and one (r2c5–r4c3) only for the logic. I kept all three because a tree
with branches missing on one side doesn't look like a tree. They still constrain the grid, so they're not decoration.

**Rangsk without the line automata.** Fed only one binary-lookup constraint per neighbouring pair, so that it sees the lines
as pairwise relations only, Rangsk still finds exactly 1 solution and solves to the same grid, but it needs 26 contradiction tests and 12
cell-forcing-chain steps. It can't see the 8-cell trunk as a whole. With the whole-line automata (the version in the report above), it uses only
tuples, pointing and sum checks. A human who knows the 16 trunk sequences is in the second situation.

**Setting history:** the tree (trunk + six branches) was drawn by hand and never changed. The little killers were chosen by
`tools/open_lk.py`, open-solution style with no target grid: 13 runs in total. Of the eight free runs on diagonals of 3+ cells, seeds 1/3/4/7 finished with
6 clues and no given, seeds 2/5/8 with 7 clues, and seed 6 with 7 clues + 1 given. With 180° pairs it took 10 clues, left–right mirrored pairs
needed 8 clues + 1–2 givens, and diagonals of 4+ cells only needed 7–9 clues + 1 given. I kept seed 7. Its clues sit on all four sides of the grid
as generated, and its very low 14 on a long diagonal gives a clean break-in into the trunk.

## Solution

```
841576923
625389174
379241568
134925786
987164352
562738419
718693245
453812697
296457831
```
