---
name: "ibn-ezra-idea-notes"
description: "Research and write the note paragraph for one of Ibn Ezra's ideas, science or 'secrets' in David's series: find and read the sources (Avi Ezer, Ibn Ezra elsewhere, Saadia's Emunot veDeot, Rambam), write it at the right length, and put it to David as an Ideas row."
---

# Ibn Ezra's ideas: researching and writing the note

Use whenever a comment of Ibn Ezra touches an idea (God's knowledge and will, the soul, prophecy, providence, creation, the image of God, free will), his science (spheres, astrology, medicine, geography, music) or a hint ("there is a secret", "the wise will understand") — in a new parasha's draft or in an audit (commentary-audit, Part F). Load **commentary-house-rules** first; the rule is in docs/rules/notes.md ("Ibn Ezra's ideas", "Idea notes: length and sources", and "Idea notes: a fixed order, Ibn Ezra first, Saadia, and a limit" of 8 Nov 2026) and review.md ("Every review list has an Ideas Part"). For a parasha already written, bring its notes up to the rule of 8 Nov with **commentary-ideas-audit** (sentences added, one row each, an Ideas Audit doc per parasha). Repo: davidross01/ibn-ezra-commentary at /home/claude/ibn-ezra-commentary; repo copy of this skill: docs/skills/ibn-ezra-idea-notes.md.

## 1. Find the places
- `python3 -I scripts/ideas_scan.py <folder>` lists candidate verses by keyword; read each one — many are false hits ("the one", "angel" in another sense, "prophet" in a quoted verse). Also look for science the scan misses (geography, the elements, medicine).
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
- **Never**: Mechokekei Yehudah (Krinsky — Yahel Ohr, Karnei Ohr), even though Sefaria links it to every comment; Aristotle; Ramban's objections unless David asks. The English on Sefaria (Strickman–Silver) may be read to check a translation, never named.
- If no source that may be named explains a hint, do not invent one: say so in the review list's notes and record `"not needed: a bare hint; no source that may be named"` in ideas.json.

## 3. Write the paragraph
- **Full** for a real idea, always in this order (David, 8 Nov 2026):
  1. what Ibn Ezra says, the idea in detail;
  2. what a reader would otherwise think;
  3. **Ibn Ezra explained by Ibn Ezra**: Yesod Mora, his comments elsewhere, and Avi Ezer on his words;
  4. **Saadia**: Emunot veDeot on the same idea;
  5. **Rambam** after him.
  Give "why he brings it here" only where the verse itself prompts it, and name the sources with chapter and verse. **Limit:** one or two sentences each from Ibn Ezra's own writings and from Saadia, about 120–250 words in all; where Saadia has nothing on the idea, say nothing about him. Revising a paragraph adds to it and never cuts.
- **Short** (3–4 sentences) for background science, with Saadia only if he speaks to it directly.
- Build every claim on a source's own words; quote him where he states it. No hedges on what a source says ("on one reading", "probably"). Where the reasoning is your own and not a source's, such as a link you draw between Ibn Ezra and Rambam or what follows from a view, say "it seems" (David, 9 Nov 2026: "Say it seems"). No unsourced keys to a secret.
- Hebrew only by marker ({q:Book c:v:i-j}, {vw:…}, {nt:…}, {ec:…}), never typed; avoid Hebrew where English will do. A vowel named in the English gets its sign.
- Anchor each added sentence on an English sentence of the existing note. Replace a sentence only when it is wrong or unsourced.

## 4. Put it to David
Build the draft **without** the additions. Then put each added sentence to David as its own short row in the review list's **Ideas Part** (Keep / Approve), in the fixed order. David, 8 Nov 2026: "show what it would be like without these additions and then an alternative with them". Each row has:
- where;
- the issue;
- Ibn Ezra's Hebrew ({hcb:c:v:k}) with its English;
- **Now**: the note without the sentence, showing the sentences before and after the place;
- **Alternative**: the same text with the sentence added;
- the plain line "Source read on Sefaria: …".

When several rows fill the same place, anchor each one on the sentence that follows the place: the op's `old` is the first words of that sentence and `new` is the added sentence followed by those words. Approved rows then go in in ID order. The model is `fadd()` in review_audit/tol1_rows.py (Toledot List 1, F1–F18). Do not make one row for a whole paragraph. Before the doc is built, check every added sentence against its source (David, 9 Nov 2026): keep the source in review_audit/sources/library.json as read on Sefaria; record in review_audit/citations.json, under `<rows key>:<row id>`, the passage(s) the sentence rests on (word ranges) and the verdict of the check (supported / partly / not supported, with the problems). Rewrite any sentence that says more than its source; a "partly" stands only with an accepted note (your own reasoning marked "it seems", the "what a reader would think" clause, background David asked for). `python3 -I scripts/cite_check.py` must pass (CI runs it), and make_rows then opens the row's Alternative with the source's Hebrew. After his answers, ideas.json "in review" becomes "done". Record what was read for every place in `<folder>/review/idea_sources.json` ({"ibn_ezra": …, "saadia": …}); check_all lists the places not yet recorded as "Idea sources".