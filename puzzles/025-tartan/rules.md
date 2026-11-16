# Tartan — rules

Normal sudoku rules apply: place 1–9 once each in every row, column and 3×3 box.

**Entropic lines (orange, rows 2, 5 and 8):** any three consecutive cells along an orange line contain one low digit (1–3),
one middle digit (4–6) and one high digit (7–9).

**Modular lines (teal, columns 2, 5 and 8):** any three consecutive cells along a teal line contain one digit from each of
the sets {1,4,7}, {2,5,8} and {3,6,9}.

**Skyscrapers:** a clue outside the grid is the number of digits visible from that side, looking along the row or column.
A digit is hidden by any larger digit in front of it.

Play: see [play.md](play.md).
