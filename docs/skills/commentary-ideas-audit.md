---
name: "commentary-ideas-audit"
description: "Go through a written parasha of David's Ibn Ezra series and make its Ideas Audit review doc: Ibn Ezra explained by his own writings, then Saadia's Emunot veDeot on the same idea, one added sentence per row."
---

# Ideas Audit for a written parasha

Use this skill when David asks to bring the idea notes of a parasha that is already written up to the rule of 8 Nov 2026 ("give each idea paragraph a fixed order; bring in Saadia on the same idea, not just the same verse; use Ibn Ezra to explain Ibn Ezra first; keep a limit"). It also applies when he asks to "go through the parashot and make a review sheet" for them. For a new parasha's draft, use **ibn-ezra-idea-notes** instead: the paragraphs are written in the fixed order from the start and go into that draft's own Ideas Part.

Load **commentary-house-rules** first. The rule is in docs/rules/notes.md, under "Idea notes: a fixed order, Ibn Ezra first, Saadia, and a limit"; the review rules are in docs/rules/review.md. The repo is davidross01/ibn-ezra-commentary at /home/claude/ibn-ezra-commentary, and its copy of this skill is docs/skills/commentary-ideas-audit.md. Model rows files: `review_audit/ideas_ber_rows.py` (15 rows), `ideas_noach_rows.py`, `ideas_ll_rows.py`, `ideas_vay_rows.py` and `ideas_cs_rows.py`. Shared helpers (`ec_en`, `plain`, `PARTS`, `cfg`) are in `review_audit/ideas_common.py`.

## 1. List the places
- `<folder>/review/ideas.json` lists every idea place of the parasha ("done …", "kept as it was …", "not needed: …").
- `python3 -c "import sys; sys.path.insert(0,'scripts'); import ideas_scan; print(ideas_scan.sources_todo('<folder>'))"` lists the places not yet recorded in `<folder>/review/idea_sources.json`. Read every place, including the ones David kept and the ones judged "not needed". Raise them again wherever Ibn Ezra's own writings or Saadia add something (David's choice of 8 Nov).
- Pull each place's note text from the model (`<folder>/data/model.json`, or `data/model_final5.json` for Bereshit) into a scratch file, so the sources can be read against what the note already says.

