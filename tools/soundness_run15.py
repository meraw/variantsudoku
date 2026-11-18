"""Run 15: checks for counting circles (new to the toolkit) and the invented fifths lines.
1. the counting-circle NFA sent to Rangsk (nfa.counting_nfa) accepts exactly the digit sequences in which every digit d that
   occurs occurs exactly d times: for 8, 12, 15 and 17 circles, shuffled valid sequences, one-cell perturbations of them and
   uniformly random sequences;
2. counting-circle logic never removes the true digit: random grids, a random valid circle set (a random digit set S, d
   circles on cells holding d), with random between lines and sandwich sums of the grid (the mix of 029) and 0-12 givens,
   solved to the tier-2 fixpoint;
3. CP-SAT model vs checker agreement for counting circles (full grid as givens; half of the circle sets valid for the grid);
4. the fifths relation: the pair table sent to Rangsk decodes to "differ by 4 or 5", and its graph is the 9-cycle
   1-5-9-4-8-3-7-2-6;
5. fifths lines + killer cages: random grids satisfying random fifths lines (CP-SAT), with random killer cages of the grid
   and 0-6 givens, solved to the tier-2 fixpoint: the true digit is never removed. Model vs checker agreement on fifths lines."""
import sys, random, itertools, base64, struct
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from nfa import counting_nfa
from rangsk import pair_table
from soundness_run12_decode import decode, accepts
from ortools.sat.python import cp_model


def rand_grid(r, spec=None):
    m, v = Puzzle(spec or {'constraints': []}).build_model()
    m.Minimize(sum(r.randint(-9, 9) * v[a] for a in v))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 5; s.parameters.random_seed = r.randrange(10 ** 6)
    st = s.Solve(m)
    return {a: s.Value(v[a]) for a in v} if st in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None


rnd = random.Random(15)
SETS = lambda n: [S for k in range(1, 10) for S in itertools.combinations(DIGITS, k) if sum(S) == n]

# 1. counting NFA
bad = tot = 0
for n in (8, 12, 15, 17):
    nfa = decode(counting_nfa(n))
    for _ in range(1000):
        S = rnd.choice(SETS(n)); seq = [d for d in S for _ in range(d)]; rnd.shuffle(seq)
        bad += not accepts(nfa, seq); tot += 1
        q = list(seq); q[rnd.randrange(n)] = rnd.randint(1, 9)
        bad += accepts(nfa, q) != all(q.count(d) == d for d in set(q)); tot += 1
        q = [rnd.randint(1, 9) for _ in range(n)]
        bad += accepts(nfa, q) != all(q.count(d) == d for d in set(q)); tot += 1
print(f'1. counting NFA: {bad} mismatches in {tot} sequence checks')


def circles_for(g, S):
    out = []
    for d in S:
        out += rnd.sample([a for a in g if g[a] == d], d)
    return out


POS = [f"r0c{k}" for k in range(1, 10)] + [f"r{k}c0" for k in range(1, 10)]
# 2. counting logic (+ between lines + sandwiches of the grid)
lost = runs = 0
for it in range(30):
    g = rand_grid(rnd)
    S = rnd.choice([S for n in range(8, 22) for S in SETS(n) if max(S) <= 9])
    circ = circles_for(g, S)
    cons = [{"type": "counting", "cells": [name(a) for a in circ]}]
    for _ in range(60):  # straight 3-5 cell between lines the grid happens to satisfy
        r0, c0 = rnd.randrange(9), rnd.randrange(9)
        d = rnd.choice([(0, 1), (1, 0), (1, 1), (1, -1)])
        cells = [(r0 + i * d[0], c0 + i * d[1]) for i in range(rnd.randint(3, 5))]
        if all(0 <= a < 9 and 0 <= b < 9 for a, b in cells):
            lo, hi = sorted((g[cells[0]], g[cells[-1]]))
            if all(lo < g[x] < hi for x in cells[1:-1]):
                cons.append({"type": "between", "cells": [name(a) for a in cells]})
    for p in rnd.sample(POS, rnd.randint(0, 5)):
        vals = [g[a] for a in outside_line(p)]
        i, j = sorted((vals.index(1), vals.index(9)))
        cons.append({"type": "sandwich", "from": p, "sum": sum(vals[i + 1:j])})
    givens = {name(a): g[a] for a in rnd.sample(sorted(g), rnd.randint(0, 12))}
    pz = Puzzle({"constraints": cons, "givens": givens})
    assert not pz.check(g), pz.check(g)
    L = Logic(pz); cand = L.init_cands()
    L.propagate(cand, 2)
    lost += sum(g[a] not in cand[a] for a in g); runs += 1
