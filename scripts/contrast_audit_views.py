#!/usr/bin/env python3
"""Mobile + desktop viewport audit using the shared payload."""
import sys, json
from playwright.sync_api import sync_playwright

CHROME = "/home/weissto_local/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome"  # override as needed
AUDIT = open('/tmp/audit_payload.js').read()

def main():
    urls = sys.argv[1:]
    viewports = [(320, 800), (768, 1024), (1440, 1000)]
    schemes = ["light", "dark"]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, headless=True)
        for url in urls:
            for scheme in schemes:
                for w, h in viewports:
                    ctx = b.new_context(viewport={"width": w, "height": h}, color_scheme=scheme)
                    page = ctx.new_page()
                    try:
                        page.goto(url, wait_until="networkidle", timeout=20000)
                        page.wait_for_timeout(4000)
                        res = page.evaluate(AUDIT)
                    except Exception as e:
                        print(f"  [{w}x{h}] ERROR {e}")
                        ctx.close()
                        continue
                    ctx.close()
                    dedup = {}
                    for r in res:
                        k = (r['cls'], r['text'])
                        if k not in dedup:
                            dedup[k] = r
                    print(f"=== {url} @{w}x{h} [{scheme}] : {len(dedup)} low-contrast ===")
                    for r in dedup.values():
                        bgdesc = f"grad[{r['bgCss']}]" if r['bgType']=='gradient' else f"solid#{''.join(f'{max(0,min(255,round(x))):02x}' for x in r['bgArr'][:3])}"
                        print(f"  .{r['cls']} \"{r['text']}\" ratio {r['ratio']:.2f} < {r['need']} [{r['size']}px{' bold' if r['bold'] else ''}] bg={bgdesc}")
        b.close()

if __name__ == '__main__':
    main()
