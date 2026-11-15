# Sources, accounts and delivery

Where the texts come from, which accounts are used, and how drafts, final PDFs and these documents reach you. Each rule gives the rule, an example and the reason; the numbers ("Ruling 78") are entries in **03 Rulings**. The last part, "For Claude", has the exact accounts, endpoints and commands.

## Accounts and sources

### 1. Google files only in your own account
**Rule.** Every Google file of the series (review docs, sheets, uploads, these documents) is created and kept in your personal account, davross846@gmail.com — never the Going Pro film account (filmgoingpro@gmail.com) unless you say so.

**Why.** The Going Pro account is only for the film project. *Ruling 78.*

### 2. The texts come from Sefaria, and the comparisons are checked there
**Rule.** The verses, Ibn Ezra's Hebrew, the other commentators and Onkelos are taken from Sefaria, and every Rashi, Talmud and Midrash comparison in the notes is checked there and cited (the notes never say so: **07 Notes**, rule 15). The project is backed up in your private GitHub repository.

**Example.** "Bereshit Rabbah 19:8".

**Why.** One source that can be checked, with its licence credited in the front matter.

### 3. Your grammar workbook is a help, not a witness
**Rule.** Your "beginners_guide_to_diqduq.docx" (a 32-lesson workbook with a glossary and Ibn Ezra quotations) is used for plain-word definitions, not as a witness for the vowels: its vowels of Ibn Ezra were added and its letters sometimes differ from Sefaria.

**Why.** It explains grammar well, but it is not a source text.

## Drafts and finished PDFs

### 4. Drafts: when they are sent and what they are called
**Rule.** A draft is named "Ibn Ezra <Parasha> - draft N.pdf" (the last one "- final.pdf", with "Draft for review" removed from its title page). It is sent when you ask for one, after you have answered a review and asked to apply it, or when you ask for a layout fix; draft 1 of a new parasha goes out together with its review list. Each draft comes with its page count and what changed, in a line or two, and goes into the Drive folder ("05 Drafts").

**Why.** You see every draft, and only when there is something to decide or to read.

### 5. The Drive folder: no full book; parashot numbered in order
**Rule.** The full book is still built (on GitHub) but not put on Drive. In "03 Parashot" each final parasha is "NN <Parasha>.pdf", and in "04 Key Insights" "NN <Parasha> - Key Insights.pdf", NN being its place in the Torah. Files are replaced in place, so their links stay the same.

**Example.** 01 Bereshit, 02 Noach, … 05 Chayei Sarah.

**Why.** "The full book is at the upload limit — don't upload to Drive then, just have in each parasha, but put 01 PARASHA_NAME to make it in order." *Ruling 79.*

### 6. How the book is made, kept in Drive and kept current
**Rule.** These documents — Start here, the handoff, the README, the rulings, the rules, the core skill, the history and the commentator's profiles — are Google Docs in the private, numbered folder "-03 How it is made" inside "Ibn Ezra on the Torah - PDFs" (limited access, so the book's public link does not open them). They are copies of the files in the repository:
- they are **refreshed in place**, so their links never change, whenever a rule or a document changes, in the same session;
- an out-of-date copy is **flagged** by the checks;
- a **comment you leave** on one of them is read at the start of the next session and taken as a ruling (or answered, if it is a question), and the reply is left under your comment;
- a **weekly scheduled task** refreshes them and sends you a short note on what changed that week.

A copy is never refreshed while it has an open comment of yours, so the comment keeps its place.

**Why.** You can read and check the rules on any device, and the copy never drifts from the rules Claude follows. *Ruling 82.*

### 7. Automatic checks on every push
**Rule.** Every change pushed to GitHub runs all the checks of every parasha. A red X on a change means a new problem not yet read and accepted, or a broken script; it is fixed (or the hit accepted) in the same session, before going on.

**Why.** Mistakes are caught the moment they are made. *Ruling 80.*

### 8. Each finished edition is a GitHub Release
**Rule.** Each finished edition (parasha PDFs, booklets, front matter, full book) is published as a GitHub Release, tagged by date. Claude cannot create Releases from here, so you create it on github.com (Releases → "Draft a new release") with the files listed by Claude.

**Example.** The first is "editions-2026-10-29", the edition before the audit.

**Why.** A fixed copy of every edition. *Ruling 81.*

