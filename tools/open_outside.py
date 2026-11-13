"""Run 6: open-solution setting for outside clues (X-sums, skyscrapers, sandwiches), no target grid.

python3 open_outside.py base.json out.json seed [--types xsum,skyscraper] [--sym] [--samples N] [--topk K]
                        [--bonus skyscraper=1.6] [--mixpairs]

Like open_clues.py (run 5), but for clues read from a direction. Every one of the 36 outside positions can
hold at most one clue. A move is (position, type, value), or with --sym a pair of 180-degree-opposite positions
with the same clue type (values may differ; only value pairs that occur together in a sampled grid are tried).
  1. sample grids that satisfy the clues so far (CP-SAT, random objectives);
  2. score every still-possible move by the candidates the logical solver (tiers 1-2) then removes;
  3. pick one of the top K, confirm satisfiable with CP-SAT, commit.
--bonus multiplies the score of one clue type (plain candidate counts favour X-sums, which say more per clue);
--mixpairs lets the two clues of a symmetric pair have different types.
When no clue move removes at least GIVEN_THRESHOLD candidates, single givens become moves as well.
Stops when the logical solver finishes (which proves uniqueness), then drops clues (pairs) and givens that are
not needed for uniqueness + a tier-2 logical solve, newest first."""
import sys, json, random, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from open_clues import samples, logic_ok, unique, feasible

GIVEN_THRESHOLD = 12
POS = [f"r0c{k}" for k in range(1, 10)] + [f"r10c{k}" for k in range(1, 10)] + \
      [f"r{k}c0" for k in range(1, 10)] + [f"r{k}c10" for k in range(1, 10)]
KEY = {'xsum': 'sum', 'skyscraper': 'count', 'sandwich': 'sum', 'frog': 'sum'}


def opt(name_, default):
    return sys.argv[sys.argv.index(name_) + 1] if name_ in sys.argv else default


def side(p):
    r, k = parse(p)
    return 'T' if r < 0 else 'B' if r > 8 else 'L' if k < 0 else 'R'


def rot_pos(p):
    r, k = parse(p)
    return f"r{(8 - r) + 1}c{(8 - k) + 1}"


def clue_value(typ, p, g):
    vals = [g[a] for a in (outside_ray(p) if typ != 'sandwich' else outside_line(p))]
    if typ == 'frog':
        return frog_sum(vals)
    if typ == 'xsum':
        return sum(vals[:vals[0]])
    if typ == 'skyscraper':
        return sum(1 for i, x in enumerate(vals) if all(x > y for y in vals[:i]))
    i, j = sorted((vals.index(1), vals.index(9)))
    return sum(vals[i + 1:j])


def trivial(typ, val):
    """clues that are just a given digit in disguise (skyscraper 1 = a 9 in the first cell, 9 = 1..9 in order;
    X-sum 1 = a 1 in the first cell, X-sum 45 = a 9 there) are never offered"""
    return (typ == 'skyscraper' and val in (1, 9)) or (typ == 'xsum' and val in (1, 45)) or (typ == 'frog' and val == 17)


def mk(typ, p, val):
    return {"type": typ, "from": p, KEY[typ]: val}


