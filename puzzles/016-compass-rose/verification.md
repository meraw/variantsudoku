# Verification report — Compass Rose

Generated 2026-11-11 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.31s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 43, 2: 62, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- whole-constraint consistency: 45
- naked single: 31
- hidden single: 12
- locked candidates: 11
- subsets: 6

Whole-constraint steps that made progress: 45. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 128 steps, of which non-single steps by kind: Sandwich (constraint step) 21, Sum re-evaluated 12, Pointing 9, Tuple 3, TUVWXYZ-Wing 1, Region Forcing Chain (Region 6) 1
- note: the Rangsk path uses advanced techniques (listed above).

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** — 62 tier-2 rounds with my solver, no contradiction tests (just above the 4 band, so the method says 5). I rate it 4: Rangsk's solver needs only basic steps plus one TUVWXYZ-wing and one region forcing chain, far fewer than Pinwheel Whispers (rated 4 after feedback), and the opening (the compass forces r5c5 = 9) is gentle.

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

## Extra checks for this puzzle

**The idea.** Eight two-cell arrows leave one central circle, one in each compass direction. The first cell of every arrow lies in box 5,
so the eight first cells and the circle hold 1–9. If the circle were not 9, the 9 would be on a first cell, and that arrow would sum to
more than its circle. So **r5c5 = 9**, the first ring holds 1–8, and each outer cell is 9 minus the box-5 cell it touches. That gives row 5 and
column 5 their 9 for the sandwich sums.

**Drafts (the compass was fixed by hand; only the partner rule changed):**
- Compass + more arrows, grown by solver (`open_lines.py arrow`, three seeds): 7–8 extra arrows + 2–4 givens, random-looking.
- Compass + arrows in 4-fold rotation orbits (`orbit_grow.py`, new this run, straight arrows only, no crossings): two orbits + 4 givens, or
  5 givens with 180° pairs, and one seed stalled. Arrows alone carry too little.
- Compass + German whispers (`clean_grow.py`, new this run, clean straight/one-turn whispers, three seeds): 7–8 whispers + 2–5 givens, and the
  whispers ran over the compass. Not kept.
- **Compass + sandwich sums** (`open_outside.py --types sandwich`, five runs): with 180° pairs, 12 clues + 1 given (47 rounds); mixed with
  X-sums, 8 clues + 1 given, with two outside clue types that look alike; free placement, seeds 4 and 5, 9 clues + 1 given (35 and 55 rounds); **free
  placement, seed 1: 8 clues and no given (62 rounds). Kept.** The run added a ninth clue (20 above column 7), which pruning later found
  unnecessary, so it was dropped.
- Nothing inside the grid but the compass. All other information sits outside, like bearings.

Each constraint removed in turn (CP-SAT, limit 2; my logical solver up to tier 2):

| removed | solutions | logical solve |
|---|---|---|
| arrow N (r4c5, r3c5) | 2+ | stuck |
| arrow NE (r4c6, r3c7) | 2+ | stuck |
| arrow E (r5c6, r5c7) | 1 | stuck |
| arrow SE (r6c6, r7c7) | 2+ | stuck |
| arrow S (r6c5, r7c5) | 2+ | stuck |
| arrow SW (r6c4, r7c3) | 1 | stuck |
| arrow W (r5c4, r5c3) | 1 | stuck |
| arrow NW (r4c4, r3c3) | 2+ | stuck |
| sandwich 33, row 7 (right) | 2+ | stuck |
| sandwich 33, row 9 (left) | 2+ | stuck |
| sandwich 4, column 9 (bottom) | 2+ | stuck |
| sandwich 24, row 6 (right) | 2+ | stuck |
| sandwich 18, row 4 (right) | 2+ | stuck |
| sandwich 10, row 3 (left) | 2+ | stuck |
| sandwich 12, row 1 (right) | 2+ | stuck |
| sandwich 30, column 8 (top) | 2+ | stuck |

Every sandwich clue is needed for uniqueness. Three compass arrows (E, SW, W) are needed only for the logical path. They stay anyway,
because the rose is the picture.

**How the logic opens (in human terms).** The compass gives r5c5 = 9 at once. A sandwich of 33 is every digit from 2 to 8 except the 2 (they total 35). So the 1 and 9 enclose six cells, sit in columns 1 and 8 or in
columns 2 and 9, and the 2 is in the remaining end cell. This holds in both row 7 and row 9. In column 9, a sandwich of 4 can only be a single 4 between the 1 and the 9. My solver starts with those three clues and places the 2s and the
column-9 4 before it ever uses the compass. A human will probably take r5c5 = 9 first.

**Second opinion.** Rangsk's SudokuSolver knows arrows and sandwiches natively. Its logical path uses basic steps (sum checks, pointing,
tuples) plus one TUVWXYZ-wing and one region forcing chain. That is crunchier than 008 or 011 and much lighter than Pinwheel Whispers (28 forcing chains).

## Solution

```
879534126
621978435
345612897
796481253
452793681
138256974
217845369
563129748
984367512
```
