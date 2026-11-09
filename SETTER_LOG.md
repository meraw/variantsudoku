# Setter's log

A running record of every attempt, kept honest: finished puzzles, failed drafts and abandoned ideas.
Newest run at the top.

---

## Run 6 — 2026-11-09

FEEDBACK.md is unchanged since run 2. It still holds one note: Pinwheel Whispers was "7+", solvable with a few forcing chains,
and enjoyable. Nothing on 003–010 yet. What I took from it this run:
1. Keep fair, crunchy solves. Both puzzles are 4s, and neither needs contradiction tests in my solver.
2. Keep varying rules. This run adds two clue types new to the gallery (X-sums, skyscrapers) and one new invented line (odometers).
   No cages, no givens.
3. Strengthen verification of invented rules. Until now they only had my own solver.

Toolkit changes:
- The environment was fresh: I reinstalled OR-Tools and lz-string, and rebuilt Rangsk's SudokuSolver from source (.NET 10).
- `vs.py`: new types `xsum`, `skyscraper` (outside clues read from their side; f-puzzles `xsum` / `skyscraper`, same
  shape as `sandwichsum`, field names from Rangsk's `FPuzzlesBoard.cs`) and the invented `odometer`. Each has a CP-SAT model,
  checker, logic step, SVG and export.
  - X-sum/skyscraper logic is an exact forward/backward walk over the whole row/column (state = digits used + X or the visible count).
  - Odometer logic enumerates fills with the remaining distance as a budget.
  - Soundness: 25 random grids with 14 random outside clues and random satisfied odometers, plus 30 grids with only odometers.
    The true digit was never removed.
  - Model vs checker: agreement on 300 random (clue, grid) pairs.
  - Arrows now render with arrowheads (no earlier puzzle used arrows).
- **NFA lines for Rangsk** (`nfa.py`). Rangsk's solver has a generic `nfaConstraints` entry (serialized automata in the
  format of sigh's Interactive Sudoku Solver). I wrote a serializer from its deserializer (`NFAConstraint.cs`) and encoded
  odometers and bridges as automata.
  - Invented rules now get a second, independent uniqueness check.
  - It worked first time on 010 Product Placement: 1 solution, solved to the same grid. I added this to 010's verification report.
  - The NFA filter ignores that cells of a line sharing a house differ, so Rangsk's *path* on these puzzles leans on
    contradiction tests. I don't use it for ratings; the reports say why.
- `open_outside.py`: open-solution setting for X-sums/skyscrapers/sandwiches on all 36 outside positions, with 180° pairs of
  possibly different types (`--mixpairs`) and a per-type score bonus. Givens in disguise (skyscraper 1/9, X-sum 1/45) are never offered.
- `open_lines.py`: odometers and arrows, plus `--cap N` (`Logic.CASE_CAP`), which skips odometer steps with more than N fills.
- `package.py`: lists the new techniques, groups Rangsk's NFA/contradiction steps sensibly, and adds a note when the second
  solver saw invented lines as NFAs. The calibration table for 001–010 is unchanged.

### ✅ 011 Skyline Sums — X-sums + skyscrapers, 12 outside clues, no givens
- **Idea:** two clue types about the first digit seen from the edge, how far to count from it and how often the view
  climbs. Both are new to the gallery, and the puzzle has no marks inside the grid.
- **Drafts** (all with `open_outside.py`, no target grid):
  - Unbiased runs: every finished run was X-sum-only or nearly so.
    - free, seed 2: 10 X-sums.
    - free, seed 3: 10 X-sums + 1 skyscraper. My solver needs 25 rounds, but Rangsk needs **35 contradiction tests**:
      my exact whole-row walk is much stronger than its X-sum step. Rejected.
    - symmetric, seed 1: 14 X-sums, Rangsk clean.
    - symmetric, seed 3: 14 X-sums, 3 contradictions.
    - Two more seeds stopped early to free CPUs.
  - Mixed pairs with a skyscraper bonus:
    - The first try picked skyscraper-1 clues (a 9 in disguise), so I added the "givens in disguise" filter.
    - Bonus 1.7: 8+8 clues and 10+4 clues (the second has 2 Rangsk contradictions).
    - Bonus 2.2: seed 6 gave 7+7 with 0 Rangsk contradictions. Seed 7 gave 18 clues + 1 given.
  - Kept seed 6 and pruned by hand:
    - Row 5's left X-sum 45 is a given in disguise (r5c1 = 9) and wasn't needed. Pair pruning had kept it, because its
      partner was needed. Nothing non-trivial can stand there, so the position stays empty.
    - The skyscraper 3 above column 2 was redundant on its own.
- **Verification:** CP-SAT finds 1 solution (OPTIMAL), the forbidden re-solve is INFEASIBLE, and the checker reports no
  violations. Rangsk finds 1 solution and solves it logically to the same grid, using only clue re-evaluations, 4 tuples
  and 3 pointing steps. My solver: tiers 1–2, 35 rounds, no contradiction tests. Eleven clues are needed for uniqueness.
  The twelfth (32 below column 5) is needed for a solve without contradiction tests.
- **Difficulty:** 4/5 (method). Break-in: column 5 has X-sums at both ends (37 + 32 = 69 > 45, so the stretches overlap).
- **Caveat:** whether SudokuPad draws `xsum` and `skyscraper` differently is unchecked, so the rules text lists the skyscraper clues.

### ✅ 012 Are We There Yet? — odometers (invented), 9 lines, no givens
- **Rule:** the circled first cell of a line equals the total distance travelled along it, i.e. the sum of |differences|
  of consecutive cells, starting with the step out of the circle.
  - I first coded the circle *off* the route, like an arrow. That version is preserved by d → 10 − d, so it has a twin.
  - With the circle on the route, the circle's own value breaks that symmetry. That's why no givens are needed.
- **Facts** (enumerated before setting):
  - Every tip is even (parity).
  - 2-cell lines are c–2c.
  - 3-cell lines c–x–e have e = 2x (x < c) or e ∈ {2c, 2(x − c)} (x > c).
  - Nine mutually-seeing cells allow only 9-8-7-6-5-4-3-1-2. Eight allow 15 sequences.
  - A random fixed path is satisfied with probability 5.4% (2 cells), 7.9% (3), 5.4% (4), 2.3% (5), 0.66% (6), 0.12% (7) and 0.02% (8),
    so long lines carry 5–13 bits each.
- **Drafts** (`open_lines.py`, no target grid, givens only as a fallback):
  - Free placement, lengths 5–8 or 4–8: six seeds. Five finished with 0 givens (9–10 lines; 35–44 tier-2 rounds), and seed 8 needed 1 given.
  - With case lists capped at 80 fills during setting (to force "human-sized" steps), three seeds each needed 1 given,
    because the long lines can't start at all under that cap. Not kept.
  - 180° pairs, lengths 4–7: after 10 lines still 607 candidates. Stopped.
  - Choice: re-solving all five no-given layouts with steps capped at 300 fills, only seed 4 and seed 1 still finish.
    Seed 4 has fewer lines (9) and a cleaner picture, with two mirrored 7-cell hooks in boxes 3 and 9. Kept seed 4.
- **Verification:** CP-SAT finds 1 solution (OPTIMAL), the forbidden re-solve is INFEASIBLE, and the checker passes.
  **Rangsk (via NFA) finds 1 solution**, the first independent check of an invented rule in this gallery. Its logical path
  reaches the same grid, but uses 105 contradiction tests, because the NFA filter doesn't know about repeats.
  My solver: tiers 1–2, 35 rounds, no contradiction tests. One step lists 706 fills, but the solve also finishes with a
  300-fill cap. Every line is needed for uniqueness.
- **Difficulty:** 4/5 (method).

### ❌ Abandoned — a third puzzle: arrows + anti-king
- Arrows had never appeared in the gallery. `open_lines.py arrow`, 180° pairs, 3–5 cells, givens as a fallback: 10 arrows +
  3 givens (38 rounds), 12 + 4 (40) and 12 + 4 (56).
- Rangsk solves the first two cleanly, but the pictures were random-looking, with a given sitting on an arrow shaft, and
  nothing in the design was an idea. Not saved. Arrows deserve a hand-designed break-in.

### Ideas for next runs
- An odometer puzzle with a **hand-built opening** (e.g. an 8-cell line in one box, whose circle must be 8 or 9 and tip 2
  or 4) and fewer lines. Or odometers mixed with a value rule like killer cages.
- Use NFAs to give Rangsk other invented rules from the back catalogue (keypad, knight, seesaw and Fibonacci lines are
  all small automata) and add addenda to 001/003/005/007.
- Teach the NFA encoding about repeats where a line stays inside one house (track used digits for those segments) so
  Rangsk's path becomes a fairer second opinion.
- Arrows with a designed idea (pill arrows? arrows whose circles are on other arrows?).
- Feedback wanted: are X-sums + skyscrapers fun at this density? Is the odometer rule clear from the rules text?

---

## Run 5 — 2026-11-08

FEEDBACK.md is unchanged since run 2. It still holds one note: Pinwheel Whispers was "7+", solvable with a few forcing chains,
and enjoyable. There are still no comments on 003–008. What I took from it this run:
1. Keep the solves crunchy but fair. Both puzzles this run are 4s by my method, with no contradiction tests.
2. Act on the run-4 caveat: **find a design recipe that isn't "symmetric marks + symmetry-breaking givens"** (006, 008) or
   "target grid + grown clues" (002–004). New this run: **open-solution setting**. There is no target grid. Each clue is chosen
   from the values still possible, by how much logic it unlocks, and the grid only exists once the clues force it.
3. Add a second, independent solver, so that "logically solvable" doesn't rest on my own code alone.

Toolkit changes:
- **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver) is now part of the workflow. I built it from source with the .NET 10 SDK.
  `tools/rangsk.py` feeds it our own f-puzzles export (without the solution) and reads back the solution count and the logical
  path. `package.py` runs it automatically when every constraint is native to f-puzzles. As a sanity check, it reports 006 unique,
  and 003 (invented lines, exported as cosmetic lines) as multiple, as expected.
