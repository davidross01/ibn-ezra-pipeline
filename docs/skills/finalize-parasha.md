---
name: finalize-parasha
description: "Make a parasha of David's Ibn Ezra series final in one chain: apply the last answers, final build and checks, book.json, key to terms, front matter, parts export, booklets, full book, Drive folder, archiving."
---

# Finalize a parasha (the whole chain)

Use when David says a parasha's reviews are finished and agrees to make it final, or says "apply and make it final". This is the one finishing sequence: apply-review-decisions (for the last round), commentary-publish-pdfs and the Drive refresh are steps of it, so run them from here rather than separately. Load **commentary-house-rules** (and docs/rules/review.md, page.md) and **commentary-book-build** first. Repo: davidross01/ibn-ezra-commentary at /home/claude/ibn-ezra-commentary (`git pull` first).

## 0. Before starting
- Status in one call: `review_status()` in the workbench (scripts/workbench/wb.py), `git pull`, then `python3 -I scripts/series_status.py --checks`. Its NEXT list also names review docs that are applied but not archived, with links. Every review doc of this parasha must be fully answered (or applied); Discuss rows settled (chat_answers.json). An unanswered grammar-sheet tab counts as "kept as drafted" only if David says so.
- Ask David with checkboxes, in one question set: make it final now? any follow-on question left (e.g. the same word translated two ways)? archive the finished review docs?
- **Browser:** book.json gives each parasha's Chromium version ("chromium"); a parasha keeps the version of its draft 1 to the final. Check this machine's version (`python3 -c "from playwright.sync_api import sync_playwright as s; p=s().start(); b=p.chromium.launch(); print(b.version)"`). If it differs, don't make the final here: tell David (another version can move page breaks; Noach gives 38 pages instead of 39 with 153).

## 1. Apply the last round
If the last review has answers not yet applied, run apply-review-decisions steps 1–5 (answers.json + chat_answers.json; one substitution at a time, logged).

