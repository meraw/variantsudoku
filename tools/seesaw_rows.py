"""Search layouts of one straight seesaw per row, all pivoting in one column, 180-degree symmetric (run 3).
python3 seesaw_rows.py seed iters [pivot_col=5] [time_limit=20]
Each row r gets a line with a left arm of a cells and a right arm of b cells around the pivot; row 10-r gets the
mirror image. Simulated annealing on the CP-SAT solution count (limit 40). Prints the best layout and writes
seesaw_rows_<seed>.json (no givens; finish with givens_logic.py)."""
import sys, json, random, math, itertools
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *


def feasible(a, b):
    """some all-different fill of a straight line with arms a (left) and b (right) balances"""
    w = list(range(-a, 0)) + [0] + list(range(1, b + 1))
    return any(sum(x * y for x, y in zip(w, p)) == 0 for p in itertools.permutations(range(1, 10), a + b + 1))


def line(r, pc, a, b):
    cells = [(r, pc - a + i) for i in range(a + b + 1)]
    return {"type": "seesaw", "cells": [name(x) for x in cells], "pivot": name((r, pc))}


def main():
    seed, iters = int(sys.argv[1]), int(sys.argv[2])
    pc = int(sys.argv[3]) - 1 if len(sys.argv) > 3 else 4
    tl = float(sys.argv[4]) if len(sys.argv) > 4 else 20
    rnd = random.Random(seed)
    arms = [(a, b) for a in range(1, pc + 1) for b in range(1, 9 - pc) if feasible(a, b)]
    mids = [(a, b) for a, b in arms if a == b and pc == 4]

    def cons(st):  # st: arms for rows 1-4 and the middle row
        out = [line(r, pc, *st[r]) for r in range(4)] + [line(4, pc, *st[4])]
        out += [line(8 - r, 8 - pc, st[r][1], st[r][0]) for r in range(4)]
        return out

    def score(st):
        sols, status = Puzzle({"constraints": cons(st)}).count_solutions(limit=40, time_limit=tl)
        if not sols:
            return None
        return math.log(len(sols)) * 10 + (8 if status != 'OPTIMAL' else 0), len(sols), status
    while True:
        st = [rnd.choice(arms) for _ in range(4)] + [rnd.choice(mids)]
        s = score(st)
        if s:
            break
    best, T, seen = (s, st), 5.0, {}
    for it in range(iters):
        q = list(st); r = rnd.randrange(5)
        q[r] = rnd.choice(mids) if r == 4 else rnd.choice(arms)
        if tuple(q) not in seen:
            seen[tuple(q)] = score(q)
        s2 = seen[tuple(q)]
        if s2 is None:
            continue
        if s2[0] <= s[0] or rnd.random() < math.exp((s[0] - s2[0]) / T):
            st, s = q, s2
            if s[0] < best[0][0]:
                best = (s, list(st)); print(it, best, flush=True)
        T = max(0.5, T * 0.99)
    json.dump({"title": "", "givens": {}, "constraints": cons(best[1])}, open(f'seesaw_rows_{seed}.json', 'w'), indent=1)
    print('final', best)


main()
