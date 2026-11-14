# Mind the Gap — rules

Normal sudoku rules apply: place 1–9 once each in every row, column and 3×3 box.

**1-5-9 indexing (shaded columns):** in every row, the digit in column 1 tells you which column holds that row's 1. The digit in
column 5 tells you which column holds that row's 5, and the digit in column 9 tells you which column holds that row's 9.
Example: if r3c1 = 7, then r3c7 = 1. If r6c5 = 5, the 5 of row 6 is in column 5 itself.

**German whispers:** neighbouring digits along a green line differ by at least 5.

**Thermometers:** digits strictly increase along a grey thermometer, starting from the bulb.

Play: see [play.md](play.md).
