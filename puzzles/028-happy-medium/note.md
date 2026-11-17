# Setter's note — Happy Medium

A smiley face drawn in German whispers, the rule Elena liked in Pinwheel Whispers, with five **median** clues around it.
Median clues are new to the gallery: each one is the middle value of the first three digits it looks at. I found them in
clover's Median Sudoku (Genuinely Approachable Sudoku series, GM Puzzles). No givens, five clues.

**The idea.** On their own, median clues are gentle: one clue removes no candidate from any single cell. A puzzle of
median clues alone needed 9–11 givens. So the clues needed a partner that does a lot of work, and whispers do: the face
outline is a 24-cell loop that must alternate between high (6–9) and low (1–4) digits all the way round, and no whisper
cell can be a 5. That also explains the title. My first face had the smile one row higher, and it was impossible inside the
loop. Lowered by one row it fits. Then a script chose median clues one at a time, with no target grid, by how much each one
taught my solver. Its runs needed 4–11 clues, some with a given or two. This run needed only five clues and no givens, and
**every clue and every line is needed**.

**Where to start (light spoiler):** below column 3. Which of those three cells can hold the 5?

Logical solvability: verified with my candidate-elimination solver (23 rounds of tier-2 logic, no guessing, no contradiction
tests). Rangsk's SudokuSolver finds the same unique solution with direct cell forcings, tuples, pointing and one AIC (a short
alternating chain), so expect one spot that needs a little chain. I rate it **3/5**. The hardest part is the loop in the
middle of the solve. It has **not** been test-solved by a human.
