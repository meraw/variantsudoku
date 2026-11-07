# Verification report — Liber Abaci

Generated 2026-11-07 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.01s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, whole-constraint consistency (enumerate fills of one cage/line against current candidates); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 35, 2: 34, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 26
- whole-constraint consistency: 13
- hidden single: 9
- locked candidates: 8
- fibonacci parity: 7
- subsets: 6

Whole-constraint steps that made progress: 13. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** — 34 tier-2 rounds with the current solver (method says 4), just under Centre of Gravity (38) and Pinwheel Whispers (51; Elena needed forcing chains there). Every line step is a small seed list (at most 25 seed pairs for one line, usually under 16), and the Fibonacci parity pattern (odd-odd-even repeating) is used 7 times in combination with the four-evens-per-house count. No contradiction tests. 4.

Method (run 3 onwards; the solver now applies one whole-constraint step per round, easiest first, so round counts are higher than in runs 1-2): 1 = singles + pairwise only; 2 = up to 8 tier-2 rounds; 3 = 9-30 tier-2 rounds; 4 = 31-60 tier-2 rounds or 1-3 tier-3 tests; 5 = more, or not solved logically. Adjusted by at most one step for rule novelty / setter judgement (stated above).

Calibration against the earlier puzzles, re-solved with the same solver version:

- 001-speed-dial: rated 3/5, solved, tier rounds {1: 48, 2: 14, 3: 0}
- 002-pinwheel-whispers: rated 4/5, solved, tier rounds {1: 72, 2: 51, 3: 0}
- 003-knight-calls: rated 3/5, solved, tier rounds {1: 27, 2: 15, 3: 0}
- 004-picture-frame: rated 3/5, solved, tier rounds {1: 43, 2: 23, 3: 0}
- 005-centre-of-gravity: rated 4/5, solved, tier rounds {1: 43, 2: 38, 3: 0}
- 006-which-way-up: rated 2/5, solved, tier rounds {1: 41, 2: 6, 3: 0}

## Extra checks for this puzzle

- Without the givens: CP-SAT finds exactly **4** solutions (status `OPTIMAL`).
  - every digit × 9, last digit kept = the solution rotated by 180°
  - every digit × 3, last digit kept
  - every digit × 7, last digit kept
  - every digit × 1, last digit kept
- The solution is 180°-complement-symmetric (opposite cells sum to 10, the centre is 5): True. Spoiler for solvers; it is not implied by the rules.
- Without fibonacci from r6c1 (8 cells) + fibonacci from r4c9 (8 cells): 2 solution(s) (limit 2, `FEASIBLE`); logical solver: stuck, tier rounds {1: 1, 2: 2, 3: 0}.
- Without fibonacci from r9c6 (3 cells) + fibonacci from r1c4 (3 cells): 2 solution(s) (limit 2, `FEASIBLE`); logical solver: stuck, tier rounds {1: 25, 2: 32, 3: 6}.
- Without fibonacci from r6c2 (3 cells) + fibonacci from r4c8 (3 cells): 1 solution(s) (limit 2, `OPTIMAL`); logical solver: solved, tier rounds {1: 29, 2: 30, 3: 4}.
- Without fibonacci from r1c8 (5 cells) + fibonacci from r9c2 (5 cells): 2 solution(s) (limit 2, `FEASIBLE`); logical solver: stuck, tier rounds {1: 11, 2: 16, 3: 18}.
- Without fibonacci from r1c1 (3 cells) + fibonacci from r9c9 (3 cells): 2 solution(s) (limit 2, `FEASIBLE`); logical solver: stuck, tier rounds {1: 31, 2: 29, 3: 0}.
- Without the given r4c2 = 9: 1 solution(s) (`OPTIMAL`); logical solver: solved, tier rounds {1: 36, 2: 40, 3: 4}.
- Without the given r6c8 = 1: 1 solution(s) (`OPTIMAL`); logical solver: solved, tier rounds {1: 35, 2: 42, 3: 5}.
- Without the given r2c3 = 7: 1 solution(s) (`OPTIMAL`); logical solver: solved, tier rounds {1: 33, 2: 31, 3: 1}.
- Without the given r8c7 = 3: 1 solution(s) (`OPTIMAL`); logical solver: solved, tier rounds {1: 33, 2: 36, 3: 1}.
- Whole-constraint steps on Fibonacci lines try seed pairs (the first two digits fix the line). The size recorded for these steps is the number of seed pairs left by the candidates of the first two cells: the largest was 25, so no step came close to the 500-combination mark used for heavy steps.

## Solution

```
862437159
317925684
945168273
496813725
271654938
583792416
738249561
624581397
159376842
```
