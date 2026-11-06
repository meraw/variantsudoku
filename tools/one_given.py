"""Symmetric negative-XV designs that need exactly one given (run 3, used for 006 Which Way Up).
python3 one_given.py base.json seed_from n lo hi
base.json holds 180-degree-symmetric constraints (e.g. thermometers). For each seed, CP-SAT finds a grid satisfying the
base whose X/V pattern is 180-degree symmetric with lo..hi marks (random objective for variety). Every such design has
solutions in rotated pairs, so it needs at least one given. If it has exactly two, try every tie-breaking single given
and keep the ones the logical solver (tiers 1-2) finishes. Writes one_<seed>.json with the spec and the solvable givens."""
import sys, json, random
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from ortools.sat.python import cp_model


def design(base, seed, lo, hi, tl=20):
    rnd = random.Random(seed)
    m, v = Puzzle(base).build_model()
    marks = {}
    for r in range(N):
        for c in range(N):
            for b in ((r, c + 1), (r + 1, c)):
                if b[0] >= N or b[1] >= N:
                    continue
                a = (r, c); x = m.NewBoolVar(''); y = m.NewBoolVar('')
                m.Add(v[a] + v[b] == 10).OnlyEnforceIf(x); m.Add(v[a] + v[b] != 10).OnlyEnforceIf(x.Not())
                m.Add(v[a] + v[b] == 5).OnlyEnforceIf(y); m.Add(v[a] + v[b] != 5).OnlyEnforceIf(y.Not())
                marks[frozenset((a, b))] = (a, b, x, y)
    rot = lambda a: (8 - a[0], 8 - a[1])
    for a, b, x, y in marks.values():
        _, _, x2, y2 = marks[frozenset((rot(a), rot(b)))]
        m.Add(x == x2); m.Add(y == y2)
    tot = sum(x + y for _, _, x, y in marks.values())
    m.Add(tot >= lo); m.Add(tot <= hi)
    m.Maximize(sum(rnd.randint(-3, 3) * v[a] for a in v))
    s = cp_model.CpSolver(); s.parameters.random_seed = seed; s.parameters.max_time_in_seconds = tl
    if s.Solve(m) not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    xv = []
    for a, b, x, y in marks.values():
        if s.Value(x):
            xv.append({"type": "xv", "cells": [name(a), name(b)], "value": "X"})
        if s.Value(y):
            xv.append({"type": "xv", "cells": [name(a), name(b)], "value": "V"})
    return xv


def main():
    base = json.load(open(sys.argv[1]))
    s0, n, lo, hi = map(int, sys.argv[2:6])
    for seed in range(s0, s0 + n):
        xv = design(base, seed, lo, hi)
        if xv is None:
            continue
        spec = dict(base, givens={}, constraints=base['constraints'] + xv)
        spec['global'] = sorted(set(base.get('global', [])) | {'neg_xv'})
        sols, _ = Puzzle(spec).count_solutions(limit=3, time_limit=30)
        if len(sols) != 2:
            print(seed, len(xv), 'marks:', len(sols), 'solutions, skipped', flush=True)
            continue
        A, B = sols; ok = []
        for a in A:
            if A[a] != B[a]:
                L = Logic(Puzzle(dict(spec, givens={name(a): A[a]})))
                res, _ = L.solve(2)
                if res == 'solved':
                    ok.append((L.tier_counts[2], name(a), A[a]))
        ok.sort()
        print(seed, len(xv), 'marks: solvable single givens', len(ok), ok[-5:], flush=True)
        if ok:
            json.dump({"spec": spec, "givens": ok}, open(f'one_{seed}.json', 'w'))


main()
