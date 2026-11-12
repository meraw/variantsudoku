"""Run 9: checks for factor lines, jigsaw regions and the law-of-leftovers step.
1. the binary-lookup table sent to Rangsk for factor lines decodes (as BinaryLookupConstraint.DecodeTable does) to exactly
   the factor relation;
2. seqs_nfa accepts exactly the sequences it was built from (random factor-line shapes, decoded with run 8's reader);
3. factor-line logic never removes the true digit: random grids, random satisfied factor lines + random little killers;
4. jigsaw: random grids of the run-9 jigsaw (CP-SAT, random objective) with random skyscraper clues and a few givens, run to
   the tier-2 fixpoint (which includes the leftovers step): the true digit is never removed;
5. CP-SAT model vs checker on random (factor line, grid) pairs."""
import sys, random, base64, struct, json
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from nfa import seqs_nfa
from soundness_run8 import decode, accepts, rand_grid, rpath  # noqa: E402 (prints the run-7/8 summaries too)
from rangsk import pair_table, line_fills

print('--- run 9 ---')
t = pair_table('factor')
by = base64.urlsafe_b64decode(t + '=' * (-len(t) % 4))
tab = struct.unpack('<9I', by)
ok = all(bool(tab[v - 1] >> (w - 1) & 1) == PAIR_REL['factor'](v, w) for v in DIGITS for w in DIGITS)
print('factor binary-lookup table matches the relation:', ok)

rnd = random.Random(9)
mism = 0; nl = 0
for _ in range(30):
    p = rpath(rnd.randint(2, 6))
    if not p:
        continue
    c = {'type': 'factor', 'cells': [name(a) for a in p]}
    pz = Puzzle({'constraints': [c]})
    fills = line_fills(pz, pz.cons[0])
    nfa = decode(seqs_nfa(fills))
    fs = set(fills)
    for _ in range(300):
        v = tuple(rnd.choice(fills)) if rnd.random() < 0.5 else tuple(rnd.randint(1, 9) for _ in p)
        mism += accepts(nfa, v) != (v in fs)
    nl += 1
print(f'seqs_nfa on {nl} random factor lines: mismatches {mism}')

bad = tested = agree = total = 0
for gi in range(40):
    g = rand_grid(2000 + gi)
    cons = []
    for _ in range(3000):
        p = rpath(rnd.randint(3, 6))
        if p and all(PAIR_REL['factor'](g[a], g[b]) for a, b in zip(p, p[1:])):
            cons.append({'type': 'factor', 'cells': [name(a) for a in p]})
    cons = rnd.sample(cons, min(len(cons), 10))
    for _ in range(3):
        frm, d = rnd.choice([(f"r0c{k}", 'DR') for k in range(0, 7)] + [(f"r0c{k}", 'DL') for k in range(3, 11)])
        cells = lk_cells(frm, d)
        cons.append({'type': 'littlekiller', 'from': frm, 'dir': d, 'sum': sum(g[a] for a in cells)})
    givens = {name(a): g[a] for a in rnd.sample(sorted(g), rnd.randint(0, 6))}
    pz = Puzzle({'constraints': cons, 'givens': givens})
    assert pz.check(g) == [], pz.check(g)
    L = Logic(pz); cand = L.init_cands()
    try:
        L.propagate(cand, 2); tested += 1
        bad += any(g[a] not in cand[a] for a in cand)
    except Contradiction:
        bad += 1
    for j, c in enumerate([c for c in cons if c['type'] == 'factor'][:10]):
        h = g if j % 2 else rand_grid(rnd.randrange(10 ** 6))
        p1 = Puzzle({'constraints': [c]})
        ok_checker = p1.check(h) == []
        m, v = p1.build_model()
        for a, d in h.items():
            m.Add(v[a] == d)
        s = cp_model.CpSolver(); st = s.Solve(m)
        total += 1; agree += ok_checker == (st in (cp_model.OPTIMAL, cp_model.FEASIBLE))
print(f'factor/little-killer logic soundness: {tested} grids at fixpoint, true digit removed in {bad}')
print(f'factor model vs checker: {agree}/{total} agree')

REG = ["000111222", "000012222", "030111252", "333414555", "333414555", "363444585", "666747888", "667747788", "666777888"]
bad = tested = 0
for gi in range(30):
    pz0 = Puzzle({'regions': REG, 'constraints': []})
    m, v = pz0.build_model()
    m.Minimize(sum(rnd.randint(-9, 9) * v[a] for a in v))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 2; s.parameters.random_seed = gi
    s.Solve(m)
    g = {a: s.Value(v[a]) for a in v}
    cons = []
    for frm in rnd.sample([f"r0c{k}" for k in range(1, 10)] + [f"r10c{k}" for k in range(1, 10)] +
                          [f"r{k}c0" for k in range(1, 10)] + [f"r{k}c10" for k in range(1, 10)], 8):
        ray = [g[a] for a in outside_ray(frm)]
        cons.append({'type': 'skyscraper', 'from': frm, 'count': sum(1 for i, x in enumerate(ray) if all(x > y for y in ray[:i]))})
    givens = {name(a): g[a] for a in rnd.sample(sorted(g), rnd.randint(0, 8))}
    pz = Puzzle({'regions': REG, 'constraints': cons, 'givens': givens})
    assert pz.check(g) == [], pz.check(g)
    L = Logic(pz); cand = L.init_cands()
    try:
        L.propagate(cand, 2); tested += 1
        bad += any(g[a] not in cand[a] for a in cand)
    except Contradiction:
        bad += 1
print(f'jigsaw + skyscrapers (incl. leftovers): {tested} grids at fixpoint, true digit removed in {bad}; leftover pairs used: {len(L._leftover_pairs)}')
