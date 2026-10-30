---
name: ibn-ezra-idea-notes
description: "Research and write the note paragraph for one of Ibn Ezra's ideas, science or 'secrets' in David's series — find and read the sources (Avi Ezer, Ibn Ezra elsewhere, Rambam), write it at the right length, and put it to David as an Ideas row."
---

# Ibn Ezra's ideas: researching and writing the note

Use whenever a comment of Ibn Ezra touches an idea (God's knowledge and will, the soul, prophecy, providence, creation, the image of God, free will), his science (spheres, astrology, medicine, geography, music) or a hint ("there is a secret", "the wise will understand") — in a new parasha's draft or in an audit (commentary-audit, Part F). Load **commentary-house-rules** first; the rule is in docs/rules/notes.md ("Ibn Ezra's ideas", "Idea notes: length and sources") and review.md ("Every review list has an Ideas Part").

## 1. Find the places
- `python3 -I scripts/ideas_scan.py <folder>` lists candidate verses by keyword; read each one — many are false hits ("the one", "angel" in another sense, "prophet" in a quoted verse). Also look for science the scan misses (geography, the elements, medicine).
- `<folder>/review/ideas.json` records each verse: `"in review: <list>, F<n>"`, `"done …"`, or `"not needed: <why>"`. check_all "Ideas" lists what is left; `--accept` never hides it.

## 2. Read the sources (all on Sefaria, all named in the note)
The shell cannot reach Sefaria. Fetch in the Composio workbench (`requests.get('https://www.sefaria.org/api/v3/texts/<Ref>', params={'return_format': 'text_only'})`, add `'version': 'english'` for English), save the texts to a JSON in the repo with `gh_commit` (scripts/workbench/wb.py), `git pull`, and read them locally with python (strip niqqud before searching: `re.sub('[֑-ׇ]', '', ud.normalize('NFD', s))`). Keep them in `review_audit/sources/` so the next round need not fetch again.
- **Avi Ezer** for every idea and every hint: `src/avi_ezer_genesis.json` (all of Genesis; chapters 26, 36, 39, 46 are not on Sefaria). Where he points ("see the Rav on Exodus …", Sefer Tzachot, Moznayim), follow the pointer.
- **Ibn Ezra elsewhere** first — he often explains his own hint: Exodus 3:15 (the Name; "האדם … the name of the species"), Exodus 23:21, 32:14, Leviticus 1:1, 1:4, 17:11, Psalms 49:16, 73:24, Ecclesiastes 12:7 and its introduction. Find more with `POST /api/search-wrapper` (`{"query": …, "type": "text", "field": "exact"}`) and `/api/related/Ibn_Ezra_on_Genesis.c.v` (who links to the comment).
- **Rambam** wherever he discusses the same idea: Guide (I:2 knowledge of good and evil; I:7 Seth in Adam's image; I:26, I:29 language of men; I:61 the Name; II:30, II:42 the serpent, Balaam's she-ass; III:10, III:12, III:17 evil, Galen, providence; III:51 death by a kiss), Mishneh Torah (Foundations of the Torah 4; Repentance 5, 8; Idolatry 11:16), Treatise on Logic 14. Check the halakha or chapter number in the fetched text before citing it.
- Others that may be named: Radak, Rashi, Onkelos (by their rules), Rabbi Isaac Arama (Akedat Yitzchak), Krochmal (Moreh Nevukhei HaZeman, gate 17 — mostly quotations of Ibn Ezra).
- **Never**: Mechokekei Yehudah (Krinsky — Yahel Ohr, Karnei Ohr), even though Sefaria links it to every comment; Aristotle; Ramban's objections unless David asks. The English on Sefaria (Strickman–Silver) may be read to check a translation, never named.
- If no source that may be named explains a hint, do not invent one: say so in the review list's notes and record `"not needed: a bare hint; no source that may be named"` in ideas.json.

## 3. Write the paragraph
- **Full** (about 120–200 words) for a real idea: the idea in detail; what a reader would otherwise think; "why he brings it here" only where the verse itself prompts it; the sources by name with chapter and verse. Revising one adds, never cuts.
- **Short** (3–4 sentences) for background science.
- Build every claim on a source's own words; quote him where he states it. No hedges ("it seems", "on one reading"); no unsourced keys to a secret.
- Hebrew only by marker ({q:Book c:v:i-j}, {vw:…}, {nt:…}, {ec:…}), never typed; avoid Hebrew where English will do. A vowel named in the English gets its sign.
- Anchor the paragraph after an English sentence of the existing note; replace a sentence only when it is wrong or unsourced.

## 4. Put it to David
Every idea paragraph is its own row in the review list's **Ideas Part** (Keep / Approve): where, the issue, Ibn Ezra's Hebrew ({hcb:c:v:k} or {hcw:…}) with its English, the note now and with the paragraph, and in the plain line "Sources read on Sefaria: …". In a new parasha the paragraph is already in the draft and Keep removes or shortens it. After his answers, ideas.json "in review" becomes "done". Models: Audit 1 F1 (Vayera 18:21), Audit 2 Part F.
