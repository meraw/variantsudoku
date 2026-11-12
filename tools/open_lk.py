"""Run 9: open-solution setting for little-killer clues around a kept core, no target grid.

python3 open_lk.py base.json out.json seed [--samples N] [--topk K] [--minlen 3] [--sym | --mirror] [--nogivens]

Like open_outside.py (run 6), but the moves are little-killer sums. Every diagonal of at least --minlen cells
(default 3: a 2-cell diagonal sum is close to a pair of givens) can carry one clue; it is written at one of its two
ends (picked at random when committing, so the picture isn't one-sided). With --sym a move is a pair of
180-degree-opposite diagonals; with --mirror, a pair of left-right mirrored diagonals.
  1. sample grids that satisfy the clues so far (CP-SAT, random objectives);
  2. score every still-possible (diagonal, sum) move by the candidates the logical solver (tiers 1-2) then removes;
  3. pick one of the top K, confirm satisfiable with CP-SAT, commit.
When no clue move removes at least GIVEN_THRESHOLD candidates, single givens become moves too (unless --nogivens).
Stops when the logical solver finishes, then drops clues (pairs) and givens that are not needed for uniqueness + a
tier-2 logical solve, newest first."""
import sys, json, random, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from open_clues import samples, logic_ok, unique, feasible

GIVEN_THRESHOLD = 12


def opt(name_, default):
    return sys.argv[sys.argv.index(name_) + 1] if name_ in sys.argv else default


def diagonals(minlen):
    """each diagonal once, as a pair of (from, dir) ends"""
    out = []
    for k in range(0, 8):  # down-right diagonals starting on the top edge (k=0 is the corner r0c0)
        a = (f"r0c{k}", 'DR'); out.append(a)
    for k in range(1, 8):
        out.append((f"r{k}c0", 'DR'))
    for k in range(3, 11):
        out.append((f"r0c{k}", 'DL'))
    for k in range(1, 8):
        out.append((f"r{k}c10", 'DL'))
    res = []
    for frm, d in out:
        cells = lk_cells(frm, d)
        if len(cells) < minlen:
            continue
        r, k = cells[-1]
        dr, dc = LK_DIRS[d]
        other = (f"r{r + dr + 1}c{k + dc + 1}", {'DR': 'UL', 'DL': 'UR'}[d])
        res.append(((frm, d), other, cells))
    return res


def rot(cells):
    if MIRROR:  # left-right mirror image instead of the 180-degree turn
        return sorted((r, 8 - k) for r, k in cells)
    return sorted((8 - r, 8 - k) for r, k in cells)


MIRROR = '--mirror' in sys.argv


def main():
    argv = [a for i, a in enumerate(sys.argv) if not a.startswith('--') and not (i > 0 and sys.argv[i - 1] in ('--samples', '--topk', '--minlen'))]
    base, out, seed = argv[1], argv[2], int(argv[3])
    ns, topk, minlen = int(opt('--samples', 24)), int(opt('--topk', 3)), int(opt('--minlen', 3))
    sym, nogivens = '--sym' in sys.argv or MIRROR, '--nogivens' in sys.argv
    rnd = random.Random(seed)
    spec = json.load(open(base)); spec.setdefault('constraints', [])
    D = diagonals(minlen)
    while True:
        L = Logic(Puzzle(spec)); cand = L.init_cands()
        L.propagate(cand, 2)
        left = sum(len(x) for x in cand.values())
        used = [sorted(c['rc']) for c in Puzzle(spec).cons if c['type'] == 'littlekiller']
        print('clues', len(used), 'givens', len(spec.get('givens', {})), 'candidates left', left, flush=True)
        if left == 81:
            break
        sm = samples(spec, ns, rnd)
        groups = []
        for i, (e1, e2, cells) in enumerate(D):
            if sorted(cells) in used:
                continue
            if sym:
                j = next(j for j, x in enumerate(D) if sorted(x[2]) == rot(cells))
                if j < i or sorted(D[j][2]) in used:
                    continue
                for s1, s2 in {(sum(g[a] for a in cells), sum(g[a] for a in D[j][2])) for g in sm}:
                    grp = [{"type": "littlekiller", "from": e1[0], "dir": e1[1], "sum": s1}]
                    if j != i:
                        grp.append({"type": "littlekiller", "from": D[j][0][0], "dir": D[j][0][1], "sum": s2})
                    groups.append(grp)
            else:
                for s in {sum(g[a] for a in cells) for g in sm}:
                    groups.append([{"type": "littlekiller", "from": e1[0], "dir": e1[1], "sum": s}])
        moves = []
        for grp in groups:
            sp2 = copy.deepcopy(spec); sp2['constraints'] += grp
            c2 = {a: set(x) for a, x in cand.items()}
            try:
                Logic(Puzzle(sp2)).propagate(c2, 2)
            except Contradiction:
                continue
            moves.append(((left - sum(len(x) for x in c2.values())) / len(grp), rnd.random(), sp2, grp))
        moves.sort(key=lambda t: (-t[0], t[1]))
        if not nogivens and (not moves or moves[0][0] < GIVEN_THRESHOLD):
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
                # write each new clue at a random end of its diagonal
                taken = {d['from'] for d in sp2['constraints'] if d.get('from') and d not in grp}
                for c in sp2['constraints']:
                    if c in grp:
                        e = next(x for x in D if x[0] == (c['from'], c['dir']))
                        ends = [x for x in (e[0], e[1]) if x[0] not in taken] or [e[0], e[1]]
                        c['from'], c['dir'] = rnd.choice(ends)
                        taken.add(c['from'])
                spec = sp2
                print('  add', sc, grp, flush=True)
                break
        else:
            print('no feasible move'); return
    assert unique(spec)
    i = len(spec['constraints']) - 1
    while i >= 0:
        c = spec['constraints'][i]
        if c['type'] != 'littlekiller' or c.get('keep'):
            i -= 1; continue
        idx = [i]
        if sym:
            me = sorted(lk_cells(c['from'], c['dir']))
            idx += [j for j, d in enumerate(spec['constraints']) if j != i and d['type'] == 'littlekiller'
                    and sorted(lk_cells(d['from'], d['dir'])) == rot(me)]
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
    print('FINAL givens', len(spec.get('givens', {})), 'clues', sum(c['type'] == 'littlekiller' for c in spec['constraints']),
          'tier2 rounds', r2, 'solved', ok)
    json.dump(spec, open(out, 'w'), indent=1)


if __name__ == '__main__':
    main()
