# Verification report — Counting Stars

Generated 2026-11-18 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.27s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, the law of leftovers on jigsaw grids (run 9), whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column; entropic/modular lines: every fill of the line, or for long lines the class pattern that repeats every three cells; battlefields (run 13): every pair of end digits with every set of digits for the overlap or gap, the rest of the row/column checked as perfect matchings); polydivisible lines (run 13): every fill of the line, pruned prefix by prefix; median clues (run 14): every ordered triple of the first three cells; counting circles (run 15): every set of digits the circles could use (its digits add up to the number of circles, and each digit d in it has d circles that could hold it with no two in one row, column or box), then a matching of circles to digits with exactly d circles per digit d; fifths lines (run 15, invented): every fill of the line, as for other neighbour-relation lines; tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 40, 2: 53, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- whole-constraint consistency: 37
- naked single: 30
- locked candidates: 10
- hidden single: 10
- subsets: 6

Whole-constraint steps that made progress: 37. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 81 steps, of which non-single steps by kind: none

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** — 53 tier-2 rounds, so the method says 4. The counting circles carry most of the global reasoning: which digits the 15 circles can use and how often. No 9 (row 7 has no circle), no 8 (eight rows would force r2c9 and r8c6, leaving row 4 without a free circle), and later no 3/4 and no 6. Not lowered: the solver comes back to the digit-set question several times.

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
- 030-tuning-fork: rated 3/5, solved, tier rounds {1: 53, 2: 31, 3: 0}

## Extra checks for this puzzle

- **Counting circles reach Rangsk's solver as one automaton** (`nfa.counting_nfa`) over all 15 circles in a fixed order. Its
  state counts how many circles so far hold each digit, and only states from which the rule can still be met are kept
  (3,313 live states for 15 circles). `soundness_run15.py` checks that it accepts exactly the valid sequences
  (0 mismatches in 12,000 checks). Rangsk's automaton filter runs before its first logged step and does the counting work
  silently, so its logged path is singles only. That path is a uniqueness cross-check, not a difficulty signal.
- **Soundness of the new logic step** (`soundness_run15.py`): counting-circle logic, with between lines and sandwich sums
  of the grid, never removed a true digit (30 random grids); the CP-SAT model and the checker agreed on 60/60 counting
  checks.
- **What each element does** (remove it, count solutions with CP-SAT up to 50, re-run my solver to tier 2):
  - every sandwich is needed for uniqueness (without the 31: 41 solutions, the 2: 21, the 11: 9) except the 33, which is
    needed for the logic;
  - between lines: four are needed for uniqueness (without Betelgeuse–Alnitak 4 solutions, Alnitak–Saiph 27,
    Mintaka–Rigel 3, Bellatrix–shield 5), four more for the logic (Bellatrix–Mintaka, the belt, the club, the lower
    shield), and **three are not needed at all**: Meissa–Betelgeuse, Meissa–Bellatrix and the top of the shield
    (r2c9–r4c9). I kept them so the figure stays whole;
  - the three faint stars cannot be removed: without any one of them the sky has no solution.
- **Digit set of the solution:** the 15 circles hold one 1, two 2s, five 5s and seven 7s.

## Solution

```
352471869
948536712
761298543
583162497
174953286
629784135
497615328
236847951
815329674
```
