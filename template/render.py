#!/usr/bin/env python3
"""Render TWD branded Facebook graphics (1080x1080 PNG).

Usage: python3 render.py card.json out.png
card.json fields:
  eyebrow   short label above headline, e.g. "AI SERVICES"
  headline  main text; wrap words in *asterisks* to color them orange
  body      optional 1-2 sentence supporting line
  cta       call to action line, e.g. "Call 210-985-8528"
  style     "dark" (default) or "orange"
"""
import json, sys, re, html, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent
F = ROOT / "node_modules/@fontsource"  # setup: npm i @fontsource/oswald @fontsource/inter (in this folder)
FONTS = f"""
@font-face{{font-family:Oswald;font-weight:500;src:url('file://{F}/oswald/files/oswald-latin-500-normal.woff2')}}
@font-face{{font-family:Oswald;font-weight:700;src:url('file://{F}/oswald/files/oswald-latin-700-normal.woff2')}}
@font-face{{font-family:Inter;font-weight:400;src:url('file://{F}/inter/files/inter-latin-400-normal.woff2')}}
@font-face{{font-family:Inter;font-weight:600;src:url('file://{F}/inter/files/inter-latin-600-normal.woff2')}}
"""

LOGO_B64 = __import__("base64").b64encode((ROOT / "logo.png").read_bytes()).decode()
BADGE = f'<img src="data:image/png;base64,{LOGO_B64}" style="width:300px;height:auto;display:block">'


def build(c):
    style = c.get("style", "dark")
    bg, accent, ink, sub = ("#0E0E0E", "#FF6B1A", "#FFFFFF", "#B9B9B9")
    if style == "orange":
        bg, accent, ink, sub = ("#FF6B1A", "#0E0E0E", "#FFFFFF", "#1A1A1A")
    head = html.escape(c["headline"])
    head = re.sub(r"\*(.+?)\*", rf'<span style="color:{accent}">\1</span>', head)
    n = len(re.sub(r"\*", "", c["headline"]))
    size = 132 if n <= 28 else 112 if n <= 44 else 94 if n <= 64 else 80
    body = f'<p class="body">{html.escape(c["body"])}</p>' if c.get("body") else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1080px;background:{bg};color:{ink};font-family:Inter;overflow:hidden;position:relative}}
.grain{{display:none}}
.frame{{position:absolute;inset:40px;border:2px solid rgba(255,255,255,.14)}}
.wrap{{position:absolute;inset:96px 96px 96px;display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:flex-start}}
.eyebrow{{font-family:Oswald;font-weight:500;font-size:30px;letter-spacing:6px;color:{accent};text-transform:uppercase;border-left:8px solid {accent};padding-left:20px;margin-top:20px}}
h1{{font-family:Oswald;font-weight:700;font-size:{size}px;line-height:1.02;text-transform:uppercase;letter-spacing:1px;margin-top:auto}}
.body{{font-size:36px;line-height:1.4;color:{sub};margin-top:36px;max-width:820px}}
.foot{{margin-top:56px;display:flex;justify-content:space-between;align-items:center;border-top:2px solid rgba(255,255,255,.18);padding-top:32px}}
.cta{{font-family:Oswald;font-weight:700;font-size:40px;letter-spacing:2px;text-transform:uppercase;background:{accent};color:{bg if style=='dark' else '#fff'};padding:14px 28px}}
.site{{font-family:Oswald;font-weight:500;font-size:30px;letter-spacing:3px;color:{sub}}}
</style></head><body><div class="grain"></div><div class="frame"></div>
<div class="wrap"><div class="top"><div class="eyebrow">{html.escape(c.get('eyebrow',''))}</div>{BADGE}</div>
<h1>{head}</h1>{body}
<div class="foot"><div class="cta">{html.escape(c.get('cta','Call 210-985-8528'))}</div><div class="site">TEXASWEBDESIGN.COM</div></div></div>
</body></html>"""


def main():
    card = json.loads(pathlib.Path(sys.argv[1]).read_text())
    out = pathlib.Path(sys.argv[2]).resolve()
    tmp = out.with_suffix(".html")
    tmp.write_text(build(card))
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1080})
        pg.goto(f"file://{tmp}")
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(out))
        b.close()
    tmp.unlink()
    # shrink to ~30KB (flat colors) so it uploads easily
    from PIL import Image
    Image.open(out).convert('RGB').quantize(colors=32, method=Image.Quantize.MEDIANCUT).save(out, optimize=True)
    print(out)


if __name__ == "__main__":
    main()
