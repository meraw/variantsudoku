# Setter's note — Mind the Gap

The gallery's first 1-5-9 puzzle, with German whispers (the rule from Pinwheel Whispers) and two thermometers. No givens.

**The idea.** A German whisper can never hold a 5, and every shaded column needs a 5 somewhere. I put short whispers on two of the three
bands of each shaded column and left a gap on a different band each time: the bottom of column 1, the top of column 5, the middle of
column 9. The 5s have to go in the gaps, and what a 5 means in a shaded column tells you something about the other two.

**One fact worth finding:** in each band, the three cells of a shaded column point at the 1s (or 5s, or 9s) of three rows of that band. Those sit in three
different boxes, so the three cells hold one digit from 1–3, one from 4–6 and one from 7–9. On a whisper the middle one can't be 5, so it is
a 4 or a 6. A 4 needs a 9 beside it and a 6 needs a 1, and a column has only one of each. So that middle digit always sits at an
end of its whisper.

**How it was set.** I found that fact the hard way. My first designs put long whispers down the shaded columns, and CP-SAT called every one
of them impossible. Free growth of whispers on the indexing grid either needed givens (two runs) or ran out of room for clean lines (three runs), and thermometers alone gave a trivial solve. The staircase of
gaps was the core that worked. A script then added straight whispers and thermometers where they taught my solver the most: four
lines, no givens. Of six runs I kept the one with the cleanest picture: eight upright whisper bars and two thermometers. Every line
is needed for the logical solve, and eight of the ten for uniqueness.

**Hint (light spoiler):** start with where the three 5s of the shaded columns go. A 5 in column 1 sends the row's 1 to column 5, and a 5 in
column 9 sends the row's 9 to column 5.

Logical solvability: verified with my candidate-elimination solver (11 rounds of tier-2 logic, no guessing, no contradiction tests).
Rangsk's SudokuSolver, reading the indexing rule natively, finds the same unique solution, but its path is much heavier (forcing chains
and five contradiction tests). Its whispers are pairwise only, so it can't use the "middle digit at the end" fact. I rate it **3/5**. If you
miss the band fact it may play like a 4. It has **not** been test-solved by a human.
