"""Run 7: python3 eq_maxlines.py seed [min_lines] [seconds] -- a grid with as many rows/columns as possible that are
correct sums ABC + DEF = GHI (either orientation); with min_lines it only asks for a grid with at least that many."""
import sys, random
from ortools.sat.python import cp_model
seed=int(sys.argv[1]); minr=int(sys.argv[2]) if len(sys.argv)>2 else 0
m=cp_model.CpModel(); v=[[m.NewIntVar(1,9,'') for _ in range(9)] for _ in range(9)]
for i in range(9):
    m.AddAllDifferent(v[i]); m.AddAllDifferent([v[r][i] for r in range(9)])
    m.AddAllDifferent([v[3*(i//3)+a][3*(i%3)+b] for a in range(3) for b in range(3)])
num=lambda cs:100*cs[0]+10*cs[1]+cs[2]
lits={}
for kind in 'RC':
    for i in range(9):
        line=v[i] if kind=='R' else [v[r][i] for r in range(9)]
        seg=[line[0:3],line[3:6],line[6:9]]
        for res in (0,2):
            b=m.NewBoolVar(''); lits[(kind,i,res)]=b
            o=[seg[j] for j in range(3) if j!=res]
            m.Add(num(o[0])+num(o[1])==num(seg[res])).OnlyEnforceIf(b)
if minr: m.Add(sum(lits.values())>=minr)
else: m.Maximize(sum(lits.values()))
s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=float(sys.argv[3]) if len(sys.argv)>3 else 60; s.parameters.random_seed=seed; s.parameters.num_workers=4
st=s.Solve(m)
print(s.StatusName(st))
print(sorted(k for k,b in lits.items() if s.Value(b)))
for r in range(9): print(''.join(str(s.Value(x)) for x in v[r]))
