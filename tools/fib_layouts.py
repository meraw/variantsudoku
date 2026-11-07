"""Run 4: search 180-degree symmetric layouts of Fibonacci lines (orthogonal steps, lengths 3/5/8) on CP-SAT solution count.
python3 fib_layouts.py seed pairs iters ortho
Fibonacci lines are invariant under multiplying every digit by 3, 7 or 9 (last digit kept), so the minimum count is 4.
Writes fb_<seed>_<pairs>.json (no givens; finish with sym_givens.py or givens_logic.py)."""
import sys, json, random, math
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *

NB = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
def rot(rc): return (8-rc[0], 8-rc[1])

def walk(rnd, L, used, ortho_only=False):
    nb = [d for d in NB if not ortho_only or 0 in d]
    for _ in range(200):
        s = (rnd.randrange(9), rnd.randrange(9))
        if s in used or rot(s) in used or rot(s) == s: continue
        p = [s]
        while len(p) < L:
            opts = []
            for dr, dc in nb:
                q = (p[-1][0]+dr, p[-1][1]+dc)
                if 0 <= q[0] < 9 and 0 <= q[1] < 9 and q not in p and q not in used and rot(q) not in used and rot(q) not in p and q != rot(q):
                    # no diagonal crossing of itself: skip complexity
                    opts.append(q)
            if not opts: break
            p.append(rnd.choice(opts))
        if len(p) == L: return p
    return None

def spec_of(lines, givens=None):
    cons = []
    for p in lines:
        cons.append({"type": "fibonacci", "cells": [name(x) for x in p]})
        cons.append({"type": "fibonacci", "cells": [name(rot(x)) for x in p]})
    return {"givens": givens or {}, "constraints": cons}


LENS = [3, 5, 8]
def evaluate(lines, tl=10):
    sols, st = Puzzle(spec_of(lines)).count_solutions(limit=40, time_limit=tl)
    if not sols: return None
    return math.log(len(sols)) + (2 if st != 'OPTIMAL' else 0) + 0.02 * sum(len(p) for p in lines), len(sols), st

def mutate(rnd, lines, ortho):
    new = [list(p) for p in lines]
    i = rnd.randrange(len(new))
    if rnd.random() < 0.15:
        new[i] = new[i][::-1]; return new
    used = set(x for j, p in enumerate(new) if j != i for x in p)
    q = walk(rnd, rnd.choice(LENS), used, ortho)
    if q is None: return None
    new[i] = q
    return new

if __name__ == '__main__':
    seed, K, iters = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    ortho = len(sys.argv) > 4 and sys.argv[4] == 'ortho'
    rnd = random.Random(seed)
    while True:
        lines, used = [], set()
        for _ in range(K):
            p = walk(rnd, rnd.choice(LENS), used, ortho)
            if p is None: break
            lines.append(p); used |= set(p)
        if len(lines) == K:
            s = evaluate(lines)
            if s: break
    cur, cs = lines, s; best = (cs, cur); T = 1.0
    for it in range(iters):
        new = mutate(rnd, cur, ortho)
        if new is None: continue
        s = evaluate(new)
        if s is None: continue
        if s[0] <= cs[0] or rnd.random() < math.exp((cs[0] - s[0]) / T):
            cur, cs = new, s
            if cs[0] < best[0][0]:
                best = (cs, cur); print(it, cs, flush=True)
                json.dump(spec_of(best[1]), open(f'fb_{seed}_{K}.json', 'w'))
        T = max(0.1, T * 0.99)
    print('final', best[0])
