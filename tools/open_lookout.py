"""Run 11: open-solution setting for lookout towers (invented), optionally mixed with other position-only clues.

python3 open_lookout.py base.json out.json seed [--sym] [--sep] [--gthresh N] [--topk K] [--maxtowers N]
                        [--sky] [--skybonus x]

A tower is just a marked cell (its digit is the clue), so a move is a position. Every free cell is scored by the
candidates the logical solver (tiers 1-2) removes when a tower is put there (a contradiction = impossible move);
one of the top K is committed after CP-SAT confirms the puzzle is still satisfiable. --sym adds towers in 180°
pairs (the centre cell alone), --sep keeps towers from touching orthogonally. Givens (values taken from sampled
solutions) become moves only when the best tower removes fewer than --gthresh candidates (default 1: only when no
tower makes progress). Stops when the logical solver finishes, then drops every tower/given not needed for
uniqueness + a tier-2 solve (newest first; towers in "keep" constraints of the base spec are never dropped).
--sky also offers skyscraper clues (any of the 36 outside positions, totals 2-8 taken from sampled solutions), with
their score multiplied by --skybonus (default 1). Positive-only towers cannot finish a puzzle on their own: a grid
has about 5 towers on average, and after 12-13 forced towers no further tower fits anywhere (seed 1, run 11)."""
import sys, json, random, copy
from multiprocessing import Pool
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from open_clues import logic_ok, unique, feasible, samples


def opt(name_, default):
    return sys.argv[sys.argv.index(name_) + 1] if name_ in sys.argv else default


def score(args):
    spec, cand, left, add, givens = args
    sp2 = copy.deepcopy(spec)
    sp2['constraints'] += add
    sp2.setdefault('givens', {}).update(givens)
    c2 = {a: set(x) for a, x in cand.items()}
    for g, d in givens.items():
        c2[parse(g)] &= {d}
    try:
        Logic(Puzzle(sp2)).propagate(c2, 2)
    except Contradiction:
        return None
    return left - sum(len(x) for x in c2.values()), sp2


