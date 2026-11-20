"""Run 17 soundness tests.
1. graceful_nfa accepts exactly the sequences whose neighbour differences are all different (random sequences of
   length 2-9, plus every 3-digit sequence).
2. The exact graceful step (memoised fill search) keeps exactly the digits that occur in some fill (brute force on
   random short lines with random candidates), and the relaxed walk never removes a digit the exact step keeps.
3. On random grids with random graceful lines that the grid satisfies (plus random kropki dots and sandwich sums from
   the same grid), the logical solver never removes a true digit; model and checker agree.
4. Windoku: on random windoku grids with random skyscraper clues from the grid, the logical solver never removes a
   true digit, and the CP-SAT model and checker agree (the windows are houses).
python3 soundness_run17.py [grids]"""
import sys, random, itertools
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
import vs
from nfa import graceful_nfa
from soundness_run12_decode import decode, accepts
from ortools.sat.python import cp_model


def random_grid(seed, glob=()):
    pz = vs.Puzzle({'global': list(glob), 'constraints': []})
    m, v = pz.build_model()
    rng = random.Random(seed)
    for x in v:
        m.AddHint(v[x], rng.randint(1, 9))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 5; s.parameters.random_seed = seed
    s.parameters.randomize_search = True; s.parameters.num_workers = 1
    assert s.Solve(m) in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    return {x: s.Value(v[x]) for x in v}


