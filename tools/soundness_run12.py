"""Run 12: checks for complete summit/valley maps and lockout lines.
1. notext_nfa (unmarked cells of a complete map, for Rangsk's solver) accepts exactly the sequences [cell, neighbours...]
   with a larger (notmax) or smaller (notmin) neighbour: all 9^3 and 9^4 sequences and 20,000 random 5-digit sequences;
2. lockout_nfa accepts exactly the valid lockout fills read as [diamond, diamond, inner...]: all sequences of 2-4 digits
   and 20,000 random 5-8 digit sequences;
3. the summit/valley logic never removes the true digit: random grids with their complete summit map, valley map or
   both, plus 0-12 random givens, solved to the tier-2 fixpoint;
4. the lockout logic never removes the true digit: random grids, random satisfied lockout lines (3-9 cells, random
   king-step paths), 0-10 random givens;
5. CP-SAT model vs checker agreement on random (map/line, grid) pairs, half of them true for the grid; and solution
   counting with a full grid as givens returns exactly 1 (the auxiliary booleans are fully reified)."""
import sys, random, itertools
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from nfa import notext_nfa, lockout_nfa
import base64
from ortools.sat.python import cp_model


def decode(s):  # copied from soundness_run11 (importing it would rerun its tests)
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


rnd = random.Random(12)
grids = [rand_grid(rnd) for _ in range(40)]

# 1. notext NFA
bad = tot = 0
for kind in ('notmax', 'notmin'):
    nfa = decode(notext_nfa(kind))
    seqs = list(itertools.product(range(1, 10), repeat=3)) + list(itertools.product(range(1, 10), repeat=4)) + \
        [tuple(rnd.randint(1, 9) for _ in range(5)) for _ in range(10000)]
    for sq in seqs:
        truth = sq[0] < max(sq[1:]) if kind == 'notmax' else sq[0] > min(sq[1:])
        bad += accepts(nfa, sq) != truth; tot += 1
print(f'1. notext NFA: {bad} mismatches in {tot} sequences')

# 2. lockout NFA
nfa = decode(lockout_nfa())
bad = tot = 0
seqs = [sq for L in (2, 3, 4) for sq in itertools.product(range(1, 10), repeat=L)] + \
    [tuple(rnd.randint(1, 9) for _ in range(rnd.randint(5, 8))) for _ in range(20000)]
for sq in seqs:
    lo, hi = sorted(sq[:2])
    truth = hi - lo >= 4 and all(x < lo or x > hi for x in sq[2:])
    bad += accepts(nfa, sq) != truth; tot += 1
print(f'2. lockout NFA: {bad} mismatches in {tot} sequences')

# 3. summit/valley logic
lost = 0
for i, g in enumerate(grids[:30]):
    kinds = [('summits',), ('valleys',), ('summits', 'valleys')][i % 3]
    cons = [{'type': k, 'cells': [name(a) for a in sorted(local_extrema(g, k))]} for k in kinds]
    giv = {name(a): g[a] for a in rnd.sample(sorted(g), rnd.randint(0, 12))}
    L = Logic(Puzzle({'constraints': cons, 'givens': giv})); cand = L.init_cands()
    L.propagate(cand, 2)
    lost += sum(g[a] not in cand[a] for a in cand)
print(f'3. summit/valley logic, 30 random grids: true digits removed {lost}')


def rand_path(r, L):
    p = [(r.randrange(9), r.randrange(9))]
    while len(p) < L:
        nb = [(p[-1][0] + a, p[-1][1] + b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]
        nb = [x for x in nb if 0 <= x[0] < 9 and 0 <= x[1] < 9 and x not in p]
        if not nb:
            return None
        p.append(r.choice(nb))
    return p


def lockout_ok(vals):
    lo, hi = sorted((vals[0], vals[-1]))
    return hi - lo >= 4 and all(x < lo or x > hi for x in vals[1:-1])


# 4. lockout logic
lost = nlines = 0
for g in grids[:30]:
    cons = []
    for _ in range(400):
        p = rand_path(rnd, rnd.randint(3, 9))
        if p and lockout_ok([g[a] for a in p]):
            cons.append({'type': 'lockout', 'cells': [name(a) for a in p]})
        if len(cons) >= 6:
            break
    nlines += len(cons)
    giv = {name(a): g[a] for a in rnd.sample(sorted(g), rnd.randint(0, 10))}
    L = Logic(Puzzle({'constraints': cons, 'givens': giv})); cand = L.init_cands()
    L.propagate(cand, 2)
    lost += sum(g[a] not in cand[a] for a in cand)
print(f'4. lockout logic, 30 random grids ({nlines} lines): true digits removed {lost}')

# 5. model vs checker, and exact counting with all givens
agree = tot = 0
one = 0
for trial in range(200):
    g = grids[trial % len(grids)]
    if trial % 2:
        k = rnd.choice(['summits', 'valleys'])
        cells = local_extrema(g, k)
        if trial % 4 == 1:  # perturb: drop or add one cell
            cells = set(cells) ^ {(rnd.randrange(9), rnd.randrange(9))}
        cons = [{'type': k, 'cells': [name(a) for a in sorted(cells)]}]
    else:
        p = None
        while not p:
            p = rand_path(rnd, rnd.randint(3, 7))
        cons = [{'type': 'lockout', 'cells': [name(a) for a in p]}]
    pz = Puzzle({'constraints': cons})
    m, v = pz.build_model()
    for x in v:
        m.Add(v[x] == g[x])
    s = cp_model.CpSolver(); st = s.Solve(m)
    tot += 1; agree += (st in (cp_model.OPTIMAL, cp_model.FEASIBLE)) == (not pz.check(g))
    if trial < 20 and not pz.check(g):
        sp = {'constraints': cons, 'givens': {name(a): g[a] for a in g}}
        sols, st2 = Puzzle(sp).count_solutions(5, 30)
        one += len(sols) == 1 and st2 == 'OPTIMAL'
print(f'5. model vs checker: {agree}/{tot} agree; counting with a full grid as givens gave exactly 1 solution in {one} valid cases')
