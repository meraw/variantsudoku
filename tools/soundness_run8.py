"""Run 8: checks for the new pendulum line (invented), palindromes and the compass arrows.
1. pendulum_nfa (for Rangsk's solver) accepts exactly the sequences pendulum_ok accepts, for every length 2-5
   (decoded with a small reader of the serialized format written by nfa.serialize);
2. the pendulum logic step never removes the true digit: random grids, random satisfied pendulum lines (plus
   palindromes), the logical solver run to its fixpoint from a few random givens;
3. CP-SAT model vs checker agreement on random (line, grid) pairs."""
import sys, random, itertools, base64
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from nfa import pendulum_nfa
from soundness_run7 import rand_grid, rpath  # noqa: E402  (importing runs the run-7 tests too; they print their own summary)


def decode(s):
    by = base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))
    bits = ''.join(f'{b:08b}' for b in by); pos = [0]

    def get(n):
        v = int(bits[pos[0]:pos[0] + n], 2) if n else 0; pos[0] += n; return v
    assert get(2) == 0
    sb = get(4) + 1; nsym = get(4) + 1
    nstart = get(sb); nacc = get(sb)
    sia = get(nstart)
    tcb = get(4)
    # number of states is not stored: read until the bits run out (padding < 8 bits)
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


nfa = decode(pendulum_nfa(5))
for L in range(2, 6):
    mism = [v for v in itertools.product(DIGITS, repeat=L) if accepts(nfa, v) != pendulum_ok(v)]
    print(f'pendulum NFA, length {L}: {len(PENDULUM_SEQS[L])} valid sequences, mismatches {len(mism)}')

rnd = random.Random(8)
bad = tested = agree = total = 0
for gi in range(40):
    g = rand_grid(1000 + gi)
    cons = []
    for _ in range(3000):
        p = rpath(rnd.randint(3, 5))
        if not p:
            continue
        v = [g[a] for a in p]
        if pendulum_ok(v):
            cons.append({'type': 'pendulum', 'cells': [name(a) for a in p]})
        if v == v[::-1]:
            cons.append({'type': 'palindrome', 'cells': [name(a) for a in p]})
    cons = rnd.sample(cons, min(len(cons), 12))
    givens = {name(a): g[a] for a in rnd.sample(sorted(g), rnd.randint(0, 6))}
    pz = Puzzle({'constraints': cons, 'givens': givens})
    assert pz.check(g) == [], pz.check(g)
    L = Logic(pz); cand = L.init_cands()
    try:
        L.propagate(cand, 2)
        tested += 1
        if any(g[a] not in cand[a] for a in cand):
            bad += 1
    except Contradiction:
        bad += 1
    # model/checker agreement: a random grid either satisfies a random line or not, and CP-SAT must agree
    for j, c in enumerate(cons[:10]):
        h = g if j % 2 else rand_grid(rnd.randrange(10 ** 6))  # half the checks on the grid that satisfies the line
        p1 = Puzzle({'constraints': [c]})
        ok_checker = p1.check(h) == []
        m, v = p1.build_model()
        for a, d in h.items():
            m.Add(v[a] == d)
        s = cp_model.CpSolver(); st = s.Solve(m)
        ok_model = st in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        total += 1; agree += ok_checker == ok_model
print(f'pendulum/palindrome logic soundness: {tested} grids at fixpoint, true digit removed in {bad}')
print(f'model vs checker: {agree}/{total} agree (half of them on grids that satisfy the line)')
