# Watchtowers — rules

Normal sudoku rules apply: place 1–9 once each in every row, column and 3×3 box.

**Lookout towers (invented):** a digit in an amber circle is a lookout tower. Its digit equals the **number of cells it overlooks**.
From the tower, look along its row and its column in all four directions. In each direction, count the cells up to the first digit
that is **larger** than the tower, or up to the edge of the grid. The larger digit blocks the view and is not counted.

Example: a 5 tower. To its left are 3 then 7: it overlooks the 3, and the 7 blocks (1). To its right are 2, 4, 1, 9: it overlooks
2, 4 and 1, and the 9 blocks (3). Above it is an 8, which blocks straight away (0). Below it is a 1, then the edge (1). Total
1 + 3 + 0 + 1 = 5, so this 5 works as a tower.

**Skyscrapers:** a grey clue outside the grid is the number of digits you can see from that side of the row or column. A digit is
seen if it is larger than every digit in front of it.

Play: see [play.md](play.md).
