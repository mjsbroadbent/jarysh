#!/usr/bin/env python3
"""Aigyr Lager brand: roundel crest, script wordmark, horizontal lockup, PNG renders.   python3 tools/make_aigyr.py"""
import math
from pathlib import Path
from brandlib import text_path, arc_text, silhouette, star, svg_to_png

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "img"; SRC = IMG / "src"

DEFS = """<linearGradient id="ag" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#fff4c4"/><stop offset=".3" stop-color="#f2c447"/><stop offset=".55" stop-color="#a8700c"/>
<stop offset=".75" stop-color="#f6d06a"/><stop offset="1" stop-color="#8e5c08"/></linearGradient>
<linearGradient id="ag2" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#fff2b8"/><stop offset=".45" stop-color="#e2ad2c"/><stop offset=".7" stop-color="#9a6508"/><stop offset="1" stop-color="#f0c75a"/></linearGradient>
<linearGradient id="rib" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d42a2a"/><stop offset=".5" stop-color="#a5121b"/><stop offset="1" stop-color="#6e0a10"/></linearGradient>
<radialGradient id="disc" cx=".5" cy=".42" r=".6"><stop offset="0" stop-color="#3a2408"/><stop offset="1" stop-color="#0e0904"/></radialGradient>
<filter id="bev" x="-5%" y="-5%" width="110%" height="110%">
<feGaussianBlur in="SourceAlpha" stdDeviation="1.6" result="b"/>
<feSpecularLighting in="b" surfaceScale="3" specularConstant=".8" specularExponent="18" lighting-color="#fff3cc" result="s"><fePointLight x="100" y="-200" z="260"/></feSpecularLighting>
<feComposite in="s" in2="SourceAlpha" operator="in" result="sc"/>
<feComposite in="SourceGraphic" in2="sc" operator="arithmetic" k1="0" k2="1" k3=".6" k4="0"/></filter>"""


def crest_body(cx=200, cy=200):
    R = 196
    rays = []
    for i in range(36):
        a0, a1 = math.radians(i * 10), math.radians(i * 10 + 5)
        rays.append(f'M{cx},{cy} L{cx + 150 * math.cos(a0):.1f},{cy + 150 * math.sin(a0):.1f} L{cx + 150 * math.cos(a1):.1f},{cy + 150 * math.sin(a1):.1f}Z')
    hd, vb = silhouette("head")
    s = 158 / vb[3]
    hx, hy = cx - vb[2] * s / 2 - vb[0] * s + 6, cy - 118 - vb[1] * s
    top = arc_text("bonum-b", "AIGYR BREWING COMPANY", 25, cx, cy, 166, -90, tracking=3.5)
    bot = arc_text("bonum-b", "KARA-BULAK · 2009", 24, cx, cy, 166, 90, tracking=2.5, bottom=True)
    # ribbon
    ry, rh = cy + 34, 46
    rib = (f'<path d="M{cx - 168},{ry + 12} l24,{rh / 2 - 10} l-24,{rh / 2 + 2} h42 v-{rh}z" fill="#6e0a10"/>'
           f'<path d="M{cx + 168},{ry + 12} l-24,{rh / 2 - 10} l24,{rh / 2 + 2} h-42 v-{rh}z" fill="#6e0a10"/>'
           f'<path d="M{cx - 140},{ry - 6} Q{cx},{ry - 22} {cx + 140},{ry - 6} v{rh} Q{cx},{ry + rh - 16} {cx - 140},{ry + rh - 6}z" fill="url(#rib)" stroke="#f2c447" stroke-width="2.5"/>')
    gl, gw = text_path("bonum-b", "GOLD LAGER", 30, tracking=80)
    lab = f'<path d="{gl}" transform="translate({cx - gw / 2:.1f} {ry + 27})" fill="#fff4dc"/>'
    return f'''<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#ag2)"/>
<circle cx="{cx}" cy="{cy}" r="{R - 7}" fill="#140d05"/>
<circle cx="{cx}" cy="{cy}" r="{R - 12}" fill="none" stroke="url(#ag)" stroke-width="2"/>
<circle cx="{cx}" cy="{cy}" r="146" fill="url(#ag2)"/>
<circle cx="{cx}" cy="{cy}" r="140" fill="url(#disc)"/>
<path d="{"".join(rays)}" fill="#f2c447" fill-opacity=".07"/>
<g fill="url(#ag)" filter="url(#bev)">{top}{bot}</g>
<path d="{star(cx - 166, cy, 10)}" fill="#f2c447"/><path d="{star(cx + 166, cy, 10)}" fill="#f2c447"/>
<path d="{hd}" transform="translate({hx:.1f} {hy:.1f}) scale({s:.4f})" fill="url(#ag)" filter="url(#bev)"/>
{rib}{lab}'''


def crest(path):
    Path(path).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400"><title>Aigyr Brewing Company</title><defs>{DEFS}</defs>{crest_body()}</svg>\n')


def wordmark_body(x=0, y=150, size=168, light=False):
    d, w = text_path("bonum-bi", "Aigyr", size, x=x, y=y, tracking=-10)
    sw_y = y + 22
    swash = (f'<path d="M{x + 10},{sw_y} C{x + w * .35},{sw_y + 40} {x + w * .75},{sw_y + 26} {x + w + 40},{sw_y - 30} '
             f'C{x + w * .78},{sw_y + 4} {x + w * .4},{sw_y + 12} {x + 10},{sw_y}Z"/>')
    tl, tw = text_path("heroscn-b", "IRADI GOLD LAGER", 24, tracking=240)
    tag = f'<path d="{tl}" transform="translate({x + (w - tw) / 2 + 14:.1f} {sw_y + 52})"/>'
    fill = "#fff4dc" if light else "url(#ag)"
    return (f'<g><path d="{d}" fill="none" stroke="#000" stroke-opacity=".55" stroke-width="10" transform="translate(3 5)"/>'
            f'<path d="{d}" fill="none" stroke="#a5121b" stroke-width="12" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="#140d05" stroke-width="6" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="{fill}" filter="url(#bev)"/>'
            f'<g fill="#a5121b" stroke="#140d05" stroke-width="3">{swash}</g>'
            f'<g fill="#f2c447">{tag}</g></g>'), w


def wordmark(path):
    body, w = wordmark_body(20, 150)
    W = int(w + 80)
    Path(path).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 250" width="{W}" height="250"><title>Aigyr</title><defs>{DEFS}</defs>{body}</svg>\n')
    return W


def lockup(path):
    body, w = wordmark_body(250, 150)
    W = int(250 + w + 70)
    Path(path).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 250" width="{W}" height="250"><title>Aigyr Lager</title><defs>{DEFS}</defs>'
                          f'<g transform="translate(5 10) scale(.575)">{crest_body()}</g>{body}</svg>\n')
    return W


if __name__ == "__main__":
    crest(IMG / "aigyr-crest.svg")
    ww = wordmark(IMG / "aigyr-wordmark.svg")
    lw = lockup(IMG / "aigyr-logo.svg")
    svg_to_png(IMG / "aigyr-crest.svg", SRC / "aigyr-crest.png", 600, 600)
    svg_to_png(IMG / "aigyr-wordmark.svg", SRC / "aigyr-wordmark.png", 900, 300)
    svg_to_png(IMG / "aigyr-logo.svg", SRC / "aigyr-logo.png", 1000, 300)
    print("aigyr brand done", ww, lw)
