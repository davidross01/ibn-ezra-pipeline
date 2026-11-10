"""The rulings log: every ruling of David's, numbered, newest first, with the rulings that replaced older ones on top.
Writes docs/RULINGS.md (the Google Doc "03 Rulings"); never edit that file by hand.

    python3 -I scripts/rulings.py           # rewrite docs/RULINGS.md
    python3 -I scripts/rulings.py --check   # CI: RULINGS.md is current, every ruling number a rule cites exists, every
                                            # ruling points to a rule that exists, no rule file carries a date, and
                                            # no rule or skill copy still points to a superseded model

The data: docs/rules/rulings.json — one entry per ruling {n, date "YYYY-MM-DD" or "YYYY-MM", rule "<file> <number>"
(or "replaced", or "<file>, glossary" / "<file>, For Claude"), ruling, words (David's own words), from (where he said
it)} — and docs/rules/superseded.json (the replaced rulings, with the "stale" phrases that would point to the old way).
The rules themselves are in docs/rules/*.md, each "### N. Title", citing its rulings as "Ruling 12" / "Rulings 4, 5";
the dates live only here (David, 10 Nov 2026).

When David gives a new ruling: the core skill, "A new rule from David".
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = os.path.join(ROOT, 'docs', 'rules')
OUT = os.path.join(ROOT, 'docs', 'RULINGS.md')
MON = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
# the rule files and their documents in the Drive folder "-03 How it is made" (docs/handbook.json)
DOC = {'translation': '04 Translation', 'grammar': '05 Grammar', 'hebrew': '06 Hebrew', 'notes': '07 Notes',
       'review': '08 Review', 'review_doc': '09 Review doc', 'page': '10 Page', 'sources': '11 Sources'}
DATED = re.compile(r'\b\d{1,2} (?:Sep|Oct|Nov|Dec)\w* 20\d\d|\b(?:Sep|Oct|Nov|Dec)\w* 20\d\d\b')
CITE = re.compile(r'Rulings? (\d+(?:, \d+)*)')


def load():
    R = json.load(open(os.path.join(RULES, 'rulings.json'), encoding='utf-8'))
    S = json.load(open(os.path.join(RULES, 'superseded.json'), encoding='utf-8'))
    return R, S


def fmt(d):
    p = d.split('-')
    return f'{int(p[2])} {MON[int(p[1])]} {p[0]}' if len(p) == 3 else f'{MON[int(p[1])]} {p[0]}'


def where(rule):
    if rule == 'replaced':
        return 'replaced: see above'
    out = []
    for part in rule.split('; '):
        f, _, rest = part.partition(' ')
        f = f.rstrip(',')
        out.append(f'{DOC.get(f, f)}, ' + (f'rule {rest}' if rest[:1].isdigit() else rest.lstrip(', ')))
    return '; '.join(out)


def render():
    R, S = load()
    L = ['# Rulings', '',
         'Every ruling you have given, numbered, newest first: when, what, your own words where there are any, and '
         'where you said it. The rules cite these numbers ("Ruling 12"). Read **Replaced rulings** first: a ruling '
         'listed there no longer holds, and nothing may follow it. (Made by `scripts/rulings.py` from '
         'docs/rules/rulings.json; not edited by hand.)', '',
         '## Replaced rulings', '', '| Date | No longer | Now | Where |', '|---|---|---|---|']
    L += [f"| {s['date']} | {s['old']} | {s['new']} | {s['where']} |" for s in S]
    L += ['', '## Every ruling, newest first', '', '| No. | Date | Ruling | Your words | From | Rule |',
          '|---|---|---|---|---|---|']
    key = lambda r: (r['date'] + '-00')[:10]
    for r in sorted(R, key=lambda r: (key(r), r['n']), reverse=True):
        w = f"“{r['words']}”" if r['words'] else ''
        L.append(f"| {r['n']} | {fmt(r['date'])} | {r['ruling']} | {w} | {r['from']} | {where(r['rule'])} |")
    return '\n'.join(x.replace('\n', ' ') for x in L) + '\n'


def rule_numbers(f):
    return [int(n) for n in re.findall(r'^### (\d+)\. ', open(f, encoding='utf-8').read(), re.M)]


def problems():
    R, S = load()
    bad, ns = [], {r['n'] for r in R}
    if sorted(ns) != list(range(1, len(R) + 1)):
        bad.append('rulings.json: the numbers are not 1..N without gaps')
    for f in sorted(glob.glob(os.path.join(RULES, '*.md'))):
        name = os.path.basename(f)[:-3]
        if name == 'CORE_SKILL':
            continue
        text = open(f, encoding='utf-8').read()
        nums = rule_numbers(f)
        if nums != list(range(1, len(nums) + 1)):
            bad.append(f'docs/rules/{name}.md: rules are not numbered 1..N in order')
        for i, l in enumerate(text.split('\n'), 1):
            if DATED.search(l):
                bad.append(f'docs/rules/{name}.md:{i}: a date in a rule (dates belong in rulings.json): {DATED.search(l).group(0)}')
            for m in CITE.finditer(l):
                for x in m.group(1).split(', '):
                    if int(x) not in ns:
                        bad.append(f'docs/rules/{name}.md:{i}: cites Ruling {x}, which does not exist')
    for r in R:
        for part in r['rule'].split('; '):
            f, _, rest = part.partition(' ')
            f = f.rstrip(',')
            if f == 'replaced':
                continue
            path = os.path.join(RULES, f + '.md')
            if not os.path.exists(path):
                bad.append(f"rulings.json {r['n']}: no rule file {f}.md"); continue
            for x in re.findall(r'\d+', rest if rest[:1].isdigit() else ''):
                if int(x) not in rule_numbers(path):
                    bad.append(f"rulings.json {r['n']}: {f}.md has no rule {x}")
    return bad


CORE = os.path.join(RULES, 'CORE_SKILL.md')


def core_index():
    """The index at the end of the core skill: every rule's number and title, one line per file."""
    out = []
    for f in DOC:
        path = os.path.join(RULES, f + '.md')
        titles = re.findall(r'^### (\d+)\. (.+)$', open(path, encoding='utf-8').read(), re.M)
        out.append(f'- **{f}.md** ({DOC[f]}): ' + ' · '.join(f'{n} {t}' for n, t in titles))
    return '\n'.join(out)


