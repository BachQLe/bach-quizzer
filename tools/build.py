"""Build the release bundle.
usage: python3 tools/build.py            (from the repo root)

dist/bachs-quizzer/       the skill folder: SKILL.md, references/, version.json, page/ (the Quizzer page)
dist/bachs-quizzer.zip    what people download and upload in Claude (Settings → Capabilities → Skills)
dist/npm/                 the tiny npm package "bach-quizzer" whose latest.js tells every Quizzer page a new version is out

Background photos are scaled down to 1920px wide for the zip so the skill stays well under upload limits.
Bach's own Quizzer keeps the full-size originals from quizzer/img/."""
import json, os, re, shutil, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
SKILL = os.path.join(DIST, "bachs-quizzer")
MAX_W, QUALITY = 1920, 80
SKIP = re.compile(r"(\.png$|__pycache__|\.DS_Store$|^shots/)")

def main():
    ver = json.load(open(os.path.join(ROOT, "version.json")))
    page_ver = re.search(r'const BQ_VERSION = "([^"]+)"', open(os.path.join(ROOT, "quizzer/index.html")).read())
    if not page_ver or page_ver.group(1) != ver["version"]:
        sys.exit(f"BQ_VERSION in quizzer/index.html ({page_ver and page_ver.group(1)}) must match version.json ({ver['version']})")

    shutil.rmtree(DIST, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, "skill"), SKILL)
    shutil.copy(os.path.join(ROOT, "version.json"), os.path.join(SKILL, "version.json"))
    src = os.path.join(ROOT, "quizzer")
    for dp, _, fs in os.walk(src):
        for f in fs:
            rel = os.path.relpath(os.path.join(dp, f), src)
            if SKIP.search(rel): continue
            out = os.path.join(SKILL, "page", rel)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            if rel.startswith("img/") and f.endswith(".webp"): shrink(os.path.join(dp, f), out)
            else: shutil.copy(os.path.join(dp, f), out)

    zpath = os.path.join(DIST, "bachs-quizzer.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, _, fs in os.walk(SKILL):
            for f in sorted(fs):
                full = os.path.join(dp, f)
                z.write(full, os.path.relpath(full, DIST))   # top level of the zip is bachs-quizzer/

    npm = os.path.join(DIST, "npm"); os.makedirs(npm)
    latest = {"version": ver["version"], "released": ver.get("released", ""), "notes": ver.get("notes", [])}
    open(os.path.join(npm, "latest.js"), "w").write("window.__bqLatest=" + json.dumps(latest, ensure_ascii=False).replace("<", "\\u003c") + ";\n")
    json.dump({"name": "bach-quizzer", "version": ver["version"], "description": "Release marker for Bach's Quizzer: latest.js tells Quizzer pages a new version is out.",
               "files": ["latest.js"], "license": "MIT", "repository": {"type": "git", "url": "https://github.com/BachQLe/bach-quizzer"}},
              open(os.path.join(npm, "package.json"), "w"), indent=2)
    open(os.path.join(npm, "README.md"), "w").write("Release marker for [Bach's Quizzer](https://github.com/BachQLe/bach-quizzer). `latest.js` sets `window.__bqLatest` to the latest version and its notes.\n")
    print(f"built {ver['version']}: {zpath} ({os.path.getsize(zpath)/1e6:.1f} MB)")

def shrink(src, out):
    try:
        from PIL import Image
    except ImportError:
        shutil.copy(src, out); return
    im = Image.open(src)
    if im.width <= MAX_W: shutil.copy(src, out); return
    im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    im.save(out, "WEBP", quality=QUALITY, method=6)
    if os.path.getsize(out) >= os.path.getsize(src): shutil.copy(src, out)

if __name__ == "__main__":
    main()
