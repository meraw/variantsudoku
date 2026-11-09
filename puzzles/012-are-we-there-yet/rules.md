# Are We There Yet? — rules

Normal sudoku rules apply: place 1–9 once each in every row, column and 3×3 box.

**Odometers (invented rule, blue lines):** every blue line starts in a circle. Travel along the line from the circle to the
arrowhead and add up the size of every step, i.e. the difference between each pair of neighbouring digits on the line. The
step out of the circle counts too. This total distance must equal the digit in the circle.

*Example:* a line reading 5 – 4 – 2 – 4 from its circle travels 1 + 2 + 2 = 5, so the circle may hold 5.
A line 7 – 5 – 2 – 3 – 4 travels 2 + 3 + 1 + 1 = 7. ✓

Digits may repeat on a line if sudoku rules allow.

No given digits.

Play: see [play.md](play.md).
