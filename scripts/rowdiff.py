"""Turn a review row's Now / Alternative windows (plain text, markup removed) into an exact
(old, new) pair of the model's raw text, with just enough context to be unique.

  raw_pair(raw, now, alt, others=())  ->  (old, new)
raw     the model string the window was cut from (with {b}, {s} … markup)
now     the row's Now window; alt the Alternative window (same text with the change made)
others  further texts in which `old` must not occur (e.g. the other chapter files), so that an exact-once
        substitution in the source files is safe.
The changed stretch must not cross a markup tag; Hebrew is never typed: both sides come from the row
and the model.
"""
import re
import unicodedata as ud

TAG = re.compile(r'\{/?[a-z]+\}')


def plain_map(raw):
    """plain text and, for each plain character, its index in raw"""
    out, idx, i = [], [], 0
    while i < len(raw):
        m = TAG.match(raw, i)
        if m:
            i = m.end(); continue
        out.append(raw[i]); idx.append(i); i += 1
    return ''.join(out), idx


def core_diff(a, b):
    p = 0
    while p < min(len(a), len(b)) and a[p] == b[p]: p += 1
    s = 0
    while s < min(len(a), len(b)) - p and a[len(a) - 1 - s] == b[len(b) - 1 - s]: s += 1
    return p, len(a) - s, b[p:len(b) - s]


def raw_pair(raw, now, alt, others=()):
    import difflib
    raw = ud.normalize('NFC', raw); now = ud.normalize('NFC', now.strip()); alt = ud.normalize('NFC', alt.strip())
    plain, idx = plain_map(raw)
    k = plain.find(now)
    if k < 0 or plain.find(now, k + 1) >= 0:
        raise ValueError(f'Now window found {plain.count(now)} times: {now[:60]}')
    hunks = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, now, alt, autojunk=False).get_opcodes():
        if op == 'equal': continue
        pa, pb = k + i1, k + i2
        ra = idx[pa] if pa < len(idx) else len(raw)
        rb = (idx[pb - 1] + 1) if pb > pa else ra
        if TAG.search(raw[ra:rb]): raise ValueError(f'change crosses markup: {raw[ra:rb]!r}')
        hunks.append((pa, pb, ra, rb, alt[j1:j2]))
    if not hunks: raise ValueError('Now and Alternative are the same')
    PA, PB = hunks[0][0], hunks[-1][1]
    for w in range(2, 400):
        lo = max(0, PA - w); hi = min(len(plain), max(PB, PA + 1) + w)
        rlo = idx[lo]; rhi = idx[hi - 1] + 1
        old = raw[rlo:rhi]; new = old
        for pa, pb, ra, rb, ins in reversed(hunks):
            new = new[:ra - rlo] + ins + new[rb - rlo:]
        if raw.count(old) == 1 and not any(old in o for o in others) and old != new:
            return old, new
    raise ValueError('could not make the change unique')
