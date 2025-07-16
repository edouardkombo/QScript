#!/usr/bin/env python3
"""
QScript Handler v1
"""

import re
import json
import asyncio
import logging
import time
import argparse
import http.client
from difflib import SequenceMatcher
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright, Page, BrowserContext
from pathlib import Path

__version__ = "v1"

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

SUPPORTED_COMMANDS = [
    "Goto", "Click", "Fill", "FillAuto", "WaitFor", "ScrollTo",
    "Assert", "AssertCookie", "Viewport", "Retry", "SetVar",
    "WaitForPopup", "SwitchToPopup", "ClosePopup",
    "SwitchToIFrame", "ReturnFromIFrame",
    "SaveSession", "RestoreSession"
]

DEVICE_VIEWPORTS = {
    "desktop": {"viewport": {"width": 1440, "height": 900}},
    "mobile":  {"viewport": {"width": 390,  "height": 844}, "is_mobile": True},
    "bot":     {"user_agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"}
}

HTTP_REASONS = http.client.responses

# --- Utilities ---
def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

async def wait_after_action(page: Page):
    for _ in range(2):
        try:
            await page.wait_for_load_state("networkidle", timeout=7000)
        except:
            pass
    await asyncio.sleep(0.3)

async def wait_for_main_content(page: Page, selector: str = "body"):
    try:
        await page.wait_for_selector(selector, timeout=7000)
        await page.wait_for_load_state("networkidle", timeout=7000)
        await asyncio.sleep(0.5)
    except:
        pass

async def extract_visible_text(page: Page, selector: str) -> str:
    return await page.locator(selector).evaluate(r'''
el => {
    function visibleText(node) {
        if (!node) return '';
        if (node.nodeType === Node.TEXT_NODE) {
            const style = window.getComputedStyle(node.parentElement);
            if (style.visibility==='hidden' || style.display==='none') return '';
            return node.textContent.trim();
        }
        const st = window.getComputedStyle(node);
        if (st.visibility==='hidden' || st.display==='none') return '';
        return Array.from(node.childNodes).map(visibleText).join(' ');
    }
    return visibleText(el);
}
''')

async def save_snapshot(page: Page, prefix: str):
    html = await page.content()
    Path(f"{prefix}.html").write_text(html)
    await page.screenshot(path=f"{prefix}.png")
    return f"{prefix}.html", f"{prefix}.png"

def get_redirect_chain(response) -> list:
    chain, req = [], response.request
    while getattr(req, 'redirected_from', None):
        prev = req.redirected_from
        chain.append(prev.url + " â†’ " + req.url)
        req = prev
    return list(reversed(chain))

# --- Assertion Handlers ---
async def assert_status(page: Page, expr: str):
    m = re.match(r'page\.status\s+is\s+(\d+)', expr)
    if m:
        if not hasattr(page, '_last_response') or page._last_response is None:
            raise AssertionError("No prior Goto; cannot check page.status")
        exp, got = int(m.group(1)), page._last_response.status
        if got != exp:
            raise AssertionError(f"Expected status {exp}, got {got}")
        return {}
    return None

async def assert_url(page: Page, expr: str):
    m = re.match(r'page\.url\s+is\s+"(.+?)"', expr)
    if m:
        exp, got = m.group(1), page.url
        if got != exp:
            raise AssertionError(f"Expected URL {exp}, got {got}")
        return {}
    return None

async def assert_exists(page: Page, expr: str):
    m = re.match(r'element\s+"(.+?)"\s+exists', expr)
    if m:
        sel = m.group(1)
        cnt = await page.locator(sel).count()
        if cnt == 0:
            raise AssertionError(f"{sel} not found")
        return {"children_count": cnt}
    return None

async def assert_visible(page: Page, expr: str):
    m = re.match(r'element\s+"(.+?)"\s+visible', expr)
    if m:
        sel = m.group(1)
        locator = page.locator(sel)
        try:
            # strict mode: exactly one
            if await locator.count() == 1:
                if not await locator.is_visible():
                    raise AssertionError(f"{sel} not visible")
                return {"matches": 1, "visible": 1}
        except Exception:
            # strictâ€‘mode error or other: fall back
            pass

        # Fallback: many or zero matches
        total = await locator.count()
        if total == 0:
            raise AssertionError(f"{sel} not found")

        # Count how many of the matched elements are visible
        visible_count = 0
        for i in range(total):
            if await locator.nth(i).is_visible():
                visible_count += 1
        if visible_count == 0:
            raise AssertionError(f"{sel} matched {total} elements, none visible")

        return {"matches": total, "visible": visible_count}    
    return None

