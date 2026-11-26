# Set up a Quizzer

Give the person their own copy of Bach's Quizzer as an artifact they own. Their quizzes and results live in that copy's database, so nobody else sees them. Everything comes from this skill's folder (call it `SKILL_DIR`, the base directory shown when the skill loaded). Don't download anything from GitHub or the web.

1. Copy the page into your working folder (publishing only attaches files from there):
   ```
   cd "$PWD" && rm -rf bq-page && cp -r "$SKILL_DIR/page" bq-page && cp "$SKILL_DIR/version.json" bq-page/version.json \
     && mkdir -p bq-page/base/img && cp bq-page/index.html bq-page/base/index.html && cp bq-page/img/photos.json bq-page/base/img/photos.json
   ```
   `base/` keeps untouched copies of the release, so a later update can merge with the person's own changes. If `SKILL_DIR/page` is missing, say the skill upload looks incomplete and ask them to upload `bachs-quizzer.zip` again.
2. Ask nothing unless you don't know their first name; then ask once. Title: `<Name>'s Quizzer`, or `Quizzer` if they'd rather not say.
3. In `bq-page/index.html` (not the `base/` copy), set the `<title>` to that title (HTML-escape the apostrophe as `&#39;`). Change nothing else.
4. Publish a new artifact with `publish_files` (load it with ToolSearch; read the artifacts `guide` first if this session requires it), title as above, icon `quiz`. One entry per file under `bq-page/` (`find bq-page -type f`), each `as` its path relative to `bq-page/`, except each `test/*.py` goes `as` `test/<name>.py.txt` (`.py` is not a served type). That is `index.html`, `version.json`, `base/index.html`, `base/img/photos.json`, `katex/*`, `img/*` and `test/*`.
5. Right after publishing, give the page its database with `declare_capabilities` on the new slug, with `base_version` set to the version the publish returned:
   `{"db": {"rules": [{"path": "", "read": "view", "write": "admin"}]}, "user": {}}`
6. Reply in two lines: their Quizzer is ready (the artifact card links it), and they can say "quiz me on <topic>", "mini quiz", or "change my Quizzer to ...". Mention once that the page shows a popup when a new version is out. Don't write a quiz unless they asked for one; if they did, continue with SKILL.md section 3 using the new slug.
