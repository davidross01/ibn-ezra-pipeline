#!/usr/bin/env python3
"""Check a review-list Google Doc: chips, links both ways, IDs against the rows file.

Usage:
  python3 -I scripts/check_review_doc.py <doc.json> [--rows <parasha>/review/listN_rows.json]

<doc.json> is the document read with includeTabsContent (the Google Docs read_doc
result saved to a file, {"content": {...}}, or a raw documents.get / Composio
GOOGLEDOCS_GET_DOCUMENT_BY_ID result). Read-only: it never edits the doc.
Prints one report and exits 1 if anything is wrong.
"""
import json, sys, argparse


def load_doc(path):
    d = json.load(open(path, encoding='utf-8'))
    for k in ('content', 'data', 'response_data'):
        if isinstance(d, dict) and k in d and isinstance(d[k], dict) and 'tabs' not in d:
            d = d[k]
    if 'tabs' not in d:
        sys.exit('no tabs in the document JSON: read it with includeTabsContent')
    return d


def ptext(p):
    return ''.join(e.get('textRun', {}).get('content', '') for e in p.get('elements', [])).strip()


def cell_info(cell):
    txt, links, chips = [], [], []
    for s in cell.get('content', []):
        p = s.get('paragraph')
        if not p:
            continue
        txt.append(ptext(p))
        for e in p.get('elements', []):
            tr = e.get('textRun')
            if tr:
                l = tr.get('textStyle', {}).get('link')
                if l:
                    links.append((tr.get('content', '').strip(), l))
            for k, v in e.items():
                if isinstance(v, dict):
                    dv = v.get('dropdownProperties', {}).get('displayValue') or v.get('displayValue')
                    if dv is not None:
                        chips.append(dv)
    return ' '.join(t for t in txt if t), links, chips


def headings(content, out):
    for s in content:
        p = s.get('paragraph')
        if p:
            hid = p.get('paragraphStyle', {}).get('headingId')
            if hid:
                out[hid] = ptext(p)
        if 'table' in s:
            for row in s['table']['tableRows']:
                for c in row['tableCells']:
                    headings(c['content'], out)
    return out


def tables(content):
    return [s['table'] for s in content if 'table' in s]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('doc')
    ap.add_argument('--rows')
    a = ap.parse_args()
    d = load_doc(a.doc)
    tabs = {t['tabProperties']['tabId']: t for t in d['tabs']}
    main_id = d['tabs'][0]['tabProperties']['tabId']
    exp = [t for t in d['tabs'] if t['tabProperties']['title'].strip().lower() == 'explanations']
    problems = []
    print('Doc:', d.get('title'), '| id', d.get('documentId'))
    if not exp:
        problems.append('no Explanations tab')
    exp_id = exp[0]['tabProperties']['tabId'] if exp else None
    H = {tid: headings(t['documentTab']['body']['content'], {}) for tid, t in tabs.items()}

    # main tab rows
    main_rows = []
    for tb in tables(tabs[main_id]['documentTab']['body']['content']):
        rows = tb['tableRows']
        head = [cell_info(c)[0].lower() for c in rows[0]['tableCells']]
        def col(name):
            return next((i for i, h in enumerate(head) if h.startswith(name)), None)
        ci, cd, cn, ce = col('id'), col('decision'), col('your note'), col('explanation')
        if ci is None:
            continue
        for r in rows[1:]:
            cells = [cell_info(c) for c in r['tableCells']]
            rid = cells[ci][0]
            chip = cells[cd][2] if cd is not None else []
            note = cells[cn][0] if cn is not None else ''
            link = cells[ce][1] if ce is not None else []
            main_rows.append(rid)
            if cd is None:
                problems.append(f'{rid}: table has no Decision column')
            elif len(chip) != 1:
                problems.append(f'{rid}: {len(chip)} Decision chips (want 1)')
            if ce is None or not link:
                problems.append(f'{rid}: no Explanation link')
            else:
                h = link[0][1].get('heading', {})
                if h.get('tabId') != exp_id:
                    problems.append(f'{rid}: Explanation link goes to tab {h.get("tabId")}, not Explanations')
                elif H.get(exp_id, {}).get(h.get('id')) != rid:
                    problems.append(f'{rid}: Explanation link lands on "{H.get(exp_id, {}).get(h.get("id"))}"')
            main_rows[-1] = (rid, chip[0] if chip else None, note)

    # explanations rows
    exp_rows = []
    if exp_id:
        for tb in tables(tabs[exp_id]['documentTab']['body']['content']):
            for r in tb['tableRows'][1:]:
                cells = [cell_info(c) for c in r['tableCells']]
                rid = cells[0][0]
                exp_rows.append(rid)
                back = [l for c in cells for l in c[1] if l[0].startswith('↩')]
                if not back:
                    problems.append(f'{rid}: no ↩ Back link in Explanations')
                    continue
                h = back[0][1].get('heading', {})
                if h.get('tabId') != main_id:
                    problems.append(f'{rid}: Back link goes to tab {h.get("tabId")}, not the list')
                elif H[main_id].get(h.get('id')) != rid:
                    problems.append(f'{rid}: Back link lands on "{H[main_id].get(h.get("id"))}"')

    ids = [r[0] for r in main_rows]
    if exp_id and ids != exp_rows:
        problems.append(f'IDs differ between the list and Explanations: {ids} vs {exp_rows}')
    if len(set(ids)) != len(ids):
        problems.append('duplicate IDs in the list')
    if a.rows:
        src = json.load(open(a.rows, encoding='utf-8'))
        src = src.get('rows', src) if isinstance(src, dict) else src
        sid = [r['id'] for r in src]
        if sid != ids:
            problems.append(f'rows file has {len(sid)} IDs, doc has {len(ids)}; differ at '
                            f'{[x for x in set(sid) ^ set(ids)] or "order"}')

    # answers
    tally = {}
    for rid, chip, note in main_rows:
        k = chip if chip and chip != 'Unanswered' else ('note only' if note else 'Unanswered')
        tally.setdefault(k, []).append(rid)
    print(f'Rows: {len(ids)} in the list, {len(exp_rows)} in Explanations')
    print('Answers:', '; '.join(f'{k} {len(v)}' for k, v in tally.items()))
    for k, v in tally.items():
        if k != 'Unanswered':
            print(f'  {k}: {", ".join(v)}')
    for rid, chip, note in main_rows:
        if note:
            print(f'  note {rid}: {note[:120]}')
    if problems:
        print(f'PROBLEMS ({len(problems)}):')
        for p in problems:
            print('  -', p)
        sys.exit(1)
    print('OK: every row has one chip, every Open and Back link lands on its own row.')


if __name__ == '__main__':
    main()
