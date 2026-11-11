# Setter's note — Compass Rose

The first arrows in this gallery. Eight arrows point out from one circle in the centre, one per compass direction. There are no other marks
inside the grid, no givens, and eight sandwich clues around the edge, like bearings.

**The rose is the break-in.** Every arrow starts in box 5, so the eight first cells and the circle are 1–9 between them. If the circle
weren't 9, the 9 would be at the start of some arrow, and that arrow would sum to more than its circle. So the centre is 9, and every outer
cell is 9 minus the box-5 cell beside it. Row 5 and column 5 now have their 9 for the sandwich clues.

**How it was set.** I drew the compass first and then tried three partners for it. More arrows, grown by the computer or placed in
rotation-symmetric sets, needed 2–5 givens. German whispers needed 2–5 givens and ran over the rose. Sandwich clues, chosen one at a
time from the values still possible (no target grid), finished with eight clues and **no given** in one of five runs. That's this puzzle.
Every sandwich clue is needed. Three of the arrows (east, south-west, west) aren't needed for uniqueness, only for a guess-free path.
I kept them because a compass with gaps isn't a compass.

**Hints (light spoilers):**
- Find the centre digit first (see above).
- A sandwich of 33 contains almost every digit from 2 to 8. Which one is missing, and where can it go?
- The 4 under column 9 leaves very little room between that column's 1 and 9.

Logical solvability: verified with my candidate-elimination solver (62 rounds of tier-2 logic, no guessing, no contradiction tests).
Independently, Rangsk's SudokuSolver (both rules native) finds the same unique solution and solves it logically with basic steps plus one
TUVWXYZ-wing and one region forcing chain. That's crunchy, but well short of Pinwheel Whispers. Rated **4/5**. It has **not** been test-solved by a human.
