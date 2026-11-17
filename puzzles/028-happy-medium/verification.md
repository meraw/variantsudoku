# Verification report — Happy Medium

Generated 2026-11-17 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.02s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, the law of leftovers on jigsaw grids (run 9), whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column; entropic/modular lines: every fill of the line, or for long lines the class pattern that repeats every three cells; battlefields (run 13): every pair of end digits with every set of digits for the overlap or gap, the rest of the row/column checked as perfect matchings); polydivisible lines (run 13): every fill of the line, pruned prefix by prefix; median clues (run 14): every ordered triple of the first three cells; tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 45, 2: 23, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 23
- pair consistency: 12
- whole-constraint consistency: 10
- hidden single: 10
- locked candidates: 7
- subsets: 6

Whole-constraint steps that made progress: 19. Steps after the first placed digit that enumerated more than 500 combinations: 6 — median (576 combos, 1 cells solved), median (576 combos, 2 cells solved), whisper (49152 combos, 7 cells solved), whisper (15552 combos, 7 cells solved), whisper (10368 combos, 7 cells solved), whisper (5184 combos, 7 cells solved).
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 136 steps, of which non-single steps by kind: Direct Cell Forcing 35, Tuple 13, Pointing 6, AIC 1
- note: the Rangsk path uses advanced techniques (listed above).

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**3 / 5** — 23 tier-2 rounds (method: 3), no contradiction tests. The report lists six steps over 500 combinations, but those are raw products of candidate counts: the two median steps had 32 surviving fills each, and four steps on 8-cell stretches of the face loop had 140-707 surviving fills. Those loop steps are the hardest part; a human does them with the high/low alternation and pairwise reasoning rather than a list. Rangsk's solver needs one AIC (an alternating chain) besides direct cell forcings, tuples and pointing, so expect one spot that asks for a short chain. I kept the method's 3.

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

## Extra checks for this puzzle

**Every clue and line is needed** (each removed in turn; CP-SAT counts solutions up to 50, my solver retries tiers 1-2):

| removed | solutions without it | logical solve without it |
|---|---|---|
| face outline (24-cell whisper loop) | 50+ | stuck |
| smile (5-cell whisper) | 50+ | stuck |
| left eye (r3c4–r4c4) | 50+ | stuck |
| right eye (r3c6–r4c6) | 7 | stuck |
| median 5 below column 8 | 9 | stuck |
| median 5 below column 3 | 1 | stuck (needed for the logic only) |
| median 4 above column 5 | 3 | stuck |
| median 2 right of row 7 | 1 | stuck (needed for the logic only) |
| median 4 left of row 4 | 2 | stuck |

**Median clues are new to the toolkit this run** (`tools/soundness_run14.py`, parts 1-3):
- the automaton sent to Rangsk for a median clue accepts exactly the ordered triples of different digits with that middle
  value (0 mismatches in 5,103 triple/clue checks);
- median logic, with German whispers that the grid satisfies, never removed a true digit (30 random grids, 6-16 clues each,
  0-10 givens);
- the CP-SAT model and the checker agreed on 100/100 (clue, grid) pairs.

**A bug caught on the way:** my f-puzzles export for Rangsk sent a looped whisper as an open line (the closing pair r2c2–r1c3
was missing). Rangsk then reported several solutions for this puzzle while CP-SAT reported one. With the loop closed, Rangsk
also finds exactly one. No earlier puzzle sent a loop to Rangsk natively; I re-checked 004 Picture Frame (an entropic loop)
with the fix and it is still unique for Rangsk.

**Speed fix:** whole-line enumeration of the 24-cell whisper loop made each logical solve take minutes. Lines of a neighbour
rule longer than 8 cells are now checked as overlapping 8-cell windows when the full candidate product is over 5 million
(a sound relaxation: any valid fill of the line is valid on every window).

## Solution

```
563917284
891342675
247658931
724183569
158496723
936725148
379564812
485271396
612839457
```
