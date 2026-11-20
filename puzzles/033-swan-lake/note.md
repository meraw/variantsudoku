# Setter's note — Swan Lake

A swan on a lake, drawn with a new invented rule: **graceful lines**. Along a line, every step between neighbouring
digits must be a different size. The name comes from graph theory. A *graceful labelling* numbers the points of a
graph so that every edge gets a different difference. Musicians know a close cousin, the all-interval twelve-tone row.

**Why it works.** The rule looks loose: almost any three digits pass. It tightens quickly with length. Only about 0.7% of
orders of 8 different digits are graceful. A whole row has to use every difference from 1 to 8 exactly once, and only
120 orders of 1–9 do that. So the lake is the strict part of the picture. The only way to make a difference of 8
is 1 next to 9, so **the lake's 1 and 9 are neighbours**. The 7 is then 1–8 or 2–9, hanging off that pair. And the
differences add up to 36, which is even, so the lake's two ends have the same parity.

The swan's lines are freer. They cross box borders on diagonal steps, so a digit may repeat there (a difference of 0).
The solution uses that once, on the wing.

**Why sandwiches.** Swapping every digit d for 10 − d keeps every difference, so graceful lines alone can never have
a unique solution. Something has to tell high from low. Sandwich sums do, and they fit the theme: they are about where
the 1 and the 9 sit, and so is the lake. My first partner was kropki dots. They needed 16–22 dots scattered over the
picture, so I dropped them.

**How it was set.** I drew the swan and the lake first. Then a script (`tools/open_outside.py`) chose sandwich clues one
at a time with no target grid, by how much each one taught my solver. Over 15 runs, this one needed the fewest: seven
clues and no givens. Every element is needed: remove any line or any clue and there are several solutions. (I left the
row-9 sandwich out of the choice. The rules already say it is 0.)

**Where to start (light spoiler):** four clues are 31, 32 or 33. Five digits from 2–8 add up to at most 30, so each of
those sandwiches holds six digits and leaves out exactly one digit of 2–8. Later the lake has to become one of its 120
orders. Look for the 1–9 pair.

Logical solvability: verified with my candidate-elimination solver (29 rounds of tier-2 logic, no guessing, no
contradiction tests) and independently with Rangsk's SudokuSolver. Rangsk gets the graceful lines as automata, and its
logged path is singles plus two tuples. I rate it **4/5**: my round count says 3, but the lake step is a real search and
the rule is new. It has **not** been test-solved by a human.
