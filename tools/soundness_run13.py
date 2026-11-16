"""Run 13: checks for battlefield clues (and the entropic/modular lines first used in a puzzle this run).
1. battlefield_nfa accepts exactly the rows of nine different digits with the right battlefield total (it tracks the
   digits used): 4,000 random rows of distinct digits plus 4,000 random sequences with repeats (always rejected), each
   against its true total and two random totals 0-45;
2. the battlefield logic step never removes the true digit: random grids, 6-14 random battlefield clues of the grid,
   0-10 random givens, solved to the tier-2 fixpoint;
3. entropic/modular logic never removes the true digit: random grids satisfying random straight entropic/modular
   lines (found by CP-SAT), plus skyscraper clues of the grid;
4. CP-SAT model vs checker agreement on random (battlefield clue, grid) pairs, half of them true for the grid, and solution
   counting with a full grid as givens returns exactly 1 (the region booleans are fully reified);
5. polydivisible lines (invented): POLYDIV_SEQS equals a brute-force filter of all digit strings (lengths 1-6) and its
   distinct-digit 9-cell member is 381654729; the line NFA sent to Rangsk accepts exactly the line's valid fills;
6. polydivisible logic never removes the true digit: random grids satisfying random king-step polydivisible lines of 3-6 cells
   (found by CP-SAT), 0-8 random givens; and model vs checker agreement on random (line, grid) pairs."""
import sys, random
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from nfa import battlefield_nfa
from soundness_run12_decode import decode, accepts
from ortools.sat.python import cp_model


def rand_grid(r, spec=None):
    m, v = Puzzle(spec or {'constraints': []}).build_model()
    m.Minimize(sum(r.randint(-9, 9) * v[a] for a in v))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 2; s.parameters.random_seed = r.randrange(10 ** 6)
    st = s.Solve(m)
    return {a: s.Value(v[a]) for a in v} if st in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None


rnd = random.Random(13)

# 1. NFA
bad = tot = 0
rows = [tuple(rnd.sample(range(1, 10), 9)) for _ in range(4000)] + [tuple(rnd.randint(1, 9) for _ in range(9)) for _ in range(4000)]
nfas = {t: decode(battlefield_nfa(t)) for t in range(0, 46)}
for row in rows:
    true_t = battlefield_sum(list(row)) if row[0] != row[-1] else None
    if true_t is not None and true_t > 45:
        true_t = None
    for t in {true_t, rnd.randint(0, 45), rnd.randint(0, 45)} - {None}:
        truth = (t == true_t) and len(set(row)) == 9
        bad += accepts(nfas[t], row) != truth; tot += 1
print(f'1. battlefield NFA: {bad} mismatches in {tot} (row, total) checks')

# 2. battlefield logic
POSL = [f"r0c{k}" for k in range(1, 10)] + [f"r{k}c0" for k in range(1, 10)]
lost = runs = 0
for it in range(30):
    g = rand_grid(rnd)
    cons = []
    for p in rnd.sample(POSL, rnd.randint(6, 14)):
        cons.append({"type": "battlefield", "from": p, "sum": battlefield_sum([g[a] for a in outside_line(p)])})
    givens = {name(a): g[a] for a in rnd.sample(sorted(g), rnd.randint(0, 10))}
    pz = Puzzle({"constraints": cons, "givens": givens})
    assert not pz.check(g)
    L = Logic(pz); cand = L.init_cands()
    L.propagate(cand, 2)
    lost += sum(g[a] not in cand[a] for a in g); runs += 1
print(f'2. battlefield logic: true digit removed {lost} times in {runs} grids')

# 3. entropic / modular + skyscrapers
lost = runs = 0
for it in range(20):
    cons = []
    for t in ('entropic', 'modular'):
        for _ in range(rnd.randint(1, 3)):
            if rnd.random() < 0.5:
                r = rnd.randrange(9); a = rnd.randint(0, 5); b = rnd.randint(a + 2, 8)
                cons.append({"type": t, "cells": [name((r, k)) for k in range(a, b + 1)]})
            else:
                k = rnd.randrange(9); a = rnd.randint(0, 5); b = rnd.randint(a + 2, 8)
                cons.append({"type": t, "cells": [name((r, k)) for r in range(a, b + 1)]})
    g = rand_grid(rnd, {"constraints": cons})
    if g is None:
        continue
    POS = [f"r0c{k}" for k in range(1, 10)] + [f"r{k}c0" for k in range(1, 10)] + [f"r10c{k}" for k in range(1, 10)] + [f"r{k}c10" for k in range(1, 10)]
    for p in rnd.sample(POS, 6):
        vals = [g[a] for a in outside_ray(p)]
        cons.append({"type": "skyscraper", "from": p, "count": sum(1 for i, x in enumerate(vals) if all(x > y for y in vals[:i]))})
    pz = Puzzle({"constraints": cons, "givens": {name(a): g[a] for a in rnd.sample(sorted(g), rnd.randint(0, 6))}})
    assert not pz.check(g)
    L = Logic(pz); cand = L.init_cands(); L.propagate(cand, 2)
    lost += sum(g[a] not in cand[a] for a in g); runs += 1
