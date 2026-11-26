# Bach's Quizzer mini quiz (pilot while learning)

> Part of the bachs-quizzer skill. It was written for Bach: when someone else runs it, "Bach" and "he" mean the person you're working with, and the Quizzer is their own copy, at the slug SKILL.md found. Bach's course list is only an example of naming; reuse the subjects the person already uses.

Small check-ins while he studies. Same page and database as SKILL.md's quizzes; the differences are size and scope.

- Artifact slug: the one SKILL.md found (the person's own Quizzer). Never rebuild, read, restyle or republish the page. Never use the built-in quiz widget. Never print questions or answers in chat.
- Two tool calls: `ToolSearch` with `select:mcp__claude-artifacts__db_write` (skip if already loaded), then one `db_write`. Nothing else, and no read-back.

## Scope

5 questions on what he just covered: the section taught in this chat, or the notes/slides he named. Not the whole chunk (the big quiz does that later). Key ideas only, one question per idea, in the order taught. Use what's already in the chat. If there is nothing to quiz on, ask one short question.

These are a pretest of what he just learned, so some misses are expected and fine. Test the idea, not the wording of the notes.

## The write

One op: `set` on `quizzes/<id>`, no `ifVersion`.

- `<id>`: lowercase letters, digits, hyphens: `<subject>-pilot-<yyyymmdd><letter>`, e.g. `econ3010-pilot-20261115a`. If refused because it exists, change the last letter.
- Fields only: `title`, `subject`, `createdAt`, `questions`. No `id`, `topic` or `type`.
- `title`: "Pilot · <specific section>".
- `createdAt`: current UTC time, later than any quiz written earlier in this chat so it sorts first and opens.
- `subject`: use the same folder as his big quiz for that material so the missed pile merges: `ECON 3010`, `PSYC 2005`, `SOC 2870`, `ANTH 2444`, `Linear Algebra`, `French`; otherwise the course code or 1-3 words in Title Case.
- All multiple choice: 4 choices, `answer` is the letter, plausible distractors (common errors, neighboring concepts), no "all of the above", spread the correct letter. Prompt under 40 words, choices under 12 words, explanation 1-2 sentences under 30 words saying why it's right and why the tempting one is wrong.
- Math as LaTeX `$...$` (backslashes doubled because it's JSON); if the math starts with a digit use `\\(2x+3\\)`. `**bold**` and `` `code` `` render.

Reply in one line: "5 pilot questions on X are in your Quizzer under ECON 3010."

## FRQ pilots

If he asks to pilot a free-response topic, write 1-2 `type: "frq"` questions instead of 5 multiple choice, following SKILL.md's "Free response (FRQ) and rubrics" section: rubric bullets with points, no sample or model response, and one `db_get` on `rubrics/<subject-key>` first so the bullets match the class's grading.

## The loop

Teach a section, then pilot, he answers in the page, then recap his misses, then the next section. In a study session you may end a section with one line offering a pilot, nothing more.

When he says he's done or pastes his results: one `db_get` on `results/<quiz id>` (or work from the pasted text), explain each miss in a sentence or two, and keep teaching. Don't re-quiz until he asks.