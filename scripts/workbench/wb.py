# Workbench helpers for the Ibn Ezra series. They run INSIDE the Composio workbench
# (run_composio_tool and upload_local_file are preloaded there) and print only short reports,
# so the large Google and GitHub responses never reach the conversation.
#
# Load (one workbench cell):
#     r, _ = run_composio_tool('GITHUB_GET_RAW_REPOSITORY_CONTENT', {'owner': 'davidross01',
#            'repo': 'ibn-ezra-commentary', 'path': 'scripts/workbench/wb.py', 'ref': 'main'})
#     import requests; exec(requests.get(r['data']['content']['s3url']).content.decode('utf-8'))   # .content.decode: .text guesses Latin-1 and garbles '·' and '–'
# Then:
#     read_answers('vowels')      # or 'Vayera', a doc id, or part of a title (review_docs.json)
#     refresh_drive()             # dry=True to see the plan without changing Drive
#
# Accounts: David's own Google account only (davross846@gmail.com). Never the default
# Going Pro / filmgoingpro accounts.
import io, json, os, re, hashlib, contextlib, datetime, requests

OWNER, REPO, REF = 'davidross01', 'ibn-ezra-commentary', 'main'
DOCS = 'googledocs_spinet-dirk'      # davross846
DRIVE = 'googledrive_pulse-dwang'    # davross846
DRIVE_ROOT = '1bVsTk1WHrJM0NB158u4tFmU4g4rmbkMo'   # "Ibn Ezra on the Torah", anyone with the link can view
AUTHOR = {'name': 'Claude', 'email': 'noreply@anthropic.com'}


