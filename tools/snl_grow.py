"""Run 14: open-solution growth of "snakes" (wiggly region-sum lines) and "ladders" (a stack of kropki dots on
neighbouring pairs, like rungs) around a kept core, with no target grid.

python3 snl_grow.py base.json out.json seed [--sym] [--nogivens] [--snakelen 5,8] [--ladlen 2,4] [--bonus snake=1,ladder=1]

The base spec's constraints are kept. A base spec may also list "ladders": [[[a, b], ...], ...] = rung positions whose
colours are not chosen yet; they are placed first, each with the colouring (taken from a sampled solution) that lets
my logical solver remove the most candidates. After that every round:
  1. sample solutions of the current puzzle;
  2. propose snakes (king-step paths whose every step is within 45 degrees of one heading and that never run straight
     for more than two steps, so they wiggle; they must cross a box border) and ladders (2-5 rungs stacked across one
     column border or one row border), on cells no other snake or ladder uses; colours and fits come from the samples;
  3. score each by the candidates the logical solver (tiers 1-2) removes, divided by 1 + 0.08 x cells;
     with --sym a move comes together with its 180-degree rotation;
  4. take one of the best three after a CP-SAT feasibility check.
A given is a penalised fallback (unless --nogivens) when no move removes at least 5 candidates.
Stops when the tier-2 solve finishes, then drops unneeded snakes/ladders (newest first) and trims ladder end rungs."""
import sys, json, random, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from open_clues import samples, feasible, unique, logic_ok
from open_lines import segs_of, crosses

argv = [a for i, a in enumerate(sys.argv) if not a.startswith('--') and not sys.argv[i - 1] in ('--bonus', '--snakelen', '--ladlen')]
base, out, seed = argv[1], argv[2], int(argv[3])
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
SN = tuple(map(int, opt('--snakelen', '5,8').split(',')))
LD = tuple(map(int, opt('--ladlen', '2,5').split(',')))
BON = {k: float(v) for k, v in (kv.split('=') for kv in opt('--bonus', 'snake=1,ladder=1').split(','))}
SYM = '--sym' in sys.argv
GIVENS = '--nogivens' not in sys.argv
rnd = random.Random(seed)
spec = json.load(open(base))
pending = spec.pop('ladders', [])
for c in spec['constraints']:
    c['keep'] = True
H8 = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]


def rot(a):
    return (8 - a[0], 8 - a[1])


def elem_cells(spec):
    used = set()
    for c in spec['constraints']:
        used |= {parse(x) for x in c['cells']}
    return used


def diag_steps(spec):
    return [d for c in spec['constraints'] if c['type'] == 'regionsum' for d in segs_of([parse(x) for x in c['cells']])]


def rs_segs(p):
    segs = [[0]]
    for i in range(1, len(p)):
        (segs[-1].append(i) if box(p[i]) == box(p[i - 1]) else segs.append([i]))
    return segs


def snake_path():
    L = rnd.randint(*SN)
    h = rnd.randrange(8)
    p = [(rnd.randrange(9), rnd.randrange(9))]
    run = 0
    last = None
    while len(p) < L:
        d = H8[(h + rnd.choice((-1, 0, 1))) % 8]
        run = run + 1 if d == last else 1
        if run > 2:
            return None
        n = (p[-1][0] + d[0], p[-1][1] + d[1])
        if not (0 <= n[0] < 9 and 0 <= n[1] < 9) or n in p:
            return None
        if len(p) >= 2 and max(abs(n[0] - p[-2][0]), abs(n[1] - p[-2][1])) <= 1:
            return None  # no tight hooks: the line must not come back next to the cell before last
        p.append(n); last = d
    if len({box(a) for a in p}) < 2:
        return None
    if all(a[0] == p[0][0] for a in p) or all(a[1] == p[0][1] for a in p):
        return None  # a straight line is not a snake
    return p


