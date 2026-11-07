# Verification report — Good Fences

Generated 2026-11-07 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.01s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, whole-constraint consistency (enumerate fills of one cage/line against current candidates); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 62, 2: 14, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 29
- pair consistency: 22
- hidden single: 11
- whole-constraint consistency: 7
- locked candidates: 5
- subsets: 2

Whole-constraint steps that made progress: 7. Steps after the first placed digit that enumerated more than 500 combinations: 2 — renban (2700 combos, 5 cells solved), renban (1920 combos, 9 cells solved).
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**3 / 5** — 14 tier-2 rounds with the current solver (method says 3). Most of the work is pairwise: an unmarked edge removes both neighbours of a placed digit. The two five-cell L renbans need short case analysis (five consecutive digits with no two neighbours on the line consecutive). No contradiction tests. 3.

Method (run 3 onwards; the solver now applies one whole-constraint step per round, easiest first, so round counts are higher than in runs 1-2): 1 = singles + pairwise only; 2 = up to 8 tier-2 rounds; 3 = 9-30 tier-2 rounds; 4 = 31-60 tier-2 rounds or 1-3 tier-3 tests; 5 = more, or not solved logically. Adjusted by at most one step for rule novelty / setter judgement (stated above).

Calibration against the earlier puzzles, re-solved with the same solver version:

- 001-speed-dial: rated 3/5, solved, tier rounds {1: 48, 2: 14, 3: 0}
- 002-pinwheel-whispers: rated 4/5, solved, tier rounds {1: 72, 2: 51, 3: 0}
- 003-knight-calls: rated 3/5, solved, tier rounds {1: 27, 2: 15, 3: 0}
- 004-picture-frame: rated 3/5, solved, tier rounds {1: 43, 2: 23, 3: 0}
- 005-centre-of-gravity: rated 4/5, solved, tier rounds {1: 43, 2: 38, 3: 0}
- 006-which-way-up: rated 2/5, solved, tier rounds {1: 41, 2: 6, 3: 0}
- 007-liber-abaci: rated 4/5, solved, tier rounds {1: 35, 2: 34, 3: 0}

## Extra checks for this puzzle

- Without the givens: CP-SAT finds exactly **2** solutions (status `OPTIMAL`).
  - every digit d replaced by 10 − d = the solution rotated by 180°
  - the solution itself
- The solution is 180°-complement-symmetric (opposite cells sum to 10, the centre is 5): True. Spoiler for solvers; it is not implied by the rules.
- Without renban from r2c2 (5 cells) + renban from r8c8 (5 cells): 1 solution(s) (limit 2, `OPTIMAL`); logical solver: solved, tier rounds {1: 63, 2: 12, 3: 17}.
- Without renban from r4c6 (3 cells): 1 solution(s) (limit 2, `OPTIMAL`); logical solver: solved, tier rounds {1: 70, 2: 13, 3: 1}.
- Without the given r2c5 = 8: 1 solution(s) (`OPTIMAL`); logical solver: solved, tier rounds {1: 62, 2: 21, 3: 8}.
- Without the given r8c5 = 2: 1 solution(s) (`OPTIMAL`); logical solver: solved, tier rounds {1: 59, 2: 19, 3: 7}.
- Without the given r3c7 = 4: 1 solution(s) (`OPTIMAL`); logical solver: solved, tier rounds {1: 60, 2: 15, 3: 2}.
- Without the given r7c3 = 6: 1 solution(s) (`OPTIMAL`); logical solver: solved, tier rounds {1: 75, 2: 13, 3: 1}.
- The two renban steps flagged above as over 500 combinations are raw candidate products (2,700 and 1,920). When the line's own rules are applied (five consecutive digits, and no two neighbours along the L consecutive because no dot is drawn), only **3** fills survive each time. So these are short case lists, not forcing chains.

## Solution

```
518264739
364789152
792531468
925816374
481357926
637492581
246975813
859123647
173648295
```
