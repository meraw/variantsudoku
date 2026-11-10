"""Run 7. python3 line_replace.py spec.json 'cells of line to drop' seed [maxtests]: clean straight/L replacements that keep unique + tier-2 solve"""
import sys, json, random, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from open_clues import samples, unique, logic_ok
from open_lines import segs_of, crosses
args=[x for x in sys.argv if not x.startswith('--')]
spec=json.load(open(args[1])); drop=args[2].split(); rnd=random.Random(int(args[3])); maxt=int(args[4]) if len(args)>4 else 40
spec['constraints']=[c for c in spec['constraints'] if c['cells']!=drop]
used={}; tused={'zipper':set(),'dutch':set()}
for c in spec['constraints']:
    for x in c['cells']: used[parse(x)]=used.get(parse(x),0)+1; tused[c['type']].add(parse(x))
STR='--straight' in sys.argv
diag=[d for c in spec['constraints'] for d in segs_of([parse(x) for x in c['cells']])]
sm=samples(spec,60,rnd)
def okv(t,v):
    if t=='zipper':
        n=len(v); s={v[i]+v[n-1-i] for i in range(n//2)}
        if n%2: s.add(v[n//2])
        return len(s)==1
    return all(abs(a-b)>=4 for a,b in zip(v,v[1:]))
D=[(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
shapes=set()
for r in range(9):
  for c in range(9):
    for d1 in D[:4]:
      for L1 in range(1,5):
        for d2 in [None]+[d for d in D[:4] if d!=d1 and d!=(-d1[0],-d1[1])]:
          for L2 in ([0] if d2 is None else range(1,4)):
            p=[(r,c)]; ok=True
            for i in range(L1+L2):
                d=d1 if i<L1 else d2; n=(p[-1][0]+d[0],p[-1][1]+d[1])
                if not(0<=n[0]<9 and 0<=n[1]<9) or n in p: ok=False; break
                p.append(n)
            if ok and 3<=len(p)<=5 and sum(used.get(a,0)>0 for a in p)<=1: shapes.add(tuple(p))
pz=Puzzle(spec); L=Logic(pz); cand=L.init_cands(); L.propagate(cand,2); left=sum(len(x) for x in cand.values())
sc=[]
for p in shapes:
    for t in ('zipper','dutch'):
        if t=='zipper' and p[::-1] in shapes and p>p[::-1]: continue
        if t=='dutch' and p>p[::-1]: continue
        if set(p)&tused[t]: continue
        if STR and not (len({x[0] for x in p})==1 or len({x[1] for x in p})==1): continue
        if not any(okv(t,[g[a] for a in p]) for g in sm): continue
        sp2=copy.deepcopy(spec); sp2['constraints'].append({"type":t,"cells":[name(a) for a in p]})
        c2={a:set(x) for a,x in cand.items()}
        try: Logic(Puzzle(sp2)).propagate(c2,2)
        except Contradiction: continue
        sc.append((left-sum(len(x) for x in c2.values()),t,p,sp2))
sc.sort(key=lambda x:-x[0]); print('candidates',len(sc),flush=True)
for g,t,p,sp2 in sc[:maxt]:
    ok,r2=logic_ok(sp2)
    if ok and unique(sp2): print('WORKS',g,t,' '.join(name(a) for a in p),'tier2',r2,flush=True)
