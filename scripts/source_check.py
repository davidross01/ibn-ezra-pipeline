#!/usr/bin/env python3
"""Every Hebrew span in the English commentary and the notes must come from a source (David, 28 Oct 2026:
Hebrew is copied by script, never typed).

A span is {h}…{/h}, {hb}…{/hb} or the Hebrew of {w}…{g}…{/g}{/w}. It is compared by consonants (vowels,
cantillation, maqaf and punctuation stripped; final letters folded; every form of the Name —
ה׳ ד׳ יי יְיָ יהוה — counted as one word) with:
  - this parasha's own verses and Hebrew commentary (the model),
  - every */src/*.json in the repo (Ibn Ezra, Rashi, Radak, Ramban, Rashbam, Onkelos, Genesis) and
    src/rashi_genesis.json (Rashi on all of Genesis), src/talmud.json (Talmud passages the notes quote),
    and Bereshit's data/ibnezra_he.json, radak_on_ie.json, ramban_on_ie.json, genesis_mam.json,
  - the whole Tanakh, src/tanakh.json (Miqra according to the Masorah, Sefaria).
A span joined by "…" is checked piece by piece. A word that matches only without a one- or two-letter
prefix (ו ה ב כ ל מ ש) still counts as traced. Not checked: letters and letter lists (א, ה ו י), root
patterns (ש־כ־ך, פ״א) and spans of one letter-pair.

Usage (repo root):  python3 -I scripts/source_check.py <folder> [--where]
check_all.py runs it as the check "Hebrew sources" (baseline-able, like the vowel hits).
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = {'bereshit': 'data/model_final5.json'}
EXTRA = ['bereshit/data/ibnezra_he.json', 'bereshit/data/radak_on_ie.json',
         'bereshit/data/ramban_on_ie.json', 'bereshit/data/genesis_mam.json']
FINAL = str.maketrans('ךםןףץ', 'כמנפצ')
MARKS = re.compile('[֑-ׇֽֿׁׂׅׄ]')
NAME_RE = re.compile(r"(?<![א-ת])([ובלמשכה]{0,2})(?:[הד]['׳’]|יְיָ|ייָ|יי|יהוה|יֱהֹוִה|יְהֹוָה|יְהוָה)(?![א-ת])")
PREFIX = re.compile('^[והבכלמש]{1,2}')
NAME = 'ΝΑΜΕ'


def norm_tokens(s):
    s = re.sub(r'<[^>]+>|&[a-z]+;|\{[^{}]*\}', ' ', s)
    s = MARKS.sub('', s)                      # vowels and cantillation, so the Name forms below match
    s = NAME_RE.sub(lambda m: ' ' + m.group(1) + NAME + ' ', s)
    s = s.replace('־', ' ').replace('׀', ' ')
    toks = re.findall('[א-ת]+(?:' + NAME + ')?|' + NAME, s)
    return [t.translate(FINAL) for t in toks]


def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values(): yield from strings(v)
    elif isinstance(o, list):
        for v in o: yield from strings(v)


def variants(w):
    """w and w without a one- or two-letter prefix (ו ה ב כ ל מ ש), keeping at least two letters."""
    out = {w}
    for k in (1, 2):
        if len(w) - k >= 2 and all(c in 'והבכלמש' for c in w[:k]):
            out.add(w[k:])
    return out


class Corpus:
    def __init__(self):
        self.docs, self.names, self.keys, self.idx, self.core = [], [], [], {}, {}

    def add(self, name, text, key=None):
        """key: (book, ch, v) of the verse the text belongs to, or None (not tied to one verse)."""
        t = norm_tokens(text)
        if not t: return
        d = len(self.docs); self.docs.append(t); self.names.append(name); self.keys.append(key)
        for i, w in enumerate(t):
            self.idx.setdefault(w, []).append((d, i))
            for c in variants(w):
                self.core.setdefault(c, []).append((d, i))

    @staticmethod
    def _eq(a, b):
        """Equal, or one is the other with a prefix in front (a quotation may drop or add a ו or ה)."""
        return a == b or b in variants(a) or a in variants(b)

    def find(self, toks, keys=None):
        """Source name where toks occur in a row (exactly, else with prefix slack), or None.
        keys: only look in texts tied to one of these verses."""
        for strict in (True, False):
            k = min(range(len(toks)), key=lambda j: len(self.idx.get(toks[j], [])) or 10**9)
            key = toks[k]
            cands = self.idx.get(key, []) if strict else set(self.core.get(key, [])) | {x for c in variants(key) for x in self.idx.get(c, [])}
            for d, i in cands:
                if keys is not None and self.keys[d] not in keys: continue
                s = i - k
                doc = self.docs[d]
                if s < 0 or s + len(toks) > len(doc): continue
                seg = doc[s:s + len(toks)]
                if strict and seg == toks: return self.names[d]
                if not strict and all(self._eq(a, b) for a, b in zip(seg, toks)): return self.names[d] + ' (prefix)'
        return None


def _vkey(k):
    m = re.match(r'(\d+):(\d+)', str(k))
    return ('Genesis', int(m.group(1)), int(m.group(2))) if m else None


def add_source(C, rel, d):
    """Add one source file, tying each text to its verse where the file's shape shows it."""
    if rel == 'src/tanakh.json':
        for book, chs in d.items():
            for c, vs in enumerate(chs, 1):
                for v, t in enumerate(vs, 1):
                    C.add(f'{book} {c}:{v}', t, (book, c, v))
        return
    name = rel.split('/')[-1].replace('.json', '').replace('_on_ie', '').replace('_genesis', '')
    name = {'ie': 'Ibn Ezra', 'ibnezra_he': 'Ibn Ezra'}.get(name, name.capitalize())
    if rel.endswith('rashi_genesis.json'):
        for c, vs in enumerate(d['text'], 1):
            for v, segs in enumerate(vs, 1):
                for t in strings(segs): C.add(f'Rashi {c}:{v}', t, ('Genesis', c, v))
        return
    if rel.endswith('ibnezra_he.json'):
        for c, vs in d.items():
            for v, segs in enumerate(vs, 1):
                for t in strings(segs): C.add(f'Ibn Ezra {c}:{v}', t, ('Genesis', int(c), v))
        return
    if rel.endswith('genesis_mam.json'):
        return                                         # Genesis is in src/tanakh.json
    if isinstance(d, list):
        for e in d:
            for t in strings(e.get('he', e)): C.add(f'{name} {e.get("ch")}:{e.get("v")}', t, ('Genesis', e.get('ch'), e.get('v')))
        return
    if isinstance(d, dict) and isinstance(d.get('text'), dict):
        d = d['text']
    for k, val in d.items():
        vk = _vkey(k)
        for t in strings(val.get('he', val) if isinstance(val, dict) else val):
            if re.search('[א-ת]', t): C.add(f'{name} {k.split("#")[0]}' if vk else rel, t, vk)


