# Setter's note — Bowstring

An archer's bow, drawn and ready: the bow is a **double arrow**, the string is a **between line** through the same two
circles, and an **arrow** is nocked on the string, pointing at the clue on the far side of the grid. Double arrows are
new to the gallery. Nine X-sums sit around the edge.

**Why it works.** The bow and the string pull against each other, as a real bow does. The string's five inner cells all
lie between the tips and sit in one column, so the tips must be at least six apart. The bow's inner cells hold three
different digits in column 2 and two in column 3, so they add up to at least 9. The tips must match that total, so only
a few tip pairs survive. The arrow then has to be long enough for its circle on the string.

**How it was set.** I drew the bow, string and arrow first and checked with CP-SAT that they fit together (an earlier
drawing with the bow spanning all nine rows was impossible: a full-height string needs tips 1 and 9, and the bow's
inner cells can't add up to only 10). The X-sums were then chosen one at a time with no target grid, by how much each
one taught my solver (`open_outside.py`, X-sums only). Skyscraper and mixed versions needed as many clues and two clue
types, so I kept the plain one. The bow, the string, the arrow and eight of the X-sums are all needed for uniqueness.
The ninth, the 12 the arrow points at, is needed for the logic only. I like that the target is the clue that finishes
the job.

**Where to start (light spoiler):** work out which pairs of digits the bow's tips can be. Then look at the 44: how many
digits can an X-sum of 44 add up?

Logical solvability: verified with my candidate-elimination solver (37 rounds of tier-2 logic, no guessing, no
contradiction tests) and independently with Rangsk's SudokuSolver, which needs only pointing, tuples and clue steps.
I rate it **3/5**. My round count says 4, but the steps are light. It has **not** been test-solved by a human.
