# Skyline Sums — rules

Normal sudoku rules apply: place 1–9 once each in every row, column and 3×3 box.

**X-sums (plain numbers outside the grid):** read the row or column from the clue. The first digit you meet is X; the clue
is the sum of the first X digits, counting that first digit itself. *Example:* a row starting 3 – 5 – 1 – … has X-sum 3 + 5 + 1 = 9.

**Skyscrapers (numbers in grey boxes):** each digit is a building of that height. Looking along the row or column from the
clue, a building is visible unless a taller one stands in front of it. The clue is the number of visible buildings.
*Example:* 2 – 5 – 3 – 7 – 1 – 9 – … shows 2, 5, 7 and 9, so its clue would be 4.

The skyscraper clues are: below columns 3, 6 and 8; to the right of rows 2, 4 and 5; to the left of row 6.
Every other clue is an X-sum. Rows and columns without a clue have no extra constraint.

No given digits.

Play: see [play.md](play.md).
