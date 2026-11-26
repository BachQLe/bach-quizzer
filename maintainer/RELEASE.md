# Releasing a change (maintainer only)

For Bach's own Claude. Bach's live Quizzer is the original; this repo is what friends copy from. Friends' Claudes never run this file.

When Bach says "ship it", "release this" or "push it to GitHub" after a page or skill change:

1. Get write access: `add_repo` for BachQLe/bach-quizzer with `access: "push"`, then clone it into the working folder (`git clone https://github.com/BachQLe/bach-quizzer`) and run git there.
2. Bring in what changed:
   - Page: `read_file` on Bach's Quizzer (`list_artifacts`, the one titled "Bach's Quizzer") for `index.html` and any other file he changed, copied over `quizzer/`. Keep the `<title>` as in the repo (friends set their own at setup). Run `git diff` and show him the summary, not the whole diff.
   - Skills: edit `skills/bachs-quizzer*/SKILL.md` directly.
3. Run the page checks: `node --check` on the inline script, and `python3 -I quizzer/test/qa.py quizzer/index.html shots` from the repo root (expects `errors: []`).
4. Bump `version.json` (`version`, `released`, one or two plain `notes`; raise `loader` only if the loader skill changed) and add a `CHANGELOG.md` entry.
5. Commit to `main`, fast-forward `stable` to it, create branch `release-<version>` at the same commit, and push all three. Tags can't be pushed from Claude sessions, which is why releases are branches.
6. Publish the new `version.json` to Bach's own Quizzer with `publish_files` (patch mode, `base_version` from `get_artifact`) so it doesn't offer him an update to his own release.
7. Reply with the version and the notes.

Setup-only or docs-only changes (`setup/`, `README.md`, `maintainer/`) don't need a version bump: commit to `main` and fast-forward `stable`.
