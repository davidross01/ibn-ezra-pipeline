---
name: commentary-ideas-audit
description: Go through a written parasha of David's Ibn Ezra series and make its Ideas Audit review doc — Ibn Ezra explained by his own writings and Saadia's Emunot veDeot on the same idea, added in the fixed order, one row per sentence.
---

# Ideas Audit for a written parasha

Use when David asks to bring the idea notes of a parasha that is already written up to the rule of 8 Nov 2026 ("give each idea paragraph a fixed order; bring in Saadia on the same idea, not just the same verse; use Ibn Ezra to explain Ibn Ezra first; keep a limit"), or to "go through the parashot and make a review sheet" for it. For a new parasha's draft, use **ibn-ezra-idea-notes** instead: the paragraphs are written in the order from the start and go into the draft's own Ideas Part.

Load **commentary-house-rules** first. The rule is docs/rules/notes.md, "Idea notes: a fixed order, Ibn Ezra first, Saadia, and a limit"; the review rules are docs/rules/review.md. Repo: davidross01/ibn-ezra-commentary at /home/claude/ibn-ezra-commentary. Models: `review_audit/ideas_ber_rows.py` (15 rows), `ideas_noach_rows.py`, `ideas_ll_rows.py`, `ideas_vay_rows.py`, `ideas_cs_rows.py`; shared helpers in `review_audit/ideas_common.py`.

## 1. List the places
- `<folder>/review/ideas.json` lists every idea place of the parasha ("done …", "kept as it was …", "not needed: …").
- `python3 -c "import sys; sys.path.insert(0,'scripts'); import ideas_scan; print(ideas_scan.sources_todo('<folder>'))"` lists the places not yet recorded in `<folder>/review/idea_sources.json`. Every place is read, including those David kept (Keep) and those judged "not needed": raise them again where Ibn Ezra's own writings or Saadia add something (his choice of 8 Nov).
- Pull each place's note text from the model (`<folder>/data/model.json`; Bereshit `data/model_final5.json`) to a scratch file, so the sources are read against what the note already says.

## 2. Read the sources on Sefaria (Composio workbench; the shell cannot reach Sefaria)
- **Ibn Ezra by Ibn Ezra first**: `/api/links/Genesis.<c>.<v>` and `/api/related/Ibn_Ezra_on_Genesis.<c>.<v>` for his other commentaries that touch the verse; *Yesod Mora*; and every place he says "as I will explain" / "as I explained" or "the secret of …" (e.g. Exodus 6:3 on El Shaddai, Deuteronomy 1:2 on "the secret of the twelve", Psalms 73:24 and 49:16 on the soul's joining, Daniel on the kingdoms).
- **Saadia on the same idea, not the same verse**: *HaEmunot veHaDeot* (Ibn Tibbon). Refs: `HaEmunot veHaDeot, [Treatise II] The Unity of the Creator 6`; Treatises I–IV and X also have an Introduction node. Treatises: I creation, II the unity of God (borrowed terms II:10, the plural of majesty II:6, the created light the prophets see II:12, the image II:9), III commandments, IV free will (God's knowledge IV:4), V merit (trials of the righteous V:3), VI the soul (its three names VI:3, after death VI:7), VII resurrection, VIII redemption, IX the world to come, X conduct (music X:18, astrology X:7). Search by idea with keywords (strip niqqud first), not only by the verse. Where Ibn Ezra cites "the Gaon", find the place.
- Fetch the text again just before writing each sentence and quote from it; check the chapter number in the ref you fetched. Save long texts under `review_audit/sources/` if the next round will need them.
- Never: Krinsky's Mechokekei Yehudah, Aristotle, or naming the Strickman–Silver English.

## 3. Write the rows (add sentences only)
- One row per added sentence (two at most when they belong together), anchored after an exact English sentence of the note (`ops=[('notes', (c, v), '<anchor>', '<anchor> <added>')]`); the anchor must occur once in that verse's notes (make_rows stops otherwise). Nothing already in the note is rewritten.
- Place it where the fixed order puts it: what Ibn Ezra says → what a reader would otherwise think → **Ibn Ezra by Ibn Ezra** (Part A) → **Saadia** (Part B) → Rambam. A Saadia sentence goes before Rambam: anchor on the sentence before Rambam, or insert before "Rambam …".
- Limit: one or two sentences per source; the paragraph stays a paragraph (about 120–250 words). Where Emunot veDeot has nothing on the idea, nothing is added. If the same Saadia passage serves two places (Bereshit 1:26 and Noach 11:7), give the proofs once and point to it at the second.
- Name the source in the sentence: "(Emunot veDeot VI:3)", "On Exodus 6:3 he …", "In Yesod Mora (1:7) …". When the sentence ends with a verse reference, put the Emunot reference after Saadia's name, not as a second parenthesis.
- House rules as everywhere: no typed Hebrew (markers only; avoid Hebrew where English will do — "the soul's name for knowing", not a transliteration); H{sc}ashem{/sc} in the added text; vowels named with their signs; no hedges.
- Row fields: `id` (A1…, B1…), `part`, `c`, `v`, `where`, `ie=True`, `folder`, `issue` (say when a place is raised again), `heb='{hcb:c:v:k}'` and `heb_en=ec_en(F, c, v, k)` for the Explanations tab, `ops`, `plain=plain('<source>')`. CFG and PARTS from `ideas_common.cfg()` / `PARTS` (keep only the Parts that have rows).
- `python3 -I review_audit/make_rows.py ideas_<key>`; read every row's "As it stands" and "If changed" before building.

## 4. Record what was read
- `<folder>/review/idea_sources.json`: for **every** key of ideas.json, `{"ibn_ezra": "<source> (ideas_<key> A1)" | "already in the note: …" | "nothing further on Sefaria (links and Yesod Mora read)", "saadia": "Emunot veDeot II:6 (ideas_<key> B1)" | "nothing on this idea in Emunot veDeot"}`; false hits are "not an idea". `sources_todo('<folder>')` must come back empty, and `check_all.py <folder>` shows no "Idea sources".
- The doc's closing section ("What the check found clean") says how many places were read, which already had Ibn Ezra's own writings in the note, and where Saadia has nothing.

## 5. Build the doc and register it
- Commit and push the rows files and idea_sources.json (Co-Authored-By and Claude-Session lines).
- In the workbench: load `scripts/workbench/wb.py` (GITHUB_GET_RAW_REPOSITORY_CONTENT → s3url → exec), `exec(gh_bytes('scripts/review_doc.py'))`, then `cfg = gh_json('review_audit/<key>_doc_cfg.json'); cfg['rows'] = gh_json('review_audit/<key>_rows.json')`; assert `cfg['account'] == 'googledocs_spinet-dirk'` (davross846; never the Going Pro accounts); `B = Builder(cfg); B.phase_main(); B.phase_explanations(); B.phase_styles(); B.phase_links(); B.verify()` — n_bad must be 0. One doc per cell (180 s limit); keep `B.id` and `B.etab`.
- Save `review_audit/<key>_doc_id.txt`; add the doc to `review_docs.json` (parasha, list "Ideas Audit", title, id, explanations_tab, rows_file, rows, opened, status "open", note, checked) and to docs/HANDOFF.md's open review docs.
- Tell David in a line or two per doc what it adds, with the link to every doc. Approving a row reopens that parasha: apply with apply-review-decisions, rebuild, renumber later parashot if pages change.