## 2. Final build and checks
```
cd <folder> && mkdir -p build          # a fresh clone has no build/
python3 -I work/assemble.py            # Sefaria-built parashot (Noach on)
python3 scripts/render.py data/model.json build/book.html
python3 scripts/make_pdf.py "$PWD/build/book.html" "$PWD/build/book.pdf" build/rep.json
cd .. && python3 -I scripts/check_all.py <folder>
```
- check_all must end `RESULT: clean`, or every new hit read and either fixed or accepted (`--accept`) as right. A failing hard check (letters, Text lines, Onkelos, pages, a script that didn't run) stops the chain. The pages check includes the Chromium version (make_pdf.py records it in rep.json).
- Compare with the last draft: same page count and the same last line on every page (pdftotext, split on \f, strip \xad); line breaks inside the verse band may differ only if the browser did.
- Find the pages of the last round's changes and look at two or three of them as images.
- No "Draft for review" may remain (grep build/book.html); for the first parasha of a volume, remove it from data/front.json.

## 3. Files and book.json
- `cp build/book.pdf "drafts/Ibn Ezra <Parasha> - final.pdf"`.
- book.json: status "final (<date>): <which reviews>", first/last page from rep.json, "chromium" = the major version in rep.json "browser". If the page count changed, renumber every later parasha (commentary-book-build) and tell David; check_all's pages check must then be clean for each.
- **Key to terms** (Front Matter C5: each entry gives its first place in every parasha). Add this parasha's places:
  ```
  python3 -I review_round/key_add_parasha.py <Parasha> <folder>/data/model.json <first ch> <last ch>
  ```
  It only appends to entries that already have a "First:" list, writes nothing until `APPLY=1`, and logs to `review_round/key_places_<parasha>_log.json`. Check every proposed place by hand: print the English comment at that verse and confirm the term is used in the key's sense. Typical false hits: the English word in another sense ("the number that I named" for noun/name), a longer word with a prefix ("the grammarian" for grammar). Add each false hit to `EXCLUDE` in the script, keyed by the entry's **English** (so no Hebrew is typed), and run again; an entry with no true place is left without one. Then `APPLY=1 python3 -I review_round/key_add_parasha.py ...` and commit the log. (key_places.py / apply_key.py are only for entries with no list yet.)

## 4. Front matter (contents page lists every final parasha)
```
cd bereshit
python3 scripts/render.py data/model_final5.json build/front.html frontonly
python3 scripts/make_pdf.py "$PWD/build/front.html" "$PWD/build/front.pdf" build/frep.json
cp build/front.pdf "../front/Ibn Ezra on the Torah - Front Matter.pdf"
# the build must report "warnings 0": a front page past 980 px loses its last lines (the key to terms grows with each parasha)
# the Contents now ends with the Glossary on the page after the new last page; publish_pdfs.py rebuilds the glossary itself
```
Check: 10 pages (i–x) and the new parasha in the contents with its first page (`pdftotext -layout`, strip \xad: names may carry soft hyphens).

## 5. Parts export
`python3 scripts/export_parts.py` at the repo top (add the folder to MODEL if its final model is not data/model.json). The counts must match the model: verses; Hebrew comments = hc blocks; English comments = ec blocks minus the chapter markers; notes.

## 6. Booklet and full book
- Make sure the parasha's davar Torah is in insights/davar.py (commentary-key-insights-booklet).
- Rebuild **this parasha's** booklet only: `python3 insights/booklet.py <Parasha>`. A booklet takes its page references from its parasha's build/rep.json, so rebuild another parasha's booklet only from a build made with that parasha's Chromium version (`publish_pdfs.py --rebuild` rebuilds them all: use it only when every parasha has such a build).
- `python3 scripts/publish_pdfs.py` (no --rebuild): copies the final into `<folder>/Ibn Ezra on Parashat <P>.pdf` and joins `book/Ibn Ezra on the Torah - Bereshit to <P>.pdf` (one file; the old one is replaced). Check: page count = 10 + the parasha's last page; each parasha starts on its book.json page (`pdftotext -f <page+10> -l <page+10>`); each insight's "Full commentary … page N" is the page of the comment it quotes; grep the booklet for wordings changed in the last round.
- The full book stays in GitHub (and is sent in chat); it is not uploaded to Drive (David, 29 Oct 2026).

## 7. Back up
A line in docs/HISTORY.md under "The latest work" (what changed last, pages, export counts, full-book pages, next parasha's first page), commit with the session's attribution lines, push. Then `python3 -I scripts/handbook.py build`, push, and `sync_handbook()` in the workbench, so the documents in Drive (00 Start here, 13 History) show the final.

## 8. Drive folder
In the workbench: `refresh_drive(dry=True)`, then `refresh_drive()` (wb.py; it loads from GitHub main, so push first). It puts the parasha's PDF into "03 Parashot" as `NN <Parasha>.pdf` and its booklet into "04 Key Insights" as `NN <Parasha> - Key Insights.pdf` (NN = place in book.json: 01 Bereshit … 05 Chayei Sarah), replaces the front matter in place, renames older names in place (links stay), trashes the parasha's old draft from "05 Drafts" and any full book. It prints one line per change and verifies sizes. A single file over 5 MB cannot upload: tell David.

## 9. Archive the review docs (only when David says; review-list-google-doc, "Archiving"; docs/rules/review_doc.md)
In the workbench, per doc:
- Decisions with chips: `read_answers(<id>, commit=False, show=False, check_links=False)`; attach `<rows dir>/chat_answers.json` entries as `resolved_in_chat`.
- Text: `run_composio_tool('GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT', {'document_id': id, 'include_tabs_content': True}, account=DOCS)` → `data['plain_text']` (check both tabs are there).
- Google Sheet: every tab as CSV plus decisions.json (GOOGLESHEETS_BATCH_GET, account `david-personal`).
- One `gh_commit` under `<folder>/review/archive/` (or `review_vowels/archive/`, `review_sources/archive/`, `review_grammar/archive/`): `<title>.txt`, `<title> — decisions.json`, `decisions.json`; confirm with `gh_tree()`. Then the doc into “Ibn Ezra — Older reviews” (`sync_reviews()` does this for every doc set to `applied`; David, 9 Nov 2026: kept, not trashed); then status `archived` + `archive` folder in review_docs.json, commit, push.

## 10. Report
Send the full book and the parasha PDF with SendUserFile. In a few lines: final pages, what the last change was, full-book page count, key-to-terms places added, the Drive folder refreshed, what was archived (with each doc's link), and the next parasha with its first page.
