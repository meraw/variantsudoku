# Setter's toolkit

Python 3 + OR-Tools (`pip install ortools`); `cairosvg` is optional and only used for PNG previews.
Link export calls `node` with the `lz-string` package. Install it with `npm install lz-string` in `/tmp/lz`, or change the
path in `vs.links`.

| file | purpose |
|---|---|
| `vs.py` | Puzzle spec (JSON), CP-SAT model and solution counting, a tiered logical solver (`Logic`), an SVG renderer and f-puzzles/SudokuPad export |
| `check.py spec.json [--logic] [--sample N]` | Counts solutions (up to N), shows which cells are fixed, and optionally runs the logical solver |
| `givens.py` | Greedy givens for uniqueness only (ignores logic) |
| `givens_logic.py spec out seed` | Greedy givens chosen for logical progress, then pruned |
| `grow_cages.py base out seed [killer\|kropki\|xv] [--sym]` | Solution-first clue growth guided by the logical solver, with optional 180° symmetric pairs |
| `seesaw_rows.py seed iters [pivot_col] [time_limit]` | Run 3: anneals one-seesaw-per-row layouts with a shared pivot column (180° symmetric) on CP-SAT solution count |
| `one_given.py base.json seed n lo hi` | Run 3: symmetric negative-XV designs over a symmetric base. Finds the designs whose only ambiguity is the 180° twin and lists every single given that the logical solver can finish from |
| `fib_layouts.py seed pairs iters ortho` | Run 4: anneals 180°-symmetric Fibonacci-line layouts (lengths 3/5/8) on CP-SAT solution count. The minimum is 4, because ×3/×7/×9 relabellings preserve the rule |
| `sym_givens.py spec.json [...]` | Run 4: greedy logic-guided givens in 180°-symmetric pairs (digits summing to 10) for designs with a complement-symmetric solution, then prunes pairs |
| `consec_designs.py base.json maxdots from to [--sym]` | Run 4: renban + negative white kropki. Samples grids with at most `maxdots` consecutive neighbours (optionally in a symmetric pattern), derives the dots, counts solutions and tests single givens |
| `open_clues.py base.json out.json seed [samples] [topk] [--no-sandwich]` | Run 5: "open-solution" clue setting with no target grid. Repeatedly samples grids that fit the clues so far, scores every still-possible sandwich total (and the total of every sum-less killer cage) by how much the logical solver then deduces, confirms the pick with CP-SAT and commits it. A given becomes a move only when no clue removes at least 15 candidates. Prunes unneeded clues at the end |
| `open_lines.py base.json out.json seed [type] [pairs] [minlen] [maxlen] [--snakes] [--givens] [--cap N]` | Run 5: the same idea for lines (bridges). Random paths (optionally 180° pairs, box-covering "snakes") that some sampled grid satisfies are scored by logical progress. Lines marked `"keep"` in the base spec form a hand-placed core that is never pruned |
| `open_outside.py base.json out.json seed [--types xsum,skyscraper] [--sym] [--mixpairs] [--bonus skyscraper=2.2]` | Run 6: open-solution setting for directional outside clues (X-sums, skyscrapers, sandwiches) on all 36 outside positions, optionally in 180° pairs whose two clues may differ in type. `--bonus` multiplies one type's score (raw candidate counts favour X-sums). Clues that are givens in disguise (skyscraper 1 or 9, X-sum 1 or 45) are never offered |
| `nfa.py` | Run 6: encodes invented line rules (odometer, bridge) as NFAs in the serialized format read by Rangsk's `NFAConstraint` (`nfaConstraints` in f-puzzles JSON), so the second solver can check invented rules too |
| `zip_grow.py base.json out.json seed [dutch_bonus] [minlen] [maxlen]` | Run 7: grows zipper/Dutch-whisper lines around a kept hand-drawn core. Lines are clean shapes (straight, or one turn). A new line never touches a line of the same colour, so you can always see where a line ends. A given is allowed as a penalised fallback when no line removes ≥5 candidates. Prunes at the end |
| `line_replace.py spec.json 'cells' seed [maxtests] [--straight]` | Run 7: finds every clean straight/L zipper or Dutch-whisper line that can replace one line and keep both uniqueness and the tier-2 solve (curation by hand) |
| `eq_maxlines.py seed [min] [seconds]` | Run 7: a grid with as many "Carry the One" sum rows/columns as possible |
| `eq_patterns.py feas\|enum <pattern>` | Run 7: feasibility of a pattern of sum lines with free orientations, and solution counts per orientation |
| `ones_givens.py spec.json k part nparts` | Run 7: every k-subset of the solution's 1-cells as the only givens: uniqueness + tier-2 logic |
| `soundness_run7.py` | Run 7: soundness tests for the zipper, Dutch-whisper and equation logic steps, and model/checker agreement |
| `rangsk.py spec.json` | Run 5: independent check with Rangsk's SudokuSolver (built from source; see the file for setup) through our own f-puzzles export: solution count and logical path. `package.py` calls it automatically when every constraint is native to f-puzzles |
| `package.py spec puzzles/<slug> <diff> "<why>"` | Refuses to package unless CP-SAT proves a unique solution. Writes puzzle.json, grid.svg, solution.svg and verification.md |

