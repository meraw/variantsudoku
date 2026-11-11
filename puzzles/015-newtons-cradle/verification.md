# Verification report — Newton's Cradle

Generated 2026-11-11 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.02s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 46, 2: 40, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 37
- whole-constraint consistency: 25
- locked candidates: 10
- hidden single: 9
- subsets: 5

Whole-constraint steps that made progress: 25. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 81 steps, of which non-single steps by kind: line check (silent NFA filter step) 1, Tuple 1
- note: Rangsk's NFA constraint removes candidates without writing a step description; its logger then prints 'reported the board was invalid without specifying why' (SolverLogic.cs). The solve continues and reaches the CP-SAT grid, so these are silent line-filter steps, not errors.

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**3 / 5** — 40 tier-2 rounds with my solver (the method says 4), no contradiction tests. I rate it one lower: every line step is a lookup in a short list (at most 56 sequences for a 4-cell pendulum, usually under 15), and Rangsk's solver, given exact per-line automata, needs almost nothing beyond singles. The rule is new, so the first few steps take some getting used to.

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

## Extra checks for this puzzle

**The rule and its facts.** A pendulum line is read from its circle (the resting digit c). The other digits sit alternately above
and below c, and each is strictly closer to c than the one before. Enumerated before setting (`vs.PENDULUM_SEQS`):
- A line's digits are always all different (the distances to c are), so a pendulum behaves like a small cage for repeats.
- Lengths: 3 cells allow 68 sequences, 4 cells 32, 5 cells only 6, and 6 or more cells none (a 5th swing would need c ≥ 6 and c ≤ 5
  at once). A random fixed 4-cell line is satisfied by 0.5% of digit strings, so each long pendulum carries about 7.7 bits.
- A 4-cell pendulum has its circle in 3–7. **Circle 7 forces the tail 9, 6** (7, x, 9, 6 with x ≤ 4) and **circle 3 forces 1, 4**.
- The rule is unchanged by d → 10 − d, so pendulums alone always leave solutions in twins. At least one given is needed.

**Toolkit (run 8).** New constraint type `pendulum` (`{"type": "pendulum", "cells": [circle, ...]}`): CP-SAT table constraint over the
valid sequences, checker, logic step (the valid sequences of the line filtered by the candidates), SVG (slate line, white circle with a
pivot pin) and f-puzzles export (cosmetic line + circle). For Rangsk's solver it is an NFA (`nfa.pendulum_nfa`, state = circle digit,
side and size of the last swing). `tools/soundness_run8.py`: the NFA accepts exactly the valid sequences for every length 2–5
(0 mismatches); over 40 random grids with 12 random satisfied pendulum/palindrome lines and up to 6 random givens, the logical solver
never removed a true digit; CP-SAT model and checker agreed on 400 of 400 (line, grid) pairs.

**How it was set.**
1. Hand-drawn core: a Newton's cradle. Five 4-cell pendulums hang from row 1 in columns 4–8. The left one is lifted: it runs diagonally
   from r1c4 down to r4c1.
   - Five *straight* adjacent 4-cell pendulums from row 1 are **infeasible**. So are five 5-cell ones, and nine 3-cell ones in a row
     (circles of 3+ cells can never be 1 or 9).
   - With the left ball lifted, the core is feasible, and its five circles in row 1 must be exactly {3, 4, 5, 6, 7}.
2. Free growth (`open_lines.py pendulum --hang --givens`, vertical lines only, six seeds): all finished with 11–14 lines and
   2–3 givens (34–45 rounds), but the lower half looked scattered. One seed reached exactly the twin pair without givens (14 lines), yet
   **no single given** made it logically solvable. A single given placed first, before growth, stalled in both tries (no room left for lines).
3. Designed lower half: a second bar of pendulums hanging from row 6. I sampled 180 random bars (`bars.py`: columns and lengths
   3/4/5, from row 5 or 6) and kept those leaving ≤ 40 solutions. Then I tested every pair of givens that makes the solution unique
   (`pairgiv.py`) with my logical solver.
   - Bar c1/c4/c5/c7/c9 (16 solutions): 5,984 unique pairs, 44 solvable, the best at 35 rounds (two givens in circles).
   - **Bar c1/c5/c7/c8/c9 (12 solutions): 2,418 unique pairs, 18 solvable.** The best (40 rounds) is r2c4 = 6 + r4c8 = 6. Neither
     given sits in a circle. Kept.

Each line and given removed in turn (CP-SAT, limit 2; my logical solver up to tier 2):

| removed | solutions | logical solve |
|---|---|---|
| lifted pendulum r1c4–r4c1 | 2+ | stuck |
| pendulum r1c5 | 2+ | stuck |
| pendulum r1c6 | 2+ | stuck |
| pendulum r1c7 | 2+ | stuck |
| pendulum r1c8 | 2+ | stuck |
| pendulum r6c1 | 2+ | stuck |
| pendulum r6c5 | 2+ | stuck |
| pendulum r6c7 | 2+ | stuck |
| pendulum r6c8 (3 cells) | 2+ | stuck |
| pendulum r6c9 (3 cells) | 2+ | stuck |
| given 6 at r2c4 | 2+ | stuck |
| given 6 at r4c8 | 1 | stuck |

Every line is needed for uniqueness. The r4c8 given is needed only for the logical path.

**How the logic opens** (my solver's first steps, in human terms): the given 6 in row 4 means no 4-cell pendulum ending in row 4 can
have circle 7, because circle 7 needs a 6 at the tip, except the r1c8 pendulum, whose tip is that 6. The three circles in box 2 can't be 6 either
(the 6 at r2c4), so they are 3, 4, 5. Row 1's circles are {3, 4, 5, 6, 7}, so r1c7 and r1c8 are 6 and 7, and r1c7 can't be 7: r1c7 = 6 and r1c8 = 7.
The r1c8 line then reads 7, x, 9, 6, and the r1c7 line 6, x, 8, 5.

**Second opinion.** Rangsk's solver gets each pendulum as an NFA. Its filter is exact for a single line, and a pendulum's digits are
always different anyway. With that, Rangsk solves the puzzle with very few named steps: almost everything is singles after silent line
filtering. Read this as "each line step is a simple lookup", which is part of why I rate it below my round count.

## Solution

```
982435671
751689234
463712895
318947562
245863917
697251348
134598726
876324159
529176483
```