async def assert_similar(page: Page, expr: str):
    m = re.match(
        r'element\s+"(.+?)"\s+similar to\s+"(.+?)"\s*<\s*([\d.]+)',
        expr
    )
    if m:
        sel, phrase, thr = m.group(1), m.group(2), float(m.group(3))

        # Specialâ€‘case <meta> tags: compare their content attribute
        if sel.lower().startswith("head meta"):
            try:
                attr = await page.locator(sel).get_attribute("content")
            except PlaywrightTimeoutError:
                raise AssertionError(f"Could not read attribute 'content' from {sel}: timed out")
            score = similar(phrase.lower(), (attr or "").lower())
            if score >= thr:
                raise AssertionError(f"Similarity {score:.2f} â‰¥ {thr}")
            return {"similarity": score, "attribute": attr}

        # Fallback: extract visible text, handling timeouts
        try:
            txt = await extract_visible_text(page, sel)
        except PlaywrightTimeoutError:
            raise AssertionError(f"Could not extract visible text from selector {sel}: timed out")

        score = similar(phrase.lower(), txt.lower())
        if score >= thr:
            raise AssertionError(f"Similarity {score:.2f} â‰¥ {thr}")
        return {"similarity": score, "text_snippet": txt[:50]}

    return None

async def assert_children(page: Page, expr: str):
    m = re.match(r'children of\s+"(.+?)"\s+count\s*(>=|<=|>|<|==)\s*(\d+)', expr)
    if m:
        sel, op, val = m.group(1), m.group(2), int(m.group(3))
        cnt = await page.locator(f"{sel} > *").count()
        ops = {'>':cnt>val,'<':cnt<val,'>=':cnt>=val,'<=':cnt<=val,'==':cnt==val}
        if not ops[op]:
            raise AssertionError(f"Children count {cnt} {op} {val} failed")
        return {"children_count": cnt}
    return None

async def assert_cls(page: Page, expr: str):
    m = re.match(r'CLS\s*<\s*([\d.]+)', expr)
    if m:
        thr = float(m.group(1))
        cls = await page.evaluate(
            "() => performance.getEntriesByType('layout-shift')"
            ".reduce((sum,e)=>sum+e.value,0)"
        )
        if cls >= thr:
            raise AssertionError(f"CLS {cls} â‰¥ {thr}")
        return {"cls": cls}
    return None

async def assert_attribute_regex(page: Page, expr: str):
    #Handles: Assert attribute <selector>@<attr> matches /regex/
    #Example: Assert attribute link[rel='canonical']@href matches /^https://github.com\/?$/
    m = re.match(r'attribute\s+(.+?@.+?)\s+matches\s+/(.+)/', expr)
    if m:
        elem_attr, regex = m.group(1), m.group(2)
        sel, attr = elem_attr.split('@', 1)
        try:
            val = await page.locator(sel).get_attribute(attr)
        except PlaywrightTimeoutError:
            raise AssertionError(f"Could not read attribute '{attr}' from {sel}: timed out")
        if not re.match(regex, val or ''):
            raise AssertionError(f"{sel}@{attr}='{val}' does not match /{regex}/")
        return {"attribute": val}
    return None

async def assert_regex_each(page: Page, expr: str):
    m = re.match(r'each attribute (\w+) in elements "([^"]+)" matches /(.+)/', expr)
    if m:
        attr, sel, regex = m.group(1), m.group(2), m.group(3)

        # Expand <BASE_URL> placeholder if present
        # `page._vars` was populated by your SetVar logic; fallback to empty if missing
        base = getattr(page, "_vars", {}).get("BASE_URL", None)
        if base:
            # escape dots etc
            esc = re.escape(base)
            raw_regex = raw_regex.replace("<BASE_URL>", esc)

        els = page.locator(sel)
        seen = set()
        for i in range(await els.count()):
            val = await els.nth(i).get_attribute(attr)
            if not re.match(regex, val or ''):
                raise AssertionError(f"{sel}[{i}]@{attr}='{val}' fails /{regex}/")
            if val in seen:
                raise AssertionError(f"Duplicate {attr}='{val}'")
            seen.add(val)
        return {"count": len(seen)}
    return None

