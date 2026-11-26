# Releasing a change (maintainer only)

GitHub is only the delivery channel for updates. The Quizzer page and the skill must never need GitHub to work: nothing in `skill/` or the page may fetch GitHub, and if the update check can't load, the page carries on as normal.

For Bach's own Claude. Bach's live Quizzer is the original; this repo is what friends' zips are built from. Friends' Claudes never run this file.

When Bach says "ship it", "release this" or "push it to GitHub" after a page or skill change:

1. Get write access: `add_repo` for BachQLe/bach-quizzer with `access: "push"`, then clone it into the working folder (`git clone https://github.com/BachQLe/bach-quizzer`) and run git there.
2. Bring in what changed:
   - Page: `read_file` with `paths` on Bach's Quizzer (`list_artifacts`, the one titled "Bach's Quizzer") for `index.html` and any other file he changed, copied over `quizzer/`. Photos stay full size here; the build shrinks them for the zip. Run `git diff --stat` and show him a summary, not the whole diff.
   - Skills: Bach's own account skills are the originals: zen-quiz (one self-contained skill for every quiz, pilots included) → `skill/SKILL.md`, and quizzer-page-edits → `skill/references/edits.md`. Port the change into those files, keeping their shared-copy wording ("the slug found in step 1", no GitHub downloads).
3. Bump the version (semver: patch for fixes, minor for features): `version` in `version.json`, plus `released` and one or two plain `notes` (they show in everyone's update popup), and the same number in `const BQ_VERSION = "..."` in `quizzer/index.html`. Add a `CHANGELOG.md` entry.
4. Checks: `node --check` on the inline script, `python3 -I quizzer/test/qa.py index.html`, `python3 -I quizzer/test/update.py index.html` and `python3 -I quizzer/test/welcome.py quizzer/index.html` from the repo root (all expect `errors: []`), then `python3 tools/build.py` (it refuses if `BQ_VERSION` and `version.json` disagree; the zip should stay under 8 MB).
5. Commit to `main`, fast-forward `stable` to it, push both. The Action on `stable` builds the zip, creates GitHub Release `v<version>` with `bachs-quizzer.zip`, and publishes the npm package that triggers everyone's popup. Check it with `gh run list -R BachQLe/bach-quizzer -L 1` if `gh` works; otherwise ask Bach to glance at the Actions tab.
6. Publish to Bach's own Quizzer with `publish_files` (patch mode, `base_version` from `get_artifact`): `index.html` with the new `BQ_VERSION` and `version.json`, so it doesn't offer him an update to his own release.
7. Reply with the version and the notes.

Docs-only changes (`README.md`, `maintainer/`) don't need a version bump: commit to `main` and fast-forward `stable` (the Action re-uploads the same zip).
