"""Variant sudoku toolkit: puzzle spec, CP-SAT uniqueness checker, logical
(propagation-only) solver for difficulty estimation, SVG renderer and
f-puzzles / SudokuPad link export.

Puzzle spec (JSON):
{
  "title": str, "author": str, "rules": str,
  "givens": {"r1c1": 5, ...},
  "global": ["antiknight", "antiking", "diag+", "diag-", "neg_kropki", "neg_xv"],
  "constraints": [
     {"type": "thermo",   "cells": ["r1c1", ...]},          # bulb first
     {"type": "whisper",  "cells": [...]},                  # adjacent |diff| >= 5
     {"type": "keypad",   "cells": [...]},                  # invented, see KEYPAD_ADJ
     {"type": "renban",   "cells": [...]},
     {"type": "killer",   "cells": [...], "sum": 10},       # sum optional
     {"type": "arrow",    "circle": ["r1c1"], "cells": [...]},
     {"type": "kropki_w", "cells": [a, b]},
     {"type": "kropki_b", "cells": [a, b]},
     {"type": "xv",       "cells": [a, b], "value": "X"|"V"},
     {"type": "parity",   "cells": [...]},                  # adjacent cells differ in parity
     {"type": "knight",   "cells": [...]},                  # invented: adjacent digits a knight's move apart on keypad
     {"type": "entropic", "cells": [...]},                  # any 3 consecutive cells: one of 123, 456, 789
     {"type": "modular",  "cells": [...]},                  # any 3 consecutive cells: one of each residue mod 3
     {"type": "regionsum","cells": [...]},                  # box segments of the line have equal sums
  ]
}
"""
import itertools, json, sys
from ortools.sat.python import cp_model

N = 9
DIGITS = range(1, 10)


def parse(c):
    c = c.lower()
    r, k = c[1:].split('c')
    return int(r) - 1, int(k) - 1


def name(rc):
    return f"r{rc[0]+1}c{rc[1]+1}"


