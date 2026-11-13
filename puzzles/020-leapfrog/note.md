# Setter's note — Leapfrog

A new outside clue for the gallery, and as far as I know a new rule. A frog hops along a row, each hop as long as the digit it lands on, and
the clue adds up the digits it touched. There are 14 lily pads and nothing else: no givens, and every pad is needed for a unique solution.

**The one thing to notice.** The digits the frog lands on are its hop lengths, so the clue is simply **how far the frog travels**. It starts on
the first cell and leaves the grid somewhere past the ninth. So:
- a total of 9 means its last hop ends exactly one step past the far edge. 17, the largest possible, means it lands on the far cell and that cell is a 9;
- if the frog's last landing is the c-th cell from its pad and holds d, then **c + d = total + 1**. A 16 ends on an 8 in the far cell
  or on a 9 in the cell before it;
- a 9 next to a pad only fits a total of 9.

**How it was set.** No target grid. A script offered every total still possible at every free pad position and placed the one that taught my
solver the most. I first allowed givens whenever no pad made much progress. Those runs ended with 14–18 pads plus 1–2 givens. With givens
allowed only if *no* pad could make progress at all, two runs finished with 14 pads and no givens. I kept the one with the friendlier
opening and the cleaner second-solver check. Two runs restricted to the bottom and left edges stalled and were abandoned.

**Hint (light spoiler):** row 1 has a frog at each end. The 16 on the right can only finish on an 8 or a 9 near the left end. Then follow the
left-hand frog.

Logical solvability: verified with my candidate-elimination solver (39 rounds of tier-2 logic, no guessing, no contradiction tests). Rangsk's
SudokuSolver, given each pad as an automaton over its row or column, finds the same unique solution and solves it with pointing, a tuple and one
contradiction test. Its automaton view is weaker than reading the clue properly (see the verification report). I rate it **4/5**. It has
**not** been test-solved by a human.
