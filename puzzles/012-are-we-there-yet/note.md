# Setter's note — Are We There Yet?

A new invented line: the **odometer**. The circle is where the trip starts, and the circle's digit is how far you travel,
step by step, along the line. As far as I know this rule hasn't been used before. Its nearest relatives are arrows (a circle
that totals its line) and whisper-type lines (rules about neighbouring differences).

**Facts worth finding (checked by enumerating every digit sequence):**
- **Every tip is even.** The total distance has the same parity as (circle − tip), and the total *is* the circle, so the
  tip is even. Each arrowhead in the grid is a 2, 4, 6 or 8.
- **Short lines double.** A two-cell odometer reads c – 2c. A three-cell line c – x – e has e = 2x when x < c, and
  e = 2c or 2(x − c) when x > c.
- **Budgets are tight.** A circle holds at most 9, so a long line has to travel gently. If all of a line's cells see each other,
  six of them already need a distance of at least 5. Nine such cells allow exactly one sequence: 9-8-7-6-5-4-3-1-2.
- **No twin.** Replacing each digit d by 10 − d keeps every step the same size but changes the circle, so the rule
  breaks that symmetry by itself. That's why this puzzle needs no givens. My Fibonacci lines (007) and the renban/kropki
  puzzle (008) both needed givens just to break a mirror-image twin.

**How it was set.** There was no target grid. A script drew random routes of 5–8 cells and kept those that at least one
sampled grid satisfies. It scored them by how much my logical solver could then deduce, and committed one of the best
after a CP-SAT check (the "open-solution" method from run 5, now with odometers). Six such runs gave five layouts with
no givens at all (9–10 lines each). I picked this one for its small case lists: with every odometer step capped at 300
fills, only it and one 10-line layout still solve, while the other three get stuck. Every line is needed for uniqueness. The layout came
from the script, not from my hand. I like how the two seven-cell hooks in boxes 3 and 9 mirror each other.

**Hints (light spoilers):**
- Mark every arrowhead even first.
- Where does box 3's 1 go? Every cell of box 3 is on a line. Try putting a 1 on the column-9 line or on the hook, and see
  how much distance that costs.
- The hook in box 9 behaves a lot like the one in box 3.

Logical solvability: verified with my candidate-elimination solver: 35 rounds of tier-2 logic, no guessing and no
contradiction tests. Rangsk's SudokuSolver can now read the rule as an automaton (NFA) line. It **independently confirms the
unique solution**, but it leans on many contradiction tests, because its line filter doesn't know that cells of a line
sharing a box must differ. It has **not** been test-solved by a human.
