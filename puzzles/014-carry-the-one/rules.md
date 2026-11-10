# Carry the One — rules

Normal sudoku rules apply: place 1–9 once each in every row, column and 3×3 box.

**Sums (invented rule, red symbols):** some rows and columns carry two red symbols, a **+** and an **=**, on their box borders.
Read such a row (left to right) or column (top to bottom) as three three-digit numbers, one per box. It must be a correct sum,
with the symbols read in order:
- **+ then =** means *first + second = third*;
- **= then +** means *first = second + third*.

A symbol sitting on the border between two cells of a row belongs to that row; one between two cells of a column belongs to that column.

*Example:* a row reading 2 1 8 | 3 4 9 | 5 6 7 and marked + then = is correct, because 218 + 349 = 567.

The only given digits are 1s.

Play: see [play.md](play.md).
