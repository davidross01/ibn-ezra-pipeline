#!/usr/bin/env python3
"""One status report for the whole Ibn Ezra series. Read-only.

Usage (repo top):  python3 -I scripts/series_status.py [--json]

For each parasha in book.json: status and pages, latest draft PDF, open review
docs (from review_docs.json), and whether the parasha PDF, parts export, Key
Insights booklet and full-book PDF are newer than the parasha's data. "Newer"
uses git commit times, not file times (a fresh clone gives every file the same
time). Then: the full-book PDF, the next parasha and its first page, and any
uncommitted changes.
"""
import json, os, re, subprocess, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

GENESIS = ['Bereshit', 'Noach', 'Lech Lecha', 'Vayera', 'Chayei Sarah', 'Toledot',
           'Vayetze', 'Vayishlach', 'Vayeshev', 'Miketz', 'Vayigash', 'Vayechi']
TORAH = GENESIS + ['Shemot', 'Vaera', 'Bo', 'Beshalach', 'Yitro', 'Mishpatim', 'Terumah',
    'Tetzaveh', 'Ki Tisa', 'Vayakhel', 'Pekudei', 'Vayikra', 'Tzav', 'Shemini', 'Tazria',
    'Metzora', 'Acharei Mot', 'Kedoshim', 'Emor', 'Behar', 'Bechukotai', 'Bamidbar', 'Nasso',
    "Beha'alotcha", "Sh'lach", 'Korach', 'Chukat', 'Balak', 'Pinchas', 'Matot', 'Masei',
    'Devarim', 'Vaetchanan', 'Eikev', "Re'eh", 'Shoftim', 'Ki Teitzei', 'Ki Tavo', 'Nitzavim',
    'Vayeilech', "Ha'azinu", "V'Zot HaBerachah"]


def ctime(*paths):
    """Last commit time (unix) touching any of the paths; 0 if never committed."""
    paths = [p for p in paths if p]
    if not paths:
        return 0
    out = subprocess.run(['git', 'log', '-1', '--format=%ct', '--'] + paths,
                         capture_output=True, text=True).stdout.strip()
    return int(out) if out else 0


def day(t):
    if not t:
        return '—'
    import datetime
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime('%d %b %H:%M UTC')


def draft_key(p):
    m = re.search(r'draft (\d+)', p)
    return (1, 0) if p.endswith('final.pdf') else (0, int(m.group(1)) if m else -1)


