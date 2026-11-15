"""Compare the series skills saved in David's account with their copies in this repo (docs/skills/, and
docs/rules/CORE_SKILL.md for commentary-house-rules). Run at the start of every session (docs/HANDOFF.md, step 2).

    python3 -I scripts/skill_sync.py            # report: same / DIFFERS / missing
    python3 -I scripts/skill_sync.py --diff X   # show the differences for skill X
    python3 -I scripts/skill_sync.py --pull X   # copy the saved skill X (or 'all') into the repo

The saved skill is the one that runs, so it is the authority: a change made only in the repo copy does nothing until
David saves it from a propose_skills card. So: when a copy DIFFERS, either a proposal is waiting for David (say so and
leave it) or the repo copy is behind (pull). Never edit the saved skill files on disk; they are a read-only cache.
The saved skills are only on disk inside a Claude session (~/.claude/skills/synced/...); elsewhere this reports
"no saved skills here" and stops.
"""
import difflib, glob, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERIES = ['commentary-house-rules', 'commentary-book-build', 'commentary-audit', 'commentary-ideas-audit',
          'ibn-ezra-idea-notes', 'apply-review-decisions', 'review-list-google-doc', 'check-review-doc',
          'explain-commentary-row', 'commentary-onkelos-notes', 'commentary-misprint-finder',
          'commentary-key-insights-booklet', 'finalize-parasha', 'commentary-publish-pdfs', 'commentary-series-status',
          'commentary-sense-read', 'commentary-term-sheet', 'commentary-checks-upkeep']

def repo_path(name):
    return os.path.join(ROOT, 'docs', 'rules', 'CORE_SKILL.md') if name == 'commentary-house-rules' \
        else os.path.join(ROOT, 'docs', 'skills', name + '.md')

def saved_path(name):
    hits = glob.glob(os.path.expanduser(f'~/.claude/skills/synced/*/{name}/SKILL.md'))
    return hits[0] if hits else None

def norm(t):
    t = re.sub(r'^(name|description): "(.*)"$', r'\1: \2', t, flags=re.M)      # quoting of the frontmatter only
    return '\n'.join(l.rstrip() for l in t.strip().split('\n'))

def state(name):
    s, r = saved_path(name), repo_path(name)
    if not s: return 'not saved in the account'
    if not os.path.exists(r): return 'missing in repo'
    return 'same' if norm(open(s, encoding='utf-8').read()) == norm(open(r, encoding='utf-8').read()) else 'DIFFERS'

def main(a):
    if not glob.glob(os.path.expanduser('~/.claude/skills/synced/*/')):
        print('no saved skills here (run inside a Claude session)'); return 0
    if a[:1] == ['--diff']:
        n = a[1]; s, r = open(saved_path(n), encoding='utf-8').read(), open(repo_path(n), encoding='utf-8').read()
        for l in difflib.unified_diff(norm(r).split('\n'), norm(s).split('\n'), 'repo', 'saved', lineterm='', n=0): print(l)
        return 0
    if a[:1] == ['--pull']:
        for n in (SERIES if a[1] == 'all' else [a[1]]):
            if saved_path(n) and state(n) != 'same':
                shutil.copyfile(saved_path(n), repo_path(n)); print('pulled', n)
        return 0
    pend_f = os.path.join(ROOT, 'docs', 'skills', 'pending.json')        # {name: "date: what the proposal changes"}
    pend = json.load(open(pend_f, encoding='utf-8')) if os.path.exists(pend_f) else {}
    bad = 0
    for n in SERIES:
        st = state(n)
        if st == 'DIFFERS' and n in pend: st = f'DIFFERS: proposal waiting for David ({pend[n]})'
        elif st == 'same' and n in pend: st = 'same (saved: remove it from docs/skills/pending.json)'
        bad += not st.startswith('same') or 'remove' in st
        print(f'{n:34} {st}')
    print('all copies match' if not bad else f'{bad} to look at: a proposal waiting for David, or --pull')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
