#!/usr/bin/env python3
"""Publish the current version of everything (David, 10 Nov 2026, Ruling 105).

A parasha goes draft -> final -> audit; the audit never closes. Whatever version is being edited is the
current one: every applied change rebuilds what depends on it and replaces the files in place, so the
links in Drive ("03 Parashot/05 Chayei Sarah.pdf" …) and on GitHub always open the latest version.

    python3 -I scripts/publish_current.py            # rebuild what changed, renumber, booklets, front, full book
    python3 -I scripts/publish_current.py --dry      # only say what would be rebuilt and why
    python3 -I scripts/publish_current.py --force noach,toledot   # rebuild these even if unchanged ('all' = every one)
Then commit, push and run refresh_drive() in the workbench (the Drive copies are replaced in place).

What it does, in Torah order:
 1. Brings each parasha's model up to date (work/assemble.py; Bereshit: work/build_model.py) and fingerprints
    its content (scripts/stage.py, content_hash). Changed since book.json "built_hash" -> a new edition:
    "edition" = today, and a final parasha moves to stage "audit".
 2. Page numbers run on: first_page = the last page before + 1. A parasha is rebuilt when its content changed
    or its first page moved; a page count that changes moves every later parasha, which is rebuilt in the same run.
 3. The PDF: a published parasha (final/audit) -> drafts/"Ibn Ezra <P> - final.pdf"; a draft -> its latest
    draft is replaced if it is not yet committed (not yet sent), otherwise a new "draft N+1" is made.
 4. Each rebuilt published parasha: its Key Insights booklet (page references come from this build).
 5. If any published parasha was rebuilt: front matter (contents page), parts export, and publish_pdfs.py
    (parasha copies, glossary, the one full book). check_all on every rebuilt parasha.
"""
import datetime, glob, hashlib, json, os, re, shutil, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import stage

DRY = '--dry' in sys.argv
FORCE = set()
if '--force' in sys.argv:
    FORCE = set(sys.argv[sys.argv.index('--force') + 1].split(','))
TODAY = datetime.date.today().isoformat()
PY = sys.executable


def run(cmd, cwd=ROOT, show=False):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f'!! {" ".join(cmd)} (in {cwd}) failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}')
    if show:
        print(r.stdout.rstrip())
    return r.stdout


def committed_unchanged(path):
    """True if the file is in git and unchanged since the last commit (so David has had it)."""
    if subprocess.run(['git', 'ls-files', '--error-unmatch', path], capture_output=True).returncode:
        return False
    return subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', path]).returncode == 0


def update_model(folder):
    if folder == 'bereshit':
        run([PY, '-I', 'bereshit/work/build_model.py'])
    elif os.path.exists(f'{folder}/work/assemble.py'):
        run([PY, '-I', 'work/assemble.py'], cwd=folder)


