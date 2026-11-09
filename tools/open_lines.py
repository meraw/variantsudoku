"""Run 5: "open-solution" line placement (no target grid), used for bridge lines.

python3 open_lines.py base.json out.json seed [type] [pairs:0/1] [minlen] [maxlen] [--snakes] [--givens]
(type: bridge; odometer or arrow since run 6)   [--cap N: odometer steps with more than N cases are not used]

--snakes adds box-covering paths (all 9 cells of a box, or 8, plus an outside end on each side) to the pool;
--givens allows a given digit as a move when no line removes at least 15 candidates (scored with a penalty).
Lines marked "keep" in the base spec (a hand-placed core) are never pruned.

Repeat until the logical solver (tiers 1-2) finishes, which also proves uniqueness:
  1. sample solutions of the current puzzle;
  2. generate random paths (king steps, no shared cells with existing lines, no crossing diagonals) of the
     wanted length; with pairs=1 a path is added together with its 180-degree rotation;
  3. keep paths satisfied by at least one sample, score them by the candidates the logical solver removes
     from the current fixpoint, take one of the best three after a CP-SAT feasibility check.
Then drop every line (pair) that is not needed for uniqueness + the tier-2 logical solve."""
import sys, json, random, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from ortools.sat.python import cp_model
from open_clues import samples, logic_ok, unique, feasible

SNAKES = '--snakes' in sys.argv
if '--cap' in sys.argv:  # run 6: human-sized case lists only (see Logic.CASE_CAP)
    Logic.CASE_CAP = int(sys.argv[sys.argv.index('--cap') + 1])
GIVENS = '--givens' in sys.argv
GIVEN_PENALTY = 30
STEPS = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]


def rot(a):
    return (8 - a[0], 8 - a[1])


def segs_of(path):
    return [(a, b) for a, b in zip(path, path[1:]) if a[0] != b[0] and a[1] != b[1]]


def crosses(d1, d2):
    (a, b), (c, d) = d1, d2
    # two diagonal steps cross if they span the same 2x2 square in opposite directions
    return {a, b} != {c, d} and min(a[0], b[0]) == min(c[0], d[0]) and min(a[1], b[1]) == min(c[1], d[1]) \
        and {a, b} | {c, d} == {(min(a[0], b[0]) + i, min(a[1], b[1]) + j) for i in (0, 1) for j in (0, 1)}


def rand_path(rnd, used, diag, L, ortho_bias=0.75):
    r, c = rnd.randrange(9), rnd.randrange(9)
    if (r, c) in used:
        return None
    path = [(r, c)]
    while len(path) < L:
        opts = []
        for dr, dc in STEPS:
            n = (path[-1][0] + dr, path[-1][1] + dc)
            if not (0 <= n[0] < 9 and 0 <= n[1] < 9) or n in used or n in path:
                continue
            if dr and dc:
                if any(crosses((path[-1], n), d) for d in diag + segs_of(path)):
                    continue
                if rnd.random() < ortho_bias:
                    continue
            opts.append(n)
        if not opts:
            return None
        path.append(rnd.choice(opts))
    return path


