#!/usr/bin/env python3
"""Render the HTML ads in tools/ads/ to animated WebP in img/ads/.
python3 tools/render_ads.py [name ...]
Each ad declares <meta name="ad" content="out=NAME w=300 h=250 dur=4000 fps=12">. The renderer pauses every CSS
animation and steps it frame by frame, so loops are seamless when dur is a multiple of every animation's length."""
import re, sys, io
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ADS = ROOT / "tools" / "ads"; OUT = ROOT / "img" / "ads"; OUT.mkdir(parents=True, exist_ok=True)


def meta(html):
    m = re.search(r'<meta name="ad" content="([^"]+)"', html)
    return {k: v for k, v in (kv.split("=") for kv in m.group(1).split())}


def render(page, f):
    cfg = meta(f.read_text())
    w, h, dur, fps = int(cfg["w"]), int(cfg["h"]), int(cfg["dur"]), int(cfg.get("fps", 12))
    page.set_viewport_size({"width": w, "height": h})
    page.goto(f"file://{f}")
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(300)
    page.evaluate("document.getAnimations().forEach(a => a.pause())")
    frames = []
    n = round(dur * fps / 1000)
    for i in range(n):
        t = i * 1000 / fps
        page.evaluate(f"document.getAnimations().forEach(a => a.currentTime = {t})")
        frames.append(Image.open(io.BytesIO(page.screenshot(clip={"x": 0, "y": 0, "width": w, "height": h}))).convert("RGB"))
    out = OUT / f'{cfg["out"]}.webp'
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=round(1000 / fps), loop=0,
                   quality=int(cfg.get("q", 78)), method=4)
    poster = int(cfg.get("poster", 0))
    frames[min(round(poster * fps / 1000), n - 1)].save(OUT / f'{cfg["out"]}.jpg', quality=86)
    print(f'{out.name}: {n} frames, {out.stat().st_size // 1024} KB')


if __name__ == "__main__":
    names = sys.argv[1:]
    files = sorted(p for p in ADS.glob("*.html") if not names or p.stem in names)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        for f in files:
            render(pg, f)
        b.close()
