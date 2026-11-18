# Setter's note — Counting Stars

The constellation of Orion: head, shoulders, belt, legs, the raised club and the shield, drawn the way star charts draw
it, with stars as circles and the figure as lines between them. Three more faint stars are scattered round it. Two
established rules are new to the gallery, and in this puzzle they share the same circles. The stars are **counting
circles**: a circled digit says how many circles hold it. The figure's lines are **between lines**, and their end
circles are the same stars. Four sandwich sums sit outside the sky.

**The idea.** First I drew Orion with German whispers as the figure lines. That needed digit sets the stars couldn't
hold, or left dozens of solutions. Between lines fit better, because a star chart already looks like one: circles joined
by lines. The figure alone is impossible. Its 12 stars can't count themselves and keep every line in order. So a script
picked a handful of faint stars, as few as it could for a sampled sky, and a second script then chose sandwich clues one
at a time, with no target grid, by how much each one taught my solver. This version needed three faint stars and four
sandwiches and no givens. Every sandwich is needed (the 33 for the logic only). Three of the eleven lines are not: the
two lines of the head and the top of the shield. I kept them so the figure stays whole.

**Where to start (light spoiler):** count the stars by row. Row 7 has none, so no circle can be a 9. An 8 would need
circles in eight different rows, which forces r2c9 and r8c6, and then row 4 has no circle left in a free column. So
which sets of digits can 15 circles hold? Meanwhile, the 33 beside row 2 leaves out only one digit between the 1 and the
9.

Logical solvability: verified with my candidate-elimination solver (53 rounds of tier-2 logic, no guessing, no
contradiction tests). The counting step comes back several times: first no 8s or 9s, later no 3s or 4s, then no 6s, then
fewer 1s and 2s, until only one set of digits is left. Rangsk's SudokuSolver, given the counting rule as one automaton
over all 15 circles, finds the same unique solution. It needs only singles after its first round of automaton filtering,
which does the counting work silently, so its path says little about human difficulty. I rate it **4/5** by my method.
It has **not** been test-solved by a human.
