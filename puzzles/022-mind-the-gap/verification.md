# Verification report — Mind the Gap

Generated 2026-11-14 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.02s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, the law of leftovers on jigsaw grids (run 9), whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 54, 2: 11, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 25
- pair consistency: 20
- hidden single: 9
- locked candidates: 7
- whole-constraint consistency: 4

Whole-constraint steps that made progress: 4. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 206 steps, of which non-single steps by kind: Col Indexer (constraint step) 68, Direct Cell Forcing 24, Pointing 18, Cell Forcing Chain 6, contradiction test 5, Tuple 3, Finned Swordfish 1
- note: the Rangsk path uses advanced techniques (listed above).

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**3 / 5** — 11 tier-2 rounds (method: 3). The break-in is a counting idea, not arithmetic: each shaded column has one band free of whispers, so its 5 is there, and the band rule (one low, one middle, one high index per band) forces the middle digit of each whisper to its end. Rangsk's solver needs forcing chains and contradiction tests here (see below), so this is a firm 3 that may play as a 4 for a solver who misses the band rule.

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

## Extra checks for this puzzle

**1-5-9 indexing in the toolkit (run 11).** The rule is new to `vs.py`. It is a global flag (`"global": ["idx159"]`) expanded into
pairwise relations: in each row, the column-1/5/9 cell holds k exactly when the column-k cell holds 1/5/9. CP-SAT gets them as
allowed-pair tables, and the logical solver uses them in its tier-1 pairwise consistency. The export uses f-puzzles `columnindexer`
cells (columns 1, 5 and 9), which Rangsk's solver reads natively as its `ColIndexerConstraint`. Its answer is an independent check
that the export means the same rule. Soundness (`tools/soundness_run11.py`, test 4): 30 random 1-5-9 grids all pass the checker, and with random satisfied
whispers/thermos and 3–12 random givens, the tier-2 logic never removed a true digit.

**About Rangsk's path.** Rangsk's solver finds the same unique solution and solves it logically. Its path is much heavier than mine: about two dozen
direct cell-forcing steps, six forcing chains, a finned swordfish and five contradiction tests, where my solver needs none. Its indexer works through weak links between candidates. My solver applies the
indexing relations together with the whisper and thermometer pairs in every round of pairwise consistency, so it sees more at
once. Rangsk's whisper is also only a pairwise rule, so it can't see fact 3 below (the middle digit sits at
the end of a 3-cell whisper in a shaded column), which needs the three cells to differ. A human who spots the facts below should find
a 3. One who doesn't may find it plays like a 4.

**Every line is needed** (CP-SAT and the logical solver, each line removed in turn): eight of the ten lines are needed for uniqueness
(2–25 solutions without each). The whispers r1c1–r3c1 and r1c9–r3c9 are not needed for uniqueness, but the tier-2 solve gets stuck
without either, so they stay. They also complete the picture.

**Design method:** a hand-drawn core of six 3-cell whispers on the shaded columns, two bands per column, leaving column 1's bottom band,
column 5's top band and column 9's middle band free (a staircase of gaps). Then `tools/clean_grow.py --straight --ortho --nogivens`
with whispers and thermos (seed 36 of six runs) added four straight lines, and pruning removed nothing. Before the core, free growth
of whispers (with or without the indexing columns) either needed givens or stalled.

**Facts used in the solve:**
1. A German whisper never holds a 5. Each shaded column has one band without a whisper, and the column's 5 must be there.
2. In each band, the three cells of a shaded column hold one digit from each of 1–3, 4–6 and 7–9. That's because they point at the
   1s (or 5s, or 9s) of three rows of the band, which sit in three different boxes.
3. So a 3-cell whisper in a band of a shaded column holds a low, a middle and a high digit. The middle one can't be 5, so it is a 4 or a 6.
   A 4 needs a 9 next to it and a 6 needs a 1, so the middle digit sits at an end of the whisper.

## Solution

```
381259746
962784351
475136298
893547612
127693485
654821937
219478563
546312879
738965124
```
