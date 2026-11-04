"""Usage: python3 check.py spec.json [--logic] [--sample N]
Reports solution count (CP-SAT, limit 2), differing cells, and optional logical-solver result."""
import sys, json
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *

def main():
    path = sys.argv[1]
    pz = load(path)
    sols, st = pz.count_solutions(limit=int(sys.argv[sys.argv.index('--sample')+1]) if '--sample' in sys.argv else 2)
    print('solutions found:', len(sols), 'status:', st)
    if len(sols) >= 2:
        fixed = [a for a in sols[0] if all(s[a] == sols[0][a] for s in sols)]
        print('cells fixed across found solutions:', len(fixed))
        g = sols[0]
        print('\n'.join(''.join(str(g[(r,k)]) if (r,k) in fixed else '.' for k in range(9)) for r in range(9)))
    elif sols:
        print(grid_str(sols[0]))
        print('violations:', pz.check(sols[0]))
    if '--logic' in sys.argv:
        L = Logic(pz)
        res, cand = L.solve(max_tier=3)
        print('logic:', res, 'tier steps:', L.tier_counts)
        if res != 'solved':
            print(cand_str(cand))
        L2 = Logic(pz); r2, _ = L2.solve(max_tier=2)
        print('without tier3:', r2)
        L1 = Logic(pz); r1, _ = L1.solve(max_tier=1)
        print('tier1 only:', r1)

main()
