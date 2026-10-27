# House rules — Grammar terms — David's grammar sheet

Part of commentary-house-rules (the core is the skill itself). Moved here word for word on 27 Oct 2026; change a rule here and in the core line that points to it.

## Grammar terms — David's grammar sheet
David gave an "Ibn Ezra Grammar Organizer" cheat sheet to learn from. A copy is kept in the project as ref/grammar_sheet.png; if the project is missing, ask him for it. Check every grammar term against it before translating, and again before each draft.

**How to use it**
1. When a Hebrew grammar term appears in the commentary, translate it with the English below, the same way every time. If Ibn Ezra uses a term in his own medieval sense, his sense wins; mark that in the key to terms with ◆.
2. Put each term the reader may not know into the key to terms (front matter) and the foot-of-page strip (data/foot_terms.json). The key's English must match the translation.
3. Before each draft, run `python3 scripts/terms_audit.py <model.json>` in the parasha folder (scripts/check_book.py runs it too; Bereshit's model is data/model_final5.json, Noach's data/model.json). For every term it finds in the Hebrew, it checks that the English of the same verse uses the house rendering. It lists the places that don't, and the terms rendered more than one way. Read each listed place. A real inconsistency becomes a review-list row, not a silent change, because it is a translation change and David decides. Places David has already decided stay as he decided (Bereshit: G1 "the discerning will understand" at 1:1 and G2 "superfluous" at 1:14 were both Keep).
4. **When unsure, ask in the review.** If you are not sure how a grammar term or rule should be translated (the sheet and Ibn Ezra seem to disagree, a term isn't on the sheet, or the grammar of a passage could be read two ways), don't guess silently. Translate it with your best reading, state it plainly in the note (no "Uncertain" label, see Translation), and add a row to the review list's grammar Part (Part G in the Bereshit list; Part C in Noach's and Lech Lecha's). Each row gives: where, the Hebrew line, your rendering (Now), the alternative (Proposal), and in plain words why you are unsure. If the list has no grammar Part yet, create one. Add David's answer to the glossary below once he decides.

**Glossary (Hebrew → English used in the book)**
- Parts of speech:
  - שֵם noun, name (also הַשֵּם = Hashem, see "Translation").
  - פּוֹעַל verb (also the active participle).
  - מִלָּה word (key to terms: just "word"; Ibn Ezra's מִלַּת X means "the word X").
  - מִלַּת עִנְיָן word of relation (a small word that links or relates rather than names a thing, as הֵן, עִם; David, Lech Lecha Review List 1 row C4, 16:11).
  - כִּנּוּי pronoun, pronominal suffix; also a byname or euphemism.
  - תּוֹאַר / שֵם הַתּוֹאַר adjective — always simply "adjective" (David's decision, rows G3/G4: also at 1:1 אֱלֹהִים "an adjective, not a proper noun" and at 1:26 נַעֲשֶׂה).
  - שֹׁרֶשׁ root (three-letter base).
- Tenses and forms: עָבָר past · עָתִיד future · צִוּוּי imperative (command) · מָקוֹר and Ibn Ezra's שֵם הַפּוֹעַל infinitive · פּוֹעֵל active participle · פָּעוּל passive participle · פּוֹעַל יוֹצֵא transitive verb · פּוֹעַל עוֹמֵד intransitive verb.
- Conjugations (בִּנְיָנִים):
  - קַל / הַבִּנְיָן הַקַּל = the light conjugation (kal, simple).
  - נִפְעַל = nif'al (passive/reflexive).
  - פִּעֵל and Ibn Ezra's הַבִּנְיָן הַכָּבֵד = the heavy conjugation, pi'el (intensive) ◆.
  - הִפְעִיל and Ibn Ezra's הַכָּבֵד הַנּוֹסָף = the heavy conjugation with an added letter, hif'il (causative) ◆.
  - הִתְפַּעֵל = hitpa'el (reflexive).
  - בִּנְיָן שֶׁלֹּא נִקְרָא שֵׁם פּוֹעֲלוֹ = "(the conjugation) whose agent is not named", i.e. the passive.
- Root letters: פּ"א / ע"י / ל"מ הַפּוֹעַל first / middle / last root letter · weak roots פּ"נ, פּ"י, פּ"א, ע"ו, ע"י, ל"ה, ל"א = "roots whose first/middle/last letter is X" · כְּפוּלִים doubled roots · מִגִּזְרַת from the root of · מִשְׁקָל pattern · Ibn Ezra's הַפְּעָלִים הַשְּׁנִיִּים הַנִּרְאִים = "the verbs whose middle root letter is ו" (Lech Lecha 17:10, row C5, checked on Sefaria).
- Weak and silent letters: גְּרוּנִיּוֹת guttural letters (א ה ח ע) · אוֹתִיּוֹת אֶהוָ"י weak letters (א ה ו י) · נָח / נָחִים quiescent (silent) letter(s) · נָח נֶעְלָם hidden quiescent letter · נֶעְלָמִים dropped (unpronounced) letters.
- Letter changes: הַבְלָעָה absorption · חִלּוּף / מִתְחַלְּפִים substitution, interchange (letters that take each other's place) · תַּחַת in place of · הִתְמַזְּגוּת merging · הִדּוּמָה assimilation · נָפַל dropped · נוֹסָף added (not of the root; not "superfluous") · חָסֵר missing · יָתֵר extra · דָּגֵשׁ dagesh · רָפֶה without dagesh (soft) · שְׁוָא נָח silent sheva · שְׁוָא נָע mobile sheva · סִימַן הַמְדַבֵּר the sign of the speaker (the prefix for "I").
- Vowels: פַּתָּח patach · קָמָץ kamatz · צֵירֵי tzere · סֶגּוֹל segol · חִירִיק hirik · חוֹלָם holam · שׁוּרוּק shuruk · קָבּוּץ kubutz · שְׁוָא sheva (written in the English with its sign on an alef, see "Letters and vowels in the English").
  - Ibn Ezra's own names: קָמָץ גָּדוֹל "large kamatz" (= kamatz) · קָמָץ קָטָן "small kamatz" (= tzere) ◆ · פַּתָּח גָּדוֹל "large patach" (= patach) · פַּתָּח קָטָן "small patach" (= segol) ◆.
  - Translate his name literally, and give the modern name the first time it appears on a page or in the note.
- Accents: where Ibn Ezra names an accent whose sense is unclear, give the name in Hebrew and the literal English together: עִנְיַן מוּכְרָת ("a matter cut off") (David, Lech Lecha Review List 1 row C1, 12:19).
- Syntax: סָמוּךְ construct (state), bound to the next word · נִפְרָד absolute (independent) form · טַעַם sense, meaning; also reason, and an accent (◆, e.g. בַּעַל הַטְּעָמִים "the master of the accents") · חַסְר מִלָּה an implied (understood) word · מוֹשֵׁךְ / מְשָׁרֵת עַצְמוֹ וְאַחֵר עִמּוֹ draws / serves itself and another with it (one word applies twice) · דֶּרֶךְ קְצָרָה a short way of speaking · לְשׁוֹן רַבִּים / יָחִיד plural / singular · זָכָר / נְקֵבָה masculine / feminine (in grammar).
- Reading and interpretation: דֶּרֶךְ הַפְּשָׁט the plain (literal) sense · **דְּרָשׁ homiletical interpretation** (David, 25 Oct 2026, replacing "homily"; in the key to terms and the foot strip: "an exposition of a Torah passage that draws out a deeper, often moral, theological, or conceptual meaning beyond its plain sense"; the strip label is "homiletical interpretation (derash)") · דֶּרֶךְ הַדִּקְדּוּק the way of grammar · כְּמִשְׁפָּט according to (the) rule · אֵין לוֹ אָח it has no other like it (a unique form in Scripture) · הֶקְשֵׁר context · סוֹד secret.
- Signature phrases (always the same English): יֵשׁ אוֹמְרִים / י"א some say · וַאֲחֵרִים אָמְרוּ others say · וְהַמַּשְׂכִּיל יָבִין and the wise will understand · כְּמִשְׁפָּט according to rule · פֵּירוּשׁ / פי' its explanation is · כְּמַשְׁמָעָם as they sound (literally).

