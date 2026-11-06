# Setter's note — Which Way Up

A classic ruleset this time, and a gentle one: thermometers, XV with the negative constraint, and a single given digit.

**Why exactly one given?** Everything else in the grid is 180°-symmetric: the four thermometers, and every X and V,
including the places where there *isn't* a mark. Turn any solution upside down and it still satisfies all the clues.
So without givens this puzzle can never be unique. It has exactly two solutions, and each is the other one rotated by 180°. The 7 in
the middle of the grid is there only to tell you which way up the grid goes. In the other solution that cell is a 3.

**How it was set.** I drew the thermometers first: four diagonals from the centre box out to the corners, all running
outwards. Then I asked CP-SAT for grids that satisfy the thermometers *and* have an X/V pattern that is
180°-symmetric, with 12–16 marks, under a random objective so that every seed gives a different grid. For each grid that
had exactly the two twin solutions, I tried every single given that breaks the tie and kept the
designs where my logical solver could finish from that one digit alone. This grid had 30 such givens. I chose r6c5,
which needs the most logic of the 30 and also sits in the middle of the picture. Every thermometer earns its place:
take any one away and the solver either needs trial-and-error or gets stuck. With the r6c4 thermometer gone, the
puzzle isn't even unique any more.

**Hints (light spoilers):** start top-left. The cell r2c2 is third on its thermometer, so it can't be small. It also has a V
below it and an X above it. The bottom-right corner is the same shape turned round. After that, the unmarked edges do
most of the work. A placed digit d rules out 5−d and 10−d in every unmarked neighbour, so every digit except 5 removes
something.

Logical solvability: verified with my candidate-elimination solver (no guessing, no contradiction tests). It has **not**
been test-solved by a human.