def main():
    book = json.load(open('book.json', encoding='utf-8'))
    reg = json.load(open('review_docs.json', encoding='utf-8'))['docs'] if os.path.exists('review_docs.json') else []
    rep = {'parashot': [], 'book': {}, 'next': {}, 'uncommitted': []}
    finals = []
    lines = []
    for p in book['parashot']:
        name, f = p['parasha'], p['folder']
        final = p['status'].lower().startswith('final')
        data_t = ctime(f'{f}/data', f'{f}/work')
        drafts = sorted(glob.glob(f'{f}/drafts/*.pdf'), key=draft_key)
        latest = drafts[-1] if drafts else None
        lat_t = ctime(latest)
        r = {'parasha': name, 'pages': f"{p['first_page']}–{p['last_page']}", 'status': p['status'],
             'latest_pdf': latest, 'data_changed': day(data_t), 'warnings': []}
        if latest and lat_t < data_t:
            r['warnings'].append(f'data changed after the latest PDF ({os.path.basename(latest)}): rebuild')
        if final:
            finals.append((name, f, data_t))
            pub = f'{f}/Ibn Ezra on Parashat {name}.pdf'
            if not os.path.exists(pub):
                r['warnings'].append('no parasha PDF in its folder (commentary-publish-pdfs)')
            elif ctime(pub) < data_t:
                r['warnings'].append('parasha PDF older than its data (commentary-publish-pdfs)')
            if not os.path.isdir(f'{f}/export'):
                r['warnings'].append('final but no parts export (scripts/export_parts.py)')
            elif ctime(f'{f}/export') < data_t:
                r['warnings'].append('parts export older than the data (scripts/export_parts.py)')
        ins = f'insights/Ibn Ezra on Parashat {name} - Key Insights.pdf'
        if not os.path.exists(ins):
            r['insights'] = 'none yet'
        else:
            it = ctime(ins)
            r['insights'] = 'from ' + ('final' if final and it >= data_t else 'draft' if not final else 'older data')
            if it < data_t:
                r['warnings'].append('Key Insights booklet older than the data (rebuild it)')
        docs = [d for d in reg if d['parasha'] == name]
        r['open_reviews'] = [{'list': d['list'], 'title': d.get('title'), 'status': d['status'],
                              'rows': d.get('rows'), 'checked': d.get('checked'),
                              'link': f"https://docs.google.com/{"spreadsheets" if d.get("kind")=="Google Sheet" else "document"}/d/{d["id"]}/edit" if d.get('id') else None}
                             for d in docs if d['status'] in ('open', 'answered')]
        r['review_notes'] = [d['note'] for d in docs if d.get('note') and d['status'] == 'applied']
        rep['parashot'].append(r)

    # full book
    bpdfs = glob.glob('book/*.pdf')
    last_final = finals[-1][0] if finals else None
    b = {'files': bpdfs, 'warnings': []}
    want = f'book/Ibn Ezra on the Torah - Bereshit to {last_final}.pdf' if last_final else None
    if want and want not in bpdfs:
        b['warnings'].append(f'full book should be "{os.path.basename(want)}" (commentary-publish-pdfs --rebuild)')
    elif want and ctime(want) < max(t for _, _, t in finals):
        b['warnings'].append('full book older than a final parasha\'s data (commentary-publish-pdfs --rebuild)')
    if len(bpdfs) > 1:
        b['warnings'].append('more than one full-book PDF: keep only the latest')
    rep['book'] = b

    # front matter (its own file since 23 Oct 2026) and review docs that belong to no single parasha
    names = {p['parasha'] for p in book['parashot']}
    fpdf = 'front/Ibn Ezra on the Torah - Front Matter.pdf'
    rep['front'] = {'pdf': fpdf if os.path.exists(fpdf) else None, 'warnings': []}
    if not os.path.exists(fpdf):
        rep['front']['warnings'].append('no front matter PDF (bereshit/scripts/render.py ... frontonly)')
    elif ctime(fpdf) < ctime('bereshit/data/front.json'):
        rep['front']['warnings'].append('front matter PDF older than bereshit/data/front.json: rebuild it')
    rep['other_reviews'] = [{'parasha': d['parasha'], 'list': d['list'], 'rows': d.get('rows'), 'checked': d.get('checked'),
                             'link': f"https://docs.google.com/{"spreadsheets" if d.get("kind")=="Google Sheet" else "document"}/d/{d["id"]}/edit"}
                            for d in reg if d['parasha'] not in names and d['status'] in ('open', 'answered')]
    last = book['parashot'][-1]['parasha']
    nxt = TORAH[TORAH.index(last) + 1] if last in TORAH and TORAH.index(last) + 1 < len(TORAH) else None
    rep['next'] = {'parasha': nxt, 'first_page': book.get('next_first_page')}
    st = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True).stdout
    rep['uncommitted'] = [l for l in st.splitlines() if '__pycache__' not in l]

    if '--json' in sys.argv:
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        return
    print(book['title'])
    for r in rep['parashot']:
        print(f"\n{r['parasha']} — pages {r['pages']} — {r['status']}")
        print(f"  latest PDF: {os.path.basename(r['latest_pdf']) if r['latest_pdf'] else 'none'}; data last changed {r['data_changed']}")
        print(f"  Key Insights: {r['insights']}")
        for d in r['open_reviews']:
            print(f"  review OPEN: List {d['list']} ({d['rows']} rows) {d['link']}  [{d['checked'] or 'not checked'}]")
        for n in r['review_notes']:
            print(f"  review note: {n}")
        for w in r['warnings']:
            print(f"  ! {w}")
        if not r['warnings']:
            print('  everything built from the latest data')
    print(f"\nFront matter (pages i–x): {os.path.basename(rep['front']['pdf']) if rep['front']['pdf'] else 'none'}")
    for w in rep['front']['warnings']:
        print(f'  ! {w}')
    for d in rep['other_reviews']:
        print(f"  review OPEN: {d['parasha']} List {d['list']} ({d['rows']} rows) {d['link']}  [{d['checked'] or 'not checked'}]")
    print(f"\nFull book: {', '.join(os.path.basename(x) for x in rep['book']['files']) or 'none'}")
    for w in rep['book']['warnings']:
        print(f'  ! {w}')
    n = rep['next']
    print(f"\nNext parasha: {n['parasha']}, from page {n['first_page']}")
    if rep['uncommitted']:
        print(f"\nUncommitted changes ({len(rep['uncommitted'])}):")
        for l in rep['uncommitted'][:20]:
            print('  ' + l)


if __name__ == '__main__':
    main()
