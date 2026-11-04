"""Greedy given-placement helper: python3 givens.py spec.json [seed] [--prefer r1c1,r2c2]
Picks a solution, adds givens at the most ambiguous cells until unique, then removes redundant ones."""
import sys, json, random, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *

def count(spec, limit=2, sample=False):
    return Puzzle(spec).count_solutions(limit=limit)[0]

def main():
    spec = json.load(open(sys.argv[1]))
    seed = int(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else 0
    rnd = random.Random(seed)
    sols = count(spec, limit=60)
    target = rnd.choice(sols)
    spec = copy.deepcopy(spec)
    spec.setdefault('givens', {})
    while True:
        sols = count(spec, limit=40)
        sols = [s for s in sols]
        if len(sols) == 1:
            target = sols[0]; break
        if target not in sols:
            target = sols[0]
        # most ambiguous cell
        best = max(sols[0], key=lambda a: (len({s[a] for s in sols}), rnd.random()))
        spec['givens'][name(best)] = target[best]
        print('add', name(best), target[best], 'ambiguity', len({s[best] for s in sols}), flush=True)
    # minimise
    keys = list(spec['givens'])
    rnd.shuffle(keys)
    for k in keys:
        trial = copy.deepcopy(spec); del trial['givens'][k]
        if len(count(trial)) == 1:
            spec = trial; print('removed', k, flush=True)
    print(json.dumps(spec['givens']))
    print(len(spec['givens']), 'givens')
    json.dump(spec, open(sys.argv[1].replace('.json', '_g.json'), 'w'), indent=1)

main()
