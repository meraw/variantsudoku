"""Run 14: solution-first growth of "snakes" (wiggly region-sum lines) and "ladders" (kropki dots stacked like rungs)
around a kept core. Open-solution sampling (snl_grow.py) found almost no ladders or snakes that fit, so this
version fixes a target grid first, as grow_cages.py does.

python3 snl_target.py base.json out.json seed [--snakelen 5,8] [--ladlen 2,4] [--tries 400] [--snakew 1.0]

1. T = a random solution of the base spec (CP-SAT with a random objective).
2. Repeat until my logical solver (tiers 1-2) finishes: draw `tries` random snakes and ladders that T satisfies,
   on cells no other snake/ladder uses (snakes may not cross diagonals of other snakes), score each by the
   candidates left after a full tier-2 solve plus a size penalty (4 per cell, as in grow_cages.py), add the best.
3. Drop unneeded elements (newest first), then trim ladder end rungs (a ladder keeps at least 2 rungs).
Uniqueness is confirmed with CP-SAT at the end (the logical solve already implies it)."""
import sys, json, random, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from ortools.sat.python import cp_model
from open_lines import segs_of, crosses

argv = [a for i, a in enumerate(sys.argv) if not a.startswith('--') and sys.argv[i - 1] not in ('--snakelen', '--ladlen', '--tries', '--snakew')]
base, out, seed = argv[1], argv[2], int(argv[3])
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
SN = tuple(map(int, opt('--snakelen', '5,8').split(',')))
LD = tuple(map(int, opt('--ladlen', '2,4').split(',')))
TRIES = int(opt('--tries', 400))
SNAKEW = float(opt('--snakew', 1.0))  # multiplies the per-cell penalty of snakes (higher = fewer snake cells)
rnd = random.Random(seed)
spec = json.load(open(base))
pending = spec.pop('ladders', [])  # core ladders: rung positions; T is drawn with "a dot of either colour" there
for c in spec['constraints']:
    c['keep'] = True
H8 = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

pz0 = Puzzle(dict(spec, constraints=spec['constraints'] + [{"type": "kropki_any", "cells": list(ab)} for ld in pending for ab in ld]))
m, v = pz0.build_model()
m.Minimize(sum(rnd.randint(-9, 9) * v[a] for a in v))
s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 20; s.parameters.random_seed = seed
assert s.Solve(m) in (cp_model.OPTIMAL, cp_model.FEASIBLE)
T = {a: s.Value(v[a]) for a in v}
print(grid_str(T), flush=True)
for i, ld in enumerate(pending):
    for a, b in ld:
        x, y = T[parse(a)], T[parse(b)]
        spec['constraints'].append({"type": 'kropki_w' if abs(x - y) == 1 else 'kropki_b', "cells": [a, b], "ladder": 100 + i, "keep": True})


def rs_segs(p):
    segs = [[0]]
    for i in range(1, len(p)):
        (segs[-1].append(i) if box(p[i]) == box(p[i - 1]) else segs.append([i]))
    return segs


def snake_path():
    L = rnd.randint(*SN)
    h = rnd.randrange(8)
    p = [(rnd.randrange(9), rnd.randrange(9))]
    run, last = 0, None
    while len(p) < L:
        d = H8[(h + rnd.choice((-1, 0, 1))) % 8]
        run = run + 1 if d == last else 1
        if run > 2:
            return None
        n = (p[-1][0] + d[0], p[-1][1] + d[1])
        if not (0 <= n[0] < 9 and 0 <= n[1] < 9) or n in p:
            return None
        if len(p) >= 2 and max(abs(n[0] - p[-2][0]), abs(n[1] - p[-2][1])) <= 1:
            return None
        p.append(n); last = d
    if len(rs_segs(p)) < 2 or all(a[0] == p[0][0] for a in p) or all(a[1] == p[0][1] for a in p):
        return None
    return p


def colour(a, b):
    x, y = T[a], T[b]
    if abs(x - y) == 1:
        return 'kropki_w'
    if x == 2 * y or y == 2 * x:
        return 'kropki_b'
    return None