def _run(slug, args, account=None):
    """run_composio_tool without its schema printout; raises on error."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r, e = run_composio_tool(slug, args, account=account) if account else run_composio_tool(slug, args)
    if e:
        raise RuntimeError(f'{slug}: {e}')
    if isinstance(r, dict) and r.get('error'):
        raise RuntimeError(f'{slug}: {r["error"]}')
    return r.get('data', r) if isinstance(r, dict) else r


def gh_bytes(path):
    d = _run('GITHUB_GET_RAW_REPOSITORY_CONTENT', {'owner': OWNER, 'repo': REPO, 'path': path, 'ref': REF})
    return requests.get(d['content']['s3url'], timeout=120).content


def gh_json(path):
    return json.loads(gh_bytes(path).decode('utf-8'))


def gh_tree():
    d = _run('GITHUB_GET_A_TREE', {'owner': OWNER, 'repo': REPO, 'tree_sha': REF, 'recursive': True})
    t = d.get('tree') or d.get('data', {}).get('tree') or []
    return {x['path']: x.get('size') for x in t if x.get('type') == 'blob'}


def gh_commit(files, message):
    """files: {path: text}. One commit on main."""
    ups = [{'path': p, 'content': c, 'encoding': 'utf-8'} for p, c in files.items()]
    _run('GITHUB_COMMIT_MULTIPLE_FILES', {'owner': OWNER, 'repo': REPO, 'branch': REF, 'message': message,
                                          'upserts': ups, 'author': AUTHOR, 'committer': AUTHOR})


# ---------------------------------------------------------------- review answers
def _ptext(cell):
    out = []
    for s in cell.get('content', []):
        out.append(''.join(e.get('textRun', {}).get('content', '') for e in s.get('paragraph', {}).get('elements', [])))
    return ' '.join(x.strip() for x in out if x.strip())


def _chip(cell):
    for s in cell.get('content', []):
        for e in s.get('paragraph', {}).get('elements', []):
            dv = e.get('dropdown', {}).get('dropdownProperties', {}).get('displayValue')
            if dv:
                return dv
    return None


def _first_tab_body(doc):
    for k in ('document', 'data', 'response_data'):
        if isinstance(doc, dict) and k in doc and 'tabs' not in doc and 'body' not in doc:
            doc = doc[k]
    if 'tabs' in doc:
        return doc['tabs'][0]['documentTab']['body']['content'], doc.get('title')
    return doc['body']['content'], doc.get('title')


def find_review(key):
    reg = gh_json('review_docs.json')['docs']
    k = key.lower()
    hits = [d for d in reg if d.get('id') and (d['id'] == key or k in (d.get('title') or '').lower()
                                                or k in (d.get('parasha') or '').lower()
                                                or k in (d.get('rows_file') or '').lower())]
    open_hits = [d for d in hits if str(d.get('status', '')).startswith('open')]
    hits = open_hits or hits
    if len(hits) != 1:
        raise SystemExit(f'"{key}" matches {len(hits)} review docs: ' + '; '.join(d.get('title') or d['id'] for d in hits))
    return hits[0]


def _unwrap(doc):
    for k in ('document', 'data', 'response_data'):
        if isinstance(doc, dict) and k in doc and 'tabs' not in doc and 'body' not in doc:
            doc = doc[k]
    return doc


def _link_check(doc, rows_file):
    """Run scripts/check_review_doc.py (chips, Open/Back links, IDs) on the doc, here in the workbench."""
    import subprocess
    json.dump(doc, open('/mnt/files/rv_doc.json', 'w'), ensure_ascii=False)
    open('/mnt/files/rv_check.py', 'wb').write(gh_bytes('scripts/check_review_doc.py'))
    args = ['python3', '-I', '/mnt/files/rv_check.py', '/mnt/files/rv_doc.json']
    if rows_file:
        open('/mnt/files/rv_rows.json', 'wb').write(gh_bytes(rows_file)); args += ['--rows', '/mnt/files/rv_rows.json']
    r = subprocess.run(args, capture_output=True, text=True)
    lines = (r.stdout + r.stderr).splitlines()
    if r.returncode == 0:
        return 'OK: one chip per row, every Open and Back link lands on its own row'
    i = next((i for i, l in enumerate(lines) if l.startswith('PROBLEMS')), None)
    return [l.strip(' -') for l in lines[i + 1:]] if i is not None else lines[-3:]


def _progress_line(rows, when):
    from collections import OrderedDict
    import re as _re
    done = [r for r in rows if r['decision'] not in ('Unanswered', '', None)]
    cnt = OrderedDict()
    for r in done: cnt[r['decision']] = cnt.get(r['decision'], 0) + 1
    runs, prev = [], None
    for r in rows:
        if r['decision'] not in ('Unanswered', '', None): continue
        m = _re.match(r'([A-Z]+)(\d+)', r['id'])
        if not m: continue
        L, n = m.group(1), int(m.group(2))
        if prev and prev[0] == L and prev[2] == n - 1: prev[2] = n
        else: prev = [L, n, n]; runs.append(prev)
    rng = ', '.join(f'{L}{a}' if a == b else f'{L}{a}–{L}{b}' for L, a, b in runs)
    return (f'Progress ({when}): {len(done)} of {len(rows)} answered' + (' (' + ', '.join(f'{k} {v}' for k, v in cnt.items()) + ')' if cnt else '')
            + (f' · open: {rng}' if rng else ' · all answered'))

def _set_progress(doc_id, body, line):
    """The progress line under the doc's subtitle (David, 9 Nov 2026): replaced in place, or added if missing.
    Touches no row, chip or note."""
    paras = [el for el in body if 'paragraph' in el][:8]
    old = next((el for el in paras if _ptext({'content': [el]}).startswith('Progress')), None)
    if old:
        a, b = old['startIndex'], old['endIndex'] - 1
        reqs = [{'deleteContentRange': {'range': {'startIndex': a, 'endIndex': b}}}, {'insertText': {'location': {'index': a}, 'text': line}}]
    else:
        ti = next((i for i, el in enumerate(paras) if el['paragraph'].get('paragraphStyle', {}).get('namedStyleType') == 'TITLE'), None)
        if ti is None or ti + 1 >= len(paras): return
        a = paras[ti + 1]['endIndex']
        reqs = [{'insertText': {'location': {'index': a}, 'text': line + '\n'}},
                {'updateParagraphStyle': {'range': {'startIndex': a, 'endIndex': a + len(line.encode('utf-16-le')) // 2 + 1}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT'}, 'fields': 'namedStyleType'}}]
    n = len(line.encode('utf-16-le')) // 2
    reqs.append({'updateTextStyle': {'range': {'startIndex': a, 'endIndex': a + n}, 'textStyle': {'italic': True, 'bold': False, 'foregroundColor': {'color': {'rgbColor': {'red': 0x52/255, 'green': 0x51/255, 'blue': 0x4f/255}}}}, 'fields': 'italic,bold,foregroundColor'}})
    _run('GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT', {'document_id': doc_id, 'edit_docs': reqs}, account=DOCS)

def read_answers(key, commit=True, show=True, check_links=True, meta=None, progress=True):
    """Read only ID / Decision / Your note from a review Google Doc (main tab), check its chips and links,
    save <rows file> -> answers.json to GitHub and print a short summary. Returns the answers dict."""
    meta = meta or find_review(key)
    doc = _unwrap(_run('GOOGLEDOCS_GET_DOCUMENT_BY_ID', {'id': meta['id'], 'includeTabsContent': True}, account=DOCS))
    body, title = _first_tab_body(doc)
    rows, seen = [], set()
    for el in body:
        if 'table' not in el:
            continue
        trs = el['table']['tableRows']
        head = [_ptext(c).lower() for c in trs[0]['tableCells']]
        if 'id' not in head or 'decision' not in head:
            continue
        ci, cd = head.index('id'), head.index('decision')
        cn = head.index('your note') if 'your note' in head else None
        for tr in trs[1:]:
            cells = tr['tableCells']
            rid = _ptext(cells[ci])
            if not rid or rid in seen:
                continue
            seen.add(rid)
            dec = _chip(cells[cd]) or _ptext(cells[cd]) or 'Unanswered'
            note = _ptext(cells[cn]) if cn is not None else ''
            rows.append({'id': rid, 'decision': dec, 'note': note})
    counts = {}
    for r in rows:
        key2 = r['decision'] if not (r['decision'] == 'Unanswered' and r['note']) else 'Note only'
        counts[key2] = counts.get(key2, 0) + 1
    out = {'doc_id': meta['id'], 'title': title or meta.get('title'),
           'read_at': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
           'counts': counts, 'rows': rows}
    rf = meta.get('rows_file') or ''
    try:      # every row of the rows file must be in the doc, and nothing else
        rr = gh_json(rf) if rf else None
        rr = rr if isinstance(rr, list) else (rr or {}).get('rows', [])
        want = [x.get('id') or x.get('ID') for x in rr if isinstance(x, dict)]
        got = [r['id'] for r in rows]
        out['missing_from_doc'] = [i for i in want if i and i not in got]
        out['not_in_rows_file'] = [i for i in got if want and i not in want]
    except Exception as ex:
        out['rows_check'] = f'not checked: {ex}'
    if check_links:
        try:
            out['link_check'] = _link_check(doc, rf)
        except Exception as ex:
            out['link_check'] = [f'not checked: {ex}']
    out['link'] = f"https://docs.google.com/document/d/{meta['id']}/edit"
    if progress and rows:
        try:
            _set_progress(meta['id'], body, _progress_line(rows, datetime.datetime.now().strftime('%-d %b %Y')))
        except Exception as ex:
            out['progress'] = f'not updated: {ex}'
    path = (rf.replace('rows.json', 'answers.json') if rf.endswith('rows.json') else (rf.rsplit('/', 1)[0] + '/answers.json' if '/' in rf else 'answers.json'))
    out['_path'] = path
    if commit:
        gh_commit({path: json.dumps({k: v for k, v in out.items() if k != '_path'}, ensure_ascii=False, indent=1) + '\n'},
                  f'Review answers read: {out["title"]} ({len(rows)} rows)')
    if show:
        print(f'{out["title"]}: {len(rows)} rows ' + json.dumps(counts, ensure_ascii=False) + (f'  -> {path}' if commit else ''))
        for k in ('missing_from_doc', 'not_in_rows_file', 'rows_check'):
            if out.get(k): print(f'  !! {k}: {out[k]}')
        if 'missing_from_doc' in out and not out['missing_from_doc'] and not out['not_in_rows_file']:
            print('  IDs match the rows file')
        lc = out.get('link_check')
        if lc:
            print('  ' + lc if isinstance(lc, str) else '  !! chips/links: ' + '; '.join(lc[:8]))
        for r in rows:
            if r['note'] or r['decision'] not in ('Approve', 'Keep', 'Unanswered'):
                print(f'  {r["id"]}: {r["decision"]}' + (f' | {r["note"][:300]}' if r['note'] else ''))
    return out


def review_status(check_links=False):
    """Read the answers of every open review doc (review_docs.json), save all answers.json files in one
    commit, and print one short block per doc. Used by commentary-series-status."""
    reg = gh_json('review_docs.json')['docs']
    docs = [d for d in reg if d.get('id') and d.get('status') in ('open', 'answered') and d.get('kind', 'Google Doc') == 'Google Doc']
    outs, files = [], {}
    for d in docs:
        try:
            o = read_answers(d['id'], commit=False, show=False, check_links=check_links, meta=d)
            outs.append(o)
            files[o['_path']] = json.dumps({k: v for k, v in o.items() if k != '_path'}, ensure_ascii=False, indent=1) + '\n'
        except Exception as ex:
            print(f"!! {d.get('title')}: {ex}")
    if files:
        gh_commit(files, f'Review answers read: {len(files)} open review(s)')
    for o in outs:
        c = o['counts']; n = sum(c.values()); un = c.get('Unanswered', 0)
        state = 'ALL ANSWERED - ready to apply' if un == 0 else f'{n - un} of {n} answered'
        print(f"{o['title']}: {state} {json.dumps(c, ensure_ascii=False)}\n  {o['link']}  -> {o['_path']}")
        for r in o['rows']:
            if r['note'] or r['decision'] in ('Change', 'Discuss'):
                print(f"  {r['id']}: {r['decision']}" + (f" | {r['note'][:200]}" if r['note'] else ''))
        lc = o.get('link_check')
        if lc and not isinstance(lc, str):
            print('  !! chips/links: ' + '; '.join(lc[:8]))
    return outs


# ---------------------------------------------------------------- Drive refresh
def _drive_ls(folder):
    d = _run('GOOGLEDRIVE_FIND_FILE', {'folder_id': folder, 'q': 'trashed = false',
                                       'fields': 'files(id,name,size,md5Checksum,mimeType)', 'pageSize': 200}, account=DRIVE)
    return d.get('files', [])


def _upload(local, name, file_id=None, parent=None, mimetype='application/pdf'):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        up, e = upload_local_file(local)
    if e:
        raise RuntimeError(f'upload {name}: {e}')
    f = {'name': name, 'mimetype': mimetype, 's3key': up['s3key']}
    if os.path.getsize(local) > 4 * 1024 * 1024:     # the plain upload stops at 5 MB; the resumable one has no such limit
        args = {'file_to_upload': f, 'chunkSize': 4 * 262144}
        if file_id: args['file_id'] = file_id
        else: args.update(folder_to_upload_to=parent, metadata={'name': name, 'parents': [parent]})
        d = _run('GOOGLEDRIVE_RESUMABLE_UPLOAD', args, account=DRIVE)
        return file_id or (d.get('id') if isinstance(d, dict) else None)
    if file_id:
        _run('GOOGLEDRIVE_UPLOAD_UPDATE_FILE', {'fileId': file_id, 'file_to_upload': f}, account=DRIVE)
        return file_id
    d = _run('GOOGLEDRIVE_CREATE_FILE', {'name': name, 'parents': [parent], 'mimeType': mimetype,
                                          'file_to_upload': f}, account=DRIVE)
    return d.get('id')


def drive_plan(tree=None):
    """{folder prefix: [(drive name, repo path, match prefix or None)]} from book.json and the repo tree."""
    tree = tree or gh_tree()
    book = gh_json('book.json')
    # The parasha files are numbered in Torah order ("01 Bereshit.pdf") so Drive lists them in order. The full book is on
    # Drive too, first in "03 Parashot" as "00 …" (David, 15 Nov 2026, Ruling 114: "I want the full book on drive, even
    # for Ibn Ezra"); it is over 5 MB, so _upload sends it by the resumable upload.
    plan = {'02': [], '03': [], '04': [], '05': [], '06': []}
    full = sorted(p for p in tree if p.startswith('book/Ibn Ezra on the Torah - Bereshit to') and p.endswith('.pdf'))
    if full:
        plan['03'].append(('00 ' + full[-1].split('/')[-1], full[-1], '00 Ibn Ezra on the Torah - Bereshit to'))
    # "06 Plain text": the whole book as plain text, the parts export (David, 15 Nov 2026: Drive is a second way to everything)
    for part, label in (('chumash_hebrew', 'The verses in Hebrew'), ('chumash_english', 'The verses in English'),
                        ('ibn_ezra_hebrew', 'Ibn Ezra in Hebrew'), ('ibn_ezra_english', 'Ibn Ezra in English'), ('notes', 'The notes')):
        if f'export/{part}.txt' in tree:
            plan['06'].append((f'Ibn Ezra on the Torah - {label}.txt', f'export/{part}.txt', None))
    plan['02'] = [('Ibn Ezra on the Torah - Front Matter.pdf', 'front/Ibn Ezra on the Torah - Front Matter.pdf', None)]
    if 'back/Ibn Ezra on the Torah - Glossary.pdf' in tree:   # the glossary at the back of the book (David, 9 Nov 2026)
        plan['02'].append(('Ibn Ezra on the Torah - Glossary.pdf', 'back/Ibn Ezra on the Torah - Glossary.pdf', None))
    for i, e in enumerate(book['parashot'], 1):
        P, folder = e['parasha'], e['folder']
        final = (e.get('stage') in ('final', 'audit') if e.get('stage') else str(e.get('status', '')).startswith('final'))   # final or audit (Ruling 105)
        ins = f'insights/Ibn Ezra on Parashat {P} - Key Insights.pdf'
        if ins in tree:
            plan['04'].append((f'{i:02d} {P} - Key Insights.pdf', ins, ins.split('/')[-1]))
        if final:
            src = f'{folder}/Ibn Ezra on Parashat {P}.pdf'
            if src not in tree:
                src = f'{folder}/drafts/Ibn Ezra {P} - final.pdf'
            plan['03'].append((f'{i:02d} {P}.pdf', src, f'Ibn Ezra on Parashat {P}.pdf'))
        else:
            drafts = [p for p in tree if p.startswith(f'{folder}/drafts/Ibn Ezra {P} - draft ') and p.endswith('.pdf')]
            if drafts:
                n = max(drafts, key=lambda p: int(p.rsplit('draft ', 1)[1][:-4]))
                plan['05'].append((n.split('/')[-1], n, f'Ibn Ezra {P} - draft'))
    finals = [e['parasha'] for e in book['parashot'] if (e.get('stage') in ('final', 'audit') if e.get('stage') else str(e.get('status', '')).startswith('final'))]
    return plan, finals


def refresh_drive(dry=False):
    """Make the Drive folder match GitHub: replace changed files in place (links stay the same),
    add new ones, rename superseded drafts, trash the draft of a parasha that is now final.
    Compares MD5, so unchanged files are left alone. Prints one line per change."""
    tree = gh_tree()
    plan, finals = drive_plan(tree)
    subs = {f['name'][:2]: f['id'] for f in _drive_ls(DRIVE_ROOT) if f.get('mimeType', '').endswith('folder')}
    log, same = [], 0
    for pre, items in plan.items():
        fid = subs.get(pre)
        if not fid:
            log.append(f'!! no sub-folder {pre} in Drive'); continue
        files = _drive_ls(fid)
        used = set()
        for name, path, prefix in items:
            hit = [f for f in files if f['name'] == name] or ([f for f in files if prefix and f['name'].startswith(prefix)] if prefix else [])
            # an older name (prefix) is renamed in place, so the file keeps its link
            data = gh_bytes(path)
            md5 = hashlib.md5(data).hexdigest()
            ext = os.path.splitext(path)[1] or '.pdf'
            mt = 'text/plain' if ext == '.txt' else 'application/pdf'
            local = '/mnt/files/drive_' + hashlib.sha1(path.encode()).hexdigest()[:10] + ext
            if hit:
                f = hit[0]; used.add(f['id'])
                if f.get('md5Checksum') == md5 and f['name'] == name:
                    same += 1; continue
                if not dry:
                    if f.get('md5Checksum') != md5:
                        open(local, 'wb').write(data); _upload(local, name, file_id=f['id'], mimetype=mt)
                    if f['name'] != name:
                        _run('GOOGLEDRIVE_UPDATE_FILE_PUT', {'fileId': f['id'], 'name': name}, account=DRIVE)
                log.append(f'{pre} updated: {name}' + (f' (was {f["name"]})' if f['name'] != name else ''))
            else:
                if not dry:
                    open(local, 'wb').write(data); _upload(local, name, parent=fid, mimetype=mt)
                log.append(f'{pre} added: {name}')
        for f in files:
            if f['id'] in used:
                continue
            stale_draft = pre == '05' and any(f['name'].startswith(f'Ibn Ezra {P} - draft') for P in finals)
            if stale_draft:
                if not dry:
                    _run('GOOGLEDRIVE_TRASH_FILE', {'file_id': f['id']}, account=DRIVE)
                log.append(f'{pre} trashed (parasha now final): {f["name"]}')
            else:
                log.append(f'{pre} left alone (not in the plan): {f["name"]}')
    # the full book is no longer kept on Drive: trash any copy, then the empty "01 Full book" folder
    if '01' in subs:
        left = []
        for f in _drive_ls(subs['01']):
            if f['name'].startswith('Ibn Ezra on the Torah - Bereshit to'):
                if not dry:
                    _run('GOOGLEDRIVE_TRASH_FILE', {'file_id': f['id']}, account=DRIVE)
                log.append(f'01 trashed (full book not kept on Drive): {f["name"]}')
            else:
                left.append(f['name'])
        if left:
            log.append(f'01 left alone (not in the plan): {", ".join(left)}')
        else:
            if not dry:
                _run('GOOGLEDRIVE_TRASH_FILE', {'file_id': subs['01']}, account=DRIVE)
            log.append('01 folder trashed (empty)')
    # verify
    bad = []
    if not dry:
        for pre, items in plan.items():
            fid = subs.get(pre)
            if not fid: continue
            have = {f['name']: f.get('size') for f in _drive_ls(fid)}
            for name, path, _ in items:
                if str(have.get(name)) != str(tree.get(path)):
                    bad.append(f'{name}: Drive {have.get(name)} vs GitHub {tree.get(path)}')
    print(('DRY RUN — ' if dry else '') + f'Drive: {len(log)} change(s), {same} already current' + (f', {len(bad)} MISMATCH' if bad else ', verified'))
    for x in log + ['!! ' + b for b in bad]:
        print('  ' + x)
    try:
        sync_reviews(dry=dry)          # the reviews-in-progress folder, every time the Drive is refreshed
    except Exception as ex:
        print(f'  !! reviews folder not synced: {ex}')
    try:
        make_release(dry=dry)          # a GitHub Release of the current version (Ruling 115)
    except Exception as ex:
        print(f'  !! release not made: {ex}')
    return {'changes': log, 'same': same, 'mismatch': bad}


# ---------------------------------------------------------------- GitHub Releases (David, 15 Nov 2026, Ruling 115)
# "It doesn't have to be finished, it can be the most up to date": every publish makes a Release of the current version
# (checkboxes: every publish, automatically). The tag is the edition date and a fingerprint of what was built
# (book.json's built_hash of each parasha and the front matter's hash), so a refresh with nothing new makes none.
GITHUB = 'github_cosse-palay'      # davidross01

def release_files(tree=None):
    tree = tree or gh_tree()
    book = gh_json('book.json')
    out = sorted(p for p in tree if p.startswith('book/Ibn Ezra on the Torah - Bereshit to') and p.endswith('.pdf'))
    out += [p for p in ('front/Ibn Ezra on the Torah - Front Matter.pdf', 'back/Ibn Ezra on the Torah - Glossary.pdf') if p in tree]
    for e in book['parashot']:
        P, folder = e['parasha'], e['folder']
        out += [p for p in (f'{folder}/Ibn Ezra on Parashat {P}.pdf', f'insights/Ibn Ezra on Parashat {P} - Key Insights.pdf') if p in tree]
    return out, book

def make_release(dry=False, budget=150):
    import time
    t0 = time.time()
    tree = gh_tree()
    files, book = release_files(tree)
    fp = hashlib.sha1(json.dumps([e.get('built_hash') for e in book['parashot']] + [book.get('front_hash')]).encode()).hexdigest()[:8]
    date = max(e.get('edition', '') for e in book['parashot']) or datetime.date.today().isoformat()
    tag = f'edition-{date}-{fp}'
    try:
        rel = _run('GITHUB_GET_A_RELEASE_BY_TAG_NAME', {'owner': OWNER, 'repo': REPO, 'tag': tag}, account=GITHUB)
    except Exception:
        rel = None
    if rel and rel.get('id'):
        have = {a['name'] for a in (_run('GITHUB_LIST_RELEASE_ASSETS', {'owner': OWNER, 'repo': REPO, 'release_id': rel['id']}, account=GITHUB) or [])}
    else:
        have = set()
        if dry:
            print(f'DRY RUN — release {tag}: {len(files)} files'); return tag
        names = ', '.join(e['parasha'] for e in book['parashot'])
        rel = _run('GITHUB_CREATE_A_RELEASE', {'owner': OWNER, 'repo': REPO, 'tag_name': tag, 'target_commitish': REF,
                    'name': f'Ibn Ezra on the Torah — edition of {date}',
                    'body': f'The current version of every file ({names}): the full book, the front matter and glossary, each parasha and its Key Insights booklet. Made automatically when the book was published (Ruling 115).'}, account=GITHUB)
    todo = [p for p in files if p.split('/')[-1] not in have]
    for p in todo:
        if time.time() - t0 > budget:
            print(f'release {tag}: {len(todo) - todo.index(p)} file(s) left; run make_release() again'); return tag
        local = '/mnt/files/rel_' + hashlib.sha1(p.encode()).hexdigest()[:10] + '.pdf'
        open(local, 'wb').write(gh_bytes(p))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            up, e = upload_local_file(local)
        if e: raise RuntimeError(f'upload {p}: {e}')
        _run('GITHUB_UPLOAD_RELEASE_ASSET', {'owner': OWNER, 'repo': REPO, 'release_id': rel['id'], 'content_type': 'application/pdf',
                                             'asset': {'name': p.split('/')[-1], 'mimetype': 'application/pdf', 's3key': up['s3key']}}, account=GITHUB)
    print(f'release {tag}: ' + (f'{len(todo)} file(s) added' if todo else 'already complete') + f', {len(files)} in all')
    return tag


# ---------------------------------------------------------------- reviews in progress (David, 9 Nov 2026)
# "make a section in the Google drive with all of the current reviews in progress and have [them] removed once they
# are fully applied" — with checkboxes he chose: once fully applied, archive (a copy in the repo) and trash.
# The folder is its own top-level folder in his Drive, not inside "Ibn Ezra on the Torah", because that folder is
# shared with anyone who has the link and a doc inside it would be shared with them too.
REVIEWS_FOLDER = '-02 Ibn Ezra — Reviews in progress'   # David's names (he put -01/-02 in front to sort them first); found by id
_FOLDER_MIME = 'application/vnd.google-apps.folder'


def _find(d, k):
    if isinstance(d, dict):
        if k in d: return d[k]
        for v in d.values():
            r = _find(v, k)
            if r is not None: return r
    elif isinstance(d, list):
        for v in d:
            r = _find(v, k)
            if r is not None: return r
    return None


REVIEWS_FOLDER_ID = '1O7WtvLyYhia5hb0PldzL5NKzgZMLRStN'
OLDER_FOLDER = '-01 Ibn Ezra — Older reviews'            # David, 9 Nov 2026: finished reviews kept, not trashed
OLDER_FOLDER_ID = '1jUeiNkiIifdx6nSU8U8tosrQOjf5LX9A'  # in the book folder, limited access like the reviews folder


def _private_folder(fid, name):
    m = _run('GOOGLEDRIVE_GET_FILE_METADATA', {'file_id': fid, 'fields': 'id,parents,trashed,inheritedPermissionsDisabled'}, account=DRIVE)
    if _find(m, 'trashed') or DRIVE_ROOT not in (_find(m, 'parents') or []):
        raise RuntimeError(f'{name}: not found in the book folder; make it there with the Google Drive connector '
                           '(create_file, inheritedPermissionsDisabled=true) and set its id in wb.py')
    if _find(m, 'inheritedPermissionsDisabled') is not True:
        raise RuntimeError(f'{name} is not limited-access: anyone with the book link could read the reviews. '
                           'Set inheritedPermissionsDisabled=true (Google Drive connector, update_file) first.')
    return fid


def _move_into(file_id, folder_id):
    """Out of the trash if it is there, and into the folder alone (its other parents removed)."""
    _run('GOOGLEDRIVE_UPDATE_FILE_METADATA_PATCH', {'fileId': file_id, 'labels': {'trashed': False}}, account=DRIVE)
    m = _run('GOOGLEDRIVE_GET_FILE_METADATA', {'file_id': file_id, 'fields': 'parents'}, account=DRIVE)
    a = {'fileId': file_id, 'add_parents': folder_id}
    other = [x for x in (_find(m, 'parents') or []) if x != folder_id]
    if other: a['remove_parents'] = ','.join(other)
    _run('GOOGLEDRIVE_UPDATE_FILE_PUT', a, account=DRIVE)


def _reviews_folder(create=True):
    """The folder "Ibn Ezra — Reviews in progress", inside the book folder "Ibn Ezra on the Torah - PDFs" (David, 9 Nov
    2026: "the folder in Ibn Ezra on the Torah - PDFs"). The book folder is shared with anyone who has the link, so this
    folder has LIMITED ACCESS (inheritedPermissionsDisabled = true): the review docs inside stay private to David. That
    setting cannot be made with the Composio tools (their raw proxy is the Going Pro account), only with the Google Drive
    connector's update_file — so this never creates the folder, and stops if the folder is not limited."""
    return _private_folder(REVIEWS_FOLDER_ID, REVIEWS_FOLDER)


