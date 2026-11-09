#!/usr/bin/env python3
"""One report of every house-rule check before a draft (review row D1, Oct 2026).

Usage (from the parasha folder):
    python3 scripts/check_book.py [data/model_final5.json] [build/rep.json]

Text checks run on the model, front matter and foot strip. Layout checks run on
the layout report written by make_pdf.py, when it exists. Each check prints its
hits; the summary at the end counts them. A hit is something to read, not
always an error: real problems become review rows (translation) or are fixed
(markup, layout).
"""
import json, re, sys, os, subprocess, collections, unicodedata as ud

SHARED = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # shared/: scripts, lib, fonts for every parasha
ROOT = os.environ.get('PARASHA_ROOT') or os.getcwd()                   # the parasha's own folder (data/, build/, parasha.json)
MODEL = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'data/model_final5.json')
REP = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'build/rep.json')
M = json.load(open(MODEL, encoding='utf-8'))
FRONT = json.load(open(os.path.join(ROOT, 'data/front.json'), encoding='utf-8'))
FOOT = json.load(open(os.path.join(ROOT, 'data/foot_terms.json'), encoding='utf-8'))

KNOWN_TAGS = {'i', 'b', 'h', 'hb', 'hi', 'sc', 'sci', 's', 'k', 'w', 'g', 'lem', 'v'}
HEB = re.compile(r'[א-ת]')
plain = lambda t: re.sub(r'\{/?[a-z]+\}', '', t)

def blocks():
    """Yield (where, field, text) for every English-bearing text in the book."""
    for v in M['verses']:
        yield f"verse {v['ch']}:{v['v']}", 'verse-en', v.get('en') or ''
    for sec in ('ec', 'notes'):
        for b in M[sec]:
            if 'text' in b:
                yield f"{sec} {b.get('ch')}:{b.get('v')}", sec, b['text']
    fr = FRONT if isinstance(FRONT, list) else [(k, x) for k in FRONT for x in FRONT[k]]
    for i, f in enumerate(fr):
        part, f = f if isinstance(f, tuple) else ('front', f)
        if isinstance(f, dict) and 'html' in f:
            yield f'{part} matter page {i+1}', 'front', re.sub(r'<[^>]+>', ' ', f['html'])
    for f in FOOT:
        yield f"foot strip '{f['label']}'", 'foot', re.sub(r'<[^>]+>', '', f['gloss'])

R = collections.OrderedDict()
def hit(check, where, text):
    R.setdefault(check, []).append((where, text))

def ctx(t, m, a=70, b=70):
    return plain(t[max(0, m.start()-a):m.end()+b]).replace('\n', ' ')

# 1. Markup: unknown or unbalanced tags
for where, field, t in blocks():
    if field in ('front', 'foot'):
        continue
    tags = re.findall(r'\{(/?)([a-z]+)\}', t)
    cnt = collections.Counter()
    for close, tag in tags:
        if tag not in KNOWN_TAGS:
            hit('markup: unknown tag', where, '{' + close + tag + '}')
        cnt[tag] += -1 if close else 1
    for tag, n in cnt.items():
        if n:
            hit('markup: unbalanced tag', where, f'{{{tag}}} off by {n}')

# 2. Hashem: English renderings that should be Hashem
for where, field, t in blocks():
    p = plain(t)
    for m in re.finditer(r'\bthe Name\b|\bthe LORD\b|\bthe Lord\b|\bLORD\b', p):
        s = p[max(0, m.start()-60):m.end()+40]
        if re.search(r'four-letter Name|Honored|Awesome|letter of the Name', s):
            continue
        hit('Hashem: "the Name"/"Lord" in English', where, s)
    for m in re.finditer(r'.{0,12}ashem', t, re.I):
        if not re.search(r'H(\{/?i\})?\{sci?\}ashem', m.group(0)) and field != 'front':
            hit('Hashem: not in small caps', where, plain(t[max(0, m.start()-30):m.end()+30]))
# verse band: every verse with the Tetragrammaton has Hashem in the English
for v in M['verses']:
    cons = ''.join(c for c in ud.normalize('NFD', v['he']) if 'א' <= c <= 'ת')
    if 'יהוה' in cons and 'ashem' not in (v.get('en') or ''):
        hit('Hashem: verse has the Name but the English lacks Hashem', f"verse {v['ch']}:{v['v']}", v.get('en'))

