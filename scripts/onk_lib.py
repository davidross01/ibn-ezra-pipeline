"""Onkelos lines in the notes (David, Oct 2026: Onkelos is a main commentator, on par with Rashi).

Each parasha has work/onkelos.py with entries:
  A(ref, text, before=None)  add a line to the verse's note: before `before` if given, else before the
                             first "Rashi" sentence, else before the {i}Text.{/i} line, else at the end.
                             If the verse has no note, a new note is made with `text` (give a lemma then).
  S(ref, old, new)           replace wording in the verse's existing note (old must occur exactly once).
In the text, {o:i-j} (or {o:i}) prints words i..j of Onkelos on that verse, copied from src/onkelos.json
(Sefaria, "Targum Onkelos, vocalized according to the Yemenite Taj", CC-BY-SA); {o:ch:v:i-j} another verse.
The Name, written יְיָ in the Targum, prints as ה׳, as the Name is shown everywhere in the English.
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