def box(rc):
    return (rc[0] // 3) * 3 + rc[1] // 3


def sees_sudoku(a, b):
    return a != b and (a[0] == b[0] or a[1] == b[1] or box(a) == box(b))


KEYPAD_POS = {d: ((d - 1) // 3, (d - 1) % 3) for d in DIGITS}
KEYPAD_ADJ = {(a, b) for a in DIGITS for b in DIGITS
              if abs(KEYPAD_POS[a][0] - KEYPAD_POS[b][0]) + abs(KEYPAD_POS[a][1] - KEYPAD_POS[b][1]) == 1}
KNIGHT_ADJ = {(a, b) for a in DIGITS for b in DIGITS
              if sorted((abs(KEYPAD_POS[a][0] - KEYPAD_POS[b][0]), abs(KEYPAD_POS[a][1] - KEYPAD_POS[b][1]))) == [1, 2]}
# lines whose only rule is a relation between neighbouring cells
ADJ_LINES = ('whisper', 'keypad', 'parity', 'knight')
# lines where every window of 3 cells holds one digit of each class
WINDOW_LINES = {'entropic': lambda d: (d - 1) // 3, 'modular': lambda d: d % 3}

PAIR_REL = {
    'whisper': lambda a, b: abs(a - b) >= 5,
    'keypad': lambda a, b: (a, b) in KEYPAD_ADJ,
    'knight': lambda a, b: (a, b) in KNIGHT_ADJ,
    'entropic': lambda a, b: (a - 1) // 3 != (b - 1) // 3,
    'modular': lambda a, b: a % 3 != b % 3,
    'parity': lambda a, b: (a + b) % 2 == 1,
    'kropki_w': lambda a, b: abs(a - b) == 1,
    'kropki_b': lambda a, b: a == 2 * b or b == 2 * a,
    'X': lambda a, b: a + b == 10,
    'V': lambda a, b: a + b == 5,
    'neg_kropki': lambda a, b: abs(a - b) != 1 and a != 2 * b and b != 2 * a,
    'neg_kropki_w': lambda a, b: abs(a - b) != 1,
    'neg_xv': lambda a, b: a + b not in (5, 10),
    'lt': lambda a, b: a < b,
    'ne': lambda a, b: a != b,
}


class Puzzle:
    def __init__(self, spec):
        self.spec = spec
        self.givens = {parse(k): v for k, v in spec.get('givens', {}).items()}
        self.glob = set(spec.get('global', []))
        self.cons = []
        for c in spec.get('constraints', []):
            c = dict(c)
            c['rc'] = [parse(x) for x in c.get('cells', [])]
            if 'circle' in c:
                c['crc'] = [parse(x) for x in c['circle']]
            if c['type'] == 'regionsum':
                segs = [[0]]
                for i in range(1, len(c['rc'])):
                    if box(c['rc'][i]) == box(c['rc'][i - 1]):
                        segs[-1].append(i)
                    else:
                        segs.append([i])
                c['segs'] = segs
            self.cons.append(c)
        self._build_pairs()

    # ---- derived structure -------------------------------------------------
    def _build_pairs(self):
        """List of (a, b, relname) binary relations (a,b cells)."""
        pairs = []
        marked_kropki, marked_xv = set(), set()
        for c in self.cons:
            t, rc = c['type'], c['rc']
            if t in ADJ_LINES:
                for a, b in zip(rc, rc[1:]):
                    pairs.append((a, b, t))
                if c.get('loop'):
                    pairs.append((rc[-1], rc[0], t))
            elif t in WINDOW_LINES:
                ext = rc + rc[:2] if c.get('loop') else rc
                for a, b in list(zip(ext, ext[1:])) + list(zip(ext, ext[2:])):
                    pairs.append((a, b, t))
            elif t == 'thermo':
                for a, b in zip(rc, rc[1:]):
                    pairs.append((a, b, 'lt'))
            elif t in ('kropki_w', 'kropki_b'):
                pairs.append((rc[0], rc[1], t))
                marked_kropki.add(frozenset(rc))
            elif t == 'xv':
                pairs.append((rc[0], rc[1], c['value']))
                marked_xv.add(frozenset(rc))
        cells = [(r, k) for r in range(N) for k in range(N)]
        if 'neg_kropki' in self.glob or 'neg_kropki_w' in self.glob or 'neg_xv' in self.glob:
            for a in cells:
                for b in [(a[0], a[1] + 1), (a[0] + 1, a[1])]:
                    if b[0] >= N or b[1] >= N:
                        continue
                    fs = frozenset((a, b))
                    if 'neg_kropki' in self.glob and fs not in marked_kropki:
                        pairs.append((a, b, 'neg_kropki'))
                    if 'neg_kropki_w' in self.glob and fs not in marked_kropki:
                        pairs.append((a, b, 'neg_kropki_w'))
                    if 'neg_xv' in self.glob and fs not in marked_xv:
                        pairs.append((a, b, 'neg_xv'))
        self.pairs = pairs
        # extra "sees" (must differ) relations from globals
        self.extra_sees = set()
        for a in cells:
            for b in cells:
                if a >= b:
                    continue
                dr, dc = abs(a[0] - b[0]), abs(a[1] - b[1])
                if 'antiknight' in self.glob and {dr, dc} == {1, 2}:
                    self.extra_sees.add((a, b))
                if 'antiking' in self.glob and dr == 1 and dc == 1:
                    self.extra_sees.add((a, b))
                if 'diag-' in self.glob and a[0] == a[1] and b[0] == b[1]:
                    self.extra_sees.add((a, b))
                if 'diag+' in self.glob and a[0] + a[1] == 8 and b[0] + b[1] == 8:
                    self.extra_sees.add((a, b))
        # houses: rows, cols, boxes (+ diagonals)
        houses = []
        for i in range(N):
            houses.append([(i, k) for k in range(N)])
            houses.append([(r, i) for r in range(N)])
            houses.append([(r, k) for r in range(N) for k in range(N) if box((r, k)) == i])
        if 'diag-' in self.glob:
            houses.append([(i, i) for i in range(N)])
        if 'diag+' in self.glob:
            houses.append([(i, 8 - i) for i in range(N)])
        self.houses = houses

    def sees(self, a, b):
        if sees_sudoku(a, b):
            return True
        return (min(a, b), max(a, b)) in self.extra_sees

    # ---- verification of a full grid ----------------------------------------
    def check(self, g):
        """g: dict rc->digit. returns list of violated items (empty=ok)."""
        bad = []
        for h in self.houses:
            if sorted(g[x] for x in h) != list(DIGITS):
                bad.append(('house', h[0]))
        for (a, b) in self.extra_sees:
            if g[a] == g[b]:
                bad.append(('sees', a, b))
        for a, v in self.givens.items():
            if g[a] != v:
                bad.append(('given', a))
        for a, b, rel in self.pairs:
            if not PAIR_REL[rel](g[a], g[b]):
                bad.append((rel, a, b))
        for c in self.cons:
            if not self._group_ok(c, [g[x] for x in c['rc']], [g[x] for x in c.get('crc', [])]):
                bad.append((c['type'], c['rc'][0]))
        return bad

    @staticmethod
    def _group_ok(c, vals, cvals):
        t = c['type']
        if t == 'killer':
            if len(set(vals)) != len(vals):
                return False
            return 'sum' not in c or sum(vals) == c['sum']
        if t == 'renban':
            return len(set(vals)) == len(vals) and max(vals) - min(vals) == len(vals) - 1
        if t == 'arrow':
            return sum(vals) == int(''.join(map(str, cvals)))
        if t == 'thermo':
            return all(a < b for a, b in zip(vals, vals[1:]))
        if t == 'regionsum':
            return len({sum(vals[i] for i in seg) for seg in c['segs']}) == 1
        if t == 'littlekiller':
            return sum(vals) == c['sum']
        return True

    # ---- CP-SAT ----------------------------------------------------------------
    def build_model(self):
        m = cp_model.CpModel()
        v = {(r, k): m.NewIntVar(1, 9, f"v{r}{k}") for r in range(N) for k in range(N)}
        for h in self.houses:
            m.AddAllDifferent([v[x] for x in h])
        for a, b in self.extra_sees:
            m.Add(v[a] != v[b])
        for a, d in self.givens.items():
            m.Add(v[a] == d)
        for a, b, rel in self.pairs:
            f = PAIR_REL[rel]
            m.AddAllowedAssignments([v[a], v[b]], [(x, y) for x in DIGITS for y in DIGITS if f(x, y)])
        for c in self.cons:
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
            elif t == 'littlekiller':
                m.Add(sum(v[x] for x in rc) == c['sum'])
            elif t == 'regionsum':
                sums = [sum(v[rc[i]] for i in seg) for seg in c['segs']]
                for s2 in sums[1:]:
                    m.Add(s2 == sums[0])
        return m, v

    def count_solutions(self, limit=2, time_limit=120):
        m, v = self.build_model()
        sols = []

        class CB(cp_model.CpSolverSolutionCallback):
            def __init__(s):
                super().__init__()

            def on_solution_callback(s):
                sols.append({x: s.Value(v[x]) for x in v})
                if len(sols) >= limit:
                    s.StopSearch()

        solver = cp_model.CpSolver()
        solver.parameters.enumerate_all_solutions = True
        solver.parameters.max_time_in_seconds = time_limit
        st = solver.Solve(m, CB())
        complete = st in (cp_model.OPTIMAL, cp_model.FEASIBLE, cp_model.INFEASIBLE) and (
            len(sols) >= limit or st != cp_model.UNKNOWN)
        return sols, solver.StatusName(st)


# ---- logical solver --------------------------------------------------------
class Contradiction(Exception):
    pass


ALL = frozenset(DIGITS)


class Logic:
    """Candidate-elimination solver with tiers. No guessing except tier 3
    (single-candidate contradiction test, propagated with tiers 1-2)."""

    def __init__(self, pz):
        self.pz = pz
        self.cells = [(r, k) for r in range(N) for k in range(N)]
        self.peers = {a: [b for b in self.cells if pz.sees(a, b)] for a in self.cells}
        self.pair_index = {a: [] for a in self.cells}
        for a, b, rel in pz.pairs:
            f = PAIR_REL[rel]
            self.pair_index[a].append((b, lambda x, y, f=f: f(x, y)))
            self.pair_index[b].append((a, lambda x, y, f=f: f(y, x)))
        self.groups = [c for c in pz.cons if c['type'] in
                       ('killer', 'renban', 'arrow', 'thermo', 'regionsum', 'littlekiller') + ADJ_LINES + tuple(WINDOW_LINES)]
        self.gac_sizes = []  # (type, enumeration size, solved cells) of every whole-constraint step that made progress
        self.trace = []
        self.tier_counts = {1: 0, 2: 0, 3: 0}
        self.house_sets = [set(h) for h in pz.houses]
        # parity components from keypad / parity lines (adjacent cells have opposite parity)
        adj = {a: [] for a in self.cells}
        for a, b, rel in pz.pairs:
            if rel in ('keypad', 'parity', 'knight'):
                adj[a].append(b); adj[b].append(a)
        self.parity_comps = []
        seen = {}
        for a in self.cells:
            if a in seen or not adj[a]:
                continue
            col = {a: 0}; stack = [a]
            while stack:
                x = stack.pop()
                for y in adj[x]:
                    if y not in col:
                        col[y] = 1 - col[x]; stack.append(y)
            seen.update(col)
            self.parity_comps.append(col)

    def init_cands(self):
        cand = {a: set(DIGITS) for a in self.cells}
        for a, d in self.pz.givens.items():
            cand[a] = {d}
        return cand

    # techniques -------------------------------------------------------------
    # each returns True if it changed anything. Tier 1: singles + pairwise
    # constraint consistency. Tier 2: everything else (still no guessing).
    def naked_singles(self, cand):
        changed = False
        for a in self.cells:
            if len(cand[a]) == 0:
                raise Contradiction(a)
            if len(cand[a]) == 1:
                d = next(iter(cand[a]))
                for b in self.peers[a]:
                    if d in cand[b]:
                        cand[b].discard(d); changed = True
                        if not cand[b]:
                            raise Contradiction(b)
        return changed

    def hidden_singles(self, cand):
        changed = False
        for h in self.pz.houses:
            for d in DIGITS:
                where = [a for a in h if d in cand[a]]
                if not where:
                    raise Contradiction(('house', h[0], d))
                if len(where) == 1 and len(cand[where[0]]) > 1:
                    cand[where[0]] = {d}; changed = True
        return changed

    def pair_consistency(self, cand):
        changed = False
        for a in self.cells:
            for b, f in self.pair_index[a]:
                keep = {x for x in cand[a] if any(f(x, y) and (x != y or not self.pz.sees(a, b)) for y in cand[b])}
                if keep != cand[a]:
                    cand[a] = keep; changed = True
                    if not keep:
                        raise Contradiction(a)
        return changed

    def parity_count(self, cand):
        """each house holds exactly 4 even and 5 odd digits"""
        if not self.parity_comps:
            return False
        changed = False
        EV = {2, 4, 6, 8}; OD = {1, 3, 5, 7, 9}
        for h in self.pz.houses:
            ke = [a for a in h if cand[a] <= EV]
            ko = [a for a in h if cand[a] <= OD]
            for known, full, rm in ((ke, 4, EV), (ko, 5, OD)):
                if len(known) == full:
                    for a in h:
                        if a not in known and cand[a] & rm:
                            cand[a] -= rm; changed = True
        for comp in self.parity_comps:
            for h in self.pz.houses:
                inh = [a for a in h if a in comp]
                if len(inh) < 2:
                    continue
                outside = [a for a in h if a not in comp]
                kev = sum(1 for a in outside if cand[a] <= EV)
                kod = sum(1 for a in outside if cand[a] <= OD)
                for colour in (0, 1):
                    cnt = sum(1 for a in inh if comp[a] == colour)
                    bad = None
                    if cnt + kev > 4:
                        bad = EV
                    elif cnt + kod > 5:
                        bad = OD
                    if bad:
                        for a, cc in comp.items():
                            rm = bad if cc == colour else (OD if bad is EV else EV)
                            if cand[a] & rm:
                                cand[a] -= rm; changed = True
        return changed

    def locked_candidates(self, cand):
        changed = False
        H = self.pz.houses
        for i1, h1 in enumerate(H):
            s1 = self.house_sets[i1]
            for d in DIGITS:
                where = [a for a in h1 if d in cand[a]]
                if len(where) < 2:
                    continue
                for i2, h2 in enumerate(H):
                    if i2 == i1:
                        continue
                    s2 = self.house_sets[i2]
                    if all(a in s2 for a in where):
                        for b in h2:
                            if b not in s1 and d in cand[b]:
                                cand[b].discard(d); changed = True
        return changed

    def subsets(self, cand):
        changed = False
        for h in self.pz.houses:
            un = [a for a in h if len(cand[a]) > 1]
            for k in (2, 3):
                for combo in itertools.combinations(un, k):
                    u = set().union(*(cand[a] for a in combo))
                    if len(u) == k:
                        for b in h:
                            if b not in combo and cand[b] & u:
                                cand[b] -= u; changed = True
                digs = [d for d in DIGITS if sum(d in cand[a] for a in h) > 1]
                for dc in itertools.combinations(digs, k):
                    where = {a for a in h for d in dc if d in cand[a]}
                    if len(where) == k:
                        for a in where:
                            if cand[a] - set(dc):
                                cand[a] &= set(dc); changed = True
        return changed

    def pointing_general(self, cand):
        """a cell that sees every candidate position of digit d in some house cannot be d"""
        changed = False
        for h in self.pz.houses:
            for d in DIGITS:
                where = [a for a in h if d in cand[a]]
                if 1 < len(where) <= 4:
                    common = set(self.peers[where[0]])
                    for a in where[1:]:
                        common &= set(self.peers[a])
                    for b in common:
                        if d in cand[b]:
                            cand[b].discard(d); changed = True
        return changed

    def group_consistency(self, cand):
        changed = False
        for g in self.groups:
            if self.gac(g, cand):
                changed = True
        return changed

    TECHS = [('naked single', 1), ('hidden single', 1), ('pair consistency', 1),
             ('parity count', 2), ('locked candidates', 2), ('subsets', 2),
             ('pointing (general)', 2), ('whole-constraint consistency', 2)]

    def _tech_fn(self, nm):
        return {'naked single': self.naked_singles, 'hidden single': self.hidden_singles,
                'pair consistency': self.pair_consistency, 'parity count': self.parity_count,
                'locked candidates': self.locked_candidates, 'subsets': self.subsets,
                'pointing (general)': self.pointing_general,
                'whole-constraint consistency': self.group_consistency}[nm]

    def propagate(self, cand, max_tier=2, count=False):
        while True:
            for nm, tier in self.TECHS:
                if tier > max_tier:
                    continue
                before = sum(len(v) for v in cand.values()) if count else 0
                if self._tech_fn(nm)(cand):
                    for a in self.cells:
                        if not cand[a]:
                            raise Contradiction(a)
                    if count:
                        self.tier_counts[tier] += 1
                        self.trace.append((nm, before - sum(len(v) for v in cand.values()),
                                           sum(len(v) == 1 for v in cand.values())))
                    break
            else:
                return cand

    def gac(self, g, cand):
        t = g['type']
        cells = list(g.get('crc', [])) + list(g['rc'])
        nc = len(g.get('crc', []))
        distinct_all = t in ('killer', 'renban')
        idx_pairs = []
        for i in range(len(cells)):
            for j in range(i):
                if distinct_all or self.pz.sees(cells[i], cells[j]):
                    idx_pairs.append((j, i))
        prev = {i: [j for (j, k) in idx_pairs if k == i] for i in range(len(cells))}
        # adjacent relations along line
        rel = None
        if t in ADJ_LINES:
            rel = PAIR_REL[t]
        elif t == 'thermo':
            rel = PAIR_REL['lt']
        support = [set() for _ in cells]
        doms = [sorted(cand[a]) for a in cells]
        if any(len(d) == 0 for d in doms):
            raise Contradiction(cells)
        # skip very large enumerations
        size = 1
        for d in doms:
            size *= len(d)
        if t == 'regionsum':
            return self.gac_regionsum(g, cand, size)
        if t in WINDOW_LINES and size > 20000:
            return self.window_classes(g, cand, size)
        if t == 'littlekiller' and size > 200000:
            return self.sum_bounds(g, cand)
        if size > 2_000_000 and t not in ('thermo',) + ADJ_LINES + tuple(WINDOW_LINES):
            return False
        cls = WINDOW_LINES.get(t)
        vals = [0] * len(cells)
        target = g.get('sum')

        def rec(i, s):
            if i == len(cells):
                v = vals
                if t in ('killer', 'littlekiller') and target is not None and s != target:
                    return
                if t == 'renban' and max(v) - min(v) != len(v) - 1:
                    return
                if g.get('loop') and rel is not None and not rel(v[-1], v[0]):
                    return
                if g.get('loop') and cls is not None and len({cls(v[-2]), cls(v[-1]), cls(v[0])}) < 3 or \
                        g.get('loop') and cls is not None and len({cls(v[-1]), cls(v[0]), cls(v[1])}) < 3:
                    return
                if t == 'arrow':
                    circ = int(''.join(map(str, v[:nc])))
                    if sum(v[nc:]) != circ:
                        return
                for k in range(len(cells)):
                    support[k].add(v[k])
                return
            for x in doms[i]:
                if any(vals[j] == x for j in prev[i]):
                    continue
                if rel is not None and i > 0 and not rel(vals[i - 1], x):
                    continue
                if cls is not None and ((i > 0 and cls(vals[i - 1]) == cls(x)) or (i > 1 and cls(vals[i - 2]) == cls(x))):
                    continue
                if t in ('killer', 'littlekiller') and target is not None and s + x > target:
                    continue
                if t == 'renban' and i > 0:
                    lo = min(min(vals[:i]), x); hi = max(max(vals[:i]), x)
                    if hi - lo > len(cells) - 1:
                        continue
                vals[i] = x
                # early exit if all supports already full
                rec(i + 1, s + x if i >= nc or t != 'arrow' else s)
            vals[i] = 0

        rec(0, 0)
        changed = False
        for k, a in enumerate(cells):
            if support[k] != cand[a]:
                cand[a] = set(support[k]) & cand[a]
                changed = True
                if not cand[a]:
                    raise Contradiction(a)
        if changed:
            self.gac_sizes.append((t, size, sum(len(x) == 1 for x in cand.values())))
        return changed

    def sum_bounds(self, g, cand):
        """bounds reasoning for long sums: each cell must leave a reachable total for the others"""
        rc, target = g['rc'], g['sum']
        lo = sum(min(cand[a]) for a in rc); hi = sum(max(cand[a]) for a in rc)
        changed = False
        for a in rc:
            olo, ohi = lo - min(cand[a]), hi - max(cand[a])
            keep = {x for x in cand[a] if olo <= target - x <= ohi}
            if keep != cand[a]:
                cand[a] = keep; changed = True
                if not keep:
                    raise Contradiction(a)
        return changed

    def window_classes(self, g, cand, size):
        """Cheap propagation for entropic/modular lines: the class of position i is perm[i % 3] for one of the
        six permutations; a pattern is possible if every cell has a candidate in its class and no box gets more
        than three cells of one class."""
        cls = WINDOW_LINES[g['type']]
        rc = g['rc']
        if g.get('loop') and len(rc) % 3:
            raise Contradiction(rc[0])
        sup = [set() for _ in rc]
        for perm in itertools.permutations(range(3)):
            allowed = [{d for d in cand[a] if cls(d) == perm[i % 3]} for i, a in enumerate(rc)]
            if any(not x for x in allowed):
                continue
            boxes = {}
            for i, a in enumerate(rc):
                boxes.setdefault((box(a), perm[i % 3]), []).append(i)
            bad = False
            for idx in boxes.values():
                if len(idx) > 3 or len(set().union(*(allowed[i] for i in idx))) < len(idx):
                    bad = True
            if bad:
                continue
            for i in range(len(rc)):
                sup[i] |= allowed[i]
        changed = False
        for i, a in enumerate(rc):
            if sup[i] != cand[a]:
                cand[a] = cand[a] & sup[i]; changed = True
                if not cand[a]:
                    raise Contradiction(a)
        if changed:
            self.gac_sizes.append((g['type'], 6, sum(len(x) == 1 for x in cand.values())))
        return changed

    def gac_regionsum(self, g, cand, size):
        """each box segment is all-distinct; segment sums must be equal."""
        rc = g['rc']
        seg_fills = []
        for seg in g['segs']:
            fills = {}
            for combo in itertools.product(*[sorted(cand[rc[i]]) for i in seg]):
                if len(set(combo)) == len(combo):
                    fills.setdefault(sum(combo), []).append(combo)
            seg_fills.append(fills)
        ok = set(seg_fills[0])
        for f in seg_fills[1:]:
            ok &= set(f)
        changed = False
        for seg, fills in zip(g['segs'], seg_fills):
            sup = [set() for _ in seg]
            for s_ in ok:
                for combo in fills[s_]:
                    for j, x in enumerate(combo):
                        sup[j].add(x)
            for j, i in enumerate(seg):
                a = rc[i]
                if sup[j] != cand[a]:
                    cand[a] = cand[a] & sup[j]; changed = True
                    if not cand[a]:
                        raise Contradiction(a)
        if changed:
            self.gac_sizes.append(('regionsum', size, sum(len(x) == 1 for x in cand.values())))
        return changed

    def solved(self, cand):
        return all(len(cand[a]) == 1 for a in self.cells)

    def solve(self, max_tier=3):
        cand = self.init_cands()
        try:
            self.propagate(cand, 1 if max_tier == 1 else 2, count=True)
            while not self.solved(cand) and max_tier >= 3:
                progress = False
                for a in sorted(self.cells, key=lambda a: len(cand[a])):
                    if len(cand[a]) < 2:
                        continue
                    for d in sorted(cand[a]):
                        if d not in cand[a] or len(cand[a]) < 2:
                            continue
                        trial = {x: set(cand[x]) for x in self.cells}
                        trial[a] = {d}
                        try:
                            self.propagate(trial, 2)
                        except Contradiction:
                            cand[a].discard(d)
                            self.tier_counts[3] += 1
                            self.trace.append(('contradiction test: %s != %d' % (name(a), d), 1, sum(len(v) == 1 for v in cand.values())))
                            progress = True
                    if progress:
                        break
                if not progress:
                    break
                self.propagate(cand, 2, count=True)
        except Contradiction as e:
            return 'contradiction', cand
        return ('solved' if self.solved(cand) else 'stuck'), cand


def grid_str(g):
    return '\n'.join(''.join(str(g[(r, k)]) for k in range(N)) for r in range(N))


def cand_str(cand):
    out = []
    for r in range(N):
        out.append(' '.join(''.join(map(str, sorted(cand[(r, k)]))).ljust(9) for k in range(N)))
    return '\n'.join(out)


# ---- SVG rendering ---------------------------------------------------------
def render_svg(pz, solution=None, cell=60, title=None):
    S = cell
    M = 20
    W = S * N + 2 * M
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{W}" viewBox="0 0 {W} {W}" font-family="Helvetica, Arial, sans-serif">',
           f'<rect width="{W}" height="{W}" fill="white"/>']

    def cx(rc):
        return M + rc[1] * S + S / 2, M + rc[0] * S + S / 2

    op = 0.4 if solution else 0.85
    colors = {'whisper': '#5fd35f', 'keypad': '#d27bd8', 'renban': '#e08ae0', 'parity': '#e6a23c',
              'knight': '#9b59d0', 'entropic': '#f0a030', 'modular': '#30b0c0', 'regionsum': '#4a90e2'}
    # cages first (under lines)
    for c in pz.cons:
        if c['type'] == 'killer':
            out.append(cage_svg(c['rc'], c.get('sum'), S, M))
    for c in pz.cons:
        t = c['type']
        if t in colors:
            col = c.get('color', colors[t])
            w = {'renban': 0.35, 'keypad': 0.22}.get(t, 0.22) * S
            pts = ' '.join(f"{x:.1f},{y:.1f}" for x, y in map(cx, c['rc']))
            tag = 'polygon' if c.get('loop') else 'polyline'
            out.append(f'<{tag} points="{pts}" fill="none" stroke="{col}" stroke-width="{w:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>')
        elif t == 'thermo':
            pts = ' '.join(f"{x:.1f},{y:.1f}" for x, y in map(cx, c['rc']))
            out.append(f'<polyline points="{pts}" fill="none" stroke="#bbbbbb" stroke-width="{0.3*S:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
            x, y = cx(c['rc'][0])
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.38*S:.1f}" fill="#bbbbbb"/>')
        elif t == 'arrow':
            x, y = cx(c['crc'][0])
            pts = [cx(c['crc'][-1])] + [cx(r) for r in c['rc']]
            out.append('<polyline points="%s" fill="none" stroke="#888" stroke-width="2.5"/>' % ' '.join(f"{a:.1f},{b:.1f}" for a, b in pts))
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.4*S:.1f}" fill="white" stroke="#888" stroke-width="2.5"/>')
    # grid
    for i in range(N + 1):
        w = 3 if i % 3 == 0 else 1
        out.append(f'<line x1="{M}" y1="{M+i*S}" x2="{M+N*S}" y2="{M+i*S}" stroke="black" stroke-width="{w}"/>')
        out.append(f'<line x1="{M+i*S}" y1="{M}" x2="{M+i*S}" y2="{M+N*S}" stroke="black" stroke-width="{w}"/>')
    for c in pz.cons:
        if c['type'] == 'killer':
            out.append(cage_svg(c['rc'], c.get('sum'), S, M, label_only=True))
    # dots / xv
    for c in pz.cons:
        t = c['type']
        if t in ('kropki_w', 'kropki_b', 'xv'):
            (x1, y1), (x2, y2) = cx(c['rc'][0]), cx(c['rc'][1])
            x, y = (x1 + x2) / 2, (y1 + y2) / 2
            if t == 'xv':
                out.append(f'<rect x="{x-0.17*S:.1f}" y="{y-0.17*S:.1f}" width="{0.34*S:.1f}" height="{0.34*S:.1f}" fill="white"/>')
                out.append(f'<text x="{x:.1f}" y="{y+0.11*S:.1f}" font-size="{0.32*S:.1f}" text-anchor="middle" font-weight="bold">{c["value"]}</text>')
            else:
                fill = 'black' if t == 'kropki_b' else 'white'
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.12*S:.1f}" fill="{fill}" stroke="black" stroke-width="1.5"/>')
    for a, d in pz.givens.items():
        x, y = cx(a)
        out.append(f'<text x="{x:.1f}" y="{y+0.18*S:.1f}" font-size="{0.55*S:.1f}" text-anchor="middle">{d}</text>')
    if solution:
        for a, d in solution.items():
            if a in pz.givens:
                continue
            x, y = cx(a)
            out.append(f'<text x="{x:.1f}" y="{y+0.18*S:.1f}" font-size="{0.5*S:.1f}" text-anchor="middle" fill="#1a5fb4">{d}</text>')
    out.append('</svg>')
    return '\n'.join(out)


def cage_svg(rc, total, S, M, label_only=False):
    cells = set(rc)
    i = 0.08 * S
    out = []
    if not label_only:
        for (r, k) in rc:
            x0, y0 = M + k * S, M + r * S
            x1, y1 = x0 + S, y0 + S
            inn = lambda dr, dc: (r + dr, k + dc) in cells

            def end(side_n, diag_n, base, sign):
                # side_n: neighbour along the edge direction, diag_n: diagonal beyond the edge
                if not side_n:
                    return base + sign * i
                if not diag_n:
                    return base
                return base - sign * i
            segs = []
            if not inn(-1, 0):
                segs.append((end(inn(0, -1), inn(-1, -1), x0, 1), y0 + i, end(inn(0, 1), inn(-1, 1), x1, -1), y0 + i))
            if not inn(1, 0):
                segs.append((end(inn(0, -1), inn(1, -1), x0, 1), y1 - i, end(inn(0, 1), inn(1, 1), x1, -1), y1 - i))
            if not inn(0, -1):
                segs.append((x0 + i, end(inn(-1, 0), inn(-1, -1), y0, 1), x0 + i, end(inn(1, 0), inn(1, -1), y1, -1)))
            if not inn(0, 1):
                segs.append((x1 - i, end(inn(-1, 0), inn(-1, 1), y0, 1), x1 - i, end(inn(1, 0), inn(1, 1), y1, -1)))
            for xa, ya, xb, yb in segs:
                out.append(f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" stroke="black" stroke-width="1.3" stroke-dasharray="4,3"/>')
    if total is not None and label_only:
        tl = min(rc)
        x0, y0 = M + tl[1] * S, M + tl[0] * S
        w = 0.14 * S * len(str(total)) + 0.06 * S
        out.append(f'<rect x="{x0+2:.1f}" y="{y0+2:.1f}" width="{w:.1f}" height="{0.24*S:.1f}" fill="white"/>')
        out.append(f'<text x="{x0+4:.1f}" y="{y0+0.22*S:.1f}" font-size="{0.21*S:.1f}">{total}</text>')
    return '\n'.join(out)


# ---- f-puzzles export --------------------------------------------------------
def fpuzzles_json(pz, solution):
    spec = pz.spec
    grid = [[{} for _ in range(N)] for _ in range(N)]
    for (r, k), d in pz.givens.items():
        grid[r][k] = {"value": d, "given": True}
    J = {"size": 9, "title": spec.get('title', ''), "author": spec.get('author', ''),
         "ruleset": spec.get('rules', ''), "grid": grid,
         "solution": [solution[(r, k)] for r in range(N) for k in range(N)]}
    U = lambda rc: f"R{rc[0]+1}C{rc[1]+1}"
    colors = {'whisper': '#67F067', 'keypad': '#D27BD8', 'renban': '#F067F0', 'parity': '#E6A23C',
              'knight': '#9B59D0', 'entropic': '#F0A030', 'modular': '#30B0C0', 'regionsum': '#4A90E2'}
    for c in pz.cons:
        t = c['type']
        if t == 'thermo':
            J.setdefault('thermometer', []).append({"lines": [[U(x) for x in c['rc']]]})
        elif t == 'killer':
            e = {"cells": [U(x) for x in c['rc']]}
            if 'sum' in c:
                e['value'] = str(c['sum'])
            J.setdefault('killercage', []).append(e)
        elif t == 'arrow':
            J.setdefault('arrow', []).append({"cells": [U(x) for x in c['crc']], "lines": [[U(c['crc'][-1])] + [U(x) for x in c['rc']]]})
        elif t in colors:
            J.setdefault('line', []).append({"lines": [[U(x) for x in c['rc'] + (c['rc'][:1] if c.get('loop') else [])]], "outlineC": c.get('fcolor', colors[t]),
                                             "width": 0.35 if t == 'renban' else 0.25, "isNewConstraint": True})
        elif t == 'kropki_w':
            J.setdefault('difference', []).append({"cells": [U(x) for x in c['rc']]})
        elif t == 'kropki_b':
            J.setdefault('ratio', []).append({"cells": [U(x) for x in c['rc']], "value": "2"})
        elif t == 'xv':
            J.setdefault('xv', []).append({"cells": [U(x) for x in c['rc']], "value": c['value']})
    neg = []
    if 'neg_xv' in pz.glob:
        neg.append('xv')
    if 'neg_kropki' in pz.glob:
        neg += ['ratio', 'difference']
    if neg:
        J['negative'] = neg
    if 'antiknight' in pz.glob:
        J['antiknight'] = True
    if 'antiking' in pz.glob:
        J['antiking'] = True
    if 'diag+' in pz.glob:
        J['diagonal+'] = True
    if 'diag-' in pz.glob:
        J['diagonal-'] = True
    return J


def links(pz, solution):
    import subprocess
    js = json.dumps(fpuzzles_json(pz, solution), separators=(',', ':'))
    comp = subprocess.run(['node', '-e',
                           "const lz=require('/tmp/lz/node_modules/lz-string');let s='';process.stdin.on('data',d=>s+=d).on('end',()=>process.stdout.write(lz.compressToBase64(s)))"],
                          input=js.encode(), capture_output=True, check=True).stdout.decode()
    return {"sudokupad": "https://sudokupad.app/fpuzzles" + comp,
            "fpuzzles": "https://www.f-puzzles.com/?load=" + comp}


def load(path):
    with open(path) as f:
        return Puzzle(json.load(f))
