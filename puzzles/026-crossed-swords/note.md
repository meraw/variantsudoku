# Setter's note — Crossed Swords

Battlefield clues around a pair of crossed swords. Battlefield is new to the gallery; the swords are German whisper blades
with Dutch whisper hilts. No givens, six clues.

**The rule in one line:** each row or column with a clue holds two armies, sized by its two end digits, and the clue adds up
where they clash (or the no man's land between them). So a 1 in a column can only be a single cell holding 1. And a total
in the high 30s means a long overlap or a long gap, which tells you a lot about the ends.

**The idea.** I drew the swords first. The blades cross in the middle of box 5, which already says something: r5c5 has four
whisper neighbours in its own box, and they must all be different. Hilts made of German whispers were impossible, so they became
Dutch whispers, a slightly gentler line, in orange. Then a script chose the battlefield clues one at a time, with no target grid,
by how much each one taught my solver. Some runs needed only four clues. I kept a six-clue run because it had the most
interesting solve.

**Where to start (light spoiler):** row 8. A 37 is far too big for a short overlap. Count which digits can be left out.

Logical solvability: verified with my candidate-elimination solver (25 rounds of tier-2 logic, no guessing, no contradiction
tests). Rangsk's SudokuSolver, with each battlefield clue given as a small automaton, finds the same unique solution using
only pointing, tuples and direct cell forcings. I rate it **3/5**. If battlefield arithmetic is new to you, it may feel more
like a 4. It has **not** been test-solved by a human. One line, the left sword's grip, isn't needed for the solve; it's
there to finish the picture.
