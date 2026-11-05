# Knight Calls — rules

Normal sudoku rules apply: place 1–9 once each in every row, column and 3×3 box.

**Anti-knight:** two cells a chess knight's move apart cannot contain the same digit.

**Knight lines (purple):** two cells that are next to each other along a purple line must hold digits that are a
chess knight's move apart on a phone keypad:

```
1 2 3
4 5 6
7 8 9
```

So 1 may sit next to only 6 or 8, 2 only next to 7 or 9, and so on. 5 has no knight moves, so it can never appear on a line.
The purple square in box 5 is a closed loop: its last cell also neighbours its first. Digits may repeat on a line if
sudoku rules allow it.

**Killer cages:** digits in a cage do not repeat and add up to the small number in the cage's top-left corner.

No given digits.

*Knight lines are an invented rule (as far as the setter knows), a follow-up to the keypad lines of #001 Speed Dial.*

Play: see [play.md](play.md).
