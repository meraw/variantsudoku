# Verification report — Long Division

Generated 2026-11-17 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.02s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, the law of leftovers on jigsaw grids (run 9), whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column; entropic/modular lines: every fill of the line, or for long lines the class pattern that repeats every three cells; battlefields (run 13): every pair of end digits with every set of digits for the overlap or gap, the rest of the row/column checked as perfect matchings); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 35, 2: 35, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 27
- whole-constraint consistency: 24
- hidden single: 8
- locked candidates: 6
- subsets: 5

Whole-constraint steps that made progress: 24. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 100 steps, of which non-single steps by kind: Tuple 7, Sum re-evaluated 5, Pointing 5, Killer Cage (constraint step) 2

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**3 / 5** — 35 tier-2 rounds (the method says 4), no contradiction tests, and no case list over 500 (the line steps that made progress had 2-47 surviving fills). I lowered it one step: the opening is gentle (the three 5s are free, and the 11 cage under the top bracket gives 9 and 2 at once), and Rangsk's solver needs only tuples, pointing and one innie sum (45 rule). The divisibility checks never go beyond 6, so every test is a schoolbook rule (even, digit sum, last two digits, ends in 5). If divisibility arithmetic is new to you, it may feel like a 4.

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

## Extra checks for this puzzle

**Every clue is needed** (each removed in turn; CP-SAT counts solutions up to 50, my solver retries tiers 1-2):

| removed | solutions without it | logical solve without it |
|---|---|---|
| bracket r3c1–r1c5 | 50+ | stuck |
| bracket r6c3–r4c7 | 50+ | stuck |
| bracket r9c5–r7c9 | 50+ | stuck |
| cage 18 (r2c3–r2c5) | 50+ | stuck |
| cage 12 (r5c5–r5c7) | 7 | stuck |
| cage 17 (r8c7–r8c9) | 50+ | stuck |
| cage 11 (r1c2–r1c3) | 1 | stuck (needed for the logic only) |
| cage 8 (r3c4, r3c5, r4c5) | 50+ | stuck |
| cage 7 (r3c7–r3c8) | 50+ | stuck |
| cage 9 (r3c9–r4c9) | 4 | stuck |
| cage 17 (r5c1–r6c1) | 50+ | stuck |
| cage 8 (r1c7–r1c8) | 5 | stuck |

**Polydivisible-line steps are small.** From run 14 the report counts, for a polydivisible line, the fills that survive the
current candidates (before, it printed the raw product of candidate counts, which was in the hundreds of thousands here).
The five line steps that made progress had 38, 47, 4, 6 and 2 surviving fills. The lines have 6 cells, so no step ever needs
divisibility by 7 or 8.

**Soundness tests** (`tools/soundness_run14.py`, part 4): random grids with 1-3 random bracket-shaped polydivisible lines
(found by CP-SAT), random killer cages of the grid and 0-6 givens, solved to the tier-2 fixpoint: the true digit was never
removed (8 grids; random layouts with overlapping or impossible brackets were skipped). Polydivisible-line logic, its table and its Rangsk automaton were already tested in run 13 (`soundness_run13.py`).

**Rangsk's view of the lines:** each line goes to Rangsk's solver as an automaton (NFA) that accepts exactly the line's valid
fills, with repeats ruled out where its cells see each other. Its eliminations from those automata are mostly silent in the
log, so its step list understates the line work. Every other step it reports is a tuple, pointing, a cage step or one innie
sum (the 45 rule on row 1).

## Solution

```
392584176
185762349
476319528
237845691
951623784
864197235
719436852
643258917
528971463
```
