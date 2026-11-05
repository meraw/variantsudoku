# Setter's note — Picture Frame

The main feature is one big entropic loop, a 24-cell frame running through rows 2 and 8 and columns 2 and 8. Entropic lines have
a rhythm: low/middle/high in some order, then the same order again. On a closed loop that rhythm has to fit exactly,
so a loop only works if its length is a multiple of 3. 24 cells is just right. (I also tried adding the two long
diagonals as entropic lines. The solver showed that frame + diagonals is impossible, so the diagonals shrank to the little
cross in the centre.)

**How it was set.** I drew the frame and the cross first. Then I grew killer cages against a fixed grid in 180°-symmetric pairs,
keeping the pair that helped my logical solver most each time, and removed every pair that wasn't needed. Eight cages
remain, and here they are all needed: removing any one cage, or the centre cross, leaves several solutions.

**Hints (light spoilers):** number the frame cells 0–23 around the loop. Every third cell is in the same class, and that includes
all four corners. Find a cage that tells you what that class is. A second small cage then fixes the whole frame's rhythm.
Each frame row and column has seven cells on the loop, so the two cells left over in that row or column are easy to classify.

Logical solvability: verified with my candidate-elimination solver (no guessing). It has **not** been test-solved by a human.
