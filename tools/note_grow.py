"""Run 15: open-solution growth of "musical notes" (fifths line stems/beams/flags + 2-cell killer-cage note heads).
python3 note_grow.py base.json out.json seed [--maxnotes N] [--types q,e,b] [--topk K] [--nopair]

A move is one note placed in free space: a note head (2-cell killer cage) with a stem (a fifths line) going up or down,
optionally a flag (eighth note) or a beam to a second head (beamed pair). Note templates follow music engraving:
stem up = stem on the right of the head, stem down = stem on the left. Notes never overlap or touch each other
orthogonally. Each proposal must hold in a sampled grid (its cage sums come from that grid); proposals are scored by the
candidates my logical solver (tiers 1-2) removes, divided by the number of cells drawn; one of the top K is confirmed
with CP-SAT and committed. Stops when the logical solver finishes, then drops whole notes that are not needed for
uniqueness + a tier-2 solve (newest first). No givens ever."""
import sys, json, random, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from open_clues import samples, feasible, unique, logic_ok


def opt(n, d):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d


argv = [a for i, a in enumerate(sys.argv) if not a.startswith('--') and not (i > 0 and sys.argv[i - 1].startswith('--'))]
base, out, seed = argv[1], argv[2], int(argv[3])
MAXN = int(opt('--maxnotes', 12))
TYPES = opt('--types', 'q,e,b').split(',')
TOPK = int(opt('--topk', 3))
rnd = random.Random(seed)
spec = json.load(open(base))
for c in spec['constraints']:
    c['keep'] = True


def templates():
    """(kind, line cells, list of head cages) relative to an anchor (0, 0) = bottom (stem up) / top (stem down) of the stem"""
    out = []
    for L in (3, 4):
        up = [(-i, 0) for i in range(L)]
        dn = [(i, 0) for i in range(L)]
        if 'q' in TYPES:
            out.append(('q', up, [[(0, -1), (0, 0)]]))
            out.append(('q', dn, [[(0, 0), (0, 1)]]))
        if 'e' in TYPES:  # flag: from the free end of the stem one diagonal step to the right, back towards the head
            out.append(('e', up + [(-(L - 2), 1)], [[(0, -1), (0, 0)]]))
            out.append(('e', dn + [(L - 2, 1)], [[(0, 0), (0, 1)]]))
        if 'b' in TYPES:
            for w in (2, 3):
                beam_up = [(-(L - 1), j) for j in range(1, w + 1)]
                out.append(('b', up + beam_up + [(-i, w) for i in range(L - 2, -1, -1)], [[(0, -1), (0, 0)], [(0, w - 1), (0, w)]]))
                beam_dn = [(L - 1, j) for j in range(1, w + 1)]
                out.append(('b', dn + beam_dn + [(i, w) for i in range(L - 2, -1, -1)], [[(0, 0), (0, 1)], [(0, w), (0, w + 1)]]))
    return out


TPL = templates()


def occupied(sp):
    occ = set()
    for c in sp['constraints']:
        occ |= {parse(x) for x in c.get('cells', [])}
    return occ


def propose(occ):
    kind, line, heads = rnd.choice(TPL)
    r0, k0 = rnd.randrange(9), rnd.randrange(9)
    cells = [(r0 + a, k0 + b) for a, b in line]
    hs = [[(r0 + a, k0 + b) for a, b in h] for h in heads]
    allc = set(cells) | {x for h in hs for x in h}
    if any(not (0 <= r < 9 and 0 <= k < 9) for r, k in allc):
        return None
    if allc & occ or any(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a in allc for b in occ):
        return None
    return kind, cells, hs


def note_cons(cells, hs, g, nid):
    cs = [{"type": "fifths", "cells": [name(a) for a in cells], "nid": nid}]
    for h in hs:
        cs.append({"type": "killer", "cells": [name(a) for a in h], "sum": sum(g[a] for a in h), "nid": nid})
    return cs


notes = []  # list of constraint-index groups added (for pruning)
while True:
    pz = Puzzle(spec); L = Logic(pz); cand = L.init_cands()
    L.propagate(cand, 2)
    left = sum(len(x) for x in cand.values())
    print('notes', len(notes), 'left', left, flush=True)
    if left == 81 or len(notes) >= MAXN:
        break
    sm = samples(spec, 25, rnd)
    occ = occupied(spec)
    props = {}
    for _ in range(6000):
        p = propose(occ)
        if not p:
            continue
        kind, cells, hs = p
        for g in sm:
            if all(abs(g[a] - g[b]) in (4, 5) for a, b in zip(cells, cells[1:])) and all(len({g[x] for x in h}) == 2 for h in hs):
                key = (tuple(cells), tuple(tuple(h) for h in hs), tuple(sum(g[x] for x in h) for h in hs))
                props[key] = (kind, cells, hs, g)
        if len(props) > 400:
            break
    items = list(props.values()); rnd.shuffle(items)
    sc = []
    for kind, cells, hs, g in items[:300]:
        sp2 = copy.deepcopy(spec); sp2['constraints'] += note_cons(cells, hs, g, len(notes))
        c2 = {a: set(x) for a, x in cand.items()}
        try:
            Logic(Puzzle(sp2)).propagate(c2, 2)
        except Contradiction:
            continue
        gain = left - sum(len(x) for x in c2.values())
        ncell = len(cells) + 2 * len(hs)
        sc.append((gain / ncell, rnd.random(), sp2, kind, cells, len(hs)))
    sc.sort(key=lambda x: (-x[0], x[1]))
    top = sc[:TOPK]; rnd.shuffle(top)
    for s_, _, sp2, kind, cells, nh in top + sc[TOPK:]:
        if feasible(sp2):
            n0 = len(spec['constraints'])
            spec = sp2; notes.append(len(notes))
            print('  add', round(s_, 2), kind, ' '.join(name(a) for a in cells), [c.get('sum') for c in spec['constraints'][n0:]], flush=True)
            break
    else:
        print('no move'); break
if unique(spec):
    for nid in reversed(notes):
        sp2 = copy.deepcopy(spec)
        sp2['constraints'] = [c for c in spec['constraints'] if c.get('nid') != nid]
        ok, r2 = logic_ok(sp2)
        if ok and unique(sp2):
            print('  drop note', [c['cells'] for c in spec['constraints'] if c.get('nid') == nid], flush=True)
            spec = sp2
ok, r2 = logic_ok(spec)
print('FINAL constraints', len(spec['constraints']), 'unique', unique(spec), 'logic', ok, 'tier2', r2)
for c in spec['constraints']:
    c.pop('keep', None); c.pop('nid', None)
json.dump(spec, open(out, 'w'), indent=1)
