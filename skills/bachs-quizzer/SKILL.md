---
name: "bachs-quizzer"
description: "Use when Bach says 'quiz me', runs /bachs-quizzer, wants practice questions, FRQs or free-response practice with rubrics, a quiz from his missed pile, a spaced quiz, grading of his written answers, or a review of his results and blind spots. Writes to Bach's Quizzer."
---

# Bach's Quizzer

> Shared copy. This file is loaded from github.com/BachQLe/bach-quizzer by the bachs-quizzer loader. It was written for Bach: when someone else runs it, "Bach" and "he" mean the person you're working with, and the Quizzer is their own copy, at the slug the loader gave you. Bach's course list is only an example of naming; reuse the subjects the person already uses.

Bach's quiz page is already built and published. Your only job is to write questions into its database.

- Artifact slug: the one the loader found (the person's own Quizzer). Without a loader, find it once with `list_artifacts` (query "Quizzer").
- Link: only give it if he asks.

Never rebuild, read, restyle or republish the page. Never use the built-in quiz widget. Never print questions or answers in chat.

## Budget: two tool calls per quiz

1. `ToolSearch` with `select:mcp__claude-artifacts__db_write` (skip if already loaded).
2. One `db_write`.

Nothing else. No `list_artifacts`, `get_artifact`, `list_types`, `guide`, `db_list`, memory reads, past-chat searches or task lists, and no read-back to verify the write. Two exceptions: a quiz built from his missed pile (see "Missed pile and blind spots"), which starts with a single `db_get`, and a quiz with FRQs (see "Free response (FRQ) and rubrics"), which starts with a single `db_get` on the class rubric and may add one more op to the same `db_write`. Grading his written answers is one `db_get` plus one `db_write` (see "Review results"). Only if the write fails because the slug is wrong, find it once with `list_artifacts` (query "Quizzer"); if the page is gone, say so in one line and stop.

Write the questions once, directly inside the `db_write` call. Do not draft them in your thinking or in chat first. Check each answer key as you write it.

Use material already in the chat or project (notes, slides, readings) over general knowledge. Do not re-read a file whose content is already in context; if you must open one, read only the part the quiz covers. If there is no topic at all, ask one short question. Otherwise don't ask or confirm anything.

## The write

One op: `set` on `quizzes/<id>`, no `ifVersion` (it is a new document).

`<id>`: lowercase letters, digits and hyphens: subject, topic, date, a letter, e.g. `econ3010-elasticity-20261114a`. If the write is refused because the id exists, change the last letter and retry.

```json
{
  "title": "Slutsky and consumer choice",
  "subject": "ECON 3010",
  "createdAt": "2026-11-14T18:30:00Z",
  "questions": [
    {"prompt": "...", "choices": ["...", "...", "...", "..."], "answer": "C", "explanation": "..."},
    {"prompt": "...", "answer": "model answer", "accept": ["alt phrasing"], "explanation": "..."}
  ]
}
```

- Write only these fields. No `id` or `topic` (the page infers them), and no `type` except `"graph"` on a graph question or `"frq"` on a free-response question. Add `availableAt` only for a spaced quiz (see "Missed pile and blind spots"), and `kind` only as below.
- `kind` (hidden tag, never mention it to Bach): `"test"` for a practice test, mock exam or exam simulation (spans the exam scope, usually 20+ questions); `"compound"` for a cumulative quiz that mixes several topics or units (a last-10 cold test, a unit review, a mixed missed-pile quiz across topics). Leave it out for an ordinary single-topic quiz. The Stats tab's predicted test score weights tests about 4x and compound quizzes about 2.5x, on top of a 12-hour recency half-life, so tag honestly.
- `createdAt` is required: the current UTC time (if you only know the date, estimate the time; never run a tool for it). It must be later than any quiz you wrote earlier in this chat, so the new quiz sorts first and opens.
- `title` is specific ("Slutsky and consumer choice", not "Quiz 3").
- `subject` is the folder. Reuse these exactly when they fit: `ECON 3010`, `PSYC 2005`, `SOC 2870`, `ANTH 2444`, `Linear Algebra`, `French`. Otherwise use the course code he uses, or 1-3 words in Title Case. The project or course of the chat decides it.
- Multiple choice: 4 choices, `answer` is the letter. `**bold**` and `` `code` `` render.
- Short answer: no `choices`. It auto-grades only on a near-exact match with `answer` or `accept`, so keep those short.
- Math (subscripts, partial derivatives, integrals, fractions, sums): write LaTeX as `$...$` inline or `$$...$$` for display, in prompts, choices and explanations, e.g. `$\\frac{\\partial U}{\\partial x_1}$` or `$\\int_0^1 f(x)\\,dx$`. Backslashes are doubled because this is JSON. Plain dollar amounts like $4 are fine. If the math starts with a digit, use `\\(2x+3\\)` instead. Never put `$` inside backticks.
- Table, only when a question needs data laid out (a demand schedule, payoff matrix, results): add `"table": {"headers": ["Price", "Qty"], "rows": [["$4", "100"], ["$5", "80"]]}` to that question. Max 8 columns and 12 rows. The question itself stays in `prompt`. Don't use tables for decoration.
- Graph question, when the topic is something he should sketch (functions, transformations, supply and demand, indifference curves, budget lines, distributions): `{"type": "graph", "prompt": "Sketch $y=(x-2)^2-1$ and mark the vertex.", "graph": {...}, "answer": "words describing the graph", "explanation": "..."}`. The page shows graph paper with Pencil, Line (drag the faint middle dot to bend it; there is no separate curve tool), Arrow (a line with a head; click the tool again for heads at both ends), Dot, Open dot, Eraser, Edit, Snap, Undo and Clear, plus a Letter tool when the question sets point letters. At the end it overlays the real graph on his drawing (Overlay, Mine, Answer views) and he marks it Good or Bad himself, so it is self-graded like a written answer. `answer` is a short text description of the correct graph (it is what shows in results and the missed pile). `graph` holds the axes and the answer key: `{"xMin": -2, "xMax": 6, "yMin": -3, "yMax": 8, "xStep": 1, "yStep": 1, "xLabel": "x", "yLabel": "y", "given": {...}, "answer": {"curves": [{"fn": "(x-2)^2-1"}], "dots": [{"x": 2, "y": -1}], "vlines": [], "hlines": []}}`. `given` (optional, same shape as `answer`) is drawn on the paper before he starts, in blue, e.g. the parent function. A curve is `{"fn": "<formula in x>"}` or `{"points": [[x, y], ...]}` for polylines and line segments, plus optional `"domain": [a, b]` (piecewise pieces) and `"dash": true`. Formulas support + - * / ^, parentheses, `2x` style multiplication, pi, e and sin cos tan asin acos atan sqrt cbrt abs exp ln log floor ceil sign, e.g. `"1/(x-1)+2"`, `"2sin(x)"`, `"abs(x-1)"`, `"e^x"`. A dot is `{"x": 2, "y": 3, "open": true}` (open or closed), and may carry `"label": "A"` (up to 4 characters) to draw a point letter beside it. `vlines` and `hlines` are numbers, drawn dashed, for asymptotes. Add `"arrows": "end"`, `"start"` or `"both"` to a curve to put arrowheads on its ends (`both` for end behavior; `end` for a ray or vector given as two `points`). Letters are set by the question: put `"letters": ["A", "B", "C"]` in `graph` and the Letter tool offers only those letters, so he places each one himself; without `letters`, the labels on the answer `dots` become the choices. Give the answer dots matching `label`s, and name the points in `answer` and `explanation` ("A is the vertex"). Use letters only when the question asks him to mark named points; with none the tool is hidden. For supply and demand or other economics curves, use `points` or linear `fn` with labelled axes (`xLabel` "Quantity", `yLabel` "Price"). Keep ranges small and gridlines at whole numbers so he can place lattice points; put the points he must mark in `dots`. Pick a range where the answer is fully visible, up to about 10 gridlines per axis. Graph questions need no `choices`. Use 1-3 per quiz alongside the usual questions unless he asks for a graphing quiz.

## Free response (FRQ) and rubrics

Use when he asks for FRQs, free response, essay or long-answer practice, or the class exam has them. The page shows a tall writing box. After Reveal he ticks the rubric bullets his response hit; 70% of the points counts as right. Nothing auto-grades.

```json
{"type": "frq", "prompt": "A city taxes sellers of coffee $2. Explain who bears the burden and why.", "points": 6, "rubric": ["Says incidence depends on relative elasticity (2)", "Explains the less elastic side bears more (2)", {"text": "Applies it to the coffee market", "pts": 2}], "explanation": "Full credit names the mechanism and applies it. Naming who pays without why is partial."}
```

- **NEVER write a sample, model or exemplar response for a long FRQ.** Not in `answer`, `explanation`, `rubric`, or chat. The rubric is the only guide. Leave `answer` out. Use `answer` only for a one or two sentence response (a definition), as short key points.
- `rubric` = the bullets graders look for. Each is one observable criterion (claim stated, mechanism named, evidence cited, counterargument addressed, graph labeled), under 20 words, with points as a trailing `(2)` or `{"text", "pts"}`. 3-8 bullets. Points sum to `points`; no `choices`.
- `explanation` says what separates full credit from partial credit as criteria, not as an answer.
- Prompts can run to about 80 words and can use `table`. 3-5 FRQs per quiz unless he gives a number; they can sit beside multiple choice. Use `"kind": "test"` for a full exam simulation.
- Written in the class's grading style: match the point structure, wording and partial-credit habits in the class rubric below, or in material in the chat.

### Class rubric (the class folder)

The class folder is the quiz `subject`. Its shared grading tendencies live as markdown in the db at `rubrics/<subject-key>` (key = subject lowercased, non-alphanumerics to hyphens, e.g. `ECON 3010` -> `econ-3010`). The page shows it under the results as "Class rubric" and puts it in the "Copy prompt" grading text.

```json
{"op": "set", "path": "rubrics/econ-3010", "data": {"subject": "ECON 3010", "key": "econ-3010", "updatedAt": "2026-11-23T19:40:00Z", "markdown": "# ECON 3010 FRQs\n- Reward labeled graphs\n- State the mechanism before the example\n\n## Partial credit\n- Correct reasoning from a wrong number still earns most points"}}
```

- Before writing FRQs for a subject, one `db_get` on `rubrics/<subject-key>`. If it exists, shape each question's bullets to it.
- If it doesn't exist and the material in the chat shows how that class grades (a pasted rubric, graded feedback, a syllabus, an FRQ guide, his own description), add a second op to the same `db_write`: `set` on `rubrics/<subject-key>`, no `ifVersion` for a new doc. If it exists and you are adding to it, `set` with the `ifVersion` from the `db_get`, keeping every line already there.
- Only record grading tendencies he gave or the course material states. Don't invent a class's grading policy, and don't create a rubric from a guess.
- Keep it under about 40 lines: `#`/`##` headings and `- ` bullets, plus `**bold**` where needed. Classes with similar tendencies share one doc. If one class has different assignment types (essays vs problem sets), use a `##` section for each in the same doc.
- When he pastes new grader feedback or a rubric for a class, update the doc.
- Per-question `rubric` bullets are specific to that question. The class rubric is the general layer under them.

## Questions

- 10 unless he gives a number. Multiple choice does most of the work: quizzes of 10 or fewer are all multiple choice. Around 15 questions, add 1-2 short short answers (1-3 words: a term, a number, a formula, a translation) with `accept` variants so they auto-grade. Use more short answer only when he must produce the answer (formulas, translations).
- Apply, compute, or catch a misconception, not trivia. Easy to hard.
- Plausible distractors (common errors, neighboring concepts). No "all of the above". Spread the correct letter.
- Each question stands alone.
- Keep it tight: prompt under 40 words, each choice under 12 words, explanation 1-2 sentences under 35 words saying why the answer is right and why the tempting one is wrong.

Then reply in one line: "10 questions on X are in your Quizzer under ECON 3010." Nothing more.

## Review results

- If he pastes the "Copy results for Claude" text, work from that. No tool calls.
- Otherwise one `db_get` on `results/<quiz id>` (same id as the quiz). Load `db_get` with ToolSearch if needed. Only if you don't know the id, `db_list` `results` once and match by `title` or latest `finishedAt`. If there is no result, he hasn't hit "Reveal answers" yet.
- A result has `score`, `total`, `history`, and `items[]` with `prompt`, `yourAnswer`, `correctAnswer`, `correct`, `flagged`. FRQ items also carry `type: "frq"`, `points`, `pointsEarned` and `rubric[]` (`text`, `pts`, `met`), and a long FRQ's `correctAnswer` is "(see rubric)". For an FRQ, teach from the unmet bullets: what the response needed to do, as criteria. Never write a model response.
- **Grade my quiz** ("grade my quiz", "grade my FRQs", "grade my short answers", or he pastes the grading prompt): write the grades straight into the page instead of telling him what to tick.
  1. One `db_get` on `results/<quiz id>` (or work from the pasted text if it has everything). For FRQs also read `rubrics/<subject-key>` once if it isn't already in this chat.
  2. Judge each FRQ item (`type: "frq"`) bullet by bullet against its `rubric`, and each short-answer item (its `correctAnswer` doesn't start with a letter like `B.`) on meaning, not wording. Skip graph items and anything in `dropped`.
  3. One `db_write`: `set` on `grades/<quiz id>`, no `ifVersion` (if refused because it exists, `db_get` it and retry with its version):
  ```json
  {"quizId": "econ3010-elasticity-20261114a", "finishedAt": "<the results doc's finishedAt, copied exactly>", "gradedAt": "2026-11-23T20:30:00Z", "items": [{"n": 9, "verdict": "partly", "met": [true, true, false], "note": "Named the mechanism; never applied it to the coffee market."}, {"n": 4, "verdict": "got", "note": "Right term."}]}
  ```
  `n` is the item's `n`. FRQ: `met` has one boolean per rubric bullet, in order (the page ticks them; 70% of the points counts as right). Short answer: `verdict` is `got` or `missed` (`partly` counts as missed). `note` is one or two sentences on what earned or lost credit, as criteria, quoting him under 15 words. Never write a sample or model response. Be honest and don't round up. `gradedAt` is the current UTC time and must change on every regrade.
  4. The page applies it live: ticks the rubric, sets I got it / Missed it, shows the note under each answer, and re-syncs his results and missed pile. Reply in one or two lines (new score, the main gap). No per-bullet list in chat unless he asks.
- Cover misses first, then flagged-but-right. Teach the idea behind each in a sentence or two and name any pattern across misses. Offer one follow-up quiz on the weak spots.

## Missed pile and blind spots

The page keeps a ready-made summary per subject, so don't dig through individual results. One `db_get` on `review/<subject-key>`. The key is the subject lowercased with every run of non-alphanumerics turned into a hyphen (`ECON 3010` -> `econ-3010`, `Linear Algebra` -> `linear-algebra`). No doc means he hasn't revealed a quiz in that subject yet.

Fields: `missed[]` (newest first, up to 40: `prompt`, `type`, `choices`, `answer`, `explanation`, `table`, `misses`, `tries`, `lastConfidence`, `blindSpot`), `unresolved` (count), `blindSpots` (count of sure-but-wrong), `confidence` (`sure`, `unsure`, `guess`, each `{n, right}`), and `recent[]` (quiz `title`, `score`, `total`, `tries`, `dueAt`).

- **Missed-pile quiz** ("quiz me on what I missed"): take up to 10 from `missed`, blind spots first, then most misses. Write them verbatim (same `prompt`, `choices`, `answer`, `table`, and for FRQs `rubric` and `points`) so a correct answer clears them from the pile; the page matches on the prompt text. Title like "ECON 3010 · missed pile". If the pile has fewer than 10, use what's there and say so in the reply.
- **Last-10 cold test**: about half from `missed`, half fresh or rephrased questions on concepts he got right before, since those fade too.
- **Analyze my holes**: lead with `blindSpot` entries (he was sure and wrong, so it's a wrong model, not a slip), then repeated misses, then shaky-but-right. Compare `sure` accuracy to `unsure` and `guess`: if they're close, his confidence isn't tracking what he knows. Name the pattern in a sentence or two; don't list every question.
- **Stats and blind spots** ("stats", "how am I doing", "blind spots"): the Quizzer's Stats tab already computes a predicted test score (heavily weighted to recent work and to `kind` test/compound quizzes), accuracy per quiz on a time axis, per-day volume, pie breakdowns and a Blind spots list from `results/*` (3 days, 7 days or all time), so point him there instead of recomputing by hand. In chat, work from the same data (`db_list` on `results`, filter by subject and `finishedAt`) and rank questions by the same signals: missed 2+ times, a fast miss (wrong in well under his median seconds, which usually means he believed it), wrong after being right before, and still wrong on the latest attempt. Use real sure-but-wrong data from `review/<subject-key>` only when it has any. Without confidence ratings, say the ranking is a proxy and suggest turning on Conf. Group related misses into rules (e.g. "CI excludes 0 means significant") and call out asymmetries (right when X, wrong when the mirror case). Check the exam scope first so he doesn't study material that isn't on the test.
- **Spaced quiz** ("spaced quiz", "schedule a quiz on what I missed"): built like the missed-pile quiz (one `db_get` on `review/<subject-key>`, hardest first: blind spots, then most `misses`, then lowest confidence, up to 10, written verbatim), plus `"availableAt"`: the current UTC time + 8 hours as an ISO string (e.g. `2026-11-16T02:23:00Z`; work it out from the timestamp in the chat, don't run a tool). Title "<subject> · spaced". The page keeps it locked in his To do list with a countdown and opens it when the time comes. Reply in one line with his local time (America/New_York): "10 hard questions on X are scheduled in your Quizzer for 9:23 PM." If the pile is empty, say so and don't schedule anything.