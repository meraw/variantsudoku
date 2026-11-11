"""Run 8 (015 Newton's Cradle): the hand-drawn cradle (five 4-cell pendulums from row 1, columns 4-8, the left one lifted
diagonally to r4c1) plus a random second bar of vertical pendulums hanging from row 5 or 6 (random columns, lengths 3-5).
python3 pend_bars.py seed iterations   -> prints solution count (up to 100) and tier-2 fixpoint size per bar, and saves
bars with <= 40 solutions as bar_<seed>_<i>.json for pair_givens.py."""
import sys, json, random
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *


def hang(r, c, L):
    return [(r + i, c) for i in range(L)]


cradle = [[(i, 3 - i) for i in range(4)]] + [hang(0, c, 4) for c in range(4, 8)]
used0 = {a for l in cradle for a in l}
seed = int(sys.argv[1]); rnd = random.Random(seed)
for it in range(int(sys.argv[2])):
    row = rnd.choice([4, 5])
    lines, used = list(cradle), set(used0)
    for c in range(9):
        L = rnd.choice([0, 0, 3, 4] if row == 5 else [0, 0, 3, 4, 5])
        if L == 0:
            continue
        l = hang(row, c, L)
        if any(a in used for a in l) or l[-1][0] > 8:
            continue
        lines.append(l); used |= set(l)
    if len(lines) < 9:
        continue
    sp = {"constraints": [{"type": "pendulum", "cells": [name(a) for a in l]} for l in lines]}
    sols, st = Puzzle(sp).count_solutions(limit=100, time_limit=20)
    if not sols:
        continue
    L_ = Logic(Puzzle(sp)); cand = L_.init_cands(); L_.propagate(cand, 2)
    print(len(sols) if st == 'OPTIMAL' else '100+', sum(len(x) for x in cand.values()),
          f"row{row + 1} " + ' '.join(f"c{l[0][1] + 1}:{len(l)}" for l in lines[5:]), flush=True)
    if st == 'OPTIMAL' and len(sols) <= 40:
        json.dump(sp, open(f'bar_{seed}_{it}.json', 'w'))