def ladder_pos():
    L = rnd.randint(*LD)
    if rnd.random() < 0.5:  # rungs across the border between columns c and c+1, rows r..r+L-1
        r, c = rnd.randrange(10 - L), rnd.randrange(8)
        return [((r + i, c), (r + i, c + 1)) for i in range(L)]
    r, c = rnd.randrange(8), rnd.randrange(10 - L)
    return [((r, c + i), (r + 1, c + i)) for i in range(L)]


def colour(g, a, b):
    x, y = g[a], g[b]
    if abs(x - y) == 1:
        return 'kropki_w'
    if x == 2 * y or y == 2 * x:
        return 'kropki_b'
    return None


def ladder_cons(rungs, g, lid):
    out = []
    for a, b in rungs:
        t = colour(g, a, b)
        if t is None:
            return None
        out.append({"type": t, "cells": [name(a), name(b)], "ladder": lid})
    return out


def score(sp2, cand, left):
    c2 = {a: set(x) for a, x in cand.items()}
    try:
        Logic(Puzzle(sp2)).propagate(c2, 2)
    except Contradiction:
        return None
    return left - sum(len(x) for x in c2.values())


nlad = 1 + max([c.get('ladder', 0) for c in spec['constraints']] + [0])
while True:
    pz = Puzzle(spec); L = Logic(pz); cand = L.init_cands(); L.propagate(cand, 2)
    left = sum(len(x) for x in cand.values())
    print('elements', len(spec['constraints']), 'left', left, flush=True)
    if left == 81 and not pending:
        break
    sm = samples(dict(spec, constraints=spec['constraints'] + [{"type": "kropki_any", "cells": list(ab)} for ld in pending for ab in ld]), 30, rnd)
    used = elem_cells(spec); diag = diag_steps(spec)
    moves = []
    if pending:  # core ladders first: try the colourings seen in the samples
        rungs = [(parse(a), parse(b)) for a, b in pending[0]]
        seen = set()
        for g in sm:
            cs = ladder_cons(rungs, g, nlad)
            if cs and tuple(c['type'] for c in cs) not in seen:
                seen.add(tuple(c['type'] for c in cs))
                moves.append(('ladder', cs))
    else:
        tries = 0
        seen = set()
        while len(moves) < 300 and tries < 300000:
            tries += 1
            g = rnd.choice(sm)  # every proposal is fitted to one sampled solution
            if rnd.random() < 0.5:
                p = snake_path()
                if not p:
                    continue
                ps = [p] + ([[rot(a) for a in p]] if SYM else [])
                allc = [a for q in ps for a in q]
                if len(set(allc)) < len(allc) or set(allc) & used:
                    continue
                if not all(len({sum(g[q[i]] for i in sg) for sg in rs_segs(q)}) == 1 for q in ps):
                    continue
                if any(crosses(x, y) for q in ps for x in segs_of(q) for y in diag) or \
                        SYM and any(crosses(x, y) for x in segs_of(ps[0]) for y in segs_of(ps[1])):
                    continue
                key = tuple(map(tuple, ps))
                if key in seen:
                    continue
                seen.add(key)
                moves.append(('snake', [{"type": "regionsum", "cells": [name(a) for a in q]} for q in ps]))
            else:
                rungs = ladder_pos()
                rs = [rungs] + ([[(rot(a), rot(b)) for a, b in rungs]] if SYM else [])
                allc = [x for q in rs for ab in q for x in ab]
                if len(set(allc)) < len(allc) or set(allc) & used:
                    continue
                k = 0  # the longest run of rungs from the start that the sample fits (in both copies with --sym)
                while k < len(rungs) and all(colour(g, *q[k]) for q in rs):
                    k += 1
                if k < 2:
                    continue
                cs = [ladder_cons(q[:k], g, nlad + i) for i, q in enumerate(rs)]
                if all(cs):
                    key = tuple((c['type'], tuple(c['cells'])) for q in cs for c in q)
                    if key in seen:
                        continue
                    seen.add(key)
                    moves.append(('ladder', [c for q in cs for c in q]))
        print('  proposals', len(moves), 'tries', tries, flush=True)
    sc = []
    for kind, cs in moves:
        sp2 = copy.deepcopy(spec); sp2['constraints'] += cs
        s_ = score(sp2, cand, left)
        if s_ is None:
            continue
        ncell = sum(len(c['cells']) for c in cs)
        sc.append((s_ * BON.get(kind, 1) / (1 + 0.08 * ncell), rnd.random(), sp2, kind, cs))
    sc.sort(key=lambda x: (-x[0], x[1]))
    if GIVENS and not pending and (not sc or sc[0][0] < 5):
        for a_ in L.cells:
            if len(cand[a_]) < 2:
                continue
            for val in {g[a_] for g in sm}:
                sp2 = copy.deepcopy(spec); sp2.setdefault('givens', {})[name(a_)] = val
                s_ = score(sp2, cand, left)
                if s_ is not None:
                    sc.append((s_ / 4, rnd.random(), sp2, 'given', [name(a_), val]))
        sc.sort(key=lambda x: (-x[0], x[1]))
    top = sc[:3]
    rnd.shuffle(top)
    if not sc:
        print('  moves', len(moves), 'scored', len(sc))
    for s_, _, sp2, kind, cs in (sc if pending else top + sc[3:]):
        if feasible(sp2):
            spec = sp2
            if kind == 'ladder':
                nlad = 1 + max(c.get('ladder', 0) for c in spec['constraints'])
            if pending:
                pending.pop(0)
                for c in spec['constraints']:
                    c['keep'] = True
            print('  add', round(s_, 1), kind, cs if kind == 'given' else [(c['type'], ' '.join(c['cells'])) for c in cs], flush=True)
            break
    else:
        print('no move'); sys.exit()
