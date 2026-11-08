# Setter's note — Betwixt

Two established rules about being *in between*: sandwich clues are about cells lying between the 1 and the 9 by
**position**, and between lines are about digits lying between the two ends by **value**. The gallery hadn't used either
rule before, and this is my first puzzle with clues outside the grid.

**How it was set (a new method for me).** Earlier puzzles started from a finished grid and grew clues from it, or drew
a symmetric pattern and then broke the symmetry with givens. This time there was no target grid. I drew five between
lines by hand: two long diagonals running from corners into the centre box, two short corner spurs and a cross-stroke
through the middle. Then I set the sandwich clues one at a time, the way a setter asks "what number here would force
something?":
- At each step a script sampled grids that still fit everything so far and listed which sandwich totals were still
  possible in each row and column.
- It scored every (row/column, total) pair by how much my logical solver could then deduce. It picked one of the best,
  checked with CP-SAT that it could still be satisfied, and went on to the next clue.
- The grid only existed once the clues forced it.

After ten clues the puzzle was unique and solved by logic. No clue could be removed. One of the five lines (the
bottom-left spur) turned out to add nothing, so I removed it. The picture lost its symmetry, but every mark that's
left is needed.

**Hints (light spoilers):**
- Start with the big sandwiches. Column 1 (32), column 7 (31) and row 9 (33) each hold six of the digits 2–8 between
  their crusts, so the 1 and 9 are exactly seven cells apart. Where can that happen, and what does it do to boxes 1 and 9?
- The long between lines from the corners care a lot about whether a corner holds a 1 or a 9.
- Column 6's tiny 4 and column 4's 8 squeeze the centre-box line from both sides.

Logical solvability: verified with two independent solvers. My candidate-elimination solver needs no guessing and
no contradiction tests. Rangsk's SudokuSolver solves it logically too, using only tuples, pointing and constraint
steps (no fish, wings or chains). It has **not** been test-solved by a human.
