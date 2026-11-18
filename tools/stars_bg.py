"""Run 15: background counting circles ("faint stars") for a fixed picture of lines + circles.
python3 stars_bg.py base.json out.json seed [--maxbg N] [--noadj] [--first]
base: lines + one counting constraint (the picture's stars, kept). Finds a target grid G (CP-SAT, random objective, with
background stars free), then picks the fewest background stars (on cells off the lines and not touching a picture star;
--noadj: not touching each other either) that make the counting rule hold in G.
--first: write that spec and stop (used for 029, whose base alone is infeasible; other clues then finish it).
Without --first it continues CEGAR-style: it adds every alternative solution CP-SAT finds as a grid the star set must
FAIL in, and re-picks, until the puzzle is unique. (Run 15: this never got anywhere on Orion, because the alternative
solutions differed only in cells no star set could reach.)"""
import sys, json, random, itertools, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from ortools.sat.python import cp_model
base, out, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
MAXBG = int(sys.argv[sys.argv.index('--maxbg') + 1]) if '--maxbg' in sys.argv else 12
NOADJ = '--noadj' in sys.argv
rnd = random.Random(seed)
spec = json.load(open(base))
cons = [c for c in spec['constraints'] if c['type'] != 'counting']
stars0 = [parse(x) for c in spec['constraints'] if c['type'] == 'counting' for x in c['cells']]
online = {parse(x) for c in cons for x in c.get('cells', [])}
cells = [(r, k) for r in range(9) for k in range(9)]
def nb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1])) <= 1
allowed = [a for a in cells if a not in online and a not in stars0 and not any(nb(a, b) for b in stars0)]
print('allowed bg cells', len(allowed))
def eqb(m, var, d):
    b = m.NewBoolVar(''); m.Add(var == d).OnlyEnforceIf(b); m.Add(var != d).OnlyEnforceIf(b.Not()); return b
def target():
    pz = Puzzle({'constraints': cons, 'givens': spec.get('givens', {})}); m, v = pz.build_model()
    x = {a: m.NewBoolVar('') for a in allowed}
    if NOADJ:
        for a, b in itertools.combinations(allowed, 2):
            if nb(a, b): m.AddBoolOr([x[a].Not(), x[b].Not()])
    m.Add(sum(x.values()) <= MAXBG)
    for d in DIGITS:
        bs = [eqb(m, v[a], d) for a in stars0]
        for a in allowed:
            b = eqb(m, v[a], d); y = m.NewBoolVar('')
            m.AddBoolAnd([b, x[a]]).OnlyEnforceIf(y); m.AddBoolOr([b.Not(), x[a].Not()]).OnlyEnforceIf(y.Not()); bs.append(y)
        u = m.NewBoolVar(''); m.Add(sum(bs) == d * u)
    m.Maximize(sum(rnd.randint(-9, 9) * v[a] for a in v))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 20; s.parameters.num_workers = 8; s.parameters.random_seed = rnd.randint(0, 999)
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    return {a: s.Value(v[a]) for a in v}
def counts_ok_expr(m, x, grid):
    """bool that is true iff the star set (stars0 + chosen x) satisfies counting in grid"""
    oks = []
    for d in DIGITS:
        c0 = sum(1 for a in stars0 if grid[a] == d)
        terms = [x[a] for a in allowed if grid[a] == d]
        cnt = m.NewIntVar(0, 81, ''); m.Add(cnt == c0 + sum(terms))
        ok = m.NewBoolVar('')
        # ok <=> cnt in {0, d}
        z = m.NewBoolVar(''); w = m.NewBoolVar('')
        m.Add(cnt == 0).OnlyEnforceIf(z); m.Add(cnt != 0).OnlyEnforceIf(z.Not())
        m.Add(cnt == d).OnlyEnforceIf(w); m.Add(cnt != d).OnlyEnforceIf(w.Not())
        m.AddBoolOr([z, w]).OnlyEnforceIf(ok); m.AddBoolAnd([z.Not(), w.Not()]).OnlyEnforceIf(ok.Not())
        oks.append(ok)
    allok = m.NewBoolVar(''); m.AddBoolAnd(oks).OnlyEnforceIf(allok); m.AddBoolOr([o.Not() for o in oks]).OnlyEnforceIf(allok.Not())
    return allok
for attempt in range(30):
    G = target()
    if G is None:
        print('no target'); sys.exit()
    alts = []
    while True:
        m = cp_model.CpModel(); x = {a: m.NewBoolVar('') for a in allowed}
        if NOADJ:
            for a, b in itertools.combinations(allowed, 2):
                if nb(a, b): m.AddBoolOr([x[a].Not(), x[b].Not()])
        m.Add(sum(x.values()) <= MAXBG)
        m.Add(counts_ok_expr(m, x, G) == 1)
        for H in alts:
            m.Add(counts_ok_expr(m, x, H) == 0)
        m.Minimize(100 * sum(x.values()) + sum(rnd.randint(0, 50) * x[a] for a in allowed))
        s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 60; s.parameters.num_workers = 8
        st = s.Solve(m)
        if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            print('attempt', attempt, 'no star set after', len(alts), 'alts'); break
        B = [a for a in allowed if s.Value(x[a])]
        sp = copy.deepcopy(spec)
        for c in sp['constraints']:
            if c['type'] == 'counting':
                c['cells'] = [name(a) for a in stars0 + B]
        if '--first' in sys.argv:
            json.dump(sp, open(out, 'w'), indent=1)
            print(grid_str(G)); print('bg', [name(a) for a in B], 'digits', sorted(G[a] for a in stars0 + B)); sys.exit()
        sols, st2 = Puzzle(sp).count_solutions(limit=2, time_limit=60)
        if len(sols) == 1 and st2 == 'OPTIMAL':
            L = Logic(Puzzle(sp)); r, _ = L.solve(max_tier=3)
            print('UNIQUE with', len(B), 'bg stars; logic', r, L.tier_counts, flush=True)
            json.dump(sp, open(out, 'w'), indent=1)
            sys.exit()
        H = sols[0] if sols[0] != G else sols[1]
        alts.append(H)
        print('  alts', len(alts), 'bg', len(B), flush=True)