async def assert_canonical(page: Page, expr: str):
    if expr.strip() == 'canonical href equals page.url':
        link = page.locator("link[rel='canonical']").first
        href = await link.get_attribute("href")
        if href != page.url:
            raise AssertionError(f"canonical='{href}' != url='{page.url}'")
        return {"canonical": href}
    return None

async def assert_language(page: Page, expr: str):
    m = re.match(r'element\s+"(.+?)"\s+language\s+equals\s+html@lang', expr)
    if m:
        sel = m.group(1)
        html_lang = await page.locator("html").get_attribute("lang")
        elem_lang = await page.locator(sel).get_attribute("lang")
        if elem_lang != html_lang:
            raise AssertionError(f"{sel}@lang='{elem_lang}' != html@lang='{html_lang}'")
        return {"element_lang": elem_lang, "html_lang": html_lang}
    return None

async def assert_no_duplicates(page: Page, expr: str):
    m = re.match(r'no duplicates in attribute\s+(\w+)\s+of elements\s+"([^"]+)"', expr)
    if m:
        attr, sel = m.group(1), m.group(2)
        els = page.locator(sel)
        seen = set()
        for i in range(await els.count()):
            val = await els.nth(i).get_attribute(attr)
            if val in seen:
                raise AssertionError(f"Duplicate {attr}='{val}' in {sel}[{i}]")
            seen.add(val)
        return {"unique_count": len(seen)}
    return None

async def handle_assert(page: Page, expr: str, save_snapshots: bool):
    step_line = f"Assert {expr}"
    handlers = [
        assert_status, assert_url, assert_exists, assert_visible,
        assert_similar, assert_children, assert_cls,
        assert_attribute_regex, assert_regex_each, assert_canonical,
        assert_language, assert_no_duplicates
    ]
    for h in handlers:
        try:
            res = await h(page, expr)
        except AssertionError as e:
            error_msg = str(e)
            if save_snapshots:
                prefix = f"snapshot_{int(time.time()*1000)}"
                html_file, img_file = await save_snapshot(page, prefix)
                return {
                    "step": step_line, "status": "FAIL", "error": error_msg,
                    "snapshot_html": html_file, "snapshot_image": img_file
                }
            return {"step": step_line, "status": "FAIL", "error": error_msg}
        if res is not None:
            return {"step": step_line, "status": "PASS", "error": None, **res}
    return {"step": step_line, "status": "SYNTAX_ERROR", "error": f"Unknown assertion: {expr}"}

# --- DSL Handlers ---
async def handle_goto(page: Page, line: str) -> dict:
    #"""
    #Goto "URL"
    #Returns PASS/FAIL and includes:
    #  - HTTP status and headers
    #  - PerformanceNavigationTiming metrics:
    #      startTime, domainLookupTime, connectTime, requestTime,
    #      responseTime, domLoadTime, totalTime
    #"""
    m = re.match(r'Goto\s+"(.+?)"', line)
    if not m:
        return {"step": line, "status": "SYNTAX_ERROR", "error": "Malformed Goto"}
    url = m.group(1)

    # 1) Navigate
    try:
        response = await page.goto(url, wait_until="networkidle", timeout=60000)
    except Exception as e:
        return {"step": line, "status": "FAIL", "error": str(e)}

    # 2) Basic status info
    status_code = response.status
    status_text = HTTP_REASONS.get(status_code, "")
    headers = response.headers
    page._last_response = response

    # 3) Extract navigation timing
    perf = await page.evaluate("""() => {
        const [entry] = performance.getEntriesByType('navigation');
        return {
          startTime: entry.startTime,
          redirectCount: entry.redirectCount,
          domainLookupTime: entry.domainLookupEnd - entry.domainLookupStart,
          connectTime: entry.connectEnd - entry.connectStart,
          requestTime: entry.responseStart - entry.requestStart,
          responseTime: entry.responseEnd - entry.responseStart,
          domContentLoadedTime: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
          domCompleteTime: entry.domComplete - entry.domLoading,
          totalTime: entry.duration
        };
    }""")

    # 4) Build result object
    result = {
        "step": line,
        "status": "PASS" if status_code < 400 else "FAIL",
        "error": None if status_code < 400 else f"HTTP {status_code} {status_text}",
        "status_code": status_code,
        "status_text": status_text,
        "redirect_chain": get_redirect_chain(response),
        "headers": headers,
        "page_title": await page.title(),
        "timing": perf
    }

    return result


