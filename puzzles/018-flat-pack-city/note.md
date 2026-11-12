# Setter's note — Flat-Pack City

A city that arrives in a flat box: the regions are jigsaw pieces, and the only clues are ten skyscraper counts around the edge. There are no givens.
It's the first jigsaw in this gallery.

**The pieces.** Each region is a 3×3 box with a tab sticking into one neighbour and a slot where another neighbour's tab fits. I searched
for every way to give the boxes tabs (1 or 2 cells deep) so that each region keeps nine connected cells. At most 10 of the 12 inner edges can
carry a tab, and I picked a layout that is mirror-symmetric left to right. The tabs climb the outer columns and the middle column slides down.

**Facts worth finding:**
- *Law of leftovers.* The top three rows hold the top three pieces, apart from the long tab that hangs into rows 4–5 of the middle
  column. Two tabs from below poke into row 3 instead, so those two cells hold the same pair of digits as the hanging tab. The same works at the
  bottom, and for the left and right stacks: r2c4 = r8c3 and r2c6 = r8c7.
- A skyscraper 7 means only two buildings are hidden, so the low digits are pushed far away from that clue.

**How it was set.** I drew the pieces first, then tried partners for them with no target grid: region-sum lines (which care about
region shapes, so they seemed the natural partner), German whispers, thermometers and outside clues. The lines all needed 3–5 givens
or gave easy, random-looking puzzles. Skyscraper clues, chosen one at a time by how much they let my solver deduce, finished with
ten clues and no givens. Every clue but one is needed for uniqueness, and the remaining one (the 4 above column 5) is needed to avoid guessing.

**Hints (light spoilers):**
- Start with the 7 at the top right. Where can the 9 of row 1 be, and which piece does that cell belong to?
- Row 4 has clues at both ends, 6 and 4. Where is its 9?

Logical solvability: verified with my candidate-elimination solver (51 rounds of tier-2 logic, no guessing; the law of leftovers does
real work in 10 of them). Independently, Rangsk's SudokuSolver finds the same unique solution and solves it logically, using a finned
X-wing, a few region forcing chains and one contradiction test along the way. I rate it **4/5**, crunchy. It has **not** been
test-solved by a human.
