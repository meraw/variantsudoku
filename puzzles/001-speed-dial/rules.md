# Speed Dial — rules

Normal sudoku rules apply: place 1–9 once each in every row, column and 3×3 box.

**Keypad lines (purple):** two cells that are next to each other along a purple line must hold digits that are
orthogonally adjacent on a standard keypad:

```
1 2 3
4 5 6
7 8 9
```

So 5 can sit next to 2, 4, 6 or 8; 2 can sit next to 1, 3 or 5; 1 can sit next to only 2 or 4.
(A computer numpad has 7 8 9 on top, but the adjacencies are identical, so either picture works.)
Digits may repeat on a line if sudoku rules allow it.

*Keypad lines are an invented rule (as far as the setter knows) introduced in this puzzle.*

Givens: r6c2 = 8, r8c1 = 4, r9c5 = 3.

Play: see [play.md](play.md).
