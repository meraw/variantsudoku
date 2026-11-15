# Setter's note — Trail Map

A map of two mountain ridges with five hiking trails. The rule is short: every summit is on the map. A summit is a cell
bigger than all four of its orthogonal neighbours, and the shaded cells are exactly the summits, no more and no fewer.

Marked "bigger than its neighbours" cells (maximum or fortress cells) are an established rule. The new part is that the map is
complete. The unmarked cells carry information too: each one must have a bigger neighbour somewhere. As far as I know that
"complete map" twist is new.

**The idea.** A 9 is always a summit, so every 9 sits on the map. An 8 that isn't on the map must be touching a 9. I drew the
two ridges first: a big Λ peaking at r1c5 and a smaller one in front of it peaking at r6c5. A solver search said the picture
needs exactly two more summits, and only a handful of positions work for them. I put them in the sky as two stars (r1c1 and r2c9).
Then a script laid straight thermometers that must end on a summit, like trails climbing to a peak, and kept them only
where they taught my solver something. The run I chose needed just five trails and no givens.

**Where to start (light spoiler):** count summits row by row. One row has only one, and that settles a column, and then the
9s fall into place box by box. After that, ask which unmarked cells could hold an 8.

Logical solvability: verified with my candidate-elimination solver (37 rounds of tier-2 logic, no guessing, no contradiction
tests). Rangsk's SudokuSolver, given the summits natively and the "no other summits" rule as small automata, finds the same unique
solution with a light path: tuples, pointing and a few direct cell forcings. I rate it **3/5**. The negative half of the rule is the
part to get used to. It has **not** been test-solved by a human.
