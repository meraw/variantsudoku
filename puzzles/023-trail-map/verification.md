# Verification report — Trail Map

Generated 2026-11-15 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.04s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, the law of leftovers on jigsaw grids (run 9), whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 73, 2: 37, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 30
- whole-constraint consistency: 25
- pair consistency: 23
- hidden single: 20
- locked candidates: 10
- subsets: 2

Whole-constraint steps that made progress: 25. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 102 steps, of which non-single steps by kind: Maximum (constraint step) 10, Pointing 4, Tuple 4, Direct Cell Forcing 3

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**3 / 5** — 37 tier-2 rounds (method: 4). I took one off: Rangsk's solver needs only 10 summit-cell steps, 4 pointing steps, 4 tuples and 3 direct cell forcings, and every step is a short ordering argument (bigger than, smaller than), with no case lists over 500. The opening is a counting idea (where can the 9s go?). The new negative half of the rule (every unmarked cell has a bigger neighbour) is what a first-time solver must get used to, so it may feel like a 4 at first.

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
- 024-combination-lock: rated 4/5, solved, tier rounds {1: 31, 2: 48, 3: 0}

## Extra checks for this puzzle

**Complete summit maps in the toolkit (run 12).** The rule is new to `vs.py` (`{"type": "summits", "cells": [...]}`). The
marked cells get pairwise "smaller than" relations with each orthogonal neighbour (tier 1 handles them). Every unmarked cell
gets an auxiliary group [cell, its orthogonal neighbours]: some neighbour must be larger. CP-SAT gets the same as fully
reified booleans. My first model reified only one direction, so solution enumeration counted the free booleans as different
solutions and a growth run "failed" uniqueness. A fixed-grid test (full grid as givens → exactly 1 solution) now guards
against that. The logic step `gac_notext` keeps a digit of the unmarked cell only if some neighbour can still beat it, and a
neighbour's digit only if the cell still has a supported digit (it does not require two neighbours to differ, a sound
relaxation). The independent checker recomputes the whole summit map from the grid and compares it with the marked cells.
Rangsk's solver gets the marked cells natively as f-puzzles `maximum` cells and every unmarked cell as an 11-state NFA over
[cell, neighbours] (`nfa.notext_nfa`), so it checks the complete-map rule too.

Soundness (`tools/soundness_run12.py`): the NFA accepts exactly the right sequences (0 mismatches in 34,580); on 30 random
grids with their complete summit map, valley map or both (plus 0–12 random givens) the logic never removed a true digit;
model and checker agreed on 200/200 (map or line, grid) pairs.

**Design method.** The map came first, drawn by hand: two nested mountain ridges (a big Λ from r5c1 up to r1c5 and down to
r5c9, a smaller one from r9c2 up to r6c5 and down to r9c8). A CP-SAT search showed that this picture needs exactly two more
summits. With one of them in a top corner area (r1c1, r1c2, r2c1 or their mirrors), only r1c1 + r2c9, r1c1 + r8c5, r1c1 + r8c9
and their mirror images work. I chose the two "stars"
in the sky, r1c1 and r2c9, so the lower half shows only the ridges. The map alone leaves very many solutions (more than
1,000), but it already places seven 9s and two 8s logically.
Then `tools/clean_grow.py --tips --straight --nogivens` added thermometers that must end on a summit (a trail climbing to a
peak), never pass another summit and are straight. Of eight runs with straight trails, two finished (seed 13 with eight
trails, seed 16 with five); the other six ran out of room for a clean trail. I kept seed 16. Pruning removed nothing.
Earlier runs on the same map with bent trails (one turn allowed) finished in four of eight runs (the four that let trails share a summit tip), with 5–6 trails and 44–64 rounds, but looked cluttered.

**Every trail is needed.** Without any one of the five thermometers the puzzle has 3 or more solutions (30+ for four of them),
and the logical solver gets stuck.

**Facts used in the solve:**
1. A 9 is always a summit, so every 9 sits on a marked cell. Row 6 has only one summit, so r6c5 = 9.
2. An unmarked 8 must touch a 9. Unmarked cells far from any summit can't be 8 (or 9).
3. With r6c5 = 9, column 5 rules out r1c5, so row 1's 9 is r1c1. The rest follows box by box: r3c7, r4c2, r5c9, r8c3, r9c8.
4. A thermometer ending on a summit makes its tip larger than everything on the trail and around the tip.

## Solution

```
954783216
627915438
318642975
195326784
842157369
763498152
236879541
479561823
581234697
```
