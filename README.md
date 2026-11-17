# Ibn Ezra on the Torah: book pipeline

This is the build and quality-check pipeline behind my translated edition of Ibn Ezra's commentary on the Torah. It takes the Hebrew sources, combines them with my English translation and notes, and turns them into a print-ready, typeset book with Hebrew and English side by side. Automated checks and a human review step run along the way.

The book itself is still in progress, so its full source lives in a private repository. This repository shows how it's built. A finished sample, **Parashat Bereshit**, is in [`sample/`](sample/).

## What the pipeline does

- **Source to model:** loads the Hebrew text of the Chumash and the commentary (from Sefaria), along with the translation and notes, into one structured JSON model per parasha.
- **Typesetting:** renders the model to HTML and paginates it in the browser with a custom page planner (`shared/scripts/layout.js`). The planner places the verse band, the Hebrew commentary and the English commentary on each page, then prints a PDF through headless Chromium.
- **Automated checks** (`scripts/check_all.py`, run on every push by GitHub Actions): house-style rules, Hebrew vowel and spelling checks, a misprint scan of the printed Hebrew, source and citation checks, a terms audit that keeps one English rendering per recurring phrase, and consistency of names.
- **Human-in-the-loop review:** decisions that need a person become rows in a generated Google Doc, each with a dropdown Decision chip and links to a full explanation (`scripts/review_doc.py`). The answers are read back and applied to the build automatically, touching only the rows that were answered.
- **Publishing:** exports each finished parasha into separate reusable parts (Chumash, translation, Ibn Ezra Hebrew and English, notes), rebuilds the full-book PDF and refreshes a shared Drive folder.
- **Rules and procedures as code:** `docs/rules/` holds the house rules (translation, Hebrew, grammar terms, notes, page layout, review process). `docs/skills/` holds the step-by-step procedures that an AI agent (Claude) follows to run each stage the same way every time.

## Layout

```
scripts/          checks, review-doc builder, export, publishing, status report
shared/scripts/   renderer, page planner (JS), PDF maker, misprint scan, terms audit
docs/rules/       house rules the checks and the agent follow
docs/skills/      agent procedures for each stage of the pipeline
.github/          CI workflow that runs the checks
sample/           finished PDF of Parashat Bereshit
```

Fonts, source texts and the parasha data aren't included here, so the scripts won't run as they stand. They're here to show how the pipeline is built.

## Tools

Python, JavaScript, HTML/CSS, headless Chromium, GitHub Actions, Google Docs and Drive APIs, and Claude (Claude Code) as the agent that drives the stages.

Built by David Ross. Hebrew sources from [Sefaria](https://www.sefaria.org).
