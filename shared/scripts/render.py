# Render the book model to one HTML file. The JS planner (scripts/layout.js) paginates it in Chromium.
import json, re, sys, os, html, unicodedata as ud
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'))   # shared/lib
import pyphen

import os
SHARED = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # shared/: scripts, lib, fonts for every parasha
ROOT = os.environ.get('PARASHA_ROOT') or os.getcwd()                   # the parasha's own folder (data/, build/, parasha.json)
MODEL = sys.argv[1] if len(sys.argv) > 1 else f'{ROOT}/data/model_final.json'
FRONT = f'{ROOT}/data/front.json'
OUT = sys.argv[2] if len(sys.argv) > 2 else f'{ROOT}/build/book.html'

M = json.load(open(MODEL, encoding='utf-8'))
HY = pyphen.Pyphen(lang='en_US', left=2, right=3)

HEBNUM = {1: 'א', 2: 'ב', 3: 'ג', 4: 'ד', 5: 'ה', 6: 'ו', 7: 'ז', 8: 'ח', 9: 'ט', 10: 'י', 20: 'כ', 30: 'ל', 40: 'מ', 50: 'נ', 60: 'ס'}
def heb(n):
    if n == 15: return 'טו'
    if n == 16: return 'טז'
    out = ''
    for v in (60, 50, 40, 30, 20, 10):   # 50 and 60 added for Chayei Sarah (24:50-67)
        if n >= v: out += HEBNUM[v]; n -= v; break
    if n: out += HEBNUM[n]
    return out

# ---------- inline markup -> HTML
def hyphenate_text(s):
    def rep(m):
        w = m.group(0)
        if len(w) < 6: return w
        return HY.inserted(w, hyphen='­')
    return re.sub(r"[A-Za-z][a-z’']+", rep, s)

TAGS = {
    'i': ('<i>', '</i>'), 'b': ('<b>', '</b>'),
    'h': ('<span class="h">', '</span>'), 'hb': ('<span class="h hb">', '</span>'),
    'hi': ('<span class="h">', '</span>'),
    'sc': ('<span class="sc">', '</span>'), 'sci': ('<i class="sc">', '</i>'),
    's': ('<span class="ref">', '</span>'), 'k': ('<span class="key">', '</span>'),
    'w': ('<span class="hw"><span class="h">', '</span>'), 'g': ('</span><span class="gl">', '</span>'),
    'v': ('<span class="h vs" dir="rtl">', '</span>'),
    'hy': ('', ''), 'n': ('', ''), 'lem': ('<b class="lem">', '</b>'),
}
def md(text, lang='en', hyph=True):
    text = ud.normalize('NFC', text)
    toks = re.split(r'(\{/?[a-z]+\})', text)
    out = []; stack = []
    for t in toks:
        m = re.fullmatch(r'\{(/?)([a-z]+)\}', t)
        if m:
            close, tag = m.group(1), m.group(2)
            if tag not in TAGS: raise ValueError('unknown tag ' + tag + ' in ' + text[:80])
            if tag == 'g':
                out.append(TAGS['g'][0] if not close else TAGS['g'][1]); continue
            if tag == 'w':
                out.append(TAGS['w'][0] if not close else '</span>')
                if close: stack.pop()
                else: stack.append('w')
                continue
            out.append(TAGS[tag][1] if close else TAGS[tag][0])
            if close:
                if stack and stack[-1] == tag: stack.pop()
            else: stack.append(tag)
            continue
        s = html.escape(t, quote=False)
        in_heb = any(x in ('h', 'hb', 'hi', 'w', 's', 'lem') for x in stack) or lang == 'he'
        if hyph and not in_heb and lang == 'en': s = hyphenate_text(s)
        out.append(s)
    return ''.join(out)

# ---------- verses
verses = M['verses']
VI = {(v['ch'], v['v']): i for i, v in enumerate(verses)}
aliyot = M['aliyot']
vdata = []
for i, v in enumerate(verses):
    vdata.append({'ch': v['ch'], 'v': v['v'], 'he': html.escape(v['he']), 'en': md(v['en']),
                  'brk': v['brk'], 'aliyah': (lambda a: None if a == 'ראשון' else a)(aliyot.get(f"{v['ch']}:{v['v']}")),
                  'hv': heb(v['v']), 'hch': heb(v['ch'])})

# ---------- streams
blocks = []  # dicts: s, vi, kind, html
def add(s, vi, kind, h, cls=''):
    blocks.append({'s': s, 'vi': vi, 'kind': kind, 'html': h, 'cls': cls})

for P in M['hc']:
    vi = VI[(P['ch'], P['v'])]
    body = md(P['text'].replace('{b}', '{lem}').replace('{/b}', '{/lem}'), lang='he', hyph=False)
    add('hc', vi, 'p', f'<span class="hcn">({heb(P["v"])})</span> ' + body)

