# Setter's note — Unlucky for Some

This run fell on Friday 13 November, so every number in the puzzle is a 13. There are three killer cages, three little killers and three
X-sums, nine 13s in all. There are no givens. Each of the nine clues is needed: take any one away and the puzzle has more than one solution.

**How it was set.** Usually the hard part of setting is choosing the numbers. Here the numbers were decided before I started, and I could
only choose where the 13s go. A new script tried every spot where a 13 could still go: every small cage, every diagonal of three or more
cells, every X-sum position or sandwich line. It placed the one that told my solver the most, and stopped as soon as the grid was forced.
Seven of eight runs finished with 9–10 clues; one stalled. I didn't use any of the runs with sandwich sums, because a sandwich 13 and an X-sum 13 look
identical outside the grid. I kept the run with three of each kind.

**Facts worth finding:**
- An X-sum of 13 is short. X can't be 1 or 2, and X = 5 would need at least 5+1+2+3+4 = 15. So the first digit is a 3 (followed by a pair
  summing to 10) or a 4 (followed by {1,2,6} or {1,3,5}).
- A 13 on a long diagonal is very small. Count the smallest total each diagonal can have, box by box.

**Hint (light spoiler):** the 13 in the top-right corner covers eight cells. Its smallest possible total is 11, not 8. Now look at the cage
it passes through.

Logical solvability: verified with my candidate-elimination solver (25 rounds of tier-2 logic, no guessing, no contradiction tests). Rangsk's
SudokuSolver, given all three rules natively, finds the same unique solution and solves it with clue checks, one tuple and singles. I rate it
**3/5**. It has **not** been test-solved by a human.
