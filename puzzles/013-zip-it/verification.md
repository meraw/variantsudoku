# Verification report — Zip It

Generated 2026-11-10 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 0.01s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 51, 2: 35, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 28
- whole-constraint consistency: 27
- pair consistency: 14
- hidden single: 9
- locked candidates: 6
- subsets: 2

Whole-constraint steps that made progress: 27. Steps after the first placed digit that enumerated more than 500 combinations: 3 — dutch (7776 combos, 12 cells solved), dutch (1728 combos, 13 cells solved), dutch (700 combos, 15 cells solved).
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 137 steps, of which non-single steps by kind: Zipper Line (constraint step) 35, Pointing 11, Direct Cell Forcing 4, Tuple 4, contradiction test 2, Cell Forcing Chain (r1c5) 1
- note: the Rangsk path uses advanced techniques (listed above).

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** — 35 tier-2 rounds with my solver (method says 4), no contradiction tests. The three Dutch-whisper steps flagged above as >500 combinations are raw candidate products; the fills that actually survive the candidates at those moments are 1 (the column-5 chain: only one order is left by then), 50 and 21 (the L in box 9). Rangsk's solver needs 2 contradiction tests and one cell-forcing chain, about the level of Pinwheel Whispers (002), which Elena found solvable with a few forcing chains. 4.

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
- 014-carry-the-one: rated 4/5, solved, tier rounds {1: 27, 2: 35, 3: 0}

## Extra checks for this puzzle

How it was set (run 7). This is the first puzzle in the gallery to use zipper lines or Dutch whispers. Rangsk's solver knows both natively,
so it checks this puzzle with its own constraint logic, not through an NFA.

1. **Hand-designed core (the "zip fastener").** Column 5 is a single 9-cell Dutch whisper (the chain). Short 3-cell zippers
   cross it on rows 2, 4, 6 and 8 (teeth: left + right = the chain digit). Long 5-cell zippers grow out of the chain
   on rows 1 and 7 (to the left) and rows 3 and 9 (to the right), alternating like interlocking teeth.
   - Facts checked by enumeration: a whole-house Dutch whisper has 72 orders. With the four short teeth (each centre is a sum of two different digits, so ≥ 3),
     only 24 orders of column 5 put 3 or more on every tooth centre, and in all of them r5c5 ∈ {1, 2, 3, 9}.
   - Short teeth on rows 1/3/7/9 instead are **infeasible**, and so is a long tooth on row 5.
   - Any second full-column Dutch whisper (I tried columns 1, 2, 3, 7, 8 and 9) is **infeasible** next to this chain.
   - The core is 180°-symmetric, so on its own its solutions come in rotated pairs (more than 20,000 of them).
2. **Rejected drafts.**
   - *Zip with teeth on both sides of every odd row* (zc0): the core, plus short teeth on row 5 and orange half-rows on rows 3 and 7.
     It is a lovely picture with a **unique** solution, but neither solver can solve it logically. Rangsk stops after 16 contradiction tests.
     With any one of the 81 possible givens, my solver still has 505+ candidates left. Abandoned.
   - Greedy growth from the core (my logical solver scores each proposed line). One run in four finished. That run's 15-line layout
     (Rangsk: 3 contradiction tests) had purple lines touching purple lines, so you couldn't see where a zipper ends. I then forbade any contact
     between same-coloured lines. Under that rule, 11 of 12 further runs (three cores) stalled without givens. The one that finished was on
     a lighter core (chain + short teeth only) and looked random.
   - With a given allowed as a penalised fallback, four runs all finished (0–2 givens). Seed 43 needed no given, but its picture was
     cluttered and Rangsk needed 7 contradiction tests plus an AIC. I kept seed 41 (one given).
3. **Curation by hand (seed 41 → final).** Two lines were bent diagonals. For each one I searched every clean straight or L-shaped replacement that keeps
   uniqueness and the tier-2 solve. The bent whisper became the straight r2c1–r2c3 whisper. No straight zipper could replace the bent zipper, so an
   orange L in box 9 (r7c7–r8c7–r8c8–r8c9) replaced it. Result: every extra Dutch whisper is a short orange "stitch", and no purple line
   touches another purple line.

Each line removed in turn (CP-SAT, limit 2; my logical solver up to tier 2):

| line removed | solutions | logical solve |
|---|---|---|
| chain, column 5 (Dutch) | 2+ | stuck |
| tooth r2c4–r2c6 | 1 | solved (31 rounds) |
| tooth r4c4–r4c6 | 2+ | stuck |
| tooth r6c4–r6c6 | 1 | stuck |
| tooth r8c4–r8c6 | 1 | stuck |
| long tooth r1c5–r1c1 | 2+ | stuck |
| long tooth r3c5–r3c9 | 2+ | stuck |
| long tooth r7c5–r7c1 | 2+ | stuck |
| long tooth r9c5–r9c9 | 2+ | stuck |
| zipper r5c5–r5c3 | 1 | stuck |
| Dutch r2c7–r4c7 | 2+ | stuck |
| Dutch r4c3–r6c3 | 1 | stuck |
| Dutch r3c2–r5c2 | 2+ | stuck |
| Dutch r2c1–r2c3 | 2+ | stuck |
| Dutch r7c7–r8c9 (L) | 2+ | stuck |

The short tooth on row 2 is the one redundant line: the puzzle stays unique and logically solvable without it. I kept it because
it completes the even-row teeth of the zipper picture. It adds no information. The given r4c3 = 4 is not needed for uniqueness (the
lines alone have exactly one solution), but both solvers get stuck without it. Rangsk stops after 9 contradiction tests, and my solver
can't place a digit.

The intended opening (Rangsk's first steps agree): the 4 forces r5c3 onto 8 or 9 (Dutch whisper). r5c4 is the centre of the
row-5 zipper, so r5c4 = r5c3 + r5c5 ≤ 9. That forces r5c3 = 8, r5c5 = 1 and r5c4 = 9.
Soundness of the new logic steps (zipper, Dutch whisper and equation, run 7) is covered in the run-7 log.

## Solution

```
489152637
715396482
326748915
694583271
258917346
173264859
537429168
842671593
961835724
```
