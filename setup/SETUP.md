# Set up a Quizzer

Give the person their own copy of Bach's Quizzer as an artifact they own. Their quizzes and results live in their copy's database, so nobody else sees them.

1. Get the release:
   `rm -rf /tmp/bq && git clone -q --depth 1 -b stable https://github.com/BachQLe/bach-quizzer /tmp/bq`
   If git can't reach GitHub, say so in one line and stop.
2. Ask nothing unless you don't know their first name; then ask once. Title: `<Name>'s Quizzer`, or `Quizzer` if they'd rather not say.
3. In `/tmp/bq/quizzer/index.html`, set the `<title>` to that title (HTML-escape the apostrophe as `&#39;`). Change nothing else.
4. Publish a new artifact with `publish_files` (load it with ToolSearch; read the artifacts `guide` first if this session requires it), title as above, icon `quiz`. Files, each `as` its path under `quizzer/`:
   - `index.html`, `katex/katex.css`, `katex/katex.min.js`, `img/photos.json` and every `img/*.webp`
   - `test/mock.js`, `test/texts-quiz.json`, and each `test/*.py` as `test/<name>.py.txt` (`.py` is not a served type)
   - `/tmp/bq/version.json` as `version.json` (this records which release they have, so updates can merge with their changes)
5. Right after publishing, give the page its database with `declare_capabilities` on the new slug:
   `{"db": {"rules": [{"path": "", "read": "view", "write": "admin"}]}, "user": {}}`
6. Reply in two lines: their Quizzer is ready (the artifact card links it), and they can say "quiz me on <topic>", "mini quiz", or "change my Quizzer to ...". Don't write a quiz unless they asked for one; if they did, continue with the quiz instructions now, using the new slug.
