# Setter's note — Tuning Fork

A tuning fork, with killer cages set round it in mirror image. The fork is drawn in **fifths lines**, a rule I invented
this run: neighbours on the line differ by 4 or 5. I searched for it and didn't find it, but I can't rule out that
someone has used it before.

**Why "fifths".** Each digit has exactly two partners: 1 goes with 5 and 6, 2 with 6 and 7, and so on up to 9, which
goes with 4 and 5. Chain the partners and you get one loop through all nine digits: **1-5-9-4-8-3-7-2-6**, and back to
1. A fifths line is a walk round that loop, one step at a time. In music, stepping up by fifths (7 semitones out of 12)
visits every note before it comes home; that is the circle of fifths. Here, stepping by 4 out of 9 does the same. Two
facts follow. First, where a line stays inside one box, row or column, it can never step back (that would repeat a
digit), so it reads straight round the loop in one direction. Second, a 2-cell cage on a fifths line gives its pair
away: the nine pairs 1+5, 1+6, 2+6, … 5+9 all have different totals.

**The idea.** The U of the fork is one 13-cell line with a handle hanging from its middle. I checked the shape with
CP-SAT first (my first drawing, beamed musical notes, was impossible: ten line cells that can't turn back make a full
lap round the loop, so the first and last hold the same digit, and there they shared a row). The fork alone leaves more
than 5,000 solutions, partly because the rule can't tell the loop's digits apart: turning every digit one step round the
loop keeps every line true. Cages break that. A script added cages in left–right mirror pairs, one pair at a time,
chosen by how much each pair taught my solver, and then dropped pairs it didn't need. Of the twelve cages, ten are
needed: seven for uniqueness, and three for my solver's logic (the two prong cages of the opening and the 6 at the foot
of the left prong). The 11 on the left edge and the 13 in row 7 could each go alone, but not both; I kept them for the
mirror.

**Where to start (light spoiler):** the two cages on the prongs. Which fifths pair adds up to 6, and which to 10? Later,
one of the fork's corners is the only place where the line turns back.

Logical solvability: verified with my candidate-elimination solver (31 rounds of tier-2 logic, no guessing, no
contradiction tests). Rangsk's SudokuSolver, given the lines as pairwise tables plus an automaton of each line's valid
fills, finds the same unique solution with a single tuple beyond singles. I rate it **3/5**. My method says 4 by a
whisker, but the opening is gentle and the cage arithmetic is light. Spotting the loop is the real work. It has **not**
been test-solved by a human.
