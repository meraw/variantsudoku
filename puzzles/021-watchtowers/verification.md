# Verification report — Watchtowers

Generated 2026-11-14 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.17s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, the law of leftovers on jigsaw grids (run 9), whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 34, 2: 45, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- whole-constraint consistency: 28
- naked single: 25
- locked candidates: 11
- hidden single: 9
- subsets: 6

Whole-constraint steps that made progress: 28. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 90 steps, of which non-single steps by kind: Skyscraper (constraint step) 6, Pointing 2, Tuple 1

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** — 45 tier-2 rounds (method: 4). The opening is short: in the bottom-left corner, the column-3 skyscraper and the corner tower pin r9c1 = 6 within a few steps. After that, every tower needs case work on its four rays, and the rule is new.

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
- 022-mind-the-gap: rated 3/5, solved, tier rounds {1: 54, 2: 11, 3: 0}

## Extra checks for this puzzle

**New rule, new checks (run 11, `tools/soundness_run11.py`).** The lookout tower is new in `vs.py`: CP-SAT model (one
"still overlooked" flag per cell of each ray, chained outwards), checker (`lookout_view`), logic step (`gac_lookout`) and NFA
(`nfa.lookout_nfa`) for Rangsk's solver. The logic step lists every case (tower digit t, view length on each of the four rays)
that the candidates allow, and for each case checks the overlooked cells and blockers of the row, and of the column, as a
system of distinct representatives (overlooked cells take different digits below t, blockers different digits above t);
cells beyond a blocker are free. Results:
- the NFA accepts exactly the crosses whose view count equals the tower digit: 0 mismatches in 6,000 crosses
  (209 of them towers in the final run) over all 81 ray-length patterns;
- lookout logic never removed a true digit (30 random grids with every true tower marked, 159 towers, up to 6 givens);
- CP-SAT model and checker agree on 200/200 (cell, grid) pairs, half of them true towers.

**About Rangsk's path.** f-puzzles has no lookout rule, so Rangsk's solver gets each tower as an automaton read along
[tower, left ray, right ray, up ray, down ray]. Its state includes the digits used so far in the row part and in the
column part, so the automaton knows that those cells are all different, as a human does. These automata make the load string
longer than one command-line argument can be, so `rangsk.py` passes it through a file (a one-line local patch to
Rangsk's console program, described in `rangsk.py`). The play links show each tower as a cosmetic amber circle, so the apps
won't enforce the rule; the answer check still works because the solution is in the link.

**Every clue is needed for uniqueness** (CP-SAT, each clue removed in turn): without the tower in r4c2 there are 3 solutions,
without r1c7 2, without the 5 below column 5 4, without the 3 left of row 3 3, and removing any other clue leaves at least 50.

**Design method:** open-solution setting with `tools/open_lookout.py --sky --skybonus 0.4` (seed 4). There is no target grid.
Every free cell is scored as a tower, and every still-possible skyscraper count at every free outside position is scored too,
by the candidates my logical solver then removes. Skyscraper scores are multiplied by 0.4, so towers are preferred when they do
comparable work. Givens are allowed only when no clue makes progress, which never happened. Pruning removed nothing. Towers
on their own cannot finish a puzzle: a towers-only run stalled after 13 towers, when no further tower fitted anywhere.

**Facts used in the solve:** a tower is never 1 (nothing smaller to see) or 9 (it would overlook all 16 cells of its row and
column). A tower t overlooks at most t − 1 cells of its row (there are only t − 1 smaller digits), and likewise of its column,
so it overlooks at least one cell in each. A 2 tower therefore has a 1 next to it in its row and another next to it in its column.
An 8 tower is blocked only by 9s.

## Solution

```
149526783
567893214
328417569
976285431
815349672
234671958
783952146
491768325
652134897
```
