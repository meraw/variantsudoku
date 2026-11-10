# Verification report — Carry the One

Generated 2026-11-10 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.33s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 27, 2: 35, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 22
- whole-constraint consistency: 20
- locked candidates: 8
- subsets: 7
- hidden single: 5

Whole-constraint steps that made progress: 20. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 81 steps, of which non-single steps by kind: Tuple 2, line check (silent NFA filter step) 1
- note: Rangsk's NFA constraint removes candidates without writing a step description; its logger then prints 'reported the board was invalid without specifying why' (SolverLogic.cs). The solve continues and reaches the CP-SAT grid, so these are silent line-filter steps, not errors.

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** — 35 tier-2 rounds with my solver (method says 4), no contradiction tests. Every step is one sum checked against the candidates (at most 32 of the 336 sums survive at any step), plus singles and locked candidates. Rangsk's solver, given the sums as automata that know the digits differ, solves it with line-consistency steps, two tuples and singles. The arithmetic is unusual for sudoku and may play harder than its round count suggests, so I considered a 5; I kept 4 because no step needs more than one sum at a time.

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

## Extra checks for this puzzle

**The rule and its facts.** A marked row or column holds 1–9 once each, so it is the classic puzzle "ABC + DEF = GHI using each
digit once". By enumeration there are 336 such sums. All of them have these properties, and all are easy to prove by hand:
- **the result's digits sum to 18** and the two addends' digits to 27 (casting out nines: digit sums drop by 9 per carry, and 45 is odd);
- **exactly one carry** happens, either out of the units or out of the tens (168 sums each), never out of the hundreds;
- the result's hundreds digit is at least 4.

**Toolkit (run 7).** New constraint type `equation` (`{"type": "equation", "line": "r3", "result": 2}`), with a CP-SAT model, a checker,
a logic step (the 336 sums filtered by the current candidates), SVG output (red + and = circles on the box borders) and f-puzzles export
(cosmetic circles with the symbol as text). For Rangsk's solver, the sum is an NFA read in schoolbook order (units column, tens, hundreds), whose
state carries the carry and **the set of digits already used**. I checked by simulation over all 9! orders that it accepts exactly the 336 sums. A first
version without the used-digit set accepted the same 336 permutations, but Rangsk's line filter then didn't know the pandigital property,
and it couldn't solve this puzzle logically.

**How it was set.**
1. Feasibility. Random sets of marked rows/columns are usually **infeasible**. In a search for grids with as many sum lines as possible, the best
   had 8 (4 rows + 4 columns, rows 1/4/6/7 and columns 1/2/6/7). A 9- or 10-line grid wasn't found within the time limit.
   - Those 8 lines leave 4 solutions: two independent binary ambiguities, so at least two givens. Logic-guided greedy givens
     needed 3, and no pair of givens is logically solvable. A working draft, but the line pattern looks arbitrary.
2. Designed patterns. I tested each pattern with the orientations left free.
   - Frame + cross (rows and columns 1, 5, 9): all 64 orientations are feasible; the best leaves 157 solutions.
   - Rows and columns 4–6, and three rows of one band with three columns of one stack: **infeasible**.
   - Odd rows and columns (1, 3, 7, 9): 5,760 solutions over 12 orientations. Even ones (2, 4, 6, 8): 112 over 8.
   - **Rows 1, 3, 5, 7, 9 + columns 1, 5, 9**: only **2** of the 256 orientations are feasible (they are the same layout with bands 1 and 3
     swapped), with exactly **3** solutions each. I kept the first.
3. "Carry the One": only 1s as givens.
   - In this layout a **single** given 1 (r2c2) already makes the solution unique. But my solver can't start, and Rangsk needs
     53 contradiction tests. Not fair.
   - The same happened in frame + cross: one orientation is unique with a single 1, yet with all nine 1s placed, both solvers still get stuck. Abandoned.
   - Here, I tested every set of the solution's 1-positions. No pair is logically solvable. Eight triples are, with 10 to 37 tier-2 rounds.
     I chose r2c2 + r3c9 + r7c8 (35 rounds). It keeps the one-1 uniqueness story (r2c2) and has the second-crunchiest solve.

Each line and given removed in turn (CP-SAT, limit 2; my logical solver up to tier 2):

| removed | solutions | logical solve |
|---|---|---|
| row 1 (= +) | 1 | solved (27 rounds) |
| row 3 (+ =) | 1 | stuck |
| row 5 (+ =) | 2+ | stuck |
| row 7 (+ =) | 2+ | stuck |
| row 9 (+ =) | 2+ | stuck |
| column 1 (= +) | 1 | stuck |
| column 5 (= +) | 2+ | stuck |
| column 9 (+ =) | 2+ | stuck |
| given 1 at r2c2 | 2+ | stuck |
| given 1 at r3c9 | 1 | stuck |
| given 1 at r7c8 | 1 | stuck |

The row-1 sum is the one redundant clue: the puzzle stays unique and logically solvable without it. I kept it because it completes the
odd-rows pattern. For every one of the eight solvable triples of 1s, some line was redundant. The triple where row 1 matters (r2c2, r3c9, r6c5)
makes rows 9 and column 1 redundant instead, and is much easier (18 rounds).

How the logic opens (my solver's first steps, using only the facts above): the 1 at r3c9 is the units digit of row 3's result, so
the units digits of row 3's addends sum to 11. That is the carry, so the tens column has none. The same 1 is in the top addend of column 9. Each step after that is one
sum checked against the candidates; at most 32 sums survive at any step.

## Solution

```
954281673
718963254
236745981
673824195
142596738
895317426
367452819
581679342
429138567
```
