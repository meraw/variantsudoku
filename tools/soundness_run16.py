"""Run 16 soundness tests.
1. Innies/outies (45 rule): on random grids with random disjoint killer cages (true totals), with or without anti-king,
   the logical solver (now with the innies/outies step) never removes the true digit, and every 45-rule equation it
   builds holds on the true grid.
2. Double arrows: random lines (2-8 inner cells, king steps) that a random grid satisfies; the logical solver (bridge step
   with a sum, including the long-line box-segment relaxation) never removes the true digit, and the CP-SAT model and the
   checker agree on random grids.
python3 soundness_run16.py [grids]"""
import sys, random
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
import vs
from ortools.sat.python import cp_model


def random_grid(seed, glob=()):
    pz = vs.Puzzle({'global': list(glob), 'constraints': []})
    m, v = pz.build_model()
    rng = random.Random(seed)
    m.Minimize(sum(rng.randint(-20, 20) * v[x] for x in v))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 3; s.parameters.random_seed = seed
    assert s.Solve(m) in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    return {x: s.Value(v[x]) for x in v}


def random_cages(g, rng, n_cages):
    free = set(g); cages = []
    for _ in range(400):
        if len(cages) == n_cages:
            break
        a = rng.choice(sorted(free)); cs = [a]
        size = rng.randint(2, 5)
        while len(cs) < size:
            nb = [(x[0] + dr, x[1] + dc) for x in cs for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0))]
            nb = [b for b in nb if b in free and b not in cs and g[b] not in {g[c] for c in cs}]
            if not nb:
                break
            cs.append(rng.choice(nb))
        if len(cs) >= 2:
            cages.append(cs); free -= set(cs)
    return [{'type': 'killer', 'cells': [vs.name(a) for a in cs], 'sum': sum(g[a] for a in cs)} for cs in cages]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    bad = eqs = removed = 0
    for i in range(n):
        glob = ['antiking'] if i % 2 else []
        g = random_grid(1000 + i, glob)
        rng = random.Random(i)
        spec = {'global': glob, 'constraints': random_cages(g, rng, rng.randint(8, 20))}
        pz = vs.Puzzle(spec); L = vs.Logic(pz)
        for plus, minus, tot in L.sum_equations():
            eqs += 1
            assert sum(g[a] for a in plus) - sum(g[a] for a in minus) == tot, (i, plus, minus, tot)
        res, cand = L.solve(max_tier=2)
        removed += sum(1 for _, _, _ in [t for t in L.trace if t[0] == 'innies/outies'])
        lost = [a for a in g if g[a] not in cand[a]]
        if lost or res == 'contradiction':
            bad += 1
            print('UNSOUND', i, lost[:5], res)
    print(f'innies/outies: {n} grids, {eqs} equations all true on the grid, {removed} innies/outies rounds, '
          f'{bad} grids lost a true digit')


def random_path(rng, L):
    r, c = rng.randrange(9), rng.randrange(9)
    p = [(r, c)]
    while len(p) < L:
        nb = [(p[-1][0] + dr, p[-1][1] + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc]
        nb = [b for b in nb if 0 <= b[0] < 9 and 0 <= b[1] < 9 and b not in p]
        if not nb:
            return None
        p.append(rng.choice(nb))
    return p


def doublearrows(n):
    bad = lines = agree = 0
    rng = random.Random(77)
    for i in range(n):
        g = random_grid(2000 + i)
        cons = []
        for _ in range(4000):
            if len(cons) == 6:
                break
            p = random_path(rng, rng.randint(4, 10))
            if p and g[p[0]] + g[p[-1]] == sum(g[a] for a in p[1:-1]) and not any(set(p) & set(vs.parse(x) for x in c['cells']) for c in cons):
                cons.append({'type': 'doublearrow', 'cells': [vs.name(a) for a in p]})
        lines += len(cons)
        pz = vs.Puzzle({'constraints': cons})
        assert not pz.check(g)
        L = vs.Logic(pz); res, cand = L.solve(max_tier=2)
        if any(g[a] not in cand[a] for a in g) or res == 'contradiction':
            bad += 1; print('UNSOUND doublearrow', i)
        # model vs checker on a random (usually violating) grid: fix the grid in the model, compare
        h = random_grid(3000 + i)
        m, v = pz.build_model()
        for a in h:
            m.Add(v[a] == h[a])
        s = cp_model.CpSolver(); feas = s.Solve(m) in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        agree += feas == (not pz.check(h))
        m, v = pz.build_model()
        for a in g:
            m.Add(v[a] == g[a])
        agree += cp_model.CpSolver().Solve(m) in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    print(f'double arrows: {n} grids, {lines} lines, {bad} grids lost a true digit; model/checker agreed {agree}/{2 * n}')


if __name__ == '__main__':
    main()
    doublearrows(int(sys.argv[1]) if len(sys.argv) > 1 else 30)
