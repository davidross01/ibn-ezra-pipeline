---
name: "check-review-doc"
description: "Check one of David's review-list Google Docs: a Decision chip on every row, every Open and Back link landing on its own row, IDs matching the rows file, and which rows are answered."
---

# Check a review doc

Use when David asks whether a review doc is linked or built correctly ("is everything linked correctly"), how far he has got with one ("what have I answered"), and right after building or editing a doc (review-list-google-doc, last step). Read-only: never edit the doc, never touch his Decision or Your note. Since 27 Oct 2026 the check runs inside the answer reader, so this is one workbench call.

## Steps
1. `git pull` davidross01/ibn-ezra-commentary (clone to /home/claude/ibn-ezra-commentary if missing). Find the doc in `review_docs.json` (parasha, list, id, rows_file). If it isn't there, search David's Drive by title (search_files: `title contains 'Review List' and title contains '<Parasha>'`) and add it to the registry.
2. In the Composio workbench load scripts/workbench/wb.py (load line at its top) and run `read_answers('<review>')` (all open docs at once: `review_status(check_links=True)`). In the workbench, with David's account (googledocs_spinet-dirk; never proxy_execute, never the default Going Pro account), it:
   - keeps every row's ID, Decision chip and Your note, and saves `<rows file>` → answers.json to GitHub;
   - checks the IDs against the rows file (none missing, none extra);
   - runs scripts/check_review_doc.py on the doc: an Explanations tab exists; one Decision chip per row; every "Open X" link lands on the Explanations heading of the same ID; every "↩ Back to X" lands on the same row in the list; same IDs in the same order in both tabs, no duplicates;
   - prints one short summary: counts, every Change/Discuss/noted row, "IDs match the rows file", and "OK: one chip per row, every Open and Back link lands on its own row" — or the problem rows by ID.
   The whole doc (2–3 MB) never enters the conversation.
3. **Owner.** If the doc is new or was found by search, confirm with Google Drive get_file_metadata that the owner is davross846@gmail.com, never filmgoingpro.
4. **Record** the result in the registry entry (`checked`: date, chips and links OK or the problems, how many answered) and commit.
5. **Report** in two or three lines, with the doc's link: whether every link and chip is right (or the problem rows and what is wrong), and how many rows are answered, which ones. Say that the check covers chips, links and IDs, not the wording. If links are broken, offer targeted edits (review-list-google-doc, docs/rules/review_doc.md, Explanations tab step 4) rather than rebuilding.

## Notes
- scripts/check_review_doc.py still runs on its own on a saved doc JSON (`python3 -I scripts/check_review_doc.py <file> --rows <rows file>`), e.g. on an archived copy; it reads either the connector's `{"content": {...}}` file or a raw documents.get JSON.
- A chip is any element with a displayValue; "Unanswered" counts as no answer. A row with a note but no chip is "note only": apply-review-decisions treats a clear note as an answer.
- Tested 27 Oct 2026: Vowels Review 1 (57 rows) and Vayera Review List 1 (39 rows), both OK (earlier: Noach Review List 2, Lech Lecha Review List 1).