"""Run 8: every pair of givens that makes a puzzle unique, tested with the logical solver.
python3 pair_givens.py spec.json [max_tests]
Enumerates the puzzle's solutions (up to 5000), finds every pair of (cell, digit) givens that exactly one solution
matches (numpy), and runs the tier-2 logical solver on up to max_tests of them (random order). Prints the solvable pairs,
most tier-2 rounds first."""
import sys, json, copy, random, time
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *

f = sys.argv[1]; maxtest = int(sys.argv[2]) if len(sys.argv) > 2 else 300
s = json.load(open(f)); s.setdefault('givens', {})
sols, st = Puzzle(s).count_solutions(limit=5000, time_limit=300)
print('solutions', len(sols), st, flush=True)
cells = [(r, k) for r in range(9) for k in range(9)]
S = np.array([[g[a] for a in cells] for g in sols])
uniq = set()
for i in range(81):
    eqi = S[:, i][:, None] == S[:, i][None, :]
    for j in range(i + 1, 81):
        cnt = (eqi & (S[:, j][:, None] == S[:, j][None, :])).sum(1)
        for t in np.nonzero(cnt == 1)[0]:
            uniq.add((i, S[t, i], j, S[t, j]))
uniq = sorted(uniq); print('unique pairs', len(uniq), flush=True)
random.seed(1); random.shuffle(uniq)
res = []; t0 = time.time()
for (i, vi, j, vj) in uniq[:maxtest]:
    s2 = copy.deepcopy(s); s2['givens'].update({name(cells[i]): int(vi), name(cells[j]): int(vj)})
    L = Logic(Puzzle(s2)); r, _ = L.solve(max_tier=2)
    if r == 'solved':
        res.append((L.tier_counts[2], name(cells[i]), int(vi), name(cells[j]), int(vj)))
print('tested', min(maxtest, len(uniq)), 'solvable', len(res), 'time', round(time.time() - t0))
for x in sorted(res, reverse=True):
    print(x)
