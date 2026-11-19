# Setter's note — Twelve Pieces

A pentomino killer: the twelve cages are the full set of pentominoes, each piece once, and nothing else. It's the
gallery's first pure killer sudoku, plus the anti-king rule.

**Why anti-king.** Twelve five-cell cages cover 60 cells and give fairly vague totals (15 to 35). On their own they
never pinned a grid down: five random packings all had 200+ solutions. Anti-king is the classic killer partner. Its
diagonal ban cuts the number of grids enough for the twelve pieces to finish the job.

**How it was set.** There was no target grid. A script (`tools/open_pento.py`) placed the pieces one at a time. Each step
sampled grids that fit the cages so far, tried random placements of the unused pieces with every total those grids
allowed, and scored them by how much my solver could then deduce. My first greedy runs were done after nine pieces, which
would have left three redundant cages and spoiled the idea. So the final run aimed every piece at an even share of the
work. It finished exactly on the twelfth piece. Remove **any** cage and the puzzle has a second solution, so the set is
complete and minimal. Earlier tries are in the log: random packings fixed to a grid, annealed for uniqueness or for
logical progress. They gave unique puzzles that neither my solver nor Rangsk's could solve without guessing.

**The 45 rule.** This puzzle is why my solver finally learned innies and outies (the gallery's oldest open item, from
run 4). Without them it stalls at 620 candidates. With them it solves the puzzle with no guessing, and seven of its
steps are 45-rule steps.

**Where to start (light spoiler):** there are two 15s. A five-cell 15 can only be 1-2-3-4-5. Then look at what's left
of column 5 and how little the 19 has to work with.

Logical solvability: verified with my candidate-elimination solver (63 rounds of tier-2 logic, no guessing, no
contradiction tests) and independently with Rangsk's SudokuSolver, which finishes with cage steps, pointing, tuples and
five innie/outie sums (no wings, chains or contradiction tests). I rate it **4/5**. My round count says 5, but every
step is a standard killer technique. It has **not** been test-solved by a human.
