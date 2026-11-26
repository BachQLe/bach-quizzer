# Set up a Quizzer

Give the person their own copy of Bach's Quizzer as an artifact they own. Their quizzes and results live in their copy's database, so nobody else sees them.

1. Get the release:
   `cd "$PWD" && rm -rf bq-release && git clone -q --depth 1 -b stable https://github.com/BachQLe/bach-quizzer bq-release`
   Clone into your working folder (where `pwd` points), not /tmp: publishing only attaches files from the working folder, by absolute path. If git can't reach GitHub, say so in one line and stop.
2. Ask nothing unless you don't know their first name; then ask once. Title: `<Name>'s Quizzer`, or `Quizzer` if they'd rather not say.
3. In `bq-release/quizzer/index.html`, set the `<title>` to that title (HTML-escape the apostrophe as `&#39;`). Change nothing else.
4. Publish a new artifact with `publish_files` (load it with ToolSearch; read the artifacts `guide` first if this session requires it), title as above, icon `quiz`. Files, each `as` its path under `quizzer/`:
   - `index.html`, `katex/katex.css`, `katex/katex.min.js`, `img/photos.json` and every `img/*.webp`
   - `test/mock.js`, `test/texts-quiz.json`, and each `test/*.py` as `test/<name>.py.txt` (`.py` is not a served type)
   - `bq-release/version.json` as `version.json` (this records which release they have, so updates can merge with their changes)
5. Right after publishing, give the page its database with `declare_capabilities` on the new slug, with `base_version` set to the version the publish returned:
   `{"db": {"rules": [{"path": "", "read": "view", "write": "admin"}]}, "user": {}}`
6. Reply in two lines (add a third about the skill card if you show one in step 7): their Quizzer is ready (the artifact card links it), and they can say "quiz me on <topic>", "mini quiz", or "change my Quizzer to ...". Don't write a quiz unless they asked for one; if they did, continue with the quiz instructions now, using the new slug.
7. If the person doesn't already have a skill named `bachs-quizzer` (check with ListSkills if you have it), offer it so "quiz me" works from now on: read `bq-release/skills/bachs-quizzer-loader/SKILL.md` and call `propose_skills` with kind `new`, name `bachs-quizzer`, the description from its frontmatter, and the whole file as `skillMd`. Don't alter the text. If `propose_skills` isn't available, tell them in one line to upload `skills/bachs-quizzer-loader/SKILL.md` from the repo as a skill.
