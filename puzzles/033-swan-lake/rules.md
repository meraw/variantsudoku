# Swan Lake — rules

Normal sudoku rules apply: place 1–9 once each in every row, column and 3×3 box.

**Graceful lines (blue, invented):** along each blue line, the differences between neighbouring digits are all
different. *Example:* 2 – 7 – 5 – 6 works (differences 5, 2, 1). 3 – 5 – 7 does not (2 and 2).
Digits may repeat on a line where sudoku allows. Two equal neighbours count as a difference of 0, so this can happen at
most once per line.

There are three lines: the swan's neck and belly (from the head at r2c2 down to r8c6), the swan's wing and tail (from
r7c5 over the wing to r8c7; the two swan lines do not join), and the lake (the whole of row 9, drawn as a wave).

**Sandwich sums:** a number outside the grid is the sum of the digits between the 1 and the 9 in that row or column.

No given digits.

Play: see [play.md](play.md).
