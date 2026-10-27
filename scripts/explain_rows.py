#!/usr/bin/env python3
"""Material for explaining review rows, from the repo only (no Google call).

Usage (repo top):
  python3 -I scripts/explain_rows.py <review> C3 E2        # these rows
  python3 -I scripts/explain_rows.py <review> --discuss     # every Discuss row (also --change, --open, --noted)
<review>: part of a title, a parasha, a rows-file path or a doc id, as in review_docs.json
(an open doc is preferred when several match).

For each row it prints the doc link, Where, Issue, Now, Alternative, the Explanations-tab text
("as it stands" / "if changed"), the Sefaria link, and David's answer from answers.json
(written by read_answers() in scripts/workbench/wb.py; run it first if the answers may be stale),
and any answer David gave in chat (chat_answers.json next to the rows file: {id: {decision, note, date}}).
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find(key):
    reg = json.load(open(os.path.join(ROOT, 'review_docs.json'), encoding='utf-8'))['docs']
    k = key.lower()
    hits = [d for d in reg if d.get('rows_file') and (d.get('id') == key or k in (d.get('title') or '').lower()
            or k in (d.get('parasha') or '').lower() or k in d['rows_file'].lower())]
    hits = [d for d in hits if d.get('status') == 'open'] or hits
    if len(hits) != 1:
        sys.exit(f'"{key}" matches {len(hits)} reviews: ' + '; '.join(d.get('title') or '?' for d in hits))
    return hits[0]


def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    flags = {x for x in sys.argv[1:] if x.startswith('--')}
    if not a:
        sys.exit(__doc__)
    meta = find(a[0])
    rf = meta['rows_file']
    rows = json.load(open(os.path.join(ROOT, rf), encoding='utf-8'))
    rows = rows if isinstance(rows, list) else rows.get('rows', [])
    ap = os.path.join(ROOT, rf.replace('rows.json', 'answers.json'))
    ans = {r['id']: r for r in json.load(open(ap, encoding='utf-8'))['rows']} if os.path.exists(ap) else {}
    read_at = json.load(open(ap, encoding='utf-8')).get('read_at') if ans else None
    cp = os.path.join(ROOT, rf.replace('rows.json', 'chat_answers.json'))
    chat = json.load(open(cp, encoding='utf-8')) if os.path.exists(cp) else {}
    cfgp = [os.path.join(ROOT, os.path.dirname(rf), n) for n in ('doc_cfg.json', os.path.basename(rf).replace('rows.json', 'doc_cfg.json'))]
    heads = {}
    for c in cfgp:
        if os.path.exists(c):
            for part in json.load(open(c, encoding='utf-8')).get('parts', []):
                heads[part[0]] = (part[1], [h for h in part[3] if h not in ('ID', 'Sefaria', 'Decision', 'Your note', 'Explanation')])
            break
    want = set(a[1:])
    def chosen(r):
        d = ans.get(r['id'], {})
        dec, note = d.get('decision', 'Unanswered'), d.get('note', '')
        return (r['id'] in want or ('--discuss' in flags and dec == 'Discuss') or ('--change' in flags and dec == 'Change')
                or ('--open' in flags and dec == 'Unanswered' and not note) or ('--noted' in flags and note))
    sel = [r for r in rows if chosen(r)]
    print(f"{meta.get('title')}\nhttps://docs.google.com/document/d/{meta['id']}/edit")
    print(f"answers read {read_at}" if read_at else 'no answers.json yet: run read_answers() in the workbench')
    missing = want - {r['id'] for r in rows}
    if missing:
        print('not in the rows file: ' + ', '.join(sorted(missing)))
    for r in sel:
        part = r.get('part', r['id'][0])
        title, hh = heads.get(part, ('', ['Where', 'Issue', 'Now', 'Alternative']))
        d = ans.get(r['id'], {})
        print(f"\n=== {r['id']}  {title}")
        for h, c in zip(hh, r.get('cells', [])):
            print(f"{h}: {c}")
        print(f"Answer: {d.get('decision', 'Unanswered')}" + (f" | note: {d['note']}" if d.get('note') else ''))
        if r['id'] in chat:
            c = chat[r['id']]
            print(f"Answered in chat ({c.get('date')}): {c.get('decision')}" + (f" | {c['note']}" if c.get('note') else ''))
        if r.get('plain'):
            print('Explanation: ' + r['plain'].split('\n', 1)[-1])
        for k in ('stands', 'changed'):
            if r.get(k):
                print(('As it stands: ' if k == 'stands' else 'If changed: ') + r[k])
        if r.get('url'):
            print('Sefaria: ' + r['url'])
    print(f'\n{len(sel)} row(s)')


if __name__ == '__main__':
    main()
