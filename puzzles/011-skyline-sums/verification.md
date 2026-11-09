# Verification report — Skyline Sums

Generated 2026-11-09 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.03s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 34, 2: 35, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 27
- whole-constraint consistency: 24
- locked candidates: 8
- hidden single: 7
- subsets: 3

Whole-constraint steps that made progress: 24. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 111 steps, of which non-single steps by kind: Skyscraper (constraint step) 15, X-Sum (constraint step) 8, Tuple 4, Pointing 3

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** — 35 tier-2 rounds with my solver (method says 4), no contradiction tests. Rangsk's solver finishes it with only X-sum/skyscraper re-evaluations, tuples and pointing (no contradictions, wings, fish or chains), so each step is fair. The work is in combining the X-sum case lists with the skyscraper counts. 4.

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
- 012-are-we-there-yet: rated 4/5, solved, tier rounds {1: 52, 2: 35, 3: 0}

## Extra checks for this puzzle

How the clue set was made (run 6, `tools/open_outside.py`, seed 6, `--sym --mixpairs --bonus skyscraper=2.2`): no target grid;
clues were added in 180°-opposite pairs (types may differ), each chosen from the totals still possible in sampled grids, by
how many candidates my logical solver could then remove. Plain candidate counts favour X-sums, so skyscraper moves had
their score multiplied by 2.2. Without a bonus, all four runs that finished used X-sums almost only (at most one skyscraper).

After the script: the left clue of row 5 (X-sum 45, which only says r5c1 = 9) was removed, because the puzzle stays unique
and logically solvable without it (the script prunes pairs together, so it had kept it). The only clue that could stand
there is a disguised given (X-sum 45 or skyscraper 1), so that position stays empty. Then the skyscraper 3 above column 2
turned out to be redundant on its own and was removed too. 12 clues remain.

Each clue removed in turn (CP-SAT, limit 2; logical solver up to tier 3):

| clue removed | solutions | my logical solver |
|---|---|---|
| X-sum 37 above column 5 | 2+ | stuck |
| X-sum 32 below column 5 | **1** | solved only with 3 contradiction tests |
| X-sum 8 above column 4 | 2+ | stuck |
| skyscraper 7 below column 6 | 2+ | stuck |
| skyscraper 7 right of row 5 | 2+ | stuck |
| skyscraper 6 right of row 4 | 2+ | stuck |
| skyscraper 2 left of row 6 | 2+ | stuck |
| skyscraper 4 right of row 2 | 2+ | stuck |
| X-sum 15 left of row 8 | 2+ | stuck |
| X-sum 29 above column 7 | 2+ | stuck |
| skyscraper 5 below column 3 | 2+ | stuck |
| skyscraper 4 below column 8 | 2+ | stuck |

So every clue except one is needed for uniqueness, and that one (column 5's 32 from below) is needed for a solve without
contradiction tests.

## Solution

```
468279513
719653842
523418796
231987654
987546321
654132978
146395287
375824169
892761435
```
