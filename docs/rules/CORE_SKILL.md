---
name: "commentary-house-rules"
description: "The one source of David's house rules for his translated Torah-commentary series (Ibn Ezra etc.): translation, Hebrew, grammar terms (his grammar sheet), misprints, review process, page look. Load it before any work on that series."
---

# House rules: David's commentary translation series

The other series skills point here instead of repeating these rules. This file is the **core**: every rule in one line. The full wording, examples and history of each rule are in the repo davidross01/ibn-ezra-commentary (clone: /home/claude/ibn-ezra-commentary) under `docs/rules/`, moved there word for word on 27 Oct 2026:

| File | Read it when |
|---|---|
| docs/rules/translation.md | translating, writing the verse band, Hashem/Elohim, place names, letters and vowels in the English, glosses |
| docs/rules/grammar.md | any grammar term: David's glossary (Hebrew → English), the grammar sheet, terms_audit |
| docs/rules/hebrew.md | pointing, letters against Sefaria, ketiv/qere, misprints and reference corrections |
| docs/rules/notes.md | writing notes: Onkelos, Rashi, Radak, Rashbam, Ramban, grammar notes, Ibn Ezra's ideas, Sefaria remarks |
| docs/rules/review.md | making, reading or applying a review list; the checks before a draft |
| docs/rules/review_doc.md | building or changing a review Google Doc by hand, archiving one |
| docs/rules/page.md | layout, page numbers, front matter, foot strip, title pages |
| docs/rules/sources.md | accounts, Sefaria endpoints, reading review docs, deliverables |

Read the file for the task at hand before starting it; the one-liners below are a reminder, not the full rule. **Live facts are never kept in a skill**: page numbers and status come from book.json, the state of each review doc from review_docs.json, answers from `<rows file>` → answers.json.