def snake_path(rnd, used, diag, minus_one=False):
    """Random king-move path through every cell of one box (or all but one), plus one outside cell at each end."""
    b = rnd.randrange(9)
    r0, c0 = (b // 3) * 3, (b % 3) * 3
    cells = [(r0 + i, c0 + j) for i in range(3) for j in range(3)]
    if minus_one:
        cells.remove(rnd.choice(cells))
    if any(a in used for a in cells):
        return None
    cs = set(cells)
    for _ in range(30):
        path = [rnd.choice(cells)]
        while len(path) < len(cells):
            opts = [(path[-1][0] + dr, path[-1][1] + dc) for dr, dc in STEPS]
            opts = [o for o in opts if o in cs and o not in path and
                    not ((o[0] != path[-1][0] and o[1] != path[-1][1]) and any(crosses((path[-1], o), d) for d in diag + segs_of(path)))]
            if not opts:
                break
            path.append(rnd.choice(opts))
        if len(path) < len(cells):
            continue
        ends = []
        for a in (path[0], path[-1]):
            opts = [(a[0] + dr, a[1] + dc) for dr, dc in STEPS[:4]]
            opts = [o for o in opts if 0 <= o[0] < 9 and 0 <= o[1] < 9 and o not in cs and o not in used and o not in ends]
            if not opts:
                break
            ends.append(rnd.choice(opts))
        if len(ends) == 2:
            return [ends[0]] + path + [ends[1]]
    return None


def path_of(c):
    """run 6: all cells of a line constraint in order (an arrow's circle first)"""
    return c.get('circle', []) + c.get('cells', [])


def make_con(typ, path):
    names = [name(a) for a in path]
    if typ == 'arrow':  # run 6: the first cell is the circle, the rest is the shaft
        return {"type": "arrow", "circle": names[:1], "cells": names[1:]}
    return {"type": typ, "cells": names}


def ok_path(pz_vals, typ, path):
    v = [pz_vals[a] for a in path]
    if typ == 'bridge':
        return v[0] * v[-1] == sum(v[1:-1])
    if typ == 'odometer':  # run 6: circled first cell = total distance travelled along the line
        return v[0] == sum(abs(a - b) for a, b in zip(v, v[1:]))
    if typ == 'arrow':  # run 6: circle (first cell) = sum of the shaft
        return v[0] == sum(v[1:])
    raise ValueError(typ)


def main():
    argv = [a for i, a in enumerate(sys.argv) if not a.startswith('--') and sys.argv[i - 1] != '--cap']
    base, out, seed = argv[1], argv[2], int(argv[3])
    typ = argv[4] if len(argv) > 4 else 'bridge'
    pairs = int(argv[5]) if len(argv) > 5 else 1
    minlen = int(argv[6]) if len(argv) > 6 else 3
    maxlen = int(argv[7]) if len(argv) > 7 else 6
    rnd = random.Random(seed)
    spec = json.load(open(base)); spec.setdefault('constraints', [])
    while True:
        pz = Puzzle(spec)
        L = Logic(pz); cand = L.init_cands(); L.propagate(cand, 2)
        left = sum(len(x) for x in cand.values())
        print('lines', len(spec['constraints']), 'candidates left', left, flush=True)
        if left == 81:
            break
        used = {parse(x) for c in spec['constraints'] for x in path_of(c)}
        diag = [d for c in spec['constraints'] for d in segs_of([parse(x) for x in path_of(c)])]
        sm = samples(spec, 30, rnd)
        cands = {}
        for it in range(6000):
            if SNAKES and it % 4 == 0:
                p = snake_path(rnd, used, diag, minus_one=rnd.random() < 0.5)
            else:
                p = rand_path(rnd, used, diag, rnd.randint(minlen, maxlen))
            if not p:
                continue
            group = [p]
            if pairs and set(rot(a) for a in p) != set(p):  # a self-symmetric line stands alone
                q = [rot(a) for a in p]
                if set(q) & (used | set(p)) or any(crosses(d1, d2) for d1 in segs_of(q) for d2 in diag + segs_of(p)):
                    continue
                group.append(q)
            if not any(all(ok_path(g, typ, x) for x in group) for g in sm):
                continue
            cands[tuple(map(tuple, group))] = group
        scored = []
        for key, group in list(cands.items())[:400]:
            sp2 = copy.deepcopy(spec)
            for x in group:
                sp2['constraints'].append(make_con(typ, x))
            c2 = {a: set(x) for a, x in cand.items()}
            try:
                Logic(Puzzle(sp2)).propagate(c2, 2)
            except Contradiction:
                continue
            scored.append((left - sum(len(x) for x in c2.values()), rnd.random(), sp2, group))
        scored.sort(key=lambda t: (-t[0], t[1]))
        if GIVENS and (not scored or scored[0][0] < 15):
            for a in Logic(pz).cells:
                if len(cand[a]) < 2:
                    continue
                for val in {g[a] for g in sm}:
                    c2 = {b: set(x) for b, x in cand.items()}; c2[a] = {val}
                    try:
                        Logic(pz).propagate(c2, 2)
                    except Contradiction:
                        continue
                    sp2 = copy.deepcopy(spec); sp2.setdefault('givens', {})[name(a)] = val
                    scored.append((left - sum(len(x) for x in c2.values()) - GIVEN_PENALTY, rnd.random(), sp2, [[a]]))
            scored.sort(key=lambda t: (-t[0], t[1]))
        top = scored[:3]; rnd.shuffle(top)
        for sc, _, sp2, group in top + scored[3:]:
            if feasible(sp2):
                spec = sp2
                print('  add', sc, [[name(a) for a in x] for x in group], 'givens' if len(group[0]) == 1 else '', flush=True)
                break
        else:
            print('no feasible move'); return
    assert unique(spec)
    i = len(spec['constraints']) - 1
    while i >= 0:
        c = spec['constraints'][i]
        if c['type'] != typ or c.get('keep'):
            i -= 1; continue
        # find its partner (rotation) if pairs
        idx = [i]
        if pairs:
            rc = [rot(parse(x)) for x in path_of(c)]
            for j, d in enumerate(spec['constraints']):
                if j != i and d['type'] == typ and [parse(x) for x in path_of(d)] == rc:
                    idx.append(j)
        sp2 = copy.deepcopy(spec)
        sp2['constraints'] = [d for j, d in enumerate(spec['constraints']) if j not in idx]
        ok, r2 = logic_ok(sp2)
        if ok and unique(sp2):
            print('  drop', [path_of(spec['constraints'][j]) for j in idx], flush=True)
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
    print('FINAL givens', len(spec.get('givens', {})), 'lines', len(spec['constraints']), 'tier2 rounds', r2, 'solved', ok)
    json.dump(spec, open(out, 'w'), indent=1)


if __name__ == '__main__':
    main()
