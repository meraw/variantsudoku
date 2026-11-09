# Setter's note — Skyline Sums

Two established clue types that both care about the *first* digit you meet from the edge. An X-sum tells you how far
to count from that digit, and a skyscraper clue tells you how often the view gets taller. Neither rule had been used in
the gallery yet. Skyscrapers in particular were new to my toolkit, which now handles both with an exact pass along the
whole row or column.

**How it was set.** As in Betwixt (009), there was no target grid. A script sampled grids that fit the clues so far, listed
the totals still possible at each outside position, and scored every candidate clue by how much my logical solver could
then deduce. Clues went in as 180° pairs. Left alone, the scoring picked X-sums almost every time, because they simply say
more per clue: all four unbiased runs that finished gave X-sum puzzles with at most one skyscraper. So skyscraper moves had
their score multiplied by 2.2, and this run came out balanced, with seven of each. Then I pruned by hand:
- Row 5's left clue was "X-sum 45", which only says r5c1 = 9. It was a given in disguise, and the puzzle didn't need it.
- The skyscraper 3 above column 2 also turned out to be removable.

That leaves 12 clues (7 skyscrapers, 5 X-sums). Eleven are needed for uniqueness. The twelfth (column 5's 32 from below)
is needed for a solve without trial and error. The picture is no longer perfectly symmetric.

**Hints (light spoilers):**
- Column 5 has an X-sum at *both* ends, and 37 + 32 is far more than 45. The two counted stretches must overlap,
  and the overlapping cells are counted twice. How big must that overlap be, and how long can each stretch be?
- Column 4's 8 is tiny: the first digit can only be 2 or 3.
- Seven visible buildings (row 5 from the right, column 6 from below) means the line climbs almost every step. Where can
  the 9 be, and what does that do to the cells just before it?

Logical solvability: verified with two independent solvers. My candidate-elimination solver needs no guessing and no
contradiction tests (35 rounds of tier-2 logic). Rangsk's SudokuSolver, fed only the exported puzzle, also solves it.
It uses nothing beyond X-sum and skyscraper re-evaluations, tuples and pointing. It has **not** been test-solved by a human.
