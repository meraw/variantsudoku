"""Run 5: "open-solution" clue setting for outside sum clues (sandwich), with no target grid.

python3 open_clues.py base.json out.json seed [samples] [topk] [--no-sandwich]

Open clue positions: the 18 sandwich positions (unless --no-sandwich) and every killer cage in the base spec
that has no "sum". When no open clue removes at least GIVEN_THRESHOLD candidates, given digits become moves too.

Repeat until the puzzle is unique and the logical solver (tiers 1-2) finishes:
  1. sample solutions of the current puzzle (CP-SAT, random objectives) and collect, for every row/column
     without a clue, the sandwich totals that still occur;
  2. score each (position, total) move by how many candidates the logical solver removes from the current
     fixpoint when that clue is added (a contradiction = impossible move);
  3. pick at random among the `topk` best, confirm with CP-SAT that the clue is still satisfiable, commit.
Finally drop every clue that is not needed for uniqueness + a tier-2 logical solve (latest clues tried first).
This is how a setter picks "the clue that would force something here": the solution is decided by the clues,
not the other way round."""
import sys, json, random, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from ortools.sat.python import cp_model

GIVEN_THRESHOLD = 15
OPEN_SANDWICH = '--no-sandwich' not in sys.argv
POS = [f"r0c{k}" for k in range(1, 10)] + [f"r{k}c0" for k in range(1, 10)]


def sand(vals):
    i, j = sorted((vals.index(1), vals.index(9)))
    return sum(vals[i + 1:j])


def samples(spec, n, rnd):
    pz = Puzzle(spec)
    out = []
    for _ in range(n):
        m, v = pz.build_model()
        m.Minimize(sum(rnd.randint(-9, 9) * v[a] for a in v))
        s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 0.4; s.parameters.num_workers = 2
        s.parameters.random_seed = rnd.randrange(10 ** 6)
        st = s.Solve(m)
        if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):  # tight puzzles: allow longer to find any solution
            s.parameters.max_time_in_seconds = 10
            st = s.Solve(m)
        if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            out.append({a: s.Value(v[a]) for a in v})
    return out


def line_of(pos):
    return outside_line(pos)


def logic_state(spec):
    L = Logic(Puzzle(spec)); cand = L.init_cands(); L.propagate(cand, 2)
    return cand


def logic_ok(spec):
    L = Logic(Puzzle(spec)); res, _ = L.solve(max_tier=2)
    return res == 'solved', L.tier_counts[2]


def feasible(spec):
    sols, st = Puzzle(spec).count_solutions(limit=1, time_limit=60)
    return len(sols) == 1


def unique(spec):
    sols, st = Puzzle(spec).count_solutions(limit=2, time_limit=120)
    return len(sols) == 1 and st == 'OPTIMAL'


def main():
    argv = [a for a in sys.argv if not a.startswith('--')]
    base, out, seed = argv[1], argv[2], int(argv[3])
    ns = int(argv[4]) if len(argv) > 4 else 20
    topk = int(argv[5]) if len(argv) > 5 else 3
    rnd = random.Random(seed)
    spec = json.load(open(base))
    spec.setdefault('constraints', [])
    used = {c['from'] for c in spec['constraints'] if c['type'] == 'sandwich'}
    while True:
        cand = logic_state(spec)
        left = sum(len(x) for x in cand.values())
        print('clues', len(used), 'candidates left', left, flush=True)
        if left == 81:
            break
        sm = samples(spec, ns, rnd)
        moves = []
        # sum-less killer cages are open clues too: their total is chosen like a sandwich value
        for ci, c in enumerate(spec['constraints']):
            if c['type'] == 'killer' and 'sum' not in c:
                for val in {sum(g[parse(x)] for x in c['cells']) for g in sm}:
                    c2 = {a: set(x) for a, x in cand.items()}
                    sp2 = copy.deepcopy(spec); sp2['constraints'][ci]['sum'] = val
                    try:
                        Logic(Puzzle(sp2)).propagate(c2, 2)
                    except Contradiction:
                        continue
                    moves.append((left - sum(len(x) for x in c2.values()), f'K{ci}', val))
        for p in (POS if OPEN_SANDWICH else []):
            if p in used:
                continue
            vals = {sand([g[a] for a in line_of(p)]) for g in sm}
            for val in vals:
                c2 = {a: set(x) for a, x in cand.items()}
                sp2 = copy.deepcopy(spec); sp2['constraints'].append({"type": "sandwich", "from": p, "sum": val})
                L = Logic(Puzzle(sp2))
                try:
                    L.propagate(c2, 2)
                except Contradiction:
                    continue
                moves.append((left - sum(len(x) for x in c2.values()), p, val))
        moves.sort(reverse=True)
        if not moves or moves[0][0] < GIVEN_THRESHOLD:
            # sandwich clues have run out of steam (typically a 2-8 deadly pattern they cannot see): allow a given
            for a in Logic(Puzzle(spec)).cells:
                if len(cand[a]) < 2:
                    continue
                for val in {g[a] for g in sm}:
                    c2 = {b: set(x) for b, x in cand.items()}; c2[a] = {val}
                    try:
                        Logic(Puzzle(spec)).propagate(c2, 2)
                    except Contradiction:
                        continue
                    moves.append((left - sum(len(x) for x in c2.values()), 'G' + name(a), val))
            moves.sort(reverse=True)
        pick = None
        for sc, p, val in rnd.sample(moves[:topk], min(topk, len(moves))) + moves[topk:]:
            sp2 = copy.deepcopy(spec)
            if p.startswith('G'):
                sp2.setdefault('givens', {})[p[1:]] = val
            elif p.startswith('K'):
                sp2['constraints'][int(p[1:])]['sum'] = val
            else:
                sp2['constraints'].append({"type": "sandwich", "from": p, "sum": val})
            if feasible(sp2):
                pick = (sc, p, val); spec = sp2; break
        print('  add', pick, flush=True)
        used.add(pick[1])
    assert unique(spec)
    # prune: newest clues first
    i = len(spec['constraints']) - 1
    while i >= 0:
        c = spec['constraints'][i]
        if c['type'] == 'sandwich':
            sp2 = copy.deepcopy(spec); del sp2['constraints'][i]
            ok, r2 = logic_ok(sp2)
            if ok and unique(sp2):
                print('  drop', c['from'], c['sum'], flush=True)
                spec = sp2
        i -= 1
    for a in list(spec.get('givens', {})):
        sp2 = copy.deepcopy(spec); del sp2['givens'][a]
        ok, r2 = logic_ok(sp2)
        if ok and unique(sp2):
            print('  drop given', a, flush=True)
            spec = sp2
    ok, r2 = logic_ok(spec)
    print('FINAL givens', len(spec.get('givens', {})), 'clues', sum(c['type'] == 'sandwich' for c in spec['constraints']), 'tier2 rounds', r2)
    json.dump(spec, open(out, 'w'), indent=1)


if __name__ == '__main__':
    main()
