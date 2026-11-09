"""Every sentence a review row adds on the strength of a source is backed by the source itself (David, 9 Nov 2026).

    python3 -I scripts/cite_check.py               # check every open idea row (CI runs this)
    python3 -I scripts/cite_check.py --show ideas_vay:B2   # print a row's sentence and its source passages

review_audit/sources/library.json holds each source as read on Sefaria; review_audit/citations.json holds, for each
idea row, the sentence as it was checked, the passages it rests on (word ranges in the library) and the verdict of the
check (supported / partly / not supported, with the problems). A row fails here when:
  - it adds a sentence and has no citation (the sentence was never checked against its source);
  - its sentence has changed since it was checked (check it again);
  - a passage points outside its source, or a source is missing from the library;
  - the verdict is not "supported" and there is no accepted note saying why it may stand
    (Claude's own reasoning marked "it seems", the "what a reader would think" clause, background David asked for).
Idea rows: every row of an Ideas Audit (ideas_*), and Part F of a parasha's review list.
How a citation is made: skill ibn-ezra-idea-notes / commentary-ideas-audit, "Check every sentence against its source".
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = json.load(open(os.path.join(ROOT, 'review_audit', 'sources', 'library.json'), encoding='utf-8'))['sources']
CIT = json.load(open(os.path.join(ROOT, 'review_audit', 'citations.json'), encoding='utf-8'))['rows']
STRIP = lambda t: re.sub(r'\{/?[a-z]+\}', '', t)

def added(op):
    new, old = op['new'], op['old']
    if new.startswith(old): return STRIP(new[len(old):]).strip()
    if new.endswith(old): return STRIP(new[:len(new) - len(old)]).strip()
    return STRIP(new).strip()

def passage(p):
    return ' '.join(LIB[p['source']]['he'].split(' ')[p['start']:p['end'] + 1])

def hebrew(key):
    """The source Hebrew a row rests on, for its Alternative box (make_rows)."""
    c = CIT.get(key)
    return ' … '.join(passage(p) for p in c['passages']) if c and c.get('passages') else ''

def idea_rows():
    reg = json.load(open(os.path.join(ROOT, 'review_docs.json'), encoding='utf-8'))['docs']
    for d in reg:
        if d.get('status') != 'open' or not d.get('rows_file'): continue
        key = os.path.basename(d['rows_file']).replace('_rows.json', '')
        rows = json.load(open(os.path.join(ROOT, d['rows_file']), encoding='utf-8'))
        for r in rows:
            if (key.startswith('ideas_') or r.get('part') == 'F') and r.get('ops'):
                yield key, r

def check():
    bad = []
    for key, r in idea_rows():
        k = f"{key}:{r['id']}"; c = CIT.get(k); sent = added(r['ops'][0])
        if not c: bad.append(f'{k}: no citation — check the sentence against its source'); continue
        if re.sub(r'\s+', ' ', c['sentence']) != re.sub(r'\s+', ' ', sent): bad.append(f'{k}: the sentence changed since it was checked — check it again'); continue
        for p in c.get('passages', []):
            if p['source'] not in LIB: bad.append(f"{k}: {p['source']} is not in the library")
            elif not (0 <= p['start'] <= p['end'] < len(LIB[p['source']]['he'].split(' '))): bad.append(f"{k}: passage {p['start']}–{p['end']} is outside {p['source']}")
        if c.get('verdict') != 'supported' and not c.get('accepted'):
            bad.append(f"{k}: {c.get('verdict')} — {c.get('problems')}")
    return bad

if __name__ == '__main__':
    if sys.argv[1:2] == ['--show']:
        c = CIT[sys.argv[2]]
        print(c['sentence'], '\n', c['verdict'], c['problems'], c['accepted'])
        for p in c['passages']: print(f"\n[{p['source']} {p['start']}–{p['end']}]\n{passage(p)}")
        sys.exit(0)
    bad = check()
    n = sum(1 for _ in idea_rows())
    print('\n'.join(bad) or f'citations: all {n} open idea rows checked against their sources')
    sys.exit(1 if bad else 0)