async def handle_click(page: Page, line: str) -> dict:
    m = re.match(r'Click\s+"(.+?)"', line)
    if not m:
        return {"step": line, "status": "SYNTAX_ERROR", "error": "Malformed Click"}
    sel = m.group(1)
    try:
        await page.click(sel)
        await wait_after_action(page)
        return {"step": line, "status": "PASS", "error": None}
    except Exception as e:
        return {"step": line, "status": "FAIL", "error": str(e)}

async def handle_fill(page: Page, line: str) -> dict:
    m = re.match(r'Fill\s+"(.+?)"\s+with\s+"(.+?)"', line)
    if not m:
        return {"step": line, "status": "SYNTAX_ERROR", "error": "Malformed Fill"}
    sel, txt = m.group(1), m.group(2)
    try:
        await page.fill(sel, txt)
        await wait_after_action(page)
        return {"step": line, "status": "PASS", "error": None}
    except Exception as e:
        return {"step": line, "status": "FAIL", "error": str(e)}

async def handle_fillauto(page: Page, line: str) -> dict:
    m = re.match(r'FillAuto\s+"(.+?)"\s+with\s+"(.+?)"', line)
    if not m:
        return {"step": line, "status": "SYNTAX_ERROR", "error": "Malformed FillAuto"}
    sel, txt = m.group(1), m.group(2)
    try:
        await page.fill(sel, txt)
        await page.press(sel, 'Enter')
        await wait_after_action(page)
        return {"step": line, "status": "PASS", "error": None}
    except Exception as e:
        return {"step": line, "status": "FAIL", "error": str(e)}

async def handle_waitfor(page: Page, line: str) -> dict:
    m = re.match(r'WaitFor\s+"(.+?)"', line)
    if not m:
        return {"step": line, "status": "SYNTAX_ERROR", "error": "Malformed WaitFor"}
    sel = m.group(1)
    try:
        await page.wait_for_selector(sel, timeout=30000)
        return {"step": line, "status": "PASS", "error": None}
    except Exception as e:
        return {"step": line, "status": "FAIL", "error": str(e)}

async def handle_scrollto(page: Page, line: str) -> dict:
    m = re.match(r'ScrollTo\s+"(.+?)"', line)
    if not m:
        return {"step": line, "status": "SYNTAX_ERROR", "error": "Malformed ScrollTo"}
    sel = m.group(1)
    try:
        await page.locator(sel).scroll_into_view_if_needed()
        return {"step": line, "status": "PASS", "error": None}
    except Exception as e:
        return {"step": line, "status": "FAIL", "error": str(e)}

async def handle_assertcookie(page: Page, line: str) -> dict:
    m = re.match(r'AssertCookie\s+"(.+?)"\s+is\s+"(.+?)"', line)
    if not m:
        return {"step": line, "status": "SYNTAX_ERROR", "error": "Malformed AssertCookie"}
    name, val = m.group(1), m.group(2)
    try:
        ck = next((c for c in await page.context.cookies() if c['name']==name), None)
        assert ck and ck['value']==val, f"Cookie {name} has value {ck['value'] if ck else None}, expected {val}"
        return {"step": line, "status": "PASS", "error": None}
    except Exception as e:
        return {"step": line, "status": "FAIL", "error": str(e)}

async def handle_viewport(page: Page, line: str) -> dict:
    m = re.match(r'Viewport\s+(\d+)x(\d+)', line)
    if not m:
        return {"step": line, "status": "SYNTAX_ERROR", "error": "Malformed Viewport"}
    w, h = int(m.group(1)), int(m.group(2))
    try:
        await page.set_viewport_size({"width": w, "height": h})
        return {"step": line, "status": "PASS", "error": None}
    except Exception as e:
        return {"step": line, "status": "FAIL", "error": str(e)}

# Stubs for unimplemented commands
async def handle_waitforpopup(page: Page, line: str): return {"step": line, "status": "FAIL", "error": "Not implemented: WaitForPopup"}
async def handle_switchtopopup(page: Page, line: str): return {"step": line, "status": "FAIL", "error": "Not implemented: SwitchToPopup"}
async def handle_closepopup(page: Page, line: str): return {"step": line, "status": "FAIL", "error": "Not implemented: ClosePopup"}
async def handle_switchtoiframe(page: Page, line: str): return {"step": line, "status": "FAIL", "error": "Not implemented: SwitchToIFrame"}
async def handle_returnfromiframe(page: Page, line: str): return {"step": line, "status": "FAIL", "error": "Not implemented: ReturnFromIFrame"}
async def handle_savesession(page: Page, line: str): return {"step": line, "status": "FAIL", "error": "Not implemented: SaveSession"}
async def handle_restoresession(page: Page, line: str): return {"step": line, "status": "FAIL", "error": "Not implemented: RestoreSession"}
async def handle_retry(page: Page, line: str): return {"step": line, "status": "FAIL", "error": "Not implemented: Retry"}

