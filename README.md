# variantsudoku

Variant sudoku puzzles from an experimental setter, published at the GitHub Pages gallery (`index.html`).

- `puzzles/NNN-slug/` — one folder per finished puzzle: `rules.md`, `note.md`, `puzzle.json` (spec + solution + links),
  `grid.svg`, `solution.svg`, `play.md`, `verification.md` (uniqueness proof, logic check, difficulty).
- `SETTER_LOG.md` — every attempt, including abandoned ones.
- `FEEDBACK.md` — notes from the owner.
- `tools/` — the setter's toolkit (CP-SAT uniqueness, logical solver, rendering, export). See `tools/README.md`.
