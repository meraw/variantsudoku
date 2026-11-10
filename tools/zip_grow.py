"""Run 7: zipper + Dutch whisper growth around a kept core (lines in the base spec are never pruned).
python3 zip_grow.py base.json out.json seed [dutch_bonus] [minlen] [maxlen]
Proposes clean straight/one-turn lines that some sampled solution satisfies, scored by the candidates my logical solver
removes (Dutch whispers get dutch_bonus); a new line never touches a line of the same colour; a given is allowed as a
penalised fallback when no line removes at least 5 candidates. Stops when the tier-2 solve finishes, then prunes lines and givens."""
"""python3 autozip.py base.json out.json seed [dutch_bonus] [minlen] [maxlen]
core lines in base are kept; adds clean-shaped zipper/dutch lines until my logical solver finishes; prunes."""
import sys, json, random, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from open_clues import samples, feasible, unique, logic_ok
from open_lines import segs_of, crosses
base,out,seed=sys.argv[1],sys.argv[2],int(sys.argv[3])
BON=float(sys.argv[4]) if len(sys.argv)>4 else 1.5
mn=int(sys.argv[5]) if len(sys.argv)>5 else 3; mx=int(sys.argv[6]) if len(sys.argv)>6 else 6
rnd=random.Random(seed)
spec=json.load(open(base))
for c in spec['constraints']: c['keep']=True
DIRS=[(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
def okv(t,v):
    if t=='zipper':
        n=len(v); s={v[i]+v[n-1-i] for i in range(n//2)}
        if n%2: s.add(v[n//2])
        return len(s)==1
    return all(abs(a-b)>=4 for a,b in zip(v,v[1:]))
def shape(diag):
    Lh=rnd.randint(mn,mx); p=[(rnd.randrange(9),rnd.randrange(9))]
    d1=rnd.choice(DIRS); l1=rnd.randint(1,Lh-1)
    d2=rnd.choice([d for d in DIRS if d!=d1 and d!=(-d1[0],-d1[1])])
    for i in range(Lh-1):
        d=d1 if i<l1 else d2; n=(p[-1][0]+d[0],p[-1][1]+d[1])
        if not(0<=n[0]<9 and 0<=n[1]<9) or n in p: return None
        p.append(n)
    if any(crosses(x,y) for x in segs_of(p) for y in diag): return None
    return p
while True:
    pz=Puzzle(spec); L=Logic(pz); cand=L.init_cands(); L.propagate(cand,2)
    left=sum(len(x) for x in cand.values()); print('lines',len(spec['constraints']),'left',left,flush=True)
    if left==81: break
    used={}; tused={'zipper':set(),'dutch':set()}
    for c in spec['constraints']:
        for x in c['cells']: used[parse(x)]=used.get(parse(x),0)+1; tused[c['type']].add(parse(x))
    diag=[d for c in spec['constraints'] for d in segs_of([parse(x) for x in c['cells']])]
    sm=samples(spec,30,rnd); cands={}
    for it in range(8000):
        p=shape(diag)
        if not p or sum(used.get(a,0)>0 for a in p)>1: continue
        if any(used.get(a,0)>=2 for a in p): continue
        for t in ('zipper','dutch'):
            if set(p)&tused[t]: continue  # clean: never touch a line of the same colour
            if any(okv(t,[g[a] for a in p]) for g in sm): cands[(t,tuple(p))]=1
    items=list(cands); rnd.shuffle(items); sc=[]
    for t,p in items[:350]:
        sp2=copy.deepcopy(spec); sp2['constraints'].append({"type":t,"cells":[name(a) for a in p]})
        c2={a:set(x) for a,x in cand.items()}
        try: Logic(Puzzle(sp2)).propagate(c2,2)
        except Contradiction: continue
        g=left-sum(len(x) for x in c2.values())
        sc.append((g*(BON if t=='dutch' else 1)/(1+0.08*len(p)),rnd.random(),sp2,t,p))
    sc.sort(key=lambda x:(-x[0],x[1]))
    if not sc or sc[0][0]<5:  # fallback: a given digit (penalised)
        for a_ in L.cells:
            if len(cand[a_])<2: continue
            for val in {g[a_] for g in sm}:
                c2={b:set(x) for b,x in cand.items()}; c2[a_]={val}
                try: Logic(pz).propagate(c2,2)
                except Contradiction: continue
                sp2=copy.deepcopy(spec); sp2.setdefault('givens',{})[name(a_)]=val
                sc.append(((left-sum(len(x) for x in c2.values()))/4,rnd.random(),sp2,'given',[a_]))
        sc.sort(key=lambda x:(-x[0],x[1]))
    top=sc[:3]; rnd.shuffle(top)
    for s_,_,sp2,t,p in top+sc[3:]:
        if feasible(sp2):
            spec=sp2; print('  add',round(s_,1),t,' '.join(name(a) for a in p),flush=True); break
    else: print('no move'); sys.exit()
assert unique(spec)
i=len(spec['constraints'])-1
while i>=0:
    c=spec['constraints'][i]
    if c.get('keep'): i-=1; continue
    sp2=copy.deepcopy(spec); del sp2['constraints'][i]
    ok,r2=logic_ok(sp2)
    if ok and unique(sp2): print('  drop',c['type'],c['cells'],flush=True); spec=sp2
    i-=1
for g_ in list(spec.get('givens',{})):
    sp2=copy.deepcopy(spec); del sp2['givens'][g_]
    ok,r2=logic_ok(sp2)
    if ok and unique(sp2): print('  drop given',g_,flush=True); spec=sp2
ok,r2=logic_ok(spec)
print('givens',spec.get('givens'))
print('FINAL lines',len(spec['constraints']),'tier2',r2,ok)
for c in spec['constraints']: c.pop('keep',None)
json.dump(spec,open(out,'w'),indent=1)
