"""Run 8: grow straight arrows around a kept core in rotation orbits (4-fold by default, --pairs for 180-degree pairs).
python3 orbit_grow.py base.json out.json seed [--pairs] [--maxshaft N] [--givens]
Every straight arrow (circle + 1..N shaft cells in one of 8 directions, no shared cells with other lines) is grouped with
its rotations. Each step tries the orbits that CP-SAT finds feasible together with the puzzle so far, scores them by the
candidates my logical solver removes (minus a small cost per cell), and adds one of the best three. A given is a fallback
when nothing removes at least 10 candidates. Stops when the tier-2 solve finishes, then prunes whole orbits and givens."""
import sys, json, random, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from open_clues import samples, feasible, unique, logic_ok
from open_lines import segs_of, crosses

argv = [a for i, a in enumerate(sys.argv) if not a.startswith('--') and sys.argv[i - 1] != '--maxshaft']
base, out, seed = argv[1], argv[2], int(argv[3])
PAIRS = '--pairs' in sys.argv
MAXS = int(sys.argv[sys.argv.index('--maxshaft') + 1]) if '--maxshaft' in sys.argv else 4
GIVENS = '--givens' in sys.argv
rnd = random.Random(seed)
spec = json.load(open(base))
for c in spec['constraints']:
    c['keep'] = True
DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]


def rot90(a):
    return (a[1], 8 - a[0])


def rots(p):
    k = 2 if PAIRS else 1
    out, q = [p], p
    for _ in range(4 // k - 1):
        for _ in range(k):
            q = [rot90(a) for a in q]
        out.append(q)
    return out


def cells_of(c):
    return [parse(x) for x in c.get('circle', []) + c.get('cells', [])]


def orbits(used, diag):
    seen, res = set(), []
    for r in range(9):
        for k in range(9):
            for dr, dc in DIRS:
                for n in range(1, MAXS + 1):
                    p = [(r + dr * i, k + dc * i) for i in range(n + 1)]
                    if not all(0 <= a[0] < 9 and 0 <= a[1] < 9 for a in p):
                        break
                    grp = rots(p)
                    allc = [a for q in grp for a in q]
                    if len(set(allc)) != len(allc) or set(allc) & used:
                        continue
                    dg = [d for q in grp for d in segs_of(q)]
                    if any(crosses(x, y) for x in dg for y in diag + dg if x != y):
                        continue
                    key = frozenset(tuple(q) for q in grp)
                    if key in seen:
                        continue
                    seen.add(key); res.append(grp)
    return res


def con(p):
    return {"type": "arrow", "circle": [name(p[0])], "cells": [name(a) for a in p[1:]]}


while True:
    pz = Puzzle(spec); L = Logic(pz); cand = L.init_cands(); L.propagate(cand, 2)
    left = sum(len(x) for x in cand.values()); print('arrows', len(spec['constraints']), 'left', left, flush=True)
    if left == 81:
        break
    used = {a for c in spec['constraints'] for a in cells_of(c)}
    diag = [d for c in spec['constraints'] for d in segs_of(cells_of(c))]
    sm = samples(spec, 40, rnd)
    sc = []
    for grp in orbits(used, diag):
        # cheap filter: each arrow of the orbit must hold in some sample (CP-SAT confirms the whole orbit later)
        if not all(any(g[q[0]] == sum(g[a] for a in q[1:]) for g in sm) for q in grp):
            continue
        sp2 = copy.deepcopy(spec); sp2['constraints'] += [con(q) for q in grp]
        c2 = {a: set(x) for a, x in cand.items()}
        try:
            Logic(Puzzle(sp2)).propagate(c2, 2)
        except Contradiction:
            continue
        g = left - sum(len(x) for x in c2.values())
        sc.append((g - 1.5 * sum(len(q) for q in grp), rnd.random(), sp2, grp))
    sc.sort(key=lambda x: (-x[0], x[1]))
    if GIVENS and (not sc or sc[0][0] < 10):
        for a_ in L.cells:
            if len(cand[a_]) < 2:
                continue
            for val in {g[a_] for g in sm}:
                c2 = {b: set(x) for b, x in cand.items()}; c2[a_] = {val}
                try:
                    Logic(pz).propagate(c2, 2)
                except Contradiction:
                    continue
                sp2 = copy.deepcopy(spec); sp2.setdefault('givens', {})[name(a_)] = val
                sc.append(((left - sum(len(x) for x in c2.values())) - 40, rnd.random(), sp2, [[a_]]))
        sc.sort(key=lambda x: (-x[0], x[1]))
    top = sc[:3]; rnd.shuffle(top)
    for s_, _, sp2, grp in top + sc[3:60]:
        if feasible(sp2):
            spec = sp2; print('  add', round(s_, 1), [[name(a) for a in q] for q in grp], flush=True); break
    else:
        print('no feasible move'); sys.exit()
assert unique(spec)
# prune whole orbits (consecutive blocks of non-kept arrows were added together)
k = 2 if PAIRS else 4
cons = spec['constraints']
blocks, i = [], 0
while i < len(cons):
    if cons[i].get('keep'):
        i += 1; continue
    blocks.append(list(range(i, i + k))); i += k
for b in reversed(blocks):
    sp2 = copy.deepcopy(spec)
    sp2['constraints'] = [c for j, c in enumerate(spec['constraints']) if j not in b]
    ok, r2 = logic_ok(sp2)
    if ok and unique(sp2):
        print('  drop orbit', [spec['constraints'][j]['circle'] for j in b], flush=True); spec = sp2
for g_ in list(spec.get('givens', {})):
    sp2 = copy.deepcopy(spec); del sp2['givens'][g_]
    ok, r2 = logic_ok(sp2)
    if ok and unique(sp2):
        print('  drop given', g_, flush=True); spec = sp2
ok, r2 = logic_ok(spec)
print('givens', spec.get('givens'))
print('FINAL arrows', len(spec['constraints']), 'tier2', r2, ok)
for c in spec['constraints']:
    c.pop('keep', None)
json.dump(spec, open(out, 'w'), indent=1)
