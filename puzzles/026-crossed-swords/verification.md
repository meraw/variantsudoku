# Verification report — Crossed Swords

Generated 2026-11-16 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.16s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, the law of leftovers on jigsaw grids (run 9), whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column; entropic/modular lines: every fill of the line, or for long lines the class pattern that repeats every three cells; battlefields (run 13): every pair of end digits with every set of digits for the overlap or gap, the rest of the row/column checked as perfect matchings); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 60, 2: 25, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 31
- pair consistency: 17
- whole-constraint consistency: 12
- hidden single: 12
- locked candidates: 8
- subsets: 5

Whole-constraint steps that made progress: 12. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 104 steps, of which non-single steps by kind: Direct Cell Forcing 14, Tuple 5, Pointing 4

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**3 / 5** — 25 tier-2 rounds (method: 3), no contradiction tests, no case list over 500. Rangsk's solver (battlefield clues as automata that track the digits used) solves it with direct cell forcings, tuples and pointing; its battlefield eliminations happen inside the automaton filter. Battlefield arithmetic is unfamiliar to many solvers and every clue needs a small case split over the two end digits, so it could play harder than the count says, but I kept the method's 3.

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

## Extra checks for this puzzle

**Battlefield in the toolkit (run 13).** Battlefield is an established rule, new to this gallery and to `vs.py`
(`{"type": "battlefield", "from": "r0c3", "sum": 30}`). With first digit a and last digit b, the counted cells are the
indices from min(a, 9 − b) to max(a, 9 − b) − 1: the overlap when a + b > 9 and the gap when a + b < 9 (none when a + b = 9).
The end cells themselves count only when the other army covers them (a or b is 9). CP-SAT: that range with fully reified
"inside" flags per cell. Logic step `gac_battlefield`: every pair (a, b) the candidates allow and every set of digits that
can fill the range with the clue's total; the range cells and the other cells are then checked as perfect matchings, as for
sandwiches, so the step is exact for one row or column. Rendering: a dark red total under small crossed swords. Export: f-puzzles
has no battlefield entry, so each clue is a cosmetic circle with the total at the outside position, and the rules text carries
the rule. Rangsk's solver gets one NFA per clue (`nfa.battlefield_nfa`): the far army b is guessed at the start, and the
state tracks the digits used, so the filter knows that the row's digits differ. My first version tracked only the running sum;
with it Rangsk found two four-clue drafts unique but stalled after twelve contradiction tests each. With the used digits it
solves every draft of this run with singles, pointing, tuples and direct cell forcings.

Soundness (`tools/soundness_run13.py`): the battlefield NFA accepts exactly the rows of nine different digits with the right total
(0 mismatches in 23,033 row/total checks, including 4,000 sequences with repeats); the battlefield logic never removed the true
digit (30 random grids with 6–14 clues and 0–10 givens); model and checker agreed on 100/100 (clue, grid) checks, and a full grid
as givens gives exactly one solution.

**Design.** The swords came first. Each blade is a German whisper from a top corner to row 7; the blades cross in r5c5. Each
hilt is a crossguard through the blade's last cell plus a grip to the bottom corner. Drafts (CP-SAT feasibility):
- both full diagonals as whispers (an X): feasible; with whisper crossguards as well: **infeasible**;
- whisper blades + whisper crossguards + whisper grips: infeasible; + Dutch grips: feasible;
- **whisper blades + Dutch crossguards + Dutch grips: feasible. Kept**, because the hilts read as one piece.

Then `open_outside.py --types battlefield --sides TL --gthresh 1` (clues only on the top and left, since a battlefield clue
reads the same from both ends; givens only if no clue makes progress) chose the clues with no target grid. Runs:
- the plain X: 6 and 7 clues, no givens (13–26 tier-2 rounds);
- whisper crossguards + Dutch grips: 4 clues each (9–12 rounds), no givens;
- Dutch hilts (five seeds): 6 clues / 23 rounds, 5 / 12, 4 / 10, 5 / 20 and **6 clues / 28 rounds (seed 5, kept; 25 rounds with the clues listed in reading order)**, all with
  no givens. I kept the one with the most work in it.

**A fact for the solver.** The blades cross in box 5, so r5c5 has four whisper neighbours that all sit in box 5 and must
differ. A 2 would need four different digits from 7–9, so r5c5 is 1 or 9, and its four diagonal neighbours are 6, 7, 8, 9 or
1, 2, 3, 4. My solver does not see this directly (it needs the two lines together) and reaches it later by other means.

**What is needed.** Lines alone: 1,000+ solutions (count stopped there). Without the battlefield clue above column 3 there are
20+ solutions; without 35 (column 4) or 17 (row 9), 2 each. The 1 (column 1), the 36 (row 1) and the 37 (row 8) are not needed for
uniqueness but are needed for my logical solve. Every line is needed except the left grip (r7c3–r9c1): without it the
puzzle is still unique and still solves logically. I kept it for the picture.

## Solution

```
149385762
376291485
582476319
613749528
728513946
495628173
831964257
254837691
967152834
```
