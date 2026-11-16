# Verification report — Tartan

Generated 2026-11-16 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.09s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, the law of leftovers on jigsaw grids (run 9), whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column; entropic/modular lines: every fill of the line, or for long lines the class pattern that repeats every three cells; battlefields (run 13): every pair of end digits with every set of digits for the overlap or gap, the rest of the row/column checked as perfect matchings); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 28, 2: 24, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- whole-constraint consistency: 19
- naked single: 18
- pair consistency: 9
- locked candidates: 3
- subsets: 2
- hidden single: 1

Whole-constraint steps that made progress: 19. Steps after the first placed digit that enumerated more than 500 combinations: 1 — modular (17280 combos, 11 cells solved).
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 104 steps, of which non-single steps by kind: Direct Cell Forcing 9, Skyscraper (constraint step) 8, Pointing 5, Tuple 1

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**3 / 5** — 24 tier-2 rounds (method: 3), no contradiction tests, no case list over 500. Rangsk's solver, which knows entropic and modular lines natively, finds it light (pointing, one tuple, direct cell forcings and skyscraper steps). The human work is the class bookkeeping: which class is low, middle or high on each tartan row, and which residue each tartan column carries; the skyscrapers label the classes. I kept the method's 3.

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

## Extra checks for this puzzle

**Design.** The lines were drawn first, as a plaid: full-length entropic lines on rows 2, 5 and 8 and full-length
modular lines on columns 2, 5 and 8. CP-SAT says this weave is feasible, while a variant with an entropic column 5 and
a modular row 5 (crossing the other type) is infeasible. The lines alone leave 1,000+ solutions (count stopped there),
and no class is labelled: any relabelling of the three entropic classes among themselves and of the three modular classes
among themselves maps solutions to solutions on the lines, so outside information is needed. Skyscraper clues were then
chosen by `open_outside.py --types skyscraper --gthresh 1` (open-solution setting, no target grid, givens only if no clue
makes progress). Eight skyscraper seeds were run: 6 clues and no givens (seed 7, kept), 9 clues and no givens (seeds 5, 9, 10;
36-46 tier-2 rounds), 5-10 clues plus one given (seeds 3, 6, 8) and 12 clues + 1 given with 180° pairs (seed 11).
X-sums gave 5 clues with no givens (seed 1), but Rangsk needed contradiction tests and wings there. Thermometers grown inside
the plaid (`clean_grow.py`, 4 seeds) needed 2-3 givens and were easy (7-11 rounds), or stalled without givens.

**A structural fact the solver can use.** Each tartan row has the same entropic class in its columns 2, 5 and 8 (they are
three apart on the line), and each tartan column has the same modular class in rows 2, 5 and 8. So the nine box centres
hold three digits of one entropic class per row and three of one modular class per column, i.e. all nine digits laid out
like a phone keypad with its rows and columns shuffled. In the solution the centres read 987 / 321 / 654.

**Clue necessity.** Without the 8 left of row 1: 50+ solutions. Without the 5 left of row 8: 8 solutions. Without the 4
below column 1: 7. Without the 4 below column 4 or the 3 above column 9: 2 each. The 6 above column 1 is not needed for
uniqueness, but without it my solver stalls at 533 candidates (it needs 13 contradiction tests at tier 3), so it stays.
With it, the column-1 pair 6 + 4 = 10 says that every digit of column 1 is seen from one end or the other: the column climbs
to its 9 in row 6 and then falls.

**Toolkit (run 13).** Entropic and modular lines were already in `vs.py` (004 used an entropic loop), but this is the
first puzzle with modular lines. Rangsk's solver reads both natively (`entropicline` / `modularline` in its f-puzzles parser),
so `rangsk.py` now sends them natively. The play links show them as cosmetic coloured lines. `soundness_run13.py` part 3:
random grids satisfying random straight entropic/modular lines plus six random skyscraper clues, solved to the tier-2
fixpoint, never lost the true digit (17 grids). The grid picture draws the lines as a weave (`"weave": true` in the spec:
over and under alternate box by box at the crossings); that is cosmetic only.

## Solution

```
124567893
593482671
678319452
752134968
836925714
941876325
485791236
367258149
219643587
```
