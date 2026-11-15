# Setter's note — Combination Lock

A padlock drawn with lockout lines, a keyhole cage, and seven sandwich clues around the edge as the combination. Lockout lines
are new to the gallery. No givens.

**The rule in one line:** the diamonds are at least 4 apart, and everything else on the line stays outside them. So a lockout line
always shuts out at least five digits (both diamonds and everything between). The body's top bar has three inner cells in one
row, so they must use three of the at most four digits left outside.

**The idea.** I drew the lock first. The body is four lockout lines meeting at diamond corners, the shackle is a fifth line
over the top that shares the body's two top diamonds, and the keyhole is a cage. My first, taller shackle made the puzzle
impossible (columns 3 and 7 ran out of room), so the arch comes down to row 3. Then a script chose the keyhole total and
the sandwich clues one at a time, with no target grid. Each clue was picked by how much it taught my solver. The run I kept
needed no givens.

**Where to start (light spoiler):** row 6, the top of the lock. The 28 sandwich has to fit around a lockout bar whose three inner
digits all avoid the corners' range. Only one pair of corner digits survives, and then the shackle knows a lot about itself.

Logical solvability: verified with my candidate-elimination solver (48 rounds of tier-2 logic, no guessing, no contradiction
tests). Rangsk's SudokuSolver, with the lockout lines given as small automata, finds the same unique solution using only
pointing, tuples and sandwich steps. Its lockout reasoning happens silently inside the automaton filter, though, so its log looks
lighter than the solve is. I rate it **4/5**. It has **not** been test-solved by a human.
