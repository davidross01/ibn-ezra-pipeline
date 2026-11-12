# A verse quoted in a note gives its Hebrew before the English (notes.md, rule 17; Ruling 110, 12 Nov 2026).
# Finds an English quotation “…” followed by a verse reference, e.g. “Take, I pray, your son” (22:2), with no Hebrew
# ({h} or {hb}) just before it. A place that stands in an open review list (review_docs.json, status open or
# answered) is waiting for David and is not counted.
#   python3 -I scripts/quote_hebrew.py [parasha]
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = {'bereshit': 'bereshit/data/model_final5.json'}
PAT = re.compile(r'“([^”]{2,160})”\s*\((?:(?:I{1,2} )?[A-Z][a-z]+(?: of Songs)? )?\d+:\d+[^)]*\)')


def places(folder, M=None):
    M = M or json.load(open(os.path.join(ROOT, MODEL.get(folder, f'{folder}/data/model.json')), encoding='utf-8'))
    out = []
    for b in M['notes']:
        t = b.get('text') or ''
        for m in PAT.finditer(t):
            before = t[max(0, m.start() - 40):m.start()]
            if '{/h}' in before or '{/hb}' in before:
                continue
            out.append((b['ch'], b['v'], m.group(0)))
    return out


def waiting():
    d = json.load(open(os.path.join(ROOT, 'review_docs.json'), encoding='utf-8'))
    t = []
    for x in d['docs']:
        if x.get('status') in ('open', 'answered') and x.get('rows_file') and os.path.exists(os.path.join(ROOT, x['rows_file'])):
            t.append(open(os.path.join(ROOT, x['rows_file']), encoding='utf-8').read().replace('\\"', '"'))
    return '\n'.join(t)


def missing(folder, M=None, _w={}):
    if 'w' not in _w:
        _w['w'] = waiting()
    return [p for p in places(folder, M) if p[2] not in _w['w']]


if __name__ == '__main__':
    fs = sys.argv[1:] or ['bereshit', 'noach', 'lech_lecha', 'vayera', 'chayei_sarah', 'toledot']
    n = 0
    for f in fs:
        for c, v, q in missing(f):
            print(f, f'{c}:{v}', q); n += 1
    print(n, 'quotations without their Hebrew')
