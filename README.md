# Bach's Quizzer

A retro pixel quiz page that lives as a Claude artifact, plus the Claude skills that write quizzes into it.

## How it works

- **Everyone gets their own copy.** The first time a friend uses the skill, their Claude builds a Quizzer in their own artifacts from this repo (`setup/SETUP.md`). Their quizzes and results save in their copy's database. Nobody else sees them, Bach included.
- **One skill to install.** `skills/bachs-quizzer-loader/SKILL.md` is a short loader. Each time it runs, Claude downloads the current instructions from the `stable` branch: quizzes (`skills/bachs-quizzer`), mini quizzes (`skills/bachs-quizzer-mini`), page changes (`skills/bachs-quizzer-edits`), setup and updates (`setup/`). Pushing to `stable` updates everyone's quizzing with no re-install.
- **Customize freely.** People can ask their Claude to change their own page. "Update my Quizzer" does a three-way merge (`setup/UPDATE.md`) between the release they installed (tag `vX`), their copy, and the new release, so their changes survive.
- **Update notices.** Each copy keeps a `version.json`. When `stable` is newer, the loader tells them a new version is out and offers to update.

## Releasing

1. Commit to `main`; bump `version` in `version.json` (and `loader` if the loader itself changed), add `notes` and a `CHANGELOG.md` entry.
2. Fast-forward `stable` to `main`, tag `v<version>`, push `main`, `stable` and the tag.
3. Bach updates his own Quizzer the same way as everyone else: "update my Quizzer".

## Install (friends)

Upload `skills/bachs-quizzer-loader/SKILL.md` as a skill in Claude, then say "set up my Quizzer" or just "quiz me on <topic>".

## Credits

Background photos are from [Unsplash](https://unsplash.com) (Unsplash License); the Tokumeien garden photo is by [@dreiimos](https://www.instagram.com/dreiimos/). *The Great Wave off Kanagawa* is Hokusai's public-domain print. KaTeX is MIT-licensed.
