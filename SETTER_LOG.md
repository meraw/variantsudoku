# Setter's log

A running record of every attempt, kept honest: finished puzzles, failed drafts and abandoned ideas.
Newest run at the top.

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
