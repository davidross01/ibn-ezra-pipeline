# Build a review list as a Google Doc in David's own account (davross846), with Decision chips and an
# Explanations tab linked both ways (review-list-google-doc skill).
#
# Runs INSIDE the Composio workbench, where run_composio_tool is preloaded. Typical use there:
#     src = <this file, fetched from GitHub>; exec(src)
#     B = Builder(cfg); B.phase_main(); B.phase_explanations(); B.phase_styles(); B.phase_links(); B.verify()
# cfg: title, subtitle, how (list of (kind, text)), parts [(letter, heading, sentence, headers, widths)],
#      rows (review/listN_rows.json), clean (list of lines), account (googledocs account id of davross846).
# Never use the default googledocs account: since 22 Oct 2026 it is the Going Pro account.
import json, os, re

HEB = re.compile('[א-ת]'); LAT = re.compile('[A-Za-z]')
INK, GREY, HFILL, LINE, WHITE, LINK = '1f1e1d', '52514f', 'f5f3ee', 'e8e5dd', 'ffffff', '1155cc'
OPTS = [('unans', 'Unanswered', 'f4cccc'), ('approve', 'Approve', 'd9ead3'), ('keep', 'Keep', 'cfe2f3'),
        ('change', 'Change', 'fff2cc'), ('discuss', 'Discuss', 'fce5cd')]
DD = 'kix.decision01'
# David, 15 Nov 2026 (Ruling 116): each row's dropdown offers its own two choices in plain words — the first does what
# the Alternative says (read back as Approve), the second leaves the book as it is (read back as Keep) — then Change
# and Discuss. A row gives them as `choices` [first, second]; a row without them keeps Approve / Keep. One dropdown
# definition per pair of choices; read_answers (wb.py) turns the chosen words back into Approve / Keep from the rows file.
import hashlib as _hl
def choices(row):
    c = row.get('choices') or ['Approve', 'Keep']
    return (c[0], c[1])
def def_id(pair):
    return DD if pair == ('Approve', 'Keep') else 'kix.dc' + _hl.md5('|'.join(pair).encode()).hexdigest()[:8]
def def_requests(pairs, have=()):
    out = []
    for pair in dict.fromkeys(pairs):
        i = def_id(pair)
        if i in have: continue
        labels = {'unans': 'Unanswered', 'approve': pair[0], 'keep': pair[1], 'change': 'Change', 'discuss': 'Discuss'}
        out.append({'createDropdownDefinition': {'dropdownDefinition': {'dropdownDefinitionId': i, 'dropdownDefinitionProperties': {
            'title': 'Decision', 'options': [{'optionId': 'dropdownItem.' + k, 'displayValue': labels[k], 'textStyle': {'backgroundColor': rgb(col)}} for k, _t, col in OPTS]}}}})
    return out
def find_all(o, key, out=None):
    out = set() if out is None else out
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key and isinstance(v, str): out.add(v)
            else: find_all(v, key, out)
    elif isinstance(o, list):
        for v in o: find_all(v, key, out)
    return out
EXPL_HEAD = ['ID', 'Where · what it is', 'As it stands', 'If changed', 'Back to the list']
EXPL_W = [40, 230, 230, 230, 80]


def rgb(h):
    return {'color': {'rgbColor': {'red': int(h[0:2], 16) / 255, 'green': int(h[2:4], 16) / 255, 'blue': int(h[4:6], 16) / 255}}}


def find_key(o, key):
    if isinstance(o, dict):
        if key in o: return o[key]
        for v in o.values():
            r = find_key(v, key)
            if r is not None: return r
    elif isinstance(o, list):
        for v in o:
            r = find_key(v, key)
            if r is not None: return r
    return None


def ptext(par):
    out = ''
    for x in par.get('paragraph', {}).get('elements', []):
        if 'textRun' in x: out += x['textRun']['content']
        elif 'dropdown' in x: out += ''
    return out


