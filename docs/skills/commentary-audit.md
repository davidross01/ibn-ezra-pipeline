---
name: commentary-audit
description: "Bring a parasha of David's Ibn Ezra series that is already written up to the current house rules: rule fixes applied with a log, judgment calls (verse vs Ibn Ezra, translation, grammar notes, names and Onkelos, print, Ibn Ezra's ideas) as a review doc; renumber once at the end."
---

# Audit a written parasha against the current rules

Use when David asks to check, audit or bring up to date work already done ("go through everything we have done and make sure it is consistent", "audit Noach"), and for each round of the whole-book audit begun 30 Oct 2026 (Bereshit to Vayera). Load **commentary-house-rules** first. Repo: davidross01/ibn-ezra-commentary at /home/claude/ibn-ezra-commentary. The checklist is `review_audit/checklist.md`; the audit's current state is in `docs/HANDOFF.md` ("Whole-book audit").

## David's settings (30 Oct 2026)
- **Pure rule fixes are applied directly, with a log**, and listed at the end of the review doc: grammar terms by the glossary, vowel signs, Hashem / ה׳, place names, Text lines that report no difference, hedges ("probably", "may"), markup, Ibn Ezra quoting a verse in that verse's own English, a misprint quoted in its corrected form, leftover placeholders.
- **Judgment calls are review rows**: translation, wording, notes. Brackets are **Ibn Ezra-led**: wherever he explains a word of the verse, the verse shows his reading in [square brackets].
- **Ibn Ezra's ideas** (his rule of 30 Oct): Part F, below.
- **Nothing is rebuilt during the audit.** At the end every parasha is rebuilt once (Chromium 153), book.json "chromium" becomes 153 for all, and the pages are renumbered once.
- **Order**: calibration on Bereshit 1 (Audit 1), then one parasha at a time; Chayei Sarah waits. Later rounds follow his answers to Audit 1 (`review_audit/ber1_answers.json`): a kind of row he answered Keep is not raised again; a kind he answered Approve is raised again as rows unless he says to apply it directly.

## Steps
1. `git pull`; `python3 -I scripts/series_status.py`; read the checklist.
2. Dump the chapter: `python3 -I review_audit/dump.py <folder> <ch> > <scratchpad>/<x>.txt` and read **all** of it, to the last line (it has no final newline).
3. Programs: `python3 -I scripts/check_all.py <folder>` (letters, vowels, misprints, Hebrew sources, partly pointed, Text lines, Onkelos, Ideas); `python3 -I scripts/ideas_scan.py <folder>`; compare every "(Genesis c:v)" quotation in the English with that verse's English in the book; count conventions across the four parashot (square vs round brackets in the verse band, glossary terms, Text-line remarks, pointing remarks, "A reader might think") to see where an older parasha differs.
4. Read verse by verse, with the checklist: the verse band against every comment on it and on the verses before and after; the English commentary against the Hebrew, sentence by sentence (mistranslations first); each note (grammar in three steps; the ideas paragraph; Onkelos, Rashi, Radak, Rashbam, Ramban by their rules; every name, language and reference identified; no hedges; Text lines only for differences). Check sources on Sefaria (Onkelos from `src/onkelos.json`; the Sefaria MCP for Rashi, Radak, Avi Ezer and Ibn Ezra elsewhere). Never name Strickman, Silver, Weiser or Krinsky — Mechokekei Yehudah (Yahel Ohr, Karnei Ohr) is Krinsky's.
5. **Rule fixes**: a script `review_audit/<part>_fixes.py` that writes a GENERATED block — Bereshit: C entries in `bereshit/work/changes.py` (`'@DELETE_BLOCK'` removes a block), then `python3 -I bereshit/work/build_model.py`; other parashot: their `work/chN.py` or `review_round/subs.py`, then `work/assemble.py`. Every Hebrew string is copied from the model or a source file, never typed. Log `review_audit/<part>_fixes_log.json`; doubts and pointing remarks taken out of notes go to `review_grammar/all/editorial_record.json`. Print every change as a diff and read it. check_all must stay clean apart from the pages check.
6. **Rows**: `review_audit/<part>_rows.py` as data with markers — `{vw:c:v:i-j}` verse words, `{vh:c:v}`, `{hcw:c:v:i-j}` Ibn Ezra's Hebrew (`|strip`, `|first`), `{ec:c:v:n}` / `{nt:c:v:n}` Hebrew spans of the commentary / notes, `{q:…}` Scripture, `{o:…}` Onkelos; a row may name its `folder` and chapter `c`. Each row has `ops` (sec, (c, v), old, new). `python3 -I review_audit/make_rows.py` resolves the markers, checks that each old occurs once, adds the Sefaria links and writes `<part>_rows.json` and `<part>_doc_cfg.json`. No typed Hebrew in the rows file (grep for Hebrew outside markers). One row per item. Parts:
   - **A** the verse against Ibn Ezra; **B** the translation of his words (mistranslations marked); **C** grammar notes — "A reader might think …" and why it matters; **D** names, references, Onkelos and the other commentators; **E** book-wide print or conventions;
   - **F** Ibn Ezra's ideas: wherever he discusses an idea (God's knowledge, creation, angels, the soul, prophecy, the image of God), his science (spheres, astrology) or a "secret", one full paragraph of 120–200 words — the idea in detail, why he brings it here, what a reader would otherwise think; a hint is explained with its source named (his own comment elsewhere, Avi Ezer), read on Sefaria first; Ramban's objections stay out unless David asks. The model is F1 of Audit 1 (Vayera 18:21).
7. **The doc**: commit and push; in the Composio workbench exec `scripts/review_doc.py`, `B = Builder(cfg)`, then `phase_main`, `phase_explanations`, `phase_styles`, `phase_links`, `verify` in separate cells; compare the md5 of the rows on both sides; confirm the owner is davross846 (GOOGLEDRIVE_GET_FILE_METADATA, `fileId`). Add the doc to `review_docs.json` (status open) and save `review_audit/<part>_doc_id.txt`; run check-review-doc (`read_answers`). A new Part for an open doc: `B.append_part(doc_id, part, rows)`.
8. **Report** with the doc's link: what turned up, most serious first; what was applied; the rows by Part.

## Applying the answers
- `read_answers(<id>)` → `<part>_answers.json`. Discuss rows: explain, ask with checkboxes, save the answer to chat_answers.json.
- Approved rows: their `ops` from the rows file — Bereshit as C entries (row id as `row`) in a GENERATED block; other parashot in their work files. Book-wide rows (a word changed everywhere, how Hashem prints) need their own script over every parasha, the front matter and the booklets.
- Each verse whose idea paragraph is done (or judged not needed) goes into `<folder>/review/ideas.json`, so check_all "Ideas" stays clean.
- Archive the doc when applied (finalize-parasha step 9; docs/rules/review_doc.md).

## At the end of the audit
Rebuild every parasha once with Chromium 153, set book.json pages and "chromium", renumber; check_all clean for each; then finalize-parasha (front matter, parts export, booklets with the wording in insights/davar.py, full book, Drive). Update README History and docs/HANDOFF.md.
