---
name: "ibn-ezra-idea-notes"
description: "Research and write the note paragraph for one of Ibn Ezra's ideas, science or 'secrets' in David's series: find and read the sources (Avi Ezer, Ibn Ezra elsewhere, Saadia's Emunot veDeot, Rambam), write it at the right length, and put it to David as an Ideas row."
---

# Ibn Ezra's ideas: researching and writing the note

Use whenever a comment of Ibn Ezra touches an idea (God's knowledge and will, the soul, prophecy, providence, creation, the image of God, free will), his science (spheres, astrology, medicine, geography, music) or a hint ("there is a secret", "the wise will understand") — in a new parasha's draft or in an audit (commentary-audit, Part F). Load **commentary-house-rules** first, then read **docs/profiles/ibn-ezra.md**, sections 4 and 6: which kinds of comment get an idea note and at what length, which sources are used and in what order, and which are never used. The profile points to the rules, which win: docs/rules/notes.md, rules 9-13 ("Ibn Ezra's ideas get a full paragraph", "Idea notes: length and sources", "Idea notes in the old style, with Saadia and Ibn Ezra's own writings", "The idea places are found in Ibn Ezra's Hebrew too", "Every idea sentence is checked against its source") and review.md, rule 5 ("An Ideas Part"). This skill says how the sources are found and read; it does not decide which may be named. For a parasha already written, bring its notes up to the rule of 8 Nov with **commentary-ideas-audit** (sentences added, one row each, an Ideas Audit doc per parasha). Repo: davidross01/ibn-ezra-commentary at /home/claude/ibn-ezra-commentary; repo copy of this skill: docs/skills/ibn-ezra-idea-notes.md.

## 1. Find the places
- `python3 -I scripts/ideas_scan.py <folder>` lists candidate verses by English keyword, and `… <folder> --hebrew` by the words of Ibn Ezra's own Hebrew (David, 9 Nov 2026: the English scan missed Toledot 25:23 and 27:27); a Hebrew find leaves the list through ideas.json or `<folder>/review/ideas_he.json` (“not an idea: …” / explained in the note). Run both; read each one — many are false hits ("the one", "angel" in another sense, "prophet" in a quoted verse). Also look for science the scan misses (geography, the elements, medicine).
- `<folder>/review/ideas.json` records each verse: `"in review: <list>, F<n>"`, `"done …"`, or `"not needed: <why>"`. check_all "Ideas" lists what is left; `--accept` never hides it.

## 2. Read the sources (all on Sefaria, all named in the note)
The shell cannot reach Sefaria. Fetch in the Composio workbench (`requests.get('https://www.sefaria.org/api/v3/texts/<Ref>', params={'return_format': 'text_only'})`, add `'version': 'english'` for English), save the texts to a JSON in the repo with `gh_commit` (scripts/workbench/wb.py), `git pull`, and read them locally with python (strip niqqud before searching). Keep them in `review_audit/sources/` so the next round need not fetch again.
- **Avi Ezer** for every idea and every hint: `src/avi_ezer_genesis.json` (all of Genesis; chapters 26, 36, 39, 46 are not on Sefaria). Where he points ("see the Rav on Exodus …", Sefer Tzachot, Moznayim), follow the pointer.
- **Ibn Ezra elsewhere** first — *Yesod Mora* and his comments on other verses and books. He often explains his own hint, so always look where he says "as I will explain" or "as I explained": Exodus 3:15 (the Name; "the man … is the name of the species"), Exodus 23:21, 32:14, Leviticus 1:1, 1:4, 17:11, Psalms 49:16, 73:24, Ecclesiastes 12:7 and its introduction, Exodus 6:3 (El Shaddai and the stars), Deuteronomy 1:2 (the secret of the twelve). Find more with `POST /api/search-wrapper` (`{"query": …, "type": "text", "field": "exact"}`) and `/api/related/Ibn_Ezra_on_Genesis.c.v` (who links to the comment).
- **Saadia Gaon, Emunot veDeot** wherever he discusses the **same idea**, not merely the same verse. On Sefaria it is *HaEmunot veHaDeot*, in Ibn Tibbon's Hebrew; refs look like `HaEmunot veHaDeot, [Treatise VI] The Soul and Death 3`, and Treatises I–IV and X also have an Introduction node. Search by idea with keywords, and wherever Ibn Ezra cites "the Gaon", find the place. Name the treatise and chapter ("Emunot veDeot II:10"). Chapters used so far:
  - I:1, I:3: creation from nothing
  - II:6: plurals of majesty, and the three men of Genesis 18
  - II:9: "My image"
  - II:10: borrowed terms ("and Hashem smelled" is acceptance)
  - II:12: the created light the prophets see
  - III:1–2: the commandments, holy days
  - IV introduction: man as the purpose of creation
  - IV:4: God's knowledge is not the cause of man's choice
  - V:3: trials of the righteous
  - VI:1–3: the soul and its three names
  - VI:7: the soul after death
  - X:7: astrology and love
  - X:18: music
- **Rambam** wherever he discusses the same idea: Guide (I:2 knowledge of good and evil; I:7 Seth in Adam's image; I:26, I:29 language of men; I:61 the Name; II:30, II:42 the serpent, Balaam's she-ass; III:10, III:12, III:17 evil, Galen, providence; III:51 death by a kiss), Mishneh Torah (Foundations of the Torah 4; Repentance 5, 8; Idolatry 11:16), Treatise on Logic 14. Check the halakha or chapter number in the fetched text before citing it.
- Others that may be named: Radak, Rashi, Onkelos (by their rules), Rabbi Isaac Arama (Akedat Yitzchak), Krochmal (Moreh Nevukhei HaZeman, gate 17 — mostly quotations of Ibn Ezra).
- **Never** the sources the profile (section 6) and notes.md, rules 5 and 10, rule out, even where Sefaria links them to every comment. The English on Sefaria (Strickman–Silver) may be read to check a translation, never named.
- If no source that may be named explains a hint, do not invent one: say so in the review list's notes and record `"not needed: a bare hint; no source that may be named"` in ideas.json.

## 3. Write the paragraph
- **Full** for a real idea: one paragraph, the way the notes were written before 8 Nov (David, 9 Nov 2026: "write it the way that it was before with the philosophical notes, but just add in … where rav Saadia gaon says something"). Give the idea in detail and what a reader would otherwise think; give "why he brings it here" only where the verse itself prompts it; name the sources with chapter and verse (Avi Ezer, Rambam). Inside the paragraph, where they add something:
  - **Saadia**: a sentence from Emunot veDeot on the same idea, treatise and chapter named;
  - **Ibn Ezra's own writings**: a short sentence saying where he explains himself (Yesod Mora, his comment on another verse). David asked this on the Ideas Audits: "Just say where to find the secret", "Just say where in Deuteronomy the reader can find it".
  Revising a paragraph adds to it and never cuts.
- **Short** (3–4 sentences) for background science, with Saadia only if he speaks to it directly.
- Build every claim on a source's own words; quote him where he states it. No hedges on what a source says ("on one reading", "probably"). Where the reasoning is your own and not a source's, such as a link you draw between Ibn Ezra and Rambam or what follows from a view, say "it seems" (David, 9 Nov 2026: "Say it seems"). No unsourced keys to a secret.
- Hebrew only by marker ({q:Book c:v:i-j}, {vw:…}, {nt:…}, {ec:…}), never typed; avoid Hebrew where English will do. A vowel named in the English gets its sign.
- Anchor each added sentence on an English sentence of the existing note. Replace a sentence only when it is wrong or unsourced.

## 4. Put it to David
Every idea paragraph is its own row in the review list's **Ideas Part** (Keep / Approve), one row per paragraph (David, 9 Nov 2026; the one-sentence rows of 8 Nov are superseded). Each row has:
- where;
- the issue;
- Ibn Ezra's Hebrew ({hcb:c:v:k}) with its English;
- **Now**: the note without the paragraph;
- **Alternative**: the note with it;
- the plain line "Sources read on Sefaria: …".

Model: Toledot List 1 Part F as rebuilt on 9 Nov (F1–F5).

Before the doc is built, check the paragraph against its sources (9 Nov 2026):
- Keep each source in review_audit/sources/library.json, as read on Sefaria.
- In review_audit/citations.json, under `<rows key>:<row id>`, record the passages the paragraph rests on and the verdict of the check: supported, partly or not supported, with the problems.
- Rewrite whatever says more than its source. A "partly" may stand only with an accepted note saying why: your own reasoning marked "it seems", the "what a reader would think" clause, or background David asked for.
- `python3 -I scripts/cite_check.py` must pass (CI runs it). make_rows puts the sources' Hebrew in the row's Explanation (“Source (Hebrew)”); the Alternative is the English paragraph alone (David, 9 Nov 2026).

After his answers, ideas.json "in review" becomes "done". Record what was read for every place in `<folder>/review/idea_sources.json` ({"ibn_ezra": …, "saadia": …}); check_all lists the places not yet recorded as "Idea sources".