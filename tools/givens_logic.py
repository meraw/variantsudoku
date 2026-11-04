"""Logic-guided given placement.
python3 givens_logic.py spec.json out.json [seed] [max_tier]
Picks a solution of the (given-free) constraint set, then greedily adds the given
that maximises tier-<=2 logical progress until the logical solver finishes; then
removes givens that are not needed for the logical solve. Confirms uniqueness."""
import sys, json, random, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *

def progress(spec, tier):
    lg = Logic(Puzzle(spec))
    try:
        res, c = lg.solve(max_tier=tier)
    except Contradiction:
        return None, None
    if res == 'contradiction':
        return None, None
    return sum(len(v) for v in c.values()), c

def main():
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    tier = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    rnd = random.Random(seed)
    sols, _ = Puzzle(spec).count_solutions(limit=200)
    target = rnd.choice(sols)
    spec = copy.deepcopy(spec); spec.setdefault('givens', {})
    while True:
        sc, c = progress(spec, tier)
        if sc == 81:
            break
        opts = [a for a in c if len(c[a]) > 1]
        best = None
        for a in opts:
            t = copy.deepcopy(spec); t['givens'][name(a)] = target[a]
            s2, _ = progress(t, tier)
            if s2 is not None and (best is None or s2 < best[0] or (s2 == best[0] and rnd.random() < 0.3)):
                best = (s2, a)
        spec['givens'][name(best[1])] = target[best[1]]
        print('add', name(best[1]), target[best[1]], '->', best[0], flush=True)
    keys = list(spec['givens']); rnd.shuffle(keys)
    for k in keys:
        t = copy.deepcopy(spec); del t['givens'][k]
        s2, _ = progress(t, tier)
        if s2 == 81:
            spec = t; print('removed', k, flush=True)
    sols, st = Puzzle(spec).count_solutions(limit=2)
    print('givens:', len(spec['givens']), spec['givens'], 'solutions:', len(sols), st)
    json.dump(spec, open(out, 'w'), indent=1)

main()