def _archive_dir(entry):
    base = (entry.get('parasha') or '').lower().replace(' ', '_')
    return f'{base}/review/archive' if base in ('bereshit', 'noach', 'lech_lecha', 'vayera', 'chayei_sarah', 'toledot') else 'review_audit/archive'


def archive_doc(entry):
    """Archive one applied review doc (docs/rules/review_doc.md, "Archiving"): a plain-text copy of both tabs and the
    answers (ID, Decision, Your note) committed to the repo; then, only after the commit, the doc moves to the folder
    "Ibn Ezra — Older reviews" (David, 9 Nov 2026: kept there, no longer trashed)."""
    doc_id, title = entry['id'], entry['title']
    txt = _run('GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT', {'document_id': doc_id, 'include_tabs_content': True, 'table_cell_delimiter': ' | '}, account=DOCS)
    text = txt.get('plain_text') or txt.get('text') or _find(txt, 'plain_text') or json.dumps(txt, ensure_ascii=False)
    ans = read_answers(doc_id, commit=False, show=False, check_links=False, progress=False)
    rows = ans.get('rows', []) if isinstance(ans, dict) else ans
    folder = _archive_dir(entry); safe = re.sub(r'[^\w .–—-]', '', title).strip()
    dpath = f'{folder}/decisions.json'
    try:
        dec = gh_json(dpath)
    except Exception:
        dec = {}
    dec[title] = {'doc_id': doc_id, 'archived': datetime.datetime.now().strftime('%Y-%m-%d'),
                  'rows': [{'id': r['id'], 'decision': r.get('decision'), 'note': r.get('note') or ''} for r in rows]}
    gh_commit({f'{folder}/{safe}.txt': text, dpath: json.dumps(dec, ensure_ascii=False, indent=1)},
              f'Archive review doc: {title}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>')
    gh_bytes(f'{folder}/{safe}.txt')                      # the commit is there before the doc goes
    _move_into(doc_id, _private_folder(OLDER_FOLDER_ID, OLDER_FOLDER))
    return folder


