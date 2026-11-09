---
name: "commentary-publish-pdfs"
description: "Re-make the parasha PDFs, Key Insights booklets and the one full-book PDF 'Bereshit to the latest parasha' of David's Ibn Ezra book on GitHub, and refresh the shared Drive folder, outside the finalize chain."
---

# Publish the PDFs (parasha folders, insights folder, full book, Drive)

Making a parasha final runs these steps inside **finalize-parasha** (steps 6–8); use this skill on its own only when a final parasha was revised (e.g. a book-wide change rebuilt it), when page numbers moved, or when David asks for "the full pdf" or to refresh the Drive folder. Load commentary-house-rules first.

## What David wants (Oct 2026)
- **Each final parasha folder holds its book PDF**: `<folder>/Ibn Ezra on Parashat <P>.pdf` (the final book pages). Drafts stay in `<folder>/drafts/`.
- **The Key Insights PDFs live in the `insights/` folder**, not in the parasha folders: `insights/Ibn Ezra on Parashat <P> - Key Insights.pdf`.
- **The full book is ONE file**, `book/Ibn Ezra on the Torah - Bereshit to <last final parasha>.pdf` (e.g. "Bereshit to Noach"). Name it only that way: no list of each parasha and no page range in the name. It is made **only once a parasha is final** (never for drafts), and each time it replaces the old file, so there is always exactly one.
- Everything is saved to GitHub, and the shared Google Drive folder is kept in step (step 5).

## Steps
1. Every parasha to publish is final in book.json (status starts with "final") with `<folder>/drafts/Ibn Ezra <P> - final.pdf`, and `first_page`, `last_page`, `next_first_page` set; its davar Torah is in insights/davar.py (commentary-key-insights-booklet).
2. `python3 scripts/publish_pdfs.py --rebuild` at the repo root: rebuilds each final parasha's booklet into insights/, copies each final book PDF into its folder, joins all final parashot (pdfunite) into the one file in book/.
3. Check: the joined file's page count equals 10 (front matter i–x) + the last final parasha's last_page, and each parasha starts on the page book.json says (`pdftotext -f <page> -l <page>`).
4. Commit the PDFs, book/, README (section "PDFs: parasha folders, insights folder, full book") and book.json; push to origin main; send David the files that changed with SendUserFile.
5. **Refresh the Google Drive folder** (David, Oct 2026): in the Composio workbench load scripts/workbench/wb.py (load line at its top) and run `refresh_drive()` — `dry=True` first to see the plan. It works only in David's account (googledrive_pulse-dwang; never the default Going Pro account) on the folder "Ibn Ezra on the Torah" (id 1bVsTk1WHrJM0NB158u4tFmU4g4rmbkMo, anyone with the link can view; sub-folders 01 Full book, 02 Front matter, 03 Parashot, 04 Key Insights, 05 Drafts (not final)). From book.json and the repo it maps: full book → 01; front matter → 02; each final parasha → 03 as "Ibn Ezra on Parashat <P>.pdf"; each booklet → 04; the latest draft of a parasha not yet final → 05. It compares MD5s (unchanged files are left alone), replaces changed files in place so links stay the same, adds new ones, renames a superseded draft, trashes the draft of a parasha that is now final, and verifies every size against GitHub. Report its summary line to David (no need to repeat the folder link unless asked).
   - Limit: 5 MB per file; the full book is about 4.2 MB, so ask David about splitting it by sefer before it passes 5 MB.
   - Fallback if wb.py fails: per file, GITHUB_GET_RAW_REPOSITORY_CONTENT (data.content.s3url) → /mnt/files → `upload_local_file` (take ['s3key']) → GOOGLEDRIVE_UPLOAD_UPDATE_FILE (fileId, file_to_upload {name, mimetype application/pdf, s3key}); UPLOAD_UPDATE_FILE does not rename, so rename with GOOGLEDRIVE_UPDATE_FILE_PUT (name); verify sizes by listing the folders.

## Notes
- Do not edit the joined PDF by hand; fix the parasha and run the script again.
- The booklet and its Google Doc are the same document; the PDF is the default and a Google Doc is made only when David asks (commentary-key-insights-booklet).
- If the book is later split into volumes (book.json volumes_plan), change the join step of scripts/publish_pdfs.py and drive_plan() in wb.py, not the folders.