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
| `clean_grow.py base.json out.json seed types [minlen] [maxlen] [--bonus t=x] [--nogivens] [--straight] [--ortho] [--tips]` | Run 8 (run 9: `regionsum` type, jigsaw-aware, and `--straight`; run 12: `--tips` = every new line ends on a summit cell of the base spec, passes no other summit, and lines may share their summit tip, "trails"): generalises `zip_grow.py` to any mix of whisper / Dutch / zipper / palindrome / renban / thermo lines: clean straight or one-turn shapes around a kept core, a line never touches one of its own type, a given is a penalised fallback; prunes at the end |
| `orbit_grow.py base.json out.json seed [--pairs] [--maxshaft N] [--givens]` | Run 8: straight arrows (no crossings) added in 4-fold rotation orbits (or 180° pairs) around a kept core, scored by logical progress after a CP-SAT feasibility check; prunes whole orbits |
| `pair_givens.py spec.json [max_tests]` | Run 8: every pair of givens that makes the puzzle unique (numpy over all solutions), each tested with the tier-2 logical solver |
| `pend_bars.py seed iterations` | Run 8: the 015 cradle plus random second bars of hanging pendulums; saves the bars with few solutions for `pair_givens.py` |
| `soundness_run8.py` | Run 8: the pendulum NFA accepts exactly the valid sequences (lengths 2–5); pendulum/palindrome logic never removes a true digit; model/checker agreement |
| `open_lk.py base.json out.json seed [--minlen 3] [--sym \| --mirror] [--nogivens]` | Run 9: open-solution setting for little-killer sums around a kept core (no target grid). Every diagonal of `--minlen`+ cells can take one clue, written at a free end of its diagonal; `--sym` / `--mirror` add clues in 180° / left–right mirrored pairs; givens are a fallback; prunes at the end |
| `open_fixed.py base.json out.json seed [--value 13] [--types killer,lk,sandwich,xsum] [--cages 2,3] [--bonus t=x] [--sep] [--maxof t=n]` | Run 10: open-solution setting where **every clue has the same value** and only positions are chosen: killer cages (2–4 cells; `--sep`: cages never touch), little killers on diagonals of 3+ cells, sandwich totals, X-sums. Scored by logical progress, committed after a CP-SAT feasibility check, no givens ever (the run fails if no clue makes progress), pruned at the end |
| `soundness_run10.py` | Run 10: `frog_nfa` accepts exactly the sequences with the right frog sum (totals 9–17); frog logic and cage + little-killer + X-sum logic never remove a true digit; frog model/checker agreement |
| `open_lookout.py base.json out.json seed [--sky] [--skybonus x] [--sym] [--sep] [--gthresh N] [--maxtowers N]` | Run 11: open-solution setting for lookout towers (a move is just a cell, the digit is the clue), optionally with skyscraper clues (`--sky`, totals 2-8 from sampled solutions, score times `--skybonus`); `--sym` adds towers in 180° pairs, `--sep` keeps towers from touching, `--maxtowers` caps the towers (hand-drawn tower cores marked `keep` count too); givens only when the best move removes fewer than `--gthresh` candidates; prunes at the end |
| `soundness_run11.py` | Run 11: `lookout_nfa` accepts exactly the true crosses (6,000 crosses, all 81 ray-length patterns); lookout logic never removes a true digit; lookout model/checker agreement |
| `soundness_run12.py` | Run 12: `notext_nfa` (unmarked cells of a complete summit/valley map) and `lockout_nfa` accept exactly the right sequences; summit/valley logic and lockout logic never remove a true digit; model/checker agreement, and exact solution counting with a full grid as givens |
| `soundness_run13.py` | Run 13: `battlefield_nfa` accepts exactly the rows of nine different digits with the right total; battlefield logic, entropic/modular + skyscraper logic and polydivisible-line logic never remove a true digit; `POLYDIV_SEQS` matches a brute-force filter and the line NFA accepts exactly the valid fills; model/checker agreement for battlefields and polydivisible lines |
| `soundness_run14.py` | Run 14: the median-clue automaton accepts exactly the right ordered triples; median (+ whisper) logic and polydivisible-bracket + killer-cage logic never remove a true digit; median model/checker agreement |
| `snl_grow.py base.json out.json seed [--sym] [--nogivens] [--snakelen 5,8] [--ladlen 2,5]` | Run 14 (abandoned design, kept for the record): open-solution growth of "snakes" (wiggly region-sum lines) and "ladders" (stacked kropki rungs). Random snakes and ladders almost never fit the sampled grids, so it found too few moves |
| `snl_target.py base.json out.json seed [--tries N]` | Run 14 (abandoned design, kept for the record): the same with a fixed target grid. Every element made almost no logical progress on an empty grid, so the growth was random and slow |
| `soundness_run12_decode.py` | Run 13: the NFA decoder of the run-11/12 soundness scripts as an importable module |
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