### 9. When a parasha becomes final
**Rule.** Making a parasha final is one chain, all at once: the final PDF, its parts exported as separate files, its Key Insights booklet rebuilt (the booklet's page references come from the final build), the full book rebuilt, the key to terms and the front matter brought up to date, the Drive folder refreshed, and its review docs archived.

**Why.** Every file that depends on the final pages is made from the same final build.

### 10. Three stages, and only the current version anywhere
**Rule.** Each parasha goes through three stages: **draft**, then **final**, then **audit**. The audit stage never closes: the parasha can be edited and updated at any time. Whatever version is being edited is the current one, and it is the only one you find in each place:
- **Draft:** only its latest draft is in "05 Drafts", replaced in place.
- **Final and audit:** the parasha is in "03 Parashot" as "NN <Parasha>.pdf" and its booklet in "04 Key Insights", and on GitHub in its own folder and in the full book.
- **Every applied change publishes:** each time answers are applied, the parasha PDF, its booklet, the parts export, the front matter, the glossary and the full book are rebuilt in the same run, and the Drive files are replaced in place, so their links never change.
- **Pages carry forward:** if a change adds or removes a page, every later parasha and its booklet are renumbered and rebuilt in the same run.
- **Edition date:** each parasha's title page says "Edition of <date>", the date of its last change (the booklet's footer too); there is no stage word, and the file names stay the same.

**Example.** An audit change to Chayei Sarah 24:1 is applied: "03 Parashot/05 Chayei Sarah.pdf" and "04 Key Insights/05 Chayei Sarah - Key Insights.pdf" are replaced in place, with that day's edition date on the title page; if it gained a page, Toledot starts one page later.

**Why.** "Whatever version is being edited should be the current version, and so when it [is in] the Google Drive or GitHub, it shows the current version in each folder of that parasha … and so too with everything." *Ruling 105.*

### 11. Drive is a second way to everything
**Rule.** Everything of the book can be reached from its Drive folder, not only from GitHub: the book (PDFs and its plain text), the booklets, the front matter, every review doc, how it is made (00–15), every skill, and the audit's working files, with a guide at the top that links to each one. Private things sit in folders whose name starts with "-" (limited access); the book itself stays open to anyone with the link. Everything there is a copy of the repository, refreshed in place whenever it changes. The full book alone stays on GitHub (rule 5), and the guide links to it. Files of the book found loose elsewhere in Drive are moved into the book folder ("-05 Old files" for what is superseded); none is trashed.

**Example.** "-00 Guide (start here)" holds the guide; "-04 Skills" a Google Doc for each skill; the audit folder its brief and findings; "06 Plain text" the five text files of the book.

**Why.** "Make sure that everything also is in the Google Drive and that it is another way of accessing everything; if you need to rearrange or add to the folders you can." *Ruling 112.*

---

## For Claude: how it is done and checked

