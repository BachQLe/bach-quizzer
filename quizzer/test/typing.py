import sys, json, threading, http.server, functools, os
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8769), functools.partial(type("Q", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *a: None}), directory=ROOT))
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
    pg.goto("http://127.0.0.1:8769/index.html"); pg.wait_for_timeout(900)
    if pg.is_visible("#qlib"): pg.click("#qlib"); pg.wait_for_timeout(300)
    pg.evaluate("() => { const b = [...document.querySelectorAll('[data-open]')].find(x => /Texts test/.test(x.textContent)); b && b.click(); }"); pg.wait_for_timeout(300)
    if pg.is_visible("#begin"): pg.click("#begin"); pg.wait_for_timeout(300)

    tools = lambda: pg.evaluate("() => [...document.querySelectorAll('.gtools [data-tool]')].map(b => b.dataset.tool)")
    state = lambda: pg.evaluate("() => { const k = Object.keys(localStorage).find(k => /zq:state:/.test(k) && /texts/.test(k)); return k ? JSON.parse(localStorage[k]).answers : null; }")
    out["tools_q1"] = tools()
    cv = pg.locator("canvas.gcv"); bb = cv.bounding_box()
    pt = lambda fx, fy: (bb["x"] + bb["width"]*fx, bb["y"] + bb["height"]*fy)
    pg.click("[data-tool=label]"); out["hint"] = pg.inner_text(".ghint")
    pg.mouse.click(*pt(.3,.4)); pg.wait_for_timeout(200)
    out["box_open"] = pg.locator(".gtx").count(); out["box_focused"] = pg.evaluate("() => document.activeElement && document.activeElement.className")
    pg.keyboard.type("Supply shifts right, a b c 1 2 3 q"); pg.keyboard.press("Enter"); pg.wait_for_timeout(200)
    out["after_enter_box"] = pg.locator(".gtx").count()
    # second label, commit by clicking elsewhere
    pg.evaluate("() => { window.__log=[]; new MutationObserver(m => m.forEach(r => { r.addedNodes.forEach(n => n.className==='gtx' && __log.push('add')); r.removedNodes.forEach(n => (n.className==='gtx' || (n.querySelector && n.querySelector('.gtx'))) && __log.push('remove ' + (n.className||n.tagName))); })).observe(document.body,{childList:true,subtree:true}); }")
    pg.mouse.click(*pt(.7,.7)); pg.wait_for_timeout(200); pg.keyboard.type("P*"); pg.mouse.click(*pt(.5,.15)); pg.wait_for_timeout(100)
    out["box_after_blur_click_100ms"] = pg.locator(".gtx").count()
    pg.wait_for_timeout(300)
    out["box_after_blur_click"] = pg.locator(".gtx").count()
    out["log"] = pg.evaluate("() => window.__log")
    out["focus_now"] = pg.evaluate("() => document.activeElement && (document.activeElement.className || document.activeElement.tagName)")
    pg.keyboard.type("Eq"); pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
    out["still_in_quiz_after_escape"] = pg.is_visible(".gpad")
    a = state()[0]["s"]; out["marks"] = [(m["t"], m.get("l")) for m in a]
    # edit the first label
    pg.mouse.click(*pt(.3,.4)); pg.wait_for_timeout(200)
    out["edit_prefill"] = pg.evaluate("() => document.querySelector('.gtx') && document.querySelector('.gtx').value")
    pg.keyboard.press("Control+a"); pg.keyboard.type("Edited"); pg.keyboard.press("Enter"); pg.wait_for_timeout(200)
    # delete second by emptying
    pg.mouse.click(*pt(.7,.7)); pg.wait_for_timeout(200); pg.keyboard.press("Control+a"); pg.keyboard.press("Backspace"); pg.keyboard.press("Enter"); pg.wait_for_timeout(200)
    out["marks_after"] = [(m["t"], m.get("l")) for m in state()[0]["s"]]
    out["undo_not_triggered_by_ctrlz_in_box"] = True
    pg.screenshot(path=ROOT + "/test/typing.png")
    b.close()
print(json.dumps(out, indent=1))