def build(folder, M):
    C = Corpus()
    for v in M['verses']:
        C.add(f'verse {v["ch"]}:{v["v"]}', v.get('he', ''), ('Genesis', v['ch'], v['v']))
    fix = re.compile(r'\(([^()]{1,40})\)(\s*)\[([^\]]{1,40})\]')
    for b in M['hc']:
        t, key = b.get('text', ''), ('Genesis', b.get('ch'), b.get('v'))
        C.add(f'Ibn Ezra {b.get("ch")}:{b.get("v")}', t, key)
        # a misprint (printed) [correction]: also each reading on its own, so a quotation of either traces
        if fix.search(t):
            C.add(f'Ibn Ezra {b.get("ch")}:{b.get("v")} (printed)', fix.sub(r'\1', t), key)
            C.add(f'Ibn Ezra {b.get("ch")}:{b.get("v")} (corrected)', fix.sub(r'\3', t), key)
    files = sorted(glob.glob(os.path.join(ROOT, '*', 'src', '*.json')))
    files += [os.path.join(ROOT, 'src', x) for x in ('rashi_genesis.json', 'talmud.json', 'tanakh.json')]
    files += [os.path.join(ROOT, p) for p in EXTRA]
    for f in files:
        rel = os.path.relpath(f, ROOT)
        base = os.path.basename(f)
        if not os.path.exists(f) or 'raw' in base or (base == 'tanakh.json' and rel != 'src/tanakh.json'):
            continue        # raw API answers repeat the cleaned files; the per-parasha tanakh.json copies are in src/
        add_source(C, rel, json.load(open(f, encoding='utf-8')))
    return C