## 2. Read the sources on Sefaria
The shell cannot reach Sefaria, so fetch in the Composio workbench.
- **Ibn Ezra explained by Ibn Ezra comes first.** Use `/api/links/Genesis.<c>.<v>` and `/api/related/Ibn_Ezra_on_Genesis.<c>.<v>` to find his other commentaries on the verse, and read *Yesod Mora*. Follow every place where he says "as I will explain", "as I explained" or "the secret of …". Examples: Exodus 6:3 on El Shaddai, Deuteronomy 1:2 on "the secret of the twelve", Psalms 73:24 and 49:16 on the soul's joining, and Daniel on the kingdoms.
- **Saadia on the same idea, not merely the same verse.** The text is *HaEmunot veHaDeot* (Ibn Tibbon). Refs look like `HaEmunot veHaDeot, [Treatise II] The Unity of the Creator 6`, and Treatises I–IV and X also have an Introduction node. What each treatise covers:
  - I: creation
  - II: the unity of God (II:6 the plural of majesty, II:9 the image, II:10 borrowed terms, II:12 the created light the prophets see)
  - III: the commandments
  - IV: free will (IV:4 God's knowledge)
  - V: merit (V:3 trials of the righteous)
  - VI: the soul (VI:3 its three names, VI:7 after death)
  - VII: resurrection; VIII: redemption; IX: the world to come
  - X: conduct (X:7 astrology, X:18 music)
  Search by idea with keywords (strip niqqud first), not only by verse. Wherever Ibn Ezra cites "the Gaon", find the place.
- Fetch each text again just before writing its sentence, quote from what you fetched, and check the chapter number in the ref. Save long texts under `review_audit/sources/` if a later round will need them.
- Never use Krinsky's Mechokekei Yehudah or Aristotle, and never name the Strickman–Silver English.

## 3. Write the rows (add sentences only)
- Each row adds one sentence, or two at most when they belong together. Anchor it after an exact English sentence of the note: `ops=[('notes', (c, v), '<anchor>', '<anchor> <added>')]`. The anchor must occur exactly once in that verse's notes, or make_rows stops. Nothing already in the note is rewritten.
- Put the sentence where the fixed order puts it. The order is: what Ibn Ezra says → what a reader would otherwise think → Ibn Ezra explained by Ibn Ezra (Part A) → Saadia (Part B) → Rambam. A Saadia sentence goes before Rambam: either anchor it on the sentence before Rambam or insert it before "Rambam …".
- Keep to the limit: one or two sentences per source, so that the paragraph stays a paragraph (about 120–250 words). Where Emunot veDeot has nothing on the idea, add nothing. When one Saadia passage serves two places (Bereshit 1:26 and Noach 11:7, for example), give its proofs once and point to them from the second place.
- Name the source in the sentence itself: "(Emunot veDeot VI:3)", "On Exodus 6:3 he …", "In Yesod Mora (1:7) …". When the sentence ends with a verse reference, put the Emunot reference right after Saadia's name rather than adding a second parenthesis.
- Follow the house rules as everywhere:
  - Never type Hebrew; use markers only.
  - Where English will do, avoid Hebrew and transliteration (write "the soul's name for knowing").
  - Write H{sc}ashem{/sc} in the added text.
  - When a vowel is named, give its sign.
  - No hedges on what a source says; where a sentence gives your own reasoning, not a source's, say "it seems" (David, 9 Nov 2026).
- Row fields:
  - `id` (A1…, B1…), `part`, `c`, `v`, `where`, `ie=True`, `folder`
  - `issue`: say so when a place is raised again
  - `heb='{hcb:c:v:k}'` and `heb_en=ec_en(F, c, v, k)` for the Explanations tab
  - `ops`, and `plain=plain('<source>')`
  - Take CFG and PARTS from `ideas_common.cfg()` and `PARTS`, keeping only the Parts that have rows.
- Run `python3 -I review_audit/make_rows.py ideas_<key>`, then read every row's "As it stands" and "If changed" before building the doc.

## 4. Record what was read
- In `<folder>/review/idea_sources.json`, give **every** key of ideas.json an entry: `{"ibn_ezra": "<source> (ideas_<key> A1)" | "already in the note: …" | "nothing further on Sefaria (links and Yesod Mora read)", "saadia": "Emunot veDeot II:6 (ideas_<key> B1)" | "nothing on this idea in Emunot veDeot"}`. A false hit gets "not an idea". Afterwards `sources_todo('<folder>')` must return an empty list, and `check_all.py <folder>` must report no "Idea sources" hits.
- The doc's closing section ("What the check found clean") says three things: how many places were read, which notes already had Ibn Ezra's own writings, and where Saadia has nothing on the idea.

## 5. Build the doc and register it
- Commit and push the rows files and idea_sources.json, ending the commit message with the Co-Authored-By and Claude-Session lines.
- Build in the workbench:
  1. Load `scripts/workbench/wb.py` (GITHUB_GET_RAW_REPOSITORY_CONTENT → s3url → exec), then run `exec(gh_bytes('scripts/review_doc.py'))`.
  2. Set `cfg = gh_json('review_audit/<key>_doc_cfg.json'); cfg['rows'] = gh_json('review_audit/<key>_rows.json')`.
  3. Assert `cfg['account'] == 'googledocs_spinet-dirk'`. That is davross846; never use the Going Pro accounts.
  4. Run `B = Builder(cfg); B.phase_main(); B.phase_explanations(); B.phase_styles(); B.phase_links(); B.verify()`. n_bad must be 0.
  5. Build one doc per cell (each cell has a 180 s limit) and keep `B.id` and `B.etab`. If a cell is stopped part-way, check what was already built before running it again.
- Save `review_audit/<key>_doc_id.txt`. Add the doc to `review_docs.json` with parasha, list "Ideas Audit", title, id, explanations_tab, rows_file, rows, opened, status "open", note and checked. List it under the open review docs in docs/HANDOFF.md.
- Tell David in a line or two per doc what it adds, with the link to every doc. Approving a row reopens that parasha: apply the answers with apply-review-decisions, rebuild, and renumber the later parashot if the page count changes.