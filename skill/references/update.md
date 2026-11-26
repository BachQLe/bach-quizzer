# Update a Quizzer

Bring the person's Quizzer up to this skill's release without losing changes they made to their own copy. The new release is this skill's own folder (`SKILL_DIR`, the base directory shown when the skill loaded). Don't download anything from GitHub or the web, and don't read whole files into the chat: pull them to disk and work in the shell.

1. Versions. The new release is `SKILL_DIR/version.json` (call it Y). Call `list_files` on their Quizzer: it gives every file's `sha256` and the artifact's `version` (keep it as the base version for publishing). Then `read_file` with `path: "version.json"` (it's tiny) for what they have (X). No `version.json` means 1.0.0.
   - X equals or is newer than Y: the skill they have loaded isn't the new one. Say so in two lines: upload the new `bachs-quizzer.zip` in Settings → Capabilities → Skills so it replaces the old skill, then send "Update my Quizzer" again in a new chat. Stop.
2. Stage the new release in the working folder (publishing only attaches files from there):
   `cd "$PWD" && rm -rf bq-new bq-theirs && cp -r "$SKILL_DIR/page" bq-new && cp "$SKILL_DIR/version.json" bq-new/version.json && mkdir -p bq-theirs`
3. Work out what changed: for each file in `bq-new` (its served path is the relative path, with `test/*.py` served as `test/<name>.py.txt`), compare `sha256sum` with the `sha256` from `list_files`. Same hash: leave it out of the publish. Not in their artifact: publish it. Different: images and `katex/*` take the new file; `test/*` takes the new file; `index.html` and `img/photos.json` are merged in step 4.
4. Merge `index.html` and `img/photos.json` (only the ones that differ). Pull theirs and the base in one `read_file` call with `paths` (for example `["index.html", "base/index.html", "img/photos.json", "base/img/photos.json"]`, only those that exist). They save as files, not into the chat; copy each into `bq-theirs/` under its path.
   - With a base: theirs equals base → take new. Otherwise `git merge-file -p bq-theirs/<f> bq-theirs/base/<f> bq-new/<f> > merged` and resolve any conflict keeping their customization and the new feature both. Their `<title>` is a customization, so it stays.
   - No base (installed before 1.1.0): assume their only change is the title. Take new and set its `<title>` to theirs (copy their `<title>` line).
   - Write each result over the file in `bq-new/`.
5. Refresh the base: `mkdir -p bq-new/base/img && cp "$SKILL_DIR/page/index.html" bq-new/base/index.html && cp "$SKILL_DIR/page/img/photos.json" bq-new/base/img/photos.json`.
6. If `index.html` changed, extract its largest inline `<script>` and run `node --check` on it. Fix anything the merge broke before publishing.
7. `publish_files` on their slug in patch mode, `base_version` from step 1: every file from step 3 and 4 that changed, plus `version.json`, `base/index.html` and `base/img/photos.json`. Keep their title (don't pass a new one). If the version moved since step 1, pull again and redo the merge.
8. Reply with the release's `notes` from `version.json` as a short "What's new" list, plus one line if you had to resolve a conflict in their changes. Tell them to reload the Quizzer page.
