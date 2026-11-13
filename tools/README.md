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
| `open_lines.py base.json out.json seed [type] [pairs] [minlen] [maxlen] [--snakes] [--givens] [--cap N] [--hang] [--cost t=x]` | Run 5: the same idea for lines (bridges). Random paths (optionally 180° pairs, box-covering "snakes") that some sampled grid satisfies are scored by logical progress. Lines marked `"keep"` in the base spec form a hand-placed core that is never pruned |
| `open_outside.py base.json out.json seed [--types xsum,skyscraper,frog] [--sym] [--mixpairs] [--bonus skyscraper=2.2] [--gthresh N] [--sides TBLR]` | Run 6 (run 10: `frog` type; `--gthresh` = the score below which givens become moves, 1 = only when no clue makes progress; `--sides` restricts the clue positions): open-solution setting for directional outside clues (X-sums, skyscrapers, sandwiches) on all 36 outside positions, optionally in 180° pairs whose two clues may differ in type. `--bonus` multiplies one type's score (raw candidate counts favour X-sums). Clues that are givens in disguise (skyscraper 1 or 9, X-sum 1 or 45) are never offered |
| `nfa.py` | Run 6: encodes invented line rules (odometer, bridge) as NFAs in the serialized format read by Rangsk's `NFAConstraint` (`nfaConstraints` in f-puzzles JSON), so the second solver can check invented rules too |
| `zip_grow.py base.json out.json seed [dutch_bonus] [minlen] [maxlen]` | Run 7: grows zipper/Dutch-whisper lines around a kept hand-drawn core. Lines are clean shapes (straight, or one turn). A new line never touches a line of the same colour, so you can always see where a line ends. A given is allowed as a penalised fallback when no line removes ≥5 candidates. Prunes at the end |
| `line_replace.py spec.json 'cells' seed [maxtests] [--straight]` | Run 7: finds every clean straight/L zipper or Dutch-whisper line that can replace one line and keep both uniqueness and the tier-2 solve (curation by hand) |
| `eq_maxlines.py seed [min] [seconds]` | Run 7: a grid with as many "Carry the One" sum rows/columns as possible |
| `eq_patterns.py feas\|enum <pattern>` | Run 7: feasibility of a pattern of sum lines with free orientations, and solution counts per orientation |
| `ones_givens.py spec.json k part nparts` | Run 7: every k-subset of the solution's 1-cells as the only givens: uniqueness + tier-2 logic |
| `soundness_run7.py` | Run 7: soundness tests for the zipper, Dutch-whisper and equation logic steps, and model/checker agreement |
| `clean_grow.py base.json out.json seed types [minlen] [maxlen] [--bonus t=x] [--nogivens] [--straight]` | Run 8 (run 9: `regionsum` type, jigsaw-aware, and `--straight`): generalises `zip_grow.py` to any mix of whisper / Dutch / zipper / palindrome / renban / thermo lines: clean straight or one-turn shapes around a kept core, a line never touches one of its own type, a given is a penalised fallback; prunes at the end |
| `orbit_grow.py base.json out.json seed [--pairs] [--maxshaft N] [--givens]` | Run 8: straight arrows (no crossings) added in 4-fold rotation orbits (or 180° pairs) around a kept core, scored by logical progress after a CP-SAT feasibility check; prunes whole orbits |
| `pair_givens.py spec.json [max_tests]` | Run 8: every pair of givens that makes the puzzle unique (numpy over all solutions), each tested with the tier-2 logical solver |
| `pend_bars.py seed iterations` | Run 8: the 015 cradle plus random second bars of hanging pendulums; saves the bars with few solutions for `pair_givens.py` |
| `soundness_run8.py` | Run 8: the pendulum NFA accepts exactly the valid sequences (lengths 2–5); pendulum/palindrome logic never removes a true digit; model/checker agreement |
| `open_lk.py base.json out.json seed [--minlen 3] [--sym \| --mirror] [--nogivens]` | Run 9: open-solution setting for little-killer sums around a kept core (no target grid). Every diagonal of `--minlen`+ cells can take one clue, written at a free end of its diagonal; `--sym` / `--mirror` add clues in 180° / left–right mirrored pairs; givens are a fallback; prunes at the end |
| `open_fixed.py base.json out.json seed [--value 13] [--types killer,lk,sandwich,xsum] [--cages 2,3] [--bonus t=x] [--sep] [--maxof t=n]` | Run 10: open-solution setting where **every clue has the same value** and only positions are chosen: killer cages (2–4 cells; `--sep`: cages never touch), little killers on diagonals of 3+ cells, sandwich totals, X-sums. Scored by logical progress, committed after a CP-SAT feasibility check, no givens ever (the run fails if no clue makes progress), pruned at the end |
| `soundness_run10.py` | Run 10: `frog_nfa` accepts exactly the sequences with the right frog sum (totals 9–17); frog logic and cage + little-killer + X-sum logic never remove a true digit; frog model/checker agreement |
| `soundness_run9.py` | Run 9: the factor-line binary-lookup table decodes to the factor relation; `seqs_nfa` accepts exactly its sequences; factor-line + little-killer logic and jigsaw + skyscraper logic (with the law of leftovers) never remove a true digit; factor model/checker agreement |
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

