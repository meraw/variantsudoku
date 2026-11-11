# Setter's note — Newton's Cradle

A new line rule, drawn as the desk toy. Five pendulums hang from row 1, and the left ball is lifted and ready to swing (the diagonal line).
A second, irregular bar of pendulums hangs from row 6. The rule is a damped pendulum: the digits swing from one side of the
resting digit to the other, and each swing is smaller than the last. As far as I know the rule is new.

**Facts worth finding:**
- A pendulum's digits are always all different, so it works like a little cage.
- Pendulums are short. With 4 cells the circle must be 3–7, and a 6-cell pendulum can't exist at all.
- A 4-cell pendulum with circle 7 must end 9, 6. With circle 3 it must end 1, 4.
- The rule is symmetric under swapping every digit d for 10 − d, so the puzzle needs a given to choose between twin solutions. One given
  (r2c4) does that. The other given (r4c8) is not needed for uniqueness, but makes it solvable without guessing.

**How it was set.** I drew the cradle first. Five *hanging* (straight) 4-cell pendulums side by side are impossible, so the lifted
ball is part of the design, not decoration. Letting the computer grow pendulums in the lower half gave scattered pictures, so I tried
a second bar of pendulums hanging from row 6 instead. I sampled bars, kept those with few solutions, then tested every pair of givens
that makes the solution unique. 18 of 2,418 pairs are solvable without guessing, and I took the one with the longest solve whose givens
are not in circles.

**Hints (light spoilers):**
- Row 1 has five circles of 4-cell pendulums. Which five digits must they be?
- Look at the 6 in row 4, and ask what a circle 7 would need at the bottom of its line.

Logical solvability: verified with my candidate-elimination solver (40 rounds of tier-2 logic, no guessing, no contradiction tests).
Independently, Rangsk's SudokuSolver (given each pendulum as an automaton) finds the same unique solution and solves it logically with
almost nothing beyond singles. I rate it **3/5**: steady rather than crunchy. It has **not** been test-solved by a human.
