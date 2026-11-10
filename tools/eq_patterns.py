"""Run 7: which rows/columns can be "Carry the One" sums together.
python3 eq_patterns.py feas  <pattern> ...   feasibility with every line's orientation left free (R0..R8 / C0..C8, 0-based)
python3 eq_patterns.py enum  <pattern>       enumerate all grids (orientation free) and count them per orientation
                                             (orientation 2 = result is the last third, 0 = the first third)"""
import sys
from collections import Counter
from ortools.sat.python import cp_model
pats={'ttt':['R1','R4','R7','C1','C4','C7'],'odd':['R0','R2','R6','R8','C0','C2','C6','C8'],
      'plus':['R3','R4','R5','C3','C4','C5'],'even':['R1','R3','R5','R7','C1','C3','C5','C7'],
      'fc+':['R0','R4','R8','C0','C4','C8','R2','R6'],'fc+c':['R0','R4','R8','C0','C4','C8','C2','C6'],
      'band':['R0','R1','R2','C6','C7','C8'],'diagbands':['R0','R1','R2','C0','C1','C2']}
def feas(lines, tl=60):
    m=cp_model.CpModel(); v=[[m.NewIntVar(1,9,'') for _ in range(9)] for _ in range(9)]
    for i in range(9):
        m.AddAllDifferent(v[i]); m.AddAllDifferent([v[r][i] for r in range(9)])
        m.AddAllDifferent([v[3*(i//3)+a][3*(i%3)+b] for a in range(3) for b in range(3)])
    num=lambda cs:100*cs[0]+10*cs[1]+cs[2]
    for l in lines:
        i=int(l[1:]); line=v[i] if l[0]=='R' else [v[r][i] for r in range(9)]
        seg=[line[0:3],line[3:6],line[6:9]]
        b=m.NewBoolVar('')
        m.Add(num(seg[0])+num(seg[1])==num(seg[2])).OnlyEnforceIf(b)
        m.Add(num(seg[1])+num(seg[2])==num(seg[0])).OnlyEnforceIf(b.Not())
    s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=tl; s.parameters.num_workers=4
    return s.StatusName(s.Solve(m))

def enum(lines, limit=20000, tl=200):
    m=cp_model.CpModel(); v=[[m.NewIntVar(1,9,'') for _ in range(9)] for _ in range(9)]
    for i in range(9):
        m.AddAllDifferent(v[i]); m.AddAllDifferent([v[r][i] for r in range(9)])
        m.AddAllDifferent([v[3*(i//3)+a][3*(i%3)+b] for a in range(3) for b in range(3)])
    num=lambda cs:100*cs[0]+10*cs[1]+cs[2]
    bs=[]
    for l in lines:
        i=int(l[1:]); line=v[i] if l[0]=='R' else [v[r][i] for r in range(9)]
        seg=[line[0:3],line[3:6],line[6:9]]
        b=m.NewBoolVar('')
        m.Add(num(seg[0])+num(seg[1])==num(seg[2])).OnlyEnforceIf(b)
        m.Add(num(seg[1])+num(seg[2])==num(seg[0])).OnlyEnforceIf(b.Not())
        bs.append(b)
    s=cp_model.CpSolver(); s.parameters.enumerate_all_solutions=True; s.parameters.max_time_in_seconds=tl
    C=Counter(); n=[0]
    class CB(cp_model.CpSolverSolutionCallback):
        def on_solution_callback(self):
            C[tuple(2 if self.Value(b) else 0 for b in bs)]+=1; n[0]+=1
            if n[0]>=limit: self.StopSearch()
    st=s.Solve(m,CB()); return n[0], s.StatusName(st), C


if __name__ == '__main__':
    mode, ks = sys.argv[1], sys.argv[2:]
    for k in ks:
        if mode == 'feas':
            print(k, feas(pats[k]), flush=True)
        else:
            n, st, C = enum(pats[k])
            print(k, n, st, 'orientations', len(C)); print(sorted(C.items(), key=lambda x: x[1])[:12])
