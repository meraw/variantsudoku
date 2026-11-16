"""Run 13: the NFA decoder of soundness_run11/12 as an importable module."""
import base64


def decode(s):  # copied from soundness_run11 (importing it would rerun its tests)
    by = base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))
    bits = ''.join(f'{b:08b}' for b in by); pos = [0]

    def get(n):
        v = int(bits[pos[0]:pos[0] + n], 2) if n else 0; pos[0] += n; return v
    assert get(2) == 0
    sb = get(4) + 1; nsym = get(4) + 1
    nstart = get(sb); nacc = get(sb)
    sia = get(nstart)
    tcb = get(4)
    trans = []
    while len(bits) - pos[0] >= tcb and (len(trans) < (1 << sb)):
        save = pos[0]
        n = get(tcb)
        if pos[0] + n * (4 + sb) > len(bits):
            pos[0] = save; break
        trans.append([(get((nsym - 1).bit_length()), get(sb)) for _ in range(n)])
    start = set(range(nstart))
    accept = set(range(nstart, nstart + nacc)) | {i for i in range(nstart) if sia >> i & 1}
    return start, accept, trans


def accepts(nfa, seq):
    start, accept, trans = nfa
    cur = set(start)
    for d in seq:
        cur = {t for s in cur if s < len(trans) for sym, t in trans[s] if sym == d - 1}
    return bool(cur & accept)
