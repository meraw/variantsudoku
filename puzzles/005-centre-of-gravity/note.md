# Setter's note — Centre of Gravity

A new line type this time, and no killer cages. A **seesaw** is like an arrow or a cage with weights. A digit far from the
fulcrum counts double or triple, so a small digit at the end of a long arm can balance a big digit close to the middle.
Another way to put it: the fulcrum sits exactly at the line's centre of mass. Every row has one seesaw, and all nine
fulcrums stand in column 5, stacked like a spine down the middle of the grid. The lines are rotationally symmetric
(row 1 mirrors row 9, row 2 mirrors row 8, and so on).

**How it was set.** I didn't grow the clues one by one this time. I chose the shape first: one straight seesaw per row, every
fulcrum in column 5, 180° symmetry. Then I searched the arm lengths, with CP-SAT counting solutions for each layout. Seesaws
are very restrictive. Nine of them alone leave only **two** solutions, and the layout above is the one I found that gets
there. I can't call two solutions a puzzle, and the empty grid gives a human no foothold either: my logical solver
couldn't place a single digit. So I added givens, keeping the ones that helped the logic most, and then removed any given the logic could
do without. Four remained. To be precise about "needed": one given would be enough for uniqueness, but take away
any one of the four and my logical solver gets stuck. They're there for a fair path, not for the count.

Some lines are much tighter than others. Take rows 6 and 8: the short arm (×2, ×1) has to balance a long arm (×1, ×2, ×3, ×4),
so the short-arm digits are big and the long-arm digits small. Rows 2 and 4 are the same lines reversed.

**Hints (light spoilers):** start in row 2. On the right side, the most the two cells can contribute is 9×2 + 8×1.
Compare that with the left side, which already has the 6 at ×2. Row 3 works the same way with the 7 at ×4.
Then use the boxes to pass digits between the rows. The bottom row is a nice case analysis once a few small digits are known.

Logical solvability: verified with my candidate-elimination solver (no guessing, no contradiction tests). The most
work it needed on a single line was checking 56 balancing fills. It has **not** been test-solved by a human.
