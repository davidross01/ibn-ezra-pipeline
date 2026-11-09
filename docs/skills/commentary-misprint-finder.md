---
name: "commentary-misprint-finder"
description: "Scan a printed Hebrew commentary for misprints and wrong references and turn the findings into review-list rows in (printed) [correction] form."
---

# Misprint finder for a Hebrew commentary

Use when preparing a commentary (e.g. Ibn Ezra) for David's translation series, or when he asks to check a text for misprints. Load **commentary-house-rules** first (Hebrew letters, the (printed) [correction] form, the review process).

## Sources to compare
- The vowelled edition being translated (the book's own Hebrew; never alter its letters).
- The verses themselves (Sefaria Tanakh) for every quoted verse and reference.
- A word-frequency lexicon from the Tanakh and the same commentator on other books (Step 1).
- The standard published translation and its notes (Ibn Ezra: Strickman–Silver) for readings it already corrects.
- Sefaria's text of the same commentary, but only to restore letters lost in the PDF text layer (see below).

## What the Bereshit test taught (Oct 2026)
Run against Ibn Ezra on Gen 1:1–6:8, where 21 letter misprints and 6 wrong references were already known:
- The automatic pass found 16 of 21 letter misprints, all with the right correction, and 5 of 6 wrong references, with about 50 false candidates to read through.
- **Sefaria's Ibn Ezra (Piotrkow) carries the same misprints as this edition**, so a letter-for-letter diff with it found none of them. It is not an independent witness.
- The five misses were all slips that make another real word (העובד for העובר, אלך for איך, העץ for העין, הקרש for הקדש, ממך for סמך). Only a reading pass catches these.

## Step 1 — Build the lexicon and verse texts
With the Sefaria MCP tool, fetch one whole book per call (`/api/v3/texts/<Book>?version=hebrew&return_format=text_only`): every Tanakh book the commentary cites (count the cited books first), plus the same commentator on other books (e.g. Ibn Ezra on Exodus, Leviticus, Deuteronomy, Isaiah). Parse the saved results into one texts.json, and count consonant-only words (finals normalised) into a frequency lexicon. About 47,000 distinct words was enough.

## Step 2 — Automatic checks (script: scripts/misprint_scan.py in the project)
Run on the printed text: drop existing [corrections] and strip markup and the {s}references{/s}.
1. **Non-words with a look-alike fix.** A word seen ≤3 times is a candidate if a one-letter change gives a common word. The classic print confusions ה/ח, ד/ר and ד/ה need the fix to occur ≥5 times and ≥5× as often. The other swaps (מ/ס, ו/ז, כ/ב, ו/י, ר/ת, נ/ג, ט/מ, ת/ח, ע/צ, ב/נ, ו/א) and a dropped letter (לל→לכל) need ≥20 and ≥20×. Rank the classic confusions first; that is what made מוה→מוח and הולה→חולה come out right.
2. **Rare real words next to a very common look-alike** (the fix occurs ≥200 times and ≥60× as often). This catches והנח for והנה.
3. **Quote vs verse, word by word.** For every "quotation" followed by a reference, flag any quoted word that is missing from the verse when its look-alike is in the verse (או for אז in Job 11:15, ממפר for מספר).
4. **References.** Numerals must be valid Hebrew numbers (בב is not). If the quoted words aren't in the cited verse, search the whole Tanakh for them and propose the place found, preferring the same book (Exodus 26:6→26:20, Joshua 5:13→8:13, Nehemiah 6:10→6:6). Compare with spelling differences ignored (plene/defective), or you will miss cases like Leviticus 25:29.
5. **Headings.** Each lemma must match a word of its verse, allowing one look-alike letter (כתנור → כתנות).

## Step 3 — Read every candidate in context
Read about ten words either side and drop the false ones. Common false alarms:
- Abbreviations once the quote marks are stripped (ואח"כ, הי', מהד').
- Grammar terms (הנח "quiescent", הנעלם "hidden").
- Rare but correct words (קרם, חדים, להט, הבה).
- References to verses outside the fetched books.

## Step 4 — Reading pass for real-word slips
Read each paragraph for sense, slowly, at every word that has a look-alike neighbour, and ask whether the sentence reads better with the swap. Check every place where Strickman–Silver translates something other than the printed word. Record the evidence for each find. If no witness and no clear sense supports a change, mark it "Uncertain" and propose nothing.

## Step 5 — Variants
Record edition brackets and variant readings (צ"ל, נ"א, manuscripts) as C rows. They are translation choices, never silent fixes.

## Output: review-list rows
One row per finding, grouped: B = misprints and wrong references, C = variant readings and hard passages.
- ID | Where (verse + lemma) | Issue ("אהר for אחר") | Now: Hebrew with (printed) [correction] + English following the correction | Alternative: printed form only (or the other reading) + its English | Decision | Your note.
- Show the Hebrew line itself (pointed, no transliteration) and the English on the next line.
- Say in the Issue cell what supports the correction (the verse, the sense, Strickman, a manuscript, lexicon frequency).
- Build or update the list with the review-list-google-doc skill. Apply nothing to the book until David answers (apply-review-decisions).
- Report the counts: candidates found, kept after reading, and how many came only from the reading pass.