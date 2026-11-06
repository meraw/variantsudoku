# Centre of Gravity — rules

Normal sudoku rules apply: place 1–9 once each in every row, column and 3×3 box.

**Seesaws (brown lines, invented rule):** each brown line is a seesaw resting on its circled cell, the *fulcrum*.
Every other digit on the line pushes its side down with a force equal to the digit × its distance from the fulcrum,
counted in cells along the line. The cells next to the fulcrum count ×1, the next ones ×2, and so on.
Every seesaw balances: the total on the left of the fulcrum equals the total on the right.
The digit in the fulcrum cell is not part of either total.

*Example:* a line reading `9 (F) 1 4` balances, because 9×1 = 1×1 + 4×2.

Given digits: 4.

Play: see [play.md](play.md).