# 3. Letter names written out in English (should be the Hebrew letter)
LETTERS = r'alef|aleph|bet|beth|gimel|dalet|daleth|heh|vav|waw|zayin|chet|het|heth|tet|teth|yod|yud|kaf|khaf|lamed|mem|nun|samekh|samech|ayin|tsadi|tzadi|tsade|kof|qof|resh|shin|sin|tav|taw'
for where, field, t in blocks():
    if field == 'verse-en':
        continue
    p = plain(t)
    for m in re.finditer(r'\b(the letter |letter )?(' + LETTERS + r')\b', p, re.I):
        w = m.group(2).lower()
        if w in ('sin', 'mem', 'nun', 'het', 'tet', 'bet') and not m.group(1):
            # ordinary English words or likely false hits: report only with "letter"
            if w in ('sin',) or not re.search(r'\b(letter|the ' + w + r' of)\b', p[max(0, m.start()-12):m.end()+8], re.I):
                continue
        hit('letters: name written out (use the Hebrew letter)', where, ctx(p, m))

# 4. Vowel names without their sign on an alef
VOWELS = r'kamatz|qamats|patach|patah|tzere|tsere|segol|sheva|shva|holam|cholam|hirik|chirik|shuruk|kubutz|qubbuts'
for where, field, t in blocks():
    if field == 'verse-en':
        continue
    p = plain(t)
    for m in re.finditer(r'\b(' + VOWELS + r')\b', p, re.I):
        after = p[m.end():m.end()+30]
        # the sign follows: "kamatz (אָ)", "kamatz gadol (אָ)", "small patach (segol, אֶ)", "tzere (אֵ{/v})"
        if re.match(r'\s*(gadol|katan)?\s*\([^)]{0,12}[\u05d0-\u05ea][\u0591-\u05c7]', after):
            continue
        # or the vowel word is itself inside a parenthesis that gives the sign: "(segol, אֶ)"
        if re.match(r',\s*[\u05d0-\u05ea][\u0591-\u05c7]', after):
            continue
        hit('vowels: name without its sign (אָ)', where, ctx(p, m))

# 5. Characters that must not appear
for where, field, t in blocks():
    for ch, name in (('�', 'replacement char U+FFFD'), ('◌', 'dotted circle ◌'), ('​', 'zero-width space')):
        if ch in t:
            hit('characters: ' + name, where, plain(t)[:80])

# 6. Typing slips: doubled words, spaces, punctuation, brackets, straight quotes
for where, field, t in blocks():
    p = plain(t)
    for m in re.finditer(r'\b([A-Za-z]+) \1\b', p):
        if m.group(1).lower() not in ('that', 'had', 'is', 'ha'):
            hit('typing: doubled word', where, ctx(p, m, 40, 40))
    if field not in ('front', 'foot'):
        for m in re.finditer(r'  +', p):
            hit('typing: double space', where, ctx(p, m, 30, 30))
    for m in re.finditer(r' [,.;:)](?!\))', p):
        if not HEB.search(p[max(0, m.start()-2):m.start()]):
            hit('typing: space before punctuation', where, ctx(p, m, 30, 20))
    if field not in ('front', 'verse-en'):
        for o, c in ('()', '[]', '“”'):
            if p.count(o) != p.count(c):
                hit(f'typing: unbalanced {o}{c}', where, f'{p.count(o)} {o} vs {p.count(c)} {c}')
    if field not in ('front', 'foot'):
        for m in re.finditer(r'(?<![֑-ת\w])"|(?<=[a-z])"', p):
            if not HEB.search(p[max(0, m.start()-3):m.end()+3]):
                hit('typing: straight double quote', where, ctx(p, m, 30, 30))

# 7. Notes: empty labels or empty notes
for b in M['notes']:
    if 'text' not in b:
        continue
    t = b['text']
    if re.search(r'\{i\}Text\.\{/i\}\s*($|\{i\}Text)', t):
        hit('notes: empty "Text." label', f"notes {b['ch']}:{b['v']}", plain(t)[-80:])
    if len(plain(t).strip()) < 25:
        hit('notes: very short note', f"notes {b['ch']}:{b['v']}", plain(t))
    for m in re.finditer(r'agrees? with Sefaria', t):
        hit('notes: "agrees with Sefaria" (David: remove)', f"notes {b['ch']}:{b['v']}", ctx(t, m))