def stream(items, s):
    pending_chap = []
    last_vi = 0
    for it in items:
        if it['kind'] == 'chapter':
            if s != 'n': pending_chap.append(it['ch'])   # row E6: no chapter numbers in the notes
            continue
        if it['kind'] == 'src':
            add(s, last_vi, 'src', md(it['text'], hyph=False)); continue
        vi = VI[(it['ch'], it['v'])]
        for ch in pending_chap:
            add(s, vi, 'chap', str(ch))
        pending_chap = []
        pre = f'<b class="vn">{it["v"]}. </b>' if it['first'] else ''
        add(s, vi, 'p', pre + md(it['text']), 'first' if it['first'] else '')
        last_vi = vi
stream(M['ec'], 'ec')
stream(M['notes'], 'n')

# ---------- glossary for the foot-of-page line (F1)
GLOSS = json.load(open(f'{ROOT}/data/foot_terms.json', encoding='utf-8'))

front = json.load(open(FRONT, encoding='utf-8')) if len(sys.argv) <= 3 or sys.argv[3] != 'nofront' else {'before': [], 'after': []}
PARASHA = json.load(open(f'{ROOT}/parasha.json', encoding='utf-8'))


def edition_div():
    """"Edition of <date>" under the parasha's title (David, 10 Nov 2026, Ruling 105): the date of the last change, from book.json."""
    sys.path.insert(0, os.path.join(os.path.dirname(SHARED), 'scripts'))
    import stage
    try:
        e = stage.entry(stage.load_book(os.path.dirname(os.path.abspath(ROOT))), os.path.basename(os.path.abspath(ROOT)))
    except (StopIteration, FileNotFoundError):
        return ''
    t = stage.edition_text(e)
    return f'<div class="tp tp-note" style="top:462px">{t}</div>' if t else ''
if not PARASHA.get('volume_front_matter', True):
    front['before'] = []  # title, preface and key to terms appear once, at the start of the book
    if PARASHA.get('title_page'):   # row E1: the parasha opens with a title page of its own, like Bereshit's
        front['before'] = [{'html': f'<div class="tp ht-he" style="top:330px">{PARASHA["heading_he"]}</div>'
                                    '<div class="tp-rule" style="left:232px;width:200px;top:398px"></div>'
                                    f'<div class="tp ht-en" style="top:410px">{PARASHA["title_en"]}</div>'
                                    + edition_div()}]
def fm(h):
    # markup + hyphenation in the text between HTML tags; the HTML tags themselves pass through
    return ''.join(seg if seg.startswith('<') else md(seg) for seg in re.split(r'(<[^>]+>)', h))
for part in ('before', 'after'):
    for item in front[part]:
        item['html'] = fm(item['html'])

def font_url(p):
    return 'file://' + p.replace('[', '%5B').replace(']', '%5D')

CSS = open(f'{SHARED}/scripts/book.css', encoding='utf-8').read()
CSS = CSS.replace('@@FRL@@', font_url(f'{SHARED}/fonts/FrankRuhlLibre[wght].ttf'))
CSS = CSS.replace('@@FSB@@', font_url('/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf'))
CSS = CSS.replace('@@FSR@@', font_url('/usr/share/fonts/truetype/freefont/FreeSerif.ttf'))
CSS = CSS.replace('@@FRC@@', font_url(f'{SHARED}/fonts/FrankRuehlCLM-Bold.otf'))
TG = '/usr/share/texmf/fonts/opentype/public/tex-gyre/'
for k, f in [('@@PR@@', 'texgyrepagella-regular.otf'), ('@@PI@@', 'texgyrepagella-italic.otf'),
             ('@@PB@@', 'texgyrepagella-bold.otf'), ('@@PBI@@', 'texgyrepagella-bolditalic.otf')]:
    CSS = CSS.replace(k, font_url(TG + f))

meas = {'hc': [], 'ec': [], 'n': []}
for i, b in enumerate(blocks):
    cls = f'blk {b["s"]} k-{b["kind"]} {b["cls"]}'.strip()
    d = ' dir="rtl"' if b['s'] == 'hc' else ''
    meas[b['s']].append(f'<div class="{cls}" id="b{i}"{d}>{b["html"]}</div>')
meta = [{'s': b['s'], 'vi': b['vi'], 'kind': b['kind'], 'id': f'b{i}'} for i, b in enumerate(blocks)]

JS = open(f'{SHARED}/scripts/layout.js', encoding='utf-8').read()
doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{html.escape(PARASHA['title'])}</title>
<style>{CSS}</style></head>
<body>
<div id="measure">
  <div id="m-hc" class="col-full">{''.join(meas['hc'])}</div>
  <div id="m-ec" class="col-full">{''.join(meas['ec'])}</div>
  <div id="m-n" class="col-note">{''.join(meas['n'])}</div>
  <div id="m-band" class="col-full"></div>
  <div id="m-strip"><span class="strip" id="strip-probe"></span></div>
</div>
<div id="book"></div>
<script>
const VERSES = {json.dumps(vdata, ensure_ascii=False)};
const BLOCKS = {json.dumps(meta)};
const GLOSS = {json.dumps(GLOSS, ensure_ascii=False)};
const FRONT = {json.dumps(front, ensure_ascii=False)};
const PARASHA = {json.dumps(PARASHA, ensure_ascii=False)};
{JS}
</script>
</body></html>'''
open(OUT, 'w', encoding='utf-8').write(doc)
print('blocks', len(blocks), {k: len(v) for k, v in meas.items()}, 'verses', len(vdata))
