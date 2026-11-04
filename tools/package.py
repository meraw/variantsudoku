"""Package a finished puzzle.
python3 package.py spec.json puzzles/<slug> <difficulty 1-5> "<difficulty reasoning>"
Writes puzzle.json (spec + solution + links), grid.svg, solution.svg, verification.md.
Refuses to write anything unless CP-SAT proves exactly one solution."""
import sys, json, os, time, datetime
from collections import Counter
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from ortools.sat.python import cp_model


def main():
    src, outdir, diff, why = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    spec = json.load(open(src))
    pz = Puzzle(spec)
    t0 = time.time()
    sols, st = pz.count_solutions(limit=2, time_limit=600)
    t1 = time.time() - t0
    if not (len(sols) == 1 and st == 'OPTIMAL'):
        print('NOT UNIQUE / NOT PROVEN:', len(sols), st); sys.exit(1)
    sol = sols[0]
    viol = pz.check(sol)
    assert not viol, viol
    # second, independent proof: forbid the solution and show infeasibility
    sols2, st2 = count_with_forbid(pz, sol)
    L = Logic(pz); res, cand = L.solve(max_tier=3)
    agree = res == 'solved' and all(next(iter(cand[a])) == sol[a] for a in cand)
    os.makedirs(outdir, exist_ok=True)
    lk = links(pz, sol)
    out = dict(spec)
    out['solution'] = grid_str(sol).split('\n')
    out['links'] = lk
    out['difficulty'] = diff
    json.dump(out, open(os.path.join(outdir, 'puzzle.json'), 'w'), indent=1)
    open(os.path.join(outdir, 'grid.svg'), 'w').write(render_svg(pz))
    open(os.path.join(outdir, 'solution.svg'), 'w').write(render_svg(pz, solution=sol))
    cnt = Counter(nm for nm, _, _ in L.trace)
    rep = [f"# Verification report — {spec.get('title','')}", '',
           f"Generated {datetime.date.today().isoformat()} by `tools/package.py`.", '',
           '## Uniqueness (solver-confirmed)', '',
           f"1. **CP-SAT enumeration** (OR-Tools {__import__('ortools').__version__}): searched for up to 2 solutions; "
           f"found **{len(sols)}**, search status `{st}` (search space exhausted) in {t1:.2f}s.",
           f"2. **Forbidden-solution re-solve**: same model plus a constraint that at least one cell differs from the found solution; "
           f"status `{st2}` ({len(sols2)} solutions).",
           f"3. **Constraint-by-constraint check** of the solution grid with an independent checker (`Puzzle.check`): "
           f"{'no violations' if not viol else viol}.", '',
           '## Logical solvability', '',
           f"Solver: `tools/vs.py` `Logic` — candidate elimination only. Tier 1 = naked/hidden singles + pairwise constraint "
           f"consistency; tier 2 = locked candidates, naked/hidden pairs & triples, generalised pointing, parity counting "
           f"(lines that force alternate parity vs. 4 evens per house), whole-constraint consistency (enumerate fills of one "
           f"cage/line against current candidates); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.", '',
           f"Result: **{res}** — tier rounds used: {L.tier_counts}. "
           f"{'Logical solve reaches the same grid as CP-SAT.' if agree else 'Logical solve did NOT complete.'}", '',
           'Technique usage (number of rounds in which each technique made progress):', '']
    for k, v in cnt.most_common():
        rep.append(f"- {k}: {v}")
    rep += ['', f"Logical solvability: {'verified with the solver above (no guessing, no tier-3 contradiction tests).' if agree and L.tier_counts[3] == 0 else ('verified only with tier-3 contradiction tests (short bifurcation).' if agree else 'not verified')}",
            'Note: the solver is a program, not a human test-solve; its techniques are human-style but '
            'whole-constraint enumeration can be heavier than a human would like.', '',
            '## Difficulty estimate', '', f"**{diff} / 5** — {why}", '',
            'Method: 1 = singles + pairwise only; 2 = up to 5 tier-2 rounds; 3 = 6-15 tier-2 rounds; '
            '4 = more than 15 tier-2 rounds or 1-3 tier-3 tests; 5 = many tier-3 tests or not solved logically. '
            'Adjusted by at most one step for rule novelty / setter judgement (stated above).', '',
            '## Solution', '', '```', grid_str(sol), '```']
    open(os.path.join(outdir, 'verification.md'), 'w').write('\n'.join(rep) + '\n')
    print('OK', outdir, res, L.tier_counts)
    print(lk['sudokupad'][:100])


def count_with_forbid(pz, sol):
    from ortools.sat.python import cp_model as cm
    m = cm.CpModel()
    v = {(r, k): m.NewIntVar(1, 9, f"v{r}{k}") for r in range(N) for k in range(N)}
    for h in pz.houses:
        m.AddAllDifferent([v[x] for x in h])
    for a, b in pz.extra_sees:
        m.Add(v[a] != v[b])
    for a, d in pz.givens.items():
        m.Add(v[a] == d)
    for a, b, rel in pz.pairs:
        f = PAIR_REL[rel]
        m.AddAllowedAssignments([v[a], v[b]], [(x, y) for x in DIGITS for y in DIGITS if f(x, y)])
    for c in pz.cons:
        t, rc = c['type'], c['rc']
        if t == 'killer':
            m.AddAllDifferent([v[x] for x in rc])
            if 'sum' in c:
                m.Add(sum(v[x] for x in rc) == c['sum'])
        elif t == 'renban':
            m.AddAllDifferent([v[x] for x in rc])
            mx = m.NewIntVar(1, 9, ''); mn = m.NewIntVar(1, 9, '')
            m.AddMaxEquality(mx, [v[x] for x in rc]); m.AddMinEquality(mn, [v[x] for x in rc])
            m.Add(mx - mn == len(rc) - 1)
        elif t == 'arrow':
            circ = sum(v[x] * 10 ** (len(c['crc']) - 1 - i) for i, x in enumerate(c['crc']))
            m.Add(sum(v[x] for x in rc) == circ)
    diffs = []
    for a, d in sol.items():
        b = m.NewBoolVar('')
        m.Add(v[a] != d).OnlyEnforceIf(b)
        m.Add(v[a] == d).OnlyEnforceIf(b.Not())
        diffs.append(b)
    m.AddBoolOr(diffs)
    s = cm.CpSolver(); s.parameters.max_time_in_seconds = 600
    st = s.Solve(m)
    return ([1] if st in (cm.OPTIMAL, cm.FEASIBLE) else []), s.StatusName(st)


main()
