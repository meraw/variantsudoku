"""Run 10: open-solution setting where every clue has the SAME value; the setter only chooses positions.

python3 open_fixed.py base.json out.json seed [--value 13] [--types killer,lk,sandwich,xsum] [--cages 2,3]
                      [--bonus killer=1.2,lk=1.5] [--samples N] [--topk K] [--sep] [--maxof killer=6]

Moves (all with the fixed value):
  killer   - a cage of 2-4 cells (dominoes, straight/L trominoes, all tetromino shapes, per --cages) not overlapping
             another cage (with --sep also not orthogonally touching one);
  lk       - a little killer on a diagonal of 3+ cells, written at a free end of the diagonal;
  sandwich - a sandwich total for a row/column (written left of the row / above the column, or the other side if taken);
  xsum     - an X-sum at one of the 36 outside positions.
Each outside position holds at most one clue. Every move is scored by the candidates the logical solver (tiers 1-2)
removes, times its type bonus; one of the top K is committed after CP-SAT confirms it is satisfiable.
No givens are ever added (a themed puzzle with givens would break the theme): the run fails if it stalls.
Stops when the logical solver finishes, then drops clues that are not needed for uniqueness + a tier-2 solve,
newest first."""
import sys, json, random, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from open_clues import logic_ok, unique, feasible
from open_lk import diagonals


def opt(name_, default):
    return sys.argv[sys.argv.index(name_) + 1] if name_ in sys.argv else default


def cage_shapes(sizes):
    shapes = set()
    cells = [(r, k) for r in range(N) for k in range(N)]

    def grow(sh, n):
        if len(sh) == n:
            shapes.add(frozenset(sh)); return
        for (r, k) in list(sh):
            for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                b = (r + dr, k + dc)
                if 0 <= b[0] < N and 0 <= b[1] < N and b not in sh:
                    grow(sh | {b}, n)
    for n in sizes:
        for a in cells:
            grow({a}, n)
    return sorted(shapes, key=lambda s: sorted(s))


def other_end(frm, d):
    cells = lk_cells(frm, d)
    r, k = cells[-1]
    dr, dc = LK_DIRS[d]
    return (f"r{r + dr + 1}c{k + dc + 1}", {'DR': 'UL', 'DL': 'UR', 'UL': 'DR', 'UR': 'DL'}[d])


def main():
    flags = ('--value', '--types', '--cages', '--bonus', '--samples', '--topk', '--maxof')
    argv = [a for i, a in enumerate(sys.argv) if not a.startswith('--') and not (i > 0 and sys.argv[i - 1] in flags)]
    base, out, seed = argv[1], argv[2], int(argv[3])
    V = int(opt('--value', 13))
    types = opt('--types', 'killer,lk,sandwich').split(',')
    sizes = [int(x) for x in opt('--cages', '2,3').split(',')]
    topk = int(opt('--topk', 3))
    sep = '--sep' in sys.argv
    bonus, maxof = {}, {}
    for key, dst in (('--bonus', bonus), ('--maxof', maxof)):
        if key in sys.argv:
            for kv in opt(key, '').split(','):
                a_, b_ = kv.split('='); dst[a_] = float(b_)
    rnd = random.Random(seed)
    spec = json.load(open(base)); spec.setdefault('constraints', [])
    SH = cage_shapes(sizes) if 'killer' in types else []
    D = diagonals(3)
    while True:
        L = Logic(Puzzle(spec)); cand = L.init_cands()
        L.propagate(cand, 2)
        left = sum(len(x) for x in cand.values())
        cons = spec['constraints']
        count = {t: sum(c['type'] == t for c in cons) for t in ('killer', 'littlekiller', 'sandwich', 'xsum')}
        print('clues', count, 'candidates left', left, flush=True)
        if left == 81:
            break
        used_pos = {c['from'] for c in cons if 'from' in c}
        caged = {parse(x) for c in cons if c['type'] == 'killer' for x in c['cells']}
        near = set(caged)
        if sep:
            for (r, k) in caged:
                near |= {(r + 1, k), (r - 1, k), (r, k + 1), (r, k - 1)}
        groups = []
        if 'killer' in types and count['killer'] < maxof.get('killer', 99):
            for s in SH:
                if not (s & near):
                    groups.append(('killer', {"type": "killer", "cells": [name(a) for a in sorted(s)], "sum": V}))
        if 'lk' in types and count['littlekiller'] < maxof.get('lk', 99):
            have = [sorted(lk_cells(c['from'], c['dir'])) for c in cons if c['type'] == 'littlekiller']
            for e1, e2, cells in D:
                if sorted(cells) in have:
                    continue
                ends = [e for e in (e1, e2) if e[0] not in used_pos]
                if ends:
                    e = rnd.choice(ends)
                    groups.append(('lk', {"type": "littlekiller", "from": e[0], "dir": e[1], "sum": V}))
        if 'sandwich' in types and count['sandwich'] < maxof.get('sandwich', 99):
            have = [sorted(outside_line(c['from'])) for c in cons if c['type'] == 'sandwich']
            for i in range(1, 10):
                for p, q in ((f"r0c{i}", f"r10c{i}"), (f"r{i}c0", f"r{i}c10")):
                    if sorted(outside_line(p)) in have:
                        continue
                    pos = [x for x in (p, q) if x not in used_pos]
                    if pos:
                        groups.append(('sandwich', {"type": "sandwich", "from": pos[0], "sum": V}))
        if 'xsum' in types and count['xsum'] < maxof.get('xsum', 99):
            for i in range(1, 10):
                for p in (f"r0c{i}", f"r10c{i}", f"r{i}c0", f"r{i}c10"):
                    if p not in used_pos:
                        groups.append(('xsum', {"type": "xsum", "from": p, "sum": V}))
        moves = []
        for typ, c in groups:
            sp2 = copy.deepcopy(spec); sp2['constraints'].append(c)
            c2 = {a: set(x) for a, x in cand.items()}
            try:
                Logic(Puzzle(sp2)).propagate(c2, 2)
            except Contradiction:
                continue
            sc = (left - sum(len(x) for x in c2.values())) * bonus.get(typ, 1.0)
            moves.append((sc, rnd.random(), sp2, c))
        moves.sort(key=lambda t: (-t[0], t[1]))
        if not moves or moves[0][0] <= 0:
            print('stalled: no clue makes logical progress'); return
        top = moves[:topk]; rnd.shuffle(top)
        for sc, _, sp2, c in top + moves[topk:]:
            if feasible(sp2):
                spec = sp2
                print('  add', round(sc, 1), c, flush=True)
                break
        else:
            print('no feasible move'); return
    assert unique(spec)
    i = len(spec['constraints']) - 1
    while i >= 0:
        c = spec['constraints'][i]
        if c.get('keep'):
            i -= 1; continue
        sp2 = copy.deepcopy(spec); del sp2['constraints'][i]
        ok, r2 = logic_ok(sp2)
        if ok and unique(sp2):
            print('  drop', c, flush=True)
            spec = sp2
        i -= 1
    ok, r2 = logic_ok(spec)
    print('FINAL clues', len(spec['constraints']), 'tier2 rounds', r2, 'solved', ok)
    json.dump(spec, open(out, 'w'), indent=1)


if __name__ == '__main__':
    main()
