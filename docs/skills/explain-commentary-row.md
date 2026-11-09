---
name: "explain-commentary-row"
description: "Explain one or more rows of David's review list for a commentary translation (e.g. 'explain B1', 'explain the Discuss rows'), showing the Hebrew, the sentence as it stands and if changed, with English."
---

# Explain review-list rows

Use when David asks "explain B1", "what does C7 mean", "explain E2 and what unpointed means", "explain the Discuss rows", or similar, about a review list of his Ibn Ezra series (or another translation/commentary book). Load **commentary-house-rules** first (Hebrew handling, misprint form).

## Get the material from the repo, not the doc
1. `git pull` davidross01/ibn-ezra-commentary (clone to /home/claude/ibn-ezra-commentary if missing).
2. If David may have answered since the last read (he says he answered, or the row's answer matters), refresh the answers first: in the Composio workbench load scripts/workbench/wb.py (load line at its top) and run `read_answers('<review>')`, then `git pull`. Otherwise skip this: the row text never changes after the doc is built.
3. Run `python3 -I scripts/explain_rows.py <review> <IDs>` — or `--discuss`, `--change`, `--open`, `--noted` for a whole group. `<review>` is part of the title, the parasha, or the doc id (review_docs.json). It prints, per row: Where, Issue, Now, Alternative (verbatim), the Explanations-tab text (as it stands / if changed), the Sefaria link, David's answer and note, and any answer he gave in chat. Never read the whole Google Doc for this (2–3 MB).
4. If the row needs more context than it holds (the whole sentence around a word, another verse with the same word), take it from the model (`<folder>/data/model.json`; Bereshit data/model_final5.json: Hebrew commentary, English commentary, notes, verses) by consonant match — strip vowels and cantillation — never typed from memory.

## Answer format (in chat, unless asked to put it in the doc)
1. **Always include the review doc's link** (the script prints it).
2. For each row, in ID order, kept short:
   - **Where and what.** One line: verse + lemma, and the issue in plain words (e.g. "the printed אהר is a misprint for אחר, 'other'").
   - **The Hebrew line itself.** Pointed, no phonetic transliteration.
   - **As it stands.** The full Hebrew sentence (whole clauses around the word), then its English translation exactly as the book has it.
   - **If changed.** The same sentence under the Alternative, then its English. If only one side changes, say so plainly ("Hebrew: the same" / "English unchanged; only the Hebrew display changes").
   - **What each choice means for the book.** One or two sentences, including whether the standard translation (Strickman–Silver) agrees, and the likeliest reading where the evidence is thin; when a row depends on another (E2 on C3), say so and which to answer first.
3. Explain any term David asks about ("what unpointed means") in plain words with one real example from the book.
4. Optionally, a one-line recommendation clearly marked as mine.

## Example (B1)
- 2:7 באפיו — the printed אהר is a misprint for אַחֵר ("other").
- As it stands: וְיָבִיאוּ אֲוִיר (אהר) [אַחֵר] — "they let out the hot air from the heat of the heart and bring in other air."
- If changed (printed form only): וְיָבִיאוּ אֲוִיר אהר — English unchanged; only the Hebrew display changes.

## Discuss rows and unclear notes: settle them in the same turn
- After explaining a Discuss row (or a Change note that can be read two ways), ask the decision with AskUserQuestion checkboxes in the same turn — one question per row, up to four per call, options from the row (e.g. "Approve: the Alternative", "Keep: as it is", and a third reading of his note if there is one).
- Save each answer to `<rows file>` → `chat_answers.json` as {id: {decision, note, date}} (create it if missing), commit and push. apply-review-decisions reads it after answers.json. Never change David's Decision chip or note in the doc.
- If David's note asks for something the row didn't offer (C3: "expand them so it says the whole word"), restate it as a concrete change (what the Hebrew would become, which places) inside the question, so his checkbox answer is unambiguous.

## Rules
- Explaining is read-only for the book and the doc; only chat_answers.json is written.
- For several rows, keep each explanation short and in ID order.
- If David wants the explanations inside the doc, use the Explanations-tab method (review-list-google-doc, docs/rules/review_doc.md).