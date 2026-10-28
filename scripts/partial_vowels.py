#!/usr/bin/env python3
"""List words of the Hebrew commentary that are pointed only in part (Vowels Review 1, E1: David,
28 Oct 2026 — every word is pointed in full; Sefaria's marks are a guide and are checked).
A word counts as partial when some of its letters carry vowels and another letter that needs one has
none. Letters that need no vowel: the last letter (unless it is ך with a kamatz, or a final ה/ח/ע with patach),
a ו or י used as a vowel letter (holam/shuruk on ו, or a י after hirik/tzere/segol), and a silent א or ה.
Skipped: abbreviations (with ' or "), references in {s}…{/s}, the printed form of a misprint (…) [ ].
Usage: python3 -I scripts/partial_vowels.py <folder>
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = {'bereshit': 'bereshit/data/model_final5.json'}
POINT = re.compile('[ְ-ׇּׁׂ]')
VOWEL = re.compile('[ְ-ׇֻ]')


def units(w):
    """[(letter, marks)]"""
    out = []
    for ch in w:
        if 'א' <= ch <= 'ת': out.append([ch, ''])
        elif out: out[-1][1] += ch
    return out


def partial(w):
    u = units(w)
    if len(u) < 2 or not any(VOWEL.search(m) for _, m in u): return False
    for i, (c, m) in enumerate(u):
        if VOWEL.search(m) or 'ּ' in m and c in 'ו': continue
        last = i == len(u) - 1
        if last: continue
        nc, nm = u[i + 1]
        if nc == 'ו' and ('\u05b9' in nm or '\u05ba' in nm or (nm.replace('\u05bc', '') == '' and '\u05bc' in nm)):
            continue                                   # the vowel is the holam/shuruk ו after it
        if c == 'ו' and ('ֹ' in m or 'ּ' in m): continue
        if c == 'ו' and i > 0 and 'ֹ' in u[i - 1][1]: continue          # holam written before the ו
        if c == 'י' and i > 0 and re.search('[ִֵֶַָ]', u[i - 1][1]): continue
        if c == 'א' and i > 0 and VOWEL.search(u[i - 1][1]): continue        # quiescent א
        if c == 'ה' and i > 0 and VOWEL.search(u[i - 1][1]) and i == len(u) - 2: continue
        if c == 'ו' and i > 0 and u[i - 1][0] == 'ו': continue
        return True
    return False


def scan(folder):
    M = json.load(open(os.path.join(ROOT, MODEL.get(folder, f'{folder}/data/model.json')), encoding='utf-8'))
    hits = []
    for b in M['hc']:
        t = b.get('text', '')
        t = re.sub(r'\{s\}.*?\{/s\}', ' ', t)
        t = re.sub(r'\([^()]{1,40}\)\s*(?=\[)', ' ', t)
        for w in re.findall(r"[א-תְ-ׇ]+['\"׳״]?[א-תְ-ׇ]*", t.replace('־', ' ')):
            if re.search('[\'"׳״]', w): continue
            if partial(w): hits.append((b['ch'], b['v'], w))
    return hits


if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(__doc__)
    h = scan(sys.argv[1])
    print(len(h), 'partly pointed words')
    for x in h: print(f'  {x[0]}:{x[1]}  {x[2]}')
