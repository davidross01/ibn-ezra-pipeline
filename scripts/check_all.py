#!/usr/bin/env python3
"""Every check for one parasha in one command; prints only what needs reading.

Usage (repo root):
  python3 -I scripts/check_all.py <folder>            # e.g. vayera
  python3 -I scripts/check_all.py <folder> --accept   # after reading every NEW hit: remember them as read
  python3 -I scripts/check_all.py <folder> --full     # also list the hits already read

Runs: letters against Sefaria (consonant_check), vowels of lemmas and quotations (vowel_check),
misprint scan, the house-rule and layout report (check_book), and these, which were done by hand before:
  - every (printed) [correction] in the Hebrew commentary has a {i}Text.{/i} line in a note on that verse
  - every Onkelos entry (work/onkelos.py) is in the model, with the Aramaic as copied from onkelos.json
  - the Name inside the English is ה׳, not ד'
  - page numbers: book.json continuous, parasha.json first_page = book.json, last build (build/rep.json)
    = book.json, and the build is newer than the model
Hits already read and judged are kept in <folder>/review/check_baseline.json (written by --accept) and
are counted, not listed, so a new problem stands out. Exit status 1 if anything new or failing.
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = {'bereshit': 'data/model_final5.json'}
HEB = re.compile('[א-ת]')


def run(folder, script, *args):
    p = os.path.join(ROOT, folder, script)
    if not os.path.exists(p):
        return None
    r = subprocess.run([sys.executable, '-I', p, *args], cwd=os.path.join(ROOT, folder),
                       capture_output=True, text=True)
    if r.returncode and 'Traceback' in r.stderr:
        CRASHED[script] = r.stderr.strip().splitlines()[-1]
    return r.stdout + (r.stderr if r.returncode else '')


CRASHED = {}


def hits_vowels(out):
    return [l.strip() for l in out.splitlines() if ' | ' in l]


def hits_misprints(out):
    # keep (ch, v, kind, word, look-alikes); drop the frequency counts, which change as the book grows
    import ast
    res = []
    for l in out.splitlines():
        if l.startswith('('):
            try:
                t = ast.literal_eval(l.strip())
                res.append(repr((*t[:4], sorted(t[4]) if isinstance(t[4], list) else t[4])))
            except Exception:
                res.append(l.strip())
    return res


def hits_book(out):
    res, sec = [], None
    for l in out.splitlines():
        m = re.match(r'== (.+): \d+$', l)
        if m:
            sec = m.group(1); continue
        if sec and l.startswith('   ') and l.strip():
            res.append(f'{sec} :: {l.strip()}')
    return res


def plain(t):
    return re.sub(r'\{/?[a-z]+\}', '', t)


def own_checks(folder, M):
    out = {'Text lines': [], 'Onkelos': [], 'Name in English': [], 'pages': []}
    # (printed) [correction] -> Text line in a note of the same verse
    notes = {}
    for b in M['notes']:
        if 'text' in b:
            notes.setdefault((b['ch'], b['v']), []).append(b['text'])
    for b in M['hc']:
        t = b.get('text', '')
        for m in re.finditer(r'\(([^()]{1,40})\)\s*\[([^\]]{1,40})\]', t):
            if not (HEB.search(m.group(1)) and re.search('[֑-ׇ]', m.group(2))):
                continue          # a reference correction, not a misprint
            if not any('{i}Text.{/i}' in n for n in notes.get((b['ch'], b['v']), [])):
                out['Text lines'].append(f"{b['ch']}:{b['v']} {plain(m.group(0))} has no Text. line in its note")
    # Onkelos entries present in the model
    ent = os.path.join(ROOT, folder, 'work', 'onkelos.py')
    if os.path.exists(ent):
        sys.path.insert(0, os.path.join(ROOT, 'scripts')); import onk_lib
        onk = {}
        for p in [os.path.join(ROOT, f, 'src', 'onkelos.json') for f in os.listdir(ROOT)]:
            if os.path.exists(p):
                onk.update(json.load(open(p, encoding='utf-8'))['text'])
        for kind, ref, a, b in onk_lib.load(ent):
            want = onk_lib.resolve(a if kind == 'A' else b, ref, onk)
            if not any(want in n for n in notes.get(ref, [])):
                out['Onkelos'].append(f'{kind} {ref[0]}:{ref[1]} not in the model as written: {plain(want)[:90]}')
    # the Name in English Hebrew spans
    for sec in ('ec', 'notes'):
        for b in M[sec]:
            for m in re.finditer(r"\{h\}([^{]*)\{/h\}", b.get('text', '')):
                if re.search(r"(?<![א-ת֑-ׇ])ד['׳](?![א-ת])", m.group(1)):
                    out['Name in English'].append(f"{sec} {b['ch']}:{b['v']}: {m.group(1)[:60]}")
    # pages
    book = json.load(open(os.path.join(ROOT, 'book.json'), encoding='utf-8'))
    prev = None
    for e in book['parashot']:
        if prev and e['first_page'] != prev['last_page'] + 1:
            out['pages'].append(f"book.json: {e['parasha']} starts {e['first_page']}, {prev['parasha']} ends {prev['last_page']}")
        prev = e
    if book.get('next_first_page') != prev['last_page'] + 1:
        out['pages'].append(f"book.json: next_first_page {book.get('next_first_page')} should be {prev['last_page'] + 1}")
    me = next(e for e in book['parashot'] if e['folder'] == folder)
    pj = json.load(open(os.path.join(ROOT, folder, 'parasha.json'), encoding='utf-8'))
    if pj.get('first_page') != me['first_page']:
        out['pages'].append(f"parasha.json first_page {pj.get('first_page')} but book.json {me['first_page']}")
    rep = os.path.join(ROOT, folder, 'build', 'rep.json')
    if os.path.exists(rep):
        r = json.load(open(rep, encoding='utf-8'))
        if (r.get('first_page'), r.get('last_page')) != (me['first_page'], me['last_page']):
            out['pages'].append(f"last build is pages {r.get('first_page')}–{r.get('last_page')}, book.json {me['first_page']}–{me['last_page']}")
        if os.path.getmtime(rep) < os.path.getmtime(os.path.join(ROOT, folder, MODEL.get(folder, 'data/model.json'))):
            out['pages'].append('the model is newer than the last build: rebuild before trusting the layout checks')
    else:
        out['pages'].append('no build/rep.json: layout checks skipped (build first)')
    return out


def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if not a:
        sys.exit(__doc__)
    folder = a[0].strip('/')
    accept, full = '--accept' in sys.argv, '--full' in sys.argv
    mpath = MODEL.get(folder, 'data/model.json')
    M = json.load(open(os.path.join(ROOT, folder, mpath), encoding='utf-8'))
    res, fail = {}, []

    out = run(folder, 'work/consonant_check.py', mpath)
    if out is not None:
        ok = out.strip().endswith('differences: 0')
        res['letters'] = [] if ok else [l for l in out.strip().splitlines()]
        if not ok: fail.append('letters')
    out = run(folder, 'work/vowel_check.py', mpath)
    if out is not None: res['vowels'] = hits_vowels(out)
    out = run(folder, 'scripts/misprint_scan.py', mpath)
    if out is not None: res['misprints'] = hits_misprints(out)
    rep = os.path.join(ROOT, folder, 'build', 'rep.json')
    args = [mpath] + (['build/rep.json'] if os.path.exists(rep) else [])
    out = run(folder, 'scripts/check_book.py', *args)
    if out is not None: res['house rules + layout'] = hits_book(out)
    for s_, k_ in (('work/consonant_check.py', 'letters'), ('work/vowel_check.py', 'vowels'),
                   ('scripts/misprint_scan.py', 'misprints'), ('scripts/check_book.py', 'house rules + layout')):
        if s_ in CRASHED: res.pop(k_, None)
    if CRASHED:
        res['scripts that did not run'] = [f'{s}: {e}' for s, e in CRASHED.items()]
        fail.append('scripts that did not run')
    for k, v in own_checks(folder, M).items():
        res[k] = v
        if k == 'pages':
            if any(not x.startswith('no build') for x in v): fail.append(k)
        elif v:
            fail.append(k)

    bpath = os.path.join(ROOT, folder, 'review', 'check_baseline.json')
    base = json.load(open(bpath, encoding='utf-8')) if os.path.exists(bpath) else {}
    accept_kinds = ('vowels', 'misprints', 'house rules + layout', 'Name in English')
    new_total = 0
    print(f'check_all {folder} ({mpath})')
    for k, v in res.items():
        known = set(base.get(k, [])) if k in accept_kinds else set()
        new = [x for x in v if x not in known]
        old = len(v) - len(new)
        new_total += len(new) if k in accept_kinds else 0
        status = 'ok' if not new else f'{len(new)} NEW' if k in accept_kinds else f'{len(new)} FAIL'
        print(f'  {k:22} {status}' + (f'  ({old} already read)' if old else ''))
        for x in new[:60]:
            print(f'      {x[:200]}')
        if len(new) > 60:
            print(f'      … {len(new) - 60} more')
        if full and old:
            for x in v:
                if x in known: print(f'      (read) {x[:200]}')
    if accept:
        base = {k: res[k] for k in accept_kinds if k in res}
        os.makedirs(os.path.dirname(bpath), exist_ok=True)
        json.dump(base, open(bpath, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'accepted: {sum(len(v) for v in base.values())} hits remembered as read -> {os.path.relpath(bpath, ROOT)}')
    hard = [k for k in fail if k not in accept_kinds]
    print('RESULT: ' + ('clean' if not hard and not new_total else
                        ', '.join(filter(None, [f'{new_total} new hit(s) to read' if new_total else '',
                                                ('failing: ' + ', '.join(hard)) if hard else '']))))
    sys.exit(1 if (hard or (new_total and not accept)) else 0)


if __name__ == '__main__':
    main()
