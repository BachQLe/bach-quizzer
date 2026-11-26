# Changelog

## 1.2.1 (2026-11-26)
- One self-contained skill: the pilot / mini quiz is folded into `SKILL.md` (mode routing, pilot ids and titles, follow-ups); `references/mini.md` is retired. Last-10 cold tests are tagged `compound`.
- Docs: GitHub is only the update channel. The skill and page never need it to run, and the page carries on if the update check can't load.

## 1.2.0 (2026-11-26)
- Welcome demo: a brand-new Quizzer (no quizzes yet) writes a 9-question tour to `quizzes/welcome-tour` and opens it: multiple choice, cross-out, math, a table with the calculator, short answer, confidence ratings, a graph with the Text tool, and an FRQ with a rubric. `meta/welcome` records it so it never comes back once deleted.
- The demo's intro says it can be deleted, and its results screen has a Delete demo button (two clicks) that removes the quiz and its results.
- New test: `quizzer/test/welcome.py`.

## 1.1.0 (2026-11-26)
- One zip: the skill (instructions plus the page files) installs from `bachs-quizzer.zip`, so Claude never fetches GitHub in a chat. Setup and updates run from the installed skill.
- Update popup: the page checks jsDelivr for the npm marker `bach-quizzer` and shows what's new, a download link and a message to copy into Claude.
- Updates merge with each person's own changes using `base/` copies kept in their Quizzer.
- Release Action builds the zip into a GitHub Release and publishes the npm marker.

## 1.0.0 (2026-11-26)
- First release on GitHub: the Quizzer page, the quiz, mini quiz and page-edit skills, per-person setup and merge-safe updates, and the self-updating loader.