def core_text():
    t = open(CORE, encoding='utf-8').read()
    a, b = t.index('<!-- index -->') + len('<!-- index -->'), t.index('<!-- /index -->')
    return t[:a] + '\n' + core_index() + '\n' + t[b:]


def stale_hits():
    _, S = load()
    phrases = [p for s in S for p in s.get('stale', [])]
    files = glob.glob(os.path.join(RULES, '*.md')) + glob.glob(os.path.join(ROOT, 'docs', 'skills', '*.md')) \
        + [os.path.join(ROOT, 'docs', 'HANDOFF.md')]
    hits = []
    for f in files:
        for i, l in enumerate(open(f, encoding='utf-8'), 1):
            for p in phrases:
                if p.lower() in l.lower() and 'superseded' not in l.lower():
                    hits.append(f'{os.path.relpath(f, ROOT)}:{i}: still says "{p}" (superseded)')
    return hits


if __name__ == '__main__':
    text = render()
    if sys.argv[1:] == ['--check']:
        bad = []
        if not os.path.exists(OUT) or open(OUT, encoding='utf-8').read() != text:
            bad.append('docs/RULINGS.md is out of date: run python3 -I scripts/rulings.py')
        if open(CORE, encoding='utf-8').read() != core_text():
            bad.append('docs/rules/CORE_SKILL.md: the index of the rules is out of date: run python3 -I scripts/rulings.py')
        bad += problems() + stale_hits()
        print('\n'.join(bad) or 'rulings: current; every citation and rule found; no dates in the rules; no superseded model pointed to')
        sys.exit(1 if bad else 0)
    open(OUT, 'w', encoding='utf-8').write(text)
    core = core_text()
    open(CORE, 'w', encoding='utf-8').write(core)
    print(f'{OUT}: {text.count(chr(10))} lines; the core skill\'s index rewritten')
    for h in problems() + stale_hits():
        print(h)