def sync_reviews(dry=False):
    """Every open review doc in "Reviews in progress"; every fully applied one archived (text + answers committed) and
    moved to "Older reviews"; every archived doc found elsewhere (the trash included) moved there too; review_docs.json updated."""
    reg = gh_json('review_docs.json'); docs = reg['docs']
    fid = _reviews_folder(create=not dry)
    inside = {f['id'] for f in _drive_ls(fid)} if fid else set()
    older = _private_folder(OLDER_FOLDER_ID, OLDER_FOLDER)
    in_older = {f['id'] for f in _drive_ls(older)}
    log, changed = [], False
    for e in docs:
        st = (e.get('status') or '')
        if not e.get('id') or e.get('status') == 'record':
            continue
        if st.startswith('open') or st.startswith('answered'):
            if e['id'] not in inside:
                if not dry:
                    _run('GOOGLEDRIVE_MOVE_FILE', {'file_id': e['id'], 'add_parents': fid}, account=DRIVE)
                log.append(f'in progress: {e["title"]}')
        elif st == 'applied':
            if not dry:
                e['archive'] = archive_doc(e); e['status'] = 'archived'; changed = True
            log.append(f'applied → archived, moved to Older reviews: {e["title"]}')
        elif st == 'archived' and e['id'] not in in_older:
            try:
                if not dry:
                    _move_into(e['id'], older)
                log.append(f'archived → moved to Older reviews: {e["title"]}')
            except RuntimeError:
                log.append(f'archived, no longer on Drive (text in {e.get("archive")}): {e["title"]}')
    if changed:
        gh_commit({'review_docs.json': json.dumps(reg, ensure_ascii=False, indent=1)},
                  'review_docs.json: applied review docs archived (sync_reviews)\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>')
    print(('DRY RUN — ' if dry else '') + f'Reviews in progress: {len(log)} change(s)')
    for x in log:
        print('  ' + x)
    return {'folder': fid, 'changes': log}


