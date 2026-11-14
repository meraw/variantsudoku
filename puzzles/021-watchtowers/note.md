# Setter's note — Watchtowers

A new rule, as far as I know. The clue is a circle with nothing written in it: the digit in the circle is its own clue. It says how
many cells that digit can see along its row and column before a taller digit blocks the view. It is a cousin of the skyscraper
clue (how many buildings you see from outside), but the view is from inside the grid and counts cells, not peaks. So the
eight towers share the grid with five ordinary skyscraper clues, all on the bottom and left edges. There are no givens, and all
13 clues are needed for a unique solution.

**Things worth finding before you start:**
- A tower is never a 1 (there is nothing smaller to see) and never a 9 (it would see all 16 cells of its row and column).
- A tower t can overlook at most t − 1 cells of its row, because only t − 1 digits are smaller. The same holds for its column.
  So every tower overlooks at least one cell in its row and at least one in its column. A 2 tower needs a 1 right next to it in its row
  and another 1 right next to it in its column.
- An 8 tower is blocked only by the 9s, so it is really a statement about where the 9s of its row and column sit.

**How it was set.** No target grid. A script offered every free cell as a tower, and every skyscraper count still possible at every
free edge position, and placed the clue that taught my solver the most. Towers on their own can't finish a puzzle: an ordinary
grid has about five towers, and a towers-only run stalled after 13, when no further tower fitted anywhere. So the skyscrapers are
needed. I weighted the script to prefer towers. Of five runs, I kept the one with clues on only two edges. I also tried
hand-drawn tower patterns. Nine towers on the main diagonal needed two givens, and nine towers in the box centres needed 16
skyscrapers. Neither was as clean. (Curiosity: the four corners can never all be towers.)

**Hint (light spoiler):** start in box 7. The 7 below column 3 and the two towers on the bottom row squeeze the box. Three of its
cells must hold 7, 8 and 9, and the corner tower turns out to be a 6.

Logical solvability: verified with my candidate-elimination solver (45 rounds of tier-2 logic, no guessing, no contradiction tests).
Rangsk's SudokuSolver, given each tower as an automaton that knows its row and column digits are all different, finds the same
unique solution and solves it with clue steps, two pointing steps and one tuple. I rate it **4/5**. It has **not** been
test-solved by a human.
