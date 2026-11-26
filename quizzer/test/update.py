"""Update-dialog check for Bach's Quizzer.
usage: python3 -I test/update.py <html file name> [shots]
Serves the working folder on :8768, injects test/mock.js, fakes jsDelivr's bach-quizzer latest.js with a newer version,
and checks: dialog appears on the hub (not during a quiz), Copy/Later/Skip work, skip persists, older/equal versions stay quiet."""
import sys, json, threading, http.server, functools, os, re
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = sys.argv[1] if len(sys.argv) > 1 else "index.html"
SHOTS = len(sys.argv) > 2
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8768), functools.partial(Q, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
CHROME = next((c for c in ("/usr/bin/google-chrome", "/usr/bin/chromium") if os.path.exists(c)), None)
MOCK = open(os.path.join(ROOT, "test/mock.js")).read()
CUR = re.search(r'const BQ_VERSION = "([^"]+)"', open(os.path.join(ROOT, PAGE)).read()).group(1)
def bump(v): a = [int(x) for x in v.split(".")]; a[1] += 1; a[2] = 0; return ".".join(map(str, a))

def run(latest, vp, label, mobile=False, pre_skip=None):
    out = {"label": label, "latest": latest, "errors": []}
    with sync_playwright() as p:
        b = p.chromium.launch(**({"executable_path": CHROME} if CHROME else {}), args=["--no-sandbox"])
        ctx = b.new_context(viewport=vp, is_mobile=mobile, has_touch=mobile)
        ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin="http://127.0.0.1:8768")
        ctx.route("https://fonts.googleapis.com/**", lambda r: r.abort())
        ctx.route("https://fonts.gstatic.com/**", lambda r: r.abort())
        body = "window.__bqLatest=" + json.dumps({"version": latest, "released": "2026-12-01", "notes": ["Quizzes now ship as one zip.", "This <b>popup</b> tells you when there's an update."]}) + ";"
        ctx.route("https://cdn.jsdelivr.net/npm/bach-quizzer@latest/latest.js", lambda r: r.fulfill(status=200, content_type="application/javascript", body=body))
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: out["errors"].append("pageerror: " + str(e)))
        pg.on("console", lambda m: out["errors"].append("console: " + m.text) if m.type == "error" and "ERR_FAILED" not in m.text and "404" not in m.text else None)
        init = "window.__MOCK={quizzes:12};" + MOCK
        if pre_skip: init = f"try{{localStorage.setItem('zq:updSkip', JSON.stringify('{pre_skip}'))}}catch(e){{}};" + init
        pg.add_init_script(init)
        pg.goto(f"http://127.0.0.1:8768/{PAGE}")
        pg.wait_for_selector("#qlib, .hub", timeout=8000)
        pg.wait_for_timeout(2200)   # check runs 1.5s after load
        out["shown_in_quiz"] = pg.is_visible("#upd.on")
        if pg.is_visible("#qlib"):
            pg.click("#qlib"); pg.wait_for_timeout(400)
        out["shown_on_hub"] = pg.is_visible("#upd.on")
        if out["shown_on_hub"]:
            out["notes_escaped"] = "<b>" not in pg.inner_html(".upd-notes") or "&lt;b&gt;" in pg.inner_html(".upd-notes")
            if SHOTS: pg.screenshot(path=f"{ROOT}/test/{label}-update.png")
            pg.click("#updCopy"); pg.wait_for_timeout(200)
            try: out["clipboard"] = pg.evaluate("navigator.clipboard.readText()")
            except Exception as e: out["clipboard"] = "ERR " + str(e)[:80]
            pg.keyboard.press("Escape"); pg.wait_for_timeout(100)
            out["esc_closes"] = not pg.is_visible("#upd.on")
            # re-render the hub: Later means not again this load
            pg.click('.hub [data-f="all"]') if pg.is_visible('.hub [data-f="all"]') else None
            pg.wait_for_timeout(200)
            out["stays_closed"] = not pg.is_visible("#upd.on")
            # skip persists across reloads
            pg.reload(); pg.wait_for_selector("#qlib, .hub", timeout=8000); pg.wait_for_timeout(2200)
            if pg.is_visible("#qlib"): pg.click("#qlib"); pg.wait_for_timeout(400)
            if pg.is_visible("#upd.on"):
                pg.click("#updSkip"); pg.wait_for_timeout(100)
                pg.reload(); pg.wait_for_selector("#qlib, .hub", timeout=8000); pg.wait_for_timeout(2200)
                if pg.is_visible("#qlib"): pg.click("#qlib"); pg.wait_for_timeout(400)
                out["skip_persists"] = not pg.is_visible("#upd.on")
        b.close()
    return out

res = [
    run(bump(CUR), {"width": 1280, "height": 800}, "desktop"),
    run(bump(CUR), {"width": 390, "height": 844}, "phone", mobile=True),
    run(CUR, {"width": 1280, "height": 800}, "same-version"),
    run("0.9.0", {"width": 1280, "height": 800}, "older"),
    run(bump(CUR), {"width": 1280, "height": 800}, "pre-skipped", pre_skip=bump(CUR)),
]
print(json.dumps(res, indent=1))
