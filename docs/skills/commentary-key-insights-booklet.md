---
name: "commentary-key-insights-booklet"
description: "Make the short Key Insights companion booklet for a parasha of David's translated Ibn Ezra commentary: chosen insights with verse, Ibn Ezra's words, explanation and other commentators."
---

# Key Insights booklet (one per parasha)

A small companion to the full commentary: about 12–15 of Ibn Ezra's key insights on the parasha — his main views on its words and on its story — in verse order. David asked for it in Oct 2026 and said: **don't ask him to approve the insights or the format — choose them and just make it.** Load commentary-house-rules first (Hashem in small caps, Rashi/Rashbam/Radak/Ramban rules, never name Strickman, Silver, Weiser or Krinsky).

## When
- Build it when a parasha has a draft; rebuild it when the parasha becomes final (Noach's first booklet was from draft 1).
- No review list for the booklet itself, unless David asks.

## Each insight (insights/data.py in davidross01/ibn-ezra-commentary)
- `id` (B1…, N1…), `title` (one line, his point), `verses` shown, `comment_at` (verse whose comment holds the point, for the page reference).
- `he` / `en`: (start, end) fragments; `insights/source.py` cuts the Hebrew from the book's Hebrew commentary and the English from its English translation, so nothing is retyped. Every fragment must be found (it prints MISSING otherwise). A fragment may come from any verse in `verses` or `comment_at`.
- `explain`: 2–4 plain sentences, stating only what the commentary says (check against the English commentary before writing; don't add claims).
- `COMPARE[id]`: how other commentators read it, summarised **only from the book's own notes** for those verses (grep the notes for Rashi, Rashbam, Radak, Ramban, Saadia, Onkelos). Leave it out where the notes have nothing useful.
- Choose insights that carry his view or the story's arc: method (plain sense, "the Torah speaks in human language"), theology, his disagreements with the Gaon or the midrash, and turning points of the story. Skip pure grammar.

## Build
- `python3 insights/build.py B "insights/booklets/Ibn Ezra on <Parasha> - Key Insights.pdf" <Parasha>` — look B, A5 and compact (David, Oct 2026: reduce the spacing and the font so more fits on a page). **No cover page and no "About this booklet" page**: the booklet opens straight on the first insight. One insight per block (verse Hebrew + translation, Ibn Ezra in a shaded box, explanation, OTHER COMMENTATORS, "Full commentary … page N"), page numbers in the footer. Page numbers come from the parasha's build/rep.json (rebuild the parasha first if build/ is stale).
- The compact look lives in `CSS_B` in insights/build.py (page margin 10mm 11mm 11mm; body 10pt/1.3; headings 13pt; Hebrew verse 13pt; Ibn Ezra box 9.5pt with 5px 9px padding; comparison 9pt). Do not enlarge it again. Bereshit and Noach come out at 8 pages each.
- Add the parasha to MODELS/REPS and PAR in source.py/build.py.
- Look at a contact sheet of every page (pdftoppm) and one page close up: Hebrew RTL, small caps, no overflow.
- Commit data and PDFs, note it in README ("Key Insights booklets"), push, and send both PDFs with SendUserFile.