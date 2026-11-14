"""Run 11: checks for the invented lookout tower.
1. lookout_nfa (for Rangsk's solver) accepts exactly the crosses [tower, left, right, up, down] whose view count equals the
   tower digit (and no ray cell repeats the tower digit): every tower position, 3,000 crosses read from random grids (about
   6% are towers) plus 3,000 crosses with a random tower digit, decoded with the reader from soundness_run10;
2. the lookout logic step never removes the true digit: random grids, every true tower (and up to 6 random givens), the
   logical solver run to its tier-2 fixpoint;
3. CP-SAT model vs checker agreement for single towers on random (cell, grid) pairs, half of them true towers;
4. 1-5-9 indexing: random 1-5-9 grids pass the checker, and whisper/thermo/indexing logic never removes a true digit."""
import sys, random
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from nfa import lookout_nfa
from ortools.sat.python import cp_model
import base64


def decode(s):  # copied from soundness_run10 (importing it would rerun its tests)
    by = base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))
    bits = ''.join(f'{b:08b}' for b in by); pos = [0]

    def get(n):
        v = int(bits[pos[0]:pos[0] + n], 2) if n else 0; pos[0] += n; return v
    assert get(2) == 0
    sb = get(4) + 1; nsym = get(4) + 1
    nstart = get(sb); nacc = get(sb)
    sia = get(nstart)
    tcb = get(4)
    trans = []
    while len(bits) - pos[0] >= tcb and (len(trans) < (1 << sb)):
        save = pos[0]
        n = get(tcb)
        if pos[0] + n * (4 + sb) > len(bits):
            pos[0] = save; break
        trans.append([(get((nsym - 1).bit_length()), get(sb)) for _ in range(n)])
    start = set(range(nstart))
    accept = set(range(nstart, nstart + nacc)) | {i for i in range(nstart) if sia >> i & 1}
    return start, accept, trans


def accepts(nfa, seq):
    start, accept, trans = nfa
    cur = set(start)
    for d in seq:
        cur = {t for s in cur if s < len(trans) for sym, t in trans[s] if sym == d - 1}
    return bool(cur & accept)


def rand_grid(r):
    m, v = Puzzle({'constraints': []}).build_model()
    m.Minimize(sum(r.randint(-9, 9) * v[a] for a in v))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 1; s.parameters.random_seed = r.randrange(10 ** 6)
    s.Solve(m)
    return {a: s.Value(v[a]) for a in v}



rnd = random.Random(11)
grids = [rand_grid(rnd) for _ in range(40)]


def towers(g):
    return [a for a in g if lookout_view(g[a], [[g[x] for x in ray] for ray in lookout_rays(a)]) == g[a]]


bad = tot = pos = 0
cache = {}
for i in range(6000):
    g = grids[i % len(grids)]
    a = (rnd.randrange(9), rnd.randrange(9))
    rays = lookout_rays(a)
    key = tuple(len(r) for r in rays)
    if key not in cache:
        cache[key] = decode(lookout_nfa(list(key)))
    seq = [g[a]] + [g[x] for r in rays for x in r]
    if i % 2:
        seq[0] = rnd.randint(1, 9)
    truth = lookout_view(seq[0], [[g[x] for x in r] for r in rays]) == seq[0] and seq[0] not in seq[1:]
    bad += accepts(cache[key], seq) != truth; tot += 1; pos += truth
print(f'1. lookout NFA vs lookout_view: {bad} mismatches in {tot} crosses ({pos} of them towers; {len(cache)} ray-length patterns)')

lost = 0; nt = 0
for g in grids[:30]:
    tw = towers(g); nt += len(tw)
    givens = {name(a): g[a] for a in rnd.sample(sorted(g), rnd.randint(0, 6))}
    L = Logic(Puzzle({'constraints': [{"type": "lookout", "cells": [name(a)]} for a in tw], 'givens': givens})); cand = L.init_cands()
    L.propagate(cand, 2)
    lost += sum(g[a] not in cand[a] for a in cand)
print(f'2. lookout logic, 30 random grids ({nt} towers): true digits removed {lost}')

agree = tot = 0
for trial in range(200):
    g = grids[trial % len(grids)]
    tw = towers(g)
    a = rnd.choice(tw) if trial % 2 == 0 and tw else (rnd.randrange(9), rnd.randrange(9))
    pz = Puzzle({'constraints': [{"type": "lookout", "cells": [name(a)]}]})
    m, v = pz.build_model()
    for x in v:
        m.Add(v[x] == g[x])
    s = cp_model.CpSolver(); st = s.Solve(m)
    tot += 1; agree += (st in (cp_model.OPTIMAL, cp_model.FEASIBLE)) == (not pz.check(g))
print(f'3. lookout model vs checker: {agree}/{tot} agree')

# 4. 1-5-9 indexing (global idx159): random 1-5-9 grids pass the checker, and with random satisfied 3-cell whispers/thermos
#    plus 3-12 random givens, the tier-2 logic never removes a true digit
bad = lost = 0
for trial in range(30):
    m, v = Puzzle({'global': ['idx159'], 'constraints': []}).build_model()
    m.Minimize(sum(rnd.randint(-9, 9) * v[a] for a in v))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 1; s.parameters.random_seed = rnd.randrange(10 ** 6); s.Solve(m)
    g = {a: s.Value(v[a]) for a in v}
    bad += bool(Puzzle({'global': ['idx159'], 'constraints': []}).check(g))
    cons = []
    for _ in range(12):
        r, k = rnd.randrange(9), rnd.randrange(7)
        cells = [(r, k), (r, k + 1), (r, k + 2)] if rnd.random() < .5 else [(k, r), (k + 1, r), (k + 2, r)]
        vals = [g[a] for a in cells]
        if all(abs(a - b) >= 5 for a, b in zip(vals, vals[1:])):
            cons.append({'type': 'whisper', 'cells': [name(a) for a in cells]})
        elif all(a < b for a, b in zip(vals, vals[1:])):
            cons.append({'type': 'thermo', 'cells': [name(a) for a in cells]})
        elif all(a > b for a, b in zip(vals, vals[1:])):
            cons.append({'type': 'thermo', 'cells': [name(a) for a in cells[::-1]]})
    giv = {name(a): g[a] for a in rnd.sample(sorted(g), rnd.randint(3, 12))}
    L = Logic(Puzzle({'global': ['idx159'], 'constraints': cons, 'givens': giv})); cand = L.init_cands()
    L.propagate(cand, 2)
    lost += sum(g[a] not in cand[a] for a in cand)
print(f'4. 1-5-9 indexing: {bad} of 30 random 1-5-9 grids fail the checker; whisper/thermo/indexing logic removed {lost} true digits')
