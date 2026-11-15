# The review doc

What a review list looks like as a Google Doc, how it is kept, found and archived. (What goes into the rows is in **08 Review**.) Each rule gives the rule, an example and the reason; the numbers ("Ruling 103") are entries in **03 Rulings**. The second part, "For Claude", is the full technical reference for building and changing a doc — it is part of the review-list-google-doc skill.

## The rules

### 1. A Google Doc in your account, answered with dropdowns
**Rule.** Every review list is a Google Doc in your own account, with a real dropdown (a "chip") in the Decision column of every row — Unanswered, the row's own two choices (08 Review, rule 13), Change, Discuss — and a Your note column, so you can answer from any device.

**Why.** You answer reviews on your phone, without your computer. *Rulings 103, 116.*

### 2. How a doc is laid out
**Rule.** A title and a date; a short **How to use this list** (what Approve, Keep, Change and Discuss mean, and "tell me 'the review is done' and I will apply every decision"); then one Part per topic, each with a heading, one sentence saying how many items it has, and its table. The columns: ID, the context (Where, Issue, Now, Alternative), a Sefaria link for rows about the text, Decision, Your note, Explanation. Closing sections may follow ("What the check found clean", "Right after the review", "Roadmap").

**Why.** Every doc reads the same way, so you know where to look.

### 3. Every doc has an Explanations tab, linked both ways
**Rule.** A second tab, **Explanations**, has a short plain-words explanation of every row. The ID of each row opens its explanation, and "↩ Back" on the explanation returns you to the same row. Each explanation is short and to its own row.

**Why.** Your standing preference: the list stays compact, and the full breakdown is one tap away. You did not like a long breakdown pasted into one cell. *Ruling 104.*

### 4. The house design
**Rule.** Headings in Georgia, text in Inter, nothing bold except the column names and leading words in "How to use"; Hebrew-only paragraphs right to left in Frank Ruhl Libre; quiet borders and a light header row. Colour comes only from the dropdown chips (and the blue of links).

**Why.** A calm page where the only colour is your answers.

### 5. Verse-against-comment rows: one per verse
**Rule.** In a Part that compares the verse band with Ibn Ezra's comments, there is one row per verse, in verse order: Where = the verse and the Hebrew word; Issue = what Ibn Ezra says, in a sentence or two; Now = the Hebrew word, then the verse band's wording; Alternative = the Hebrew word, then the usual wording. Keep = the verse stays; Approve = the usual wording. A word that recurs gets one row per verse, and each names the other verses with the same word.

**Example.** אֵלוֹן at Lech Lecha 12:6, 13:18 and 14:13: three rows, each naming the other two.

**Why.** You asked for Lech Lecha's Part E to be split into one row per verse. *Ruling 91.*

### 6. Checked before it goes out
**Rule.** Before a list is sent: for each row that changes a word's English, every other verse with the same Hebrew word is listed, so an answer doesn't leave one word translated two ways; an Alternative never says what Ibn Ezra's comment or the note denies; and where the Alternative is Claude's own plain rendering rather than a quoted translation, the Explanation says so.

**Example.** Lech Lecha 15:2: the Alternative "heir" contradicted the note's "not an heir by birth"; you chose "steward".

**Why.** An answer should not create a new inconsistency.

### 7. A doc you have started is never rebuilt
**Rule.** Once you have started answering a doc, new rows are added to it as a new Part, or a Part with no answers yet is replaced in place. Your answers are never touched.

**Why.** Your Decisions and notes are never lost or overwritten.

### 8. Ask for any review by name
**Rule.** Ask for "the Noach one", "the last one", or any review, and Claude gives its link, title and status in one line — "the last one" being the newest for that parasha, an open one before an archived one. If the request fits more than one doc, Claude lists them and asks which.

**Why.** Every review doc is in one register, so none is lost.

