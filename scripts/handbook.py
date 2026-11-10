"""The documents in David's Drive folder "-03 How it is made": Google Doc copies of the handoff, README, rulings, rules,
core skill and history (docs/rules/sources.md, rule 6). The repo files are the source; the Docs are refreshed IN PLACE
(same id, same link) by sync_handbook() in the Composio workbench (scripts/workbench/wb.py).

    python3 -I scripts/handbook.py build     # rebuild docs/handbook/NN.html from the sources (pandoc), 00 with the live
                                             # status from series_status.py; records each source's and page's md5
    python3 -I scripts/handbook.py --check   # list the copies that are out of date (exit 0; --strict exits 1)
    python3 -I scripts/handbook.py --ci      # the same as GitHub warnings (CI); never fails the run

The manifest is docs/handbook.json: [{n, title, src, doc, src_md5, html_md5, drive_md5, refreshed}]. build sets
src_md5/html_md5; sync_handbook() sets drive_md5/refreshed after replacing the Doc's content and commits the manifest.
A copy is out of date when its source changed since the last build ("build"), or the last build is not yet in Drive
("refresh in Drive").
"""
import hashlib, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = os.path.join(ROOT, 'docs', 'handbook.json')
OUTDIR = os.path.join(ROOT, 'docs', 'handbook')
FOLDER = '1ALbmTB3lrzR4Md2y_1mLeXAremu0kZMP'   # "-03 How it is made (handoff, rules, rulings)", limited access


def md5(b):
    return hashlib.md5(b).hexdigest()


def load():
    return json.load(open(MAN, encoding='utf-8'))


def save(M):
    json.dump(M, open(MAN, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(MAN, 'a', encoding='utf-8').write('\n')


def status_md():
    """'Where things stand', from series_status.py --json: short enough for David to read on his phone."""
    out = subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'scripts', 'series_status.py'), '--json'],
                         capture_output=True, text=True, cwd=ROOT)
    if out.returncode:
        return '_The status could not be made this time._\n'
    d = json.loads(out.stdout)
    L = ['| Parasha | Pages | Status |', '|---|---|---|']
    reviews = []
    for p in d['parashot']:
        st = p['status'].split('; earlier')[0]
        word = st.split(' (')[0]
        when = re.search(r'\d{1,2} \w{3} 20\d\d', st)
        L.append(f"| {p['parasha']} | {p['pages']} | {word}{' (' + when.group(0) + ')' if when else ''} |")
        reviews += [r for r in p.get('open_reviews', [])]
    reviews += [r for r in d.get('other_reviews') or [] if r.get('link')]
    nx = d.get('next') or {}
    if nx.get('parasha'):
        L += ['', f"Next parasha: {nx['parasha']}, from page {nx['first_page']}."]
    if reviews:
        L += ['', '**Open review docs**', '']
        seen = set()
        for r in reviews:
            if r['link'] in seen:
                continue
            seen.add(r['link'])
            n = f" — {r['rows']} row{'s' if r['rows'] != 1 else ''}" if r.get('rows') else ''
            L.append(f"- [{r['title']}]({r['link']}){n}")
    acts = d.get('actions') or []
    if acts:
        L += ['', '**Next steps**', '']
        L += ['- ' + re.sub(r' \(review_status\(\) in the workbench\)| https://\S+', '', a) for a in acts]
    L += ['', f"_Made on {__import__('datetime').date.today().strftime('%-d %b %Y')} from the repository._"]
    return '\n'.join(L) + '\n'


def source_text(e):
    t = open(os.path.join(ROOT, e['src']), encoding='utf-8').read()
    if e['src'] == 'docs/rules/CORE_SKILL.md':           # the skill's frontmatter is not for the reader
        t = re.sub(r'\A---\n.*?\n---\n', '', t, flags=re.S)
    if '<!-- status -->' in t:
        t = t.replace('<!-- status -->', status_md())
    return t


def build(M):
    os.makedirs(OUTDIR, exist_ok=True)
    for e in M:
        raw = open(os.path.join(ROOT, e['src']), 'rb').read()
        html = subprocess.run(['pandoc', '-f', 'gfm', '-t', 'html5', '-s', '--metadata', f"pagetitle={e['title']}"],
                              input=source_text(e).encode('utf-8'), capture_output=True, check=True).stdout
        path = os.path.join(OUTDIR, f"{e['n']}.html")
        open(path, 'wb').write(html)
        e['src_md5'], e['html_md5'] = md5(raw), md5(html)
    save(M)
    print(f'built {len(M)} pages in docs/handbook/')


def stale(M=None):
    out = []
    for e in M or load():
        raw = open(os.path.join(ROOT, e['src']), 'rb').read()
        if e.get('src_md5') != md5(raw):
            out.append((e['n'], e['title'], 'its source changed: run scripts/handbook.py build'))
        elif not e.get('doc'):
            out.append((e['n'], e['title'], 'no Google Doc yet: create it in the folder, then sync_handbook()'))
        elif e.get('drive_md5') != e.get('html_md5'):
            out.append((e['n'], e['title'], 'not yet refreshed in Drive: sync_handbook() in the workbench'))
    return out


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['build']:
        build(load())
    else:
        s = stale()
        for n, t, why in s:
            print(f'::warning title=Handbook::{t}: {why}' if '--ci' in a else f'{t}: {why}')
        if not s and '--ci' not in a:
            print('handbook: every Google Doc copy is current')
        sys.exit(1 if s and '--strict' in a else 0)
