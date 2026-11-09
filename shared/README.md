# Shared build scripts (since 9 Nov 2026)

One copy of the scripts, fonts and hyphenation library for every parasha from Noach on. Each parasha's
`scripts/*.py` is a small stub that runs the shared script on that parasha's folder (data/, build/, parasha.json),
so every command works as before: `cd toledot && python3 scripts/render.py data/model.json build/book.html`.

Proof before the switch (9 Nov 2026, Chromium 153.0.8010.12): Noach, Lech Lecha, Vayera, Chayei Sarah and Toledot were
each built with their own scripts and with these; the HTML was the same apart from the font folder's path, the layout
reports were the same, and all 152 pages were the same picture for picture (pdftoppm, 60 dpi).

Bereshit keeps its own scripts: it opens the volume (title page, front matter) and its book.css, layout.js and
render.py differ for that. A new parasha copies a parasha folder's `scripts/` stubs, not the shared files.
A change here changes every parasha's next build: make it only with a row David has answered, and rebuild each
parasha it touches with the same Chromium version (book.json "chromium").
