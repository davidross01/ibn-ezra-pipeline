---
name: "commentary-checks-upkeep"
description: "Keep the automatic checks of David's Ibn Ezra book honest: review the accepted-hit lists, require a reason for every accepted hit, close known gaps in the checks, turn each fixed error into a test, and find instructions repeated between skills and rule files."
---

# Upkeep of the checks and the instructions

check_all reports "clean" when every hit is either fixed or already accepted. An accepted list can hide a real hit, a check can have a gap, and an instruction written in two places can drift. This skill is the periodic upkeep. Load commentary-house-rules first and read review.md and the "For Claude" part of the rule file each check belongs to.

## When
- After a sense reading or an audit finds an error the checks passed.
- Before a parasha is made final, for that parasha's accepted lists.
- When David asks why a check missed something, or asks for the checks or the skills to be tidied.

## 1. The accepted lists ("already read")
- For each parasha list every accepted hit of every check (the baseline files the checks read), grouped by check and kind.
- Each hit must have a reason: a ruling number, a rule's stated exception, or a review row David answered. A hit with a reason stays.
- A hit with no reason is read again. If it is right as it stands, record the reason. If it breaks a rule, it becomes a review row (review.md, rule 1); it is never fixed silently and never left accepted.
- From then on a hit is accepted only with its reason written beside it. If the check script accepts without a reason, propose the change to the script and make it once David agrees.

## 2. Gaps in the checks
- When a reader finds an error of a kind a program could test, write the test first and run it on every parasha before fixing the one place. Real hits become rows; hits that are right are accepted with a reason.
- Known kinds to cover: a verse quoted in English with no Hebrew where the reference comes before the quotation (notes.md, rule 17); quotation marks around quoted verses in the Hebrew commentary, once David has ruled which way the book goes; pointers inside the book to a comment that does not exist; a source cited in a note that is not in the stored library.
- A rule that says "checked by" a script must name a check that exists and does that. List the rules that a program could check and that have no check, and say which you added.

## 3. Every fixed error becomes a test
When David approves a correction, add the pattern to `own_checks` in scripts/check_all.py where a program can test it (a word, a sign, a pattern, a count), run it on every parasha, and commit it with the correction. Say in one line whether the check now covers it.

## 4. Instructions written twice
- Each rule is written once, in its file in docs/rules/. A skill says when it is used, which rule file to read, and the order of the steps; it does not restate the steps of a rule or keep a live fact (pages, status, document ids).
- Compare every skill in docs/skills/ with the rule files and with the other skills by program: any paragraph or step that appears in two places, any step that differs between two places, any rule number, file or script a skill names that does not exist.
- For each, say which text should stay and which should go, quoting the sentence. Changes to a rule file follow "A new rule from David" only if the rule itself changes; changes to a skill are shown to David as a card, because only he saves skills. The repo copy in docs/skills/ is updated when he has saved it.

## Report
Per parasha: accepted hits reviewed, how many kept with a reason, how many became rows (with the review's link), which checks were added, and which skill texts are proposed for change.