print(f'2. counting (+ between + sandwich) logic: true digit removed {lost} times in {runs} grids')

# 3. model vs checker (counting)
agree = n = 0
for it in range(60):
    g = rand_grid(rnd)
    S = rnd.choice(SETS(rnd.randint(8, 18)))
    circ = circles_for(g, S)
    if it % 2:  # usually invalid: swap one circle for a random other cell
        circ[rnd.randrange(len(circ))] = rnd.choice([a for a in g if a not in circ])
    pz = Puzzle({"constraints": [{"type": "counting", "cells": [name(a) for a in circ]}], "givens": {name(a): g[a] for a in g}})
    sols, st = pz.count_solutions(limit=2, time_limit=20)
    agree += (len(sols) == 1) == (not pz.check(g)); n += 1
print(f'3. counting model vs checker: {agree}/{n} agree')

# 4. fifths relation and its pair table
tab = struct.unpack('<9I', base64.urlsafe_b64decode(pair_table('fifths') + '=' * (-len(pair_table('fifths')) % 4)))
ok = all(((tab[a - 1] >> (b - 1)) & 1) == (abs(a - b) in (4, 5)) for a in DIGITS for b in DIGITS)
cyc, x, prev = [1], 1, None
while True:
    nxt = [y for y in DIGITS if PAIR_REL['fifths'](x, y) and y != prev]
    prev, x = x, nxt[0] if prev is not None or nxt[0] == 5 else nxt[1]
    if x == 1:
        break
    cyc.append(x)
print(f'4. fifths pair table decodes correctly: {ok}; every digit has 2 partners: '
      f'{all(sum(PAIR_REL["fifths"](a, b) for b in DIGITS) == 2 for a in DIGITS)}; cycle from 1: {"-".join(map(str, cyc))}')

# 5. fifths lines + killer cages
lost = runs = 0
agree = n = 0
for it in range(45):
    lines = []
    for _ in range(rnd.randint(2, 5)):
        r0, c0 = rnd.randrange(9), rnd.randrange(9)
        cells = [(r0, c0)]
        for _ in range(rnd.randint(2, 8)):
            r, c = cells[-1]
            nb = [(r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr or dc)]
            nb = [x for x in nb if 0 <= x[0] < 9 and 0 <= x[1] < 9 and x not in cells]
            if nb:
                cells.append(rnd.choice(nb))
        lines.append({"type": "fifths", "cells": [name(a) for a in cells]})
    g = rand_grid(rnd, {"constraints": lines})
    if g is None:
        continue
    cons = list(lines); used = set()
    for _ in range(rnd.randint(4, 10)):
        a = (rnd.randrange(9), rnd.randrange(9)); cells = [a]
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
    # model vs checker on a full grid, with one line made false half of the time
    g2 = dict(g)
    if it % 2:
        a = parse(lines[0]['cells'][0]); g2[a] = rnd.choice([d for d in DIGITS if d != g[a]])
    pz2 = Puzzle({"constraints": lines, "givens": {name(a): g2[a] for a in g2}})
    sols, st = pz2.count_solutions(limit=2, time_limit=20)
    agree += (len(sols) == 1) == (not pz2.check(g2)); n += 1
print(f'5. fifths lines + killer cages logic: true digit removed {lost} times in {runs} grids; model vs checker {agree}/{n} agree')