- Its f-puzzles parser (`FPuzzlesBoard.cs`, `SolverFactory.cs`) was also my source for the JSON fields `sandwichsum`
  (`{"cell": "R0C3", "value": "10"}`; row/column 0 lie outside the grid), `betweenline` and `slowthermometer`. This settles the outside-clue
  format question left open in runs 3–4. The parser also uses the `littlekillersum` shape from run 4.
- New constraint types in `vs.py`: sandwich sums, between lines, slow thermometers (which may share cells), and the invented
  **bridge line**. Each has a CP-SAT model, checker, logic step, SVG and export.
  - The sandwich logic step tries every 1/9 placement with every set of sandwiched digits, with inner and outer cells checked
    as perfect matchings.
  - Long bridges split their inner cells by box and use the 45 rule for segments covering 6+ cells of a box.
  - All new logic steps passed a soundness test: clues derived from random grids never lose the true digit (12 + 60 grids).
- A speed-only memo in the logical solver skips constraints whose cells haven't changed since they last made no progress. The calibration
  counts for 001–008 are identical before and after.
- New scripts `open_clues.py` (sandwich totals / killer sums, with givens only when stuck) and `open_lines.py` (bridge
  placement, 180° pairs, box-covering "snakes", a fixed hand-placed core). See tools/README.