## A new rule from David (do all of it in the same turn)
When David states a rule in chat ("it should be ה׳", "place names are transliterated"), or a review answer sets one for the whole book:
1. **Rule file:** add it to the right docs/rules/*.md, with his words and the date, and commit.
2. **Core line:** add or change its one line here, and propose the skill update (propose_skills) in the same turn.
3. **Check:** if a program can test it (a word, a sign, a pattern, a count), add the test to `own_checks` in scripts/check_all.py, run it on every parasha, and `--accept` only hits that are already right; real hits are fixed or become review rows.
4. **The book:** applying it to drafts David has seen follows the review rules below (a row, unless he says to apply now); a new parasha has it from draft 1.
5. **Rulings log:** if it replaces an older ruling, add an entry to docs/rules/superseded.json (with the stale phrases that would point to the old way) and mark the old bullet "superseded"; then `python3 -I scripts/rulings.py` rewrites docs/RULINGS.md (CI fails while it is out of date). Update the repo copy of every skill you propose a change to (docs/skills/, this file) in the same turn.
6. Say in one line where it was saved and whether the check now covers it.

**At the start of every session** (9 Nov 2026): `python3 -I scripts/skill_sync.py` (saved skills against their repo copies: a copy that differs is a proposal waiting for David, or behind and pulled) and docs/RULINGS.md, "Replaced rulings" first; docs/HANDOFF.md has the map of how the book and the review cycle are built.

## Translation (translation.md)
- The translation is David's own; never present another translation's wording as his. Literal by default; explain obscure passages in the note.
- The verse band follows the commentator's reading, word for word where he comments on a word (check the next and previous verse's comments too); his preferred reading, else the first; awkward English gets [square brackets], not a standard rendering. Ibn Ezra quoting a verse uses that verse's translation.
- Check against Strickman–Silver but never name Strickman, Silver, Weiser, Krinsky or "Sefaria's English edition" in the notes. No "Uncertain" labels and no hedges: state the likeliest reading; doubts go to the Editorial record or a review row.
- הַשֵּׁם is always Hashem in small caps (H{sci}ashem{/sci}), never "the Name"/"the Lord" — except "the secret of the Name" where Ibn Ezra means God's own name (Exodus 23:21; Audit 1 B2). The Name in Hebrew inside the English is ה׳, never ד' (the Hebrew commentary keeps Sefaria's ד'). Where the verse's Name is read Elohim (Lech Lecha 15:2, 15:8), the verse band says Elohim — flag new cases as review rows.
- Place names are transliterated (Sephardi; Ur Kasdim, Mitzrayim, Chevron, Yerushalayim…; the list is in translation.md); names of people and peoples stay; every parasha's review list has a Place names row.
- Letters in the English are the letters themselves ({h}א{/h}); vowels by name with the sign on an alef: kamatz (אָ); dagesh in בּ, mappik in הּ; root types with the letters ({h}פ״א{/h}).
- A word Ibn Ezra defines himself gets no English gloss of ours; never a guessed identification (stone, plant, animal).
- Audit policy (Audit 1, 30 Oct 2026): brackets only where Ibn Ezra explains how a word of that verse works — no identifications, no book-wide word swaps, no readings carried over from another verse; translation rows only for mistranslations and inconsistencies, not smoothing; Hashem's print stays. Bracket rows only for clear cases — where the verse band contradicts his reading or hides it entirely (David, 1 Nov 2026).
- Sephardi transliteration throughout (Shabbat, Bereshit, toledot).

## Grammar (grammar.md)
- Every grammar term is translated by David's glossary in grammar.md, the same way every time; Ibn Ezra's own sense wins (◆ in the key to terms). Unsure → best reading in the note, plus a row in the review's grammar Part. terms_audit runs inside check_book.

## Hebrew (hebrew.md)
- Never retype Hebrew from memory; substitute inside existing strings; match by consonants. Show David pointed Hebrew, no transliteration.
- The letters of the Hebrew commentary are Sefaria's, letter for letter (consonant_check must print differences: 0; fix_letters.py moves vowels onto Ibn Ezra's ו/י). Lemmas and Scripture quotations take the Masorah's vowels (MAM). Every word is pointed in full: Sefaria's own marks are a guide, checked and completed or corrected (check_all "Partly pointed"). Abbreviations, ד', letter names, book names and numbers stay unpointed — except פי', which is written out (פֵּירוּשׁ, or פֵּירֵשׁ / לְפָרֵשׁ where the English reads a verb), the one allowed difference from Sefaria's letters (David, 28 Oct 2026).
- Ketiv/qere in the verse band: written form unpointed, then the reading pointed in [ ].
- Hebrew in the English commentary and notes is copied by script, never typed (David, 28 Oct 2026): Scripture as `{q:Book ch:v:i-j}` (src/tanakh.json, all 39 books), Onkelos as `{o:i-j}`, resolved by work/assemble.py; check_all's "Hebrew sources" traces every span to its source. A made-up grammar example gives way to an attested form with its verse, unless the note calls it hypothetical.
- Misprint: (printed) [correction], the correction pointed, the English follows it, and a {i}Text.{/i} line in the note of the same verse. A wrong reference: correction inside the round brackets: (תהלים קמח ה [קמח ח]). Variants and emendations are David's choice, never silent.

## Notes (notes.md)
- Onkelos is a main commentator on par with Rashi (commentary-onkelos-notes skill): Aramaic copied by script ({o:i-j}), English ours, יְיָ prints ה׳.
- Rashi throughout; Radak where he discusses or notably explains Ibn Ezra; Rashbam wherever useful (only where his text survives on Sefaria); Ramban only where he quotes or adds to Ibn Ezra's view. Keep the preface's list of commentators true.
- Grammar notes explain the point: plain point → "A reader might think …" → proof and why it matters; add to notes, never take away.
- Ideas (David, 30 Oct 2026, and his answers to Audit 1): wherever Ibn Ezra discusses an idea, his science or a “secret”, the note explains it. **Full** paragraph, nothing cut, for real ideas (God's knowledge and will, the soul, prophecy, providence, creation, the image of God, free will): the idea in detail and what a reader would otherwise think; “why he brings it here” only where the verse prompts it. **3–4 sentences** for background (spheres, the three worlds, astrology). A hint is explained with its source named. Avi Ezer for every idea and hint and wherever it notably explains him; Rambam wherever he discusses the same idea; no Aristotle; never Krinsky's Mechokekei Yehudah. All read on Sefaria. Every idea paragraph is a row in the review list's own Ideas Part (Keep / Approve), in a new parasha as in an audit, so David decides which to keep (David, 30 Oct 2026). check_all “Ideas” lists the places; review/ideas.json records the verses done (--accept never hides them).
- **Idea paragraphs, fixed order** (David, 8 Nov 2026): what Ibn Ezra says → what a reader would otherwise think → **Ibn Ezra by Ibn Ezra** (Yesod Mora, his comments on other verses and books; Avi Ezer on his words) → **Saadia**, *Emunot veDeot* on the **same idea**, not just the same verse, treatise and chapter named, read on Sefaria (*HaEmunot veHaDeot*, Ibn Tibbon's Hebrew) → Rambam after him. Limit: Ibn Ezra's own writings and Saadia one or two sentences each; nothing is said where Saadia has nothing. Parashot already written: add sentences only (no rewriting), one row each, in an “Ideas Audit — <Parasha>” doc per parasha; kept and “not needed” places are raised again where these sources add something. `<folder>/review/idea_sources.json` records what was read for every place in ideas.json; check_all lists “Idea sources” not yet recorded.
- A note never mentions the review list, "not checked", "agrees with Sefaria", "checked on Sefaria" or headword remarks; a Text line only when something differs. No per-section source lines. Run review_grammar/all/clean.py --check before each draft; when the Editorial record grows, refresh its Google Doc (review_grammar/all/make_record.py, then the doc in place).

## Review (review.md)
- When David asks to add or change something, it becomes a review row; no new draft unless he asks for one, says to apply answered rows, asks for a layout fix, or says yes to applying now when asked with checkboxes.
- One review doc per parasha (Google Doc in davross846, Decision chips, Explanations tab, Sefaria column with a one-word link); archive it when applied and David says. Only answered rows are applied; read the list's own "How to use" for what Approve/Keep mean; never overwrite David's Decision or note.
- Where Now and Alternative render Hebrew (verse translation, Ibn Ezra's English), the **Now box opens with that Hebrew**, its own line (David, 8 Nov 2026); make_rows does it, `heb_box` where its choice is wrong.
- Every review list has an **Ideas Part** (Ibn Ezra's ideas, science, hints), with its sources named, Keep / Approve. Since 8 Nov 2026: the draft goes without the additions; **one short row per added sentence**, Now = the note without it, Alternative = with it, in the fixed order (Toledot List 1 F1–F18 and the Ideas Audits are the models; the one-paragraph rows of Audit 2 Part F are superseded).
- **One row per item** — never several misprints, names or changes bundled in one row; and every parasha's list has the **names of people**, one row each, with the name as it stands and its alternative spelling (Rebekah / Rebecca; Chayei Sarah List 1 Part H is the model) (David, 2 Nov 2026).
- **Confirmed names are not asked again** (David, 5 Nov 2026): a name David has already confirmed in a review keeps that spelling, with no new row; only new names go into the names Part. The list is `docs/rules/confirmed_names.json` (name → the row that settled it); add to it whenever he answers a names row. make_rows.py stops on a names row for a confirmed name.
- **Explanations**: the Hebrew line (Ibn Ezra's, or the verse when the row gives none), then the sentence as it stands and as changed, each with English; a by-hand row gives `changed` (and `changed_he`); review_audit/make_rows.py prints EXPLANATION WARNINGS otherwise, fixed before the doc is built (4 Nov 2026).
- Read answers with `read_answers()` or `review_status()` (scripts/workbench/wb.py, in the Composio workbench), never by loading the whole doc into the conversation.
- Explain rows with `python3 -I scripts/explain_rows.py <review> <IDs | --discuss>` (from the repo; no Google call) — explain-commentary-row.
- Discuss rows: explain plainly, then ask with checkboxes in the same turn; save his chat answer to `<rows file>` → chat_answers.json ({id: {decision, note, date}}), which counts as his answer when applying (his chip in the doc is never changed). A rule David states once becomes standing only when saved here (see "A new rule from David").
- Before each draft: `python3 -I scripts/check_all.py <folder>` — read every NEW hit, then `--accept`. Also read the front matter when a rule changes.
- Bringing a parasha already written up to the current rules: the commentary-audit skill (rule fixes applied with a log, judgment calls as one detailed review doc per parasha, Parts A–F; renumber once at the end).
- Bereshit's model changes only through `bereshit/work/changes.py` (`C(row, sec, (ch, v), old, new)`), rebuilt by `python3 -I bereshit/work/build_model.py`; never edit model_final5.json by hand. Other parashot change in work/chN.py (review_round/subs.py), then work/assemble.py.

## Page look (page.md)
- Seforno-volume template: verse band (Hebrew 19.6/28 px, English on the same first line, פ/ס marks, new paragraph at a chapter), Hebrew commentary, English commentary, two-column notes (no chapter numbers), foot strip of very simple definitions.
- Comments go on the page of their verse; notes stay with it where they fit (NB = 100, STRETCH 0.15 — don't tighten); no overlap warnings in a draft that is sent.
- One book, page numbers continuous from book.json; a page-count change means rebuilding every later parasha and its booklet. Front matter (i–x) once at the start; each parasha has its own title page and ends פ פ פ.
- One Chromium version per parasha (book.json "chromium"; check_all fails on a mismatch): rebuild an older parasha only where its version is installed. Since the audit rebuild (3 Nov 2026) every parasha is on 153.
- Licensing and print set-up not decided: don't change credits, trim, margins or font embedding.

## Sources and delivery (sources.md)
- Google files only in davross846@gmail.com (Composio googledocs_spinet-dirk, googledrive_pulse-dwang); never filmgoingpro. GitHub through Composio: default account.
- Sefaria through the Sefaria MCP tool (endpoints in sources.md); Rashi, Talmud and Midrash comparisons checked there.
- Drafts: "<Commentator> <Parasha> - draft N.pdf" / "- final.pdf", sent with SendUserFile with page count and what changed, and put in the Drive folder ("05 Drafts") with refresh_drive() after the push — every draft. Making a parasha final is one chain: finalize-parasha (export, booklet, full book, Drive folder, archiving).
- Drive: no full book (over the 5 MB limit; it stays in GitHub); parasha files and booklets numbered in Torah order, "01 Bereshit.pdf", "01 Bereshit - Key Insights.pdf" (refresh_drive does it). The booklets are PDFs only; no Google Doc copies.
- Every push runs check_all on GitHub (CI); a red X means a new hit or a broken script: read it and fix or --accept before going on, the same session.