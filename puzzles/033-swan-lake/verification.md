# Verification report — Swan Lake

Generated 2026-11-20 by `tools/package.py`.

## Uniqueness (solver-confirmed)

1. **CP-SAT enumeration** (OR-Tools 9.15.6755): searched for up to 2 solutions; found **1**, search status `OPTIMAL` (search space exhausted) in 1.93s.
2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; status `INFEASIBLE` (0 solutions).
3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): no violations.

## Logical solvability

Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting (lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, the law of leftovers on jigsaw grids (run 9), whole-constraint consistency (enumerate fills of one cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column; entropic/modular lines: every fill of the line, or for long lines the class pattern that repeats every three cells; battlefields (run 13): every pair of end digits with every set of digits for the overlap or gap, the rest of the row/column checked as perfect matchings); polydivisible lines (run 13): every fill of the line, pruned prefix by prefix; median clues (run 14): every ordered triple of the first three cells; counting circles (run 15): every set of digits the circles could use (its digits add up to the number of circles, and each digit d in it has d circles that could hold it with no two in one row, column or box), then a matching of circles to digits with exactly d circles per digit d; fifths lines (run 15, invented): every fill of the line, as for other neighbour-relation lines; double arrows (run 16): every pair of circle digits with every fill of the cells between, as for bridges with a sum in place of the product; innies/outies (run 16, the 45 rule, tried only when every other step is stuck): for a union of whole houses (k consecutive rows or columns, a box, two neighbouring boxes, a 2x2 block of boxes) take the totals of the killer cages inside it off 45 per house, optionally add whole cages that stick out (their outside cells then count negatively), and list the fills of the resulting virtual cage of at most 5 cells; graceful lines (run 17, invented): every fill of the line by a search memoised on the differences used so far (exact when the raw candidate product is at most 1,000,000; above that a relaxed walk that tracks only the last digit and the differences used, so it ignores repeats between non-neighbouring cells); windoku (run 17): the four windows are houses for every technique above; tier 3 = single-candidate contradiction tests propagated with tiers 1-2.

Result: **solved** — tier rounds used: {1: 29, 2: 29, 3: 0}. Logical solve reaches the same grid as CP-SAT.

Technique usage (number of rounds in which each technique made progress):

- naked single: 26
- whole-constraint consistency: 18
- locked candidates: 6
- subsets: 5
- hidden single: 3

Whole-constraint steps that made progress: 18. Steps after the first placed digit that enumerated more than 500 combinations: 0.
(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) (Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)

Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), fed our own f-puzzles export without the solution:

- solution count (`-k`): There are 1 solutions.
- logical solve (`-l`): solved, same grid as CP-SAT; 83 steps, of which non-single steps by kind: Tuple 2

Logical solvability: verified with the solver above (no guessing, no tier-3 contradiction tests).
Note: the solver is a program, not a human test-solve; its techniques are human-style but whole-constraint enumeration can be heavier than a human would like.

## Difficulty estimate

**4 / 5** — My method says 3 (29 tier-2 rounds, in the 9-30 band). I added one step for the new rule and for one big step: to fill the lake you have to find the only graceful order of row 9 that fits its candidates (about 90,000 raw combinations, one survivor). Rangsk's solver logs only singles and two tuples, but its sandwich and line automata filter silently before its logged steps, so its path is no difficulty signal here (as for 029).

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
- 023-trail-map: rated 3/5, solved, tier rounds {1: 73, 2: 37, 3: 0}
- 024-combination-lock: rated 4/5, solved, tier rounds {1: 31, 2: 48, 3: 0}
- 025-tartan: rated 3/5, solved, tier rounds {1: 28, 2: 24, 3: 0}
- 026-crossed-swords: rated 3/5, solved, tier rounds {1: 60, 2: 25, 3: 0}
- 027-long-division: rated 3/5, solved, tier rounds {1: 35, 2: 35, 3: 0}
- 028-happy-medium: rated 3/5, solved, tier rounds {1: 45, 2: 23, 3: 0}
- 029-counting-stars: rated 4/5, solved, tier rounds {1: 40, 2: 53, 3: 0}
- 030-tuning-fork: rated 3/5, solved, tier rounds {1: 53, 2: 31, 3: 0}
- 031-twelve-pieces: rated 4/5, solved, tier rounds {1: 41, 2: 63, 3: 0}
- 032-bowstring: rated 3/5, solved, tier rounds {1: 38, 2: 37, 3: 0}
- 034-room-with-a-view: rated 4/5, solved, tier rounds {1: 43, 2: 49, 3: 0}

## Extra checks for this puzzle

- **Rule facts (graceful lines):**
  - a line of n cells has n - 1 differences, all different. Neighbours on a line that see each other differ by 1 to 8,
    so such a line has at most 9 cells. A line in one row, column or box uses 9 different digits, so its 8 differences
    are exactly 1, 2, ..., 8. The difference 8 only comes from 1 and 9, so **the lake's 1 and 9 are neighbours**, and the
    7 is 1-8 or 2-9 next to them. Only 120 orders of 1-9 are graceful (60 up to reversal);
  - the sum of the differences along a line has the parity of (first digit - last digit). On the lake that sum is
    1 + ... + 8 = 36, so r9c1 and r9c9 have the same parity;
  - replacing every digit d by 10 - d keeps every difference, so graceful lines alone never have a unique solution.
    The sandwich sums break that symmetry (a sandwich of k digits with total S becomes 10k - S).
- **Every element is needed for uniqueness.** Removing any one of the three lines or the seven clues leaves 5+ solutions
  (CP-SAT), and my solver gets stuck.
- **The lines carry real weight:** with the graceful-line step switched off, my solver stalls at 427 candidates.
- **Design (no target grid):**
  - the swan and the lake were drawn first. CP-SAT: feasible, with many solutions;
  - dots as partner (`open_dots.py`, new): white/black kropki needed 18-22 dots, and kropki + XV 16 + 0 or 1 given. The
    dots were scattered over the picture. Not kept;
  - outside clues (`open_outside.py --gthresh 1`, sampled with random hints, `VS_HINT_SAMPLING=1`): X-sums 8,
    mixed X-sum/skyscraper/sandwich 7 and 8. Sandwiches only, 15 seeds: 7 (seed 1, but one clue was the row-9 sandwich
    of 0, which the rules already imply, so row 9 was excluded from then on), 8, 9 + 1 given, 9, 9, 10, 9, 9, 8, 8 + 1
    given, 8, and **7 clues with no givens (seed 15, kept)**.

## Solution

```
839245167
416837529
275961348
947182635
158376492
362594871
594628713
721453986
683719254
```
