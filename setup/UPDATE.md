# Update a Quizzer

Bring the person's Quizzer up to the latest release without losing changes they made to their own copy.

1. Read their copy's `version.json` with `read_file` (path `version.json`). Its `version` is what they have (call it X). No file means a 1.0.0 install.
2. Clone with history and release branches:
   `rm -rf /tmp/bq && git clone -q -b stable https://github.com/BachQLe/bach-quizzer /tmp/bq`
   Read `/tmp/bq/version.json` (the new release, Y). If X equals Y, say they're up to date and stop.
3. Pull their live files to disk in one `read_file` call with `paths` (everything `list_files` shows that also exists in the release, plus `version.json`), and note the artifact's version from `get_artifact`.
4. For each file in `/tmp/bq/quizzer/`:
   - base = `git -C /tmp/bq show origin/release-X:quizzer/<path>`; theirs = their live file; new = the release file.
   - theirs equals base, or they don't have it: take new.
   - theirs differs from base (they customized it): text files get `git merge-file -p theirs base new`; resolve any conflict keeping their customization and the new feature both. Binary files: keep theirs.
   - Files they added that aren't in the release: leave them alone (patch mode keeps them).
5. If `index.html` changed, extract the inline `<script>` and run `node --check` on it. Fix anything the merge broke before publishing.
6. `publish_files` on their slug in patch mode with `base_version` from step 3: every changed file, plus `/tmp/bq/version.json` as `version.json`. Keep their title (don't pass a new one). If the version moved since step 3, pull again and redo the merge.
7. Reply with the release's `notes` from `version.json` as a short "What's new" list, plus one line if you had to resolve a conflict in their changes.