### 9. Finished docs are archived, never deleted
**Rule.** When a doc has been answered and applied, its text and every answer (chips and notes) are saved on GitHub, and only then is the Google Doc moved to "-01 Ibn Ezra — Older reviews". A review doc is never deleted. Reference documents (grammar sheets used as cards, the Editorial record) are left alone.

**Why.** The decisions stay readable, and the doc stays where you can open it. *Ruling 86.*

---

## For Claude: the technical reference

David answers review questions from any device, so the list is a Google Doc in davross846@gmail.com with real dropdown chips. Every review document has its Explanations tab, built in the same session as the list without waiting to be asked. One small review document per parasha (or per round): a long document stops opening on his phone.

### Account
The DEFAULT Composio googledocs and googledrive accounts are the Going Pro ones (filmgoingpro). Never rely on the default. Every call must name David's account explicitly:
- googledocs: `googledocs_spinet-dirk` (alias david-personal); googledrive: `googledrive_pulse-dwang` (alias david-personal); googlesheets: `david-personal` (the other one is "Film Going Pro").
- In the workbench use `run_composio_tool(slug, args, account=...)`. `proxy_execute` has no account argument and goes to the default (Going Pro) account, so do NOT use it for David's docs (it returns 403 on his files, and would create new files in the wrong Drive).
- Raw Docs API through Composio tools: `GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN` (title, markdown_text '') to create; `GOOGLEDOCS_GET_DOCUMENT_BY_ID` (id, includeTabsContent true) to read; `GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT` (document_id, edit_docs = the batchUpdate request list) for every edit. It accepts createDropdownDefinition, insertDropdown, addDocumentTab, pinTableHeaderRows and updateDocumentStyle (PAGELESS) as well.
- After creating, confirm the owner with `GOOGLEDRIVE_GET_FILE_METADATA` (fileId, fields 'owners,name', account googledrive_pulse-dwang).
- If the account ids ever change, list them with COMPOSIO_MANAGE_CONNECTIONS (action list) and pick the one whose email is davross846@gmail.com.
- For READING only, the Google Docs connector's read_doc and the Google Drive connector's search_files also reach David's files directly (no workbench). read_doc saves a large doc to a file; parse it with Python. The Google Sheets connector hits a per-minute read quota quickly; read sheets with GOOGLESHEETS_BATCH_GET (account david-personal) instead.

### Before the list goes out (rule 6)
Before building, check the rows by program and by reading:
- **Same word, other verses.** For each row that changes a word's English, list every other verse with the same Hebrew word, so an answer doesn't leave one word translated two ways.
- **Alternative against the note.** An Alternative must not say what Ibn Ezra's comment or the note denies (Lech Lecha 15:2: the Alternative "heir" contradicted "not an heir by birth"; David chose "steward"). Prefer the usual wording that doesn't contradict him.
- **Whose wording.** When the Alternative is Claude's own plain rendering rather than a quoted translation, the Explanation says so.

### The registry: review_docs.json (rule 8)
Every review doc of the Ibn Ezra series is listed in `review_docs.json` at the top of davidross01/ibn-ezra-commentary: parasha, list number, title, id, explanations tab id, rows file, row count, opened date, status, last check. Sheets are listed too (kind "sheet").
- Status values: `open` (waiting for David), `answered` (he said the review is done, not yet applied), `applied`, `archived` (saved under `<parasha>/review/archive/`; the Google Doc is kept in the Drive folder “Ibn Ezra — Older reviews”, registry field `drive`).
- **When David asks for a review doc ("link to the Noach one", "the last one")**: `git pull`, read review_docs.json, and pick by parasha and list number. "The last one" = the highest list number for that parasha (or the newest `opened` overall), and prefer an `open` one over an archived one. Give the link `https://docs.google.com/document/d/<id>/edit`, the title, and its status in one line. If it is archived, give the same link and say it is in “Ibn Ezra — Older reviews” (and where the GitHub archive is); a doc whose entry has no `drive` field is no longer on Drive, so give the archive. If the request still fits more than one doc, give the candidates in one line each and ask which.
- If a doc is not in the registry, search David's Drive by title (search_files: `title contains 'Review List' and title contains '<Parasha>'`), then add it to the registry and commit.
- Keep it current: add a new entry the moment a doc is created (build step 3 below), and update `status` and the row count when it is changed, answered, applied or archived (apply-review-decisions and the Archiving steps). The `<parasha>/review/listN_doc_id.txt` files stay as well.