print(f'3. entropic/modular + skyscraper logic: true digit removed {lost} times in {runs} grids')

# 4. model vs checker
agree = tot = 0
grids4 = [rand_grid(rnd) for _ in range(10)]
for it in range(100):
    g = grids4[it % 10]
    p = rnd.choice(POSL)
    true_s = battlefield_sum([g[a] for a in outside_line(p)])
    s_ = true_s if it % 2 == 0 else rnd.choice([x for x in range(0, 46) if x != true_s])
    pz = Puzzle({"constraints": [{"type": "battlefield", "from": p, "sum": s_}], "givens": {name(a): g[a] for a in g}})
    sols, st = pz.count_solutions(limit=2, time_limit=20)
    agree += (len(sols) == 1) == (not pz.check(g)); tot += 1
    if it % 2 == 0:
        assert len(sols) == 1, (st, len(sols))
print(f'4. model vs checker: {agree}/{tot} agree; full-grid givens give exactly 1 solution on the true clues')

# 5. polydivisible tables and NFA
import itertools
from nfa import seqs_nfa
bad = 0
for L in range(1, 7):
    brute = [v for v in itertools.product(range(1, 10), repeat=L) if all(int(''.join(map(str, v[:k]))) % k == 0 for k in range(1, L + 1))]
    bad += sorted(brute) != sorted(POLYDIV_SEQS[L])
nine = [v for v in POLYDIV_SEQS[9] if len(set(v)) == 9]
nbad = ntot = 0
for L in (3, 4, 5, 6):
    fills = POLYDIV_SEQS[L]
    nf = decode(seqs_nfa(fills)); fs = set(fills)
    for v in list(fills) + [tuple(rnd.randint(1, 9) for _ in range(L)) for _ in range(3000)]:
        nbad += accepts(nf, v) != (v in fs); ntot += 1
print(f'5. polydiv tables: {bad} mismatching lengths; distinct 9-digit members {nine}; NFA: {nbad} mismatches in {ntot}')

# 6. polydivisible logic + model/checker
KING = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
def rand_path(L):
    while True:
        p = [(rnd.randrange(9), rnd.randrange(9))]
        while len(p) < L:
            d = rnd.choice(KING); n = (p[-1][0] + d[0], p[-1][1] + d[1])
            if not (0 <= n[0] < 9 and 0 <= n[1] < 9) or n in p:
                break
            p.append(n)
        if len(p) == L:
            return p
lost = runs = 0
for it in range(25):
    cons = [{"type": "polydiv", "cells": [name(a) for a in rand_path(rnd.randint(3, 6))]} for _ in range(rnd.randint(2, 6))]
    g = rand_grid(rnd, {"constraints": cons})
    if g is None:
        continue
    pz = Puzzle({"constraints": cons, "givens": {name(a): g[a] for a in rnd.sample(sorted(g), rnd.randint(0, 8))}})
    assert not pz.check(g)
    L = Logic(pz); cand = L.init_cands(); L.propagate(cand, 2)
    lost += sum(g[a] not in cand[a] for a in g); runs += 1
agree = tot = 0
for it in range(100):
    g = grids4[it % 10]
    p = rand_path(rnd.randint(3, 6))
    c = {"type": "polydiv", "cells": [name(a) for a in p]}
    pz = Puzzle({"constraints": [c], "givens": {name(a): g[a] for a in g}})
    sols, st = pz.count_solutions(limit=2, time_limit=20)
    agree += (len(sols) == 1) == (not pz.check(g)); tot += 1
print(f'6. polydiv logic: true digit removed {lost} times in {runs} grids; model vs checker: {agree}/{tot} agree')