for b in M['ec']:
    if b.get('kind') == 'src':
        hit('English: per-section Sefaria source line (David: remove)', f"ec {b['ch']}:{b['v']}", b['text'][:80])

# 8. Verse references: corrections inside the round brackets
for sec in ('hc', 'ec', 'notes'):
    for b in M[sec]:
        t = b.get('text', '')
        # a printed reference is "(book chapter verse)"; its correction belongs inside: (תהלים קמח ה [קמח ח])
        for m in re.finditer(r'\(([^()]{3,30})\)\s*\[([^\]]{1,12})\]', t):
            inner, br = m.group(1), m.group(2)
            if len(inner.split()) < 2 or not re.fullmatch(r"[\u05d0-\u05ea'\"״׳ ]+", br) or re.search(r'[\u0591-\u05c7]', br):
                continue  # a misprint "(printed) [pointed correction]" or something else
            seg = m.group(0)
            if HEB.search(seg):
                hit('references: [correction] outside the round brackets', f"{sec} {b.get('ch')}:{b.get('v')}", plain(seg))

# 9. Glosses on words Ibn Ezra defines himself (rule from Noach on; Bereshit: David decided A3)
for b in M['ec']:
    t = b.get('text', '')
    for m in re.finditer(r'\{w\}([^{]+)\{g\}([^{]+)\{/g\}\{/w\}\s+(is|means|are called|is called)\b', t):
        hit('glosses: word Ibn Ezra defines has a gloss (check)', f"ec {b['ch']}:{b['v']}", f'{m.group(1)} ({m.group(2)}) {m.group(3)}')

# 10. Verse band: square brackets balanced, Hashem small caps
for v in M['verses']:
    en = v.get('en') or ''
    if en.count('[') != en.count(']'):
        hit('verse band: unbalanced [ ]', f"verse {v['ch']}:{v['v']}", en)

# 11. Spelling of grammar terms: one form only
FORMS = {'pi’el': r"pi[’']el|pi\-el|piel", 'hif’il': r"hif[’']il|hiphil|hifil", 'nif’al': r"nif[’']al|niphal|nifal",
         'hitpa’el': r"hitpa[’']el|hithpael", 'mappik': r'mappik|mappiq', 'dagesh': r'dagesh|daghesh',
         'kamatz': r'kamatz|qamats|qamaṣ|kamats', 'patach': r'patach|pataḥ|patah\b', 'tzere': r'tzere|tsere|ṣere'}
for name, rx in FORMS.items():
    seen = collections.Counter()
    for where, field, t in blocks():
        for m in re.finditer(rx, plain(t), re.I):
            seen[m.group(0).lower()] += 1
    if len(seen) > 1:
        hit('terms: spelled more than one way', name, dict(seen))

# 12. Grammar terms against the sheet (scripts/terms_audit.py)
try:
    out = subprocess.run([sys.executable, os.path.join(SHARED, 'scripts/terms_audit.py')], cwd=ROOT,
                         capture_output=True, text=True, timeout=300).stdout
    tail = out.split('term/verse places with no matching English')
    if len(tail) > 1:
        for line in tail[1].strip().splitlines():
            hit('terms audit: Hebrew term with no matching English (read; many are false hits)', '', line)
except Exception as ex:
    hit('terms audit: could not run', '', str(ex))

# 13. Layout report
if os.path.exists(REP):
    rep = json.load(open(REP, encoding='utf-8'))
    for line in rep.get('log', []):
        if 'WARN' in line:
            hit('layout: warning', '', line)
    pages = rep.get('report', [])
    last = pages[-1]['page'] if pages else None
    for p in pages:
        if p.get('empty', 0) > 85 and p['page'] != last:
            hit('layout: page ends with empty space (px)', f"page {p['page']}", p['empty'])
    if pages:
        hit('layout: last page empty space (px)', f"page {last}", pages[-1].get('empty'))
else:
    hit('layout: no report yet (build first)', '', REP)

# Report
total = 0
for check, hits in R.items():
    print(f'\n== {check}: {len(hits)}')
    for where, text in hits[:60]:
        print(f'   {where}: {text}')
    if len(hits) > 60:
        print(f'   … {len(hits)-60} more')
    total += len(hits)
print('\nSUMMARY')
for check, hits in R.items():
    print(f'  {len(hits):4d}  {check}')
print(f'  {total:4d}  total')