assert unique(spec)


def drop_where(spec, pred):
    sp2 = copy.deepcopy(spec)
    sp2['constraints'] = [c for c in sp2['constraints'] if not pred(c)]
    return sp2


# prune whole elements, newest first (a ladder = all rungs with its id; --sym pairs are pruned separately)
ids = []
for c in spec['constraints']:
    if c.get('keep'):
        continue
    key = ('ladder', c['ladder']) if 'ladder' in c else ('snake', tuple(c['cells']))
    if key not in ids:
        ids.append(key)
for key in reversed(ids):
    pred = (lambda c, k=key: c.get('ladder') == k[1]) if key[0] == 'ladder' else (lambda c, k=key: tuple(c['cells']) == k[1] and not c.get('keep'))
    sp2 = drop_where(spec, pred)
    ok, r2 = logic_ok(sp2)
    if ok and unique(sp2):
        print('  drop', key, flush=True); spec = sp2
# trim ladder end rungs (a ladder keeps at least 2 rungs)
for lid in sorted({c['ladder'] for c in spec['constraints'] if 'ladder' in c and not c.get('keep')}):
    while True:
        rs = [c for c in spec['constraints'] if c.get('ladder') == lid]
        if len(rs) <= 2:
            break
        for end in (rs[0], rs[-1]):
            sp2 = drop_where(spec, lambda c, e=end: c is e or (c.get('ladder') == lid and c['cells'] == e['cells']))
            ok, r2 = logic_ok(sp2)
            if ok and unique(sp2):
                print('  trim rung', end['cells'], flush=True); spec = sp2; break
        else:
            break
for g_ in list(spec.get('givens', {})):
    sp2 = copy.deepcopy(spec); del sp2['givens'][g_]
    ok, r2 = logic_ok(sp2)
    if ok and unique(sp2):
        print('  drop given', g_, flush=True); spec = sp2
ok, r2 = logic_ok(spec)
print('givens', spec.get('givens'))
print('FINAL elements', len(spec['constraints']), 'tier2', r2, ok)
for c in spec['constraints']:
    c.pop('keep', None)
json.dump(spec, open(out, 'w'), indent=1)
