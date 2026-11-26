# Bach's Quizzer

A retro pixel quiz page that lives as a Claude artifact, plus the Claude skill that writes quizzes into it.

## Install

1. Download **[bachs-quizzer.zip](https://github.com/BachQLe/bach-quizzer/releases/latest/download/bachs-quizzer.zip)**. Don't unzip it.
2. In Claude, open **Settings → Capabilities → Skills** and upload the zip.
3. Start a new chat and say **"set up my Quizzer"**. Claude builds your own Quizzer in your artifacts.

Then say "quiz me on <topic>", "mini quiz", "grade my quiz" or "change my Quizzer to ...".

Can't upload skills on your plan? Attach the zip in a chat and say "set up my Quizzer from this zip". You'll need to attach it again whenever you want quizzes.

## How it works

- **Everyone gets their own copy.** Your quizzes and results save in your copy's database. Nobody else sees them, Bach included.
- **One zip, nothing fetched.** The skill folder holds the instructions (`SKILL.md`, `references/`) and the page itself (`page/`). Claude reads it all from the installed skill, so it never needs GitHub during a chat.
- **Update popup.** Your Quizzer checks for new releases on its own. When one is out, it shows what's new, a download link, and a message to copy into Claude. Upload the new zip (it replaces the old skill), send the message in a new chat, and Claude merges the new page with any changes you made to your copy.
- **Customize freely.** Ask Claude to change your own page. Updates keep your changes.

## Releasing (Bach)

Bach's own Quizzer is the original. When he says "ship it", his Claude follows `maintainer/RELEASE.md`: copy the page into `quizzer/`, update `skill/`, bump `version.json` and `BQ_VERSION` in the page, and push to `stable`. The GitHub Action then:

1. builds `dist/bachs-quizzer.zip` (`tools/build.py`) and attaches it to a GitHub Release `v<version>`, and
2. publishes the tiny npm package `bach-quizzer`. Its `latest.js` is what Quizzer pages load from jsDelivr to learn a new version is out. Artifact pages can't fetch GitHub, but they may load scripts from jsDelivr's npm mirror.

One-time setup for step 2: create an npm account, make an automation (or granular, publish) token, and add it to this repo as the Actions secret `NPM_TOKEN`. Without it, releases still build, but no popups appear.

## Layout

- `quizzer/`: the page source (full-size photos)
- `skill/`: `SKILL.md` (every kind of quiz, pilots included) and `references/` (setup, update, edits)
- `tools/build.py`: builds the zip and the npm package into `dist/`
- `.github/workflows/release.yml`: builds and publishes on push to `stable`

## Credits

Background photos are from [Unsplash](https://unsplash.com) (Unsplash License); the Tokumeien garden photo is by [@dreiimos](https://www.instagram.com/dreiimos/). *The Great Wave off Kanagawa* is Hokusai's public-domain print. KaTeX is MIT-licensed.