Run 11 added the invented **lookout tower** (`{"type": "lookout", "cells": ["r5c5"]}`): the circled digit equals the number of cells it
overlooks along its row and column, counting outwards in each of the four directions up to the first larger digit (not counted) or the
edge. `Puzzle` expands `rc` to the tower plus its four rays (`c['rays']` = index lists; `lookout_rays`, checker `lookout_view`). CP-SAT
chains a "still overlooked" flag outwards along each ray. The logic step `gac_lookout` lists every case (tower digit, view length per ray)
the candidates allow and checks the row part and the column part as systems of distinct representatives (overlooked cells below t,
blockers above t, `_matching_support`); cells beyond a blocker are free. Drawn as an amber ring with four sight marks; exported as a
cosmetic circle. Rangsk gets `nfa.lookout_nfa`, which tracks the digits used in the row part and the column part (15,000-17,000 states
per tower), so its filter knows those cells differ. The resulting load strings exceed the 128 kB limit of one command-line argument, so
`rangsk.py` passes long strings as `-f @file`, which needs a one-line local patch to Rangsk's `SudokuSolverConsole/Program.cs`
(see `rangsk.run`). `package.py` strips the "[Name] " prefixes Rangsk writes before a step for silent NFA filters.
Also new: the global **1-5-9 indexing** rule (`"global": ["idx159"]`): in every row the digit in column 1/5/9 is the column of that
row's 1/5/9. It is a set of pairwise relations (`idx_k_j` in `PAIR_REL`: the column-j cell holds k exactly when the column-k cell holds
j), so tier 1 handles it; columns 1, 5 and 9 are shaded in the SVG; exported as f-puzzles `columnindexer` cells (read natively by
Rangsk's `ColIndexerConstraint`). `clean_grow.py` got `--ortho` (orthogonal steps only).

Run 12 added **complete summit/valley maps** (`{"type": "summits", "cells": [...]}`, `{"type": "valleys", "cells": [...]}`): the marked
cells are exactly the cells whose digit is larger (smaller) than every orthogonal neighbour. Marked cells become pairwise `lt` relations
with their neighbours. `Puzzle` adds an auxiliary group `notmax`/`notmin` (`'aux': True`, never drawn or exported) for every unmarked cell:
[cell, orthogonal neighbours], some neighbour larger (smaller). CP-SAT reifies those booleans in both directions. A one-way first version
made solution enumeration count auxiliary assignments as extra solutions, so watch for this in any new rule with helper booleans. Logic step
`gac_notext` (exact per cell, neighbours not required to differ). The checker recomputes the whole map with `local_extrema`. Rendering
shades summits tan with a small brown mountain and valleys pale blue with a blue inverted triangle. Export: f-puzzles `maximum`/`minimum`
cells plus a cell colour (`c`). Rangsk reads `maximum`/`minimum` natively and gets every unmarked cell as `nfa.notext_nfa` (11 states).
Also new: **lockout lines** (`{"type": "lockout", "cells": [diamond, ..., diamond]}`, established: the diamonds differ by at least 4,
and the other digits on the line lie outside their range; repeats allowed where sudoku allows). CP-SAT with min/max and a fully reified
below/above flag per inner cell. Logic step `gac_lockout` (every diamond pair, inner cells restricted, one matching per house). Drawn as a
slate line with white diamonds. Exported as a cosmetic line plus cosmetic `rectangle`s at angle 45. Rangsk gets `nfa.lockout_nfa`, read
as [diamond, diamond, inner...] (`NFA_ORDER`). `package.py` no longer counts Rangsk's "Direct Cell Forcing" as an advanced technique.


Run 13 added **battlefield** clues (`{"type": "battlefield", "from": "r0c3", "sum": 30}`, established): the first digit of the row/column
is the size of an army at that end, the last digit the size of an army at the other end; the clue is the sum of the cells where they
overlap, or of the gap between them (0 if they touch). Counted cells = indices min(a, 9 − b) .. max(a, 9 − b) − 1 (`battlefield_range`).
CP-SAT with fully reified "inside" flags; logic step `gac_battlefield` (every end pair × every digit set of the right size and total from
`REGION_SETS`, range and rest checked as perfect matchings, as for sandwiches); dark red total under small crossed swords; exported as a
cosmetic circle with the total at the outside position. Rangsk gets `nfa.battlefield_nfa(total)`: the far army is guessed at the start
and the state tracks the digits used (a sum-only first version was too weak: Rangsk stalled after contradiction tests). `open_outside.py`
offers `battlefield` (use `--sides TL`; a clue reads the same from both ends).
Entropic and modular lines are now sent to Rangsk natively (`entropicline` / `modularline`). `clean_grow.py` accepts `entropic`,
`modular` and `polydiv`. A spec may set `"weave": true`: crossing straight lines are then drawn over/under alternately (cosmetic).
Also new, invented: **polydivisible lines** (`{"type": "polydiv", "cells": [...]}`): read from the dotted first cell, the number formed by
the first k digits is divisible by k for every k (as in 381654729). CP-SAT table over `POLYDIV_SEQS` (at most 416 strings per length),
logic = the generic fill enumeration with prefix pruning, slate-violet line with a dot, exported as a cosmetic line + circle, Rangsk gets
an NFA of the line's valid fills. `open_lines.py` offers `polydiv`. No puzzle uses it yet (see the run-13 log).


Run 14 added **median clues** (`{"type": "median", "from": "r0c3", "value": 4}`, established: clover's Median Sudoku, GM Puzzles
2026): the clue is the middle value of the first three digits seen from it. CP-SAT table of the ordered triples; checker; the logic
is the generic fill enumeration of the three cells; drawn as a purple number under a small tilde (x-tilde, the statistician's median);
exported as cosmetic f-puzzles `text` at the outside position; Rangsk gets an NFA of the valid triples. `open_outside.py` offers
`median`. Other changes:
- **Bug fix in `rangsk.py`:** a line with `"loop": true` was sent to Rangsk as an open line (the closing pair was missing). Loops now
  repeat their first cell at the end. 004 (an entropic loop) is still unique for Rangsk with the fix.
- **Speed:** a neighbour-relation line (whisper, Dutch, ...) longer than 8 cells whose candidate product is over 5 million is
  checked as overlapping 8-cell windows (a sound relaxation). A 24-cell whisper loop made each logical solve take minutes before.
- `SURVIVOR_TYPES` (default `{'polydiv'}`): types whose whole-constraint steps record the fills that survive the candidates instead
  of the raw candidate product. The verification report printed raw products in the hundreds of thousands for polydivisible
  lines whose steps had 2-47 real fills. Analysis scripts may add other types; the default keeps the calibration of earlier puzzles.
- `kropki_any` relation (a dot of either colour), a design helper for sampling grids before dot colours are chosen.
- `clean_grow.py` accepts specs that contain outside clues (constraints without `cells`).
- `package.py` names polydivisible-line and median steps in its technique list.
