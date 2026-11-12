# Factor Tree — rules

Normal sudoku rules apply: place 1–9 once each in every row, column and 3×3 box.

**Factor lines (red):** for every two neighbouring cells along a red line, one digit is a factor of the other (it divides it exactly).
For example 2–8, 3–9, 6–3 and 1–7 can be neighbours, but 4–6 and 2–3 can't. A digit may repeat on a line where sudoku rules allow it.
The trunk and the six branches are separate lines. Each branch starts on the trunk cell it grows from.

**Little killers:** a number outside the grid, with an arrow, gives the sum of the digits along that diagonal. Digits may repeat on a
diagonal where sudoku rules allow it.

Play: see [play.md](play.md).