def main():
    flags = ('--gthresh', '--topk', '--maxtowers', '--skybonus')
    argv = [a for i, a in enumerate(sys.argv) if not a.startswith('--') and not (i > 0 and sys.argv[i - 1] in flags)]
    base, out, seed = argv[1], argv[2], int(argv[3])
    sym, sep = '--sym' in sys.argv, '--sep' in sys.argv
    gthresh = float(opt('--gthresh', 1))
    topk = int(opt('--topk', 3))
    maxtowers = int(opt('--maxtowers', 99))
    sky, skybonus = '--sky' in sys.argv, float(opt('--skybonus', 1))
    SKYPOS = [f"r0c{k}" for k in range(1, 10)] + [f"r10c{k}" for k in range(1, 10)] + \
             [f"r{k}c0" for k in range(1, 10)] + [f"r{k}c10" for k in range(1, 10)]
    rnd = random.Random(seed)
    spec = json.load(open(base)); spec.setdefault('constraints', []); spec.setdefault('givens', {})
    pool = Pool(4)
    while True:
        L = Logic(Puzzle(spec)); cand = L.init_cands()
        L.propagate(cand, 2)
        left = sum(len(x) for x in cand.values())
        towers = {parse(c['cells'][0]) for c in spec['constraints'] if c['type'] == 'lookout'}
        print('towers', len(towers), 'givens', len(spec['givens']), 'candidates left', left, flush=True)
        if left == 81:
            break
        near = set(towers)
        if sep:
            for (r, k) in towers:
                near |= {(r + 1, k), (r - 1, k), (r, k + 1), (r, k - 1)}
        jobs, keys = [], []
        if len(towers) < maxtowers:
            done = set()
            for a in L.cells:
                if a in near or a in done or not cand[a] & set(range(2, 9)):  # 1 and 9 are never towers
                    continue
                grp = [a]
                if sym:
                    b = (8 - a[0], 8 - a[1])
                    if b != a:
                        if b in near:
                            continue
                        grp.append(b)
                done |= set(grp)
                jobs.append((spec, cand, left, [{"type": "lookout", "cells": [name(x)]} for x in grp], {}))
                keys.append(('tower', grp))
        if sky:
            sm = samples(spec, 16, rnd)
            used = {c['from'] for c in spec['constraints'] if 'from' in c}
            for p in SKYPOS:
                if p in used:
                    continue
                ray = outside_ray(p)
                for val in sorted({sum(1 for i, x in enumerate(vals) if all(x > y for y in vals[:i]))
                                   for vals in ([g[a] for a in ray] for g in sm)} - {1, 9}):
                    jobs.append((spec, cand, left, [{"type": "skyscraper", "from": p, "count": val}], {}))
                    keys.append(('sky', (p, val)))
        res = pool.map(score, jobs)
        moves = [(r[0] * (skybonus if k[0] == 'sky' else 1), rnd.random(), r[1], k) for r, k in zip(res, keys) if r is not None]
        moves.sort(key=lambda t: (-t[0], t[1]))
        if not moves or moves[0][0] < gthresh:
            sm = samples(spec, 12, rnd)
            gj, gk = [], []
            for a in L.cells:
                if len(cand[a]) < 2:
                    continue
                for val in sorted({g[a] for g in sm}):
                    gv = {name(a): val}
                    if sym and (8 - a[0], 8 - a[1]) != a:
                        b = (8 - a[0], 8 - a[1])
                        for g in sm:
                            if g[a] == val and len(cand[b]) > 1:
                                gv = {name(a): val, name(b): g[b]}; break
                    gj.append((spec, cand, left, [], gv)); gk.append(('given', gv))
            res = pool.map(score, gj)
            gm = [(r[0] / len(k[1]) * 0.5, rnd.random(), r[1], k) for r, k in zip(res, gk) if r is not None]
            moves += gm
            moves.sort(key=lambda t: (-t[0], t[1]))
        if not moves or moves[0][0] <= 0:
            print('stalled'); return
        top = moves[:topk]; rnd.shuffle(top)
        for sc, _, sp2, k in top + moves[topk:]:
            if feasible(sp2):
                spec = sp2
                print('  add', round(sc, 1), k[0], k[1], flush=True)
                break
        else:
            print('no feasible move'); return
    assert unique(spec)
    # prune: newest first; towers (in sym mode: 180° partners together) and givens
    items = [('c', i) for i in range(len(spec['constraints']))] + [('g', g) for g in list(spec['givens'])]
    for kind, key in reversed(items):
        sp2 = copy.deepcopy(spec)
        if kind == 'c':
            c = spec['constraints'][key] if key < len(spec['constraints']) else None
            if c is None or c.get('keep') or c.get('_dropped'):
                continue
            sp2['constraints'][key]['_dropped'] = True
            if sym and c['type'] == 'lookout':
                a = parse(c['cells'][0]); b = name((8 - a[0], 8 - a[1]))
                for c2 in sp2['constraints']:
                    if c2['type'] == 'lookout' and c2['cells'][0] == b:
                        c2['_dropped'] = True
        else:
            if key not in sp2['givens']:
                continue
            del sp2['givens'][key]
        test = copy.deepcopy(sp2); test['constraints'] = [c for c in test['constraints'] if not c.get('_dropped')]
        ok, r2 = logic_ok(test)
        if ok and unique(test):
            print('  drop', kind, key if kind == 'g' else spec['constraints'][key], flush=True)
            spec = sp2
    spec['constraints'] = [c for c in spec['constraints'] if not c.get('_dropped')]
    ok, r2 = logic_ok(spec)
    nt = sum(c['type'] == 'lookout' for c in spec['constraints'])
    print('FINAL towers', nt, 'other', len(spec['constraints']) - nt, 'givens', len(spec['givens']), 'tier2 rounds', r2, 'solved', ok)
    json.dump(spec, open(out, 'w'), indent=1)


if __name__ == '__main__':
    main()
