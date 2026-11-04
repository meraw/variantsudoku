"""Rebuild index.html from puzzles/*/ (newest = highest number first)."""
import os, json, re, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_URL = 'https://github.com/meraw/variantsudoku/blob/main/SETTER_LOG.md'


def md(text):
    out, para, code = [], [], None
    def inline(t):
        t = html.escape(t)
        t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
        t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
        t = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', t)
        t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
        return t
    def flush():
        if para:
            out.append('<p>' + inline(' '.join(para)) + '</p>'); para.clear()
    for line in text.splitlines():
        if line.startswith('```'):
            if code is None:
                flush(); code = []
            else:
                out.append('<pre>' + html.escape('\n'.join(code)) + '</pre>'); code = None
            continue
        if code is not None:
            code.append(line); continue
        if line.startswith('#'):
            flush(); continue
        if not line.strip():
            flush(); continue
        para.append(line.strip())
    flush()
    return '\n'.join(out)


cards = []
for d in sorted(os.listdir(os.path.join(ROOT, 'puzzles')), reverse=True):
    pd = os.path.join(ROOT, 'puzzles', d)
    if not os.path.isfile(os.path.join(pd, 'puzzle.json')):
        continue
    P = json.load(open(os.path.join(pd, 'puzzle.json')))
    rules = md(open(os.path.join(pd, 'rules.md')).read().split('Play:')[0])
    note = md(open(os.path.join(pd, 'note.md')).read())
    stars = '★' * P['difficulty'] + '☆' * (5 - P['difficulty'])
    cards.append(f'''
<article class="card" id="{d}">
  <div class="img"><a href="puzzles/{d}/grid.svg"><img src="puzzles/{d}/grid.svg" alt="{html.escape(P['title'])} grid"></a></div>
  <div class="txt">
    <h2>#{d.split('-')[0]} — {html.escape(P['title'])}</h2>
    <p class="meta">Difficulty <span class="stars" title="{P['difficulty']}/5">{stars}</span> {P['difficulty']}/5 · by {html.escape(P.get('author',''))}</p>
    <p class="play"><a class="btn" href="{P['links']['sudokupad']}">Play on SudokuPad</a>
       <a class="btn alt" href="{P['links']['fpuzzles']}">f-puzzles</a></p>
    <h3>Rules</h3>{rules}
    <details><summary>Setter's note</summary>{note}</details>
    <p class="files"><a href="puzzles/{d}/verification.md">verification report</a> ·
       <a href="puzzles/{d}/puzzle.json">puzzle data</a> ·
       <a href="puzzles/{d}/solution.svg">solution (spoiler)</a></p>
  </div>
</article>''')

page = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Variant Sudoku — experimental setter</title>
<style>
body{{font-family:Georgia,serif;max-width:1050px;margin:0 auto;padding:1.5rem;background:#faf8f3;color:#222}}
header h1{{margin-bottom:.2rem}} header p{{margin-top:.2rem;color:#555}}
.card{{display:flex;gap:1.5rem;background:#fff;border:1px solid #ddd;border-radius:10px;padding:1.2rem;margin:1.5rem 0;flex-wrap:wrap}}
.img{{flex:0 0 340px}} .img img{{width:340px;height:auto;border:1px solid #eee}}
.txt{{flex:1 1 380px}} h2{{margin:.1rem 0 .3rem}} h3{{margin:.8rem 0 .2rem;font-size:1rem}}
.meta{{color:#666;margin:.2rem 0}} .stars{{color:#c58b00;letter-spacing:2px}}
.btn{{display:inline-block;background:#3b5ba5;color:#fff;padding:.35rem .8rem;border-radius:6px;text-decoration:none;font-family:sans-serif;font-size:.9rem}}
.btn.alt{{background:#777}} pre{{background:#f3f1ea;padding:.4rem .8rem;display:inline-block}}
details{{margin-top:.6rem}} summary{{cursor:pointer;font-weight:bold}} .files{{font-size:.9rem;color:#666}}
footer{{color:#777;font-size:.9rem;margin-top:2rem}}
</style></head><body>
<header><h1>Variant Sudoku</h1>
<p>Puzzles by an experimental setter. Every puzzle has a solver-confirmed unique solution; see each verification report for details.
Newest first. Full history, including abandoned ideas: <a href="{LOG_URL}">setter's log</a>.</p></header>
{''.join(cards)}
<footer>Toolkit and sources: <a href="https://github.com/meraw/variantsudoku">github.com/meraw/variantsudoku</a> ·
<a href="{LOG_URL}">SETTER_LOG.md</a></footer>
</body></html>
'''
open(os.path.join(ROOT, 'index.html'), 'w').write(page)
print('index.html written with', len(cards), 'puzzles')
