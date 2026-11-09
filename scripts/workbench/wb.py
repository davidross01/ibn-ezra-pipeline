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
import io, json, hashlib, contextlib, datetime, requests

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
    open_hits = [d for d in hits if d.get('status') == 'open']
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


def _upload(local, name, file_id=None, parent=None):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        up, e = upload_local_file(local)
    if e:
        raise RuntimeError(f'upload {name}: {e}')
    f = {'name': name, 'mimetype': 'application/pdf', 's3key': up['s3key']}
    if file_id:
        _run('GOOGLEDRIVE_UPLOAD_UPDATE_FILE', {'fileId': file_id, 'file_to_upload': f}, account=DRIVE)
        return file_id
    d = _run('GOOGLEDRIVE_CREATE_FILE', {'name': name, 'parents': [parent], 'mimeType': 'application/pdf',
                                          'file_to_upload': f}, account=DRIVE)
    return d.get('id')


def drive_plan(tree=None):
    """{folder prefix: [(drive name, repo path, match prefix or None)]} from book.json and the repo tree."""
    tree = tree or gh_tree()
    book = gh_json('book.json')
    # The full book is not kept on Drive (David, 29 Oct 2026: over the 5 MB upload limit); readers use the
    # front matter plus the parasha files, which are numbered in Torah order ("01 Bereshit.pdf") so Drive lists them in order.
    plan = {'02': [], '03': [], '04': [], '05': []}
    plan['02'] = [('Ibn Ezra on the Torah - Front Matter.pdf', 'front/Ibn Ezra on the Torah - Front Matter.pdf', None)]
    for i, e in enumerate(book['parashot'], 1):
        P, folder = e['parasha'], e['folder']
        final = str(e.get('status', '')).startswith('final')
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
    finals = [e['parasha'] for e in book['parashot'] if str(e.get('status', '')).startswith('final')]
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
            if len(data) > 5 * 1024 * 1024:
                log.append(f'!! {name}: {len(data)//1024} KB, over the 5 MB upload limit'); continue
            md5 = hashlib.md5(data).hexdigest()
            local = '/mnt/files/drive_' + hashlib.sha1(path.encode()).hexdigest()[:10] + '.pdf'
            if hit:
                f = hit[0]; used.add(f['id'])
                if f.get('md5Checksum') == md5 and f['name'] == name:
                    same += 1; continue
                if not dry:
                    if f.get('md5Checksum') != md5:
                        open(local, 'wb').write(data); _upload(local, name, file_id=f['id'])
                    if f['name'] != name:
                        _run('GOOGLEDRIVE_UPDATE_FILE_PUT', {'fileId': f['id'], 'name': name}, account=DRIVE)
                log.append(f'{pre} updated: {name}' + (f' (was {f["name"]})' if f['name'] != name else ''))
            else:
                if not dry:
                    open(local, 'wb').write(data); _upload(local, name, parent=fid)
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
    return {'changes': log, 'same': same, 'mismatch': bad}