# ---------------------------------------------------------------- the documents in "-03 How it is made"
HANDBOOK_FOLDER = '-03 How it is made (handoff, rules, rulings)'
HANDBOOK_FOLDER_ID = '1ALbmTB3lrzR4Md2y_1mLeXAremu0kZMP'    # in the book folder, limited access (docs/rules/sources.md, rule 6)
CLAUDE_TAG = 'Claude: '        # replies go out from David's own account, so Claude's begin with this


def _open_comments(doc_id):
    """David's open comments on one Doc: not resolved, not deleted."""
    out, tok = [], None
    while True:
        a = {'fileId': doc_id, 'pageSize': 100, 'fields': 'comments(id,content,resolved,deleted,createdTime,'
             'quotedFileContent,author(displayName),replies(content,author(displayName))),nextPageToken'}
        if tok: a['pageToken'] = tok
        r = _run('GOOGLEDRIVE_LIST_COMMENTS', a, account=DRIVE)
        out += [c for c in (_find(r, 'comments') or []) if not c.get('resolved') and not c.get('deleted')]
        tok = _find(r, 'nextPageToken')
        if not tok: return out


def handbook_comments(show=True):
    """Every open comment on the documents, as [{n, title, doc, id, quoted, content, replies, created}]. Each one is a
    new rule of David's (core skill, "A new rule from David") or a question; answer it with handbook_reply()."""
    hb, out = gh_json('docs/handbook.json'), []
    for e in hb:
        if not e.get('doc'): continue
        for c in _open_comments(e['doc']):
            out.append({'n': e['n'], 'title': e['title'], 'doc': e['doc'], 'id': c['id'],
                        'quoted': (c.get('quotedFileContent') or {}).get('value', ''), 'content': c.get('content', ''),
                        'replies': [x.get('content', '') for x in c.get('replies') or []], 'created': c.get('createdTime')})
    if show:
        print(f'{len(out)} open comment(s) on the documents')
        for c in out:
            print(f"- {c['title']} [{c['doc']} / {c['id']}] on “{c['quoted'][:120]}”: {c['content']}"
                  + (f"  (replies: {' | '.join(c['replies'])})" if c['replies'] else ''))
    return out


