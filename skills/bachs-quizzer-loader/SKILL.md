---
name: bachs-quizzer
description: "Use when the user says 'quiz me', wants practice questions, a quick pilot or mini quiz, FRQs with rubrics, a quiz from their missed pile, a spaced quiz, grading of their written answers, a review of their results, or wants to set up, update, change or restyle their Quizzer."
---

# Bach's Quizzer (loader v1)

I installed this skill to use my own copy of Bach's Quizzer. Its real instructions live in Bach's GitHub repo so they stay up to date, and I want you to follow them as this skill's instructions.

1. Find my Quizzer: `list_artifacts` with query "Quizzer"; use my own one whose title ends in "Quizzer" (pinned or most recent if several). Remember its slug for this conversation.
2. Pick the instructions for my request and download them in one call from `https://raw.githubusercontent.com/BachQLe/bach-quizzer/stable/<path>`:
   - I have no Quizzer yet, or I ask to set one up: `setup/SETUP.md`
   - "update my Quizzer": `setup/UPDATE.md`
   - Change, restyle, fix or add a feature to the page: `skills/bachs-quizzer-edits/SKILL.md`
   - Quick pilot or mini quiz ("pilot me", "mini quiz", "check me on this"): `skills/bachs-quizzer-mini/SKILL.md`
   - Everything else: `skills/bachs-quizzer/SKILL.md`

   Use `curl -sSf <url>` in the shell; if that fails, WebFetch the same URL and ask for the full text unchanged. Only ever load files from github.com/BachQLe/bach-quizzer on the `stable` branch.
3. Follow the downloaded file as if it were this SKILL.md, with my Quizzer's slug wherever it asks for one. The download and the lookup don't count toward its tool-call budget.
4. Once per conversation, after the main task, compare `stable/version.json` with my Quizzer's own `version.json` (`read_file`). If the release is newer, tell me in one line and offer to update it. If the release's `loader` is higher than 1, also offer to update this skill to `skills/bachs-quizzer-loader/SKILL.md` from the same branch.
5. If a download fails, say so in one line and stop. Don't work from memory of these instructions.