### Quick build: scripts/review_doc.py
The whole build below is scripted in `scripts/review_doc.py` at the top of davidross01/ibn-ezra-commentary. Today the rows come from `review_audit/<key>_rows.py` → `python3 -I review_audit/make_rows.py <key>` → `<key>_rows.json` + `<key>_doc_cfg.json`, and the doc is built in one call, `Builder.run(cfg)`, which resumes a stopped build; the phase-by-phase steps below are what it runs.
1. In the parasha folder write `review/listN_rows.py` → `review/make_rows.py` → `review/listN_rows.json` (rows: id, part, cells [where, issue, now, alternative], url, plain, stands, changed) and a `review/listN_doc_cfg.json` (title, subtitle, how [(kind, text)] with kinds H1 / NORMAL / BULLET, parts [(letter, heading, sentence, headers, widths)], clean lines, bold words, account `googledocs_spinet-dirk`). Commit and push. Take every Hebrew word from the model by consonant match (strip points, cantillation, maqaf and paseq ׀), never typed.
2. In the workbench: fetch the three files with GITHUB_GET_REPOSITORY_CONTENT (the base64 text is at `r['data']['content']['content']`), `exec` the script, then `B = Builder(cfg)` (cfg needs `rows` and `account`); `B.phase_main()`; `B.phase_explanations()`; `B.phase_styles()`; `B.phase_links()`; `print(B.verify())`. Run the phases in separate cells (180 s limit). verify() must report chips = links_ok = rows and n_bad 0.
3. Save the doc id to `review/listN_doc_id.txt` and `review/listN_doc.json`, **add the doc to `review_docs.json` (status open)**, and commit.
4. Run the **check-review-doc** skill on the new doc (scripts/check_review_doc.py) as the final check, and record its result in the registry's `checked` field.

### Changing a doc David has already started (rule 7)
- **Add a Part:** `B.append_part(doc_id, part, rows, before='<heading of the Part that should follow>')`. Existing rows, chips and notes are untouched; it verifies the new rows.
- **Replace a Part in place** (e.g. split a grouped row): first read its chips and notes and make sure every row of that Part is Unanswered (otherwise ask). Delete from that Part's heading to the next Part's heading in both tabs (`deleteContentRange` with `tabId`), then `append_part(..., before=<next Part's heading>)`. The main list keeps its order; the Explanations section goes to the end of that tab. Then check every chip in the doc by reading it back, update listN_rows.json (make_rows.py may no longer run once the book has changed; edit the JSON directly) and the registry's row count.
- **Edit text inside one cell:** a cell's `startIndex` is the cell itself; its text starts at startIndex + 1. Delete `[start+1, end-1)` and insert at `start+1`, highest index first.

### Document structure (rule 2)
1. Title (TITLE style), then a date line.
2. **How to use this list** (heading): one paragraph, then four bullets defining Approve / Keep / Change / Discuss, then one line on row IDs and Proposals. Close with: tell me "the review is done" and I will apply every decision.
   - Keep the house meanings: **Approve** = do what the Proposal / Alternative column says; **Keep** = leave the book as it is (the Now column). Write each row's plain-words explanation with the same meanings ("Keep = …, Approve = …"), never "Approve = keep as now".
3. One section per Part ("Part A — Open decisions from chat", ...): heading, one sentence saying how many items and which unblock the rest, then the table.
4. Optional closing sections (heading 3): "What the check found clean" (bulleted), "Right after the review" as a checkbox list, "Roadmap" as a numbered list, "How each ... is produced" numbered, "How to instruct me".
5. Second tab **Explanations** (always), linked from an Explanation column in every table, with a back link on every row to the same row in the list.