async def handle_setvar(page: Page, line: str) -> dict:
    #"""
    #DSL: SetVar "NAME" = JS_EXPRESSION
    #Example:
    #  SetVar "LINKS" = await page.$$eval('body a', els => els.slice(0,5).map(e => e.href))
    #"""
    # match variable name in quotes, then =, then capture the rest
    m = re.match(r'SetVar\s+"(.+?)"\s*=\s*(.+)', line)
    if not m:
        return {"step": line, "status": "SYNTAX_ERROR", "error": "Malformed SetVar"}

    varname, js_expr = m.group(1), m.group(2)
    try:
        # Evaluate whatever JS the user provided
        val = await page.evaluate(js_expr)
        # Store on page for later use if needed
        if not hasattr(page, "_vars"):
            page._vars = {}
        page._vars[varname] = val
        return {"step": line, "status": "PASS", varname: val}
    except Exception as e:
        return {"step": line, "status": "FAIL", "error": str(e)}

async def execute_step(page: Page, line: str, ctx: BrowserContext, save_snapshots: bool):
    # skip comments, blank lines, and metadata headers
    if (not line or line.startswith('#') or line.startswith('Test:') or line.startswith('Tags:') or line == 'End'):
        return None

    cmd = line.split()[0]
    dispatcher = {
        'Goto': handle_goto, 'Click': handle_click, 'Fill': handle_fill, 'FillAuto': handle_fillauto,
        'WaitFor': handle_waitfor, 'ScrollTo': handle_scrollto, 'AssertCookie': handle_assertcookie,
        'Viewport': handle_viewport,
        'WaitForPopup': handle_waitforpopup, 'SwitchToPopup': handle_switchtopopup,
        'ClosePopup': handle_closepopup, 'SwitchToIFrame': handle_switchtoiframe,
        'ReturnFromIFrame': handle_returnfromiframe,
        'SaveSession': handle_savesession, 'RestoreSession': handle_restoresession,
        'Retry': handle_retry, 'SetVar': handle_setvar
    }
    if cmd in dispatcher:
        return await dispatcher[cmd](page, line)
    if cmd == 'Assert':
        expr = line[len('Assert'):].strip()
        return await handle_assert(page, expr, save_snapshots)
    if cmd not in SUPPORTED_COMMANDS:
        return {"step": line, "status": "SYNTAX_ERROR", "error": f"Unknown or malformed: {cmd}"}
    return {"step": line, "status": "SYNTAX_ERROR", "error": f"Not implemented: {cmd}"}

async def run_device(script: str, device: str, browser: str, vars_: dict, debug: bool, save_snapshots: bool):
    results = []
    async with async_playwright() as p:
        br = await getattr(p, browser).launch(headless=not debug)
        ctx = await br.new_context(**DEVICE_VIEWPORTS[device])
        page = await ctx.new_page()
        content = Path(script).read_text()
        for k, v in vars_.items():
            content = content.replace(f'<{k}>', v)

        tags = []
        for raw in content.splitlines():
            line = raw.strip()

            # metadata: Tests and Tags
            if line.startswith("Tags:"):
                tags = re.findall(r'\w+', line[len("Tags:"):])
                continue
            if (
                not line
                or line.startswith("Test:")
                or line == "End"
                or line.startswith("#")
            ):
                continue

            # real step
            step = await execute_step(page, line, ctx, save_snapshots)
            if step:
                step["tags"] = tags.copy()
                results.append(step)

        await br.close()

    return {"device": device, "results": results}

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('script')
    parser.add_argument('--devices', default='desktop')
    parser.add_argument('--browser', default='chromium')
    parser.add_argument('-v', dest='vars', action='append', default=[])
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--snap', action='store_true')
    args = parser.parse_args()

    vars_ = dict(v.split('=', 1) for v in args.vars)
    all_results = []
    for d in args.devices.split(','):
        all_results.append(
            await run_device(args.script, d, args.browser, vars_, args.debug, args.snap)
        )

    # Always emit pure JSON array to stdout
    print(json.dumps(all_results, indent=2))

def cli():
    """Entry point for console_scripts."""
    asyncio.run(main())

if __name__ == '__main__':
    cli()

