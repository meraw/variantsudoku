# Setter's note — Room with a View

You are inside, looking out. The four shaded windows are **windoku** regions, and the numbers around the grid count the
**skyscrapers** you can see from each side. Windoku is new to the gallery. It's an old variant (four extra 3×3 regions)
that is usually set with lots of given digits. Here there are none: ten skyscraper clues do all the work.

**Why windoku.** The windows add four houses but no clue of their own. On an empty grid they deduce nothing, and they
make no picture without a partner. With the skyscrapers, though, every "this digit must be in that row" also has to fit
a window. Windoku also hides five more regions that are not drawn. Columns 2–4 hold every digit three times, and their two
windows hold it twice, so the nine cells of columns 2–4 in rows 1, 5 and 9 hold 1–9 once each. The same goes for
columns 6–8, for columns 1, 5 and 9 in rows 2–4 and in rows 6–8, and for the nine cells where rows 1, 5 and 9 meet
columns 1, 5 and 9. My solver doesn't use these hidden regions, but you may find a shortcut there.

**How it was set.** The windows came first. Then a script (`tools/open_outside.py`) chose the clues one at a time with
no target grid. Each step sampled grids that fit the clues so far, tried every clue those grids allowed, and kept one of
the clues that taught my solver the most. Nine seeds gave versions with 9–16 clues, most of them with one or two given
digits. This seed is the only 10-clue version with no givens. Eight clues are needed for uniqueness. The 3 above
column 7 and the 2 right of row 4 are needed for the logic only.

**Where to start (light spoiler):** three columns show 7 buildings from one end. A 7 forces the column to climb
almost all the way. Column 7 shows 7 from below and 3 from above: where can its 9 stand?

Logical solvability: verified with my candidate-elimination solver (49 rounds of tier-2 logic, no guessing, no
contradiction tests) and independently with Rangsk's SudokuSolver, which needs skyscraper steps, pointing and one tuple.
I rate it **4/5**. It has **not** been test-solved by a human.
