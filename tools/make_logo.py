#!/usr/bin/env python3
"""Jarysh logo: animated SVG (gold letters with a shine sweep and twinkling sparkles, a swinging lucky horseshoe)
plus static PNGs.   python3 tools/make_logo.py"""
from pathlib import Path
from brandlib import text_path, horseshoe, star, svg_to_png

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "img"

GOLD = """<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#fffbe0"/><stop offset=".16" stop-color="#ffe680"/><stop offset=".40" stop-color="#f5b400"/>
<stop offset=".52" stop-color="#9a5e00"/><stop offset=".60" stop-color="#e7a90f"/><stop offset=".76" stop-color="#fff0a8"/>
<stop offset="1" stop-color="#b67a06"/></linearGradient>
<linearGradient id="goldH" gradientUnits="userSpaceOnUse" x1="0" y1="-44" x2="0" y2="40">
<stop offset="0" stop-color="#fffbe0"/><stop offset=".3" stop-color="#ffd447"/><stop offset=".55" stop-color="#a86a00"/>
<stop offset=".72" stop-color="#ffe27a"/><stop offset="1" stop-color="#9a6200"/></linearGradient>
<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<filter id="bevel" x="-5%" y="-5%" width="110%" height="110%">
<feGaussianBlur in="SourceAlpha" stdDeviation="2.2" result="b"/>
<feSpecularLighting in="b" surfaceScale="4" specularConstant=".9" specularExponent="22" lighting-color="#fff6d0" result="s">
<fePointLight x="120" y="-160" z="220"/></feSpecularLighting>
<feComposite in="s" in2="SourceAlpha" operator="in" result="sc"/>
<feComposite in="SourceGraphic" in2="sc" operator="arithmetic" k1="0" k2="1" k3=".75" k4="0"/></filter>
<filter id="drop" x="-10%" y="-10%" width="130%" height="140%"><feGaussianBlur stdDeviation="3"/></filter>
<radialGradient id="glow"><stop offset="0" stop-color="#fff"/><stop offset=".35" stop-color="#fff6c0"/><stop offset="1" stop-color="#ffd447" stop-opacity="0"/></radialGradient>"""

STYLE = """<style>
.shine{animation:sweep 4.2s cubic-bezier(.45,.05,.35,1) infinite}
@keyframes sweep{0%{transform:translateX(-160px) skewX(-22deg)}55%,100%{transform:translateX(720px) skewX(-22deg)}}
.sp{transform-box:fill-box;transform-origin:center;animation:tw 2.8s ease-in-out infinite;opacity:0}
@keyframes tw{0%,100%{transform:scale(0) rotate(0);opacity:0}12%{transform:scale(1.15) rotate(45deg);opacity:1}26%{transform:scale(0) rotate(90deg);opacity:0}}
.shoe{transform-box:fill-box;transform-origin:50% 0%;animation:swing 3.6s ease-in-out infinite}
@keyframes swing{0%,100%{transform:rotate(-14deg)}50%{transform:rotate(-4deg)}}
@media (prefers-reduced-motion:reduce){.shine,.sp,.shoe{animation:none}.sp{opacity:0}}
</style>"""


def jarysh(path, animated=True):
    H = 150
    d, w = text_path("inter-black-it", "JARYSH", 122, x=122, y=122, sx=0.86, tracking=-10, kern={"AR": -6, "YS": -4})
    _, cw = text_path("heroscn-b", ".COM", 20, tracking=60)
    W = int(122 + w + 26)
    com, _ = text_path("heroscn-b", ".COM", 20, x=122 + w - cw + 8, y=24, tracking=60)
    line, holes = horseshoe(0, 0, 40)
    sparks = [(156, 38, 13, 0.0), (296, 34, 10, 0.7), (400, 114, 12, 1.3), (W - 40, 50, 14, 1.9), (234, 118, 9, 2.3), (34, 48, 11, 1.0)]
    sp = "".join(f'<g class="sp" style="animation-delay:{dl}s"><circle cx="{x}" cy="{y}" r="{r * .9:.0f}" fill="url(#glow)" opacity=".7"/>'
                 f'<path d="{star(x, y, r)}" fill="#fff"/></g>' for x, y, r, dl in sparks)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<title>JARYSH</title>
<defs>{GOLD}<clipPath id="tc"><path d="{d}"/></clipPath></defs>
{STYLE if animated else ""}
<g transform="translate(62 82)"><g class="shoe">
<path d="{line}" fill="none" stroke="#000" stroke-opacity=".55" stroke-width="22" transform="translate(3 5)" filter="url(#drop)"/>
<path d="{line}" fill="none" stroke="#d4101c" stroke-width="27"/>
<path d="{line}" fill="none" stroke="#2a1600" stroke-width="21"/>
<path d="{line}" fill="none" stroke="url(#goldH)" stroke-width="16" filter="url(#bevel)"/>
<path d="{line}" fill="none" stroke="#7a4a00" stroke-opacity=".55" stroke-width="2.2"/>
<g fill="#3a2200">{holes}</g>
</g></g>
<path d="{d}" fill="#000" fill-opacity=".6" transform="translate(4 6)" filter="url(#drop)"/>
<path d="{d}" fill="none" stroke="#d4101c" stroke-width="15" stroke-linejoin="round"/>
<path d="{d}" fill="none" stroke="#2a1600" stroke-width="7" stroke-linejoin="round"/>
<path d="{d}" fill="url(#gold)" filter="url(#bevel)"/>
<g clip-path="url(#tc)"><rect class="shine" x="0" y="0" width="70" height="{H}" fill="url(#shine)" opacity=".85"/></g>
<path d="{com}" fill="#ffd447"/>
{sp if animated else ""}
</svg>
'''
    Path(path).write_text(svg)


if __name__ == "__main__":
    jarysh(IMG / "jarysh-logo.svg")
    jarysh(IMG / "src" / "jarysh-logo-static.svg", animated=False)
    svg_to_png(IMG / "src" / "jarysh-logo-static.svg", IMG / "jarysh-logo.png", 240, 80)
    svg_to_png(IMG / "src" / "jarysh-logo-static.svg", IMG / "jarysh-logo@2x.png", 560, 180)
    print("logo done")
