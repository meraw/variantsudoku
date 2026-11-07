"""Run 4. python3 consec_designs.py base.json maxdots seed_from seed_to [--sym] [--min N]
Renban + negative white kropki designs: sample a grid satisfying the renbans with few consecutive neighbours,
derive the dots, count solutions, and test single givens for logic."""
import sys, json, random, time
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from ortools.sat.python import cp_model

def sample_grid(base, maxdots, seed, tl=30):
    pz = Puzzle(base)
    m, v = pz.build_model()
    rnd = random.Random(seed)
    bools = []
    bmap = {}
    for r in range(9):
        for c in range(9):
            for b in [(r, c + 1), (r + 1, c)]:
                if b[0] > 8 or b[1] > 8: continue
                d = m.NewIntVar(-8, 8, ''); m.Add(d == v[(r, c)] - v[b])
                ad = m.NewIntVar(0, 8, ''); m.AddAbsEquality(ad, d)
                x = m.NewBoolVar(''); m.Add(ad == 1).OnlyEnforceIf(x); m.Add(ad != 1).OnlyEnforceIf(x.Not())
                bools.append(x); bmap[frozenset([(r, c), b])] = x
    m.Add(sum(bools) <= maxdots)
    if SYM:
        for k, x in bmap.items():
            a, b = tuple(k)
            m.Add(x == bmap[frozenset([(8 - a[0], 8 - a[1]), (8 - b[0], 8 - b[1])])])
    if MINDOTS:
        m.Add(sum(bools) >= MINDOTS)
    # random objective for diversity
    obj = []
    for a in v:
        for d in DIGITS:
            if rnd.random() < 0.15:
                y = m.NewBoolVar(''); m.Add(v[a] == d).OnlyEnforceIf(y); m.Add(v[a] != d).OnlyEnforceIf(y.Not()); obj.append(y)
    m.Maximize(sum(obj))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = tl; s.parameters.random_seed = seed; s.parameters.num_workers = 1
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
    return {a: s.Value(v[a]) for a in v}

def design(base, g):
    spec = json.loads(json.dumps(base))
    spec['global'] = ['neg_kropki_w']
    for r in range(9):
        for c in range(9):
            for b in [(r, c + 1), (r + 1, c)]:
                if b[0] > 8 or b[1] > 8: continue
                if abs(g[(r, c)] - g[b]) == 1:
                    spec['constraints'].append({"type": "kropki_w", "cells": [name((r, c)), name(b)]})
    return spec

SYM = '--sym' in sys.argv
MINDOTS = 0
if __name__ == '__main__':
    if '--min' in sys.argv: MINDOTS = int(sys.argv[sys.argv.index('--min') + 1])
    base = json.load(open(sys.argv[1])); maxdots = int(sys.argv[2]); seeds = range(int(sys.argv[3]), int(sys.argv[4]))
    for seed in seeds:
        g = sample_grid(base, maxdots, seed)
        if g is None: print(seed, 'no grid'); continue
        spec = design(base, g)
        nd = sum(c['type'] == 'kropki_w' for c in spec['constraints'])
        sols, st = Puzzle(spec).count_solutions(limit=10, time_limit=60)
        line = f'{seed} dots={nd} sols={len(sols)} {st}'
        if len(sols) <= 4 and st == 'OPTIMAL':
            good = []
            for a in sorted(g):
                if g[a] == 5: continue
                s2 = json.loads(json.dumps(spec)); s2['givens'] = {name(a): g[a]}
                L = Logic(Puzzle(s2)); r, _ = L.solve(2)
                if r == 'solved': good.append((name(a), g[a], L.tier_counts[2]))
            line += f' one-given: {len(good)} ' + str(sorted(good, key=lambda x: -x[2])[:4])
            json.dump(spec, open(f'cs_{seed}.json', 'w'))
        print(line, flush=True)