BOOKS = None
REF = re.compile(r"\b((?:I{1,2} )?[A-Z][a-z]+(?: of [A-Z][a-z]+)?)\.? (\d+):(\d+)(?:[–-](\d+))?|"
                 r"(?:\(|\bon |\bverse |\bsee )(\d+):(\d+)|\bverses? (\d+)\b")


def near(ch, v, text, M_verses):
    """The verses a span at ch:v may quote without saying so: its verse and the two on each side, the
    verses named in the same comment or note, and every verse of the parasha (Ibn Ezra cites them often)."""
    keys = {('Genesis', ch, x) for x in range(v - 2, v + 3)}
    keys |= {('Genesis', a['ch'], a['v']) for a in M_verses}
    for m in REF.finditer(text):
        if m.group(1):
            book = {'Psalm': 'Psalms', 'Song': 'Song of Songs', 'Eccl': 'Ecclesiastes', 'Deut': 'Deuteronomy'}.get(m.group(1), m.group(1))
            a, b = int(m.group(2)), int(m.group(3)); e = int(m.group(4) or b)
            keys |= {(book, a, x) for x in range(b, e + 1)}
        elif m.group(5):
            keys.add(('Genesis', int(m.group(5)), int(m.group(6))))
        else:
            keys.add(('Genesis', ch, int(m.group(7))))
    return keys


SPAN = re.compile(r'\{(h|hb)\}(.*?)\{/\1\}|\{w\}(.*?)\{g\}', re.S)


def skip(piece_raw, toks):
    if not toks: return True
    if all(len(t) == 1 for t in toks): return True                      # letters, letter lists
    if re.search('[א-ת][֑-ׇ]*[־\\-–][א-ת][֑-ׇ]*[־\\-–]', piece_raw): return True   # ש־כ־ך
    if re.fullmatch(r"\s*[א-ת֑-ׇ]{1,3}[״\"'׳][א-ת֑-ׇ]{0,2}\s*", piece_raw): return True  # פ״א, ע״י
    if len(toks) == 1 and len(toks[0]) <= 2 and toks[0] != NAME: return True
    return False


def spans(M):
    for sec in ('ec', 'notes'):
        for b in M[sec]:
            t = b.get('text', '')
            for m in SPAN.finditer(t):
                raw = m.group(2) if m.group(2) is not None else m.group(3)
                yield sec, b.get('ch'), b.get('v'), raw, t


def check(folder, where=False):
    """Returns (not found, found only far away, pieces checked, where traced)."""
    M = json.load(open(os.path.join(ROOT, folder, MODEL.get(folder, 'data/model.json')), encoding='utf-8'))
    C = build(folder, M)
    missing, far, traced, n = [], [], {}, 0
    for sec, ch, v, raw, text in spans(M):
        keys = near(ch, v, text, M['verses'])
        for piece in re.split(r'…|\.\.\.', raw):
            toks = norm_tokens(piece)
            if skip(piece, toks): continue
            n += 1
            shown = re.sub(r'\{[^{}]*\}', '', piece).strip()[:80]
            src = C.find(toks, keys)
            if src is None:
                src = C.find(toks)
                if src is None:
                    missing.append(f'{sec} {ch}:{v}: {shown}')
                    continue
                if len(toks) > 1 or len(toks[0]) > 3:     # a short word is found somewhere in any case
                    far.append(f'{sec} {ch}:{v}: {shown}  — only in {src}')
            kind = re.sub(r' \d+:\d+.*| \(.*', '', src)
            kind = 'Tanakh' if kind in TANAKH_BOOKS else kind
            traced[kind] = traced.get(kind, 0) + 1
    return missing, far, n, traced


TANAKH_BOOKS = set(json.load(open(os.path.join(ROOT, 'src', 'tanakh.json'), encoding='utf-8')).keys()) - {'Genesis'}


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if not a: sys.exit(__doc__)
    missing, far, n, traced = check(a[0].strip('/'), '--where' in sys.argv)
    print(f'{n} Hebrew pieces checked: {len(missing)} not found in any source, {len(far)} found only far from the verse')
    if '--where' in sys.argv:
        for k, c in sorted(traced.items(), key=lambda x: -x[1]): print(f'   {c:5}  {k}')
    for h in missing: print('   NOT FOUND', h)
    for h in far: print('   FAR', h)
