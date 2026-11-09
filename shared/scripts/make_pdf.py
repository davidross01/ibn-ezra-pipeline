# Load the rendered HTML in Chromium, run the planner, print to PDF.
import json, sys, time
from playwright.sync_api import sync_playwright
src = sys.argv[1]; out = sys.argv[2]; rep = sys.argv[3] if len(sys.argv) > 3 else out + '.json'
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 664, 'height': 1000})
    msgs = []
    pg.on('console', lambda m: msgs.append(m.text))
    t0 = time.time()
    pg.goto('file://' + src)
    pg.wait_for_function("document.title === 'READY'", timeout=600000)
    L = pg.evaluate('window.__LAYOUT')
    print('layout', round(time.time() - t0, 1), 's')
    if 'error' in L:
        print(L['error']); sys.exit(1)
    pg.pdf(path=out, width='664px', height='1000px', print_background=True, prefer_css_page_size=True)
    L['browser'] = b.version   # Chromium version: page breaks depend on it (check_all compares with book.json)
    b.close()
L['console'] = msgs
json.dump(L, open(rep, 'w'), ensure_ascii=False, indent=1)
print('chromium', L['browser'])
print('pages', L['pages'], f"(numbered {L.get('first_page',1)}–{L.get('last_page',L['pages'])})", 'warnings', len(L['log']))
for l in L['log'][:40]: print(' ', l)
