"""First-run welcome demo QA for Bach's Quizzer.
usage: python3 -I quizzer/test/welcome.py quizzer/index.html [shots]   (from the repo root, or test/welcome.py index.html in a page folder)
Serves the page folder on :8768 with test/mock.js and checks:
  fresh:     empty db -> quizzes/welcome-tour + meta/welcome are written, the demo opens on its own with the welcome intro,
             every question renders (mc, math, table, short, graph, frq), reveal works, the results screen offers Delete demo,
             two clicks delete the quiz and its results doc.
  seeded:    meta/welcome already exists (demo deleted earlier) -> nothing is written, the waiting screen shows.
  library:   45 quizzes -> nothing is seeded.
Expect errors: [] in every scenario."""
import sys, json, threading, http.server, functools, os
from playwright.sync_api import sync_playwright

ARG = sys.argv[1] if len(sys.argv) > 1 else "index.html"
ROOT = os.path.dirname(os.path.abspath(ARG)) or "."
PAGE = os.path.basename(ARG)
SHOTS = len(sys.argv) > 2
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
class Q(H.func):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8768), functools.partial(Q, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
CHROME = next((c for c in ("/usr/bin/google-chrome", "/usr/bin/chromium") if os.path.exists(c)), None)
MOCK = open(os.path.join(ROOT, "test/mock.js")).read()

def page(p, init, vp, after=""):
    b = p.chromium.launch(**({"executable_path": CHROME} if CHROME else {}), args=["--no-sandbox"])
    ctx = b.new_context(viewport=vp)
    for u in ("https://fonts.googleapis.com/**", "https://fonts.gstatic.com/**", "https://cdn.jsdelivr.net/**"): ctx.route(u, lambda r: r.abort())
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
    pg.on("console", lambda m: errs.append("console: " + m.text) if m.type == "error" and "ERR_FAILED" not in m.text and "404" not in m.text else None)
    pg.add_init_script(init + MOCK + after)
    pg.goto(f"http://127.0.0.1:8768/{PAGE}")
    return b, pg, errs

def paths(pg, pre): return pg.evaluate(f"() => [...window.__docs.keys()].filter(k => k.startsWith('{pre}'))")

def fresh(p, vp, label):
    b, pg, errs = page(p, "window.__MOCK={quizzes:0};", vp)
    out = {"scenario": "fresh " + label}
    pg.wait_for_selector("#begin", timeout=8000); pg.wait_for_timeout(200)
    out["seeded"] = paths(pg, "quizzes/") == ["quizzes/welcome-tour"] and "meta/welcome" in paths(pg, "meta/")
    out["intro_says_delete"] = "delete this quiz" in pg.inner_text(".lede")
    if SHOTS: pg.screenshot(path=f"{ROOT}/test/welcome-{label}-intro.png")
    pg.click("#begin"); pg.wait_for_timeout(250)
    n = pg.evaluate("() => document.querySelectorAll('.progress .seg').length"); out["questions"] = n
    kinds = []
    for k in range(n):
        if pg.is_visible(".choice"):
            kinds.append("table" if pg.is_visible(".prompt + table, .qleft table") else ("math" if pg.query_selector(".katex") else "mc"))
            pg.keyboard.press("B" if k == 8 else "A")
        elif pg.is_visible("canvas.gcv"):
            kinds.append("graph")
            pg.click('[data-tool="line"]'); bb = pg.query_selector("canvas.gcv").bounding_box()
            pg.mouse.move(bb["x"] + bb["width"] * .2, bb["y"] + bb["height"] * .7); pg.mouse.down(); pg.mouse.move(bb["x"] + bb["width"] * .8, bb["y"] + bb["height"] * .2, steps=6); pg.mouse.up()
        elif pg.is_visible("#short.frq"):
            kinds.append("frq"); pg.fill("#short", "Recalling an answer strengthens memory more than rereading, which only feels familiar.")
        elif pg.is_visible("#short"):
            kinds.append("short"); pg.fill("#short", "Au")
        if SHOTS: pg.screenshot(path=f"{ROOT}/test/welcome-{label}-q{k + 1}.png")
        pg.click("#next"); pg.wait_for_timeout(160)
    out["kinds"] = kinds
    pg.click("#reveal"); pg.wait_for_timeout(1000)
    out["score"] = pg.inner_text(".score")
    out["results_doc"] = "results/welcome-tour" in paths(pg, "results/")
    out["delete_button"] = pg.is_visible("#delDemo")
    if SHOTS: pg.screenshot(path=f"{ROOT}/test/welcome-{label}-results.png")
    pg.click("#delDemo"); pg.wait_for_timeout(100)
    out["asks_first"] = pg.inner_text("#delDemo").strip().lower() == "yes, delete it" and pg.is_visible("#delDemo")
    pg.click("#delDemo"); pg.wait_for_timeout(600)
    out["deleted"] = paths(pg, "quizzes/") == [] and paths(pg, "results/") == []
    out["after_delete"] = "waiting" if pg.is_visible("#pasteToggle") else ("hub" if pg.is_visible(".hub") else "other")
    if SHOTS: pg.screenshot(path=f"{ROOT}/test/welcome-{label}-after.png")
    out["errors"] = errs; b.close(); return out

def seeded(p):
    # meta/welcome exists before the page boots (the demo was seeded and deleted earlier)
    b, pg, errs = page(p, "window.__MOCK={quizzes:0};", {"width": 1280, "height": 800},
                       after=";window.__docs.set('meta/welcome', {seededAt: '2026-11-01T00:00:00Z', quizId: 'welcome-tour'});")
    out = {"scenario": "seeded"}
    pg.wait_for_timeout(1500)
    out["no_writes"] = pg.evaluate("() => window.__writes.filter(w => /welcome/.test(w[1])).length") == 0
    out["waiting_screen"] = pg.is_visible("#pasteToggle")
    out["errors"] = errs; b.close(); return out

def library(p):
    b, pg, errs = page(p, "window.__MOCK={quizzes:45};", {"width": 1280, "height": 800})
    pg.wait_for_timeout(1500)
    out = {"scenario": "library", "no_seed": pg.evaluate("() => window.__writes.filter(w => /welcome/.test(w[1])).length") == 0, "errors": errs}
    b.close(); return out

if __name__ == "__main__":
    with sync_playwright() as p:
        for r in (fresh(p, {"width": 1280, "height": 800}, "desk"), fresh(p, {"width": 390, "height": 844}, "mob"), seeded(p), library(p)):
            print(json.dumps(r))
    srv.shutdown()
