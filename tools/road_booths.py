"""Run 17 (abandoned design, kept for the record): random "toll roads" for a region-sum line through all nine boxes in a
fixed box order (serp = 1-2-3-6-5-4-7-8-9, spiral = 1-2-3-6-9-8-7-4-5), 2-4 cells per box, every box crossing an
orthogonal step, plus a sum-less 2-cell killer cage ("toll booth") on every crossing. Writes rg_<order>_<seed>_<k>.json;
the booth totals were then chosen with open_clues.py --no-sandwich (see the run-17 log).
python3 road_booths.py seed count serp|spiral"""
import json, sys, random
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
ORDERS={'serp':[0,1,2,5,4,3,6,7,8],'spiral':[0,1,2,5,8,7,6,3,4]}
def boxcells(b): return [(3*(b//3)+i,3*(b%3)+j) for i in range(3) for j in range(3)]
def gen(rnd, order, lens):
    path=[]
    for bi,b in enumerate(order):
        L=lens[bi]; cells=set(boxcells(b))
        for _ in range(200):
            if bi==0:
                start=rnd.choice(sorted(cells))
            else:
                last=path[-1]
                opts=[(last[0]+dr,last[1]+dc) for dr,dc in ((0,1),(1,0),(0,-1),(-1,0))]
                opts=[o for o in opts if o in cells]
                if not opts: return None
                start=rnd.choice(opts)
            seg=[start]; ok=True
            while len(seg)<L:
                o=[(seg[-1][0]+dr,seg[-1][1]+dc) for dr in (-1,0,1) for dc in (-1,0,1) if (dr or dc)]
                o=[x for x in o if x in cells and x not in seg]
                # prefer orthogonal
                if not o: ok=False;break
                orth_=[x for x in o if abs(x[0]-seg[-1][0])+abs(x[1]-seg[-1][1])==1]
                seg.append(rnd.choice(orth_ if orth_ and rnd.random()<0.6 else o))
            if not ok: continue
            # exit must be possible orthogonally into next box
            if bi<len(order)-1:
                nb=set(boxcells(order[bi+1]))
                if not any((seg[-1][0]+dr,seg[-1][1]+dc) in nb for dr,dc in ((0,1),(1,0),(0,-1),(-1,0))): continue
            path+=seg; break
        else: return None
    return path
rnd=random.Random(int(sys.argv[1])); n=int(sys.argv[2]); order=ORDERS[sys.argv[3]]
k=0
while k<n:
    lens=[rnd.choice([2,3,3,4]) for _ in range(9)]
    if 1 in lens: pass
    p=gen(rnd,order,lens)
    if not p: continue
    d={"constraints":[{"type":"regionsum","cells":[name(a) for a in p]}]}
    for a,b in zip(p,p[1:]):
        if box(a)!=box(b): d['constraints'].append({"type":"killer","cells":[name(a),name(b)]})
    # crossings of diagonal steps inside path? skip check
    pz=Puzzle(d); s,_=pz.count_solutions(limit=1,time_limit=20)
    if not s: continue
    json.dump(d,open(f'rg_{sys.argv[3]}_{sys.argv[1]}_{k}.json','w'))
    k+=1
