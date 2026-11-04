# Setter's note — Pinwheel Whispers

This one uses familiar rules and is the "control" for the experimental puzzle set in the same run. The four L-shaped whispers turn
around the grid like a pinwheel (they have 90° rotational symmetry). Each one sits entirely inside a corner box, so
its five cells alternate high/low and must avoid 5. Note that a 4 or a 6 can only be an endpoint. The small diamond in box 5 sets
the centre's high/low rhythm.

**How it was set.** I drew the whispers first, then fixed a target grid and grew the cages in **180°-symmetric
pairs**. At each step I kept the pair that gave my logical solver the most progress. Afterwards I removed every pair
that wasn't needed, which leaves 12 cages and no givens. The cage *shapes* are symmetric, but the totals aren't.

**Hints (light spoilers):** the 16 cage at the bottom right can only be one pair of digits, and it sits on a whisper
endpoint. Box 9 unravels from there. After that, the long 28 cage and its box-9 neighbours carry you into the bottom middle.

Logical solvability: verified with my candidate-elimination solver (no guessing). It has not been test-solved by a human.
