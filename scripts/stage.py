"""The stage of each parasha and the edition date on its title page (David, 10 Nov 2026, Ruling 105).

Stages, in book.json "stage":
  draft  — being written; its latest draft is the only copy in Drive "05 Drafts".
  final  — finished; the book PDF is in "03 Parashot", its booklet in "04 Key Insights".
  audit  — final, and changed since (audits, ideas, consistency, any later review). Never closes.
Final and audit are both *published*: whatever version is being edited is the current one, and every
applied change replaces the files in place (scripts/publish_current.py), so their links stay the same.

"edition" is the date of the last change to a parasha's content; the title page prints "Edition of <date>".
"built_hash" is the fingerprint of the content it was built from, so publish_current.py knows what changed.
"""
import datetime, hashlib, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLISHED = ('final', 'audit')


def stage(p):
    s = p.get('stage')
    if s:
        return s
    return 'final' if str(p.get('status', '')).lower().startswith('final') else 'draft'


def published(p):
    return stage(p) in PUBLISHED


def edition_text(p):
    """'Edition of 10 November 2026', or '' when no edition date is set."""
    d = p.get('edition')
    if not d:
        return ''
    d = datetime.date.fromisoformat(d)
    return f'Edition of {d.day} {d.strftime("%B")} {d.year}'


def entry(book, folder):
    return next(p for p in book['parashot'] if p['folder'] == folder)


def load_book(root=ROOT):
    return json.load(open(f'{root}/book.json', encoding='utf-8'))


def content_files(folder, root=ROOT):
    """The files a parasha's pages are made from: its model and title data, and the build scripts it uses."""
    f = f'{root}/{folder}'
    if folder == 'bereshit':
        files = [f'{f}/data/model_final5.json', f'{f}/data/front.json', f'{f}/data/foot_terms.json',
                 f'{f}/scripts/render.py', f'{f}/scripts/book.css', f'{f}/scripts/layout.js']
    else:
        files = [f'{f}/data/model.json', f'{f}/parasha.json', f'{f}/data/foot_terms.json',
                 f'{root}/shared/scripts/render.py', f'{root}/shared/scripts/book.css', f'{root}/shared/scripts/layout.js']
    return [x for x in files if os.path.exists(x)]


def content_hash(folder, root=ROOT):
    """Fingerprint of the content. first_page in parasha.json is left out, so a renumbering alone is not a new edition."""
    h = hashlib.sha256()
    for path in content_files(folder, root):
        data = open(path, 'rb').read()
        if path.endswith('bereshit/data/front.json'):   # only Bereshit's own title page; the rest is the front matter
            d = [x for x in json.loads(data)['before'] if x.get('parasha_title')]
            data = json.dumps(d, sort_keys=True, ensure_ascii=False).encode()
        if path.endswith('parasha.json'):
            d = json.loads(data)
            d.pop('first_page', None)
            data = json.dumps(d, sort_keys=True, ensure_ascii=False).encode()
        h.update(os.path.relpath(path, root).encode() + b'\0' + data + b'\0')
    return h.hexdigest()[:16]
