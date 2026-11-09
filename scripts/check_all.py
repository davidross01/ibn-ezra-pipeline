#!/usr/bin/env python3
"""Every check for one parasha in one command; prints only what needs reading.

Usage (repo root):
  python3 -I scripts/check_all.py <folder>            # e.g. vayera
  python3 -I scripts/check_all.py <folder> --accept   # after reading every NEW hit: remember them as read
  python3 -I scripts/check_all.py <folder> --full     # also list the hits already read
  python3 -I scripts/check_all.py <folder> --ci       # GitHub Actions: no build there, so layout and pages are
                                                      # skipped and Ideas (the audit's to-do) are listed, not failed

Runs: letters against Sefaria (consonant_check), vowels of lemmas and quotations (vowel_check),
misprint scan, the house-rule and layout report (check_book), and these, which were done by hand before:
  - every (printed) [correction] in the Hebrew commentary has a {i}Text.{/i} line in a note on that verse
  - every Onkelos entry (work/onkelos.py) is in the model, with the Aramaic as copied from onkelos.json
  - the Name inside the English is ה׳, not ד'
  - every word of the Hebrew commentary is pointed in full (scripts/partial_vowels.py; David, 28 Oct 2026)
  - every Hebrew span in the comments and notes comes from a source (scripts/source_check.py): "not found"
    and "only far from the verse" hits are read like vowel hits; no {q:}/{o:} marker is left unresolved
  - page numbers: book.json continuous, parasha.json first_page = book.json, last build (build/rep.json)
    = book.json, and the build is newer than the model
  - Ibn Ezra's ideas (scripts/ideas_scan.py): verses not yet in <folder>/review/ideas.json; --accept never
    hides them, they stay listed until each is written up ("done") or judged "not needed: <why>"; and the wider
    search in his Hebrew ("Ideas (Hebrew)", 9 Nov 2026), whose finds leave the list through ideas.json or ideas_he.json
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
        if l.strip() and not l.startswith(' '):
            sec = None                     # SUMMARY or any other heading ends the section (its counts are not hits)
            continue
        if sec and l.startswith('   ') and l.strip():
            res.append(f'{sec} :: {l.strip()}')
    return res


def plain(t):
    return re.sub(r'\{/?[a-z]+\}', '', t)


def own_checks(folder, M):
    out = {'Text lines': [], 'Onkelos': [], 'Name in English': [], 'Partly pointed': [], 'Hebrew sources': [], 'Ideas': [], 'Ideas (Hebrew)': [], 'Idea sources': [], 'Its parallel': [], 'markers': [], 'pages': []}
    # every word pointed in full (Vowels Review 1, E1)
    sys.path.insert(0, os.path.join(ROOT, 'scripts')); import partial_vowels
    out['Partly pointed'] = [f'{c}:{v} {w}' for c, v, w in partial_vowels.scan(folder)]
    # Ibn Ezra's ideas get a full paragraph (notes.md, 30 Oct 2026): comments touching an idea, not yet in review/ideas.json
    import ideas_scan
    out['Ideas'] = [f'{c}:{v} ({", ".join(k)})' for c, v, k in ideas_scan.scan(folder)]
    # the wider search in Ibn Ezra's Hebrew (9 Nov 2026); a find leaves the list through ideas.json or ideas_he.json
    out['Ideas (Hebrew)'] = [f'{c}:{v} ({", ".join(k)})' for c, v, k in ideas_scan.scan_he(folder)]
    # each idea place: Ibn Ezra's own writings and Saadia's Emunot veDeot read and recorded (notes.md, David, 8 Nov 2026)
    out['Idea sources'] = [f'{k}: not yet in review/idea_sources.json' for k in ideas_scan.sources_todo(folder)]
    # Hebrew spans traced to a source (copied by script, never typed)
    sys.path.insert(0, os.path.join(ROOT, 'scripts')); import source_check
    missing, far, _, _ = source_check.check(folder)
    out['Hebrew sources'] = ['not found: ' + x for x in missing] + ['far: ' + x for x in far]
    # Ibn Ezra's אָחִיו said of a word is "its parallel", not "its brother" (translation.md; David, 9 Nov 2026)
    for sec in ('ec', 'notes'):
        for b in M[sec]:
            t = plain(b.get('text', ''))
            for m in re.finditer(r'\b(?:its|their) brothers?\b|\bis the brother of\b', t):
                out['Its parallel'].append(f"{sec} {b['ch']}:{b['v']}: …{t[max(0, m.start() - 40):m.end() + 30]}…")
    for sec in ('ec', 'notes'):
        for b in M[sec]:
            if re.search(r'\{[oq]:', b.get('text', '')):
                out['markers'].append(f"{sec} {b['ch']}:{b['v']}: unresolved marker (run work/assemble.py)")
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
            if re.search(r'\{(?:q|ie|iep|vow):', want):   # Chayei Sarah on: the other markers too
                want = onk_lib.resolve_every(want, ref, {(h['ch'], h['v']): h['text'] for h in M['hc']})
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
        want = str(me.get('chromium') or '')
        have = str(r.get('browser') or '').split('.')[0]
        if want and not have:
            out['pages'].append('the build does not record its Chromium version: rebuild with the current make_pdf.py')
        elif want and have != want:
            out['pages'].append(f"built with Chromium {have}, but {me['parasha']} was laid out with {want} (book.json): "
                                f"page breaks can move; rebuild where Chromium {want} is installed, or ask David before re-paginating")
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
    accept, full, ci = '--accept' in sys.argv, '--full' in sys.argv, '--ci' in sys.argv
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

    if ci:      # the Actions runner has no build/: layout hits and the pages check need one
        if 'house rules + layout' in res:
            res['house rules + layout'] = [x for x in res['house rules + layout'] if not x.startswith('layout')]
        res['pages'] = [x for x in res.get('pages', []) if not x.startswith(('no build', 'the build', 'the model is newer'))]
        fail = [k for k in fail if k != 'pages' or res['pages']]
    bpath = os.path.join(ROOT, folder, 'review', 'check_baseline.json')
    base = json.load(open(bpath, encoding='utf-8')) if os.path.exists(bpath) else {}
    accept_kinds = ('vowels', 'misprints', 'house rules + layout', 'Name in English', 'Partly pointed', 'Hebrew sources', 'Ideas', 'Ideas (Hebrew)', 'Idea sources', 'Its parallel')
    new_total = 0
    print(f'check_all {folder} ({mpath})')
    for k, v in res.items():
        # a "far" Hebrew-sources hit names where the word was first found; that place moves whenever a source
        # file is added (Chayei Sarah, 2 Nov 2026), so the same hit is matched without it
        stable = lambda x: re.sub(r'  — only in .*$', '', x) if k == 'Hebrew sources' else x
        known = {stable(x) for x in base.get(k, [])} if k in accept_kinds else set()
        new = [x for x in v if stable(x) not in known]
        old = len(v) - len(new)
        new_total += len(new) if k in accept_kinds and not (ci and k in ('Ideas', 'Ideas (Hebrew)', 'Idea sources')) else 0
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
        # Ideas are never remembered as read: a verse leaves the list only through <folder>/review/ideas.json
        base = {k: res[k] for k in accept_kinds if k in res and k not in ('Ideas', 'Ideas (Hebrew)', 'Idea sources')}
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