Supported constraints: givens, thermo, German whisper, keypad line (invented), knight line (invented, run 2), seesaw (invented, run 3:
`{"type": "seesaw", "cells": [...], "pivot": "r5c5"}`, digit × distance from the pivot balances on both sides), parity line,
entropic line, modular line, region-sum line, renban, killer cage, arrow, white/black kropki, XV, negative kropki/XV,
anti-knight, anti-king, diagonals, Fibonacci line (invented, run 4: `{"type": "fibonacci", "cells": [...]}`, read from the first cell;
each digit from the third on is the last digit of the sum of the two before it), little killer with an outside position
(`{"type": "littlekiller", "from": "r0c3", "dir": "DR", "sum": 27}`; cells are derived, drawn outside the grid and exported as
f-puzzles `littlekillersum`). Neighbour-relation lines accept `"loop": true` for closed loops.
Run 5 added: sandwich sums (`{"type": "sandwich", "from": "r0c3", "sum": 10}`, outside position r0cK/rKc0, exported as
f-puzzles `sandwichsum`), between lines (`{"type": "between", "cells": [...]}`, exported as `betweenline`), slow thermometers
(`slowthermo`, exported as `slowthermometer`), and the invented **bridge line** (`{"type": "bridge", "cells": [...]}`: the product
of the two end digits equals the sum of the digits between them; drawn as a teal line with pale circles at both ends and
exported as a cosmetic line plus circles). Run 6 added X-sums (`{"type": "xsum", "from": "r0c3", "sum": 20}`), skyscrapers
(`{"type": "skyscraper", "from": "r4c10", "count": 3}`), both read from the clue's side and exported as f-puzzles `xsum` /
`skyscraper`, and the invented **odometer** (`{"type": "odometer", "cells": [circle, ...]}`: the circled first cell equals the
sum of the absolute differences of consecutive cells along the whole line; drawn as a thin blue arrow from a circle and
exported as a cosmetic line plus circle). `open_lines.py` now also places odometers and arrows (circle first), and `--cap N`
sets `Logic.CASE_CAP`: odometer steps with more than N surviving fills are skipped, to test whether a solve needs big case lists.
The f-puzzles field names for the sandwich, between-line and slow-thermo entries were
taken from the f-puzzles JSON parser in Rangsk's SudokuSolver (`SudokuSolver/PuzzleFormats/FPuzzlesBoard.cs`, `SolverFactory.cs`).

Run 5 logic additions (tier 2, whole-constraint consistency): sandwiches try every placement of the 1 and 9 with every
set of sandwiched digits (inner and outer cells checked as perfect matchings); between lines try every pair of end digits
(with a house-count check on the inner cells); bridges enumerate fills exactly up to 6 inner cells, and longer bridges split
the inner cells by box and use the 45 rule for segments of 6+ cells of one box (a sound relaxation). A memo skips a group whose
cells are unchanged since it last made no progress (speed only; the calibration counts of 001-008 are unchanged).

Run 6 logic additions: X-sums and skyscrapers get an exact forward/backward walk along the whole row or column (state =
digits used so far + X or the number of visible digits); odometers enumerate fills with the remaining distance as a budget.
Rangsk's solver now also checks invented lines: `rangsk.py` adds an NFA per odometer/bridge (see `nfa.py`). Its NFA filter does
not know that cells of a line sharing a house differ, so its path for such puzzles leans on contradiction tests; it is used for
uniqueness and as a second opinion, not for the rating.

Logical solver tiers: (1) singles + pairwise constraint consistency; (2) locked candidates, pairs/triples,
generalised pointing, parity counting, seesaw min/max bounds, Fibonacci parity patterns (run 4: each line is all even or
odd-odd-even repeating; patterns are combined per house against the count of four evens), whole-constraint enumeration
(Fibonacci lines enumerate seed pairs; little killers use an exact per-box-segment sum DP since run 4); (3) single-candidate contradiction tests.
Since run 3, whole-constraint enumeration runs on one group per round, the one with the smallest candidate space first.
This is closer to how a human picks the easiest cage or line, but tier-2 round counts are higher than in runs 1-2. `package.py` lists the
re-solved counts of all earlier puzzles in every new verification report as a calibration table.

Run 7 added Dutch whispers (`{"type": "dutch", "cells": [...]}`, neighbours differ by at least 4, a pairwise relation like German
whispers), zipper lines (`{"type": "zipper", "cells": [...]}`: cells equally far from the centre sum to the same total, the centre digit on
odd-length lines; the logic step tries every total and fills the pairs) and the invented **equation** (`{"type": "equation", "line": "r3",
"result": 2}`: the row/column read as three 3-digit numbers is a correct sum; result = index of the answer third, 0 or 2; the logic step filters
the 336 pandigital sums against the candidates; drawn as red + and = circles on the box borders and exported as cosmetic circles with text).
`rangsk.py` now hands German/Dutch whispers (`whispers` with `value` 5/4), zipper lines (`zipperline`) and renban (`renban`) to Rangsk's
solver natively, while the play links keep them as cosmetic lines. Equations reach it as an NFA (`nfa.equation_nfa_distinct`). The NFA reads
the cells in schoolbook order (units, tens, hundreds; `NFA_ORDER`), and its state includes the set of used digits, so the solver knows the
pandigital property. I checked that it accepts exactly the 336 sums.
Export fix (run 7): the negative white-dot rule is f-puzzles' top-level `nonconsecutive: true`. Runs 4–6 wrote `negative: ["difference"]`,
which apps ignore (008's links are regenerated).
