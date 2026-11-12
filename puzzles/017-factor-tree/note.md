# Setter's note — Factor Tree

In school maths a *factor tree* splits a number into its factors, branch by branch. This one is a fir tree drawn in factor lines: a trunk
down column 5 and three pairs of diagonal branches. The only other clues are six little killers around the edge. There are no givens.

Factor lines (from the Logic Masters "Sudoku Variants Series") and little killers are both new to this gallery. Little killers were the plan
back in run 4, but my solver couldn't check them then. Now it can solve this puzzle, and Rangsk's solver gives a second opinion.

**Facts worth finding:**
- 1 divides everything, but **5 and 7 can only sit next to a 1** on a factor line. They are the lonely primes. 9 can only touch 1 or 3.
- The trunk is 8 cells in one column. Only 16 orders work, and each starts with a lonely prime and a 1 at one end. So the cell above the
  trunk, the star on top of the tree, must be the *other* lonely prime.
- Swapping every 4 with 8, or every 5 with 7, keeps every factor line happy. The little killers are what tell them apart.

**How it was set.** I drew the tree first and never changed it. Then I chose little killers one at a time from the sums still possible,
with no target grid: each time, the one that let my solver deduce the most. Several runs finished with six clues and no given. I kept the
only one with clues on all four sides. Two of the branches aren't needed for uniqueness. I kept them because a tree with branches missing
on one side looks broken. The verification report lists which marks are needed for what.

**Hints (light spoilers):**
- The 6 and the 24 are three-cell diagonals inside one box.
- The 14 is a long diagonal with a very small total. Which trunk cell does it cross, and what does that do to the trunk's order?

Logical solvability: verified with my candidate-elimination solver (21 rounds of tier-2 logic, no guessing, no contradiction tests).
Independently, Rangsk's SudokuSolver, given each factor line as a pairwise rule plus an automaton of the line's valid fills, finds the same
unique solution and solves it with tuples, pointing and sum checks. I rate it **3/5**, a gentle one for the season. It has **not**
been test-solved by a human.
