# Verification report — Leapfrog

Generated 2026-11-13 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.37s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, the law of leftovers on jigsaw grids (run 9), whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 35, 2: 39, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- whole-constraint consistency: 33
- naked single: 28
- hidden single: 7
- locked candidates: 6

Whole-constraint steps that made progress: 33. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 86 steps, of which non-single steps by kind: Pointing 3, contradiction test 1, Tuple 1
- note: the Rangsk path uses advanced techniques (listed above).

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** — 39 tier-2 rounds (method: 4). A gentle chain opens row 1, columns 1 and 9, but the middle of the solve needs repeated case work on hop paths, and Rangsk's solver (with a weaker automaton view of the clue) needs one contradiction test.

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

## Extra checks for this puzzle

**New rule, new checks (run 10, `tools/soundness_run10.py`).** The frog clue is new in `vs.py`: CP-SAT model (a "lands here" flag per
cell), checker (`frog_sum`), logic step (an exact walk along the row/column, tracking the digits used and the position of the frog's
next landing, the same machinery as X-sums and skyscrapers) and NFA (`nfa.frog_nfa`) for Rangsk's solver. Results:
- the NFA accepts exactly the sequences whose frog sum is the total, for every total 9–17 (40,000 sequences each, with and without repeats): 0 mismatches;
- frog logic never removed a true digit (30 random grids with 6–14 frog clues from the grid and up to 6 givens);
- CP-SAT model and checker agree on 200/200 (clue, grid) pairs, half of them satisfied.

**About Rangsk's path.** f-puzzles has no frog clue, so Rangsk's solver gets each clue as an automaton over its row/column (state: cells
read, position of the next landing). Its automaton filter doesn't use the fact that the nine digits of the row are all different
(Rangsk's sudoku logic does that separately), so it is weaker than a human reading the clue. That is why it needs one contradiction test
where my solver needs none. The play links show the pads as cosmetic green circles with the total, so the apps won't enforce the rule.

**Every clue is needed for uniqueness** (CP-SAT, each clue removed in turn): removing the 11 left of row 7 leaves 10 solutions, and removing any
other clue leaves at least 50.

**Design method:** open-solution setting with `tools/open_outside.py --types frog --gthresh 1` (no target grid; every still-possible frog
total at every free position scored by the candidates my logical solver then removes; givens only if no clue makes any progress, which never
happened). Seed 6 of six runs (see the setter log), then the standard pruning pass: no clue could be dropped.

**Facts used in the opening:** if the frog's last landing is the c-th cell from its pad and holds digit d, it hops out to position c + d − 1, so
c + d = total + 1. A 16 therefore ends on an 8 in the far cell or a 9 in the next-to-far cell, and a 9 is never the first digit seen from a
pad with total ≥ 10.

## Solution

```
876319254
154826739
329457186
931785462
682941573
547632918
795268341
418593627
263174895
```
