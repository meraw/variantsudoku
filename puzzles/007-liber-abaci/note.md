# Setter's note — Liber Abaci

A new invented line this time, named after Fibonacci's book of 1202. A **Fibonacci line** works like the famous sequence
1, 1, 2, 3, 5, 8, 13, …, except that only the last digit is kept, and the line may start from any two digits.
The first two digits on a line fix all the others.

**Things worth knowing about the rule** (these are deductions, not extra rules):
- *Parity.* The last digit of a sum has the same parity as the sum, so odd + odd = even, odd + even = odd and so on.
  Every line of three or more cells is therefore either **all even** or follows **odd, odd, even** repeating, starting at
  some point in that cycle. Combine this with "every row, column and box has exactly four even digits".
- *Length.* At most six cells of a line fit in one row, column or box (only eight sequences of six different digits work).
  The two long lines here are staircases that leave their boxes.
- *Fourth cells.* If a line starts a, b, then the third digit is a+b and the fourth is a+2b (last digits only).
- The line lengths in the grid are 3, 5 and 8. Those are Fibonacci numbers too.

**Why there are four givens.** Multiply every digit in a valid grid by 3 and keep the last digit: 1→3, 2→6, 3→9, 4→2,
5→5, 6→8, 7→1, 8→4, 9→7. Every Fibonacci line still works, because the rule only uses addition and last digits. The
same is true for ×7 and ×9. So Fibonacci lines on their own can never give a unique puzzle: every solution comes with three
relabelled copies, and a given 5 can't tell them apart (5 maps to itself). I searched line layouts with CP-SAT until
the lines alone left **exactly four** solutions, which is the minimum possible. In other words, the lines do all the
work except choosing the labels. Then I added givens. One given would be enough to make the solution unique, but
with a single given my logical solver gets stuck almost at once (I tested every single-given option on several layouts).
So the four givens are there for a fair path. They come in two 180°-symmetric pairs (9 and 1, 7 and 3), like the
lines. Take away any one and the puzzle stays unique, but the solver then needs trial-and-error.

**How it was set.** Layout first: five 180°-symmetric pairs of lines, orthogonal steps only, lengths 3, 5 or 8.
I annealed the layout on CP-SAT solution counts. Then I added symmetric pairs of givens one at a time, always the pair
that helped my logical solver most, and finally removed any pair it could do without. Every pair of lines matters.
Remove one and the puzzle either has more solutions or needs trial-and-error.

**Hints (light spoilers):** start with the staircase through the 9 in box 4 (it starts at r6c1). Parity first: the 9
is in fourth place, so the line can't be all even, and its 1st, 4th and 7th cells are odd. Next, the fourth digit
is a + 2b, so the first two digits must give a + 2b ending in 9. List those seed pairs and check each against the box
and row it runs through. The staircase in the other half of the grid works the same way with its 1.

**Spoiler (read after solving):** opposite cells of the finished grid always sum to 10. The rules don't force
this. It falls out of the symmetry: turning the grid round and multiplying by 9 gives the same grid back.

Logical solvability: verified with my candidate-elimination solver (no guessing, no contradiction tests). The most
work it needed on a single line was 25 seed pairs. It has **not** been test-solved by a human.