def build(folder):
    """Render and paginate one parasha; returns (pages, first, last)."""
    os.makedirs(f'{folder}/build', exist_ok=True)
    model = 'data/model_final5.json' if folder == 'bereshit' else 'data/model.json'
    run([PY, 'scripts/render.py', model, 'build/book.html'], cwd=folder)
    out = run([PY, 'scripts/make_pdf.py', f'{ROOT}/{folder}/build/book.html', f'{ROOT}/{folder}/build/book.pdf',
               'build/rep.json'], cwd=folder)
    m = re.search(r'pages (\d+) \(numbered (\d+)–(\d+)\) warnings (\d+)', out)
    if not m:
        sys.exit(f'!! {folder}: no page report from make_pdf\n{out[-1500:]}')
    warn = [l.strip() for l in out[m.end():].splitlines() if l.strip() and not l.strip().startswith('INFO')]
    if warn:   # INFO lines (a verse's comments continuing overleaf) are normal; anything else stops it
        sys.exit(f'!! {folder}: {len(warn)} layout warning(s) — not published\n' + '\n'.join(warn[:20]))
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def apply_held(book):
    """A change David chose to hold for a later build (book.json "held"; sources.md, For Claude): it runs once the
    parasha named in "at" is published (finalize-parasha sets its stage to final, then runs this script), and the
    parashot it touches are rebuilt in the same run, because their content changed."""
    keep = []
    for h in book.get('held', []):
        p = next((x for x in book['parashot'] if x['folder'] == h['at']), None)
        if not (p and stage.published(p)):
            print(f"held (Ruling {h['ruling']}): {h['what']} — waits {h['when']}")
            keep.append(h)
            continue
        if DRY:
            print(f"held (Ruling {h['ruling']}): would be applied now ({h['script']}), then its parashot rebuilt")
            keep.append(h)
            continue
        print(f"held (Ruling {h['ruling']}): applying {h['script']}")
        run([PY, '-I', h['script']], show=True)
    if not DRY and len(keep) != len(book.get('held', [])):
        if keep:
            book['held'] = keep
        else:
            book.pop('held', None)
        json.dump(book, open('book.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1); open('book.json', 'a').write('\n')


def main():
    book = stage.load_book()
    chrome = run([PY, '-c', 'from playwright.sync_api import sync_playwright as s; p=s().start(); '
                  'b=p.chromium.launch(); print(b.version.split(".")[0]); b.close(); p.stop()']).strip()
    apply_held(book)
    plan, expected_first = [], 1
    for p in book['parashot']:
        f = p['folder']
        update_model(f)
        h = stage.content_hash(f)
        why = []
        if h != p.get('built_hash'):
            why.append('content changed')
        if p['first_page'] != expected_first:
            why.append(f'first page {p["first_page"]} -> {expected_first}')
        if f in FORCE or 'all' in FORCE:
            why.append('forced')
        if why and p.get('chromium') and p['chromium'] != chrome:
            sys.exit(f'!! {p["parasha"]} is built with Chromium {p["chromium"]}, this machine has {chrome}: '
                     'rebuild it only where its version is installed (page.md)')
        plan.append((p, h, why, expected_first))
        # pages if rebuilt are not known yet: the next first page is settled after the build (below)
        expected_first = p['last_page'] + 1   # a rebuild may move this; the build loop below settles it
    if DRY:
        for p, h, why, _ in plan:
            print(f"{p['parasha']:13} {stage.stage(p):6} {'REBUILD: ' + ', '.join(why) if why else 'current'}")
        print('(page shifts after a rebuild may add later parashot)')
        return

    rebuilt, published_changed, report = [], False, []
    expected_first = 1
    for p, h, why, _ in plan:
        f, P = p['folder'], p['parasha']
        why = list(why)
        if p['first_page'] != expected_first and not any(w.startswith('first page') for w in why):
            why.append(f'first page {p["first_page"]} -> {expected_first}')
        if not why:
            expected_first = p['last_page'] + 1
            continue
        # a real change (not the first fingerprint; finalize-parasha clears built_hash and sets the edition itself)
        content = bool(p.get('built_hash')) and h != p['built_hash']
        if content:
            p['edition'] = TODAY
            if stage.stage(p) == 'final':
                p['stage'] = 'audit'
        p.setdefault('stage', stage.stage(p))
        # first page into parasha.json (Bereshit starts the book at 1)
        pj = f'{f}/parasha.json'
        d = json.load(open(pj, encoding='utf-8'))
        if d.get('first_page') != expected_first:
            d['first_page'] = expected_first
            json.dump(d, open(pj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); open(pj, 'a').write('\n')
        json.dump(book, open('book.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)   # edition for the title page
        pages, first, last = build(f)
        old = (p['first_page'], p['last_page'])
        p['first_page'], p['last_page'] = first, last
        p['chromium'] = chrome
        p['built_hash'] = stage.content_hash(f)
        if stage.published(p):
            shutil.copy(f'{f}/build/book.pdf', f'{f}/drafts/Ibn Ezra {P} - final.pdf')
            out = f'drafts/Ibn Ezra {P} - final.pdf'
            published_changed = True
        else:
            drafts = sorted(glob.glob(f'{f}/drafts/Ibn Ezra {P} - draft *.pdf'),
                            key=lambda x: int(re.search(r'draft (\d+)', x).group(1)))
            n = int(re.search(r'draft (\d+)', drafts[-1]).group(1)) if drafts else 0
            if not drafts or (content and committed_unchanged(drafts[-1])):
                n += 1
            out = f'drafts/Ibn Ezra {P} - draft {n}.pdf'
            shutil.copy(f'{f}/build/book.pdf', f'{f}/{out}')
        rebuilt.append(p)
        report.append(f"{P}: {', '.join(why)}; pages {first}–{last}" + (f' (were {old[0]}–{old[1]})' if old != (first, last) else '')
                      + f"; stage {p['stage']}; {stage.edition_text(p) or 'no edition date'} -> {f}/{out}")
        expected_first = last + 1
    book['next_first_page'] = book['parashot'][-1]['last_page'] + 1
    # A run stopped after the builds (a booklet, the front matter) must not lose the steps after them: the parashot
    # rebuilt are kept in book.json "publish_pending" until the run ends, and the next run picks them up.
    pending = set(book.get('publish_pending', [])) | {p['folder'] for p in rebuilt}
    if pending:
        rebuilt = [p for p in book['parashot'] if p['folder'] in pending]
        published_changed = published_changed or any(stage.published(p) for p in rebuilt)
        book['publish_pending'] = sorted(pending)
    json.dump(book, open('book.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open('book.json', 'a').write('\n')

    fh = hashlib.sha256(open('bereshit/data/front.json', 'rb').read()).hexdigest()[:16]
    front_changed = fh != book.get('front_hash')
    if not rebuilt and not front_changed:
        print('Everything is current: nothing rebuilt.')
        return
    pub = [p for p in rebuilt if stage.published(p)]
    for p in pub:   # booklet page references come from this build's rep.json
        if os.path.exists(f"insights/Ibn Ezra on Parashat {p['parasha']} - Key Insights.pdf") or \
                f"'{p['parasha']}':" in open('insights/source.py', encoding='utf-8').read():   # a new final parasha's first booklet
            run([PY, 'insights/booklet.py', p['parasha']])
            report.append(f"{p['parasha']}: Key Insights booklet rebuilt")
    if published_changed or front_changed:
        # front matter: the contents page lists every published parasha with its first page
        run([PY, 'scripts/render.py', 'data/model_final5.json', 'build/front.html', 'frontonly'], cwd='bereshit')
        o = run([PY, 'scripts/make_pdf.py', f'{ROOT}/bereshit/build/front.html', f'{ROOT}/bereshit/build/front.pdf',
                 'build/frep.json'], cwd='bereshit')
        if 'warnings 0' not in o:
            sys.exit('!! front matter: a page runs past the bottom\n' + o[-1500:])
        shutil.copy('bereshit/build/front.pdf', 'front/Ibn Ezra on the Torah - Front Matter.pdf')
        run([PY, 'scripts/export_parts.py'])
        o = run([PY, 'scripts/publish_pdfs.py'])
        report.append('front matter, parts export, glossary and full book rebuilt: ' + o.strip().splitlines()[-1][:160])
        book['front_hash'] = fh
        book.pop('publish_pending', None)
        json.dump(book, open('book.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1); open('book.json', 'a').write('\n')
    if book.pop('publish_pending', None) is not None:
        json.dump(book, open('book.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1); open('book.json', 'a').write('\n')
    bad = []
    for p in rebuilt:
        r = subprocess.run([PY, '-I', 'scripts/check_all.py', p['folder']], capture_output=True, text=True)
        res = (re.findall(r'RESULT: .*', r.stdout) or ['RESULT: (none)'])[-1]
        report.append(f"{p['parasha']} check_all {res}")
        if r.returncode:
            bad.append(p['parasha'])
    print('\n'.join(report))
    print('\nNext: commit, push, then refresh_drive() in the workbench.' if not bad else
          f'\n!! check_all not clean for {", ".join(bad)}: read the hits (fix or --accept) before pushing.')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
