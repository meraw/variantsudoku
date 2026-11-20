"""Run 17: open-solution setting of dots between orthogonal neighbours (no target grid), around a kept core of lines.
python3 open_dots.py base.json out.json seed [--types w,b,x,v] [--sep] [--near] [--gthresh N] [--samples N] [--maxmoves N]

A move is a dot (white kropki, black kropki, X or V) on a cell edge that some sampled grid of the current puzzle
satisfies. Moves are scored by the candidates my logical solver (tiers 1-2) removes, one of the best three is
committed after a CP-SAT feasibility check. A given digit is a move only when no dot removes at least --gthresh
candidates (default 1, i.e. only when no dot makes progress). Stops when the tier-2 solve finishes (which proves
uniqueness), then drops every dot and given that is not needed for uniqueness + the tier-2 solve.
--sep: dots never share a cell. --near: both cells of a dot touch (or lie on) a line cell of the base."""
import sys, json, random, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from open_clues import samples, feasible, unique, logic_ok
import open_clues
open_clues.HINT_SAMPLING = True  # the random-objective sampler needs seconds per grid on long graceful lines

argv = [a for i, a in enumerate(sys.argv) if not a.startswith('--') and sys.argv[i - 1] not in ('--types', '--gthresh', '--samples', '--maxmoves')]
base, out, seed = argv[1], argv[2], int(argv[3])
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
TYPES = opt('--types', 'w,b').split(',')
GTH = float(opt('--gthresh', 1))
NS = int(opt('--samples', 30))
MAXM = int(opt('--maxmoves', 150))  # proposals scored per step (a random subset, for speed)
SEP = '--sep' in sys.argv
rnd = random.Random(seed)
spec = json.load(open(base))
for c in spec['constraints']:
    c['keep'] = True
LINE = {parse(x) for c in spec['constraints'] for x in c.get('cells', [])}
NEAR = None
if '--near' in sys.argv:
    NEAR = LINE | {b for a in LINE for b in orth(a)}
EDGES = [((r, k), (r, k + 1)) for r in range(N) for k in range(N - 1)] + [((r, k), (r + 1, k)) for r in range(N - 1) for k in range(N)]
TEST = {'w': lambda a, b: abs(a - b) == 1, 'b': lambda a, b: a == 2 * b or b == 2 * a,
        'x': lambda a, b: a + b == 10, 'v': lambda a, b: a + b == 5}


def con(t, e):
    cells = [name(e[0]), name(e[1])]
    if t in ('w', 'b'):
        return {"type": "kropki_" + t, "cells": cells}
    return {"type": "xv", "cells": cells, "value": t.upper()}


while True:
    pz = Puzzle(spec); L = Logic(pz); cand = L.init_cands(); L.propagate(cand, 2)
    left = sum(len(x) for x in cand.values())
    ndots = sum(1 for c in spec['constraints'] if c['type'] in ('kropki_w', 'kropki_b', 'xv'))
    print('dots', ndots, 'givens', len(spec.get('givens', {})), 'left', left, flush=True)
    if left == 81:
        break
    dotted = {frozenset(map(parse, c['cells'])) for c in spec['constraints'] if c['type'] in ('kropki_w', 'kropki_b', 'xv')}
    dcells = {a for e in dotted for a in e}
    sm = samples(spec, NS, rnd)
    moves = []
    props = []
    for e in EDGES:
        if frozenset(e) in dotted or (SEP and (e[0] in dcells or e[1] in dcells)):
            continue
        if NEAR is not None and not (e[0] in NEAR and e[1] in NEAR):
            continue
        if all(len(cand[a]) == 1 for a in e):
            continue
        for t in TYPES:
            if any(TEST[t](g[e[0]], g[e[1]]) for g in sm):
                props.append((t, e))
    rnd.shuffle(props)
    for t, e in props[:MAXM]:
        if True:
            sp2 = copy.deepcopy(spec); sp2['constraints'].append(con(t, e))
            c2 = {a: set(x) for a, x in cand.items()}
            try:
                Logic(Puzzle(sp2)).propagate(c2, 2)
            except Contradiction:
                continue
            moves.append((left - sum(len(x) for x in c2.values()), rnd.random(), sp2, t, e))
    moves.sort(key=lambda m: (-m[0], m[1]))
    if not moves or moves[0][0] < GTH:
        for a in L.cells:
            if len(cand[a]) < 2:
                continue
            for val in {g[a] for g in sm}:
                c2 = {b: set(x) for b, x in cand.items()}; c2[a] = {val}
                try:
                    Logic(pz).propagate(c2, 2)
                except Contradiction:
                    continue
                sp2 = copy.deepcopy(spec); sp2.setdefault('givens', {})[name(a)] = val
                moves.append(((left - sum(len(x) for x in c2.values())) / 4, rnd.random(), sp2, 'given', (a,)))
        moves.sort(key=lambda m: (-m[0], m[1]))
    top = moves[:3]; rnd.shuffle(top)
    for sc, _, sp2, t, e in top + moves[3:]:
        if feasible(sp2):
            spec = sp2; print('  add', round(sc, 1), t, [name(a) for a in e], flush=True); break
    else:
        print('no feasible move'); sys.exit(1)
assert unique(spec)
i = len(spec['constraints']) - 1
while i >= 0:
    c = spec['constraints'][i]
    if c.get('keep'):
        i -= 1; continue
    sp2 = copy.deepcopy(spec); del sp2['constraints'][i]
    ok, r2 = logic_ok(sp2)
    if ok and unique(sp2):
        print('  drop', c['type'], c['cells'], flush=True); spec = sp2
    i -= 1
for g_ in list(spec.get('givens', {})):
    sp2 = copy.deepcopy(spec); del sp2['givens'][g_]
    ok, r2 = logic_ok(sp2)
    if ok and unique(sp2):
        print('  drop given', g_, flush=True); spec = sp2
ok, r2 = logic_ok(spec)
print('givens', spec.get('givens'))
print('FINAL constraints', len(spec['constraints']), 'tier2', r2, ok)
for c in spec['constraints']:
    c.pop('keep', None)
json.dump(spec, open(out, 'w'), indent=1)
