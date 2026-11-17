"""Run 14: checks for median clues (new to the toolkit) and the polydivisible lines + killer cages of 027.
1. the median NFA sent to Rangsk accepts exactly the ordered triples of different digits whose middle value is the clue
   (all 729 triples, every clue 1-9);
2. median logic never removes the true digit: random grids, 6-16 random median clues of the grid, 0-10 random givens,
   solved to the tier-2 fixpoint (and German whispers of the grid where the grid allows them);
3. CP-SAT model vs checker agreement on random (median clue, grid) pairs, half of them true for the grid, and solution
   counting with a full grid as givens returns exactly 1;
4. polydivisible lines + killer cages: random grids satisfying random bracket-shaped polydivisible lines (CP-SAT), with
   random killer cages of the grid and 0-6 givens, solved to the tier-2 fixpoint: the true digit is never removed."""
import sys, random, itertools
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from nfa import seqs_nfa
from soundness_run12_decode import decode, accepts
from ortools.sat.python import cp_model


def rand_grid(r, spec=None):
    m, v = Puzzle(spec or {'constraints': []}).build_model()
    m.Minimize(sum(r.randint(-9, 9) * v[a] for a in v))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 5; s.parameters.random_seed = r.randrange(10 ** 6)
    st = s.Solve(m)
    return {a: s.Value(v[a]) for a in v} if st in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None


rnd = random.Random(14)
POS = [f"r0c{k}" for k in range(1, 10)] + [f"r10c{k}" for k in range(1, 10)] + \
      [f"r{k}c0" for k in range(1, 10)] + [f"r{k}c10" for k in range(1, 10)]

# 1. median NFA (built exactly as rangsk.py builds it)
bad = tot = 0
for m_ in DIGITS:
    trip = [q for q in itertools.permutations(DIGITS, 3) if sorted(q)[1] == m_]
    if not trip:
        continue
    nfa = decode(seqs_nfa(trip))
    for q in itertools.product(DIGITS, repeat=3):
        truth = len(set(q)) == 3 and sorted(q)[1] == m_
        bad += accepts(nfa, q) != truth; tot += 1
print(f'1. median NFA: {bad} mismatches in {tot} (triple, clue) checks')

# 2. median logic (+ whispers that the grid satisfies)
lost = runs = 0
for it in range(30):
    g = rand_grid(rnd)
    cons = []
    for p in rnd.sample(POS, rnd.randint(6, 16)):
        cons.append({"type": "median", "from": p, "value": sorted(g[a] for a in outside_ray(p)[:3])[1]})
    for _ in range(40):  # straight 2-4 cell whisper segments that the grid happens to satisfy
        r0, c0 = rnd.randrange(9), rnd.randrange(9)
        d = rnd.choice([(0, 1), (1, 0), (1, 1), (1, -1)])
        cells = [(r0 + i * d[0], c0 + i * d[1]) for i in range(rnd.randint(2, 4))]
        if all(0 <= a < 9 and 0 <= b < 9 for a, b in cells) and all(abs(g[x] - g[y]) >= 5 for x, y in zip(cells, cells[1:])):
            cons.append({"type": "whisper", "cells": [name(a) for a in cells]})
    givens = {name(a): g[a] for a in rnd.sample(sorted(g), rnd.randint(0, 10))}
    pz = Puzzle({"constraints": cons, "givens": givens})
    assert not pz.check(g)
    L = Logic(pz); cand = L.init_cands()
    L.propagate(cand, 2)
    lost += sum(g[a] not in cand[a] for a in g); runs += 1
print(f'2. median (+ whisper) logic: true digit removed {lost} times in {runs} grids')

# 3. model vs checker
agree = n = 0
for it in range(100):
    g = rand_grid(rnd)
    p = rnd.choice(POS)
    true_v = sorted(g[a] for a in outside_ray(p)[:3])[1]
    val = true_v if it % 2 == 0 else rnd.choice([x for x in range(2, 9) if x != true_v])
    spec = {"constraints": [{"type": "median", "from": p, "value": val}], "givens": {name(a): g[a] for a in g}}
    pz = Puzzle(spec)
    sols, st = pz.count_solutions(limit=2, time_limit=20)
    model_ok = len(sols) == 1
    agree += model_ok == (not pz.check(g)); n += 1
    if model_ok:
        assert len(sols) == 1 and st == 'OPTIMAL'
print(f'3. median model vs checker: {agree}/{n} agree (full grid as givens counts exactly 1 solution when true)')

# 4. polydivisible brackets + killer cages
def bracket(r, c, n=6):
    cells = [(r + 2, c - 1), (r + 1, c), (r, c)] + [(r, c + i) for i in range(1, n - 2)]
    return [f"r{a}c{b}" for a, b in cells]


lost = runs = 0
for it in range(16):
    lay = [(rnd.randint(1, 7), rnd.randint(2, 6)) for _ in range(rnd.randint(1, 3))]
    lines = [{"type": "polydiv", "cells": bracket(r, c)} for r, c in lay]
    if len({x for l in lines for x in l['cells']}) < sum(len(l['cells']) for l in lines):
        continue
    g = rand_grid(rnd, {"constraints": lines})
    if g is None:
        continue
    cons = list(lines)
    used = set()
    for _ in range(rnd.randint(4, 10)):
        a = (rnd.randrange(9), rnd.randrange(9))
        cells = [a]
        for _ in range(rnd.randint(1, 3)):
            r, c = rnd.choice(cells)
            nb = [x for x in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)) if 0 <= x[0] < 9 and 0 <= x[1] < 9 and x not in cells]
            if nb:
                cells.append(rnd.choice(nb))
        if set(cells) & used or len({g[x] for x in cells}) < len(cells):
            continue
        used |= set(cells)
        cons.append({"type": "killer", "cells": [name(x) for x in cells], "sum": sum(g[x] for x in cells)})
    givens = {name(a): g[a] for a in rnd.sample(sorted(g), rnd.randint(0, 6))}
    pz = Puzzle({"constraints": cons, "givens": givens})
    assert not pz.check(g)
    L = Logic(pz); cand = L.init_cands()
    L.propagate(cand, 2)
    lost += sum(g[a] not in cand[a] for a in g); runs += 1
print(f'4. polydivisible brackets + killer cages logic: true digit removed {lost} times in {runs} grids')
