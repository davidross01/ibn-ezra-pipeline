#!/usr/bin/env python3
"""Put each final parasha's book PDF in its own folder and join the full book. (The Key Insights booklets live in insights/.)
  python3 scripts/publish_pdfs.py            # copy + join
  python3 scripts/publish_pdfs.py --rebuild  # also rebuild each Key Insights booklet first
Per final parasha (book.json): <folder>/Ibn Ezra on Parashat <P>.pdf  (the final book pages)
                               insights/Ibn Ezra on Parashat <P> - Key Insights.pdf  (the booklet, rebuilt with --rebuild)
Whole book: book/Ibn Ezra on the Torah - Bereshit to <last parasha>.pdf  (one file, replaced each time; built only from FINAL parashot)."""
import glob, json, os, shutil, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
B = json.load(open('book.json')); done = []
for p in B['parashot']:
    if not p['status'].startswith('final'): continue
    name, folder = p['parasha'], p['folder']
    final = f'{folder}/drafts/Ibn Ezra {name} - final.pdf'
    assert os.path.exists(final), final
    if '--rebuild' in sys.argv: subprocess.check_call([sys.executable, 'insights/booklet.py', name])
    shutil.copy(final, f'{folder}/Ibn Ezra on Parashat {name}.pdf')
    done.append((name, final, p['last_page']))
os.makedirs('book', exist_ok=True)
for old in glob.glob('book/*.pdf'): os.remove(old)
out = f'book/Ibn Ezra on the Torah - {done[0][0]} to {done[-1][0]}.pdf'
subprocess.check_call(['pdfunite'] + [d[1] for d in done] + [out])
print('wrote', out, [d[0] for d in done])
