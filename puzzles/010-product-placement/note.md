# Setter's note — Product Placement

A new invented line: on a **bridge**, the two circled ends multiply to give the sum of everything in between.
Multiplication doesn't respect any digit relabelling, so unlike my Fibonacci lines (007) or the renban/kropki
puzzle (008), there's no built-in twin solution. The givens here carry real information; they don't just break a symmetry.

**Facts I found with small scripts before setting:**
- A three-cell bridge whose cells all see each other (one row, column or box) must be 2 – 6 – 3 or 2 – 8 – 4 in some
  order of the ends. Every such bridge has a 2 at one end.
- A 1 at one end makes the middle equal to the other end. A three-cell bridge can only do that when its middle cell
  and that far end don't see each other.
- If the inner cells of a bridge fill a whole 3×3 box, they sum to 45, so the ends must be 5 and 9.
- A bridge can never fill an entire row: the ends a and b would need (a + 1)(b + 1) = 46 = 2 × 23.
- Nine three-cell bridges, one in every box, were never satisfiable in my tests (0 of 40 random layouts, 0 of 300
  symmetric ones). Four or five usually are.

**How it was set.** The first plan was *Seven Bridges*, after Euler's Königsberg problem: four killer cages as the land
masses and exactly seven bridges joining them in Euler's pattern. It didn't work. A random grid satisfies a given
bridge about 1–3% of the time, so each bridge carries only about 5–7 bits, against roughly 72 needed for a unique
sudoku. Seven bridges plus four cages still needed eight givens. A version with a river (a slow thermometer for each
river arm) had no solution at all in the geometry I drew. Both are in the setter's log.

What worked was a designed break-in, a 45-rule bridge. The teal serpentine winds through all nine cells of the
centre box from r5c3 to r5c7, so its ends are 5 and 9. Around it, a script placed bridges in 180° pairs without any
target grid. Each candidate line had to be satisfiable (sampled grids, then CP-SAT) and was scored by how much my
logical solver could then deduce. When no line helped enough, a given became allowed. Four runs gave 2–4 givens; this
one needed only two. Afterwards one bridge turned out to be redundant (its symmetric partner does the work), so I
removed it and the symmetry breaks in that one corner. Every remaining bridge and given is needed: without any of them
except one bridge, the puzzle has more than one solution. Without that bridge (r9c8–r7c9) it stays unique, but the
logic then needs contradiction tests.

**Hints (light spoilers):**
- Start at the 4. Its bridge lies entirely inside box 4, so 4 × (one end) = (the middle).
- Then look just above: a bridge whose ends share a row and a box, but whose middle sits in another box.
- The serpentine's ends are 5 and 9, which gives the 5 and 9 of box 5 only rows 4 and 6.

Logical solvability: verified with my candidate-elimination solver (no guessing, no contradiction tests; the biggest
steps are case lists of 54 and 106 fills on the two six-cell bridges). Rangsk's SudokuSolver can't model this
invented rule, so there's no second solver check. It has **not** been test-solved by a human.