def main():
    argv = [a for i, a in enumerate(sys.argv) if not a.startswith('--') and not (i > 0 and sys.argv[i - 1] in ('--types', '--samples', '--topk', '--bonus', '--gthresh', '--sides'))]
    global GIVEN_THRESHOLD, POS
    GIVEN_THRESHOLD = float(opt('--gthresh', GIVEN_THRESHOLD))  # run 10: 1 = givens only when no clue makes progress
    sides = opt('--sides', 'TBLR')  # run 10: restrict clue positions to some sides (T = above, B = below, L, R)
    POS = [p for p in POS if side(p) in sides]
    base, out, seed = argv[1], argv[2], int(argv[3])
    types = opt('--types', 'xsum,skyscraper').split(',')
    ns, topk = int(opt('--samples', 24)), int(opt('--topk', 3))
    sym = '--sym' in sys.argv
    bonus = {}
    if '--bonus' in sys.argv:
        for kv in opt('--bonus', '').split(','):
            k_, v_ = kv.split('='); bonus[k_] = float(v_)
    tpairs = [(a, b) for a in types for b in types] if '--mixpairs' in sys.argv else [(a, a) for a in types]
    rnd = random.Random(seed)
    spec = json.load(open(base)); spec.setdefault('constraints', [])
    while True:
        L = Logic(Puzzle(spec)); cand = L.init_cands()
        L.propagate(cand, 2)
        left = sum(len(x) for x in cand.values())
        used = {c['from'] for c in spec['constraints'] if 'from' in c}
        print('clues', len(used), 'givens', len(spec.get('givens', {})), 'candidates left', left, flush=True)
        if left == 81:
            break
        sm = samples(spec, ns, rnd)
        moves = []
        groups = []
        for p in POS:
            if p in used:
                continue
            if sym:
                q = rot_pos(p)
                if q in used or q < p:
                    continue
                for ta, tb in tpairs:
                    for vv in {(clue_value(ta, p, g), clue_value(tb, q, g)) for g in sm}:
                        if not (trivial(ta, vv[0]) or trivial(tb, vv[1])):
                            groups.append([mk(ta, p, vv[0]), mk(tb, q, vv[1])])
            else:
                for typ in types:
                    for v_ in {clue_value(typ, p, g) for g in sm}:
                        if not trivial(typ, v_):
                            groups.append([mk(typ, p, v_)])
        for grp in groups:
            sp2 = copy.deepcopy(spec); sp2['constraints'] += grp
            c2 = {a: set(x) for a, x in cand.items()}
            try:
                Logic(Puzzle(sp2)).propagate(c2, 2)
            except Contradiction:
                continue
            w = sum(bonus.get(c['type'], 1.0) for c in grp) / len(grp)
            moves.append(((left - sum(len(x) for x in c2.values())) * w, rnd.random(), sp2, grp))
        moves.sort(key=lambda t: (-t[0], t[1]))
        if not moves or moves[0][0] < GIVEN_THRESHOLD:
            for a in L.cells:
                if len(cand[a]) < 2:
                    continue
                for val in {g[a] for g in sm}:
                    c2 = {b: set(x) for b, x in cand.items()}; c2[a] = {val}
                    try:
                        Logic(Puzzle(spec)).propagate(c2, 2)
                    except Contradiction:
                        continue
                    sp2 = copy.deepcopy(spec); sp2.setdefault('givens', {})[name(a)] = val
                    moves.append((left - sum(len(x) for x in c2.values()), rnd.random(), sp2, [name(a) + '=' + str(val)]))
            moves.sort(key=lambda t: (-t[0], t[1]))
        top = moves[:topk]; rnd.shuffle(top)
        for sc, _, sp2, grp in top + moves[topk:]:
            if feasible(sp2):
                spec = sp2
                print('  add', sc, grp, flush=True)
                break
        else:
            print('no feasible move'); return
    assert unique(spec)
    # prune newest first (pairs together when --sym)
    i = len(spec['constraints']) - 1
    while i >= 0:
        c = spec['constraints'][i]
        if 'from' not in c or c.get('keep'):
            i -= 1; continue
        idx = [i]
        if sym:
            q = rot_pos(c['from'])
            idx += [j for j, d in enumerate(spec['constraints']) if d.get('from') == q and j != i]
        sp2 = copy.deepcopy(spec)
        sp2['constraints'] = [d for j, d in enumerate(spec['constraints']) if j not in idx]
        ok, r2 = logic_ok(sp2)
        if ok and unique(sp2):
            print('  drop', [spec['constraints'][j] for j in idx], flush=True)
            spec = sp2
            i = min(i, len(spec['constraints'])) - 1
        else:
            i -= 1
    for a in list(spec.get('givens', {})):
        sp2 = copy.deepcopy(spec); del sp2['givens'][a]
        ok, r2 = logic_ok(sp2)
        if ok and unique(sp2):
            print('  drop given', a, flush=True); spec = sp2
    ok, r2 = logic_ok(spec)
    print('FINAL givens', len(spec.get('givens', {})), 'clues', sum('from' in c for c in spec['constraints']),
          'tier2 rounds', r2, 'solved', ok)
    json.dump(spec, open(out, 'w'), indent=1)


if __name__ == '__main__':
    main()
