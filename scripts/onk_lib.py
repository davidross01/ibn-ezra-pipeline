"""Onkelos lines in the notes (David, Oct 2026: Onkelos is a main commentator, on par with Rashi).

Each parasha has work/onkelos.py with entries:
  A(ref, text, before=None)  add a line to the verse's note: before `before` if given, else before the
                             first "Rashi" sentence, else before the {i}Text.{/i} line, else at the end.
                             If the verse has no note, a new note is made with `text` (give a lemma then).
  S(ref, old, new)           replace wording in the verse's existing note (old must occur exactly once).
In the text, {o:i-j} (or {o:i}) prints words i..j of Onkelos on that verse, copied from src/onkelos.json
(Sefaria, "Targum Onkelos, vocalized according to the Yemenite Taj", CC-BY-SA); {o:ch:v:i-j} another verse.
The Name, written יְיָ in the Targum, prints as ה׳, as the Name is shown everywhere in the English.

Scripture quotations (David, 28 Oct 2026: Hebrew in the notes is copied by script from Chayei Sarah on):
{q:Book ch:v:i-j} (or {q:Book ch:v:i}) prints words i..j of that verse from src/tanakh.json (Miqra according
to the Masorah, Sefaria), with the Masorah's vowels and dagesh, without cantillation or meteg; a maqaf-joined
group counts as one word and keeps its maqaf. A ketiv/qere is one word and prints the qere. The Name (יְהֹוָה,
with or without a prefix) prints as ה׳; a Name read Elohim (יֱהֹוִה) stops the build: ask David.
Book names as in src/tanakh.json ("Genesis", "I Samuel", "Song of Songs"). Words are counted as in
`python3 -I scripts/onk_lib.py words "Isaiah 1:1"`, which prints the verse numbered word by word.
resolve_all(text, ref) resolves both kinds of marker; assemble.py runs it on every comment and note.
"""
import json, re, importlib.util

ENTRIES = []
def A(ref, text, before=None, lemma=None): ENTRIES.append(('A', tuple(ref), text, (before, lemma)))
def S(ref, old, new): ENTRIES.append(('S', tuple(ref), old, new))

NAME = {'יְיָ': 'ה׳', 'וַייָ': 'וַה׳'}

def words(onk, ch, v):
    return onk[f'{ch}:{v}'].replace('׃', '').split()

def resolve(text, ref, onk):
    def rep(m):
        parts = m.group(1).split(':')
        ch, v = (int(parts[0]), int(parts[1])) if len(parts) == 3 else ref
        rng = parts[-1]
        i, j = (rng.split('-') + [rng])[:2]
        w = words(onk, ch, v)[int(i) - 1:int(j)]
        if not w or int(j) > len(words(onk, ch, v)): raise SystemExit(f'onkelos range {m.group(0)} out of verse {ch}:{v}')
        bad = [x for x in w if 'ייָ' in x and x not in NAME]
        if bad: raise SystemExit(f'{m.group(0)} at {ch}:{v} quotes the Name with a prefix ({bad[0]}); end the quotation before it')
        w = [NAME.get(x, x) for x in w]
        return '{h}' + ' '.join(w) + '{/h}'
    out = re.sub(r'\{o:([\d:]+(?:-\d+)?)\}', rep, text)
    out = out.replace('Hashem', 'H{sci}ashem{/sci}')
    return out