- **Rule 1:** use the Composio Google connections with the davross846 account: googledocs `googledocs_spinet-dirk`, googledrive `googledrive_pulse-dwang` (alias david-personal), googlesheets `david-personal`. To trash a file, GOOGLEDRIVE_TRASH_FILE with account googledrive_pulse-dwang. GitHub through Composio uses the default account (no account argument). Limited access on a folder (inheritedPermissionsDisabled) is set only with the Google Drive connector's update_file / create_file; the Composio tools cannot set it.
- **Rule 2 (Sefaria):** use the Sefaria MCP tool (the shell can't reach sefaria.org). A whole book in one call: `/api/v3/texts/<Book>?version=hebrew&return_format=text_only`; save the large result to a file for parsing. A commentary's English a verse or chapter at a time: `/api/v3/texts/Ibn_Ezra_on_Genesis.<chapter>.<verse>?version=english` (comments come back as a list per verse, footnotes inside <i class="footnote">). Rashbam: `/api/v3/texts/Rashbam_on_Genesis.<chapters>?version=hebrew&return_format=text_only`. Onkelos: `/api/v3/texts/Onkelos_Genesis.<chapters>?version=hebrew|Targum Onkelos, vocalized according to the Yemenite Taj &return_format=text_only` (the version title ends with a space). Searching needs POST /api/search-wrapper (GET is refused). GitHub: the private repo davidross01/ibn-ezra-commentary (commentary-book-build).
- **Rule 3:** the workbook is in David's Drive; its Appendix B is the glossary; quotations at 1:1, 11:1, 22:1. Useful for later parashot.
- **Reading a review doc:** it gets large (about 2–3 MB through the API). Never read a whole review doc into the conversation: run `read_answers('<key>')` from scripts/workbench/wb.py in the Composio workbench (load line at the top of wb.py). It keeps only ID / Decision / Your note, saves `<rows file>` → answers.json to GitHub and prints a short summary; then `git pull` and read the JSON. The rows' own text is in the repo's rows file. If David's phone can't open a doc, start a new, smaller doc for the next round.
- **Rule 4:** send drafts with SendUserFile; then `refresh_drive()` after the push puts them in "05 Drafts".
- **Rule 5:** `refresh_drive()` (scripts/workbench/wb.py) does the numbering and renames older names in place, so links stay. The booklets are PDFs only; no Google Doc copies.
- **Rule 6:** the folder is id 1ALbmTB3lrzR4Md2y_1mLeXAremu0kZMP. `docs/handbook.json` lists every document (number, title, source, Google Doc id, and the checksums of the last build and the last refresh). `python3 -I scripts/handbook.py build` makes the HTML copies in docs/handbook/ (the Start here copy with the live status from series_status.py); in the workbench `sync_handbook()` replaces each changed doc's content in place (same id, same link), skips a doc with an open comment, and records the refresh; `handbook_comments()` lists David's open comments. `python3 -I scripts/handbook.py --check` lists the copies out of date (series_status prints it; CI warns). The weekly scheduled task is "Ibn Ezra — weekly handbook refresh". The steps are in docs/HANDOFF.md, "Keeping the documents current".
- **Rule 7:** .github/workflows/checks.yml runs `scripts/check_all.py <parasha> --ci` for each parasha, plus `scripts/rulings.py --check`, `scripts/cite_check.py` and the handbook check (a warning only). In CI the layout and pages checks are skipped (no build there) and Ideas are listed, not failed.
- **Rule 8:** the files to attach are listed by finalize-parasha.
- **Rule 10:** `python3 -I scripts/publish_current.py` (`--dry` for the plan, `--force <folders|all>`) after every applied change, then commit, push and `refresh_drive()`. book.json keeps per parasha `stage` (draft / final / audit), `edition` (ISO date) and `built_hash` (scripts/stage.py, `content_hash`: the model, parasha.json without first_page, foot terms, the build scripts; Bereshit's front.json only for its own title page), and `front_hash` for bereshit/data/front.json. A content change sets the edition to today and moves a final parasha to audit; a renumbering alone keeps the edition. A draft not yet committed is replaced; a committed one gets a new number. It stops on a layout warning, on a Chromium version other than book.json's, and when check_all is not clean. series_status prints the stage and edition, and warns "changed since the current edition". Code that asks whether a parasha is published uses `stage.published()` (final or audit), never `status.startswith('final')`.
- **Held changes (rule 10):** when David asks for a change to come in only at a later build, it is not applied to the data. book.json "held" lists it: the ruling, what it changes, the script that makes it, "at" (the parasha whose final ends the hold), the parashot it touches. Its rule is written at once and a new parasha follows it from draft 1. series_status prints it; publish_current.py runs the script when the parasha in "at" is published, removes the entry and rebuilds what changed in the same run; check_all checks the held parashot for what they still say.
- **Rule 9:** the finalize-parasha skill: `python3 scripts/export_parts.py` (the five parts as separate files), `python3 insights/booklet.py <Parasha>` (the davar Torah's quoted English in insights/davar.py must match the book, so change it with the book), `review_round/key_add_parasha.py`, `python3 scripts/publish_pdfs.py --rebuild` (full book and glossary), `refresh_drive()`, archiving.
- **Rule 11:** `docs/drive.json` lists every folder (id, private or not) and the files outside it the guide links to. Docs in a private folder other than -03 are entries in `docs/handbook.json` with `folder` (G00 the guide, S01… the skills, A01… the audit) and are refreshed by `sync_handbook()`; `scripts/handbook.py build` first remakes docs/DRIVE_GUIDE.md (scripts/drive_guide.py), and `--check` lists any skill or profile with no entry. The plain text is plan '06' of `refresh_drive()`. A new private folder is made with the Google Drive connector (create_file with inheritedPermissionsDisabled) and added to drive.json. audit/findings.md is remade from audit/raw/ by `python3 -I audit/tools/findings_md.py`.