### Tables
- Columns: ID | (context columns: Where, Issue, Now, Proposal / Alternative, ...) | (Sefaria, for rows about the text: see commentary-house-rules) | Decision | Your note | Explanation.
- Parts may have different columns, so when reading answers back find the Decision and Your note columns by their header text, not by position.
- One row per item; IDs are Part letter + number (A1, B3, C12).
- When a row concerns Hebrew text, show the Hebrew line itself (pointed, no transliteration) and its English, both as it stands now and as it would be if changed: put the Hebrew on one line and the English on the next line in the same cell.
- Decision cell holds a dropdown chip; Your note holds David's text (and any screenshot he attached, as an inline image under the text).
- Header row pinned (`pinTableHeaderRows`, 1).
- Document is PAGELESS (`updateDocumentStyle` documentFormat.documentMode = PAGELESS) so wide tables scroll sideways instead of squeezing.
- Column widths (FIXED_WIDTH, PT): ID 40; short context 70–130; long text 170–300 (the Now and Alternative columns are always exactly the same width, 220 as the default; make_rows stops otherwise); Sefaria 60; Decision 95 (fits the chip); Your note 200–220; Explanation 75.

### House design (rule 4; match exactly)
| Element | Font | Weight | Colour |
|---|---|---|---|
| Title and all headings | Georgia (serif) | 400, never bold | #1f1e1d |
| Body text and table cells | Inter (sans) | 400 | #1f1e1d |
| Hebrew-only paragraphs in cells | Frank Ruhl Libre, 12 pt (11 pt in Explanations), direction RIGHT_TO_LEFT, alignment START | 400 | #1f1e1d |
| Table header row text | Inter | 400, not bold | #52514f |
| Table header row fill | | | #f5f3ee |
| Body cells fill | | | #ffffff |
| All cell borders | 1 pt solid | | #e8e5dd |

No navy, no bold headers, no coloured cell fills. Colour comes only from the dropdown chips (and the default blue of links).

#### When to bold
- In "How to use": the column names **Decision** and **Your note**, the leading word of each definition bullet (**Approve**, **Keep**, **Change**, **Discuss**), and **Proposal** (or **Alternative**) where it names the column.
- In numbered roadmap items: the lead phrase only (e.g. **Finish Parashas Bereishis** — rest of the sentence regular).
- Nothing else: table text, checklist items, process steps and headings stay regular.
- Italicise transliterated terms used as words (e.g. *dorash*).

### Dropdown chips (rule 1)
Create one definition, then insert a chip in every Decision cell. The field names below are the ones the API actually accepts (checked against the Docs discovery document):
```python
def hexc(h): return {"color": {"rgbColor": {"red": int(h[0:2],16)/255, "green": int(h[2:4],16)/255, "blue": int(h[4:6],16)/255}}}
opts = [("unans","Unanswered","f4cccc"), ("approve","Approve","d9ead3"), ("keep","Keep","cfe2f3"),
        ("change","Change","fff2cc"), ("discuss","Discuss","fce5cd")]
{"createDropdownDefinition": {"dropdownDefinition": {
    "dropdownDefinitionId": "kix.decision01",
    "dropdownDefinitionProperties": {"title": "Decision", "options": [
        {"optionId": "dropdownItem." + i, "displayValue": t, "textStyle": {"backgroundColor": hexc(c)}} for i, t, c in opts]}}}}
{"insertDropdown": {"location": {"index": cell_index}, "dropdownDefinitionId": "kix.decision01", "selectedOptionId": "dropdownItem.unans"}}
```
- Definition IDs must match `^kix\.[a-zA-Z0-9_-]{2,14}$`; option IDs `^dropdownItem\.[a-zA-Z0-9_-]{2,14}$`.
- Option textStyle accepts only foregroundColor and backgroundColor.
- Reading back: a chip is a paragraph element `dropdown` with `dropdownProperties.displayValue`.
- When a Part is added to an existing doc, reuse the doc's existing definition id (kix.decision01); don't create a second one.
- Add project-specific options (e.g. Opus / Sonnet) when a Part compares versions. Copy existing answers over as the selected option.

