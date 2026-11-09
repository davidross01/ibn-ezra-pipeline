---
name: "commentary-onkelos-notes"
description: "Add Onkelos lines to the notes of a parasha of David's Ibn Ezra book: Onkelos is a main commentator on par with Rashi; Aramaic copied by script from Sefaria."
---

# Onkelos in the notes

Use when building a new parasha of David's translated Ibn Ezra book (repo davidross01/ibn-ezra-commentary), or when rebuilding one. Load commentary-house-rules and commentary-book-build first.

## The rule (David, Oct 2026)
Onkelos is a main commentator in the notes, **on par with Rashi**. He gets a line wherever his reading bears on Ibn Ezra's: where he agrees, where he reads the word differently, and wherever Ibn Ezra cites "the Translator" (the Aramaic translator). Each line gives the Aramaic words and an English rendering. Applies to every parasha from the first draft.

## How the lines are made
- **Source text:** Sefaria's "Targum Onkelos, vocalized according to the Yemenite Taj" (CC-BY-SA), saved per verse in `<parasha>/src/onkelos.json`. The credit stays in the preface and in "How this edition was made" (bereshit/data/front.json).
- **The Aramaic is never retyped.** Write `{o:i-j}` (words i to j of Onkelos on the note's verse) or `{o:ch:v:i-j}` (another verse); `scripts/onk_lib.py` copies the words from onkelos.json and wraps them in {h}...{/h}. The English rendering is Claude's own, written in the line.
- **Entries** go in `<parasha>/work/onkelos.py`:
  - `A(ref, text, before=None, lemma=None)` adds a line to the verse's note: before the first Rashi sentence by default, before the text `before`, or `before='END'` (before the {i}Text.{/i} line, or at the end). `lemma=` picks the note whose heading starts with that lemma when a verse has several.
  - `S(ref, old, new)` changes existing wording in the note (old must occur exactly once), e.g. to add the Aramaic to "as Onkelos renders it".
- **Applying:** noach, lech_lecha and vayera: `work/assemble.py` applies onkelos.py when it builds data/model.json. Bereshit's model is edited in place, so `bereshit/work/apply_onkelos.py` always applies the lines to the copy data/model_final5_pre_onkelos.json and writes data/model_final5.json (safe to rerun).
- A line that would need a new note stops the script for Bereshit; give a lemma and add the note deliberately.

## Rules inside the lines
- The Name: Onkelos writes the Name as יְיָ; the script prints it **ה׳** (the Name in Hebrew inside English is ה׳, never ד'). It refuses a quotation that includes a prefixed Name form (e.g. ending on וַייָ with another prefix): end the quotation before it.
- In English, God's name is Hashem in small caps (the script converts "Hashem" to H{sci}ashem{/sci}). Never "the Name" for הַשֵּׁם; write "as ה׳" or "of Hashem".
- Say exactly what Onkelos says; if the printed text differs from what Rashi or Ibn Ezra attribute to him, state both (Bereshit 6:6 gives both).
- Quote only the words that carry the point; keep each line to one or two sentences.
- Verse-band translation still follows Ibn Ezra's reading; Onkelos lines compare, they do not change the verse.

## Steps for a new parasha
1. Fetch Onkelos for the parasha from Sefaria (Onkelos Genesis, version vocalized per the Yemenite Taj) into src/onkelos.json.
2. Go verse by verse through Ibn Ezra's comments and the notes; list every place Onkelos bears on the comment, plus every "the Translator".
3. Write work/onkelos.py, run assemble (or apply_onkelos.py), fix any 'anchor not once' or 'out of verse' stop.
4. Run scripts/check_book.py; check by program that each quoted Aramaic word occurs verbatim in onkelos.json and that no note says "the Name".
5. Count the lines for the delivery message (Oct 2026 counts: Bereshit 50, Noach 25, Lech Lecha 35, Vayera 46).