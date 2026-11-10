"""Variant sudoku toolkit: puzzle spec, CP-SAT uniqueness checker, logical
(propagation-only) solver for difficulty estimation, SVG renderer and
f-puzzles / SudokuPad link export.

Puzzle spec (JSON):
{
  "title": str, "author": str, "rules": str,
  "givens": {"r1c1": 5, ...},
  "global": ["antiknight", "antiking", "diag+", "diag-", "neg_kropki", "neg_kropki_w", "neg_xv"],
  "constraints": [
     {"type": "thermo",   "cells": ["r1c1", ...]},          # bulb first
     {"type": "whisper",  "cells": [...]},                  # adjacent |diff| >= 5
     {"type": "dutch",    "cells": [...]},                  # run 7: Dutch whisper, adjacent |diff| >= 4
     {"type": "zipper",   "cells": [...]},                  # run 7: cells equidistant from the line's centre sum to the same
                                                            # total; on an odd-length line that total is the centre digit
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
     {"type": "seesaw",   "cells": [...], "pivot": "r5c5"}, # invented (run 3): sum of digit x distance-from-pivot
                                                            # (counted along the line) is equal on both sides
     {"type": "fibonacci","cells": [...]},                  # invented (run 4): read from the first cell, every digit from
                                                            # the third on is the last digit of the sum of the two before it
     {"type": "littlekiller", "cells": [...], "sum": 20, "from": "r0c3", "dir": "DR"},  # outside clue position for drawing/export
     {"type": "sandwich", "from": "r0c3", "sum": 10},       # run 5: sum of the digits between the 1 and the 9 of that row/column
     {"type": "between",  "cells": [...]},                  # run 5: inner cells strictly between the two (circled) end digits
     {"type": "bridge",   "cells": [...]},                  # invented (run 5): product of the two end digits = sum of the inner digits
     {"type": "slowthermo", "cells": [...]},                # run 5: bulb first, digits never decrease along the line
                                                            # (several lines may share cells, i.e. a branching thermo)
     {"type": "xsum", "from": "r0c3", "sum": 20},           # run 6: the first X cells seen from the clue sum to the total,
                                                            # where X is the digit in the first cell
     {"type": "skyscraper", "from": "r4c10", "count": 3},   # run 6: number of digits seen from the clue that are larger
                                                            # than every digit before them
     {"type": "odometer", "cells": ["r1c1", ...]},          # invented (run 6): the first cell is circled; it equals the sum of
                                                            # |differences| of consecutive cells along the whole line,
                                                            # the circle included (the distance travelled from the circle)
     {"type": "equation", "line": "r4", "result": 2},       # invented (run 7): the row/column (all 9 cells, read left to right
                                                            # or top to bottom) is a sum of three-digit numbers: the two
                                                            # non-result thirds add up to the result third (0 = first, 2 = last)
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
FIB_TRIPLES = [(a, b, (a + b) % 10) for a in DIGITS for b in DIGITS if (a + b) % 10]
# lines whose only rule is a relation between neighbouring cells
ADJ_LINES = ('whisper', 'keypad', 'parity', 'knight', 'dutch')
# lines where every window of 3 cells holds one digit of each class
WINDOW_LINES = {'entropic': lambda d: (d - 1) // 3, 'modular': lambda d: d % 3}

PAIR_REL = {
    'whisper': lambda a, b: abs(a - b) >= 5,
    'dutch': lambda a, b: abs(a - b) >= 4,
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
    'le': lambda a, b: a <= b,
    'ne': lambda a, b: a != b,
}


LK_DIRS = {'DR': (1, 1), 'DL': (1, -1), 'UR': (-1, 1), 'UL': (-1, -1)}


def lk_cells(frm, d):
    """cells of a little-killer diagonal, from an outside position like r0c3 (rows/cols 0 and 10 lie outside)"""
    r, k = parse(frm)
    dr, dc = LK_DIRS[d]
    out = []
    r, k = r + dr, k + dc
    while 0 <= r < N and 0 <= k < N:
        out.append((r, k)); r, k = r + dr, k + dc
    return out


def outside_ray(frm):
    """run 6: the row or column of an outside clue position, ordered as seen from the clue"""
    r, k = parse(frm)
    if r < 0:
        return [(i, k) for i in range(N)]
    if r >= N:
        return [(i, k) for i in range(N - 1, -1, -1)]
    if k < 0:
        return [(r, i) for i in range(N)]
    return [(r, i) for i in range(N - 1, -1, -1)]


def outside_line(frm):
    """row or column of an outside clue position: r0cK / r10cK = column K, rKc0 / rKc10 = row K"""
    r, k = parse(frm)
    if r < 0 or r >= N:
        return [(i, k) for i in range(N)]
    return [(r, i) for i in range(N)]


# run 7: ABC + DEF = GHI with the digits 1-9 once each (336 permutations); EQ_PERMS[res] lists them in the cell
# order of a row/column whose result third is third number res (0 = first, 2 = last)
_EQ = [p for p in itertools.permutations(DIGITS)
       if 100 * p[0] + 10 * p[1] + p[2] + 100 * p[3] + 10 * p[4] + p[5] == 100 * p[6] + 10 * p[7] + p[8]]
EQ_PERMS = {2: _EQ, 0: [p[6:] + p[:6] for p in _EQ]}


def equation_cells(line):
    """'r4' -> the 9 cells of row 4 left to right; 'c7' -> column 7 top to bottom"""
    i = int(line[1:]) - 1
    return [(i, k) for k in range(N)] if line[0].lower() == 'r' else [(r, i) for r in range(N)]


def num3(xs):
    return 100 * xs[0] + 10 * xs[1] + xs[2]


# digit sets from 2..8 by (size, sum), for sandwich reasoning
SANDWICH_SETS = {}
for _k in range(8):
    for _c in itertools.combinations(range(2, 9), _k):
        SANDWICH_SETS.setdefault((_k, sum(_c)), []).append(frozenset(_c))


def _matching_support(cells_doms, known=None):
    """cells_doms: list of candidate sets that must be filled with all-different digits from a set of exactly
    len(cells_doms) digits (a perfect matching). Returns per-cell supported digits (empty lists if impossible).
    Digits already in known[i] are not re-tested (they are reported as supported if a matching exists)."""
    n = len(cells_doms)
    if n == 0:
        return []

    def match(doms):
        owner = {}

        def aug(i, seen):
            for d in doms[i]:
                if d in seen:
                    continue
                seen.add(d)
                if d not in owner or aug(owner[d], seen):
                    owner[d] = i
                    return True
            return False
        return all(aug(i, set()) for i in range(n))
    if not match(cells_doms):
        return [set() for _ in range(n)]
    sup = []
    for i in range(n):
        si = set(cells_doms[i] & known[i]) if known else set()
        for d in cells_doms[i] - si:
            doms = [({d} if j == i else cells_doms[j] - {d}) for j in range(n)]
            if match(doms):
                si.add(d)
        sup.append(si)
    return sup


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
            if c['type'] == 'littlekiller' and 'from' in c and not c['rc']:
                c['rc'] = lk_cells(c['from'], c['dir'])
            if c['type'] == 'sandwich' and not c['rc']:
                c['rc'] = outside_line(c['from'])
            if c['type'] == 'equation' and not c['rc']:
                c['rc'] = equation_cells(c['line'])
            if c['type'] in ('xsum', 'skyscraper') and not c['rc']:
                c['rc'] = outside_ray(c['from'])
            if c['type'] == 'seesaw':
                p = c['rc'].index(parse(c['pivot']))
                c['w'] = [i - p for i in range(len(c['rc']))]
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
            elif t == 'slowthermo':
                for a, b in zip(rc, rc[1:]):
                    pairs.append((a, b, 'le'))
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
        if t == 'slowthermo':
            return all(a <= b for a, b in zip(vals, vals[1:]))
        if t == 'regionsum':
            return len({sum(vals[i] for i in seg) for seg in c['segs']}) == 1
        if t == 'littlekiller':
            return sum(vals) == c['sum']
        if t == 'seesaw':
            return sum(w * x for w, x in zip(c['w'], vals)) == 0
        if t == 'fibonacci':
            return all(vals[i + 2] == (vals[i] + vals[i + 1]) % 10 for i in range(len(vals) - 2))
        if t == 'sandwich':
            i, j = sorted((vals.index(1), vals.index(9)))
            return sum(vals[i + 1:j]) == c['sum']
        if t == 'between':
            lo, hi = sorted((vals[0], vals[-1]))
            return all(lo < x < hi for x in vals[1:-1])
        if t == 'bridge':
            return vals[0] * vals[-1] == sum(vals[1:-1])
        if t == 'xsum':
            return sum(vals[:vals[0]]) == c['sum']
        if t == 'skyscraper':
            return sum(1 for i, x in enumerate(vals) if all(x > y for y in vals[:i])) == c['count']
        if t == 'odometer':
            return sum(abs(a - b) for a, b in zip(vals, vals[1:])) == vals[0]
        if t == 'zipper':
            n = len(vals)
            sums = {vals[i] + vals[n - 1 - i] for i in range(n // 2)}
            if n % 2:
                sums.add(vals[n // 2])
            return len(sums) == 1
        if t == 'equation':
            seg = [vals[0:3], vals[3:6], vals[6:9]]
            res = c['result']
            return sum(num3(seg[j]) for j in range(3) if j != res) == num3(seg[res])
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
            elif t == 'seesaw':
                m.Add(sum(w * v[x] for w, x in zip(c['w'], rc)) == 0)
            elif t == 'fibonacci':
                for a, b, d in zip(rc, rc[1:], rc[2:]):
                    m.AddAllowedAssignments([v[a], v[b], v[d]], FIB_TRIPLES)
            elif t == 'sandwich':
                xs = [v[x] for x in rc]
                pos = {}
                for d in (1, 9):
                    bs = []
                    for x in xs:
                        b = m.NewBoolVar('')
                        m.Add(x == d).OnlyEnforceIf(b); m.Add(x != d).OnlyEnforceIf(b.Not())
                        bs.append(b)
                    p = m.NewIntVar(0, N - 1, '')
                    m.Add(p == sum(i * b for i, b in enumerate(bs)))
                    pos[d] = p
                lo = m.NewIntVar(0, N - 1, ''); hi = m.NewIntVar(0, N - 1, '')
                m.AddMinEquality(lo, [pos[1], pos[9]]); m.AddMaxEquality(hi, [pos[1], pos[9]])
                ys = []
                for i, x in enumerate(xs):
                    a = m.NewBoolVar(''); b = m.NewBoolVar(''); inside = m.NewBoolVar('')
                    m.Add(lo <= i - 1).OnlyEnforceIf(a); m.Add(lo >= i).OnlyEnforceIf(a.Not())
                    m.Add(hi >= i + 1).OnlyEnforceIf(b); m.Add(hi <= i).OnlyEnforceIf(b.Not())
                    m.AddBoolAnd([a, b]).OnlyEnforceIf(inside); m.AddBoolOr([a.Not(), b.Not()]).OnlyEnforceIf(inside.Not())
                    y = m.NewIntVar(0, 9, '')
                    m.Add(y == x).OnlyEnforceIf(inside); m.Add(y == 0).OnlyEnforceIf(inside.Not())
                    ys.append(y)
                m.Add(sum(ys) == c['sum'])
            elif t == 'between':
                lo = m.NewIntVar(1, 9, ''); hi = m.NewIntVar(1, 9, '')
                m.AddMinEquality(lo, [v[rc[0]], v[rc[-1]]]); m.AddMaxEquality(hi, [v[rc[0]], v[rc[-1]]])
                for x in rc[1:-1]:
                    m.Add(v[x] > lo); m.Add(v[x] < hi)
            elif t == 'bridge':
                p = m.NewIntVar(1, 81, '')
                m.AddMultiplicationEquality(p, [v[rc[0]], v[rc[-1]]])
                m.Add(sum(v[x] for x in rc[1:-1]) == p)
            elif t == 'xsum':
                for k in DIGITS:
                    b = m.NewBoolVar('')
                    m.Add(v[rc[0]] == k).OnlyEnforceIf(b); m.Add(v[rc[0]] != k).OnlyEnforceIf(b.Not())
                    m.Add(sum(v[x] for x in rc[:k]) == c['sum']).OnlyEnforceIf(b)
            elif t == 'skyscraper':
                vis = [1]
                pm = v[rc[0]]
                for x in rc[1:]:
                    b = m.NewBoolVar('')
                    m.Add(v[x] > pm).OnlyEnforceIf(b); m.Add(v[x] < pm).OnlyEnforceIf(b.Not())
                    nm = m.NewIntVar(1, 9, '')
                    m.AddMaxEquality(nm, [pm, v[x]])
                    vis.append(b); pm = nm
                m.Add(sum(vis) == c['count'])
            elif t == 'odometer':
                ds = []
                for a, b in zip(rc, rc[1:]):
                    d = m.NewIntVar(0, 8, '')
                    m.AddAbsEquality(d, v[a] - v[b]); ds.append(d)
                m.Add(sum(ds) == v[rc[0]])
            elif t == 'zipper':
                n = len(rc)
                tot = v[rc[n // 2]] if n % 2 else m.NewIntVar(2, 18, '')
                for i in range(n // 2):
                    m.Add(v[rc[i]] + v[rc[n - 1 - i]] == tot)
            elif t == 'equation':
                seg = [[v[x] for x in rc[3 * j:3 * j + 3]] for j in range(3)]
                res = c['result']
                m.Add(sum(num3(seg[j]) for j in range(3) if j != res) == num3(seg[res]))
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
    # run 6: optional cap on the case list of one odometer step (complete fills that survive). Steps with more
    # cases are skipped, as a human would not list them. None = no cap. Setting scripts set this class-wide.
    CASE_CAP = None

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
                       ('killer', 'renban', 'arrow', 'thermo', 'regionsum', 'littlekiller', 'seesaw', 'fibonacci', 'sandwich', 'between', 'bridge', 'slowthermo', 'xsum', 'skyscraper', 'odometer', 'equation', 'zipper') + ADJ_LINES + tuple(WINDOW_LINES)]
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
        """Run whole-constraint enumeration on the groups in order of how small their candidate space is and
        stop at the first one that makes progress (a human looks at the most constrained cage/line first)."""
        def space(g):
            if g['type'] == 'fibonacci':
                return len(cand[g['rc'][0]]) * len(cand[g['rc'][1]])
            if g['type'] == 'sandwich':
                return self.sandwich_space(g, cand)
            if g['type'] == 'between':
                return len(cand[g['rc'][0]]) * len(cand[g['rc'][-1]])
            if g['type'] in ('xsum', 'skyscraper'):
                return self.ray_space(g, cand)
            if g['type'] == 'equation':
                return max(1, self.equation_fills(g, cand)[0])
            if g['type'] == 'bridge' and len(g['rc']) > 8:
                return len(cand[g['rc'][0]]) * len(cand[g['rc'][-1]]) * 10 ** 4
            n = 1
            for a in list(g.get('crc', [])) + list(g['rc']):
                n *= len(cand[a])
            return n
        memo = self.__dict__.setdefault('_noprog', set())
        for g in sorted(self.groups, key=space):
            key = (id(g), tuple(frozenset(cand[a]) for a in list(g.get('crc', [])) + list(g['rc'])))
            if key in memo:  # same candidates as a previous call that made no progress: skip (speed only)
                continue
            if self.gac(g, cand):
                return True
            memo.add(key)
        return False

    TECHS = [('naked single', 1), ('hidden single', 1), ('pair consistency', 1),
             ('parity count', 2), ('locked candidates', 2), ('subsets', 2),
             ('pointing (general)', 2), ('seesaw bounds', 2), ('fibonacci parity', 2), ('whole-constraint consistency', 2)]

    def _tech_fn(self, nm):
        return {'naked single': self.naked_singles, 'hidden single': self.hidden_singles,
                'pair consistency': self.pair_consistency, 'parity count': self.parity_count,
                'locked candidates': self.locked_candidates, 'subsets': self.subsets,
                'pointing (general)': self.pointing_general, 'seesaw bounds': self.seesaw_bounds,
                'fibonacci parity': self.fibonacci_parity,
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
        elif t == 'slowthermo':
            rel = PAIR_REL['le']
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
        if t == 'seesaw':
            return self.gac_seesaw(g, cand, size)
        if t == 'fibonacci':
            return self.gac_fibonacci(g, cand)
        if t == 'sandwich':
            return self.gac_sandwich(g, cand)
        if t == 'between':
            return self.gac_between(g, cand)
        if t == 'bridge':
            return self.gac_bridge(g, cand)
        if t in ('xsum', 'skyscraper'):
            return self.gac_ray(g, cand)
        if t == 'odometer':
            return self.gac_odometer(g, cand)
        if t == 'equation':
            return self.gac_equation(g, cand)
        if t == 'zipper':
            return self.gac_zipper(g, cand)
        if t in WINDOW_LINES and size > 20000:
            return self.window_classes(g, cand, size)
        if t == 'littlekiller':
            return self.gac_littlekiller(g, cand, size)
        if size > 2_000_000 and t not in ('thermo', 'slowthermo') + ADJ_LINES + tuple(WINDOW_LINES):
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

    def ray_space(self, g, cand):
        """run 6: rough size of an outside clue's case list, for ordering only. X-sums: the number of (X, digit
        set) cases; skyscrapers: product of the candidate counts of the cells up to the first possible 9."""
        rc = g['rc']
        if g['type'] == 'xsum':
            n = 0
            for x in cand[rc[0]]:
                n += sum(1 for st in itertools.combinations(range(1, 10), x) if x in st and sum(st) == g['sum'])
            return max(n, 1)
        n = 1
        for a in rc:
            n *= len(cand[a])
            if 9 in cand[a]:
                break
        return n

    def gac_ray(self, g, cand):
        """Run 6. Exact consistency for an outside clue on a whole row/column read from the clue (X-sum or
        skyscraper). Walk the cells in order with the set of digits used so far (the line is a full house, so
        it is a permutation) plus a small state: X-sums keep X (the first digit), skyscrapers the number of
        visible digits (the running maximum is the largest digit used). Forward pass over reachable states,
        backward pass over states that can still finish; keep the digits used on surviving transitions.
        The recorded size is the number of human-level cases: (X, set of the first X digits) for X-sums,
        distinct sequences of visible digits for skyscrapers (capped at 5000)."""
        rc, t = g['rc'], g['type']
        n = len(rc)
        if t == 'xsum':
            S = g['sum']

            def step(i, mask, ex, d):
                if i == 0:
                    ex = d
                if i < ex:
                    s = sum(k for k in DIGITS if mask >> k & 1) + d
                    if s > S or (i == ex - 1 and s != S):
                        return None
                return ex
            acc = lambda ex: True
        else:
            C = g['count']

            def step(i, mask, ex, d):
                if mask < (1 << d):  # d is larger than every digit used so far
                    ex += 1
                    if ex > C:
                        return None
                return ex
            acc = lambda ex: ex == C
        layers = [{(0, 0)}]
        trans = []
        for i in range(n):
            nxt = set(); tr = []
            for mask, ex in layers[-1]:
                for d in cand[rc[i]]:
                    if mask >> d & 1:
                        continue
                    e2 = step(i, mask, ex, d)
                    if e2 is None:
                        continue
                    s2 = (mask | 1 << d, e2)
                    nxt.add(s2); tr.append(((mask, ex), d, s2))
            layers.append(nxt); trans.append(tr)
        alive = {s for s in layers[-1] if acc(s[1])}
        sup = [set() for _ in rc]
        live_tr = [None] * n
        for i in range(n - 1, -1, -1):
            prev_alive = set(); lt = []
            for s1, d, s2 in trans[i]:
                if s2 in alive:
                    sup[i].add(d); prev_alive.add(s1); lt.append((s1, d, s2))
            live_tr[i] = lt
            alive = prev_alive
        changed = False
        for k, a in enumerate(rc):
            if sup[k] != cand[a]:
                cand[a] = cand[a] & sup[k]; changed = True
                if not cand[a]:
                    raise Contradiction(a)
        if changed:
            self.gac_sizes.append((t, self._ray_cases(g, cand, live_tr), sum(len(x) == 1 for x in cand.values())))
        return changed

    def _ray_cases(self, g, cand, live_tr):
        if g['type'] == 'xsum':
            out = set()
            for x in cand[g['rc'][0]]:
                for st in itertools.combinations(range(1, 10), x):
                    if x in st and sum(st) == g['sum']:
                        out.add((x, st))
            return len(out)
        # distinct visible sequences along live transitions (visible digits stop growing once 9 is placed)
        by = {}
        for i, lt in enumerate(live_tr):
            for s1, d, s2 in lt:
                by.setdefault((i, s1), []).append((d, s2))
        seqs = set()

        def dfs(i, s, vis):
            if len(seqs) >= 5000:
                return
            if vis and vis[-1] == 9 or i == len(live_tr):
                seqs.add(vis); return
            for d, s2 in by.get((i, s), []):
                dfs(i + 1, s2, vis + (d,) if not vis or d > vis[-1] else vis)
        dfs(0, (0, 0), ())
        return len(seqs)

    def gac_odometer(self, g, cand):
        """Run 6 (invented). The circled first cell = total distance travelled along the line, starting at the
        circle (sum of |differences| of consecutive cells). Try every circle digit, then walk the line with the
        remaining distance as a budget; cells that see each other differ. The recorded size is the number of
        complete fills that survive."""
        cells = list(g['rc'])
        n = len(cells)
        sees = [[j for j in range(k) if self.pz.sees(cells[j], cells[k])] for k in range(n)]
        doms = [sorted(cand[a]) for a in cells]
        support = [set() for _ in range(n)]
        vals = [0] * n
        fills = [0]

        def rec(k, rem):
            if k == n:
                if rem == 0:
                    fills[0] += 1
                    for j in range(n):
                        support[j].add(vals[j])
                return
            for x in doms[k]:
                if any(vals[j] == x for j in sees[k]):
                    continue
                if k == 0:
                    vals[0] = x; rec(1, x)
                else:
                    r2 = rem - abs(x - vals[k - 1])
                    if r2 < 0:
                        continue
                    vals[k] = x; rec(k + 1, r2)
            vals[k] = 0
        rec(0, 0)
        if self.CASE_CAP is not None and fills[0] > self.CASE_CAP:
            return False
        changed = False
        for k in range(n):
            a = cells[k]
            if support[k] != cand[a]:
                cand[a] = cand[a] & support[k]; changed = True
                if not cand[a]:
                    raise Contradiction(a)
        if changed:
            self.gac_sizes.append(('odometer', fills[0], sum(len(x) == 1 for x in cand.values())))
        return changed

    def gac_zipper(self, g, cand):
        """Run 7. Try every total, then fill the pairs (outermost first) and the centre; cells that see each
        other differ. The recorded size is the number of complete fills that survive."""
        cells = list(g['rc'])
        n = len(cells)
        order = [i for k in range(n // 2) for i in (k, n - 1 - k)] + ([n // 2] if n % 2 else [])
        sees = {i: [j for j in order[:order.index(i)] if self.pz.sees(cells[i], cells[j])] for i in order}
        support = [set() for _ in range(n)]
        vals = [0] * n
        fills = [0]

        def rec(k, tot):
            if k == len(order):
                fills[0] += 1
                for j in range(n):
                    support[j].add(vals[j])
                return
            i = order[k]
            if n % 2 and i == n // 2:
                opts = [tot] if tot in cand[cells[i]] else []
            elif k % 2 == 1:
                x = tot - vals[order[k - 1]]
                opts = [x] if x in cand[cells[i]] else []
            else:
                opts = sorted(cand[cells[i]])
            for x in opts:
                if any(vals[j] == x for j in sees[i]):
                    continue
                vals[i] = x; rec(k + 1, tot)
            vals[i] = 0
        tots = sorted(cand[cells[n // 2]]) if n % 2 else range(2, 19)
        for tot in tots:
            rec(0, tot)
        if self.CASE_CAP is not None and fills[0] > self.CASE_CAP:
            return False
        changed = False
        for k in range(n):
            a = cells[k]
            if support[k] != cand[a]:
                cand[a] = cand[a] & support[k]; changed = True
                if not cand[a]:
                    raise Contradiction(a)
        if changed:
            self.gac_sizes.append(('zipper', fills[0], sum(len(x) == 1 for x in cand.values())))
        return changed

    def equation_fills(self, g, cand):
        """run 7: the sums ABC + DEF = GHI (digits 1-9 once each) that fit the current candidates of the row/column"""
        doms = [cand[a] for a in g['rc']]
        live = [p for p in EQ_PERMS[g['result']] if all(p[i] in doms[i] for i in range(N))]
        return len(live), live

    def gac_equation(self, g, cand):
        """Run 7 (invented). Keep the digits that appear in some still-possible sum. The recorded size is the
        number of complete sums that survive (out of 336); CASE_CAP skips steps with more survivors."""
        n, live = self.equation_fills(g, cand)
        if self.CASE_CAP is not None and n > self.CASE_CAP:
            return False
        if n == 0:
            raise Contradiction(g['rc'][0])
        changed = False
        for i, a in enumerate(g['rc']):
            sup = {p[i] for p in live}
            if sup != cand[a]:
                cand[a] = cand[a] & sup; changed = True
        if changed:
            self.gac_sizes.append(('equation', n, sum(len(x) == 1 for x in cand.values())))
        return changed

    def sandwich_space(self, g, cand):
        """number of (1-position, 9-position, set of sandwiched digits) cases still open"""
        rc, S = g['rc'], g['sum']
        n = 0
        for i in range(N):
            if 1 not in cand[rc[i]]:
                continue
            for j in range(N):
                if j != i and 9 in cand[rc[j]]:
                    n += len(SANDWICH_SETS.get((abs(i - j) - 1, S), []))
        return max(n, 1)

    def gac_sandwich(self, g, cand):
        """Run 5. Try every placement of the 1 and the 9 and every set of digits that can sit between them with
        the right total; the inner cells must take exactly that set and the outer cells the rest of 2-8
        (checked as perfect matchings). Keep the candidates that appear in some surviving case."""
        rc, S = g['rc'], g['sum']
        sup = [set() for _ in rc]
        cases = 0
        for i in range(N):
            if 1 not in cand[rc[i]]:
                continue
            for j in range(N):
                if j == i or 9 not in cand[rc[j]]:
                    continue
                lo, hi = min(i, j), max(i, j)
                inner = list(range(lo + 1, hi))
                outer = [k for k in range(N) if k not in (i, j) and not lo < k < hi]
                for st in SANDWICH_SETS.get((len(inner), S), []):
                    rest = set(range(2, 9)) - st
                    di = [cand[rc[k]] & st for k in inner]
                    do = [cand[rc[k]] & rest for k in outer]
                    if any(not x for x in di + do):
                        continue
                    si = _matching_support(di, [sup[k] for k in inner])
                    if inner and not all(si):
                        continue
                    so = _matching_support(do, [sup[k] for k in outer])
                    if outer and not all(so):
                        continue
                    cases += 1
                    sup[i].add(1); sup[j].add(9)
                    for k, x in zip(inner, si):
                        sup[k] |= x
                    for k, x in zip(outer, so):
                        sup[k] |= x
        changed = False
        for k, a in enumerate(rc):
            if sup[k] != cand[a]:
                cand[a] = cand[a] & sup[k]; changed = True
                if not cand[a]:
                    raise Contradiction(a)
        if changed:
            self.gac_sizes.append(('sandwich', cases, sum(len(x) == 1 for x in cand.values())))
        return changed

    def gac_between(self, g, cand):
        """Run 5. Try each pair of end digits; the inner cells must fit strictly between them, and inner cells
        sharing a house need enough different digits in that range (a necessary check, so it is sound)."""
        rc = g['rc']
        e0, e1, inner = rc[0], rc[-1], rc[1:-1]
        groups = []
        for h in self.house_sets:
            ins = [i for i, c in enumerate(inner) if c in h]
            if len(ins) > 1:
                groups.append(ins)
        sup = [set() for _ in rc]
        cases = 0
        for a in cand[e0]:
            for b in cand[e1]:
                if a == b and (inner or self.pz.sees(e0, e1)):
                    continue
                lo, hi = min(a, b), max(a, b)
                doms = [{x for x in cand[c] if lo < x < hi} for c in inner]
                if any(not d for d in doms):
                    continue
                if any(len(set().union(*(doms[i] for i in ins))) < len(ins) for ins in groups):
                    continue
                cases += 1
                sup[0].add(a); sup[-1].add(b)
                for i, d in enumerate(doms):
                    sup[i + 1] |= d
        changed = False
        for k, a in enumerate(rc):
            if sup[k] != cand[a]:
                cand[a] = cand[a] & sup[k]; changed = True
                if not cand[a]:
                    raise Contradiction(a)
        if changed:
            self.gac_sizes.append(('between', cases, sum(len(x) == 1 for x in cand.values())))
        return changed

    def gac_bridge_long(self, g, cand):
        """Run 5. Bridges with more than 6 inner cells: split the inner cells by box. A segment of up to 5 cells
        lists its fills (all different); a segment of 6+ cells of one box uses the rest of that box instead
        (segment total = 45 - total of the box cells off the segment, the 45 rule) and keeps all its candidates.
        Cells of different segments are treated as independent (a relaxation, so every removal is sound).
        A sum DP over the segments decides which end pairs and segment fills can reach the product."""
        rc = g['rc']
        e0, e1, inner = rc[0], rc[-1], rc[1:-1]
        segs = {}
        for a in inner:
            segs.setdefault(box(a), []).append(a)
        segs = list(segs.values())
        info = []  # per segment: dict sum -> list of fills (None = relaxed, all candidates kept)
        for sg in segs:
            if len(sg) <= 5:
                d = {}
                for p in itertools.product(*[sorted(cand[a]) for a in sg]):
                    if len(set(p)) == len(p):
                        d.setdefault(sum(p), []).append(p)
                info.append(d)
            else:
                b = box(sg[0])
                rest = [a for a in self.cells if box(a) == b and a not in sg]
                sums = set()
                for p in itertools.product(*[sorted(cand[a]) for a in rest]):
                    if len(set(p)) == len(p):
                        sums.add(45 - sum(p))
                info.append({x: None for x in sums})
        n = len(segs)
        fwd = [set() for _ in range(n + 1)]; fwd[0] = {0}
        for i in range(n):
            fwd[i + 1] = {x + y for x in fwd[i] for y in info[i] if x + y <= 81}
        bwd = [set() for _ in range(n + 1)]; bwd[n] = {0}
        for i in range(n - 1, -1, -1):
            bwd[i] = {x + y for x in bwd[i + 1] for y in info[i] if x + y <= 81}
        sup0, sup1 = set(), set()
        prods = set()
        for a in cand[e0]:
            for b in cand[e1]:
                if a == b and self.pz.sees(e0, e1):
                    continue
                if a * b in fwd[n]:
                    sup0.add(a); sup1.add(b); prods.add(a * b)
        sup = {a: set() for a in inner}
        cases = 0
        for i, sg in enumerate(segs):
            for sval, fills in info[i].items():
                if not any(P - sval - x in bwd[i + 1] for P in prods for x in fwd[i]):
                    continue
                cases += 1
                if fills is None:
                    for a in sg:
                        sup[a] |= cand[a]
                else:
                    for p in fills:
                        for a, v in zip(sg, p):
                            sup[a].add(v)
        changed = False
        for a, sp in [(e0, sup0), (e1, sup1)] + list(sup.items()):
            if sp != cand[a]:
                cand[a] = cand[a] & sp; changed = True
                if not cand[a]:
                    raise Contradiction(a)
        if changed:
            self.gac_sizes.append(('bridge', cases, sum(len(x) == 1 for x in cand.values())))
        return changed

    def gac_bridge(self, g, cand):
        """Run 5 (invented). Ends first, then the inner cells with sum bounds; cells that see each other differ.
        The recorded size is the number of complete fills that survive (the cases a solver would weigh)."""
        rc = g['rc']
        if len(rc) > 8:
            return self.gac_bridge_long(g, cand)
        order = [0, len(rc) - 1] + list(range(1, len(rc) - 1))
        cells = [rc[i] for i in order]
        doms = [sorted(cand[c]) for c in cells]
        n = len(cells)
        sees = [[j for j in range(k) if self.pz.sees(cells[j], cells[k])] for k in range(n)]
        lo = [0] * (n + 1); hi = [0] * (n + 1)
        for k in range(n - 1, 1, -1):
            lo[k] = lo[k + 1] + doms[k][0]; hi[k] = hi[k + 1] + doms[k][-1]
        support = [set() for _ in range(n)]
        vals = [0] * n
        fills = [0]

        def rec(k, rem):
            if k == n:
                if rem == 0:
                    fills[0] += 1
                    for j in range(n):
                        support[j].add(vals[j])
                return
            for x in doms[k]:
                if any(vals[j] == x for j in sees[k]):
                    continue
                vals[k] = x
                if k == 1:
                    r2 = vals[0] * x
                    if not (lo[2] <= r2 <= hi[2]):
                        continue
                    rec(2, r2)
                elif k == 0:
                    rec(1, 0)
                else:
                    r2 = rem - x
                    if lo[k + 1] <= r2 <= hi[k + 1]:
                        rec(k + 1, r2)
            vals[k] = 0
        rec(0, 0)
        changed = False
        for k in range(n):
            a = cells[k]
            if support[k] != cand[a]:
                cand[a] = cand[a] & support[k]; changed = True
                if not cand[a]:
                    raise Contradiction(a)
        if changed:
            self.gac_sizes.append(('bridge', fills[0], sum(len(x) == 1 for x in cand.values())))
        return changed

    def gac_littlekiller(self, g, cand, size):
        """Run 4. Exact consistency for a diagonal sum: split the diagonal into its box segments (cells in one
        box differ, cells in different boxes never share a row or column), list each segment's fills, and keep
        a fill only if the other segments can make up the rest of the total (sum DP forwards and backwards)."""
        rc, target = g['rc'], g['sum']
        segs = [[rc[0]]]
        for a in rc[1:]:
            if box(a) == box(segs[-1][-1]):
                segs[-1].append(a)
            else:
                segs.append([a])
        fills = []
        for sg in segs:
            f = [p for p in itertools.product(*[sorted(cand[a]) for a in sg]) if len(set(p)) == len(p)]
            fills.append(f)
        n = len(segs)
        fwd = [set() for _ in range(n + 1)]; fwd[0] = {0}
        for i in range(n):
            sums = {sum(p) for p in fills[i]}
            fwd[i + 1] = {x + y for x in fwd[i] for y in sums if x + y <= target}
        bwd = [set() for _ in range(n + 1)]; bwd[n] = {0}
        for i in range(n - 1, -1, -1):
            sums = {sum(p) for p in fills[i]}
            bwd[i] = {x + y for x in bwd[i + 1] for y in sums if x + y <= target}
        changed = False
        count = 0
        for i, sg in enumerate(segs):
            sup = [set() for _ in sg]
            for p in fills[i]:
                sp = sum(p)
                if any(target - sp - x in bwd[i + 1] for x in fwd[i]):
                    count += 1
                    for j, v in enumerate(p):
                        sup[j].add(v)
            for j, a in enumerate(sg):
                if sup[j] != cand[a]:
                    cand[a] = cand[a] & sup[j]; changed = True
                    if not cand[a]:
                        raise Contradiction(a)
        if changed:
            self.gac_sizes.append(('littlekiller', size, sum(len(x) == 1 for x in cand.values())))
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

    def fibonacci_parity(self, cand):
        """Run 4. Units digits keep parity, so a Fibonacci line of 3+ cells is either all even or has the
        pattern odd-odd-even repeating (in one of three phases). Each house holds exactly four even digits:
        for every house, try the combinations of patterns of the lines that pass through it and keep only
        the patterns (and parities of off-line cells) that can make the count four."""
        lines = [g for g in self.groups if g['type'] == 'fibonacci' and len(g['rc']) >= 3]
        if not lines:
            return False
        EV = {2, 4, 6, 8}; OD = {1, 3, 5, 7, 9}
        pats = []
        for g in lines:
            n = len(g['rc'])
            opts = [tuple((i + p) % 3 == 2 for i in range(n)) for p in range(3)] + [tuple([True] * n)]
            opts = [o for o in opts if all(cand[a] & (EV if e else OD) for a, e in zip(g['rc'], o))]
            pats.append(set(opts))
        free_par = {}
        on_line = {a for g in lines for a in g['rc']}
        changed_any = True
        while changed_any:
            changed_any = False
            for h in self.pz.houses:
                hs = set(h)
                touching = [i for i, g in enumerate(lines) if any(a in hs for a in g['rc'])]
                if not touching:
                    continue
                free = [a for a in h if a not in on_line]
                fmin = sum(1 for a in free if cand[a] <= EV)
                fmax = sum(1 for a in free if cand[a] & EV)
                opts = []
                for i in touching:
                    rc = lines[i]['rc']
                    idx = [k for k, a in enumerate(rc) if a in hs]
                    by_cnt = {}
                    for o in pats[i]:
                        by_cnt.setdefault(sum(o[k] for k in idx), []).append(o)
                    opts.append(by_cnt)
                sup = [set() for _ in touching]
                need = set()
                for combo in itertools.product(*[list(o.keys()) for o in opts]):
                    rest = 4 - sum(combo)
                    if fmin <= rest <= fmax:
                        need.add(rest)
                        for j, c in enumerate(combo):
                            sup[j].add(c)
                if not need:
                    raise Contradiction(h[0])
                for j, i in enumerate(touching):
                    keep = {o for c in sup[j] for o in opts[j][c]}
                    if keep != pats[i]:
                        pats[i] = keep; changed_any = True
                mixed = [a for a in free if cand[a] & EV and cand[a] & OD]
                if mixed and max(need) == fmin:
                    for a in mixed:
                        free_par[a] = OD
                if mixed and min(need) == fmax:
                    for a in mixed:
                        free_par[a] = EV
        changed = False
        for g, ps in zip(lines, pats):
            for k, a in enumerate(g['rc']):
                allowed = set()
                for o in ps:
                    allowed |= EV if o[k] else OD
                if cand[a] - allowed:
                    cand[a] &= allowed; changed = True
                    if not cand[a]:
                        raise Contradiction(a)
        for a, par in free_par.items():
            if cand[a] - par:
                cand[a] &= par; changed = True
                if not cand[a]:
                    raise Contradiction(a)
        return changed

    def seesaw_bounds(self, cand):
        """Human-style min/max reasoning on seesaws: the torque on one side must be reachable by the other.
        Bounds use each cell's smallest/largest candidate and, for cells that all see each other, the fact that
        the digits are different (largest weight gets the smallest digit for the minimum, etc.)."""
        changed = False
        for g in self.groups:
            if g['type'] != 'seesaw':
                continue
            rc, w = g['rc'], g['w']
            allsee = all(self.pz.sees(a, b) for a, b in itertools.combinations(rc, 2))

            def side_bounds(idx):
                # bounds of sum(|w_i| d_i) over idx
                lo = sum(abs(w[i]) * min(cand[rc[i]]) for i in idx)
                hi = sum(abs(w[i]) * max(cand[rc[i]]) for i in idx)
                if allsee:
                    ws = sorted((abs(w[i]) for i in idx), reverse=True)
                    lo = max(lo, sum(x * (j + 1) for j, x in enumerate(ws)))
                    hi = min(hi, sum(x * (9 - j) for j, x in enumerate(ws)))
                return lo, hi
            for k, a in enumerate(rc):
                if w[k] == 0 or len(cand[a]) < 2:
                    continue
                same = [i for i in range(len(rc)) if i != k and w[i] * w[k] > 0]
                opp = [i for i in range(len(rc)) if w[i] * w[k] < 0]
                slo, shi = side_bounds(same)
                olo, ohi = side_bounds(opp)
                keep = {v for v in cand[a] if abs(w[k]) * v + slo <= ohi and abs(w[k]) * v + shi >= olo}
                if keep != cand[a]:
                    cand[a] = keep; changed = True
                    if not keep:
                        raise Contradiction(a)
        return changed

    def gac_seesaw(self, g, cand, size):
        """weighted sum = 0, cells that see each other differ. DFS with bounds on the remaining weighted sum."""
        rc, w = g['rc'], g['w']
        order = sorted(range(len(rc)), key=lambda i: -abs(w[i]))
        doms = [sorted(cand[rc[i]]) for i in order]
        ws = [w[i] for i in order]
        cells = [rc[i] for i in order]
        n = len(order)
        lo = [0] * (n + 1); hi = [0] * (n + 1)
        for k in range(n - 1, -1, -1):
            a, b = ws[k] * doms[k][0], ws[k] * doms[k][-1]
            lo[k] = lo[k + 1] + min(a, b); hi[k] = hi[k + 1] + max(a, b)
        sees = [[j for j in range(k) if self.pz.sees(cells[j], cells[k])] for k in range(n)]
        support = [set() for _ in range(n)]
        vals = [0] * n
        work = [0]
        fills = [0]

        def rec(k, s):
            work[0] += 1
            if k == n:
                if s == 0:
                    fills[0] += 1
                    for j in range(n):
                        support[j].add(vals[j])
                return
            for x in doms[k]:
                if any(vals[j] == x for j in sees[k]):
                    continue
                s2 = s + ws[k] * x
                if not (lo[k + 1] <= -s2 <= hi[k + 1]):
                    continue
                vals[k] = x
                rec(k + 1, s2)
            vals[k] = 0
        rec(0, 0)
        changed = False
        for k in range(n):
            a = cells[k]
            if support[k] != cand[a]:
                cand[a] = cand[a] & support[k]; changed = True
                if not cand[a]:
                    raise Contradiction(a)
        if changed:
            # recorded size = number of balancing fills a solver has to consider (not the raw candidate product)
            self.gac_sizes.append(('seesaw', fills[0], sum(len(x) == 1 for x in cand.values())))
        return changed

    def gac_fibonacci(self, g, cand):
        """the first two digits fix the whole line: try every seed pair (a human tries the few seeds left)."""
        rc = g['rc']
        n = len(rc)
        sees = [[j for j in range(k) if self.pz.sees(rc[j], rc[k])] for k in range(n)]
        support = [set() for _ in range(n)]
        seeds = 0
        for a in cand[rc[0]]:
            for b in cand[rc[1]]:
                seq = [a, b]
                while len(seq) < n:
                    seq.append((seq[-1] + seq[-2]) % 10)
                if any(seq[k] not in cand[rc[k]] for k in range(n)):
                    continue
                if any(seq[k] == seq[j] for k in range(n) for j in sees[k]):
                    continue
                seeds += 1
                for k in range(n):
                    support[k].add(seq[k])
        changed = False
        for k, x in enumerate(rc):
            if support[k] != cand[x]:
                cand[x] = cand[x] & support[k]; changed = True
                if not cand[x]:
                    raise Contradiction(x)
        if changed:
            self.gac_sizes.append(('fibonacci', len(cand[rc[0]]) * len(cand[rc[1]]), sum(len(x) == 1 for x in cand.values())))
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
    has_lk = any(c['type'] in ('littlekiller', 'sandwich', 'xsum', 'skyscraper') and 'from' in c for c in pz.cons)
    M = int(0.8 * S) if has_lk else 20
    W = S * N + 2 * M
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{W}" viewBox="0 0 {W} {W}" font-family="Helvetica, Arial, sans-serif">',
           f'<rect width="{W}" height="{W}" fill="white"/>']

    def cx(rc):
        return M + rc[1] * S + S / 2, M + rc[0] * S + S / 2

    op = 0.4 if solution else 0.85
    colors = {'whisper': '#5fd35f', 'dutch': '#f28c28', 'zipper': '#b58ae6', 'keypad': '#d27bd8', 'renban': '#e08ae0', 'parity': '#e6a23c',
              'knight': '#9b59d0', 'entropic': '#f0a030', 'modular': '#30b0c0', 'regionsum': '#4a90e2'}
    # cages first (under lines)
    for c in pz.cons:
        if c['type'] == 'killer':
            out.append(cage_svg(c['rc'], c.get('sum'), S, M))
    for c in pz.cons:
        t = c['type']
        if t in colors:
            col = c.get('color', colors[t])
            w = {'renban': 0.35, 'keypad': 0.22, 'zipper': 0.3, 'dutch': 0.2}.get(t, 0.22) * S
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
            (ax_, ay_), (bx_, by_) = pts[-2], pts[-1]  # run 6: arrowhead at the tip
            L_ = ((bx_ - ax_) ** 2 + (by_ - ay_) ** 2) ** 0.5
            ux, uy = (bx_ - ax_) / L_, (by_ - ay_) / L_
            h = 0.22 * S
            out.append(f'<polyline points="{bx_ - ux*h - uy*h*0.7:.1f},{by_ - uy*h + ux*h*0.7:.1f} {bx_:.1f},{by_:.1f} {bx_ - ux*h + uy*h*0.7:.1f},{by_ - uy*h - ux*h*0.7:.1f}" fill="none" stroke="#888" stroke-width="2.5" stroke-linejoin="round"/>')
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.4*S:.1f}" fill="white" stroke="#888" stroke-width="2.5"/>')
        elif t == 'fibonacci':
            pts = ' '.join(f"{x:.1f},{y:.1f}" for x, y in map(cx, c['rc']))
            col = c.get('color', '#d99a00')
            out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{0.16*S:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="{0.45 if solution else 0.95}"/>')
            x, y = cx(c['rc'][0])
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.25*S:.1f}" fill="{col}" opacity="{0.45 if solution else 0.95}"/>')
        elif t == 'slowthermo':
            col = c.get('color', '#9cc8ec')
            pts = ' '.join(f"{x:.1f},{y:.1f}" for x, y in map(cx, c['rc']))
            out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{0.3*S:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
            if not c.get('nobulb'):
                x, y = cx(c['rc'][0])
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.36*S:.1f}" fill="{col}"/>')
        elif t == 'between':
            pts = ' '.join(f"{x:.1f},{y:.1f}" for x, y in map(cx, c['rc']))
            out.append(f'<polyline points="{pts}" fill="none" stroke="#9a9a9a" stroke-width="{0.1*S:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="{0.5 if solution else 1}"/>')
            for e in (c['rc'][0], c['rc'][-1]):
                x, y = cx(e)
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.4*S:.1f}" fill="white" stroke="#9a9a9a" stroke-width="{0.05*S:.1f}"/>')
        elif t == 'bridge':
            pts = ' '.join(f"{x:.1f},{y:.1f}" for x, y in map(cx, c['rc']))
            col = c.get('color', '#2a8c82')
            out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{0.14*S:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="{0.5 if solution else 0.9}"/>')
            for e in (c['rc'][0], c['rc'][-1]):
                x, y = cx(e)
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.3*S:.1f}" fill="#d6efec" stroke="{col}" stroke-width="{0.06*S:.1f}"/>')
        elif t == 'odometer':
            col = c.get('color', '#3a78c2')
            o = 0.5 if solution else 0.95
            pts = [cx(r) for r in c['rc']]
            out.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{col}" stroke-width="{0.07*S:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="{o}"/>')
            (ax, ay), (bx, by) = pts[-2], pts[-1]
            L_ = ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
            ux, uy = (bx - ax) / L_, (by - ay) / L_
            h = 0.22 * S
            p1 = (bx - ux * h - uy * h * 0.7, by - uy * h + ux * h * 0.7)
            p2 = (bx - ux * h + uy * h * 0.7, by - uy * h - ux * h * 0.7)
            out.append(f'<polyline points="{p1[0]:.1f},{p1[1]:.1f} {bx:.1f},{by:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="none" stroke="{col}" stroke-width="{0.07*S:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="{o}"/>')
            x, y = cx(c['rc'][0])
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.4*S:.1f}" fill="white" stroke="{col}" stroke-width="{0.07*S:.1f}" stroke-opacity="{o}"/>')
        elif t == 'seesaw':
            pts = ' '.join(f"{x:.1f},{y:.1f}" for x, y in map(cx, c['rc']))
            out.append(f'<polyline points="{pts}" fill="none" stroke="#b07a3c" stroke-width="{0.2*S:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="{0.45 if solution else 0.9}"/>')
            x, y = cx(parse(c['pivot']))
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.36*S:.1f}" fill="white" stroke="#4a2c0f" stroke-width="{0.06*S:.1f}"/>')
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
                out.append(f'<rect x="{x-0.2*S:.1f}" y="{y-0.2*S:.1f}" width="{0.4*S:.1f}" height="{0.4*S:.1f}" fill="white"/>')
                out.append(f'<text x="{x:.1f}" y="{y+0.14*S:.1f}" font-size="{0.4*S:.1f}" text-anchor="middle" font-weight="bold">{c["value"]}</text>')
            else:
                fill = 'black' if t == 'kropki_b' else 'white'
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.12*S:.1f}" fill="{fill}" stroke="black" stroke-width="1.5"/>')
    for c in pz.cons:
        if c['type'] == 'littlekiller' and 'from' in c:
            fr = parse(c['from'])
            dr, dc = LK_DIRS[c['dir']]
            x, y = cx(fr)
            # number nudged away from the grid, arrow pointing from the clue towards the first cell
            x0, y0 = x - dc * 0.12 * S, y - dr * 0.12 * S
            out.append(f'<text x="{x0:.1f}" y="{y0+0.11*S:.1f}" font-size="{0.32*S:.1f}" text-anchor="middle">{c["sum"]}</text>')
            ax, ay = x + dc * 0.22 * S, y + dr * 0.22 * S
            bx, by = x + dc * 0.46 * S, y + dr * 0.46 * S
            out.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="black" stroke-width="1.6"/>')
            h = 0.1 * S
            out.append(f'<polyline points="{bx-dc*h:.1f},{by:.1f} {bx:.1f},{by:.1f} {bx:.1f},{by-dr*h:.1f}" fill="none" stroke="black" stroke-width="1.6"/>')
    for c in pz.cons:
        if c['type'] == 'sandwich':
            x, y = cx(parse(c['from']))
            out.append(f'<text x="{x:.1f}" y="{y+0.14*S:.1f}" font-size="{0.4*S:.1f}" text-anchor="middle">{c["sum"]}</text>')
    for c in pz.cons:
        if c['type'] == 'xsum':
            x, y = cx(parse(c['from']))
            out.append(f'<text x="{x:.1f}" y="{y+0.14*S:.1f}" font-size="{0.4*S:.1f}" text-anchor="middle" font-style="italic">{c["sum"]}</text>')
        elif c['type'] == 'skyscraper':
            x, y = cx(parse(c['from']))
            out.append(f'<rect x="{x-0.25*S:.1f}" y="{y-0.25*S:.1f}" width="{0.5*S:.1f}" height="{0.5*S:.1f}" rx="{0.05*S:.1f}" fill="#e3e3e3" stroke="#555" stroke-width="1.2"/>')
            out.append(f'<text x="{x:.1f}" y="{y+0.13*S:.1f}" font-size="{0.36*S:.1f}" text-anchor="middle" font-weight="bold">{c["count"]}</text>')
    for c in pz.cons:
        if c['type'] == 'equation':
            rc = c['rc']
            syms = ['=', '+'] if c['result'] == 0 else ['+', '=']
            for j, sym in enumerate(syms):
                (x1, y1), (x2, y2) = cx(rc[3 * j + 2]), cx(rc[3 * j + 3])
                x, y = (x1 + x2) / 2, (y1 + y2) / 2
                col = c.get('color', '#b03a2e')
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.2*S:.1f}" fill="white" stroke="{col}" stroke-width="{0.04*S:.1f}"/>')
                if sym == '+':
                    out.append(f'<path d="M{x-0.11*S:.1f},{y:.1f} H{x+0.11*S:.1f} M{x:.1f},{y-0.11*S:.1f} V{y+0.11*S:.1f}" stroke="{col}" stroke-width="{0.05*S:.1f}" stroke-linecap="round"/>')
                else:
                    out.append(f'<path d="M{x-0.1*S:.1f},{y-0.05*S:.1f} H{x+0.1*S:.1f} M{x-0.1*S:.1f},{y+0.05*S:.1f} H{x+0.1*S:.1f}" stroke="{col}" stroke-width="{0.05*S:.1f}" stroke-linecap="round"/>')
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
    colors = {'whisper': '#67F067', 'dutch': '#F28C28', 'zipper': '#B58AE6', 'keypad': '#D27BD8', 'renban': '#F067F0', 'parity': '#E6A23C',
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
                                             "width": {'renban': 0.35, 'zipper': 0.3, 'dutch': 0.2}.get(t, 0.25), "isNewConstraint": True})
        elif t == 'seesaw':
            J.setdefault('line', []).append({"lines": [[U(x) for x in c['rc']]], "outlineC": "#B07A3C", "width": 0.2, "isNewConstraint": True})
            J.setdefault('circle', []).append({"cells": [U(parse(c['pivot']))], "baseC": "#FFFFFF", "outlineC": "#4A2C0F",
                                               "fontC": "#000000", "width": 0.72, "height": 0.72, "angle": 0, "value": ""})
        elif t == 'fibonacci':
            col = c.get('fcolor', '#D99A00')
            J.setdefault('line', []).append({"lines": [[U(x) for x in c['rc']]], "outlineC": col, "width": 0.16, "isNewConstraint": True})
            J.setdefault('circle', []).append({"cells": [U(c['rc'][0])], "baseC": col, "outlineC": col,
                                               "fontC": "#000000", "width": 0.5, "height": 0.5, "angle": 0, "value": ""})
        elif t == 'littlekiller' and 'from' in c:
            J.setdefault('littlekillersum', []).append({"cell": c['from'].upper(), "cells": [U(x) for x in c['rc']],
                                                        "direction": c['dir'], "value": str(c['sum'])})
        elif t == 'slowthermo':
            J.setdefault('slowthermometer', []).append({"lines": [[U(x) for x in c['rc']]]})
        elif t == 'sandwich':
            J.setdefault('sandwichsum', []).append({"cell": c['from'].upper(), "value": str(c['sum'])})
        elif t == 'between':
            J.setdefault('betweenline', []).append({"lines": [[U(x) for x in c['rc']]]})
        elif t == 'xsum':
            J.setdefault('xsum', []).append({"cell": c['from'].upper(), "value": str(c['sum'])})
        elif t == 'skyscraper':
            J.setdefault('skyscraper', []).append({"cell": c['from'].upper(), "value": str(c['count'])})
        elif t == 'odometer':
            col = c.get('fcolor', '#3A78C2')
            J.setdefault('line', []).append({"lines": [[U(x) for x in c['rc']]], "outlineC": col, "width": 0.07, "isNewConstraint": True})
            J.setdefault('circle', []).append({"cells": [U(c['rc'][0])], "baseC": "#FFFFFF", "outlineC": col,
                                               "fontC": "#000000", "width": 0.8, "height": 0.8, "angle": 0, "value": ""})
        elif t == 'bridge':
            col = c.get('fcolor', '#2A8C82')
            J.setdefault('line', []).append({"lines": [[U(x) for x in c['rc']]], "outlineC": col, "width": 0.14, "isNewConstraint": True})
            for e in (c['rc'][0], c['rc'][-1]):
                J.setdefault('circle', []).append({"cells": [U(e)], "baseC": "#D6EFEC", "outlineC": col,
                                                   "fontC": "#000000", "width": 0.6, "height": 0.6, "angle": 0, "value": ""})
        elif t == 'equation':
            syms = ['=', '+'] if c['result'] == 0 else ['+', '=']
            for j, sym in enumerate(syms):
                J.setdefault('circle', []).append({"cells": [U(c['rc'][3 * j + 2]), U(c['rc'][3 * j + 3])], "baseC": "#FFFFFF",
                                                   "outlineC": "#B03A2E", "fontC": "#B03A2E", "width": 0.4, "height": 0.4,
                                                   "angle": 0, "value": sym})
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
        neg.append('ratio')
    if neg:
        J['negative'] = neg
    # run 7 fix: f-puzzles has no "difference" entry in `negative`; its negative white-dot rule is the top-level
    # flag `nonconsecutive` (see SolverFactory.cs in Rangsk's SudokuSolver). Runs 4-6 exported negative: ["difference"].
    if 'neg_kropki' in pz.glob or 'neg_kropki_w' in pz.glob:
        J['nonconsecutive'] = True
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
