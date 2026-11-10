"""Run 7: python3 ones_givens.py spec.json k part nparts  -- for every k-subset of the cells holding 1 in the (unique)
solution, report uniqueness and the tier-2 logical result with those 1s as the only givens (used for Carry the One)."""
import sys, json, itertools
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
spec=json.load(open(sys.argv[1])); k=int(sys.argv[2]); part=int(sys.argv[3]); npart=int(sys.argv[4])
pz=Puzzle(spec); sol=pz.count_solutions(limit=2)[0][0]
ones=sorted(name(a) for a in sol if sol[a]==1)
for i,sub in enumerate(itertools.combinations(ones,k)):
    if i%npart!=part: continue
    sp=json.loads(json.dumps(spec)); sp['givens']={g:1 for g in sub}
    p2=Puzzle(sp); s,st=p2.count_solutions(limit=2)
    if len(s)!=1: continue
    L=Logic(p2); r,c=L.solve(max_tier=2)
    print('RES',r,L.tier_counts[2],sub,max([x[1] for x in L.gac_sizes] or [0]),flush=True)
