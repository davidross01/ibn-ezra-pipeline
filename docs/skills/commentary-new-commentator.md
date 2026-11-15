---
name: "commentary-new-commentator"
description: "Start David's translated-commentary book on another commentator (Ramban, Seforno, Rashbam ...): fill the commentator's profile from the blank, carry over the every-book rules, run a one-chapter pilot, then freeze the profile."
---

# Starting a book on another commentator

The Ibn Ezra book has three layers: the engine (build, review lists, checks, sense reading, term sheet), the house rules that hold for every book, and what is particular to Ibn Ezra. Only the third is written afresh for a new commentator, and it is written in one place: the commentator's profile. Load commentary-house-rules first. In the Ibn Ezra repo read `docs/profiles/ibn-ezra.md` (the filled example), `docs/profiles/_blank.md` (the questions) and `docs/profiles/rulings_scope.json` (which rulings carry over).

## Before anything is built
Ask David 3-4 questions with the checkboxes: which commentator and which work; the unit of work and where the pilot chapter is; whether the page keeps the same layout; whether the new book shares the Ibn Ezra repository or gets its own. Say which model or feature suits the job if another would be better.

## 1. The profile
- Copy `_blank.md` to `docs/profiles/<name>.md` in the new book's repository.
- Fill what the texts themselves answer (which edition is on Sefaria, whether a second Hebrew text exists, which supercommentaries and other works of his are on Sefaria) by looking, never from memory, and name where each was found.
- Everything that is a choice - which commentators stand in the notes and when, what each kind of comment is owed, note lengths, sources never used, the English of his terms - goes to David as rows in a review list (review-list-google-doc), a few questions per Part, each row saying plainly what each answer does. "Decide after the pilot" is an allowed answer. Give the link.
- The profile points to rules; it never restates one, and it holds no live facts.

## 2. The rules that carry over
- Rulings marked "every book" in `rulings_scope.json` are copied as they are, with their numbers recorded as "from the Ibn Ezra book". If David has not yet corrected that sorting, show it to him first.
- Rulings marked "this commentator" are not copied. Each is asked again as a profile question.
- The new book's own rulings are numbered from 1 and marked "this commentator". Each rule is written once, in the rule file it belongs to (commentary-house-rules, "A new rule from David").
- The checks: every-book checks run unchanged; for each profile rule a program can test, add a test to `own_checks` before the pilot is sent, and list the profile rules that have no check.

## 3. The pilot: one chapter
- Build one chapter with commentary-book-build, the profile as it stands.
- From its first draft run the term sheet (commentary-term-sheet) and the sense reading (commentary-sense-read): one reader, then the second reader's re-check.
- Send David the draft with its review list. Every answer that sets a rule becomes a ruling and updates the profile's pointer.
- Keep a short log of the findings by kind (wrong sense, term, note claim, reference). It is the baseline for later parashot.

## 4. Freeze and begin
- When the pilot's rows are answered and applied, read the profile through with David's answers and mark it frozen, with the date in the history, not in the profile.
- After that the profile changes only through a ruling.
- Then the first parasha starts in the usual way: commentary-book-build, the review list, apply-review-decisions, commentary-sense-read, finalize-parasha.

## Never
- Never type Hebrew or Aramaic from memory; copy it by program, pointed, never transliterated.
- Never carry an Ibn Ezra rule into the new book because it is familiar: only "every book" rulings carry over.
- Never create Google files outside davross846@gmail.com.