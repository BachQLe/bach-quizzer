"""QA + perf harness for Bach's Quizzer.
usage: python3 -I test/qa.py <html file name> [shots]
Prints per-viewport JSON: errors (must be []), card_survives_clicks (must be true), writes after 3 rubric ticks (3),
grades_applied (2 notes, 2 ticks), timings in ms. Screenshots land in test/*.png with "shots".
Serves the working folder on :8766, injects test/mock.js, walks hub -> stats -> quiz -> results."""
import sys, json, time, threading, http.server, functools, os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = sys.argv[1] if len(sys.argv) > 1 else "index.html"
SHOTS = len(sys.argv) > 2
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
class Q(H.func):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8766), functools.partial(Q, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
CHROME = next((c for c in ("/usr/bin/google-chrome", "/usr/bin/chromium") if os.path.exists(c)), None)   # else Playwright's own (python3 -m playwright install chromium)
MOCK = open(os.path.join(ROOT, "test/mock.js")).read()
TIMED = """(sel) => { const el = document.querySelector(sel); if (!el) return -1; const t = performance.now(); el.click(); return +(performance.now() - t).toFixed(1); }"""

def run(vp, label, mobile=False):
    out = {"label": label, "errors": []}
    with sync_playwright() as p:
        b = p.chromium.launch(**({"executable_path": CHROME} if CHROME else {}), args=["--no-sandbox"])
        ctx = b.new_context(viewport=vp, is_mobile=mobile, has_touch=mobile, reduced_motion=("reduce" if label.endswith("rm") else "no-preference"))
        ctx.route("https://fonts.googleapis.com/**", lambda r: r.abort())
        ctx.route("https://fonts.gstatic.com/**", lambda r: r.abort())
        ctx.route("https://cdn.jsdelivr.net/**", lambda r: r.abort())   # update check: tested in test/update.py
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: out["errors"].append("pageerror: " + str(e) + " @ " + (e.stack or "")[:400]))
        pg.on("console", lambda m: out["errors"].append("console: " + m.text) if m.type == "error" and "ERR_FAILED" not in m.text and "404" not in m.text else None)
        pg.add_init_script("window.__MOCK={quizzes:45};" + MOCK)
        t0 = time.time()
        pg.goto(f"http://127.0.0.1:8766/{PAGE}")
        pg.wait_for_selector("#qlib, .hub", timeout=8000)
        pg.wait_for_timeout(300)
        out["boot_ms"] = round((time.time() - t0) * 1000)
        if pg.is_visible("#qlib"):
            pg.click("#qlib"); pg.wait_for_timeout(250)
        out["hub_tab_ms"] = [pg.evaluate(TIMED, '.hub [data-f="econ-3010"]'), pg.evaluate(TIMED, '.hub [data-f="all"]'), pg.evaluate(TIMED, '.hub [data-f="psyc-2005"]')]
        if SHOTS: pg.screenshot(path=f"{ROOT}/test/{label}-hub.png")
        pg.click('[data-view="stats"]'); pg.wait_for_timeout(700)
        out["stats_tab_ms"] = [pg.evaluate(TIMED, '.hub [data-f="econ-3010"]'), pg.evaluate(TIMED, '.hub [data-f="all"]')]
        if SHOTS: pg.screenshot(path=f"{ROOT}/test/{label}-stats.png", full_page=False)
        pg.click('[data-view="lib"]'); pg.wait_for_timeout(400)
        # open the newest ECON quiz with math + FRQ (t0 has graph + frq)
        pg.evaluate("""() => { const b = [...document.querySelectorAll('[data-open]')].find(x => /Mock quiz 0 /.test(x.textContent)); b && b.click(); }""")
        pg.wait_for_timeout(300)
        if pg.is_visible("#begin"): pg.click("#begin"); pg.wait_for_timeout(250)
        card0 = pg.evaluate("() => { window.__card = document.querySelector('.card.q'); return !!window.__card; }")
        n = pg.evaluate("() => document.querySelectorAll('.progress .seg').length")
        same = True; nexts = []
        for k in range(n):
            pg.evaluate("() => { window.__card = document.querySelector('.card.q'); }")
            if pg.is_visible(".choice"):
                pg.click(".opt:nth-child(2) .choice"); pg.click(".opt:nth-child(3) .xbtn"); pg.click("#flag")
                same = same and pg.evaluate("() => window.__card === document.querySelector('.card.q')")
            elif pg.is_visible("#short"):
                pg.fill("#short", "indifference curve")
                same = same and pg.evaluate("() => window.__card === document.querySelector('.card.q')")
            elif pg.is_visible("canvas"):
                c = pg.query_selector("canvas.gpad-cv, .gpad canvas")
                if c:
                    bb = c.bounding_box(); pg.mouse.move(bb["x"] + 60, bb["y"] + 60); pg.mouse.down(); pg.mouse.move(bb["x"] + 160, bb["y"] + 120, steps=6); pg.mouse.up()
            if SHOTS and k in (1, 5): pg.screenshot(path=f"{ROOT}/test/{label}-q{k}.png")
            nexts.append(pg.evaluate(TIMED, "#next")); pg.wait_for_timeout(140)
        out["card_survives_clicks"] = same
        out["next_ms_max"] = max(nexts) if nexts else None
        out["reveal_ms"] = pg.evaluate(TIMED, "#reveal"); pg.wait_for_timeout(900)
        if SHOTS: pg.screenshot(path=f"{ROOT}/test/{label}-results.png")
        w0 = pg.evaluate("() => window.__writes.length")
        ticks = []
        for j in range(3):
            ticks.append(pg.evaluate("(j) => { const el = document.querySelectorAll('[data-rub]')[j]; if (!el) return -1; const t = performance.now(); el.click(); return +(performance.now() - t).toFixed(1); }", j))
        pg.wait_for_timeout(1500)
        out["rub_tick_ms"] = ticks
        out["writes_after_3_ticks"] = pg.evaluate(f"() => window.__writes.slice({w0}).map(w => w[0] + ' ' + w[1])")
        res = pg.evaluate("() => { const r = [...window.__docs].filter(([p]) => p.startsWith('results/econ3010-t0')); return r.length ? r[0][1] : null; }")
        out["result_doc_ok"] = bool(res) and any(i.get("type") == "frq" and any(x.get("met") for x in i.get("rubric", [])) for i in res["items"])
        out["mark_count"] = pg.evaluate("() => document.querySelectorAll('.res').length")
        out["self_click_ms"] = pg.evaluate(TIMED, '[data-self][data-v="1"]')
        # Claude grades the written answers: write grades/<id> the way bachs-quizzer does
        pg.evaluate("""async () => { const db = await window.claude.use('db'); const id = [...window.__docs.keys()].find(p => p.startsWith('results/econ3010-t0')).slice(8);
          const r = window.__docs.get('results/' + id), fr = r.items.find(i => i.type === 'frq'), sa = r.items.find(i => /Name the curve/.test(i.prompt));
          await db.doc('grades/' + id).set({ quizId: id, finishedAt: r.finishedAt, gradedAt: new Date().toISOString(), items: [
            { n: fr.n, verdict: 'partly', met: [true, true, false], note: 'Named the mechanism; never applied it to **coffee**.' },
            { n: sa.n, verdict: 'got', note: 'Right term.' } ] }); }""")
        pg.wait_for_timeout(1600)
        out["grades_applied"] = pg.evaluate("() => ({ notes: document.querySelectorAll('.cnote').length, ticked: document.querySelectorAll('[data-rub]:checked').length })")
        res = pg.evaluate("() => { const r = [...window.__docs].filter(([p]) => p.startsWith('results/econ3010-t0')); return r[0][1]; }")
        out["grades_in_result_doc"] = [(i["n"], i["correct"], [x["met"] for x in i.get("rubric", [])]) for i in res["items"] if i.get("type") == "frq" or "Name the curve" in i["prompt"]]
        if SHOTS: pg.evaluate("() => document.querySelector('.cnote') && document.querySelector('.cnote').scrollIntoView({block:'center'})"); pg.wait_for_timeout(100); pg.screenshot(path=f"{ROOT}/test/{label}-graded.png")
        # drop question 1 from the right-click menu; the result doc should list it under dropped after the debounce
        pg.evaluate("() => { const a = document.querySelector('.res[data-k=\"0\"] .res-top'); a.dispatchEvent(new MouseEvent('contextmenu', {bubbles: true, clientX: 300, clientY: 300})); }")
        pg.wait_for_timeout(100); pg.click('.cmenu [data-a="drop"]'); pg.wait_for_timeout(1300)
        res = pg.evaluate("() => [...window.__docs].filter(([p]) => p.startsWith('results/econ3010-t0'))[0][1]")
        out["drop_ok"] = res.get("dropped") == [1] and all(i["n"] != 1 for i in res["items"]) and pg.is_visible(".res.dropped")
        pg.click("#qlib"); pg.wait_for_timeout(300)
        out["back_to_hub"] = pg.is_visible(".hub")
        pg.set_viewport_size({"width": vp["width"], "height": vp["height"] - 40}); pg.wait_for_timeout(200)   # resize after leaving results: old graph canvases must not redraw
        pg.click('[data-view="stats"]'); pg.wait_for_timeout(500)
        pg.evaluate("() => { const b = [...document.querySelectorAll('.hub [data-f=\"econ-3010\"]')].find(x => x.offsetParent); b && b.click(); }"); pg.wait_for_timeout(900)
        out["pred"] = pg.evaluate("() => (document.querySelector('.pred') || {}).textContent")
        if SHOTS: pg.screenshot(path=f"{ROOT}/test/{label}-stats-econ.png")
        b.close()
    return out

if __name__ == "__main__":
    for vp, lab, mob in [({"width": 1280, "height": 800}, "desk", False), ({"width": 390, "height": 844}, "mob", True), ({"width": 1280, "height": 800}, "deskrm", False)]:
        print(json.dumps(run(vp, lab, mob), indent=1))
    srv.shutdown()
