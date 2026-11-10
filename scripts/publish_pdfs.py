#!/usr/bin/env python3
"""Put each final parasha's book PDF in its own folder and join the full book. (The Key Insights booklets live in insights/.)
  python3 scripts/publish_pdfs.py            # copy + join
  python3 scripts/publish_pdfs.py --rebuild  # also rebuild each Key Insights booklet first
Per final parasha (book.json): <folder>/Ibn Ezra on Parashat <P>.pdf  (the final book pages)
                               insights/Ibn Ezra on Parashat <P> - Key Insights.pdf  (the booklet, rebuilt with --rebuild)
Front matter: front/Ibn Ezra on the Torah - Front Matter.pdf (pages i–v; built by bereshit/scripts/render.py ... frontonly).
Glossary: back/Ibn Ezra on the Torah - Glossary.pdf  (David, 9 Nov 2026: every term of the foot-of-page strip in the final
           parashot, alphabetical, numbered on from the last final page; rebuilt here each time by bereshit/scripts/render.py ... backonly).
Whole book: book/Ibn Ezra on the Torah - Bereshit to <last parasha>.pdf  (front matter first, then each final parasha, then the
           glossary; one file, replaced each time; built only from FINAL parashot)."""
import glob, json, os, shutil, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
B = json.load(open('book.json')); done = []
for p in B['parashot']:
    if not (p.get('stage') in ('final', 'audit') if p.get('stage') else str(p.get('status', '')).lower().startswith('final')): continue   # final or audit: both published (Ruling 105)
    name, folder = p['parasha'], p['folder']
    final = f'{folder}/drafts/Ibn Ezra {name} - final.pdf'
    assert os.path.exists(final), final
    if '--rebuild' in sys.argv: subprocess.check_call([sys.executable, 'insights/booklet.py', name])
    shutil.copy(final, f'{folder}/Ibn Ezra on Parashat {name}.pdf')
    done.append((name, final, p['last_page']))
os.makedirs('book', exist_ok=True)
for old in glob.glob('book/*.pdf'): os.remove(old)
out = f'book/Ibn Ezra on the Torah - {done[0][0]} to {done[-1][0]}.pdf'
FRONT = 'front/Ibn Ezra on the Torah - Front Matter.pdf'   # title page, preface, key to terms, note on the vowels (i–v)
assert os.path.exists(FRONT), FRONT
BACK = 'back/Ibn Ezra on the Torah - Glossary.pdf'      # the glossary of the foot-of-page terms, after the last final parasha
os.makedirs('back', exist_ok=True)
subprocess.check_call([sys.executable, 'scripts/render.py', 'data/model_final5.json', 'build/back.html', 'backonly'], cwd='bereshit')
out_b = subprocess.run([sys.executable, 'scripts/make_pdf.py', f'{ROOT}/bereshit/build/back.html', f'{ROOT}/bereshit/build/back.pdf',
                        'build/brep.json'], cwd='bereshit', check=True, capture_output=True, text=True).stdout
assert 'warnings 0' in out_b, out_b                                      # a glossary page that runs past the bottom stops the join
assert f"numbered {done[-1][2] + 1}–" in out_b, out_b                    # numbered on from the last final page
shutil.copy('bereshit/build/back.pdf', BACK)
subprocess.check_call(['pdfunite', FRONT] + [d[1] for d in done] + [BACK, out])
print('wrote', out, [d[0] for d in done])
