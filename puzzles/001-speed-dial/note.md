# Setter's note — Speed Dial

This is the first puzzle in the collection and it tries out a new line type. On a keypad, digits that touch alternate between
odd and even (the corners and the 5 are odd, the edge digits are even). That means **every keypad line
alternates parity**, and parity is where the puzzle starts.

**How it was set.** I began with the zigzag across rows 1–2. It puts five cells of the same parity into row 1,
and a row only has four even digits, so those five cells have to be odd. That fixes the odd/even pattern of
the top two rows, and it also means the zigzag uses every digit 1–9 exactly once. In other words, it traces a
path through the keypad that visits all nine keys without lifting your finger. The spiral in box 5 works the same way: centre
and corners odd, edges even, and the whole box is another such path. I added the side zigzags, the two short
verticals and the row-7 line, and the solver showed the line layout alone left only 240 grids. Then I used a
logic-guided search to choose the givens.

**Why three givens?** The keypad can be rotated or mirrored, giving 8 symmetries in all, and none of them break the
adjacency rule. So any solution of the lines alone comes in a family of 8 relabelled grids. One given can never
separate all 8, which makes two givens the theoretical minimum. Two-given versions existed, but none could be solved
by my logical solver without guessing. Three givens keep it clean.

**Hints (light spoilers):** count the parities. Box 2 and column 5 soon tell you the parities on the row-7
line. After that, look at which keys a corner digit is allowed to touch.

Logical solvability: verified with my candidate-elimination solver (no guessing). It has **not** been test-solved
by a human yet, so I'd welcome feedback.
