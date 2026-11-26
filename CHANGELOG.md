# Changelog

## 1.1.0 (2026-11-26)
- One zip: the skill (instructions plus the page files) installs from `bachs-quizzer.zip`, so Claude never fetches GitHub in a chat. Setup and updates run from the installed skill.
- Update popup: the page checks jsDelivr for the npm marker `bach-quizzer` and shows what's new, a download link and a message to copy into Claude.
- Updates merge with each person's own changes using `base/` copies kept in their Quizzer.
- Release Action builds the zip into a GitHub Release and publishes the npm marker.

## 1.0.0 (2026-11-26)
- First release on GitHub: the Quizzer page, the quiz, mini quiz and page-edit skills, per-person setup and merge-safe updates, and the self-updating loader.