### Build order (Docs API batchUpdate)
1. Create the doc (GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN with David's account and a title). Insert all paragraphs with `insertText` at `endOfSegmentLocation` and every table with `insertTable` at `endOfSegmentLocation`, in document order, in one batch. Keep a list of (paragraph text, kind) for styling later. Create the tables with the Explanation column included from the start.
2. Re-GET the doc; fill cells working in **descending index order** so earlier indices don't shift: put the `createDropdownDefinition` first in the batch, then every cell `insertText` / `insertDropdown` sorted by index, highest first. To replace cell text: `deleteContentRange`, then insert text or the chip. A batch that is too large can be split into consecutive chunks without breaking the descending order.
3. Re-GET, then styles in one batch: named styles first (`namedStyleType`), then one `updateTextStyle` over the whole body (Inter 400, not bold, #1f1e1d); headings Georgia 400 (clear any explicit fontSize on them so the named size shows); per table `updateTableCellStyle` (borders + white fill over all rows, header fill on row 0) and header-row text colour #52514f; Hebrew-only cell paragraphs (Hebrew letters, no Latin) to RTL + Frank Ruhl Libre 12; then the bold ranges above.
4. Lists: `createParagraphBullets` with `BULLET_CHECKBOX` for checklists, `NUMBERED_DECIMAL_ALPHA_ROMAN` for roadmap/process, `BULLET_DISC_CIRCLE_SQUARE` for definitions.
5. Column widths (`updateTableColumnProperties`), pin header, PAGELESS.
6. Build the Explanations tab and the links (next section).
7. Verify: re-GET and compare every cell's text with the source rows, count the chips (one per row, showing Unanswered), and check every link (below; check-review-doc does the chip and link part in one run).

### Explanations tab (rule 3)
A plain-words explanation for every row, kept out of the main list so it stays compact. Each row in the list opens its own explanation, and each explanation returns to the same row in the list. Keep each explanation short and to its own row; David did not like a long breakdown pasted into one cell.
1. **Content first, in the local container.** For each row write: where + one short plain-English paragraph on what the question is and what each choice means (Keep = ..., Approve = ...); "As it stands" = Hebrew line, the full Hebrew passage around it, and its English; "If changed" = the same three as they would be, or "Hebrew: the same" / "English: unchanged (only the Hebrew display changes)" when only one side moves, plus "Alternative as written:" quoting the Proposal from the list. For rows that are not about the text (layout, method, licences), describe the current state and the state after the change in plain words, with a real example from the book where one exists. Take Hebrew and English from the project's real source data (never retype from memory); window the passage to whole clauses. Before sending, check by program that every Hebrew-only line occurs in the source data. Save all rows to one JSON file (id, part, plain, stands, changed) and keep the order the same as the list.
2. **Structure.** `addDocumentTab` titled "Explanations" (ids look like `t.xxxx`; the main tab is `t.0`; the reply may come back empty, so re-GET to find the new tab id by title). Every location and range then carries `tabId`. Insert a heading "Explanations", one intro line ("Each ID in the list opens its explanation here, and ↩ Back returns you to the same row"), then one Part heading + empty 5-column table per Part: ID | Where · what it is | As it stands | If changed | Back to the list. If the main tables were built without an Explanation column, `insertTableColumn` (insertRight of the last column) in every table, highest table first.
3. **Make every ID cell a link target, in both tabs.** Set the ID cell paragraph of every body row (rows 1..n, column 0) to `HEADING_4` in the main tab and in the Explanations tab; set the Explanations and Part headings to HEADING_1 / HEADING_2. Re-GET with `includeTabsContent=true` and collect each ID cell's `paragraphStyle.headingId`. In the main tab, restyle the ID cells afterwards so they look like normal cells (Inter 400 11 pt, not bold, not italic, #1f1e1d, spaceAbove/spaceBelow 0).
4. **Fill both tabs in one pass each, in descending index order.** Explanations tab: ID, plain, stands, changed, and "↩ Back to A1" linked with `{"link":{"heading":{"id":<main-tab ID-cell headingId>,"tabId":"t.0"}}}`. This takes David back to the same row, not just the Part. Main tab: header "Explanation", each row "Open A1" linked with `{"link":{"heading":{"id":<Explanations ID-cell headingId>,"tabId":<explanations tab id>}}}`. Put each link's `updateTextStyle` right after its `insertText` at the same index, with range index .. index+len(text), and give it foregroundColor #1155cc and underline, since the body-wide colour would otherwise hide it.
5. **Style the Explanations tab.** Whole tab Inter 400 9 pt #1f1e1d; headings Georgia 400; borders, header fill and header text colour as in the house design; Hebrew-only paragraphs RTL + Frank Ruhl Libre 11; ID paragraphs spaceAbove/Below 0; column widths (PT) 40 / 230 / 230 / 230 / 80; pin header; that tab PAGELESS too (`updateDocumentStyle` with `tabId`).
6. **Verify by reading back.** Compare every Explanations cell with the JSON (normalise whitespace); check that the main-tab IDs line up with the Explanations IDs in order; check that every "Open" link's headingId belongs to the Explanations ID cell with the same ID, and every "↩ Back" link's headingId belongs to the main-tab ID cell with the same ID; check that the chips are untouched. Fix mismatches with targeted edits.
- When rows or a whole Part are added to an existing doc later, insert the Part heading, sentence and table at the end of each tab (`endOfSegmentLocation` with `tabId`), add the matching explanation rows and both links in the same session, verify as above, and update the row count in review_docs.json.
- The doc read is too large for context (1–2 MB): let the tool save it to a file and parse it with a small Python script (tab ids, table start/end, per-cell start index, headingIds, Part heading ids).
- Never change the Decision or Your note columns, and never apply anything to the project while building explanations.

### What each Explanation contains
- **Every Explanation shows the Hebrew and the text both ways** (review.md, rule 12; enforced in review_audit/make_rows.py): the Hebrew line (Ibn Ezra's, or the verse when the row gives none), then the sentence as it stands and as it would be if changed, each with English. A row with no ops (made by hand) must give `changed` — the text as it would read — and `changed_he` where Hebrew changes; make_rows prints EXPLANATION WARNINGS otherwise, and they are fixed before the doc is built.

### The reviews folder on Drive (review.md, rule 4)
Every open or answered review doc sits in **“-02 Ibn Ezra — Reviews in progress”** (id 1O7WtvLyYhia5hb0PldzL5NKzgZMLRStN) and every archived one in **“-01 Ibn Ezra — Older reviews”** (id 1jUeiNkiIifdx6nSU8U8tosrQOjf5LX9A), both inside the book folder “Ibn Ezra on the Torah - PDFs”. wb.py finds them by id, so a change of name breaks nothing. The book folder is shared with anyone who has the link, so both folders have **limited access** (inheritedPermissionsDisabled = true, set with the Google Drive connector's update_file — the Composio tools cannot set it): the docs inside stay private to David. wb.py never creates the folders and stops if one is not limited. `sync_reviews()` in scripts/workbench/wb.py keeps them current and runs at the end of every `refresh_drive()`: a doc that is open or answered is moved into “Reviews in progress” (its other parents are kept, so links still work); a doc whose status is `applied` is archived as below (text and decisions.json committed under its archive folder, the commit confirmed) and then moved to “Older reviews”, and review_docs.json gets `archived` with its archive path; an archived doc found anywhere else (the trash included) is moved there too. So the moment apply-review-decisions sets a doc to `applied`, the next refresh_drive moves it from one folder to the other. A doc that is “open (partly applied)” stays until every row is applied.

### Archiving a finished review document (rule 9)
When a review document has been answered and applied (and David asks to clean up, or a new document replaces it):
1. Read it through the API (David's account) and save two things: a plain-text export (GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT with include_tabs_content, account googledocs_spinet-dirk) and the answers. **The plain-text export does not include the chip values**, so also read every table with GOOGLEDOCS_GET_DOCUMENT_BY_ID and save each row's ID, Decision displayValue and Your note to a JSON file. For a Google Sheet review: every tab as CSV (GOOGLESHEETS_BATCH_GET, account david-personal) and a decisions.json per tab (place, decision, note).
2. Commit both to the project repo under `<parasha>/review/archive/` (or `review_grammar/archive/` for a series-wide sheet; text files named after the doc, answers in `decisions.json`, keyed by doc), from the workbench with GITHUB_COMMIT_MULTIPLE_FILES on David's account, then `git pull` the local clone.
3. Only after the commit is confirmed, move the Google Doc into “Ibn Ezra — Older reviews” (`_move_into`, wb.py; account googledrive_pulse-dwang). Never trash or delete a review doc (the superseded “OLD - do not use” copy of Bereshit List 2 is the one left in the trash).
4. Set the doc's status in review_docs.json to `archived` with its `archive` folder, and commit.
5. Leave reference documents (grammar sheets used as cards, the editorial record) alone; archive only review lists and review sheets.

### Reading answers and checking a doc
- Answers: `read_answers(<key>)` in scripts/workbench/wb.py (Composio workbench). It reads the doc with David's account, keeps ID / Decision / Your note, checks the IDs against the rows file, runs scripts/check_review_doc.py there (one chip per row, every Open and Back link on its own row) and saves `<rows file>` → answers.json to GitHub. `review_status()` does it for every open doc in one call. Never load a whole doc into the conversation.
- Explaining rows: `python3 -I scripts/explain_rows.py <review> <IDs | --discuss | --change | --open | --noted>` from the repo (no Google call).
- Answers David gives in chat (Discuss rows settled with checkboxes) go to `<rows file>` → chat_answers.json ({id: {decision, note, date}}); apply-review-decisions reads them after answers.json. His Decision chip in the doc is never changed.

### Moving data into the workbench
The workbench sandbox can reset between calls and `/mnt/files` may come back empty. Prefer to push the row data and scripts to the GitHub repo and fetch them in the workbench with GITHUB_GET_REPOSITORY_CONTENT (content is base64 at `r['data']['content']['content']`); otherwise send it as Python source in the same cell that uses it. Check it arrived intact: print a short md5 of json.dumps(rows, ensure_ascii=False) on both sides and compare. Never send binary files (e.g. a .docx) as hand-copied base64: a single wrong character breaks the zip. To read a .docx from Drive, download it with GOOGLEDRIVE_DOWNLOAD_FILE inside the workbench, fetch its s3url with requests there, and parse it with python-docx.

### Images in a note cell
`insertInlineImage` needs a publicly fetchable URI. Upload the PNG to David's Drive (`GOOGLEDRIVE_UPLOAD_FILE` with an s3key from `upload_local_file`, account googledrive_pulse-dwang), add an `anyone` reader permission, insert with `https://drive.google.com/uc?export=view&id=<id>` (~230 pt wide), then delete the `anyoneWithLink` permission and trash the file. The doc keeps its own copy. If the image only exists in the local container, shrink it first (1-bit PNG, strip ICC) so it can be moved across, and check its md5 on both sides.

### Gotchas
- The default Composio Google accounts are NOT David's (see Account above): always pass his account id; never use `proxy_execute` for his docs.
- A .docx with dropdown content controls loses them on import to Docs; use the API.
- Google Sheets drops trailing empty cells; pad rows before reshaping.
- Hebrew inside JSON strings: escape a gershayim-style " (or use ״) so the request stays valid.
- Finish by telling David what changed in one or two lines; he answers in the Doc and says "review done".
