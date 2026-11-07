# Liber Abaci — rules

Normal sudoku rules apply: place 1–9 once each in every row, column and 3×3 box.

**Fibonacci lines (gold, invented rule):** read each line starting from the end with the dot. From the third cell on,
every digit is the **last digit of the sum of the two digits before it**.

*Example:* `3 4 7 1 8` works: 3+4 = 7, 4+7 = 11 (last digit 1), 7+1 = 8.

A 0 can never be placed, so two neighbouring digits that are followed by a third digit on the line never sum to 10.
Digits may repeat on a line if sudoku rules allow it.

Given digits: 4.

Play: see [play.md](play.md).
