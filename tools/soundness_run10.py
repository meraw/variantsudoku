"""Run 10: checks for the invented frog clue and the fixed-value (all-13) setting.
1. frog_nfa (for Rangsk's solver) accepts exactly the digit sequences whose frog sum is the total: every total 9-17, on
   20,000 random permutations and 20,000 random sequences with repeats (decoded with the reader from soundness_run8);
2. the frog logic step (exact ray walk) never removes the true digit: random grids, 6-14 random frog clues taken from the
   grid, plus a few random givens, the logical solver run to its tier-2 fixpoint;
3. the same for the 13-clue mix of 019 (killer cages, little killers, X-sums from random grids);
4. CP-SAT model vs checker agreement for frog clues on random (clue, grid) pairs, half of them satisfied."""
import sys, random, itertools, base64
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from nfa import frog_nfa
from ortools.sat.python import cp_model


def decode(s):  # copied from soundness_run8 (importing it would rerun the run-7/8 tests)
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


rnd = random.Random(10)
perms = [tuple(rnd.sample(range(1, 10), 9)) for _ in range(20000)]
reps = [tuple(rnd.randint(1, 9) for _ in range(9)) for _ in range(20000)]
bad = 0
for t in range(9, 18):
    nfa = decode(frog_nfa(t))
    bad += sum(accepts(nfa, v) != (frog_sum(v) == t) for v in perms + reps)
print('1. frog NFA vs frog_sum, totals 9-17, 40,000 sequences each: mismatches', bad)


def rand_grid(r):
    m, v = Puzzle({'constraints': []}).build_model()
    m.Minimize(sum(r.randint(-9, 9) * v[a] for a in v))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 1; s.parameters.random_seed = r.randrange(10 ** 6)
    s.Solve(m)
    return {a: s.Value(v[a]) for a in v}


POS = [f"r0c{k}" for k in range(1, 10)] + [f"r10c{k}" for k in range(1, 10)] + \
      [f"r{k}c0" for k in range(1, 10)] + [f"r{k}c10" for k in range(1, 10)]
lost = 0
for trial in range(30):
    g = rand_grid(rnd)
    cons = [{"type": "frog", "from": p, "sum": frog_sum([g[a] for a in outside_ray(p)])} for p in rnd.sample(POS, rnd.randint(6, 14))]
    givens = {name(a): g[a] for a in rnd.sample(sorted(g), rnd.randint(0, 6))}
    L = Logic(Puzzle({'constraints': cons, 'givens': givens})); cand = L.init_cands()
    L.propagate(cand, 2)
    lost += sum(g[a] not in cand[a] for a in cand)
print('2. frog logic, 30 random grids: true digits removed', lost)

lost = 0
for trial in range(30):
    g = rand_grid(rnd)
    cons = []
    for p in rnd.sample(POS, 3):
        cons.append({"type": "xsum", "from": p, "sum": sum([g[a] for a in outside_ray(p)][:g[outside_ray(p)[0]]])})
    for _ in range(3):
        frm, d = rnd.choice([(f"r0c{k}", 'DR') for k in range(0, 7)] + [(f"r0c{k}", 'DL') for k in range(3, 10)])
        cons.append({"type": "littlekiller", "from": frm, "dir": d, "sum": sum(g[a] for a in lk_cells(frm, d))})
    for _ in range(3):
        r, k = rnd.randrange(8), rnd.randrange(8)
        cells = [(r, k), (r, k + 1)] if rnd.random() < 0.5 else [(r, k), (r + 1, k), (r + 1, k + 1)]
        cons.append({"type": "killer", "cells": [name(a) for a in cells], "sum": sum(g[a] for a in cells)})
    L = Logic(Puzzle({'constraints': cons, 'givens': {name(a): g[a] for a in rnd.sample(sorted(g), 4)}})); cand = L.init_cands()
    L.propagate(cand, 2)
    lost += sum(g[a] not in cand[a] for a in cand)
print('3. cage + little-killer + X-sum logic, 30 random grids: true digits removed', lost)

agree = tot = 0
for trial in range(200):
    g = rand_grid(rnd) if trial % 20 == 0 or trial == 0 else g
    p = rnd.choice(POS)
    true = frog_sum([g[a] for a in outside_ray(p)])
    t = true if trial % 2 == 0 else rnd.randint(9, 17)
    pz = Puzzle({'constraints': [{"type": "frog", "from": p, "sum": t}]})
    m, v = pz.build_model()
    for a in v:
        m.Add(v[a] == g[a])
    s = cp_model.CpSolver(); st = s.Solve(m)
    model_ok = st in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    check_ok = not pz.check(g)
    tot += 1; agree += model_ok == check_ok
print(f'4. frog model vs checker: {agree}/{tot} agree')
