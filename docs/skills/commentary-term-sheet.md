---
name: "commentary-term-sheet"
description: "Keep one English for each recurring Hebrew phrase and one spelling for each name across David's Ibn Ezra book: find the recurring phrases by program, put the choices to David in a term sheet, then check every parasha against it."
---

# The term sheet: one English for one Hebrew phrase

review.md, rule 8, says one English for one Hebrew phrase across the book, and grammar.md does this for grammar terms through David's grammar sheet. This skill does the same for everything else that recurs: Ibn Ezra's own turns of phrase, his words for kinds of meaning and conduct, words he uses in a fixed sense, and the names of people. The choice of English is always David's; this skill finds the places and keeps the book to his choice. Load commentary-house-rules first.

## When
- Before a new parasha's first draft is sent: check the draft against the sheet.
- When a review answer changes the English of a recurring phrase or a name.
- When David asks for the term sheet, a term check, or why a word is translated two ways.

## 1. Find the candidates (by program, never by memory)
- From `export/ibn_ezra_hebrew.json`, strip vowels and cantillation and collect every phrase of one to four words that occurs in at least two comments. Drop quoted verses (they follow the verse band), grammar terms already in the glossary, and common function words.
- For each phrase list every place: parasha, verse, the Hebrew clause copied from the model, and the English sentence that translates it from `export/ibn_ezra_english.json`.
- For names: collect every proper name in the English commentary and the notes and group spellings that differ by one or two letters or by a known pair (a person called by two names).
- Hebrew is copied by program and shown pointed; it is never typed and never transliterated.

## 2. Put the choices to David
- A phrase whose English is the same everywhere needs no row; it goes into the sheet as settled.
- A phrase with two or more renderings is one row per phrase in a term sheet (a Google Sheet in davross846, account `david-personal`, with a dropdown of the renderings found plus "Other" and "Depends on the place"), showing each place and its English. Give the link.
- "Depends on the place" is a real answer: Ibn Ezra uses some words in more than one sense. Then David marks which places take which English, and the sheet records the senses.
- Places David has already decided stay as he decided (grammar.md, rule 4); show them as decided, not as open.

## 3. Keep the book to the sheet
- David's answers are saved in the repo as the term sheet data, beside the grammar glossary, and each answer that sets a rule for the whole book follows "A new rule from David" in commentary-house-rules (the rule written once, a numbered ruling).
- A check in `own_checks` (scripts/check_all.py) flags any place where a phrase on the sheet has an English that is not on the sheet, and any name spelled another way. If the script for steps 1 and 3 is not in the repo yet, write it under scripts/, run it on every parasha, and say so.
- Changing the book to match the sheet follows review.md, rule 1: each change in a parasha David has seen is a review row unless he says to apply now; a new parasha has the sheet from draft 1.
- The key to terms and the foot-of-page strip must agree with the sheet (grammar.md, rule 2).

## Report
One or two lines: how many recurring phrases, how many settled, how many open rows, and the link to the sheet.