def ladder(lid):
    L = rnd.randint(*LD)
    if rnd.random() < 0.5:
        r, c = rnd.randrange(10 - L), rnd.randrange(8)
        rungs = [((r + i, c), (r + i, c + 1)) for i in range(L)]
    else:
        r, c = rnd.randrange(8), rnd.randrange(10 - L)
        rungs = [((r, c + i), (r + 1, c + i)) for i in range(L)]
    cs = []
    for a, b in rungs:
        t = colour(a, b)
        if t is None:
            return None
        cs.append({"type": t, "cells": [name(a), name(b)], "ladder": lid})
    return cs


def progress(sp):
    lg = Logic(Puzzle(sp))
    res, c = lg.solve(max_tier=2)
    if res == 'contradiction':
        return None
    return sum(len(x) for x in c.values())


cur = progress(spec)
nlad = 1
while cur != 81:
    used = {parse(x) for c in spec['constraints'] for x in c['cells']}
    diag = [d for c in spec['constraints'] if c['type'] == 'regionsum' for d in segs_of([parse(x) for x in c['cells']])]
    best = None
    n = 0
    for _ in range(TRIES * 50):
        if n >= TRIES:
            break
        if rnd.random() < 0.5:
            p = snake_path()
            if not p or set(p) & used or len({sum(T[p[i]] for i in sg) for sg in rs_segs(p)}) != 1:
                continue
            if any(crosses(x, y) for x in segs_of(p) for y in diag):
                continue
            cs, size, kind = [{"type": "regionsum", "cells": [name(a) for a in p]}], len(p) * SNAKEW, 'snake'
        else:
            cs = ladder(nlad)
            if not cs or {parse(x) for c in cs for x in c['cells']} & used:
                continue
            size, kind = 2 * len(cs), 'ladder'
        n += 1
        t = copy.deepcopy(spec); t['constraints'] += cs
        p_ = progress(t)
        if p_ is None:
            continue
        score = p_ + 4 * size
        if best is None or score < best[0]:
            best = (score, p_, cs, kind)
    if best is None:
        continue
    spec['constraints'] += best[2]; cur = best[1]
    if best[3] == 'ladder':
        nlad += 1
    print('add', best[3], [(c['type'][-1], ' '.join(c['cells'])) for c in best[2]], '->', cur, flush=True)


def ok(sp):
    return progress(sp) == 81


ids = []
for c in spec['constraints']:
    if c.get('keep'):
        continue
    key = ('ladder', c['ladder']) if 'ladder' in c else ('snake', tuple(c['cells']))
    if key not in ids:
        ids.append(key)
for key in reversed(ids):
    sp2 = copy.deepcopy(spec)
    sp2['constraints'] = [c for c in spec['constraints'] if c.get('keep') or
                          not ((key[0] == 'ladder' and c.get('ladder') == key[1]) or (key[0] == 'snake' and tuple(c['cells']) == key[1]))]
    if ok(sp2):
        print('drop', key, flush=True); spec = sp2
for lid in sorted({c['ladder'] for c in spec['constraints'] if 'ladder' in c}):
    while True:
        rs = [i for i, c in enumerate(spec['constraints']) if c.get('ladder') == lid]
        if len(rs) <= 2:
            break
        for i in (rs[0], rs[-1]):
            sp2 = copy.deepcopy(spec); del sp2['constraints'][i]
            if ok(sp2):
                print('trim rung', spec['constraints'][i]['cells'], flush=True); spec = sp2; break
        else:
            break
sols, st = Puzzle(spec).count_solutions(limit=2)
print('solutions', len(sols), st, 'elements', len(spec['constraints']),
      'dots', sum(c['type'].startswith('kropki') for c in spec['constraints']),
      'snakes', sum(c['type'] == 'regionsum' for c in spec['constraints']))
for c in spec['constraints']:
    c.pop('keep', None)
json.dump(spec, open(out, 'w'), indent=1)
