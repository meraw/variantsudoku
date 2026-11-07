"""Run 4: greedy 180-degree symmetric given pairs (c, rot c) for designs whose solutions include one with g(rot c) = 10 - g(c).
python3 sym_givens.py spec.json [...]  (tries seeds 0-2, writes spec_sg<seed>.json, then prunes unneeded pairs)"""
import sys, json, random, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
rot = lambda a: (8 - a[0], 8 - a[1])

def prog(spec):
    L = Logic(Puzzle(spec))
    try:
        r, c = L.solve(2)
    except Exception:
        return None, None, None
    if r == 'contradiction': return None, None, None
    return sum(len(v) for v in c.values()), c, L

def run(f, seed=0, single=False):
    rnd = random.Random(seed)
    spec = json.load(open(f)); spec['givens'] = {}
    sols, st = Puzzle(spec).count_solutions(limit=10)
    g = None
    for s in sols:
        if all(s[rot(a)] == 10 - s[a] for a in s): g = s
    if g is None: return None
    while True:
        sc, c, _ = prog(spec)
        if sc == 81: break
        best = []
        for a in g:
            if a > rot(a) or g[a] == 5 or name(a) in spec['givens']: continue
            t = copy.deepcopy(spec); t['givens'][name(a)] = g[a]; t['givens'][name(rot(a))] = g[rot(a)]
            s2, _, _ = prog(t)
            if s2 is not None: best.append((s2, rnd.random(), a))
        best.sort()
        a = best[0][2] if seed == 0 else rnd.choice(best[:3])[2]
        spec['givens'][name(a)] = g[a]; spec['givens'][name(rot(a))] = g[rot(a)]
    keys = [k for k in spec['givens'] if parse(k) < rot(parse(k))]; rnd.shuffle(keys)
    for k in keys:
        t = copy.deepcopy(spec); del t['givens'][k]; del t['givens'][name(rot(parse(k)))]
        if prog(t)[0] == 81: spec = t
    sc, c, L = prog(spec)
    sols, st = Puzzle(spec).count_solutions(limit=2)
    return spec, len(sols), L.tier_counts

if __name__ == '__main__':
    for f in sys.argv[1:]:
        for seed in range(3):
            r = run(f, seed)
            if r is None: print(f, 'no symmetric solution'); break
            spec, n, tc = r
            print(f, seed, 'givens', len(spec['givens']), spec['givens'], 'sols', n, tc, flush=True)
            json.dump(spec, open(f.replace('.json', f'_sg{seed}.json'), 'w'))
