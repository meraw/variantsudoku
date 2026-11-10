# Setter's note — Carry the One

Every marked row or column is the old puzzle "ABC + DEF = GHI with each digit once", because a sudoku row already uses each
digit once. As far as I know, using it as a sudoku constraint on whole rows and columns is new. It has 336 solutions,
and they all share some lovely facts:

- **The answer's three digits always sum to 18** (so the two numbers being added sum to 27).
- **There is exactly one carry**, either out of the units column or out of the tens column, never both, and never out of the hundreds.
- The answer starts with 4 or more.

Each of these takes one line to prove (casting out nines), and together they are most of the solve.

**How it was set.** First I asked the computer how many rows and columns can be sums at once: 8 seemed to be the most. Then I
tried patterns I liked. Rows 1, 3, 5, 7, 9 with columns 1, 5 and 9 turned out to be amazingly tight: of the 256 ways to place the
symbols, only 2 have any solution at all, with exactly 3 grids each. A single given **1** then makes the solution unique. But neither of my solvers
can solve it from there without guessing, so I didn't publish that version. Three 1s make it fair, hence the title. The 1 in row 2 is the
one that makes the solution unique. The other two are there so you can solve it without guessing. The row-1 sum is the one clue that isn't
strictly needed (both the solution and the logic survive without it); I kept it because it completes the pattern.

**Hints (light spoilers):**
- Look at the 1 in row 3. It is the last digit of that row's answer, so the last digits of the two numbers being added (r3c3 and
  r3c6) must make 11. That's the carry, so the tens column has none.
- Where a marked row meets a marked column, the cell is a digit of both sums. Combine what each sum says about it.

Logical solvability: verified with my candidate-elimination solver (35 rounds of tier-2 logic, each step one sum against the
candidates, no guessing and no contradiction tests). Independently, Rangsk's SudokuSolver, given each sum as an automaton,
**solves it logically** with line checks, two tuples and singles. It has **not** been test-solved by a human.
