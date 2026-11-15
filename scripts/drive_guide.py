"""docs/DRIVE_GUIDE.md: the guide at the top of the book's Drive folder ("-00 Guide (start here)/00 Guide to the book's
Drive folder"), a second way to reach everything (sources.md, rule 11). Made from docs/drive.json, docs/handbook.json,
review_docs.json and book.json; run by `scripts/handbook.py build` before the pages are built, so it is always current.
    python3 -I scripts/drive_guide.py
"""
import json, os, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
DOCURL = 'https://docs.google.com/document/d/{}/edit'
SHEETURL = 'https://docs.google.com/spreadsheets/d/{}/edit'
FILEURL = 'https://drive.google.com/file/d/{}/view'
FOLDERURL = 'https://drive.google.com/drive/folders/{}'


def main():
    D, H, R, B = J('docs/drive.json'), J('docs/handbook.json'), J('review_docs.json')['docs'], J('book.json')
    gh = D['github']
    url = {'document': DOCURL, 'spreadsheet': SHEETURL, 'file': FILEURL}
    L = ['# Guide to the book’s Drive folder', '',
         'Everything of “Ibn Ezra on the Torah” can be reached from here: the book, the reviews, how it is made, the skills '
         'and the audit. The GitHub repository is the source; these are its copies, kept current. Folders whose name starts '
         'with “-” are private; the others are open to anyone with the book’s link.', '',
         f'Made by scripts/drive_guide.py. The full book is first in “03 Parashot” (Ruling 114), and on GitHub: '
         f'[{os.path.basename(gh["full_book"])}]({gh["repo"]}/blob/main/{urllib.parse.quote(gh["full_book"])}). '
         f'Every published version is also a [GitHub Release]({gh["releases"]}) (Ruling 115).', '',
         '## The folders', '']
    for f in D['folders']:
        L.append(f'- [{f["name"]}]({FOLDERURL.format(f["id"])}) — {f["holds"]}' + (' (private)' if f['private'] else ''))
    L += ['', '## The book', '']
    for i, p in enumerate(B['parashot'], 1):
        L.append(f'- {i:02d} {p["parasha"]}: pages {p["first_page"]}–{p["last_page"]}, {p.get("stage", "")} — in “03 Parashot” and “04 Key Insights”')
    L += ['- The front matter and the glossary — in “02 Front matter”', '- The plain text of the whole book — in “06 Plain text”', '',
          '## How it is made (-03)', '']
    for e in sorted([e for e in H if e['n'].isdigit()], key=lambda e: e['n']):
        L.append(f'- [{e["title"]}]({DOCURL.format(e["doc"])})')
    L += ['', '## The skills (-04)', '']
    for e in sorted([e for e in H if e['n'].startswith('S')], key=lambda e: e['title']):
        L.append(f'- [{e["title"].replace("Skill — ", "")}]({DOCURL.format(e["doc"])})')
    L.append(f'- commentary-house-rules — the core skill, “12 Core skill” above')
    L += ['', '## Reviews', '']
    for st, head in (('open', 'In progress (-02)'), ('answered', 'Answered, not yet applied (-02)'), ('archived', 'Older (-01)')):
        xs = [r for r in R if r['status'] == st]
        if xs:
            L += [f'**{head}**', ''] + [f'- [{r["title"]}]({DOCURL.format(r["id"])})' + (f' — {r["rows"]} rows' if r.get('rows') else '') for r in xs] + ['']
    L += ['## The audit (-06)', '']
    for e in [e for e in H if e['n'].startswith('A')]:
        L.append(f'- [{e["title"]}]({DOCURL.format(e["doc"])})')
    L += ['', '## Other files', '']
    for f in D['files']:
        L.append(f'- [{f["name"]}]({url[f["kind"]].format(f["id"])}) — {f["where"]}')
    L += ['', f'Repository: {gh["repo"]} (private).', '']
    open(os.path.join(ROOT, 'docs', 'DRIVE_GUIDE.md'), 'w', encoding='utf-8').write('\n'.join(L))


if __name__ == '__main__':
    main()
    print('docs/DRIVE_GUIDE.md written')
