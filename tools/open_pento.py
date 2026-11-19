"""Run 16: open-solution setting of a "pentomino killer": the twelve free pentominoes, each used once as a killer cage.

python3 open_pento.py out.json seed [--global antiking] [--per 12] [--spread 1.0]

No target grid. Each step:
  1. sample 12 grids that satisfy the cages so far (CP-SAT, random objectives);
  2. for every piece not yet used, take --per random placements (any rotation or reflection, on free cells) and every
     total that some sample gives it (with five different digits);
  3. score each (piece, placement, total) by the candidates my logical solver (tiers 1-2, now with innies/outies)
     removes from the current fixpoint;
  4. without --spread: take one of the best three. With --spread s: aim at an even share of the work, i.e. the move whose
     score is closest to s x (candidates left - 81) / (pieces left), so that the solve is spread over all twelve pieces
     instead of being finished by the first nine (greedy runs solved with 9 pieces and left 3 redundant);
  5. confirm with CP-SAT that the cages are still satisfiable, commit.
The run succeeds if the solver finishes exactly when (or before) the twelfth piece is placed. 031 Twelve Pieces is seed 21
with --global antiking --per 12 --spread 1.0 (CP-SAT sampling uses several workers, so reruns can differ)."""
import sys, random, json, copy, time
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
import vs
from ortools.sat.python import cp_model

BASE = {
    'F': [".##", "##.", ".#."], 'I': ["#####"], 'L': ["####", "#..."], 'N': ["##..", ".###"],
    'P': ["##", "##", "#."], 'T': ["###", ".#.", ".#."], 'U': ["#.#", "###"], 'V': ["#..", "#..", "###"],
    'W': ["#..", "##.", ".##"], 'X': [".#.", "###", ".#."], 'Y': ["####", ".#.."], 'Z': ["##.", ".#.", ".##"]}
PALETTE = {'F': '#fbd3d3', 'I': '#d4e4fa', 'L': '#d7f0cd', 'N': '#fdeeb5', 'P': '#e4d4f4', 'T': '#fdd9b5',
           'U': '#cbeceb', 'V': '#f4cfe2', 'W': '#e3e8c6', 'X': '#dcdcf6', 'Y': '#ece0cc', 'Z': '#f8d6c6'}


def norm(s):
    mr = min(r for r, c in s); mc = min(c for r, c in s)
    return tuple(sorted((r - mr, c - mc) for r, c in s))


def orients(name_):
    s = [(r, c) for r, row in enumerate(BASE[name_]) for c, ch in enumerate(row) if ch == '#']
    out = set()
    for _ in range(4):
        s = [(c, -r) for r, c in s]
        out.add(norm(s)); out.add(norm([(r, -c) for r, c in s]))
    return sorted(out)


ORI = {k: orients(k) for k in BASE}
assert sum(len(v) for v in ORI.values()) == 63  # the 63 fixed pentominoes


def piece_of(cells):
    """the letter of the free pentomino with these five cells (None if it is not a pentomino)"""
    n = norm(cells)
    return next((k for k in ORI if n in ORI[k]), None)


def opt(nm, default):
    return sys.argv[sys.argv.index(nm) + 1] if nm in sys.argv else default


def main():
    out, seed = sys.argv[1], int(sys.argv[2])
    glob = [g for g in opt('--global', '').split(',') if g]
    per, spread = int(opt('--per', 15)), float(opt('--spread', 0))
    rnd = random.Random(seed)

    def samples(spec, n):
        pz = vs.Puzzle(spec); res = []
        for _ in range(n):
            m, v = pz.build_model(); m.Minimize(sum(rnd.randint(-9, 9) * v[a] for a in v))
            s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 0.5; s.parameters.num_workers = 2
            s.parameters.random_seed = rnd.randrange(10 ** 6)
            st = s.Solve(m)
            if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                s.parameters.max_time_in_seconds = 10; st = s.Solve(m)
            if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                res.append({a: s.Value(v[a]) for a in v})
        return res

    def feasible(spec):
        sols, st = vs.Puzzle(spec).count_solutions(limit=1, time_limit=60)
        return len(sols) == 1

    spec = {'global': glob, 'constraints': []}
    used, occ = set(), set()
    while True:
        L = vs.Logic(vs.Puzzle(spec)); cand = L.init_cands(); L.propagate(cand, 2)
        left = sum(len(x) for x in cand.values())
        print('pieces', len(used), 'left', left, flush=True)
        if left == 81 or len(used) == 12:
            break
        sm = samples(spec, 12)
        moves = []; t0 = time.time()
        for n in BASE:
            if n in used:
                continue
            opts = []
            for o in ORI[n]:
                for r in range(9):
                    for c in range(9):
                        cs = [(r + a, c + b) for a, b in o]
                        if all(0 <= x < 9 and 0 <= y < 9 and (x, y) not in occ for x, y in cs):
                            opts.append(cs)
            for cs in rnd.sample(opts, min(per, len(opts))):
                for val in {sum(g[a] for a in cs) for g in sm if len({g[a] for a in cs}) == 5}:
                    sp2 = copy.deepcopy(spec)
                    sp2['constraints'].append({'type': 'killer', 'cells': [vs.name(a) for a in cs], 'sum': val})
                    c2 = {a: set(x) for a, x in cand.items()}
                    try:
                        vs.Logic(vs.Puzzle(sp2)).propagate(c2, 2)
                    except vs.Contradiction:
                        continue
                    moves.append((left - sum(len(x) for x in c2.values()), n, tuple(cs), val))
        moves.sort(key=lambda m: -m[0])
        print('  moves', len(moves), 'top', [m[0] for m in moves[:5]], round(time.time() - t0), flush=True)
        if spread:
            target = (left - 81) / (12 - len(used)) * spread
            order = sorted(moves, key=lambda m: abs(m[0] - target) + rnd.random() * 3)
        else:
            order = rnd.sample(moves[:3], min(3, len(moves))) + moves[3:]
        pick = None
        for mv in order:
            sp2 = copy.deepcopy(spec)
            sp2['constraints'].append({'type': 'killer', 'cells': [vs.name(a) for a in mv[2]], 'sum': mv[3]})
            if feasible(sp2):
                pick = mv; spec = sp2; break
        if pick is None:
            print('FAILED: no feasible move'); sys.exit(1)
        print('  add', pick[0], pick[1], [vs.name(a) for a in pick[2]], pick[3], flush=True)
        used.add(pick[1]); occ |= set(pick[2])
    L = vs.Logic(vs.Puzzle(spec)); res, cand = L.solve(2)
    print('FINAL', res, L.tier_counts, sum(len(x) for x in cand.values()), 'pieces', len(used))
    for c in spec['constraints']:
        c['piece'] = piece_of([vs.parse(x) for x in c['cells']])
        c['fill'] = PALETTE[c['piece']]
    assert len({c['piece'] for c in spec['constraints']}) == len(spec['constraints'])
    json.dump(spec, open(out, 'w'), indent=1)


if __name__ == '__main__':
    main()