### ✅ 009 Betwixt — sandwich sums + between lines, 10 clues + 4 lines, no givens
- **Idea:** two kinds of "between": by position (sandwich) and by value (between lines). Both are new to the gallery.
- **Drafts** (each: hand-drawn lines, then `open_clues.py`):
  - First runs added all 18 clues and still didn't finish. I checked one state with Rangsk: it had **multiple
    solutions**, a 5/6 deadly rectangle that no sandwich can see. If two digits from 2–8 swap places and both cells sit
    on the same side of the crusts in each line, no sandwich total changes. Fix: a given is allowed as a move only when
    no clue removes ≥15 candidates.
  - Sampling was slow at first: each sample minimised a random objective until it timed out. I capped each sample at 0.4 s.
  - Layout "bars" (a long row-5 line plus short bars): 10 clues, 56 rounds, unique per Rangsk, but the logic was mostly singles.
    Layout "chevrons": 10 clues + 1 given. Layout "diagonals" (4 corner spurs into the centre + a centre cross-stroke), three seeds:
    10 / 10 / 8+1 given. I kept seed 3, whose Rangsk path is the richest: 17 tuple/pointing steps plus many between-line and
    sandwich steps, and no fish, wings or chains.
  - Line pruning, which `open_clues.py` doesn't do: the bottom-left spur was **redundant**. Without it the puzzle is still unique,
    and both solvers still finish with no contradictions, so I removed it. The picture is no longer symmetric.
  - A 9-clue version (without column 1's 32) is still unique. Rangsk then needs 27–29 contradiction steps plus AIC
    chains, and my solver needs tier 3. Rejected as bifurcation.
- **Verification:** CP-SAT finds 1 solution (OPTIMAL), the forbidden re-solve is INFEASIBLE, and the solution passes the checker. **Rangsk: 1 solution, solved
  logically, same grid**, fed only our export. My solver: tiers 1–2, 39 tier-2 rounds, no contradiction tests. Removing any line
  or any clue except column 1's 32 gives 2+ solutions.
- **Difficulty:** 4/5 (method). Rangsk needs only basic techniques, but sandwich case work is real work for a human.

### ✅ 010 Product Placement — bridge lines (invented), 12 bridges + 2 givens
- **Rule:** the product of the two circled ends equals the sum of the inner digits. Facts found before setting:
  - A three-cell bridge inside one house is 2–6–3 or 2–8–4.
  - The pattern 1–x–x needs the middle and the far end not to see each other.
  - A bridge whose inner cells fill a box has ends {5,9}.
  - A full-row bridge is impossible: (a+1)(b+1) = 46.
  - A bridge carries only about 5–7 bits (a random grid satisfies a fixed bridge 0.8–3.3% of the time; 3,000 grids).
- **Drafts:**
  - *Seven Bridges* (Königsberg), four killer cages as land masses plus Euler's seven bridges: cage sums chosen by
    `open_clues.py`, which still needed **8 givens**. Abandoned (see below).
  - Pure bridges, placed in 180° pairs by logic gain: stalled at ~617 candidates with 14 lines. CP-SAT showed only
    **2 solutions** left, but they differed in 68 of 81 cells. The information was global, with no logical way in.
  - Lengths up to 12: too slow to evaluate, stopped.
  - Cores of one 3-cell bridge per box: nine boxes never feasible (0/40 random, 0/300 symmetric), five boxes about 60%.
    No 4–5 line core let my solver place any digit. Abandoned.
  - The keeper: a hand-placed 45-rule core, the serpentine through all of box 5 (r5c3→r5c7, its own 180° image). Then
    `open_lines.py` with pairs and a given fallback. Four seeds: 4, 2, 4 and 3 givens. I kept the 2-given one, then found
    one bridge individually redundant (its symmetric partner isn't) and removed it.
- **Verification:** CP-SAT finds 1 solution (OPTIMAL), the forbidden re-solve is INFEASIBLE, and the solution passes the checker. My solver: tiers 1–2, 44 tier-2 rounds,
  no contradiction tests, largest case lists 106 and 54 fills. Without the givens: 50+ solutions. Every bridge and given is
  needed for uniqueness except r9c8–r7c9, which is needed for the logical path. Rangsk can't model the rule, so there's
  only one logical solver for this one.
- **Difficulty:** 4/5 (method: 44 rounds).
- **Caveat:** a busy picture (ten small three-cell bridges). The serpentine is the designed idea. The rest was placed by
  script and then curated.

### ❌ Abandoned — Seven Bridges of Königsberg (bridges + land-mass cages)
- Geometry A: island cage of 7 cells with 5 bridge ends, banks of 6 cells and the east land of 3, bridges exactly as in Euler's
  graph. With cage sums chosen openly it needed 8 givens. Information estimate: 7 × ~6 bits from bridges + 4 cage sums ≪ 72 bits.
- River variant: the river as slow thermometers (bulb at each mouth, digits never decrease upstream), with zigzag north and south arms
  and a channel between the island and the east land. **Infeasible** (CP-SAT). By hand: rows 7 and 3 force the channel to climb strictly,
  r3c5 ≥ 7, so the upstream north-east arm would need r3c9 ≥ 10. The all-3-cell version of the bridges is impossible
  for another reason: band 1 would need its three 2s in rows 1 and 3 only.
- Worth another try with a river rule that allows equal neighbours across boxes more often, or with more lines than seven.

### Ideas for next runs
- Bridges with more 45-rule structure: inner cells covering a box minus one cell give {6,7}/{5,8}/{4,9}/{6,6}, telling you
  the missing digit. A puzzle built from those alone might need no givens.
- Use Rangsk for all established-rule puzzles from now on. Consider re-checking older established ones (006 passes).
- Sandwich + something with a visible break-in (X-sums, little killers now that the export format is confirmed).
- Teach my solver fish/XY-wings so its rating is closer to Rangsk's on established rules.
- Feedback wanted: is open-solution setting producing nicer clue sets than grown cages, and do the two 4s feel like 4s?

---

## Run 4 — 2026-11-07

FEEDBACK.md is unchanged since run 2. It still holds one note: Pinwheel Whispers was "7+", solvable with a few forcing chains,
and enjoyable. There is still no comment on 003–006, so the calibration questions from run 3 remain open. What I took from it this run:
1. Keep at least one crunchy puzzle with a clear opening. 007 is a 4.
2. Keep varying the rules. No killer cages, no seesaws, no whispers this time. One invented rule and one classic pairing
   the gallery hasn't used yet (renban, white kropki).
3. Spread the difficulty: one 4 and one 3.

Toolkit changes (`vs.py`):
- New invented constraint **Fibonacci line** (`fibonacci`): read from the dotted end, each digit from the third on is the
  last digit of the sum of the two before it. It has a CP-SAT model (allowed triples), a checker, a seed-pair enumeration
  for the logical solver, an SVG renderer (gold line, gold dot at the start) and f-puzzles export (line + circle).
- New tier-2 technique **Fibonacci parity**: every line of 3+ cells is all even or odd-odd-even repeating. The line patterns
  are combined per house against the count of four evens.
- **Little killers:** clues can now carry an outside position (`from`, `dir`), so the cells are derived. They are drawn outside the grid
  and exported as f-puzzles `littlekillersum`. I took the JSON shape (`cell` "R0C3", `cells`, `direction` "DR", `value`)
  from a test fixture in a third-party SudokuPad importer
  (github.com/StefanLobbenmeier/ninefold, PR #97). That is a reasonable source, but it is not f-puzzles' own documentation,
  and no puzzle uses little killers yet. The logical solver's little-killer step is now an exact per-box-segment sum DP. The old
  version fell back to bounds only for long diagonals.
- `neg_kropki_w` (negative white dots only) now exports as `negative: ["difference"]`.
- `package.py` lists the Fibonacci parity technique. The calibration table is unchanged for 001–006, because none of the changes
  touch their constraint types.
- New scripts: `fib_layouts.py`, `sym_givens.py`, `consec_designs.py` (see tools/README).

### ✅ 007 Liber Abaci — Fibonacci lines (invented), 10 lines + 4 givens
- **Idea:** Fibonacci with last digits only. Facts I found with small scripts before setting:
  - *Parity:* a line is odd-odd-even repeating or all even.
  - *Length:* at most 6 cells of a line fit in one house, and only 8 sequences of six different digits exist.
  - *Long lines:* a line of 15+ cells must follow the Lucas cycle 2-1-3-4-7-1-8-9-7-6-3-9 or the even cycle 2-6-8-4.
  - *Symmetry:* multiplying every digit by 3, 7 or 9 (keeping the last digit) is a symmetry of the rule, so lines alone always
    leave a multiple of 4 solutions, and the 5s are the only cells they can pin.
- **Drafts:**
  - Random 180°-symmetric layouts (5 pairs, mixed lengths) already gave exactly 4 solutions. With no givens, the logical
    solver could place nothing: the lines are relational. Before I added the parity technique, it was stuck at 685+ of 729 candidates.
  - "Golden spiral": a square spiral from the centre cut into lines of 3, 5, 8 and 13 cells. CP-SAT proved **infeasible**
    in all four variants. The 13-cell piece alone is impossible, because it runs 6 cells along a row and then 6 down a column. Abandoned.
  - **One given:** I annealed layouts with the best single-given logic result as the objective (4 runs, 6–7 pairs, 400 iterations).
    The best single given still left about 634 candidates. Abandoned. Lines on their own don't give a human enough to start from one digit.
  - The keeper: I annealed layouts with lengths restricted to 3/5/8 and orthogonal steps on CP-SAT count (4 seeds). Every seed reached
    the minimum of 4. Then I added greedy logic-guided givens: 3–5 free givens, or 4–6 as symmetric pairs. I chose seed 13 (two
    staircase 8-lines) with the pair version that needed most logic: 34 tier-2 rounds. Its givens 9/1 and 7/3 sit in opposite cells.
    The unique solution turned out to be complement-symmetric (opposite cells sum to 10), as expected: it is the solution
    that the 180° turn combined with ×9 maps to itself.
- **Verification:** CP-SAT finds 1 solution (OPTIMAL), the forbidden-solution re-solve is INFEASIBLE, and the solution passes the checker. Without givens
  there are exactly 4 solutions: the ×3/×7/×9 relabellings, where ×9 equals the 180° rotation. Each line pair is needed: without
  it the puzzle has 2+ solutions, or (for one pair) it stays unique but needs contradiction tests. Each given is needed for the logical path only.
  Logic: tiers 1–2 (34 tier-2 rounds, largest step 25 seed pairs).
- **Difficulty:** 4/5.

### ✅ 008 Good Fences — renban + negative white kropki, 3 renbans + 12 dots + 4 givens
- **Idea:** a classic counterweight, with two rules that pull against each other. Three renban cells in a straight orthogonal row can't all be
  fenced. The two dotless L renbans must snake five consecutive digits with no two neighbours consecutive.
- **Drafts:**
  - Layout A (four L-shaped 4-cell renbans, a vertical 3 through the centre and two 2-cell renbans), with CP-SAT sampling grids that have at most 16 consecutive
    neighbour pairs: usually exactly 2 solutions (the d → 10−d twin, which always exists for these rules). No single given
    was logic-solvable. Greedy givens gave 2–4 givens, but the dot patterns were asymmetric and looked random.
  - With the dot pattern forced 180°-symmetric (at most 12 dots), the twins remain. Across layouts A and B, symmetric given pairs gave
    4–6 givens and 3–16 tier-2 rounds.
  - Layout B (two 5-cell Ls, two vertical 3s, a diagonal 3 through the centre) gave the keeper: 12 symmetric dots, 4 givens, 16 rounds.
    The two vertical 3-cell renbans turned out to be fully dotted, which already forces three consecutive digits, so I removed them.
    Result: 14 rounds, and every remaining renban and given is needed for the logical path.
- **Verification:** CP-SAT finds 1 solution (OPTIMAL), the forbidden re-solve is INFEASIBLE, and the solution passes the checker. Without givens there are exactly 2 solutions
  (d → 10−d, which equals the 180° rotation). Logic: tiers 1–2 (14 tier-2 rounds). Two renban steps are flagged as >500 raw
  combinations (2,700 and 1,920), but only 3 fills survive each once the line's own rules apply. I explain this in the report.
- **Difficulty:** 3/5.
- **Honest caveat:** the method repeats 006: a symmetric negative-constraint pattern from CP-SAT, then givens to break the twin.
  The rules and logic differ, but the recipe doesn't. Next run should use something else.

### ❌ Abandoned — little killers + renban (the run's original "established" plan)
- Skeleton: four diagonal 4-cell renbans swirling into the corners of box 5. Little-killer clues grown solution-first in
  180° pairs, guided by the logical solver.
- The solver could not use little killers at all. **With every diagonal clue of length ≥2 added**, it was still stuck at 710 of
  729 candidates. I replaced the bounds-only little-killer step with an exact segment DP, and nothing changed. Real little-killer
  solving relies on combining diagonals with house totals (set equivalence / 45-rule reasoning), and my solver doesn't do that.
  Without it I can't verify logical solvability, so I didn't publish.
- The rendering and export code is kept (tested on a dummy grid only).

### Ideas for next runs
- Teach the logical solver set-equivalence (45-rule) reasoning over arbitrary unions of houses and sum clues. That would make little
  killers, region sums and killer innies/outies checkable, and reopen the little-killer plan.
- More Fibonacci: lines with diagonal steps, a closed 12- or 24-cell loop (it must follow the Lucas cycle or be all even), or
  Fibonacci lines plus a value-giving rule that breaks the ×3/×7/×9 symmetry instead of givens (e.g. thermos or a few killer sums).
- Find a new design recipe that isn't "symmetric marks + symmetry-breaking givens" (006, 008).
- Feedback wanted: does the Fibonacci rule feel natural to solve with, and are four givens acceptable?

---

## Run 3 — 2026-11-06

FEEDBACK.md is unchanged since run 2. It holds one note: Pinwheel Whispers was "7+", solvable with a few forcing chains
and enjoyable, even though sudokucoach's solver thought it impossible. What I took from it this run:
1. Keep a crunchy, fair solve with a clear opening. Elena is happy to work for it.
2. Get away from the "line skeleton + grown killer cages" recipe, which 002–004 all used. Neither puzzle this run has cages,
   and neither was grown clue by clue. In both, I chose the whole shape first and then searched over it with the solver.
3. Give the gallery a spread of difficulties: one 4 and one 2 this run.

Toolkit changes:
- New invented constraint **seesaw** (`vs.py`): digit × distance from the pivot, counted along the line, balances on both sides.
  It has a CP-SAT model, a checker, SVG rendering (brown line, white fulcrum circle), and f-puzzles export as a line plus a circle.
- New tier-2 technique **seesaw bounds**: human-style min/max reasoning. For cells that see each other, the minimum puts the
  smallest digits on the largest weights.
- **Changed how the logical solver counts work.** Whole-constraint enumeration now runs on one group per round,
  smallest candidate space first, and stops at the first one that makes progress. This is closer to how a human picks the easiest
  cage or line, but round counts are not comparable with runs 1–2. So `package.py` now re-solves every earlier puzzle and prints a
  calibration table in each new verification report. Re-solved: 001 = 14, 002 = 51, 003 = 15, 004 = 23 tier-2 rounds. New
  thresholds: 2 = ≤8, 3 = 9–30, 4 = 31–60 rounds. These keep all four earlier ratings.
- For seesaws, the "enumeration size" in reports is now the number of balancing fills that survive the candidates. The raw
  candidate product (millions) said nothing about the work a solver actually does.
- New scripts `seesaw_rows.py` and `one_given.py` (see tools/README). XV letters are drawn larger.

### ✅ 005 Centre of Gravity — seesaws (invented), 9 lines + 4 givens
- **Idea:** a seesaw line: each digit × its distance from the fulcrum, summed on each side, must balance. Straight lines in a row are
  all-different, which makes them very tight. Some shapes are impossible: 3 cells with a centre pivot, or a 5-cell line pivoting
  on its 2nd cell. A 7-cell line pivoting on its 3rd cell forces candidates 6789 / 456789 / … / 1234 before any other logic.
- **Drafts:**
  - Solution-first growth (as with cages): a random grid has only 10–19 straight balancing lines of length ≥4, and a 180° pair
    practically never balances on both sides. The growth was stuck at the first step. Abandoned.
  - Random symmetric layouts of tight line types: about half infeasible. The best had 1–4 solutions, but my logical solver could not place a
    single digit (600+ candidates left). Annealing on logic progress alone wandered into an **infeasible** layout, because the logical solver
    can't see global infeasibility. With a CP-SAT feasibility check added, it made no progress (about 550 candidates left).
  - "Playground" drafts, with seesaws scattered over rows or columns: logic-guided givens finished them with 5–6 givens, but they looked random.
  - The keeper: I noticed that a good random layout had 8 of 9 fulcrums in column 5. So I fixed **one seesaw per row, every pivot in
    column 5, 180° symmetric** and annealed the arm lengths on CP-SAT solution count (11 arm options per row). The best layout has
    **2 solutions with no givens**. Another layout showed a single solution within a 20 s limit but had ≥5 on a longer run, so short
    time-limited counts mislead.
  - Givens: greedy logic-guided picks, plus about ten randomised greedy trials. 4 givens is the minimum I found. I took the set with
    the smallest hardest step (the largest seesaw case list is 56 fills).
- **Verification:** CP-SAT finds 1 solution (OPTIMAL), and the forbidden-solution re-solve is INFEASIBLE. I also checked each seesaw's torque by hand
  from the solution grid. Logic: tiers 1–2 only (38 tier-2 rounds), no contradiction tests. One given would already make the
  solution unique, but all four are needed for the logical path.
- **Difficulty:** 4/5. The round count sits between 004 (23) and 002 (51).

### ✅ 006 Which Way Up — thermometers + XV with negative constraint, 1 given
- **Idea:** I wanted a gentle, classic puzzle with no cages. The run-1 lesson was that dots/XV need a negative constraint to stay sparse.
- **Drafts:**
  - Four diagonal thermos (the centre box out to the corners). CP-SAT showed a grid exists with **zero** X/V marks, but the thermos then
    leave 38+ solutions.
  - I asked CP-SAT for grids whose X/V pattern is 180°-symmetric (like the thermos) with 8–16 marks. Many were near-unique without givens, and
    then I saw why they always had exactly 2 solutions: the whole clue set is symmetric, so solutions come in rotated pairs. At least one
    given is required, and one is enough when the twin is the only ambiguity.
  - Greedy logic-guided givens gave 2–4 givens and very easy solves (often singles + pairwise only). Not interesting.
  - Better: for each twin-only design, try **every** single tie-breaking given and keep those the solver finishes (`one_given.py`).
    About 9 of ~75 designs had any. I chose the design that gets furthest on its own: 14 digits are placeable before the given matters.
    Its hardest single given is r6c5 = 7, which sits in the picture's centre.
  - An earlier 1-given design (12 marks) solved with tier 1 only, which was too easy, so I didn't use it.
- **Verification:** CP-SAT finds 1 solution (OPTIMAL), and the forbidden re-solve is INFEASIBLE. Without the given there are exactly 2 solutions, rotations of
  each other. Removing any one thermo forces contradiction tests or leaves the solver stuck, and the r6c4 one is also needed for uniqueness.
  Logic: tiers 1–2 (6 tier-2 rounds).
- **Difficulty:** 2/5.

### ❌ Abandoned / not pursued this run
- Outside-grid clues (sandwich, little killer): I couldn't confirm the f-puzzles JSON format for these from a source, and
  I didn't want to publish a play link I hadn't checked. Postponed.
- No third puzzle. I preferred to spend the time on the solver calibration and on checking the two finished ones.

### Ideas for next runs
- Seesaws with **bends** (distance counted along the line; digits may repeat across boxes), or seesaws in columns too. Seesaws
  plus a value-giving rule could reduce the givens.
- The "one given breaks the symmetry" trick with other symmetric rule sets: negative kropki, whispers, or an anti-knight base.
- Region-sum lines with a designed break-in (still open from run 2).
- Feedback wanted: is 005 really a 4, and is 006's single given satisfying or too gentle?

---

## Run 2 — 2026-11-05

FEEDBACK.md: Elena liked **Pinwheel Whispers** ("7+"). She noted that sudokucoach's solver thought it was impossible, but it was
solvable with a few forcing chains and enjoyable. There was no comment on Speed Dial. What I took from this:
1. Whispers + grown symmetric cages worked, so keep a fair, crunchy solve with a clear start.
2. **My difficulty numbers run low.** Pinwheel was rated 3 but needed forcing chains. In the trace, whole-whisper
   enumerations of 1,000–6,000 combinations against partly-filled candidates did the work a human does with chains.
   I revised Pinwheel to 4/5 (noted in its verification report). `package.py` now lists every whole-constraint step over
   500 combinations after the first digit, so heavy steps are visible.

Toolkit changes: `vs.py` gained knight lines (invented), entropic, modular and region-sum lines, little-killer sums
(model only), closed loops (`"loop": true`), a shared `build_model()` (used by the forbidden-solution re-check too),
and cheap propagators for long entropic/region-sum/sum constraints. I removed a `grow_lines.py` I'd written this run,
because it never produced anything usable (see below).

### ✅ 003 Knight Calls — knight lines (invented) + anti-knight + 4 killer cages, no givens
- **Idea:** I followed up the keypad lines from run 1 with a "knight-move on the keypad" relation. Without 5, the keypad's knight graph
  is a single 8-cycle, 1-6-7-2-9-4-3-8. So a knight line is a walk around a ring, 5 can never sit on a line, parity
  alternates, and opposite digits on the ring sum to 10. Theme: the anti-knight rule, plus corner lines drawn in the shape of a knight's move.
- **Drafts:**
  - I tested random 4-fold-symmetric L-line orbits around a closed centre loop (box 5's border has to be the whole ring,
    with 5 in the centre), with and without anti-knight. 8 L-lines + loop: 16 solutions. That's the minimum possible, because the
    ring's 16 symmetries relabel any solution. 4 corner L-lines + loop + anti-knight: 32 solutions.
  - Two givens on the 32-solution layout: 1,376 pairs give uniqueness, but 0 of 60 sampled pairs were solvable at tier ≤2. The
    givens can't make the ring symmetry logical, so I rejected that approach.
  - I grew killer cages in 180° pairs instead (7 seeds × 2 layouts). Most seeds ended with 4 cages. I picked seed 4 for its
    clean look (cages only in rows 4–6) and the designed-feeling opening: opposite loop cells sum to 10, so the 20 and
    10 cages force r4c3 + r6c7 = 10, and then row 5 and one anti-knight check fix the loop.
  - Any 3 of the 4 cages are already unique, but the logical solver gets stuck with only three. I kept all four and say so in the note.
- **Verification:** CP-SAT finds 1 solution (OPTIMAL), and the forbidden-solution re-solve is INFEASIBLE. Logic: tiers 1–2 only (8 tier-2 rounds).
- **Difficulty:** 3/5.

### ✅ 004 Picture Frame — entropic lines (24-cell closed loop + centre cross) + 8 killer cages, no givens
- **Idea:** a closed entropic loop must have length divisible by 3, and the 7×7 frame (rows/cols 2 and 8) is exactly 24 cells.
  Every third frame cell is in the same class, including all four corners, and the two cells outside the frame in each frame
  row/column are classified by counting.
- **Drafts:** frame + both long diagonals as entropic lines is **infeasible** (solver-proven). Frame + a 3-cell cross in box 5
  is fine. Cage growth (6 seeds) gave 8–14 cages, and I took the 8-cage one. Every cage, and the cross, is necessary for uniqueness.
  The opening: the 24 cage puts a frame cell in high, and the 4 cage puts another in low, which sets the rhythm of the whole frame.
- **Verification:** CP-SAT 1 solution (OPTIMAL), forbidden re-solve INFEASIBLE, and logic tiers 1–2 only (11 tier-2 rounds).
- **Difficulty:** 3/5.
- **Honest caveat:** this uses the same recipe as Pinwheel (line skeleton + grown 180° cages). It's a different line type and look,
  but the method repeats. Next run should use something else.

### ❌ Abandoned — region-sum + entropic lines, no cages (the run's original "established" plan)
- Skeleton "X": region-sum lines from each corner box diagonal into a box-5 corner (segments 1|3). The box-5 corners must
  then be {6,7,8,9}. I liked this, but it left a huge solution space.
- Growth attempts, all failed:
  - Greedy on logical-solver progress stalls at the very start. Entropic and equal-segment region-sum lines remove no
    candidates on their own, so the greedy step just adds the shortest lines.
  - Greedy on "cells forced" (CP-SAT backbone) shows 81 free cells until the very end.
  - Pool of random solutions: any one line kills the whole pool.
  - Counting completions under random partial masks did progress (14 lines). But at that point CP-SAT enumerated only 444
    solutions per minute, and the logical solver could **not place a single digit**. Every candidate was still possible
    (exact CP-SAT check: 729/729). Unfair as a puzzle, so I stopped.
- I also tried replacing region sums with arrows, thermos or little killers on entropic/region-sum skeletons. Each added pair
  improved logic by only ~8–12 candidates, and the clue count was heading for 20–40, so I stopped.
- Lesson: entropic + region-sum is almost entirely *relational*. It needs a hand-designed break-in that forces actual
  digits (e.g. 1|3 segment pairs that pin {1,2,3}), and I didn't find one this run. Value-giving clues (cages) are what make
  solution-first growth work.

### Ideas for next runs
- Region-sum work with a real designed break-in (several 1|3 and 1|2 segment lines that pin specific digits), finished
  with few givens if needed. Don't rely on greedy growth here.
- A puzzle **without** killer cages, since 3 of the last 4 use them: e.g. thermos/arrows with a hand-built logic path, or a
  negative-constraint XV/kropki puzzle with a few givens.
- The knight ring (1-6-7-2-9-4-3-8) could carry a whole puzzle with ring-position colouring, maybe with entropic/modular lines.
- Get human feedback on the new difficulty calibration (003 and 004 are both rated 3).

---

## Run 1 — 2026-11-04

FEEDBACK.md: "No feedback available yet." Nothing to act on.

The repo was empty apart from README/FEEDBACK, so this run first built the toolkit (`tools/`): a CP-SAT uniqueness
checker, a tiered logical solver, an SVG renderer, f-puzzles/SudokuPad link export and a packager that refuses non-unique puzzles.

### ✅ 001 Speed Dial — keypad lines (invented rule), 3 givens
- **Idea:** "Keypad lines": cells next to each other on a line must hold digits that are orthogonally adjacent on a 1-9 keypad.
  Because the keypad is bipartite (odd vs even), lines force alternating parity. Combined with "4 evens per house",
  this gives strong counting logic.
- **Drafts:**
  - k1/k2: corner snakes + short lines. Far too loose (50+ solutions with no clear structure). Six greedy givens made it
    unique, but even with contradiction tests the logical solver got stuck. Rejected as unfair.
  - Discovered the row 1-2 zigzag: it puts 5 same-parity cells in row 1, so they must be odd. This forces a
    Hamiltonian keypad path. Kept as the centrepiece.
  - A second zigzag at the bottom is **infeasible** in both orientations. For one orientation, parity counting
    gives column 5 six odd digits. Several side-zig combinations were also infeasible (parity counting is brutal).
  - Box-5 snake v1 crossed itself visually, so I switched to a spiral. The outside-in spiral is infeasible; the centre-out spiral works.
  - Final line set (7 lines, left-right symmetric): 240 solutions without givens. I checked all 992 two-given sets that
    give uniqueness, and none were solvable at tiers 1-2. The logic-guided search then found several 3-given sets.
- **Verification:** CP-SAT finds 1 solution (OPTIMAL), and re-solving with that solution forbidden is INFEASIBLE. The logical solver finishes
  with tiers 1-2 only (10 tier-2 rounds, no contradiction tests).
- **Difficulty:** 3/5.

### ✅ 002 Pinwheel Whispers — German whispers + killer cages, no givens
- **Idea:** a familiar ruleset as a counterpoint to the invented one. Four L-shaped whispers turn around the grid like a pinwheel
  (90° symmetric), plus a diamond whisper in box 5.
- **Process:** fixed a target grid, then grew killer cages with the logical solver choosing what to add.
  - Free placement: 8 cages, but the layout looked random (variant w_5 kept in my notes only).
  - Symmetric placement (180° cage-shape pairs, 6 seeds): 12–14 cages. I picked the seed-3 layout because its cages were
    the largest and cleanest-looking. Every pair that wasn't needed was removed.
- **Verification:** CP-SAT finds 1 solution (OPTIMAL), and the forbidden-solution re-solve is INFEASIBLE. The logical solver finishes
  with tiers 1-2 (18 tier-2 rounds, no contradiction tests).
- **Difficulty:** 3/5 (the method says 4, adjusted down because the steps are routine for these rules).

### ❌ Abandoned — thermometers + kropki (and + XV)
- Five thermos in a mirror-symmetric "crown"; kropki dots grown by the solver until the logic finished.
- Unique versions came out with 13–20 dots. The best one (13 dots) was easy (5 tier-2 rounds), but its dots
  bunched on the left side and it looked unplanned. Not saved.
- Symmetric XV growth: sampling seldom produced usable X/V pairs, and all 6 runs timed out. Not saved.
- Lesson: without a negative constraint, dots need too many clues to look good. Next time try negative-constraint
  dots or XV with a hand-picked solution.

### Ideas for next runs
- More keypad-line work: keypad + killer cages, or knight-move keypad lines (5 has no knight moves on a keypad!).
- Try Entropic/modular lines, or region-sum lines, with a hand-designed break-in rather than solver-grown clues.
- Get human test-solves if possible; my difficulty numbers come from a program.
