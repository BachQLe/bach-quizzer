import sys, json, threading, http.server, functools, os
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8768), functools.partial(type("Q", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *a: None}), directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(os.path.join(ROOT, "test/mock.js")).read()
QS = json.load(open(os.path.join(ROOT, "test/texts-quiz.json")))
QUIZ = {"title": "Texts test", "subject": "ECON 3010", "createdAt": "2099-01-01T00:00:00.000Z", "questions": QS}
out = {"errors": []}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    pg = b.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=2).new_page()
    pg.route("https://fonts.googleapis.com/**", lambda r: r.abort()); pg.route("https://fonts.gstatic.com/**", lambda r: r.abort())
    pg.on("pageerror", lambda e: out["errors"].append("pageerror: " + str(e)))
    pg.on("console", lambda m: out["errors"].append("console: " + m.text) if m.type == "error" and "ERR_FAILED" not in m.text and "404" not in m.text else None)
    pg.add_init_script("window.__MOCK={quizzes:3};" + MOCK + ";window.__docs.set('quizzes/texts-test'," + json.dumps(QUIZ) + ");")
    pg.goto("http://127.0.0.1:8768/index.html"); pg.wait_for_timeout(900)
    if pg.is_visible("#qlib"): pg.click("#qlib"); pg.wait_for_timeout(300)
    pg.evaluate("() => { const b = [...document.querySelectorAll('[data-open]')].find(x => /Texts test/.test(x.textContent)); b && b.click(); }"); pg.wait_for_timeout(300)
    if pg.is_visible("#begin"): pg.click("#begin"); pg.wait_for_timeout(300)
    tools = lambda: pg.evaluate("() => [...document.querySelectorAll('.gtools [data-tool]')].map(b => b.dataset.tool)")
    face = lambda: pg.evaluate("() => (document.querySelector('[data-tool=label] .gl-l')||{}).textContent")
    state = lambda: pg.evaluate("() => { const k = Object.keys(localStorage).find(k => /zq:state:/.test(k) && /texts/.test(k)); return k ? JSON.parse(localStorage[k]).answers : null; }")
    out["q1_tools"] = tools(); out["face_start"] = face()
    cv = pg.locator("canvas.gcv"); bb = cv.bounding_box()
    xr, yr = 16, 64
    def at(x, y):
        pw, ph = bb["width"] - 54, bb["height"] - 50
        return (bb["x"] + 40 + x / xr * pw, bb["y"] + 18 + (1 - y / yr) * ph)
    # dot tool: B and C points, then the text tool for B, C, SE, IE (no points)
    pg.click("[data-tool=dot]"); pg.mouse.click(*at(4, 16)); pg.mouse.click(*at(8, 32))
    pg.click("[data-tool=arrow]"); pg.mouse.move(*at(8, 8)); pg.mouse.down(); pg.mouse.move(*at(4, 16), steps=5); pg.mouse.up()
    pg.click("[data-tool=label]"); out["hint"] = pg.inner_text(".ghint")
    for pt in [(3.1, 16), (8.9, 34.5), (6.9, 14.5), (5, 24.5)]:
        out.setdefault("faces", []).append(face()); pg.mouse.click(*at(*pt))
    a = state()[0]["s"]
    out["marks"] = [(m["t"], m.get("l"), m.get("ar")) for m in a]
    out["text_marks_have_no_dot"] = all(m["t"] == "text" for m in a if m.get("l"))
    out["face_after_all"] = face()
    # re-place B elsewhere: moves it, still one B
    pg.click("[data-tool=label]")  # cycle
    pg.screenshot(path=ROOT + "/test/texts-q1.png")
    # eraser hits text anywhere on the box
    n0 = len(state()[0]["s"])
    pg.click("[data-tool=erase]"); px, py = at(8.9, 34.5); pg.mouse.click(px + 6, py + 3)
    out["erased_text"] = n0 - len(state()[0]["s"])
    # skip to results
    for _ in range(8):
        if pg.is_visible("#next"): pg.evaluate("() => document.querySelector('#next').click()"); pg.wait_for_timeout(200)
    pg.evaluate("() => document.querySelector('#reveal') && document.querySelector('#reveal').click()"); pg.wait_for_timeout(1200)
    n = pg.locator(".gres").count(); out["gres"] = n
    for i in range(n):
        g = pg.locator(".gres").nth(i)
        g.scroll_into_view_if_needed()
        g.locator("[data-gm=key]").click(); pg.wait_for_timeout(200)
        g.locator("canvas.gcv").screenshot(path=ROOT + f"/test/texts-key{i}.png")
    pg.locator(".gres").nth(0).locator("[data-gm=over]").click(); pg.wait_for_timeout(200)
    pg.locator(".gres").nth(0).locator("canvas.gcv").screenshot(path=ROOT + "/test/texts-over0.png")
    out["summary"] = pg.evaluate("() => document.body.innerText.match(/Drawn graph[^\\n]*/g)")
    b.close()
print(json.dumps(out, indent=1))
