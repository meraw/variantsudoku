"""Run 7: soundness tests for the zipper, Dutch whisper and equation logic steps (the true digit is never removed, on full
random grids and on partial grids) and CP-SAT model vs checker agreement."""
import sys, random, json
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from ortools.sat.python import cp_model
rnd=random.Random(7)
def rand_grid(seed):
    m=cp_model.CpModel(); v={(r,c):m.NewIntVar(1,9,'') for r in range(9) for c in range(9)}
    P=Puzzle({'constraints':[]})
    for h in P.houses: m.AddAllDifferent([v[x] for x in h])
    r2=random.Random(seed); m.Minimize(sum(r2.randint(-9,9)*v[a] for a in v))
    s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=0.5; s.parameters.random_seed=seed; s.Solve(m)
    return {a:s.Value(v[a]) for a in v}
D=[(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
def rpath(L):
    p=[(rnd.randrange(9),rnd.randrange(9))]
    while len(p)<L:
        o=[(p[-1][0]+a,p[-1][1]+b) for a,b in D]; o=[x for x in o if 0<=x[0]<9 and 0<=x[1]<9 and x not in p]
        if not o: return None
        p.append(rnd.choice(o))
    return p
bad=0; tested=0; agree=0
for gi in range(30):
    g=rand_grid(gi)
    cons=[]
    for _ in range(400):
        p=rpath(rnd.randint(3,8))
        if not p: continue
        v=[g[a] for a in p]
        n=len(v); s={v[i]+v[n-1-i] for i in range(n//2)}
        if n%2: s.add(v[n//2])
        if len(s)==1: cons.append({'type':'zipper','cells':[name(a) for a in p]})
        if all(abs(x-y)>=4 for x,y in zip(v,v[1:])): cons.append({'type':'dutch','cells':[name(a) for a in p]})
    for k in range(9):
        for res in (0,2):
            for line in ('r%d'%(k+1),'c%d'%(k+1)):
                c={'type':'equation','line':line,'result':res}
                if Puzzle({'constraints':[c]}).check(g)==[]: cons.append(c)
    cons=rnd.sample(cons,min(len(cons),14))
    pz=Puzzle({'constraints':cons}); assert pz.check(g)==[], pz.check(g)
    L=Logic(pz); cand=L.init_cands()
    try: L.propagate(cand,2)
    except Contradiction: bad+=1; print('contradiction on true grid!'); continue
    tested+=1
    if any(g[a] not in cand[a] for a in cand): bad+=1; print('LOST true digit', gi)
    # model vs checker: forbid nothing, the true grid must be feasible in CP-SAT
    m,v=pz.build_model()
    for a in g: m.Add(v[a]==g[a])
    s=cp_model.CpSolver(); st=s.Solve(m); agree+= st in (cp_model.OPTIMAL,cp_model.FEASIBLE)
    print(gi,len(cons),sum(c['type']=='equation' for c in cons),sum(len(x) for x in cand.values()),flush=True)
print('tested',tested,'bad',bad,'model accepts true grid',agree)
# checker vs model on random grids that violate: sample grids from model of single constraint and check
mis=0
for t in range(200):
    g=rand_grid(1000+t); p=None
    while not p: p=rpath(rnd.randint(3,7))
    typ=rnd.choice(['zipper','dutch'])
    c={'type':typ,'cells':[name(a) for a in p]}; pz=Puzzle({'constraints':[c]})
    m,v=pz.build_model()
    for a in g: m.Add(v[a]==g[a])
    st=cp_model.CpSolver().Solve(m); ok_model= st in (cp_model.OPTIMAL,cp_model.FEASIBLE)
    if ok_model != (pz.check(g)==[]): mis+=1
print('model/checker disagreements on 200 random (grid,line):',mis)

# equations: grids forced to satisfy 2-3 random equations; then logic on those equations + other random ones
bad=0; n=0; mis=0
for t in range(40):
    eqs=[]
    while len(eqs)<rnd.randint(2,3):
        k=rnd.randrange(9); eqs.append({'type':'equation','line':rnd.choice('rc')+str(k+1),'result':rnd.choice((0,2))})
    pz=Puzzle({'constraints':eqs}); sols,st=pz.count_solutions(limit=1,time_limit=10)
    if not sols: continue
    g=sols[0]; n+=1
    L=Logic(pz); cand=L.init_cands()
    try: L.propagate(cand,2)
    except Contradiction: bad+=1; continue
    if any(g[a] not in cand[a] for a in cand): bad+=1
    # partial grid: reveal 30 random cells, logic must keep the truth
    cand=L.init_cands()
    for a in rnd.sample(list(g),30): cand[a]={g[a]}
    try: L.propagate(cand,2)
    except Contradiction: bad+=1; continue
    if any(g[a] not in cand[a] for a in cand): bad+=1
    # checker vs model on a random other grid
    g2=rand_grid(5000+t); m,v=pz.build_model()
    for a in g2: m.Add(v[a]==g2[a])
    ok=cp_model.CpSolver().Solve(m) in (cp_model.OPTIMAL,cp_model.FEASIBLE)
    mis+= ok != (pz.check(g2)==[])
    mis+= pz.check(g)!=[]
print('equation grids',n,'bad',bad,'model/checker disagreements',mis)
