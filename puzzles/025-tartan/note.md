# Setter's note — Tartan

Six lines woven into a plaid and six skyscrapers around the edge. No givens. Modular lines are new to the gallery, and
entropic lines are back for the first time since 004.

**The idea.** Entropic and modular lines are two ways of sorting the digits into threes: by size (low, middle, high) and by
remainder ({1,4,7}, {2,5,8}, {3,6,9}). Each digit is the only one with its pair of labels, like a cell on a phone keypad: its row
says the size, its column the remainder. I wanted a grid where those two sortings cross as literally as possible, so the
orange lines run across and the teal lines run down, three of each, as a tartan.

Along a full-length line the pattern repeats every three cells, so each orange row has the same size class in columns 2, 5 and 8,
and each teal column has the same remainder class in rows 2, 5 and 8. The nine box centres therefore hold all nine digits, laid out
like the keypad with its rows and columns shuffled. The lines alone can't say which class is which, so the skyscrapers have
to label them. A script chose them one at a time, with no target grid, by how much each one taught my solver. The run I kept
needed only six clues and no givens.

**Where to start (light spoiler):** column 1. Its two clues add up to 10, so every digit in that column can be seen from one end
or the other.

Logical solvability: verified with my candidate-elimination solver (24 rounds of tier-2 logic, no guessing, no contradiction
tests). Rangsk's SudokuSolver, which reads entropic and modular lines natively, finds the same unique solution with pointing,
one tuple and skyscraper steps. I rate it **3/5**. It has **not** been test-solved by a human.
