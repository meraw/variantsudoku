# Combination Lock — rules

Normal sudoku rules apply: place 1–9 once each in every row, column and 3×3 box.

**Lockout lines:** the two diamonds at the ends of a slate line hold digits that differ by at least 4. Every other digit on that line
must lie outside the range of the two diamonds: smaller than the smaller diamond or larger than the larger one (equal to either is
not allowed). Digits may repeat on a line where sudoku allows. Lines may share a diamond.

**Killer cage:** the digits in the dashed cage (the keyhole) sum to the small total and don't repeat.

**Sandwich sums:** a clue outside the grid gives the sum of the digits between the 1 and the 9 of that row or column.

Play: see [play.md](play.md).
