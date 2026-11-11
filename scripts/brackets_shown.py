# Every bracket is shown to David as a review row (review.md, rule 24; Ruling 109, 11 Nov 2026): each (printed)
# [correction] in Ibn Ezra's Hebrew and each [added word] in the verse band's English must stand in a review list
# (review_audit/*_rows.json, <parasha>/review/*rows*.json, the archived lists). A bracket a held change removes
# (book.json "held" "edits") is not counted.
#   python3 -I scripts/brackets_shown.py [parasha]      lists the brackets not yet shown
import glob, json, os, re, sys, unicodedata as ud
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = {'bereshit': 'bereshit/data/model_final5.json'}
HEB = re.compile('[א-ת]')
VOW = re.compile('[֑-ׇ]')


def bare(s):
    return VOW.sub('', ud.normalize('NFD', s))


def reviewed_text(skip=()):
    t = []
    for f in (glob.glob(os.path.join(ROOT, 'review_audit', '*_rows.json')) + glob.glob(os.path.join(ROOT, '*', 'review', '*rows*.json'))
              + glob.glob(os.path.join(ROOT, '*', 'review', 'archive', '*.txt')) + glob.glob(os.path.join(ROOT, 'review_audit', 'archive', '**', '*'), recursive=True)):
        if os.path.isfile(f) and not any(os.path.basename(f).startswith(s) for s in skip):
            try:
                t.append(open(f, encoding='utf-8').read())
            except Exception:
                pass
    t = '\n'.join(t).replace('\\"', '"')
    return t, bare(t)


def held_olds():
    b = json.load(open(os.path.join(ROOT, 'book.json'), encoding='utf-8'))
    return [e[2] for h in b.get('held', []) for e in h.get('edits', [])]


def brackets(folder, M=None):
    """(kind, ch, v, text, key): every Hebrew correction and every verse-band bracket of the parasha."""
    M = M or json.load(open(os.path.join(ROOT, MODEL.get(folder, f'{folder}/data/model.json')), encoding='utf-8'))
    out = []
    for b in M['hc']:
        for m in re.finditer(r'\(([^()\[\]{}]{1,40})\)\s*\[([^\]]{1,40})\]', b.get('text') or ''):
            if HEB.search(m.group(1)) and VOW.search(m.group(2)):          # a misprint, not a reference
                out.append(('Hebrew', b['ch'], b['v'], m.group(0), m.group(2)))
    for b in M.get('verses', []):
        for m in re.finditer(r'\[[^\]]{1,80}\]', b.get('en') or ''):
            out.append(('verse', b['ch'], b['v'], m.group(0), m.group(0)))
    return out


def not_shown(folder, M=None, skip=(), _cache={}):
    if _cache.get('skip') != skip or 'r' not in _cache:
        _cache['r'] = reviewed_text(skip); _cache['h'] = held_olds(); _cache['skip'] = skip
    t, tb = _cache['r']
    res = []
    for kind, c, v, s, key in brackets(folder, M):
        if any(s in o for o in _cache['h']):
            continue
        if kind == 'Hebrew':
            if key in t or bare(key) in tb:
                continue
        elif f'{c}:{v}' in t and key in t:
            continue
        res.append((kind, c, v, s))
    return res


if __name__ == '__main__':
    fs = sys.argv[1:] or ['bereshit', 'noach', 'lech_lecha', 'vayera', 'chayei_sarah', 'toledot']
    n = 0
    for f in fs:
        for x in not_shown(f):
            print(f, *x); n += 1
    print(n, 'brackets not yet shown in a review list')