def load(path):
    ENTRIES.clear()
    spec = importlib.util.spec_from_file_location('onk_entries', path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return list(ENTRIES)

def insert_line(note, line, before):
    if before == 'END':
        m = re.search(r'\{i\}Text\.\{/i\}', note)
        return note[:m.start()] + line + ' ' + note[m.start():] if m else note.rstrip() + ' ' + line
    if before:
        if note.count(before) != 1: raise SystemExit(f'anchor not once: {before!r}')
        k = note.index(before); return note[:k] + line + ' ' + note[k:]
    m = re.search(r'(?:(?<=^)|(?<=[.”?!)}] ))Rashi\b', note)
    if not m: m = re.search(r'\{i\}Text\.\{/i\}', note)
    if m: return note[:m.start()] + line + ' ' + note[m.start():]
    return note.rstrip() + ' ' + line

def apply(N, entries_path, onk_path):
    """N: list of ((ch, v), text) in authored order. Returns a new list."""
    import glob, os
    onk = {}
    for f in glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '*', 'src', 'onkelos.json')):
        onk.update(json.load(open(f, encoding='utf-8'))['text'])
    onk.update(json.load(open(onk_path, encoding='utf-8'))['text'])
    N = [[tuple(k), t] for k, t in N]
    log = []
    for kind, ref, a, b in load(entries_path):
        idx = [i for i, (k, _) in enumerate(N) if k == ref]
        if kind == 'S':
            new = resolve(b, ref, onk); hits = [i for i in idx if a in N[i][1]]
            if len(hits) != 1 or N[hits[0]][1].count(a) != 1: raise SystemExit(f'S {ref}: old text not found once: {a!r}')
            N[hits[0]][1] = N[hits[0]][1].replace(a, new); log.append((ref, 'S'))
        else:
            b, lem = b
            line = resolve(a, ref, onk)
            if lem:
                idx = [i for i in idx if N[i][1].startswith('{hb}' + lem)]
                if len(idx) != 1: raise SystemExit(f'A {ref}: lemma {lem!r} matches {len(idx)} notes')
            if not idx: N.append([ref, line]); log.append((ref, 'new')); continue
            tgt = idx[0]
            if b and b != 'END':
                hits = [i for i in idx if b in N[i][1]]
                if len(hits) != 1: raise SystemExit(f'A {ref}: anchor {b!r} not in one note')
                tgt = hits[0]
            else:
                r = [i for i in idx if re.search(r'(?:^|[.”?!)}] )Rashi\b', N[i][1])]
                if r: tgt = r[0]
            N[tgt][1] = insert_line(N[tgt][1], line, b); log.append((ref, 'A'))
    return [(tuple(k), t) for k, t in N], log


# ---------------------------------------------------------------- {q:} Scripture quotations
_TANAKH = None
_CANT = re.compile('[\u0591-\u05af\u05bd\u034f]')      # cantillation, meteg, grapheme joiner


def tanakh():
    global _TANAKH
    if _TANAKH is None:
        import os
        p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'tanakh.json')
        _TANAKH = json.load(open(p, encoding='utf-8'))
    return _TANAKH


def verse_words(book, ch, v):
    T = tanakh()
    if book not in T: raise SystemExit(f'{{q:}} unknown book {book!r} (names as in src/tanakh.json)')
    try: t = T[book][ch - 1][v - 1]
    except IndexError: raise SystemExit(f'{{q:}} no verse {book} {ch}:{v}')
    t = re.sub(r'&[a-z]+;|\{[פס]\}', ' ', t)
    t = re.sub(r'\(([^()]*)\)\s*\[([^\]]*)\]', lambda m: m.group(2), t)     # ketiv/qere: the qere
    t = _CANT.sub('', t).replace('׀', ' ').replace('׃', '')
    return t.split()


def _name(w):
    bare = re.sub('[\u05b0-\u05c7]', '', w)
    m = re.fullmatch('([ובלמשכה]*)יהוה', bare)
    if not m: return w
    if 'ֱ' in w and w.endswith('ִה'):
        raise SystemExit(f'{{q:}} quotes the Name read Elohim ({w}); ask David how to print it')
    k = 0; n = len(m.group(1))
    while n:                                                   # keep the prefix letters with their vowels
        if '\u05d0' <= w[k] <= '\u05ea': n -= 1
        k += 1
        while k < len(w) and not ('\u05d0' <= w[k] <= '\u05ea'): k += 1
    return w[:k] + 'ה׳'


def resolve_q(text):
    def rep(m):
        book, ch, v, i, j = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5) or m.group(4))
        w = verse_words(book, ch, v)
        if not (1 <= i <= j <= len(w)): raise SystemExit(f'{m.group(0)}: the verse has {len(w)} words')
        return '{h}' + ' '.join(_name(x) for x in w[i - 1:j]) + '{/h}'
    return re.sub(r'\{q:([^{}:]+?) (\d+):(\d+):(\d+)(?:-(\d+))?\}', rep, text)


_ONK = None


def resolve_all(text, ref):
    """Both markers in one comment or note: {q:…} from the Tanakh, {o:…} from Onkelos (all */src/onkelos.json)."""
    global _ONK
    if '{q:' in text: text = resolve_q(text)
    if '{o:' in text:
        if _ONK is None:
            import glob, os
            _ONK = {}
            for f in glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '*', 'src', 'onkelos.json')):
                _ONK.update(json.load(open(f, encoding='utf-8'))['text'])
        text = resolve(text, ref, _ONK)
    if re.search(r'\{[oq]:', text): raise SystemExit(f'{ref}: a marker was not resolved: {text[:80]}')
    return text


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 3 and sys.argv[1] == 'words':
        m = re.fullmatch(r'(.+) (\d+):(\d+)', sys.argv[2])
        for k, w in enumerate(verse_words(m.group(1), int(m.group(2)), int(m.group(3))), 1): print(k, w)
    else:
        print(__doc__)
