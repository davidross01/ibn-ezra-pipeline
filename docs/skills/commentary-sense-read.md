---
name: "commentary-sense-read"
description: "Independent reading of a parasha of David's Ibn Ezra book for sense: Hebrew against English, every note's claim against its source, cross-references; findings re-checked by a second reader and put to David as review rows."
---

# Sense reading of a parasha

The checks in check_all test form: letters, references, patterns. They cannot tell that an English sentence says something Ibn Ezra does not, or that a note claims more than its source. This skill is the reading that does. It finds and reports; it changes nothing in the book. Load commentary-house-rules first and read translation.md, grammar.md, hebrew.md and notes.md in full.

## When
- Once per parasha, before it is made final (finalize-parasha), after the last review answers are applied and check_all is clean.
- On an older parasha when David asks for a sense reading or an audit of mistakes.
- Not on every draft: one parasha takes about one usage window. Tell David before starting, and run at most three readers at a time.

## The readers
1. **Chunks.** Split the parasha into chunks of about 8,000 English words of commentary and notes (usually two per parasha). Write them in a chunks file like `audit/tools/chunks.example.json` and make the per-verse dumps with `python3 -I audit/tools/dump.py <chunks file> <work folder>`: for each verse the verse, the verse band, Ibn Ezra's Hebrew in numbered segments, the English, and the notes.
2. **One reader per chunk**, a separate agent that did not write or review the draft, given `audit/READER_BRIEF.md` word for word with its chunk name. The reader saves its JSON after every block of verses, so an interrupted reader is resumed, never restarted.
3. **What each reader checks**, every verse, phrase by phrase:
   - the English against the Hebrew: omissions, additions outside round brackets, wrong sense or referent, a grammar term against David's glossary, one Hebrew phrase rendered two ways, a quoted verse that differs from the verse band;
   - every reference in Ibn Ezra's Hebrew, in the English and in the notes, by script against the Tanakh text;
   - **every claim in every note against its source, not only the quotation.** A line that says a commentator agrees, follows, also says, or takes a view is opened in the source and must say no more than the source does. Anything beyond the source is cut, or marked "it seems" as own reasoning;
   - every pointer inside the book ("see the comment on 1:28", "returns to this at ..."): the place must exist and say what the pointer says;
   - a source cited but not in the stored library (review_audit/sources/library.json) is read on Sefaria and reported as missing from the library; it is never confirmed from memory.
4. **Labels.** CERTAIN = provable from the text or the rules; PROBABLE = a strong case a competent reader could still dispute; SUGGESTION = an improvement, not an error. A guess is never presented as an error. Literal English is the house style and is not a fault; places David has already decided are not raised again; rows already in an open review are skipped.
5. **Hebrew.** Readers never type Hebrew or Aramaic. They point to it by segment id and word numbers, and the Hebrew is copied into the rows by program.

## The second reader
Before any CERTAIN or PROBABLE finding goes to David, a different agent that has not seen the first reader's reasoning gets only the place, the claim and the sources, and re-checks it against the text. What does not survive is dropped or downgraded. Say in the report how many were dropped.

## To David
- Every surviving finding is a row in a review list (review-list-google-doc), one row per proposed change, with its label, the Hebrew line, the sentence as it stands and as it would be if changed, each with English, and the source. Give the link.
- State the exact coverage: which verses were read in full and what could not be checked and why.
- Nothing is applied until David answers (apply-review-decisions).
- Afterwards: each error David approves becomes a test in `own_checks` where a program can test it, so it cannot return in a later parasha (commentary-checks-upkeep).