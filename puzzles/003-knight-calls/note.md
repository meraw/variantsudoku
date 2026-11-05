# Setter's note — Knight Calls

Everything here is a knight's move. The sudoku is anti-knight, the lines connect digits a knight's move apart on a keypad,
and the four corner lines are even drawn in the shape of a knight's move.

**The useful picture.** Join each keypad digit to the digits a knight's move away. 5 is left out, and the other eight form
a single ring:

```
1 – 6 – 7 – 2 – 9 – 4 – 3 – 8 – (back to 1)
```

So a knight line is just a walk around this ring, one step at a time. Two more facts fall out of it. The ring alternates
odd and even. Digits directly opposite each other on the ring (1/9, 6/4, 7/3, 2/8) always add up to 10.

**How it was set.** I started with the centre loop. Eight cells in one box can't repeat, so the loop has to be the whole
ring in order, and that leaves 5 in the middle. Then I added four L-shaped lines in the corners and the anti-knight rule.
At that stage the solver found 32 grids, and every one of them came in a family of 16 relabellings: you can rotate or
reflect the ring and nothing changes. Givens alone made the logic murky, so I broke the symmetry with killer cages instead.
I grew them in 180°-symmetric pairs against a fixed grid, keeping whichever pair helped my logical solver most, and then
removed every pair that wasn't needed. Four cages survived. To be precise about "needed": any three of the four cages
already give a unique solution, but with only three my logical solver gets stuck after 10–15 digits. So the fourth cage
is there for a fair solving path (and to keep the symmetry), not for uniqueness.

**Hints (light spoilers):** cells on opposite sides of the loop add up to 10. Use that to compare the 20 cage with the 10 cage.
Then look at row 5, and remember the knight.

Logical solvability: verified with my candidate-elimination solver (no guessing). It has **not** been test-solved by a human.
