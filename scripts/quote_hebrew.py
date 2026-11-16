# A verse quoted in a note gives its Hebrew before the English (notes.md, rule 17; Ruling 110, 12 Nov 2026); so does
# a verse Ibn Ezra quotes in the English commentary (translation.md, rule 19; Ruling 119, 16 Nov 2026).
# Finds an English quotation “…” followed by a verse reference, e.g. “Take, I pray, your son” (22:2), with no Hebrew
# ({h} or {hb}) just before it. A place that stands in an open review list (review_docs.json, status open or
# answered) is waiting for David and is not counted.
#   python3 -I scripts/quote_hebrew.py [parasha]
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = {'bereshit': 'bereshit/data/model_final5.json'}
PAT = re.compile(r'“([^”]{2,160})”\s*\((?:(?:I{1,2} )?[A-Z][a-z]+(?: of Songs)? )?\d+:\d+[^)]*\)')
# the same with the reference in italics, {i}(3:17){/i}, or a few words between the quotation and the reference
# (“was buried in the cities of Gil’ad,” in one of them (Judges 12:7)); 16 Nov 2026
PAT2 = re.compile(r'“([^”]{2,160})”(\s*\{i\}\(|[^“”(){}]{1,40}\()((?:(?:I{1,2} )?[A-Z][a-z]+(?: of Songs)? )?\d+:\d+[^)]*)\)(\{/i\})?')


def places(folder, M=None, sec='notes'):
    M = M or json.load(open(os.path.join(ROOT, MODEL.get(folder, f'{folder}/data/model.json')), encoding='utf-8'))
    out = []
    for b in M[sec]:
        t = b.get('text') or ''
        seen = set()
        for m in list(PAT.finditer(t)) + list(PAT2.finditer(t)):
            if m.start() in seen: continue
            seen.add(m.start())
            before = t[max(0, m.start() - 40):m.start()]
            if '{/h}' in before or '{/hb}' in before or '{/w}' in before:
                continue
            if '{h}' in m.group(0):            # the Hebrew follows the English, before the reference
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


READ = [x for x in json.load(open(os.path.join(ROOT, 'scripts', 'quote_hebrew_read.json'), encoding='utf-8'))['places']]


def missing(folder, M=None, _w={}, sec='notes'):
    if 'w' not in _w:
        _w['w'] = waiting()
    out = []
    for p in places(folder, M, sec):
        if p[2] in _w['w']: continue
        if M is None: M = json.load(open(os.path.join(ROOT, MODEL.get(folder, f'{folder}/data/model.json')), encoding='utf-8'))
        t = next((b['text'] for b in M[sec] if (b.get('ch'), b.get('v')) == (p[0], p[1]) and p[2] in b.get('text', '')), '')
        i = t.find(p[2])
        ctx = t[max(0, i - 20):i + len(p[2]) + 40]
        if any(r['folder'] == folder and (r['text'] in p[2] or r['text'] in ctx) for r in READ): continue     # read: not a quotation
        out.append(p)
    return out


if __name__ == '__main__':
    fs = sys.argv[1:] or ['bereshit', 'noach', 'lech_lecha', 'vayera', 'chayei_sarah', 'toledot']
    n = 0
    for sec in ('ec', 'notes'):
        for f in fs:
            for c, v, q in missing(f, sec=sec):
                print(sec, f, f'{c}:{v}', q); n += 1
    print(n, 'quotations without their Hebrew')
