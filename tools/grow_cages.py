"""Solution-first constraint growth (setter's assistant).
python3 grow_cages.py base.json out.json seed [kind]
kind: killer (default) | xv | kropki
Picks a solution of base, then repeatedly samples candidate clues consistent with
that solution and adds the one that gives the most tier-<=2 logical progress until the
logical solver finishes. Then removes clues not needed. Confirms uniqueness with CP-SAT."""
import sys, json, random, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *

def progress(spec):
    lg = Logic(Puzzle(spec))
    res, c = lg.solve(max_tier=2)
    if res == 'contradiction':
        return None
    return sum(len(v) for v in c.values())

def main():
    base = json.load(open(sys.argv[1])); out = sys.argv[2]
    seed = int(sys.argv[3]); kind = sys.argv[4] if len(sys.argv) > 4 else 'killer'
    rnd = random.Random(seed)
    global SYM
    SYM = '--sym' in sys.argv
    sols, _ = Puzzle(base).count_solutions(limit=100)
    T = rnd.choice(sols)
    spec = copy.deepcopy(base)
    def caged():
        return {parse(c) for x in spec['constraints'] if x['type'] == 'killer' for c in x['cells']}
    def sample():
        if kind == 'killer':
            used = caged()
            for _ in range(50):
                a = (rnd.randrange(9), rnd.randrange(9))
                if a in used: continue
                n = rnd.choice([2, 2, 3, 3, 4])
                cells = [a]
                while len(cells) < n:
                    r, c = rnd.choice(cells)
                    nb = [(r+1, c), (r-1, c), (r, c+1), (r, c-1)]
                    nb = [x for x in nb if 0 <= x[0] < 9 and 0 <= x[1] < 9 and x not in used and x not in cells]
                    if not nb: break
                    cells.append(rnd.choice(nb))
                if len({T[x] for x in cells}) < len(cells): continue
                cells.sort()
                cl = {"type": "killer", "cells": [name(x) for x in cells], "sum": sum(T[x] for x in cells)}
                if SYM:
                    rot = sorted((8 - r, 8 - c) for r, c in cells)
                    if set(rot) & (used | set(cells)) or len({T[x] for x in rot}) < len(rot): continue
                    cl2 = {"type": "killer", "cells": [name(x) for x in rot], "sum": sum(T[x] for x in rot)}
                    return [cl, cl2], 2 * len(cells)
                return cl, len(cells)
        else:
            r, c = rnd.randrange(9), rnd.randrange(9)
            b = rnd.choice([(r, c+1), (r+1, c)])
            if b[0] > 8 or b[1] > 8: return None, 0
            a = (r, c)
            cl = dot(a, b)
            if cl is None: return None, 0
            if SYM:
                ra, rb = (8 - b[0], 8 - b[1]), (8 - a[0], 8 - a[1])
                if {ra, rb} == {a, b}: return None, 0
                cl2 = dot(ra, rb)
                if cl2 is None: return None, 0
                return [cl, cl2], 2
            return cl, 1
        return None, 0
    def dot(a, b):
        if kind == 'xv':
            s = T[a] + T[b]
            if s in (5, 10): return {"type": "xv", "cells": [name(a), name(b)], "value": 'V' if s == 5 else 'X'}
        else:
            if abs(T[a]-T[b]) == 1: return {"type": "kropki_w", "cells": [name(a), name(b)]}
            if T[a] == 2*T[b] or T[b] == 2*T[a]: return {"type": "kropki_b", "cells": [name(a), name(b)]}
        return None
    cur = progress(spec)
    while cur != 81:
        best = None
        for _ in range(60):
            cl, size = sample()
            if cl is None or cl in spec['constraints']: continue
            t = copy.deepcopy(spec); t['constraints'] += cl if isinstance(cl, list) else [cl]
            p = progress(t)
            if p is None: continue
            score = p + 4 * size
            if best is None or score < best[0]: best = (score, p, cl)
        if best is None: continue
        spec['constraints'] += best[2] if isinstance(best[2], list) else [best[2]]; cur = best[1]
        print('add', best[2], '->', cur, flush=True)
    base_n = len(base['constraints'])
    idx = list(range(base_n, len(spec['constraints'])))
    if SYM:
        groups = [set(idx[k:k + 2]) for k in range(0, len(idx), 2)]
    else:
        groups = [{k} for k in idx]
    rnd.shuffle(groups)
    removed = set()
    for gset in groups:
        t = copy.deepcopy(spec)
        t['constraints'] = [c for j, c in enumerate(spec['constraints']) if j not in removed | gset]
        if progress(t) == 81:
            removed |= gset; print('removed', [spec['constraints'][i] for i in gset], flush=True)
    spec['constraints'] = [c for j, c in enumerate(spec['constraints']) if j not in removed]
    sols, st = Puzzle(spec).count_solutions(limit=2)
    print('clues added:', len(spec['constraints']) - base_n, 'solutions:', len(sols), st)
    json.dump(spec, open(out, 'w'), indent=1)

main()
