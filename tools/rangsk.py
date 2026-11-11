"""Run 5: independent cross-check with Rangsk's SudokuSolver (github.com/dclamage/SudokuSolver), through our own
f-puzzles export. Only meaningful when every constraint has a native f-puzzles form (see NATIVE).
Build: install the .NET SDK (dotnet-install.sh --channel 10.0), clone the repo, `dotnet build SudokuSolverConsole -c Release`.
Set SUDOKUSOLVER to the built SudokuSolverConsole binary and DOTNET_ROOT to the SDK (defaults: /tmp/SudokuSolver, /tmp/dotnet).

python3 rangsk.py spec.json          -> solution count (-k) and logical solve path (-l)"""
import sys, os, json, subprocess
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from vs import *
from nfa import NFAS, NFA_ORDER

BIN = os.environ.get('SUDOKUSOLVER', '/tmp/SudokuSolver/SudokuSolverConsole/bin/Release/net10.0/SudokuSolverConsole')
DOTNET = os.environ.get('DOTNET_ROOT', '/tmp/dotnet')
NATIVE = {'palindrome', 'whisper', 'dutch', 'zipper', 'renban', 'thermo', 'killer', 'arrow', 'kropki_w', 'kropki_b', 'xv', 'littlekiller', 'sandwich', 'between', 'slowthermo', 'xsum', 'skyscraper'}
NATIVE_GLOBAL = {'antiknight', 'antiking', 'diag+', 'diag-', 'neg_kropki', 'neg_kropki_w', 'neg_xv'}


def available():
    return os.path.isfile(BIN)


def native(pz):
    """every constraint is either native to f-puzzles or (run 6) encodable as an NFA line (see nfa.py)"""
    return all(c['type'] in NATIVE or c['type'] in NFAS for c in pz.cons) and pz.glob <= NATIVE_GLOBAL


def load_string(pz):
    J = fpuzzles_json(pz, {(r, k): 0 for r in range(N) for k in range(N)})
    del J['solution']  # the solver must not see the answer
    # run 7: lines that the play links show as cosmetic lines but that this solver knows natively
    for c in pz.cons:
        cells = [f"R{a[0]+1}C{a[1]+1}" for a in c['rc']]
        if c['type'] in ('whisper', 'dutch'):
            J.setdefault('whispers', []).append({"lines": [cells], "value": "5" if c['type'] == 'whisper' else "4"})
        elif c['type'] == 'zipper':
            J.setdefault('zipperline', []).append({"lines": [cells]})
        elif c['type'] == 'renban':
            J.setdefault('renban', []).append({"lines": [cells]})
    # run 6: invented line rules go in as NFA constraints (cosmetic lines/circles stay, they have no effect)
    for c in pz.cons:
        if c['type'] in NFAS:
            order = NFA_ORDER[c['type']](c) if c['type'] in NFA_ORDER else c['rc']
            J.setdefault('nfaConstraints', []).append({"cells": [f"R{a[0]+1}C{a[1]+1}" for a in order],
                                                      "nfa": NFAS[c['type']](len(order)), "name": c['type'].capitalize()})
    js = json.dumps(J, separators=(',', ':'))
    return subprocess.run(['node', '-e', "const lz=require('/tmp/lz/node_modules/lz-string');let s='';process.stdin.on('data',d=>s+=d).on('end',()=>process.stdout.write(lz.compressToBase64(s)))"],
                          input=js.encode(), capture_output=True, check=True).stdout.decode()


def run(pz, *flags, timeout=900):
    env = dict(os.environ, DOTNET_ROOT=DOTNET, PATH=DOTNET + ':' + os.environ['PATH'], DOTNET_CLI_TELEMETRY_OPTOUT='1')
    r = subprocess.run([BIN, '--hide-banner', '-f', load_string(pz)] + list(flags), capture_output=True, text=True, env=env, timeout=timeout)
    return r.stdout + r.stderr


def check(pz):
    """returns (solution count text, solved logically?, solved grid string or None, list of non-single steps)"""
    k = [l for l in run(pz, '-k').splitlines() if 'solution' in l.lower()]
    out = run(pz, '-l', '--verbose')
    lines = [l for l in out.splitlines() if not any(ch in l for ch in '║╟╠╔╚')]
    grid = next((l.strip() for l in lines if len(l.strip()) == 81 and l.strip().isdigit()), None)
    solved = grid is not None and '0' not in grid
    steps = [l.strip() for l in lines if l.strip() and not l.startswith(('Imported', 'Solving', 'Took', ' ')) and l.strip() != grid]
    return (k[0].strip() if k else '?'), solved, grid, steps


if __name__ == '__main__':
    pz = load(sys.argv[1])
    cnt, solved, grid, steps = check(pz)
    print(cnt, 'logical:', 'solved' if solved else 'not solved')
    print('\n'.join(s for s in steps if 'Single' not in s))
