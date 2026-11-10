---
name: "commentary-house-rules"
description: "The one source of David's house rules for his translated Torah-commentary series (Ibn Ezra etc.): translation, Hebrew, grammar terms (his grammar sheet), misprints, review process, page look. Load it before any work on that series."
---

# House rules: David's commentary translation series

The rules live in the repo davidross01/ibn-ezra-commentary (clone: /home/claude/ibn-ezra-commentary), **each written once**, in `docs/rules/`. This skill does not repeat them: it says which file to read, how David works, and what to do when he gives a new rule. **Before a task, read the whole rule file(s) for it** — the index at the end only helps find a rule.

| File | Google Doc in "-03 How it is made" | Read it when |
|---|---|---|
| docs/rules/translation.md | 04 Translation | translating, the verse band, Hashem / Elohim, place names, letters and vowels in the English, glosses |
| docs/rules/grammar.md | 05 Grammar | any grammar term: David's glossary, the grammar sheet, terms_audit |
| docs/rules/hebrew.md | 06 Hebrew | letters and vowels against Sefaria, ketiv/qere, Hebrew inside the English, misprints |
| docs/rules/notes.md | 07 Notes | writing notes: Onkelos, Rashi, Radak, Rashbam, Ramban, Avi Ezer, grammar notes, Ibn Ezra's ideas |
| docs/rules/review.md | 08 Review | making, reading or applying a review list; the checks before a draft |
| docs/rules/review_doc.md | 09 Review doc | building, changing, finding or archiving a review Google Doc |
| docs/rules/page.md | 10 Page | layout, page numbers, front and back matter, foot strip, title pages, the build |
| docs/rules/sources.md | 11 Sources | accounts, Sefaria, drafts and finals, Drive, the documents folder, CI, Releases |

Each file has two parts: **the rules** (for David: the rule, an example, why, and the rulings it rests on) and **For Claude** (how each rule is done and checked). Every ruling — when, David's words, where — is numbered in `docs/rules/rulings.json`, shown as docs/RULINGS.md ("03 Rulings"); replaced rulings are in `docs/rules/superseded.json` and must never be followed. **Live facts are never kept in a skill or a rule**: page numbers and status come from book.json, the state of each review doc from review_docs.json, answers from `<rows file>` → answers.json, and all of it from `python3 -I scripts/series_status.py`.

## Working with David
- Before complex work: 3–4 clarifying questions with the interactive checkboxes; then do it fully, covering edge cases.
- Brief (1–2 sentence) suggestions for automation, templates or skills when relevant; say when another model or Claude feature fits better, before running the task.
- Show Hebrew pointed, never transliterated (hebrew.md, rule 14). Whenever a review doc is mentioned, give its link.
- Only David saves skills, from the propose_skills card; `docs/skills/pending.json` lists cards waiting; remind him briefly at the end of a task.
- Commits end with the session's Co-Authored-By / Claude-Session lines.

## At the start of every session
docs/HANDOFF.md, "Start of the session": pull, `scripts/skill_sync.py`, read docs/RULINGS.md ("Replaced rulings" first), `scripts/series_status.py`, and read David's open comments on the documents (`handbook_comments()` in the workbench) — each is a new rule (below) or a question to answer under his comment.