def handbook_reply(doc_id, comment_id, text, resolve=True):
    """Reply under David's comment (what was done, the ruling number) and resolve it, so the Doc can be refreshed."""
    a = {'file_id': doc_id, 'comment_id': comment_id, 'content': CLAUDE_TAG + text}
    if resolve: a['action'] = 'resolve'
    _run('GOOGLEDRIVE_CREATE_REPLY', a, account=DRIVE)


def sync_handbook(dry=False, budget=130):
    """Make the Google Docs in "-03 How it is made" match docs/handbook/NN.html on GitHub, IN PLACE: the page is uploaded
    onto the same Doc (Drive converts text/html), so the id and link never change; a changed title is fixed. A Doc with
    an open comment is skipped (replacing its text would detach the comment): answer it first. Commits handbook.json
    with drive_md5 / refreshed. Run `python3 -I scripts/handbook.py build` and push first."""
    t0 = datetime.datetime.now().timestamp()     # a workbench cell stops at 180 s: refresh what fits, record it, run again
    hb = gh_json('docs/handbook.json')
    # 00–15 live in "-03 How it is made"; an entry with `folder` lives in another private folder (the guide, the skills,
    # the audit: David, 15 Nov 2026, "everything also in the Google Drive"). Every one must be limited-access.
    targets = {HANDBOOK_FOLDER_ID: HANDBOOK_FOLDER, **{e['folder']: e['title'] for e in hb if e.get('folder')}}
    for fid, nm in targets.items():
        _private_folder(fid, nm)
    log, changed = [], False
    for e in hb:
        if not e.get('doc'):
            log.append(f"!! {e['title']}: no Google Doc yet — create an empty Doc in the folder (Google Drive connector) "
                       "and put its id in docs/handbook.json"); continue
        if e.get('drive_md5') == e.get('html_md5') and not e.get('retitle'):
            m = _run('GOOGLEDRIVE_GET_FILE_METADATA', {'file_id': e['doc'], 'fields': 'name,trashed'}, account=DRIVE)
            if _find(m, 'name') == e['title'] and not _find(m, 'trashed'):
                continue
        if not dry and datetime.datetime.now().timestamp() - t0 > budget:
            log.append('.. stopped for time: run sync_handbook() again for the rest'); break
        data = gh_bytes(f"docs/handbook/{e['n']}.html")
        if hashlib.md5(data).hexdigest() != e.get('html_md5'):
            log.append(f"!! {e['title']}: the page on GitHub is not the one built — push, then sync again"); continue
        open_c = _open_comments(e['doc'])
        if open_c:
            log.append(f"-- {e['title']}: skipped, {len(open_c)} open comment(s) — handbook_comments(), answer, sync again"); continue
        if dry:
            log.append(f"would refresh {e['title']}"); continue
        local = f"/mnt/files/handbook_{e['n']}.html"
        open(local, 'wb').write(data)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            up, err = upload_local_file(local)
        if err:
            log.append(f"!! {e['title']}: upload failed: {err}"); continue
        _run('GOOGLEDRIVE_UPLOAD_UPDATE_FILE', {'fileId': e['doc'], 'uploadType': 'media', 'file_to_upload':
             {'name': f"{e['n']}.html", 'mimetype': 'text/html', 's3key': up['s3key']}}, account=DRIVE)
        m = _run('GOOGLEDRIVE_GET_FILE_METADATA', {'file_id': e['doc'], 'fields': 'name,mimeType,parents'}, account=DRIVE)
        if _find(m, 'mimeType') != 'application/vnd.google-apps.document':
            raise RuntimeError(f"{e['title']}: no longer a Google Doc after the upload ({_find(m, 'mimeType')})")
        if _find(m, 'name') != e['title']:
            _run('GOOGLEDRIVE_UPDATE_FILE_PUT', {'fileId': e['doc'], 'name': e['title']}, account=DRIVE)
        target = e.get('folder') or HANDBOOK_FOLDER_ID
        if target not in (_find(m, 'parents') or []):
            _move_into(e['doc'], target)
        e['drive_md5'], e['refreshed'] = e['html_md5'], datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
        e.pop('retitle', None)
        changed = True
        log.append(f"refreshed {e['title']}")
    if changed and not dry:
        gh_commit({'docs/handbook.json': json.dumps(hb, ensure_ascii=False, indent=1) + '\n'},
                  'Handbook: Google Docs refreshed in place (sync_handbook)\n\n'
                  'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>')
    known = {e.get('doc') for e in hb} | {'1_uiuWQXAHtD6pEtRZ-9ebwx1jV5wmIw3k_XXfzZhmVk'}   # + the Editorial record (a review doc, kept in -03)
    for f in [f for fid in targets for f in _drive_ls(fid)]:
        if f['id'] not in known:
            log.append(f"-- left alone, not in docs/handbook.json: {f['name']} ({f['id']})")
    print('\n'.join(log) or 'handbook: every Doc already current')
    return log
