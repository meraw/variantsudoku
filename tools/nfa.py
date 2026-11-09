"""Run 6: NFA encodings of invented line rules, for an independent check with Rangsk's SudokuSolver.

Rangsk's solver accepts `nfaConstraints` in f-puzzles JSON: a list of {"cells": [...], "nfa": <serialized>, "name": ...}.
The serialized form is the bit stream read by `NFADeserializer` in SudokuSolver/Constraints/NFAConstraint.cs
(the format of sigh's Interactive Sudoku Solver): MSB-first bits, url-safe base64. We write the PLAIN format:
  format (2 bits) = 0, stateBits-1 (4), symbolCount-1 (4), startCount (stateBits), acceptCount (stateBits),
  startIsAccept (startCount bits), transitionCountBits (4), then per state in order: a transition count
  (transitionCountBits) followed by (symbol, target) pairs (symbolBits, stateBits).
State numbering: start states first, then accepting states, then the rest. Symbol k = digit k + 1.
The NFA only describes the digit sequence along the line; sudoku rules (repeats) are the solver's job."""
import base64


def serialize(n_states, start, accept, trans, n_symbols=9):
    """start: list of state ids, accept: list of state ids, trans: dict state -> list of (symbol, target).
    Renumbers states so that starts come first and accepting states next."""
    start = list(start)
    acc_only = [s for s in accept if s not in start]
    rest = [s for s in range(n_states) if s not in start and s not in acc_only]
    order = start + acc_only + rest
    idx = {s: i for i, s in enumerate(order)}
    state_bits = max(1, (len(order) - 1).bit_length())
    assert state_bits <= 16 and len(start) < 31
    sym_bits = max(1, (n_symbols - 1).bit_length())
    max_t = max([len(trans.get(s, [])) for s in order] + [1])
    tc_bits = max(1, max_t.bit_length())
    assert tc_bits <= 15
    bits = []

    def put(v, n):
        for i in range(n - 1, -1, -1):
            bits.append((v >> i) & 1)
    put(0, 2); put(state_bits - 1, 4); put(n_symbols - 1, 4)
    put(len(start), state_bits); put(len(acc_only), state_bits)
    sia = 0
    for i, s in enumerate(start):  # bit i of the int read MSB-first = start state i accepting
        if s in accept:
            sia |= 1 << i
    put(sia, len(start))
    put(tc_bits, 4)
    for s in order:
        ts = trans.get(s, [])
        put(len(ts), tc_bits)
        for sym, tgt in ts:
            put(sym, sym_bits); put(idx[tgt], state_bits)
    while len(bits) % 8:
        bits.append(0)
    by = bytes(int(''.join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8))
    return base64.urlsafe_b64encode(by).decode().rstrip('=')


def odometer_nfa(n=None):
    """circled first digit c; after it, state (last digit, distance still to travel); accept when 0 is left."""
    sid = {}

    def S(last, rem):
        return sid.setdefault((last, rem), len(sid) + 1)
    trans = {0: []}
    for c in range(1, 10):
        trans[0].append((c - 1, S(c, c)))
    for last in range(1, 10):
        for rem in range(0, 10):
            s = S(last, rem)
            for d in range(1, 10):
                r2 = rem - abs(d - last)
                if r2 >= 0:
                    trans.setdefault(s, []).append((d - 1, S(d, r2)))
    accept = [sid[(l, 0)] for l in range(1, 10)]
    return serialize(len(sid) + 1, [0], accept, trans)


def bridge_nfa(n=11):
    """product of the two end digits = sum of the inner digits: state (first digit, inner sum so far); reading a
    digit either adds it to the sum or (nondeterministically) ends the line if first * digit = sum.
    Sums are capped at 9 * (n - 2) for a line of n cells, to keep the encoding short."""
    cap = min(81, 9 * (n - 2))
    sid = {}

    def S(a, s):
        return sid.setdefault((a, s), len(sid) + 2)
    END = 1
    trans = {0: [], END: []}
    for a in range(1, 10):
        trans[0].append((a - 1, S(a, 0)))
    for a in range(1, 10):
        for s in range(0, cap + 1):
            st = S(a, s)
            for d in range(1, 10):
                if s > 0 and a * d == s:
                    trans.setdefault(st, []).append((d - 1, END))
                if s + d <= cap:
                    trans.setdefault(st, []).append((d - 1, S(a, s + d)))
    return serialize(len(sid) + 2, [0], [END], trans)


NFAS = {'odometer': odometer_nfa, 'bridge': bridge_nfa}