def rand_path(rng, L):
    while True:
        p = [(rng.randrange(9), rng.randrange(9))]
        for _ in range(L - 1):
            opts = [(p[-1][0] + dr, p[-1][1] + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc]
            opts = [q for q in opts if 0 <= q[0] < 9 and 0 <= q[1] < 9 and q not in p]
            if not opts:
                break
            p.append(rng.choice(opts))
        if len(p) == L:
            return p


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    rng = random.Random(17)
    # 1. automaton
    A = decode(graceful_nfa())
    seqs = [tuple(rng.randint(1, 9) for _ in range(rng.randint(2, 9))) for _ in range(6000)]
    seqs += list(itertools.product(range(1, 10), repeat=3))
    # bias towards accepted sequences: random all-interval-like walks
    for _ in range(3000):
        v = [rng.randint(1, 9)]
        for _ in range(rng.randint(1, 8)):
            v.append(rng.randint(1, 9))
        seqs.append(tuple(v))
    mism = sum(accepts(A, q) != vs.graceful_ok(q) for q in seqs)
    print(f'graceful NFA: {mism} mismatches in {len(seqs)} sequences ({sum(vs.graceful_ok(q) for q in seqs)} valid)')
    assert mism == 0
    # 2. exact step vs brute force; relaxed walk contains the exact supports
    bad = bad_rel = 0
    for t in range(400):
        L = rng.randint(2, 7); p = rand_path(rng, L)
        pz = vs.Puzzle({'constraints': [{'type': 'graceful', 'cells': [vs.name(a) for a in p]}]})
        lg = vs.Logic(pz)
        doms = [sorted(rng.sample(range(1, 10), rng.randint(2, 9))) for _ in p]
        exp = [set() for _ in p]
        for v in itertools.product(*doms):
            if any(v[i] == v[j] and pz.sees(p[i], p[j]) for i in range(L) for j in range(i)) or not vs.graceful_ok(v):
                continue
            for i, x in enumerate(v):
                exp[i].add(x)
        got, _ = lg._graceful_fills(p, doms)
        rel, _ = lg._graceful_relaxed(p, doms)
        bad += got != exp
        bad_rel += any(not e <= r for e, r in zip(exp, rel))
    print(f'graceful exact step: {bad} mismatches with brute force in 400 lines; relaxed walk unsound in {bad_rel}')
    assert bad == 0 and bad_rel == 0
    # 3. logic soundness with graceful lines + dots + sandwiches
    lost_any = 0; agree = 0
    for i in range(n):
        g = random_grid(2000 + i)
        r2 = random.Random(i)
        cons = []
        tries = 0
        while len(cons) < 4 and tries < 20000:
            tries += 1
            p = rand_path(r2, r2.randint(5, 9))
            if vs.graceful_ok([g[a] for a in p]) and not any(set(p) & set(map(vs.parse, c['cells'])) for c in cons):
                cons.append({'type': 'graceful', 'cells': [vs.name(a) for a in p]})
        for _ in range(r2.randint(0, 6)):
            a = (r2.randrange(9), r2.randrange(8)); b = (a[0], a[1] + 1)
            if r2.random() < 0.5:
                a, b = (a[1], a[0]), (b[1], b[0])
            x, y = g[a], g[b]
            if abs(x - y) == 1:
                cons.append({'type': 'kropki_w', 'cells': [vs.name(a), vs.name(b)]})
            elif x == 2 * y or y == 2 * x:
                cons.append({'type': 'kropki_b', 'cells': [vs.name(a), vs.name(b)]})
        for _ in range(r2.randint(1, 4)):
            pos = r2.choice([f'r0c{k}' for k in range(1, 10)] + [f'r{k}c0' for k in range(1, 10)])
            line = [g[a] for a in vs.outside_line(pos)]
            lo, hi = sorted((line.index(1), line.index(9)))
            cons.append({'type': 'sandwich', 'from': pos, 'sum': sum(line[lo + 1:hi])})
        pz = vs.Puzzle({'constraints': cons})
        assert not pz.check(g), pz.check(g)
        L = vs.Logic(pz)
        res, cand = L.solve(max_tier=2)
        lost = [a for a in g if g[a] not in cand[a]]
        if lost or res == 'contradiction':
            lost_any += 1; print('UNSOUND', i, lost[:5], res)
        # model/checker agreement: random paths on the true grid, graceful or not
        for _ in range(4):
            p = rand_path(r2, r2.randint(3, 9))
            pz2 = vs.Puzzle({'constraints': [{'type': 'graceful', 'cells': [vs.name(a) for a in p]}]})
            m, v = pz2.build_model()
            for x in v:
                m.Add(v[x] == g[x])
            st = cp_model.CpSolver().Solve(m)
            agree += (st in (cp_model.OPTIMAL, cp_model.FEASIBLE)) == (not pz2.check(g)) == vs.graceful_ok([g[a] for a in p])
    print(f'graceful + dots + sandwich logic: true digit lost in {lost_any} of {n} grids; model/checker agree {agree}/{4 * n}')
    assert lost_any == 0 and agree == 4 * n
    # 4. windoku + skyscrapers
    lost_any = 0; agree = 0
    for i in range(n):
        g = random_grid(3000 + i, ['windoku'])
        r2 = random.Random(100 + i)
        cons = []
        for pos in r2.sample([f'r0c{k}' for k in range(1, 10)] + [f'r10c{k}' for k in range(1, 10)] +
                             [f'r{k}c0' for k in range(1, 10)] + [f'r{k}c10' for k in range(1, 10)], r2.randint(4, 14)):
            vals = [g[a] for a in vs.outside_ray(pos)]
            cons.append({'type': 'skyscraper', 'from': pos,
                         'count': sum(1 for j, x in enumerate(vals) if all(x > y for y in vals[:j]))})
        pz = vs.Puzzle({'global': ['windoku'], 'constraints': cons})
        assert not pz.check(g)
        L = vs.Logic(pz)
        res, cand = L.solve(max_tier=2)
        lost = [a for a in g if g[a] not in cand[a]]
        if lost or res == 'contradiction':
            lost_any += 1; print('UNSOUND windoku', i, lost[:5], res)
        g2 = dict(g)
        a = (r2.randrange(9), r2.randrange(9)); b = (a[0], (a[1] + 1 + r2.randrange(8)) % 9)
        if r2.random() < 0.5:  # a swap inside one box keeps rows/columns/boxes valid only sometimes; either way compare
            b = (a[0] // 3 * 3 + r2.randrange(3), a[1])
        g2[a], g2[b] = g2[b], g2[a]
        m, v = pz.build_model()
        for x in v:
            m.Add(v[x] == g2[x])
        st = cp_model.CpSolver().Solve(m)
        agree += (st in (cp_model.OPTIMAL, cp_model.FEASIBLE)) == (not pz.check(g2))
    print(f'windoku + skyscraper logic: true digit lost in {lost_any} of {n} grids; model/checker agree {agree}/{n}')
    assert lost_any == 0 and agree == n
    print('all run-17 soundness tests passed')


if __name__ == '__main__':
    main()
