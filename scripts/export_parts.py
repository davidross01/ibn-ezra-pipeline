# Export a finished parasha's five parts to separate files, and rebuild the book-wide set.
#
#   python3 scripts/export_parts.py            (every parasha marked final in book.json)
#
# For each final parasha: <folder>/export/ gets
#   chumash_hebrew, chumash_english, ibn_ezra_hebrew, ibn_ezra_english, notes
# each as .txt (plain text, readable) and .json (one entry per piece, with its verse, the plain
# text and the book's own markup, so italics, small caps, lemmas and references are kept).
# The top-level export/ folder gets the same five parts for the whole book so far (all final
# parashot, in order). David asked for this in Oct 2026: run it only when a parasha is final.
import json, os, re, sys, unicodedata as ud

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK = json.load(open(f'{ROOT}/book.json', encoding='utf-8'))
MODEL = {'bereshit': 'data/model_final5.json'}   # parashot whose final model is not data/model.json
PARTS = [('chumash_hebrew', 'Chumash (Hebrew)'), ('chumash_english', 'Chumash (translation)'),
         ('ibn_ezra_hebrew', 'Ibn Ezra (Hebrew)'), ('ibn_ezra_english', 'Ibn Ezra (translation)'),
         ('notes', 'Notes')]

def plain(t):
    t = ud.normalize('NFC', t)
    t = re.sub(r'\{w\}(.*?)\{g\}(.*?)\{/g\}\{/w\}', r'\1 (\2)', t)   # Hebrew word with its gloss
    t = re.sub(r'\{/?[a-z]+\}', '', t)
    return re.sub(r'[ \t]+', ' ', t).strip()

def strip_te(t):   # verse text without cantillation (te'amim) and meteg, for searching
    return re.sub('[֑-ֽ֯]', '', ud.normalize('NFC', t))

def export(par):
    folder = par['folder']
    M = json.load(open(f"{ROOT}/{folder}/{MODEL.get(folder, 'data/model.json')}", encoding='utf-8'))
    al = M.get('aliyot', {})
    alk = (lambda ch, v: al.get(f'{ch}:{v}')) if isinstance(al, dict) else (lambda ch, v: None)
    if isinstance(al, list):   # Noach style: list of {ch, v, name}
        d = {(int(a['ch']), int(a['v'])): a.get('name') or a.get('he') for a in al}
        alk = lambda ch, v: d.get((int(ch), int(v)))
    out = {k: [] for k, _ in PARTS}
    for V in M['verses']:
        ch, v = int(V['ch']), int(V['v'])
        base = {'parasha': par['parasha'], 'ref': f'{ch}:{v}', 'ch': ch, 'v': v}
        extra = {'section_mark': V.get('brk'), 'aliyah': V.get('aliyah') or alk(ch, v)}
        out['chumash_hebrew'].append({**base, 'text': ud.normalize('NFC', V['he']),
                                      'text_no_cantillation': strip_te(V['he']), **extra})
        out['chumash_english'].append({**base, 'text': plain(V['en']), 'markup': V['en'], **extra})
    for P in M['hc']:
        ch, v = int(P['ch']), int(P['v'])
        out['ibn_ezra_hebrew'].append({'parasha': par['parasha'], 'ref': f'{ch}:{v}', 'ch': ch, 'v': v,
                                       'text': plain(P['text']), 'markup': P['text']})
    for key, src in (('ibn_ezra_english', 'ec'), ('notes', 'notes')):
        n = {}
        for P in M[src]:
            if P.get('kind') != 'p': continue
            ch, v = int(P['ch']), int(P['v'])
            n[(ch, v)] = n.get((ch, v), 0) + 1
            out[key].append({'parasha': par['parasha'], 'ref': f'{ch}:{v}', 'ch': ch, 'v': v,
                             'part': n[(ch, v)], 'text': plain(P['text']), 'markup': P['text']})
    return out

def write(dirpath, title, out, pages=None):
    os.makedirs(dirpath, exist_ok=True)
    for key, name in PARTS:
        items = out[key]
        json.dump(items, open(f'{dirpath}/{key}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        lines = [f'{title} — {name}', '']
        chap = par_ = None
        for it in items:
            if it['parasha'] != par_:
                par_ = it['parasha']; chap = None
                if title.startswith('Ibn Ezra on the Torah'): lines += [f'=== Parashat {par_} ===', '']
            if it['ch'] != chap:
                chap = it['ch']; lines += [f'— Chapter {chap} —', '']
            tag = it['ref'] + (f" [{it['aliyah']}]" if it.get('aliyah') else '')
            lines.append(f"{tag}  {it['text']}" + (f"  {it['section_mark']}" if it.get('section_mark') else ''))
            lines.append('')
        open(f'{dirpath}/{key}.txt', 'w', encoding='utf-8').write('\n'.join(lines))
    readme = [f'# {title} — the five parts as separate files', '',
              'Made by scripts/export_parts.py from the final book data. Each part comes as:',
              '- .txt — plain text, one entry per verse (or per comment / note), headed by its verse (e.g. 1:1);',
              '- .json — the same entries with ref, ch, v, the plain text and "markup" (the book\'s own markup:',
              '  {i} italics, {sc} small caps, {h} Hebrew, {hb} lemma, {s} reference, {w}…{g}gloss{/g}{/w}, {k} key word, {v} vowel sign).',
              '  The Chumash files also give section_mark (פ/ס) and aliyah; the Hebrew verses also come without cantillation.',
              '  Comments and notes carry "part" (1, 2, … for several on one verse, in book order).', '',
              '| File | Entries |', '|---|---|']
    readme += [f'| {k} | {len(out[k])} |' for k, _ in PARTS]
    if pages: readme += ['', f'Book pages: {pages}.']
    open(f'{dirpath}/README.md', 'w', encoding='utf-8').write('\n'.join(readme) + '\n')

final = [p for p in BOOK['parashot'] if str(p.get('status', '')).startswith('final')]
if not final: sys.exit('no parasha is marked final in book.json')
book = {k: [] for k, _ in PARTS}
for p in final:
    o = export(p)
    write(f"{ROOT}/{p['folder']}/export", f"Ibn Ezra on Parashat {p['parasha']}", o, f"{p['first_page']}–{p['last_page']}")
    for k in book: book[k] += o[k]
    print(p['parasha'], {k: len(v) for k, v in o.items()})
write(f'{ROOT}/export', 'Ibn Ezra on the Torah', book,
      ', '.join(f"{p['parasha']} {p['first_page']}–{p['last_page']}" for p in final))
print('book-wide:', {k: len(v) for k, v in book.items()})
