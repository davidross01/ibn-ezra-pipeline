---
name: "commentary-series-status"
description: "One status report for David's whole Ibn Ezra series: each parasha's draft or final, pages, open review lists and answers, check results, whether PDFs, export and Key Insights are up to date, and the next action."
---

# Series status ("what's next")

Use when David asks where things stand ("status", "where are we", "what's open", "what's next", "what's the next set"), at the start of a session on the series, and before starting a new parasha. Read-only for the book and the review docs.

## Steps (three calls)
1. **Repo.** Attach and clone davidross01/ibn-ezra-commentary to /home/claude/ibn-ezra-commentary if it isn't there (see commentary-book-build), then `git pull --rebase`.
2. **Fresh answers, one workbench call.** Load scripts/workbench/wb.py in the Composio workbench (load line at its top) and run `review_status()`. It reads every open review doc in review_docs.json with David's account, saves each `answers.json` to GitHub in one commit, and prints per doc: answered / open counts, the link, and every Change, Discuss or noted row. (`review_status(check_links=True)` also checks chips and links; use it after a doc was built or edited.) Then `git pull`.
3. **Report data.** `python3 -I scripts/series_status.py --checks` at the repo top (about 20 s). Per parasha: status and pages, latest PDF, when its data changed, the Key Insights booklet, each open review with "N of M answered" and its link, the result of scripts/check_all.py, and warnings (data newer than the PDF, missing or older parasha PDF, export or booklet). Then the front matter and series-wide reviews, the full book, the next parasha and its first page, and a **NEXT** list in order of urgency: a review that is fully answered (apply it; Discuss rows first), failing checks, out-of-date files, reviews waiting on David, then starting the next parasha.

## Report to David
- One short block per parasha that has something to say; "everything built from the latest data" covers the rest. Always include the link of every open review.
- Then **Next:** the first NEXT item as the recommendation, in one or two lines, and the next one or two after it. When the first item is applying a review with Discuss rows, offer to explain them now (explain-commentary-row) — that is usually what David wants next.
- Don't fix anything as part of this skill; a fix follows the usual rules (commentary-house-rules).

## Notes
- The parasha order for "next" is the Torah's; it is in the script's TORAH list.
- If review_docs.json is missing a doc, add it (review-list-google-doc, "The registry").
- Answers in the report are as of answers.json's `read_at`; if step 2 was skipped, say how old they are.