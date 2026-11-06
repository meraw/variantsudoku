# Setter's toolkit

Python 3 + OR-Tools (`pip install ortools`); `cairosvg` is optional and only used for PNG previews.
Link export calls `node` with the `lz-string` package. Install it with `npm install lz-string` in `/tmp/lz`, or change the
path in `vs.links`.

| file | purpose |
|---|---|
| `vs.py` | Puzzle spec (JSON), CP-SAT model and solution counting, a tiered logical solver (`Logic`), an SVG renderer and f-puzzles/SudokuPad export |
| `check.py spec.json [--logic] [--sample N]` | Counts solutions (up to N), shows which cells are fixed, and optionally runs the logical solver |
| `givens.py` | Greedy givens for uniqueness only (ignores logic) |
| `givens_logic.py spec out seed` | Greedy givens chosen for logical progress, then pruned |
| `grow_cages.py base out seed [killer\|kropki\|xv] [--sym]` | Solution-first clue growth guided by the logical solver, with optional 180° symmetric pairs |
| `seesaw_rows.py seed iters [pivot_col] [time_limit]` | Run 3: anneals one-seesaw-per-row layouts with a shared pivot column (180° symmetric) on CP-SAT solution count |
| `one_given.py base.json seed n lo hi` | Run 3: symmetric negative-XV designs over a symmetric base. Finds the designs whose only ambiguity is the 180° twin and lists every single given that the logical solver can finish from |
| `package.py spec puzzles/<slug> <diff> "<why>"` | Refuses to package unless CP-SAT proves a unique solution. Writes puzzle.json, grid.svg, solution.svg and verification.md |

Supported constraints: givens, thermo, German whisper, keypad line (invented), knight line (invented, run 2), seesaw (invented, run 3:
`{"type": "seesaw", "cells": [...], "pivot": "r5c5"}`, digit × distance from the pivot balances on both sides), parity line,
entropic line, modular line, region-sum line, renban, killer cage, arrow, white/black kropki, XV, negative kropki/XV,
anti-knight, anti-king, diagonals. Neighbour-relation lines accept `"loop": true` for closed loops.

Logical solver tiers: (1) singles + pairwise constraint consistency; (2) locked candidates, pairs/triples,
generalised pointing, parity counting, seesaw min/max bounds, whole-constraint enumeration; (3) single-candidate contradiction tests.
Since run 3, whole-constraint enumeration runs on one group per round, the one with the smallest candidate space first.
This is closer to how a human picks the easiest cage or line, but tier-2 round counts are higher than in runs 1-2. `package.py` lists the
re-solved counts of all earlier puzzles in every new verification report as a calibration table.
