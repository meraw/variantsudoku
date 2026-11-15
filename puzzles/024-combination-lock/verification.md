# Verification report — Combination Lock

Generated 2026-11-15 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.12s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, the law of leftovers on jigsaw grids (run 9), whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 31, 2: 48, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- whole-constraint consistency: 30
- naked single: 24
- locked candidates: 11
- hidden single: 7
- subsets: 7

Whole-constraint steps that made progress: 30. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 110 steps, of which non-single steps by kind: Pointing 11, Tuple 9, Sandwich (constraint step) 9

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** — 48 tier-2 rounds (method: 4), no contradiction tests and no case list over 500. Rangsk's solver logs only pointing, tuple and sandwich steps, but its lockout eliminations happen silently in the automaton filter (including the whole row-6 opening, which is done before its first logged step), so its log understates the work. A human needs a real case analysis to open row 6 (16 orders of the row survive the 28 sandwich and the top bar, and all of them put 1 and 5 on the corners), and then has to combine five lines that share diamonds. I kept the method's 4.

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

## Extra checks for this puzzle

**Lockout lines in the toolkit (run 12).** Lockout lines are an established rule, new to this gallery and to `vs.py`
(`{"type": "lockout", "cells": [diamond, ..., diamond]}`). CP-SAT: the diamonds' minimum and maximum differ by at least 4, and every
inner cell is fully reified as "below the minimum" or "above the maximum". Logic step `gac_lockout`: every pair of diamond digits
the candidates allow (differing by 4 or more) is tried. The inner cells keep only the digits outside the range, and the pair
survives only if every house holding two or more inner cells (or an inner cell plus a diamond) can still give them different
digits (a matching per house). The supports are unions over the surviving pairs, which is sound. Rangsk's solver has no native lockout
constraint, so each line reaches it as a small automaton read as [diamond, diamond, inner cells...] (`nfa.lockout_nfa`, 46 states).
The play links draw the lines as cosmetic slate lines with cosmetic squares turned 45° as diamonds, so the apps don't enforce
them. Sandwich sums and the cage are native.

Soundness (`tools/soundness_run12.py`): the lockout NFA accepts exactly the valid sequences (0 mismatches in 27,371 sequences:
all of length 2–4 plus 20,000 random ones of length 5–8). On 30 random grids with 178 random satisfied lockout lines (3–9 cells,
king-step paths) and random givens, the logic never removed a true digit. Model and checker agreed on 200/200 pairs.

**Design method.** The padlock was drawn by hand. The body is four lockout lines around rows 6–9, columns 3–7, meeting at
diamond corners, and the shackle is a fifth line arching over rows 3–5 between the body's top corners. The keyhole is a 2-cell
cage. A first version with a taller shackle (feet on the body corners, top on row 2) was infeasible. With the shackle,
the left side and the right side together, column 3 and column 7 had no room. Lowering the arch to row 3 fixed it. Then
`tools/open_clues.py` chose the keyhole total and sandwich clues openly (no target grid; seed 2 of six runs). Two runs needed
1 given each. Two finished with no givens, and I kept the one where the keyhole cage gets a total (in the other, the cage was
left without one).

**Every clue is needed.** Without any one sandwich clue, the keyhole total or any lockout line except the top bar, the puzzle has
2 or more solutions (9–30+). The top bar (r6c3–r6c7) is not needed for uniqueness, but the logical solve gets stuck without it.
It's also the line the opening is built on.

**The opening, checked by enumeration:** of all 9! orders of row 6, exactly 16 give a sandwich of 28, satisfy the top bar
(diamonds r6c3 and r6c7) and keep 7 and 9 out of r6c5 (the keyhole already uses them in column 5). In all 16 the diamonds are
1 and 5 and the bar holds 6, 7 and 8. So the shackle, which shares those diamonds, can only hold 6–9.

## Solution

```
573142698
962358147
814967352
628519734
759234861
341786529
237691485
496875213
185423976
```
