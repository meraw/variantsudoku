"""Package a finished puzzle.
python3 package.py spec.json puzzles/<slug> <difficulty 1-5> "<difficulty reasoning>"
Writes puzzle.json (spec + solution + links), grid.svg, solution.svg, verification.md.
Refuses to write anything unless CP-SAT proves exactly one solution."""
import sys, json, os, re, time, datetime
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
           f"(lines that force alternate parity vs. 4 evens per house), seesaw min/max bounds, Fibonacci-line parity patterns vs. 4 evens per house, the law of leftovers on jigsaw grids (run 9), whole-constraint consistency (enumerate fills of one "
           f"cage/line against current candidates; sandwiches: every placement of the 1 and 9 with every set of sandwiched digits; "
           f"between lines: every pair of end digits; long bridges: box segments with the 45 rule; X-sums and skyscrapers (run 6): an exact walk along the whole row/column, tracking the digits used and X or the number of visible digits; odometers (run 6): every fill of the line; zipper lines (run 7): every total with every fill of the pairs; equations (run 7): every still-possible sum ABC + DEF = GHI of the row/column); tier 3 = single-candidate contradiction tests propagated with tiers 1-2.", '',
           f"Result: **{res}** — tier rounds used: {L.tier_counts}. "
           f"{'Logical solve reaches the same grid as CP-SAT.' if agree else 'Logical solve did NOT complete.'}", '',
           'Technique usage (number of rounds in which each technique made progress):', '']
    for k, v in cnt.most_common():
        rep.append(f"- {k}: {v}")
    heavy = [(t, sz, solved) for t, sz, solved in L.gac_sizes if solved > 0 and sz > 500]
    rep += ['', f"Whole-constraint steps that made progress: {len(L.gac_sizes)}. Steps after the first placed digit that enumerated "
            f"more than 500 combinations: {len(heavy)}" + (" — " + ", ".join(f"{t} ({sz} combos, {solved} cells solved)" for t, sz, solved in heavy) if heavy else "") + ".",
            "(For seesaws the number is the count of balancing fills that survive the current candidates, i.e. the cases a solver would have to check.) "
            "(Calibration from owner feedback: puzzle 002 had whisper enumerations of 1,000-6,000 combinations against "
            "partly-filled candidates and a human needed forcing chains there, so such steps count as hard.)"]
    # run 5: independent cross-check with Rangsk's SudokuSolver when every constraint is native to f-puzzles
    try:
        import rangsk
        from nfa import NFAS
        if rangsk.available() and rangsk.native(pz):
            cnt, rsolved, rgrid, rsteps = rangsk.check(pz)
            kinds = Counter()
            for st_ in rsteps:
                if 'Single' in st_:
                    continue
                # run 11: Rangsk prefixes a step with "[Name] " for every NFA constraint that filtered silently before it;
                # drop those prefixes so the step is classified by its own description
                st_ = re.sub(r'^(\[[^\]]*\]\s*)+(?=\[)', '', st_)
                if 'without specifying why' in st_:  # run 7: an NFA filter step that changed candidates silently (logging quirk)
                    kinds['line check (silent NFA filter step)'] += 1
                elif 'causes a contradiction' in st_:
                    kinds['contradiction test'] += 1
                elif ' is violated =>' in st_:  # run 6: an NFA line constraint removing a candidate it cannot extend
                    kinds['line check (constraint step)'] += 1
                elif re.match(r'^(\[[^\]]*\]\s*)+[^:\[\]=]+:', st_):  # run 6: "[Odometer] Pointing: ..." etc.
                    kinds[re.sub(r'^(\[[^\]]*\]\s*)+', '', st_).split(':')[0]] += 1
                elif st_.startswith('['):
                    # run 11: take the name inside the first brackets ("[Skyscraper 7 at r2c10] ...", "[Col Indexer] Evaluated ...")
                    nm_ = re.match(r'^\[([^\]]*)\]', st_).group(1)
                    kinds[nm_.split(' at ')[0].split(' from ')[0].split(' r')[0].rstrip('0123456789 ').replace('Sandwich sum', 'Sandwich') + ' (constraint step)'] += 1
                else:
                    kinds[re.sub(r'\s*\(r\d+c\d+\)$', '', st_.split(':')[0])] += 1  # run 11: "Cell Forcing Chain (r8c9)" -> one kind
            agree_r = rsolved and rgrid == grid_str(sol).replace('\n', '')
            rep += ['', "Independent cross-check with **Rangsk's SudokuSolver** (github.com/dclamage/SudokuSolver, built from source), "
                    "fed our own f-puzzles export without the solution:", '',
                    f"- solution count (`-k`): {cnt}",
                    f"- logical solve (`-l`): {'solved, same grid as CP-SAT' if agree_r else 'NOT solved' if not rsolved else 'solved, DIFFERENT grid (!)'}; "
                    f"{len(rsteps)} steps, of which non-single steps by kind: " + (', '.join(f"{k} {v}" for k, v in kinds.most_common()) or 'none')]
            if any(w in ' '.join(kinds) for w in ('contradiction', 'AIC', 'Wing', 'Fish', 'X-Wing', 'Swordfish', 'Forcing')):
                if any(c['type'] in NFAS for c in pz.cons):
                    rep.append('- note: invented line rules reach this solver as NFA constraints (tools/nfa.py). Its NFA filter checks '
                               'each line against the candidates but ignores that cells of a line sharing a house must differ, so '
                               'it falls back on contradiction tests far more often than a human (or my solver) would need to.')
                rep.append('- note: the Rangsk path uses advanced techniques (listed above).')
            if any(c['type'] == 'factor' for c in pz.cons):
                rep.append('- note (run 9): factor lines reach this solver as one binary-lookup constraint per neighbouring pair plus one NFA '
                           'per line that accepts exactly the valid fills of that line (repeats ruled out where its cells see each other), '
                           'so it can reason about a whole line the way a human lists its fills. Eliminations made by that line filter are '
                           'not always written to the log.')
            if kinds.get('line check (silent NFA filter step)'):
                rep.append("- note: Rangsk's NFA constraint removes candidates without writing a step description; its logger then prints "
                           "'reported the board was invalid without specifying why' (SolverLogic.cs). The solve continues and reaches the CP-SAT "
                           "grid, so these are silent line-filter steps, not errors.")
    except Exception as e:  # cross-check is optional; never block packaging on it
        rep += ['', f"(Rangsk cross-check not run: {e})"]
    rep += ['', f"Logical solvability: {'verified with the solver above (no guessing, no tier-3 contradiction tests).' if agree and L.tier_counts[3] == 0 else ('verified only with tier-3 contradiction tests (short bifurcation).' if agree else 'not verified')}",
            'Note: the solver is a program, not a human test-solve; its techniques are human-style but '
            'whole-constraint enumeration can be heavier than a human would like.', '',
            '## Difficulty estimate', '', f"**{diff} / 5** — {why}", '',
            'Method (run 3 onwards; the solver now applies one whole-constraint step per round, easiest first, '
            'so round counts are higher than in runs 1-2): 1 = singles + pairwise only; 2 = up to 8 tier-2 rounds; '
            '3 = 9-30 tier-2 rounds; 4 = 31-60 tier-2 rounds or 1-3 tier-3 tests; 5 = more, or not solved logically. '
            'Adjusted by at most one step for rule novelty / setter judgement (stated above).', '',
            'Calibration against the earlier puzzles, re-solved with the same solver version:', ''] + calibration(outdir) + extra(src) + ['',
            '## Solution', '', '```', grid_str(sol), '```']
    open(os.path.join(outdir, 'verification.md'), 'w').write('\n'.join(rep) + '\n')
    print('OK', outdir, res, L.tier_counts)
    print(lk['sudokupad'][:100])


def extra(src):
    """optional hand-written/scripted extra checks next to the spec: <spec>.extra.md"""
    f = src.rsplit('.', 1)[0] + '.extra.md'
    return ['', '## Extra checks for this puzzle', '', open(f).read().strip()] if os.path.isfile(f) else []


def calibration(outdir):
    root = os.path.dirname(os.path.abspath(outdir))
    rows = []
    for d in sorted(os.listdir(root)):
        f = os.path.join(root, d, 'puzzle.json')
        if os.path.abspath(os.path.join(root, d)) == os.path.abspath(outdir) or not os.path.isfile(f):
            continue
        P = json.load(open(f))
        L = Logic(Puzzle(P)); res, _ = L.solve(max_tier=3)
        rows.append(f"- {d}: rated {P.get('difficulty')}/5, {res}, tier rounds {L.tier_counts}")
    return rows


def count_with_forbid(pz, sol):
    from ortools.sat.python import cp_model as cm
    m, v = pz.build_model()
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
