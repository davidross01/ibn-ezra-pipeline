---
name: "review-list-google-doc"
description: "Build, update or find David's review list as a Google Doc (davross846) with dropdown Decision chips and a standard Explanations tab linked row-to-row, so he can answer from any device."
---

# Review list as a Google Doc

David answers review questions from any device, so each list is a Google Doc in davross846@gmail.com with real dropdown chips and an Explanations tab linked both ways. This file is the **core**. The full reference — raw Docs API calls, the build order, dropdown JSON, the house design table and when to bold, the Explanations tab step by step, changing a started doc, archiving, images in notes, moving data into the workbench, gotchas — is in the repo davidross01/ibn-ezra-commentary at **docs/rules/review_doc.md** (moved there word for word on 27 Oct 2026). Read it before building by hand, before changing a doc David has started, and before archiving.

## Always
- **Account:** every Google call names David's account: googledocs `googledocs_spinet-dirk`, googledrive `googledrive_pulse-dwang`, googlesheets `david-personal`. The default Composio Google accounts are Going Pro (filmgoingpro): never rely on the default, never use `proxy_execute` for his files. After creating a doc, confirm the owner (GOOGLEDRIVE_GET_FILE_METADATA, fields 'owners,name').
- **One small doc per parasha (or round)**, archived when finished; a long doc stops opening on his phone.
- **Every doc has the Explanations tab**, built in the same session as the list: each "Open X" goes to its explanation, each "↩ Back to X" returns to the same row.
- **One row per item, never a grouped row** (David, 25 Oct 2026). A "verse against comment" Part has one row per verse in verse order (Where = verse + Hebrew word; Issue = what Ibn Ezra says; Now = Hebrew word + the verse band's wording; Alternative = Hebrew word + the usual wording); a recurring word gets a row per verse, each naming the others.
- **House meanings:** Approve = do what the Proposal / Alternative says; Keep = leave the book as it is (Now). Each row's explanation says "Keep = …, Approve = …". A row whose answer depends on another row (E2 on C3) says so.
- **Hebrew in rows** is taken from the model by consonant match, never typed; show the Hebrew line and its English, as it stands and if changed. A Sefaria column (one-word link) on rows about the text (commentary-house-rules, review.md).
- **Never change David's Decision or Your note.**

## Consistency check before the list goes out
- Same word, other verses: for a row that changes a word's English, list every other verse with that Hebrew word.
- The Alternative must not say what Ibn Ezra's comment or the note denies (Lech Lecha 15:2 "heir" vs "not an heir by birth").
- When the Alternative is Claude's own rendering rather than a quoted translation, the Explanation says so.

## The registry: review_docs.json
Every review doc is in `review_docs.json` at the repo top (parasha, list, title, id, explanations tab, rows file, rows, opened, status open / answered / applied / archived, last check). When David asks for a review doc ("the Noach one", "the last one"): `git pull`, pick by parasha and list number (prefer an open one), give the link `https://docs.google.com/document/d/<id>/edit`, the title and status in one line; if archived, give the same link and say it is in “Ibn Ezra — Older reviews” (and where the GitHub archive is). Add a doc the moment it is created; update status and row count as it changes.

## Build (the normal path): scripts/review_doc.py
1. In the parasha folder: `review/listN_rows.py` → `review/make_rows.py` → `review/listN_rows.json` (id, part, cells [where, issue, now, alternative], url, plain, stands, changed), and `review/listN_doc_cfg.json` (title, subtitle, how, parts [(letter, heading, sentence, headers, widths)], clean, bold, account `googledocs_spinet-dirk`). Commit and push.
2. In the workbench: fetch the three files from GitHub, `exec` the script, then `v = Builder.run(cfg)` (9 Nov 2026): it builds the doc, with a progress line under the subtitle, and records each finished phase, so if the cell is stopped (180 s limit) running it again finishes the same doc. verify() (the return value) must report chips = links_ok = rows and n_bad 0. Load wb.py with `.content.decode('utf-8')`, not `.text`.
3. Save the id to `review/listN_doc_id.txt` and `review/listN_doc.json`, add the doc to review_docs.json (status open), commit.
4. Final check: `read_answers('<review>')` from scripts/workbench/wb.py (check-review-doc) — chips, links and IDs in one call; record its result in the registry's `checked`.
5. Tell David in one or two lines what the doc holds, with its link; he answers in the doc and says "review done".

## Reading answers, explaining, chat answers
- Answers: `read_answers('<review>')` or `review_status()` (every open doc) in the workbench; they save `<rows file>` → answers.json to GitHub. Never load the whole doc into the conversation.
- Explaining rows: `python3 -I scripts/explain_rows.py <review> <IDs | --discuss>` (explain-commentary-row).
- Answers David gives in chat go to `<rows file>` → chat_answers.json; his chip in the doc stays as he left it.

## Changing a started doc, archiving
Follow docs/rules/review_doc.md: "Changing a doc David has already started" (add a Part with `B.append_part`, replace a Part only when all its rows are Unanswered, edit one cell by index) and "Archiving a finished review document" (plain text + decisions.json — answers.json is that file — committed under `<parasha>/review/archive/`, then the doc to “Ibn Ezra — Older reviews”, status `archived`). Since 9 Nov 2026 this is done by `sync_reviews()` (wb.py), which `refresh_drive()` runs at its end: open and answered docs are moved into the folder “Ibn Ezra — Reviews in progress” inside “Ibn Ezra on the Torah - PDFs” (limited access, so the book link does not open them), and every doc whose status is `applied` is archived and moved to “Ibn Ezra — Older reviews” (same place, same limited access; never the trash). So after applying a review, set its status to `applied` and run refresh_drive (review_doc.md, “The reviews folder on Drive”).