## A new rule from David (do all of it in the same turn)
When David states a rule in chat, in a comment on one of the documents, or a review answer sets one for the whole book:
1. **The rule:** write it into the right docs/rules/*.md as a numbered rule — **Rule** (plain English), **Example**, **Why**, and its ruling number — in plain words for David, with no date and no script names; put how it is done and checked into that file's "For Claude" part. If it changes an existing rule, rewrite that rule rather than adding a second one: each rule is written once.
2. **The ruling:** add an entry to `docs/rules/rulings.json` (next number, date, David's words, where he said it, the rule). If it replaces an older ruling, add an entry to `docs/rules/superseded.json` with the stale phrases that would point to the old way, and remove the old wording from the rule file.
3. **Check:** if a program can test it (a word, a sign, a pattern, a count), add the test to `own_checks` in scripts/check_all.py, run it on every parasha, and `--accept` only hits that are already right; real hits are fixed or become review rows.
4. **The book:** applying it to drafts David has seen follows review.md, rule 1 (a row, unless he says to apply now); a new parasha has it from draft 1.
5. **Regenerate and refresh:** `python3 -I scripts/rulings.py` (RULINGS.md and the index below), `python3 -I scripts/handbook.py build`, commit and push, then `sync_handbook()` in the workbench so the Google Docs match (sources.md, rule 6). Propose the skill update (propose_skills) when this file's index changed, and update the repo copy of every skill you propose a change to (docs/skills/, this file).
6. Say in one line where it was saved, its ruling number, and whether the check now covers it.

## Index of the rules
Made by `scripts/rulings.py` from the rule files; read the file itself before acting on a rule.

<!-- index -->
- **translation.md** (04 Translation): 1 The translation is yours · 2 Literal by default · 3 Checked against the standard translation, never named · 4 No "Uncertain" labels and no hedges, except "it seems" · 5 The verse band follows Ibn Ezra's reading · 6 Ibn Ezra quoting a verse uses that verse's translation · 7 How far the audit goes: brackets in the verse band · 8 Bracket rows only for clear cases · 9 Hashem for "the Name" · 10 The Name in Hebrew inside the English is ה׳ · 11 "Elohim" where the Name is read Elohim · 12 Sephardi transliteration · 13 Place names are transliterated, not translated · 14 Letters and vowels are shown, not spelled out · 15 A word Ibn Ezra defines himself gets no translation of ours · 16 "Its parallel", not "its brother" · 17 Grammar terms
- **grammar.md** (05 Grammar): 1 One English for each term, from your grammar sheet · 2 The key to terms and the foot strip match the translation · 3 When unsure, ask in the review · 4 Places you have already decided stay as you decided
- **hebrew.md** (06 Hebrew): 1 The source's letters are never changed, and Hebrew is never typed from memory · 2 The Hebrew commentary has Sefaria's letters, letter for letter · 3 Ibn Ezra's own spelling in the headings · 4 Written and read forms (ketiv and qere) in the verse band · 5 The verse band follows the Masorah's spelling · 6 Every word is pointed in full; Sefaria's vowels are a guide · 7 Quotations of Scripture take the Bible's vowels · 8 The vowels of Ibn Ezra's own words are ours, and the book says so · 9 The abbreviation פי' is written out · 10 Hebrew in the English commentary and the notes is copied, never typed · 11 A misprint is shown as (printed) [correction] · 12 A wrong verse reference is corrected inside its brackets · 13 Variant readings are your choice · 14 Hebrew with its vowels, no transliteration · 15 Every change to Bereshit goes through its change list
- **notes.md** (07 Notes): 1 Onkelos: a main commentator, on par with Rashi · 2 Rashi throughout, with the sources he rests on · 3 Radak where he discusses or explains Ibn Ezra · 4 Rashbam like Rashi, wherever useful · 5 Ramban only where he quotes or adds to Ibn Ezra · 6 Avi Ezer wherever it explains Ibn Ezra · 7 The preface's list of commentators stays true · 8 A grammar note explains the point, not only states it · 9 Ibn Ezra's ideas get a full paragraph · 10 Idea notes: length and sources · 11 Idea notes in the old style, with Saadia and Ibn Ezra's own writings · 12 The idea places are found in Ibn Ezra's Hebrew too · 13 Every idea sentence is checked against its source · 14 A note is part of the book · 15 No remarks about Sefaria or the printed headings · 16 No source line at the end of each section
- **review.md** (08 Review): 1 What you ask for becomes a review row, not a new draft · 2 A new draft only when you ask for one · 3 Every open question is a row · 4 One review list per parasha, kept in Drive · 5 An Ideas Part · 6 Place names and names of people · 7 One row for each proposed change; places that only confirm the draft are bundled · 8 One English for one Hebrew phrase, across the book · 9 Every row says why, in plain words · 10 The Now box shows the Hebrew it translates — the clause only · 11 An idea row's Alternative is the English paragraph alone · 12 Every Explanation shows the Hebrew and the text both ways · 13 Each row says plainly what each answer does · 14 A Sefaria link on rows about the text · 15 A progress line · 16 Only answered rows are applied · 17 Discuss rows are explained, then asked with checkboxes · 18 Your Decision and Your note are never overwritten · 19 Sefaria is checked when you ask, before applying · 20 A row that has to be done by hand is never skipped · 21 Every check is run before a draft · 22 An older parasha is brought up to new rules by an audit · 23 A rule you state once becomes a standing rule
- **review_doc.md** (09 Review doc): 1 A Google Doc in your account, answered with dropdowns · 2 How a doc is laid out · 3 Every doc has an Explanations tab, linked both ways · 4 The house design · 5 Verse-against-comment rows: one per verse · 6 Checked before it goes out · 7 A doc you have started is never rebuilt · 8 Ask for any review by name · 9 Finished docs are archived, never deleted
- **page.md** (10 Page): 1 What is on a page, in order · 2 The verse band · 3 Section marks · 4 Comments go on the page of their verse · 5 Notes stay with their verse's page · 6 Lemmas in bold · 7 The foot-of-page definitions are very simple · 8 Each parasha opens with its own title page · 9 One book, page numbers carried on · 10 The front matter, at the start of the book only · 11 A glossary at the back of the book · 12 Front and back pages end above the foot · 13 Licensing and print set-up wait for you · 14 One browser version per parasha · 15 One shared set of build scripts
- **sources.md** (11 Sources): 1 Google files only in your own account · 2 The texts come from Sefaria, and the comparisons are checked there · 3 Your grammar workbook is a help, not a witness · 4 Drafts: when they are sent and what they are called · 5 The Drive folder: no full book; parashot numbered in order · 6 How the book is made, kept in Drive and kept current · 7 Automatic checks on every push · 8 Each finished edition is a GitHub Release · 9 When a parasha becomes final · 10 Three stages, and only the current version anywhere
<!-- /index -->
