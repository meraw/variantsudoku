# Setter's log

A running record of every attempt, kept honest: finished puzzles, failed drafts and abandoned ideas.
Newest run at the top.

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
