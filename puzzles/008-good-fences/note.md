# Setter's note — Good Fences

A classic ruleset this time, as a counterweight to the invented Fibonacci lines: renban lines plus white kropki dots
with the negative constraint. The two rules pull against each other. A renban wants consecutive digits close together.
An undotted edge is a fence that keeps consecutive digits apart.

**Where they meet:**
- Three renban cells in a straight orthogonal row can't all have fences between them. The middle digit would need
  to be non-consecutive with both neighbours, and no set of three consecutive digits allows that.
- The two L-shaped renbans have **no** dots at all, so each holds five consecutive digits snaking around a corner
  with no two neighbours on the line consecutive.
- The diagonal renban through the centre has no fences between its own cells, because they only touch at corners.
  The dots and fences around it still restrict it.

**Why there are four givens.** Replace every digit d by 10 − d and consecutive digits stay consecutive, so every
renban and every dot still works. Without givens the puzzle therefore always has at least two solutions. Here it has
exactly two, and the second is the first turned upside down. The givens are placed as 180°-symmetric pairs whose
digits sum to 10 (8 and 2, 4 and 6), so the picture stays symmetric. Each given is needed for the logical path, though
not for uniqueness.

**How it was set.** I drew the renbans first, then asked CP-SAT for grids that satisfy them while having at most twelve
consecutive neighbour pairs, in a 180°-symmetric pattern. In such a grid the dots are not my choice: the negative constraint
means every consecutive pair must be marked. I kept a grid whose dots and renbans left only the twin pair of solutions.
Then I added symmetric given pairs, guided by the logical solver. My first layout also had two short vertical renbans
at the right and left. I removed them: with dots on both steps, a straight three-cell line is already forced to be
consecutive, so they added nothing. The method is close to the one I used for Which Way Up (a symmetric negative
constraint, then givens to break the symmetry). The rules and the logic are different, but I want to say so.

**Hints (light spoilers):** start at the 8 in row 2. Both of its neighbours are dotted, so they are 7 and 9. Now
look at the top-left L, which contains one of them. If that cell were 9, the L would need 5, 6, 7, 8, 9. Its two cells
in row 2 could then only be 5 and 6, which are consecutive and have no dot between them. The bottom-right L
mirrors this with the 2.

Logical solvability: verified with my candidate-elimination solver (no guessing, no contradiction tests). Its two
biggest steps were the L renbans, where only three fills survive once the fences are taken into account. It has **not**
been test-solved by a human.
