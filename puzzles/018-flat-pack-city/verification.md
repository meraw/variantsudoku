# Verification report — Flat-Pack City

Generated 2026-11-12 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.04s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, the law of leftovers on jigsaw grids (run 9), whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 47, 2: 51, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 35
- whole-constraint consistency: 21
- locked candidates: 14
- hidden single: 12
- leftovers: 10
- subsets: 4
- pointing (general): 2

Whole-constraint steps that made progress: 21. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 122 steps, of which non-single steps by kind: Skyscraper (constraint step) 20, Pointing 13, Region Forcing Chain (Row 3) 3, Tuple 2, Finned X-Wing 1, Region Forcing Chain (Region 7) 1, contradiction test 1
- note: the Rangsk path uses advanced techniques (listed above).

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** — 51 tier-2 rounds (method: 4), no contradiction tests in my solver; the law of leftovers does real work. Rangsk's solver needs a finned X-wing, four region forcing chains and one contradiction test, so it is crunchy but well short of a 5.

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

## Extra checks for this puzzle

**The regions.** Each region is a 3×3 box with jigsaw-puzzle features on its inner edges. A *tab* is a cell of one region that sticks into the neighbouring box,
at the middle of the shared edge, and the neighbour has a matching *slot*. I searched every layout (CP-SAT) where tabs are 1 or 2 cells deep,
every region keeps 9 cells and stays connected, and a region with a 2-deep slot has no other slot. A region with two 1-cell slots must have them on opposite
sides, because otherwise its corner cell would be cut off. At most 10 of the 12 inner edges can carry a feature, and 12 layouts reach 10. This is one of the two
left–right mirror-symmetric ones (the other is the same flow reversed): tabs climb the outer columns, and the centre column slides down one region (two 2-deep tabs).

Law of leftovers on these regions (the tab/slot cells that must match):
- rows 1–3: {r4c5, r5c5} = {r3c2, r3c8}; rows 7–9: {r6c2, r6c8} = {r7c5, r8c5};
- columns 1–3: r8c3 = r2c4; columns 7–9: r2c6 = r8c7;
- plus the corresponding larger sets for rows 1–2 / 8–9 and the centre bands (my solver uses all of them, sets of up to 4 cells).

**Is every clue needed?** (each one removed in turn; CP-SAT for uniqueness, my solver for the tier-2 logic)

| removed | uniqueness | logic without it |
|---|---|---|
| skyscraper 7 (row 1, right) | 2+ solutions | stuck |
| skyscraper 5 (column 5, bottom) | 2+ solutions | stuck |
| skyscraper 6 (row 4, left) | 2+ solutions | stuck |
| skyscraper 4 (row 4, right) | 2+ solutions | stuck |
| skyscraper 4 (column 5, top) | **unique** | stuck (21 tier-2 rounds) |
| skyscraper 5 (column 4, top) | 2+ solutions | stuck |
| skyscraper 5 (row 3, right) | 2+ solutions | stuck |
| skyscraper 6 (column 2, bottom) | 2+ solutions | stuck |
| skyscraper 3 (column 3, bottom) | 2+ solutions | stuck |
| skyscraper 7 (row 8, left) | 2+ solutions | stuck |

The 4 above column 5 is needed only for a solve without guessing. The law-of-leftovers step made progress in 10 of the 51 tier-2 rounds, so
the jigsaw shapes are part of the logic, not just the picture.

**Setting history:** the regions came first. Then I tried four partners on them, each placed open-solution style with no target grid:
- region-sum lines, free shapes (`clean_grow.py`, 2 seeds): 7–8 lines + 3 givens, random hooks;
- region-sum lines around a hand-drawn core (two "balance" lines on rows 2 and 8 plus column 5), straight only (2 seeds): 6 lines + 3–5 givens;
- German whispers, straight (2 seeds): 6–8 lines + 3–4 givens;
- thermometers, straight (2 seeds): 7 lines + 3 givens, only 4–6 tier-2 rounds (too easy);
- skyscrapers only (`open_outside.py --types skyscraper`, 4 seeds): **10 clues + 0 givens (seed 1, kept)**, 11 + 1, 8 + 1, 8 + 2. With 180° pairs:
  14 + 2 twice. X-sums + skyscrapers (2 seeds): 10 and 9 clues, no givens. Not kept, because I wanted one clue type.

## Solution

```
987216543
316547298
492783651
123459876
674895312
568172934
859364127
245631789
731928465
```