def progress_line(answers, when=None):
    """'Progress: 41 of 73 answered (Approve 7, Keep 33, Discuss 1) · open: B5, C2, D1–D18' (David, 9 Nov 2026)."""
    tot = len(answers); done = [a for a in answers if a['decision'] not in ('Unanswered', '', None)]
    cnt = {}
    for a in done: cnt[a['decision']] = cnt.get(a['decision'], 0) + 1
    open_ = [a['id'] for a in answers if a['decision'] in ('Unanswered', '', None)]
    runs, prev = [], None                       # B5, D1–D18: consecutive IDs of one Part as a range
    for i in open_:
        L, n = re.match(r'([A-Z]+)(\d+)', i).groups(); n = int(n)
        if prev and prev[0] == L and prev[2] == n - 1: prev[2] = n
        else: prev = [L, n, n]; runs.append(prev)
    rng = ', '.join(f'{L}{a}' if a == b else f'{L}{a}–{L}{b}' for L, a, b in runs)
    head = f'Progress{" (" + when + ")" if when else ""}: {len(done)} of {tot} answered'
    return head + (' (' + ', '.join(f'{k} {v}' for k, v in cnt.items()) + ')' if cnt else '') + (f' · open: {rng}' if rng else ' · all answered')

class Builder:
    """Build a review doc in phases. Builder.run(cfg) records each finished phase in /mnt/files/review_builds/,
    so a run that is stopped part-way picks up where it left off instead of making a second doc (David, 9 Nov 2026)."""
    def __init__(s, cfg):
        s.cfg = cfg; s.acc = cfg['account']; s.id = None; s.etab = None
        s.rows = cfg['rows']; s.by_part = {}
        for r in s.rows: s.by_part.setdefault(r['part'], []).append(r)

    def _make_plans(s):
        """The paragraphs of both tabs, in order (the styles phase needs them too, also after a resume)."""
        c = s.cfg
        s.plan = [('TITLE', c['title']), ('NORMAL', c['subtitle']), ('NORMAL', progress_line([{'id': r['id'], 'decision': 'Unanswered'} for r in s.rows]))] + c['how']
        for (letter, head, sent, hdr, w) in c['parts']:
            s.plan += [('H1', head), ('NORMAL', sent), ('table', (len(s.by_part[letter]) + 1, len(hdr)))]
        s.plan += [('H1', 'What the check found clean'), ('NORMAL', 'These need no decision.')] + [('CLEAN', x) for x in c['clean']]
        s.eplan = [('H1', 'Explanations'), ('NORMAL', 'Each ID in the list opens its explanation here, and ↩ Back returns you to the same row.')]
        for (letter, head, sent, hdr, w) in c['parts']:
            s.eplan += [('H2', head), ('table', (len(s.by_part[letter]) + 1, 5))]

    # ---- resumable run ----
    def _state_path(s):
        import hashlib
        key = hashlib.md5((s.cfg['title'] + json.dumps([r['id'] for r in s.rows])).encode()).hexdigest()[:12]
        os.makedirs('/mnt/files/review_builds', exist_ok=True)
        return f'/mnt/files/review_builds/{key}.json'

    def _save(s, done):
        json.dump({'title': s.cfg['title'], 'id': s.id, 'etab': s.etab, 'done': done}, open(s._state_path(), 'w'))

    @classmethod
    def run(cls, cfg, phases=('main', 'explanations', 'styles', 'links')):
        """Run (or resume) the build; call again after a stop. Returns verify()."""
        s = cls(cfg); st = json.load(open(s._state_path())) if os.path.exists(s._state_path()) else {'done': []}
        s.id, s.etab, done = st.get('id'), st.get('etab'), st.get('done', []); s._make_plans()
        if s.id and 'main' not in done:       # stopped inside phase 1: start that doc's body again
            body = s.body('t.0'); end = body[-1]['endIndex'] - 1
            if end > 1: s.batch([{'deleteContentRange': {'range': {'startIndex': 1, 'endIndex': end, 'tabId': 't.0'}}}])
        if s.id and 'main' in done and 'explanations' not in done:   # stopped inside phase 2: drop the half-made tab
            tabs = s.get()
            for k, t in tabs.items():
                if t['tabProperties'].get('title') == 'Explanations': s.batch([{'deleteTab': {'tabId': k}}])
            s.etab = None
        for ph in phases:
            if ph in done: continue
            getattr(s, 'phase_' + ph)(); done.append(ph); s._save(done)
        return s.verify() if all(p in done for p in ('main', 'explanations', 'styles', 'links')) else {'done': done, 'id': s.id}

    # ---- API ----
    def call(s, slug, args):
        r, e = run_composio_tool(slug, args, account=s.acc)
        if e: raise RuntimeError(f'{slug}: {str(e)[:1500]}')
        return r

    def batch(s, reqs, size=120000):
        chunk, n = [], 0
        for q in reqs:
            k = len(json.dumps(q, ensure_ascii=False))
            if chunk and n + k > size:
                s.call('GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT', {'document_id': s.id, 'edit_docs': chunk}); chunk, n = [], 0
            chunk.append(q); n += k
        if chunk: s.call('GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT', {'document_id': s.id, 'edit_docs': chunk})

    def get(s):
        r = s.call('GOOGLEDOCS_GET_DOCUMENT_BY_ID', {'id': s.id, 'includeTabsContent': True})
        tabs = find_key(r, 'tabs')
        return {t['tabProperties']['tabId']: t for t in tabs}

    def body(s, tab):
        return s.get()[tab]['documentTab']['body']['content']

    # ---- helpers ----
    @staticmethod
    def loc(i, tab): return {'index': i, 'tabId': tab}
    @staticmethod
    def end(tab): return {'segmentId': '', 'tabId': tab}
    @staticmethod
    def rng(a, b, tab): return {'startIndex': a, 'endIndex': b, 'tabId': tab}

    def tables(s, content): return [el for el in content if 'table' in el]

    def cell_start(s, cell): return cell['content'][0]['startIndex']

    def structure(s, tab, items):
        reqs = []
        for kind, x in items:
            if kind == 'table':
                reqs.append({'insertTable': {'endOfSegmentLocation': s.end(tab), 'rows': x[0], 'columns': x[1]}})
            else:
                reqs.append({'insertText': {'endOfSegmentLocation': s.end(tab), 'text': x + '\n'}})
        s.batch(reqs)

    def fill(s, tab, jobs):
        # jobs: (index, text, link) ; link is None, {'url':..} or {'heading':{..}}; or (index, None, 'chip')
        reqs = []
        for idx, text, link in sorted(jobs, key=lambda j: -j[0]):
            if link == 'chip':     # text holds the row's dropdown definition id
                reqs.append({'insertDropdown': {'location': s.loc(idx, tab), 'dropdownDefinitionId': text or DD, 'selectedOptionId': 'dropdownItem.unans'}})
                continue
            if not text: continue
            reqs.append({'insertText': {'location': s.loc(idx, tab), 'text': text}})
            if link:
                reqs.append({'updateTextStyle': {'range': s.rng(idx, idx + len(text.encode('utf-16-le')) // 2, tab),
                             'textStyle': {'link': link, 'foregroundColor': rgb(LINK), 'underline': True},
                             'fields': 'link,foregroundColor,underline'}})
        return reqs

    # ---- phase 1: main tab ----
    def phase_main(s):
        c = s.cfg
        if not s.id:
            r = s.call('GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN', {'title': c['title'], 'markdown_text': ''})
            s.id = find_key(r, 'documentId') or find_key(r, 'document_id')
            if hasattr(s, '_state_path'): s._save([])            # the doc exists from here on: a rerun reuses it
        s._make_plans()
        s.structure('t.0', s.plan)
        T = s.tables(s.body('t.0'))
        jobs = []
        for t, (letter, head, sent, hdr, w) in zip(T, c['parts']):
            rows = t['table']['tableRows']
            for j, h in enumerate(hdr): jobs.append((s.cell_start(rows[0]['tableCells'][j]), h, None))
            for i, row in enumerate(s.by_part[letter], 1):
                cells = rows[i]['tableCells']
                vals = [row['id']] + row['cells']
                for j, v in enumerate(vals): jobs.append((s.cell_start(cells[j]), v, None))
                if 'Sefaria' in hdr:   # parts about the text have a Sefaria link column; others (layout, front matter) don't
                    jobs.append((s.cell_start(cells[hdr.index('Sefaria')]), 'Sefaria', {'url': row['url']}))
                jobs.append((s.cell_start(cells[hdr.index('Decision')]), def_id(choices(row)), 'chip'))
        reqs = def_requests([choices(r) for r in c['rows']])
        s.batch(reqs + s.fill('t.0', jobs))
        return s.id

    # ---- phase 2: Explanations tab ----
    def phase_explanations(s):
        s.batch([{'addDocumentTab': {'tabProperties': {'title': 'Explanations'}}}])
        tabs = s.get()
        s.etab = [k for k, t in tabs.items() if t['tabProperties'].get('title') == 'Explanations'][0]
        s.structure(s.etab, s.eplan)
        T = s.tables(s.body(s.etab))
        jobs = []
        for t, (letter, *_rest) in zip(T, s.cfg['parts']):
            rows = t['table']['tableRows']
            for j, h in enumerate(EXPL_HEAD): jobs.append((s.cell_start(rows[0]['tableCells'][j]), h, None))
            for i, row in enumerate(s.by_part[letter], 1):
                cells = rows[i]['tableCells']
                for j, v in enumerate([row['id'], row['plain'], row['stands'], row['changed']]):
                    jobs.append((s.cell_start(cells[j]), v, None))
        s.batch(s.fill(s.etab, jobs))

    # ---- phase 3: styles ----
    def style_tab(s, tab, plan, size, heb_size, widths_of):
        content = s.body(tab)
        reqs = []
        last = content[-1]['endIndex']
        kinds = {}
        for k, x in plan:
            if k != 'table': kinds.setdefault(x, k)
        paras = [el for el in content if 'paragraph' in el]
        named, georgia, bullets = [], [], []
        for el in paras:
            t = ptext(el).rstrip('\n'); k = kinds.get(t)
            if k in ('TITLE', 'H1', 'H2'):
                ns = {'TITLE': 'TITLE', 'H1': 'HEADING_1', 'H2': 'HEADING_2'}[k]
                named.append({'updateParagraphStyle': {'range': s.rng(el['startIndex'], el['endIndex'], tab), 'paragraphStyle': {'namedStyleType': ns}, 'fields': 'namedStyleType'}})
                georgia.append((el['startIndex'], el['endIndex'] - 1))
            elif k in ('BULLET', 'CLEAN'):
                bullets.append((el['startIndex'], el['endIndex']))
        T = s.tables(content)
        idcells = []
        for t in T:
            for row in t['table']['tableRows'][1:]:
                c0 = row['tableCells'][0]['content'][0]; idcells.append((c0['startIndex'], c0['endIndex']))
        for a, b in idcells:
            named.append({'updateParagraphStyle': {'range': s.rng(a, b, tab), 'paragraphStyle': {'namedStyleType': 'HEADING_4', 'spaceAbove': {'magnitude': 0, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 0, 'unit': 'PT'}},
                                                   'fields': 'namedStyleType,spaceAbove,spaceBelow'}})
        reqs += named
        reqs.append({'updateTextStyle': {'range': s.rng(1, last - 1, tab), 'textStyle': {'weightedFontFamily': {'fontFamily': 'Inter', 'weight': 400}, 'bold': False, 'foregroundColor': rgb(INK), 'fontSize': {'magnitude': size, 'unit': 'PT'}},
                                         'fields': 'weightedFontFamily,bold,foregroundColor,fontSize'}})
        for a, b in georgia:
            reqs.append({'updateTextStyle': {'range': s.rng(a, b, tab), 'textStyle': {'weightedFontFamily': {'fontFamily': 'Georgia', 'weight': 400}, 'bold': False, 'foregroundColor': rgb(INK)}, 'fields': 'weightedFontFamily,bold,foregroundColor'}})
        # headings keep their named size: clear the explicit size on them
        for a, b in georgia:
            reqs.append({'updateTextStyle': {'range': s.rng(a, b, tab), 'textStyle': {}, 'fields': 'fontSize'}})
        for a, b in idcells:
            reqs.append({'updateTextStyle': {'range': s.rng(a, b - 1, tab), 'textStyle': {'italic': False}, 'fields': 'italic'}})
        border = {'color': rgb(LINE), 'width': {'magnitude': 1, 'unit': 'PT'}, 'dashStyle': 'SOLID'}
        for ti, t in enumerate(T):
            st = t['startIndex']; rows = t['table']['tableRows']; ncol = len(rows[0]['tableCells'])
            reqs.append({'updateTableCellStyle': {'tableStartLocation': s.loc(st, tab), 'tableCellStyle': {'backgroundColor': rgb(WHITE), 'borderLeft': border, 'borderRight': border, 'borderTop': border, 'borderBottom': border},
                                                  'fields': 'backgroundColor,borderLeft,borderRight,borderTop,borderBottom'}})
            reqs.append({'updateTableCellStyle': {'tableRange': {'tableCellLocation': {'tableStartLocation': s.loc(st, tab), 'rowIndex': 0, 'columnIndex': 0}, 'rowSpan': 1, 'columnSpan': ncol},
                                                  'tableCellStyle': {'backgroundColor': rgb(HFILL)}, 'fields': 'backgroundColor'}})
            for cell in rows[0]['tableCells']:
                a, b = cell['content'][0]['startIndex'], cell['content'][-1]['endIndex']
                reqs.append({'updateTextStyle': {'range': s.rng(a, b - 1, tab), 'textStyle': {'foregroundColor': rgb(GREY)}, 'fields': 'foregroundColor'}})
            for row in rows[1:]:
                for cell in row['tableCells']:
                    for p in cell['content']:
                        if 'paragraph' not in p: continue
                        tx = ptext(p)
                        if HEB.search(tx) and not LAT.search(tx):
                            reqs.append({'updateParagraphStyle': {'range': s.rng(p['startIndex'], p['endIndex'], tab), 'paragraphStyle': {'direction': 'RIGHT_TO_LEFT', 'alignment': 'START'}, 'fields': 'direction,alignment'}})
                            reqs.append({'updateTextStyle': {'range': s.rng(p['startIndex'], p['endIndex'] - 1, tab), 'textStyle': {'weightedFontFamily': {'fontFamily': 'Frank Ruhl Libre', 'weight': 400}, 'fontSize': {'magnitude': heb_size, 'unit': 'PT'}},
                                                             'fields': 'weightedFontFamily,fontSize'}})
            for ci, wd in enumerate(widths_of(ti)):
                reqs.append({'updateTableColumnProperties': {'tableStartLocation': s.loc(st, tab), 'columnIndices': [ci], 'tableColumnProperties': {'widthType': 'FIXED_WIDTH', 'width': {'magnitude': wd, 'unit': 'PT'}}, 'fields': 'width,widthType'}})
            reqs.append({'pinTableHeaderRows': {'tableStartLocation': s.loc(st, tab), 'pinnedHeaderRowsCount': 1}})
        # bullets: consecutive runs
        runs = []
        for a, b in bullets:
            if runs and runs[-1][1] == a: runs[-1][1] = b
            else: runs.append([a, b])
        for a, b in runs:
            reqs.append({'createParagraphBullets': {'range': s.rng(a, b, tab), 'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'}})
        return reqs, paras

    def phase_styles(s):
        widths = [p[4] for p in s.cfg['parts']]
        reqs, paras = s.style_tab('t.0', s.plan, 11, 12, lambda i: widths[i])
        for el in paras:  # bold words in "How to use"
            t = ptext(el)
            for w in s.cfg.get('bold', []):
                for m in re.finditer(re.escape(w), t):
                    if w in ('Approve', 'Keep', 'Change', 'Discuss') and m.start() != 0: continue
                    a = el['startIndex'] + len(t[:m.start()].encode('utf-16-le')) // 2
                    reqs.append({'updateTextStyle': {'range': s.rng(a, a + len(w), 't.0'), 'textStyle': {'bold': True}, 'fields': 'bold'}})
        reqs.append({'updateDocumentStyle': {'documentStyle': {'documentFormat': {'documentMode': 'PAGELESS'}}, 'fields': 'documentFormat', 'tabId': 't.0'}})
        s.batch(reqs)
        reqs, _ = s.style_tab(s.etab, s.eplan, 9, 11, lambda i: EXPL_W)
        reqs.append({'updateDocumentStyle': {'documentStyle': {'documentFormat': {'documentMode': 'PAGELESS'}}, 'fields': 'documentFormat', 'tabId': s.etab}})
        s.batch(reqs)

    # ---- phase 4: links both ways ----
    def heading_ids(s, content):
        out = {}
        for t in s.tables(content):
            for row in t['table']['tableRows'][1:]:
                p = row['tableCells'][0]['content'][0]
                out[ptext(p).strip()] = (p['paragraph']['paragraphStyle'].get('headingId'), row)
        return out

    def phase_links(s):
        tabs = s.get()
        M = s.heading_ids(tabs['t.0']['documentTab']['body']['content'])
        E = s.heading_ids(tabs[s.etab]['documentTab']['body']['content'])
        jm, je = [], []
        empty = lambda cell: not ''.join(ptext(p) for p in cell['content']).strip()     # a rerun does not link twice
        for rid, (hid, row) in M.items():
            if empty(row['tableCells'][-1]): jm.append((s.cell_start(row['tableCells'][-1]), f'Open {rid}', {'heading': {'id': E[rid][0], 'tabId': s.etab}}))
        for rid, (hid, row) in E.items():
            if empty(row['tableCells'][-1]): je.append((s.cell_start(row['tableCells'][-1]), f'↩ Back to {rid}', {'heading': {'id': M[rid][0], 'tabId': 't.0'}}))
        hdr = []
        for t in s.tables(tabs['t.0']['documentTab']['body']['content']):
            c = t['table']['tableRows'][0]['tableCells'][-1]
            if not ptext(c['content'][0]).strip(): hdr.append((s.cell_start(c), 'Explanation', None))
        s.batch(s.fill('t.0', jm + hdr))
        s.batch(s.fill(s.etab, je))

    # ---- add a Part to a doc David has already started answering (no rebuild, answers kept) ----
    def append_part(s, doc_id, part, rows, before='What the check found clean', how_find=None, how_add=None, before_expl=None):
        """part = [letter, heading, sentence, headers, widths]; rows as in listN_rows.json (all of that part).
        Inserts the heading, sentence and table on the main tab just before the paragraph `before`
        (or at the end), appends the matching Explanations section, fills chips (Unanswered), styles
        only the new tables and links the new rows both ways. Existing rows, chips and notes are not touched.
        how_find/how_add: optionally insert how_add right after the text how_find in the How-to-use paragraph.
        before_expl: the Explanations heading to insert the new section before (to replace a Part in place, keeping order)."""
        s.id = doc_id; s.rows = rows
        letter, head, sent, hdr, w = part
        L = lambda t: len(t.encode('utf-16-le')) // 2
        tabs = s.get()
        s.etab = [k for k, t in tabs.items() if t['tabProperties'].get('title') == 'Explanations'][0]
        dd = find_key(tabs['t.0'], 'dropdownDefinitionId') or DD
        content = tabs['t.0']['documentTab']['body']['content']
        P = next((el['startIndex'] for el in content if 'paragraph' in el and ptext(el).strip() == before), content[-1]['endIndex'] - 1)
        s.batch([{'insertText': {'location': s.loc(P, 't.0'), 'text': head + '\n' + sent + '\n'}},
                 {'insertTable': {'location': s.loc(P + L(head) + 1 + L(sent), 't.0'), 'rows': len(rows) + 1, 'columns': len(hdr)}}])
        hs, ss = P, P + L(head) + 1
        s.batch([{'updateParagraphStyle': {'range': s.rng(hs, hs + L(head) + 1, 't.0'), 'paragraphStyle': {'namedStyleType': 'HEADING_1'}, 'fields': 'namedStyleType'}},
                 {'updateParagraphStyle': {'range': s.rng(ss, ss + L(sent) + 1, 't.0'), 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT'}, 'fields': 'namedStyleType'}},
                 {'updateTextStyle': {'range': s.rng(hs, hs + L(head), 't.0'), 'textStyle': {'weightedFontFamily': {'fontFamily': 'Georgia', 'weight': 400}, 'bold': False, 'foregroundColor': rgb(INK)}, 'fields': 'weightedFontFamily,bold,foregroundColor,fontSize'}},
                 {'updateTextStyle': {'range': s.rng(ss, ss + L(sent), 't.0'), 'textStyle': {'weightedFontFamily': {'fontFamily': 'Inter', 'weight': 400}, 'bold': False, 'foregroundColor': rgb(INK), 'fontSize': {'magnitude': 11, 'unit': 'PT'}}, 'fields': 'weightedFontFamily,bold,foregroundColor,fontSize'}}])

        def new_table(content, after_text):
            seen = False
            for el in content:
                if 'paragraph' in el and ptext(el).strip() == after_text: seen = True
                elif seen and 'table' in el: return el
            raise RuntimeError('new table not found after ' + after_text)

        t = new_table(s.body('t.0'), sent)
        tr = t['table']['tableRows']; jobs = []
        for j, h in enumerate(hdr): jobs.append((s.cell_start(tr[0]['tableCells'][j]), h, None))
        for i, row in enumerate(rows, 1):
            cells = tr[i]['tableCells']
            for j, v in enumerate([row['id']] + row['cells']): jobs.append((s.cell_start(cells[j]), v, None))
            if 'Sefaria' in hdr: jobs.append((s.cell_start(cells[hdr.index('Sefaria')]), 'Sefaria', {'url': row['url']}))
            jobs.append((s.cell_start(cells[hdr.index('Decision')]), def_id(choices(row)) if row.get('choices') else dd, 'chip'))
        have = find_all(tabs, 'dropdownDefinitionId')
        s.batch(def_requests([choices(r) for r in rows if r.get('choices')], have) + s.fill('t.0', jobs))

        # Explanations: appended at the end of its tab
        econ0 = s.body(s.etab)
        PE = next((el['startIndex'] for el in econ0 if before_expl and 'paragraph' in el and ptext(el).strip() == before_expl), None)
        if PE is None:
            s.structure(s.etab, [('H2', head), ('table', (len(rows) + 1, 5))])
        else:
            s.batch([{'insertText': {'location': s.loc(PE, s.etab), 'text': head + '\n'}},
                     {'insertTable': {'location': s.loc(PE + L(head), s.etab), 'rows': len(rows) + 1, 'columns': 5}}])
        econ = s.body(s.etab)
        hp = [el for el in econ if 'paragraph' in el and ptext(el).strip() == head][-1]
        s.batch([{'updateParagraphStyle': {'range': s.rng(hp['startIndex'], hp['endIndex'], s.etab), 'paragraphStyle': {'namedStyleType': 'HEADING_2'}, 'fields': 'namedStyleType'}},
                 {'updateTextStyle': {'range': s.rng(hp['startIndex'], hp['endIndex'] - 1, s.etab), 'textStyle': {'weightedFontFamily': {'fontFamily': 'Georgia', 'weight': 400}, 'bold': False, 'foregroundColor': rgb(INK)}, 'fields': 'weightedFontFamily,bold,foregroundColor,fontSize'}}])
        et = new_table(s.body(s.etab), head); er = et['table']['tableRows']; jobs = []
        for j, h in enumerate(EXPL_HEAD): jobs.append((s.cell_start(er[0]['tableCells'][j]), h, None))
        for i, row in enumerate(rows, 1):
            for j, v in enumerate([row['id'], row['plain'], row['stands'], row['changed']]):
                jobs.append((s.cell_start(er[i]['tableCells'][j]), v, None))
        s.batch(s.fill(s.etab, jobs))

        # styles, new tables only
        for tab, after, widths, size, heb in [('t.0', sent, w, 11, 12), (s.etab, head, EXPL_W, 9, 11)]:
            tb = new_table(s.body(tab), after); s.batch(s._style_table(tab, tb, widths, size, heb))

        # links both ways, new rows only
        tabs = s.get()
        Mt = new_table(tabs['t.0']['documentTab']['body']['content'], sent)
        Et = new_table(tabs[s.etab]['documentTab']['body']['content'], head)
        M = s.heading_ids([Mt]); E = s.heading_ids([Et])
        jm = [(s.cell_start(row['tableCells'][-1]), f'Open {rid}', {'heading': {'id': E[rid][0], 'tabId': s.etab}}) for rid, (hid, row) in M.items()]
        je = [(s.cell_start(row['tableCells'][-1]), f'↩ Back to {rid}', {'heading': {'id': M[rid][0], 'tabId': 't.0'}}) for rid, (hid, row) in E.items()]
        s.batch(s.fill('t.0', jm)); s.batch(s.fill(s.etab, je))

        # optional: a sentence in How to use
        if how_find and how_add:
            for el in s.body('t.0'):
                tx = ptext(el)
                if 'paragraph' in el and how_find in tx and how_add not in tx:
                    at = el['startIndex'] + L(tx[:tx.index(how_find) + len(how_find)])
                    s.batch([{'insertText': {'location': s.loc(at, 't.0'), 'text': how_add}}]); break
        return s.verify()

    def _style_table(s, tab, t, widths, size, heb_size):
        reqs = []; st = t['startIndex']; rows = t['table']['tableRows']; ncol = len(rows[0]['tableCells'])
        reqs.append({'updateTextStyle': {'range': s.rng(st + 1, t['endIndex'] - 1, tab), 'textStyle': {'weightedFontFamily': {'fontFamily': 'Inter', 'weight': 400}, 'bold': False, 'foregroundColor': rgb(INK), 'fontSize': {'magnitude': size, 'unit': 'PT'}},
                                         'fields': 'weightedFontFamily,bold,foregroundColor,fontSize'}})
        for row in rows[1:]:
            c0 = row['tableCells'][0]['content'][0]
            reqs.append({'updateParagraphStyle': {'range': s.rng(c0['startIndex'], c0['endIndex'], tab), 'paragraphStyle': {'namedStyleType': 'HEADING_4', 'spaceAbove': {'magnitude': 0, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 0, 'unit': 'PT'}},
                                                  'fields': 'namedStyleType,spaceAbove,spaceBelow'}})
            reqs.append({'updateTextStyle': {'range': s.rng(c0['startIndex'], c0['endIndex'] - 1, tab), 'textStyle': {'italic': False}, 'fields': 'italic'}})
        border = {'color': rgb(LINE), 'width': {'magnitude': 1, 'unit': 'PT'}, 'dashStyle': 'SOLID'}
        reqs.append({'updateTableCellStyle': {'tableStartLocation': s.loc(st, tab), 'tableCellStyle': {'backgroundColor': rgb(WHITE), 'borderLeft': border, 'borderRight': border, 'borderTop': border, 'borderBottom': border},
                                              'fields': 'backgroundColor,borderLeft,borderRight,borderTop,borderBottom'}})
        reqs.append({'updateTableCellStyle': {'tableRange': {'tableCellLocation': {'tableStartLocation': s.loc(st, tab), 'rowIndex': 0, 'columnIndex': 0}, 'rowSpan': 1, 'columnSpan': ncol},
                                              'tableCellStyle': {'backgroundColor': rgb(HFILL)}, 'fields': 'backgroundColor'}})
        for cell in rows[0]['tableCells']:
            a, b = cell['content'][0]['startIndex'], cell['content'][-1]['endIndex']
            reqs.append({'updateTextStyle': {'range': s.rng(a, b - 1, tab), 'textStyle': {'foregroundColor': rgb(GREY)}, 'fields': 'foregroundColor'}})
        for row in rows[1:]:
            for cell in row['tableCells']:
                for p in cell['content']:
                    if 'paragraph' not in p: continue
                    tx = ptext(p)
                    if HEB.search(tx) and not LAT.search(tx):
                        reqs.append({'updateParagraphStyle': {'range': s.rng(p['startIndex'], p['endIndex'], tab), 'paragraphStyle': {'direction': 'RIGHT_TO_LEFT', 'alignment': 'START'}, 'fields': 'direction,alignment'}})
                        reqs.append({'updateTextStyle': {'range': s.rng(p['startIndex'], p['endIndex'] - 1, tab), 'textStyle': {'weightedFontFamily': {'fontFamily': 'Frank Ruhl Libre', 'weight': 400}, 'fontSize': {'magnitude': heb_size, 'unit': 'PT'}}, 'fields': 'weightedFontFamily,fontSize'}})
        for ci, wd in enumerate(widths):
            reqs.append({'updateTableColumnProperties': {'tableStartLocation': s.loc(st, tab), 'columnIndices': [ci], 'tableColumnProperties': {'widthType': 'FIXED_WIDTH', 'width': {'magnitude': wd, 'unit': 'PT'}}, 'fields': 'width,widthType'}})
        reqs.append({'pinTableHeaderRows': {'tableStartLocation': s.loc(st, tab), 'pinnedHeaderRowsCount': 1}})
        return reqs

    # ---- verify ----
    def verify(s):
        tabs = s.get(); bad = []
        norm = lambda x: re.sub(r'\s+', ' ', x).strip()
        main = tabs['t.0']['documentTab']['body']['content']; ex = tabs[s.etab]['documentTab']['body']['content']
        chips = 0; links_ok = 0
        M = s.heading_ids(main); E = s.heading_ids(ex)
        for r in s.rows:
            rid = r['id']
            if rid not in M or rid not in E: bad.append(('missing', rid)); continue
            cells = M[rid][1]['tableCells']
            got = [norm(''.join(ptext(p) for p in c['content'])) for c in cells]
            for j, v in enumerate(r['cells'], 1):
                if got[j] != norm(v): bad.append(('main', rid, j))
            dd = [x for c in cells for p in c['content'] for x in p.get('paragraph', {}).get('elements', []) if 'dropdown' in x]
            if len(dd) == 1 and dd[0]['dropdown'].get('dropdownProperties', {}).get('displayValue') == 'Unanswered': chips += 1
            else: bad.append(('chip', rid))
            ecells = E[rid][1]['tableCells']
            eg = [norm(''.join(ptext(p) for p in c['content'])) for c in ecells]
            for j, v in enumerate([r['plain'], r['stands'], r['changed']], 1):
                if eg[j] != norm(v): bad.append(('expl', rid, j))
            def link_of(cell):
                for p in cell['content']:
                    for x in p.get('paragraph', {}).get('elements', []):
                        l = x.get('textRun', {}).get('textStyle', {}).get('link')
                        if l: return l
            lm, le = link_of(cells[-1]), link_of(ecells[-1])
            if lm and lm.get('heading', {}).get('id') == E[rid][0] and le and le.get('heading', {}).get('id') == M[rid][0]: links_ok += 1
            else: bad.append(('link', rid, lm, le))
        return {'rows': len(s.rows), 'chips': chips, 'links_ok': links_ok, 'bad': bad[:20], 'n_bad': len(bad),
                'url': f'https://docs.google.com/document/d/{s.id}/edit', 'explanations_tab': s.etab}
