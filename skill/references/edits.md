# Editing Bach's Quizzer page

> Part of the bachs-quizzer skill. It was written for Bach: when someone else runs it, "Bach" and "he" mean the person you're working with, and the Quizzer is their own copy, at the slug SKILL.md found. Bach's course list is only an example of naming; reuse the subjects the person already uses.

The Quizzer is a published multi-file artifact.
- Slug: the one SKILL.md found (the person's own Quizzer).
- The design rules below are Bach's defaults. In someone else's copy, their own wishes win; keep the rest.
- Files: `index.html` (all CSS + JS inline), `katex/katex.css`, `katex/katex.min.js`, `img/*.webp`, `img/photos.json`. Only `index.html` normally changes.
- Writing questions into its database is SKILL.md's job. This file is only for changing the page.

## Design rules (Bach's stated preferences)
- Keep the retro pixel look: Silkscreen on buttons, tabs, labels, pills, question numbers, the timer and the score. Keep the pixel corner brackets on the card. Don't swap pixel UI for a plain sans font.
- Cormorant Garamond is for prompts and titles. Inter is for answers, explanations and body text (weight 400 on glass).
- No distracting motion while he is answering. On the question and review screens, `body.focus` pauses the background drift, hides scanlines, the shuffle button and the credit. Only color changes of 120ms or less on interaction. At most a 120ms fade between questions. Nothing slides, bounces or scales.
- Motion is allowed only between screens (220ms fade plus a 6px rise) and once on results (score count-up and a staggered fill of the result bar right after Reveal, never on re-renders).
- In-question interactions (select, cross-out, flag, keyboard) update the DOM in place through `paintQuestion(k)` and must never rebuild the card.
- Everything respects `prefers-reduced-motion`.
- Results list: missed first, then Check, then correct. Correct items are quieter, with the explanation in a `<details>`.

## Don't touch
Data and storage logic, DB paths (`quizzes/<id>`, `results/<id>`), the quiz schema, `validQuiz()`, `pushResults()`, `resultsText()`, keyboard shortcuts, calculator and timer logic. Changing these breaks quiz writing or saved results. Also leave `BQ_VERSION` and the update-check block alone: the release steps own them, and a wrong version makes the update popup misfire.

## Workflow
1. Pull the live files to disk in one call: `read_file` with `paths: ["index.html", "katex/katex.css", "katex/katex.min.js", "img/photos.json", "test/mock.js", "test/qa.py.txt", "test/update.py.txt"]` (they save unwrapped, nothing passes through context). Copy them into a working folder (`test/qa.py.txt` becomes `test/qa.py`), keep an `index.orig.html` backup, and note the version.
2. Make targeted edits with Edit, not full rewrites.
3. Check syntax: extract the inline `<script>` to a file and run `node --check`.
4. QA: `python3 -I test/qa.py index.html shots` (serves the folder on port 8766, injects `test/mock.js`: 45 quizzes over 5 subjects with math, tables, a long prompt, short answers, graph and FRQ questions, results, a folder and a class rubric). It walks hub, stats, a full quiz, reveal, rubric ticks, a Claude grades doc, dropping a question and back to the hub at desktop 1280x800, phone 390x844 and reduced motion. Pass means `errors: []`, `card_survives_clicks: true`, 3 writes after 3 rubric ticks, `grades_applied` 2 notes and 2 ticks, `drop_ok: true`. Screenshots land in `test/*.png`. Extend the mock and the walk when you add a feature (the Letter tool isn't covered yet). When Bach asks for subagents, build with one Sonnet agent and QA with a separate one using this harness.
5. Review the full diff yourself before publishing.
6. Other chats edit this page too. Right before publishing, `get_artifact`: if the version moved, pull the new `index.html` as `index.live.html`, three-way merge with `git merge-file -p index.html index.orig.html index.live.html`, resolve any conflict keeping both sides, and rerun QA. Then `publish_files` with `index.html` (plus `test/mock.js` and `test/qa.py` as `test/qa.py.txt` if you changed them; `.py` is not a served type) using that version as `base_version`. Patch mode keeps the other files.
7. Reply in a few lines covering what changed, plus a screenshot or two. Don't paste the link unless he asks.

## Stats tab (added 2026-11-19)
The hub has Library and Stats toggles (`statsOn`, `statsRange` in localStorage `zq:statsOn` / `zq:statsRange`). Stats is read-only: `computeStats()` derives everything from `resultsById` (filtered by the active subject tab and a 3 day / 7 day / all time range) and never writes to the db. It draws inline SVG with no library: tiles, accuracy per quiz with a rolling 3-quiz average, per-day stacked bars, quiz-by-quiz bars, by-subject and answer-type bars, and a Blind spots list. Blind spots group identical prompts with `norm(prompt)` across all attempts and flag: missed 2+ times, fast miss (at or under 0.8x the median seconds, clamped 15-40s), was right before, still open. To change the flags or charts, edit `computeStats`, `trendSvg`, `daysSvg` and `statsHtml`. Keep the pixel look and no motion, and test with a mock `window.claude` db that has results with repeated prompts.

## Stats rework (2026-11-23)
- Hub title is "Quiz home page" (Quizzes view) or "Your stats" (Stats view). The Library/Stats toggle is a pixel slider `.vslide` (Quizzes / Stats, with icons).
- Predicted score bar shows only "Predicted test score", the best-guess number, and the confidence underneath (range is in the hover title). `predictScore` uses the latest answer per distinct question, a 12-hour half-life, and `KIND_W` multipliers (test 4, compound 2.5). `kind` comes from the quiz doc (`validQuiz` passes through `kind: test|compound`, hidden) or, for older quizzes, a title regex in `kindOfResult`.
- Range is a dropdown (`ddHtml`/`wirePops`), Quiz by quiz has a sort dropdown (`statsSort`) and a %/fraction toggle (`statsFmt`, applies to all bar rows, pie legends and per-day labels). Blind spots explanation lives behind a `?` popover (`helpHtml`).
- Units are spelled out in lowercase ("53 seconds", "4.2 hours") because Silkscreen's s looks like a 5.
- Pie charts via `pieSvg` (donut with surface gaps). Sections are `.st-sec` with span classes (`s-full`, `s-wide`, `s-nar`, `s-half`, `s-third`).
- Extended view (`statsWide`, `zq:statsWide`, 1100px+ only): the hub goes wide, the nav becomes a left sidebar, and stats lay out on a 12-column grid.
- Accuracy-per-quiz points sit on a real time axis and show a hover tooltip with the quiz name, score and time.

## Graph questions (added 2026-11-23)
A question with `type: "graph"` shows a drawing pad instead of choices or a text box. Everything lives in one block of index.html, headed `/* graph questions: draw it, then compare with the real graph */`, just before `/* results → db */`: `gParse`/`gCompile` (safe formula parser, no eval), `gClean`/`gShapes`/`gDescribe` (schema cleaning, called from `validQuiz`), `gDraw` and friends (canvas painting), `gPadHtml`/`gMountPad` (question screen: Pencil, Line, Dot, Open dot, Eraser, Snap, Undo, Clear, Ctrl+Z), `gResHtml`/`gMountRes` (results: Overlay / Mine / Answer views). His drawing is `st.answers[k] = {s:[{t:"pen"|"line"|"dot"|"odot", p:[[x,y],...]}]}` in graph coordinates, or null when empty. Graph questions are self-graded: `rightOf` returns null until he taps Good or Bad (`st.self[k]`), the same path as short answers. Hooks into existing code are small: the type check and graph branch in `validQuiz`, a branch in `rightOf` and `answerText`, `gPadHtml`/`gMountPad` in `renderQuestion`, `gResHtml` plus `gMountRes()` in `renderResults`, and the Grade yourself pills (labelled Good and Bad for graphs). Drawing repaints only the canvas and calls `refreshDots()`, so the card never rebuilds. Results grading now keeps the results list scroll position. The schema is documented in the block's header comment and in SKILL.md.

When publishing with `edit_version`, send every edit in one call and check the large module insert is in it: `renderResults` calls `gMountRes()` unconditionally, so a partial publish breaks the results screen for every quiz. Check the new `total_lines` against the expected count afterwards.

## Hub layout rework (2026-11-23, second pass)
- No hub title or eyebrow any more. The top is a slim centered navbar (`.hub > .card.lib.nav`): the Quizzes/Stats `.vslide`, the `.hub-q` quiz count, and a `#sbTog` button at its left end that opens and closes the class sidebar in place (`sbHidden`, localStorage `zq:sbHidden`, `.hub.noside`).
- Below it, `.hub-row` holds the class sidebar `aside.card.lib.side#hubSide` (subjects stacked, carets expand each subject's folders, saved in `zq:sbOpen`, folder rows carry `data-drop` so quizzes can be dragged onto them) and the body card. At 760px and below the sidebar is hidden and the horizontal `.tabs.top` strip shows in the navbar. The hub has a fixed viewport height in every view. Extended (`statsWide`) only widens the hub now.
- The slider thumb uses `110ms cubic-bezier(.55,0,.1,1)` and the view switches after 110ms. Bach wants it fast with a soft landing.
- Overview: the predicted score sits at the top of Overview. In compact view the tiles are 3 on the left and 2 on the right. In extended view they are one centered row of 3 above one centered row of 2.
- The %/# toggle (`.ftog` with a sliding `.fthumb`) swaps values in place from `data-pct`/`data-frac`. It never re-renders, so nothing moves.
- Blind spots and the right column (Quiz by quiz + Answer type) sit in `.st-duo` with aligned tops and bottoms. Below 700px of stats width, Answer type moves to its own section (`.at-in`/`.at-out`).
- Chart titles: "Accuracy per quiz over time" shows dots plus a solid white least-squares trend line, with the slope in the legend (no connecting line, no rolling average). The per-day chart is "Accuracy for quizzes over the past N days" / ", all time", following the range.
- Color rule on the stats page: yellow (gold) means only the 50–79% band. Neutral highlights (tile numbers, icon accents, tooltip score, 80% ref line, hover and focus) are white.
- Test harness: `test/mock.js` and `test/qa.py.txt` are published with the artifact (see Workflow). The mock auto-opens the newest unfinished quiz, so click `#qlib` to reach the hub.

## Graph letters and arrows (added 2026-11-23)
- Tools: Pencil, Line, Arrow, Dot, Open dot, Letter (only when the question has letters), Eraser, Edit. The Curve tool is gone; old `t:"curve"` strokes still draw and edit, and a Line bends by dragging its middle dot.
- Arrow is a `t:"line"` stroke with `ar:"end"|"both"`: `pointerdown` maps the arrow tool to line (`t0` is the tool, `t` the mark type). Clicking the active Arrow tool again toggles one head or two (`gArrowMode`, `cycleTool`, `paintFaces`). Heads are drawn after the clip restore in `gDraw` (`gHead`, `gHeads`, `gDrawHeads`) so they aren't cut off at the plot edge.
- Answer curves take `arrows: "end"|"start"|"both"` (cleaned in `gShapes`). `gCurvePx` keeps only the in-plot part of a formula curve, so the head sits where the curve leaves the view.
- Letters are set by the question: `graph.letters` (array or "A,B,C", `gLetters`), else the `label`s on the answer dots (`gLettersOf`). A dot takes `label` (up to 4 chars; `gLab`; `name`/`letter` accepted). His mark is `{t:"dot", p, l:"A", lp:1}`. The Letter tool face shows the next letter (`gPickLetter`, `gToolFace`); clicking the active tool cycles through the question's letters; placing a letter again moves it; after a placement it jumps to the next unplaced letter. `gPadHtml` falls back to Pencil when the tool is Letter and the question has no letters.
- `gDrawLabel` paints letters in Silkscreen with a dark halo, flipping left/below near the plot edge. `gSummary` (saved as `yourAnswer`) appends `· lettered points A (x, y), ...`. `gDescribe` lists lettered answer dots when `answer` has no text.
- QA: `test/letters.py.txt` (copy to `test/letters.py`, port 8767) opens a graph quiz with letters and arrows, checks the toolbar per question, the letter cycling and moving, arrow ends, and the results overlay. Expect `errors: []`.

## FRQ rubrics (added 2026-11-23)
A question with `type: "frq"` is a free response. It uses the normal `#short` textarea with the `.frq` class (taller) and a `.frq-meta` line ("Free response · 6 pts"). It is self-graded, like short answers and graphs.
- Code lives in the block headed `/* ---------------- FRQ rubrics ----------------`, just before `validQuiz`: `rubClean` (strings with a trailing `(2)` or `{text, pts}` become `{text, pts}`), `rubMax`, `ptsTxt`, `rubGot(k)`, `RUB_PASS` (0.7), `loadClassRubric`, `mdLite`, `paintClassRubric`. Hooks: the frq branch in `validQuiz`, `rightOf` (frq returns null until graded), `renderQuestion`, `renderResults` (`rubH` checklist, `#crub`, `[data-rub]` handler), `gradePromptText`, `resultsText`, `pushResults`, `pushReview`.
- State: `st.rub[k]` is an array of booleans per rubric bullet (`blankState` and `adopt` keep it sized). Ticking a bullet sets `st.self[k]` to whether points >= 70%; the Grade yourself pills still override.
- Class rubric: the doc `rubrics/<subject-key>` (`{subject, key, updatedAt, markdown}`), read once per subject with `db.doc(...).get()` and shown as the `details.crub` "Class rubric" under the results. `mdLite` renders `#` headings, `- ` bullets and paragraphs. bachs-quizzer writes it.
- `pushResults` now adds `type`, `points`, `pointsEarned` and `rubric[{text, pts, met}]` to FRQ items, and `correctAnswer` is "(see rubric)" when a long FRQ has no `answer`. `pushReview` cards keep `rubric` and `points` so missed FRQs can be rewritten verbatim. These are additive. Don't change the existing fields.
- Long FRQs never show a sample response: `answer` is optional and shows as "Key points" only when present.
- Phones: below 640px the whole results card scrolls (`.card.resv`) instead of the inner `.res-list`, so a rubric checklist isn't squeezed. Results re-renders that must keep scroll go through `rerenderResults()`.
- Test with a mock `window.claude` db holding an FRQ quiz plus a `rubrics/<key>` doc: tick bullets and check the mark flips at 70%, the result doc carries `rubric[].met`, and the question card isn't rebuilt while typing. Note the Silkscreen labels render in uppercase, so match text case-insensitively.

## Dropped questions (added 2026-11-23)
- Right-click a result (or its Restore pill) toggles `st.dropped[k]` via `dropQuestion(k, v)`; `isDrop(s, k)` checks it. Dropped questions are left out of `tallyOf`, missed/blind counts, the grading prompt and `resultsText`, listed last and grayed (`.res.dropped`). `pushResults` omits their items (`n` keeps the original numbering) and adds `dropped: [question numbers]`; `pushReview` takes that attempt back out of the card history.

## Performance and sync rules (optimization pass, 2026-11-23)
- `fmt()` is memoized (`fmtMemo`, cleared past 4000 entries, cached only once KaTeX has loaded). Always render text through it.
- `quizStatus` is memoized for one hub render (`qsMemo`, set by `renderHub` around `renderHubInner`).
- Grading actions (rubric ticks, Good/Bad, I got it/Missed it, drop/restore, Claude grades) call `syncSoon()`: a 900ms debounce, then `pushResults()` + `pushReview()`. `flushSync()` runs in `adopt`, `toHub`, Retake, `pagehide` and tab hide. New grading actions go through `syncSoon`, not direct pushes. `reveal()` still pushes at once.
- State autosaves every 5 seconds on the question and review screens, plus on hide and `pagehide`.
- Graph canvases register ResizeObservers only through `gWatch(el, fn)`; `gUnwatch()` runs at every render and graph mount, and draw callbacks return early when `st` is null or the canvas is detached.
- `pruneStates()` drops `zq:state:*` for quizzes no longer in the library, only after a server-confirmed load of fewer than 300 quizzes.
- One `reducedMotion()` helper for the whole page.

## Grades from Claude (2026-11-23)
- `grades/<results doc id>` = `{quizId, finishedAt, gradedAt, items:[{n, verdict, met[], note}]}`, written by bachs-quizzer when he says "grade my quiz". `watchGrades()` (called at the end of `renderResults`) keeps one doc subscription for the open quiz. `applyGrades()` (also run at the top of `renderResults`) applies it once per `gradedAt`, only when `finishedAt` matches `st.revealedAt`, only to short and FRQ items that aren't dropped: it sets `st.rub[k]`, `st.self[k]` and `st.cnote[k]`, stores `st.gradedAt`, then `syncSoon()`. The note shows as `.cnote` ("Claude" label) above the rubric. The gradebar tells him to say "grade my quiz"; Copy prompt stays as the fallback.

## Phones
- At 640px and below `.res-mark` sits on its own row above the prompt, and the stats folder pills scroll sideways in one row (`.rng-f`).
## Update check and popup (added 2026-11-26)
- Block headed `/* ---------------- updates: version check + update dialog ----------------`, just before the toast section. `BQ_VERSION` is the page's release. Artifact pages can't fetch GitHub (the CSP blocks fetch to other hosts), but scripts from `cdn.jsdelivr.net/npm/` load, so each release publishes the npm package `bach-quizzer`, whose `latest.js` only sets `window.__bqLatest = {version, released, notes[]}`.
- `checkUpdates()` runs once, 1.5s after load. `maybeShowUpdate()` (also called from `render()` when no quiz is open) shows `#upd` on the hub only, never during a quiz: notes (escaped), a link to `releases/latest/download/bachs-quizzer.zip`, the Settings → Capabilities → Skills step, and Copy message ("Update my Quizzer to vX..."), Later (this page load) and Skip this version (`zq:updSkip`). Escape and a click on the scrim close it.
- QA: `test/update.py` (copy from `test/update.py.txt`, port 8768) fakes `latest.js` and checks the dialog on desktop and phone, that it stays hidden in a quiz, for equal and older versions and after Skip. Expect `errors: []` and every flag true. `test/qa.py` blocks jsDelivr so its walk is unaffected.

## Welcome demo (added 2026-11-26, v1.2.0)
- The block headed `/* ---------------- first run: the welcome demo quiz ----------------` (just before `maybeStart`) holds `WELCOME_ID` ("welcome-tour"), `WELCOME_QUIZ` (an ordinary quiz doc in the normal schema), `WELCOME_LEDE`, `maybeWelcome()` and `deleteDemo()`.
- `onLibrary` calls `maybeWelcome()` once the server confirms an empty library. It checks `meta/welcome` (and localStorage `zq:welcomed`), writes `quizzes/welcome-tour`, then `meta/welcome {seededAt, quizId}`. The library snapshot announces the quiz, so it opens on its own. Once `meta/welcome` exists the demo is never written again.
- `renderIntro` shows `WELCOME_LEDE` for the demo. `renderResults` adds a `.gradebar.demo-done` with `#delDemo` (first click asks "Yes, delete it", second runs `deleteDemo()`: back to the hub, `deleteQuiz`, and a results delete chained after the pending results write).
- Silkscreen has no ellipsis glyph, so pixel text never uses "…".
- QA: `test/welcome.py` (port 8768): fresh empty db, already seeded, and a full library. Expect `errors: []`, `seeded`, `deleted`, `no_writes`, `no_seed` all true.
