"""Which parashot the GitHub check runs on (Nov 2026: one job instead of seven, to save Actions minutes).
    python3 -I scripts/ci_changed.py <before-sha> <sha>   -> prints the parasha folders to check, one per line
A push that touches only one parasha's folder checks that parasha; a push that touches shared code, rules, book.json
or the sources checks every parasha; a weekly or hand-started run passes "all". Folders come from book.json."""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDERS = [p['folder'] for p in json.load(open(os.path.join(ROOT, 'book.json'), encoding='utf-8'))['parashot']]
args = sys.argv[1:]
if not args or args[0] == 'all' or set(args[0]) == {'0'}:
    print('\n'.join(FOLDERS)); sys.exit()
try:
    files = subprocess.check_output(['git', 'diff', '--name-only', args[0], args[1]], cwd=ROOT, text=True).split()
except subprocess.CalledProcessError:
    print('\n'.join(FOLDERS)); sys.exit()
top = {f.split('/')[0] for f in files}
if top & {'shared', 'scripts', 'src', 'docs', 'book.json', 'review_grammar', 'bereshit', '.github'}:
    print('\n'.join(FOLDERS)); sys.exit()
print('\n'.join(f for f in FOLDERS if f in top))