Run 8 added the invented **pendulum** (`{"type": "pendulum", "cells": [circle, ...]}`: read from the circled resting digit c, the other digits
lie alternately above and below c, each strictly closer to c than the one before; at most 5 cells; CP-SAT table constraint over
`PENDULUM_SEQS`, logic step = the valid sequences filtered by the candidates; drawn as a slate line from a white circle with a pivot pin, exported
as a cosmetic line + circle; Rangsk gets `nfa.pendulum_nfa`) and **palindromes** (`{"type": "palindrome", "cells": [...]}`, mirrored cells equal,
a pairwise `eq` relation; grey line; native f-puzzles `palindrome`, so Rangsk reads it too). `open_lines.py` now accepts several line types
at once (comma-separated: bridge, odometer, arrow, pendulum, palindrome, whisper), `--hang` (straight vertical lines, circle on top) and `--cost`.

Run 9 added **factor lines** (`{"type": "factor", "cells": [...]}`, established, from Logic Masters' "Sudoku Variants Series": of two
neighbouring digits one divides the other; a pairwise relation in `ADJ_LINES`, so tier 1 handles neighbours and whole-constraint consistency lists
fills; red line, exported as a cosmetic line) and **jigsaw regions** (`"regions": ["000111222", ...]` in the spec: 9 strings of 9 labels).
`Puzzle` calls `set_regions`, and the module-level `box()` then returns the region of a cell, so houses, techniques, region-sum segments,
little-killer segments and rendering (bold borders between regions) all follow the jigsaw. The f-puzzles export writes `region` (0–8) on every grid cell,
which is the field Rangsk's `FPuzzlesBoard` reads. Region-sum lines are now exported natively (`regionsumline`).
New tier-2 technique **leftovers** (jigsaw only): for k consecutive rows/columns and the k regions with at least 5 cells inside them, the cells of the
band outside those regions and the cells of those regions outside the band hold the same digits, so each side keeps only digits still possible on
the other (sets of up to 4 cells). For Rangsk, `rangsk.py` sends each factor line as one `binaryLookupConstraints` entry per neighbouring pair
(`pair_table`: base64url little-endian uint32 masks, as `BinaryLookupConstraint.DecodeTable` reads them) plus an NFA accepting exactly the line's
valid fills with sudoku repeats ruled out (`line_fills` + `nfa.seqs_nfa`, a trie automaton). Without the NFA, Rangsk only sees pairwise
relations and needs contradiction tests where a human would list the fills of an 8-cell line.

Run 10 added the invented **frog clue** (`{"type": "frog", "from": "r0c3", "sum": 12}`): a frog enters the row/column from the clue, lands
on the first cell and hops forward as many cells as the digit it stands on until it leaves the grid; the clue is the sum of the digits it
lands on, which is the total distance hopped. CP-SAT model with a "lands here" flag per cell; checker `frog_sum`; logic = the exact ray walk of
`gac_ray` with the position of the next landing as its state (the clue is the first landing position outside the grid); drawn as a green
lily pad with the total; exported as a cosmetic green circle with the total at the outside position; Rangsk gets `nfa.frog_nfa(total)`
(state: cells read, next landing position). The f-puzzles export of 019 uses only native entries (`killercage`, `littlekillersum`, `xsum`).
