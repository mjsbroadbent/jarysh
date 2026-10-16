"""Shared helpers for the Jarysh / Aigyr brand art: text to SVG outlines, horseshoe, sparkles, PNG export."""
import math
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONTS = {
    "inter-black-it": "/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf",
    "inter-black": "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf",
    "bonum-bi": "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrebonum-bolditalic.otf",
    "bonum-b": "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrebonum-bold.otf",
    "heroscn-b": "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreheroscn-bold.otf",
    "chorus": "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrechorus-mediumitalic.otf",
    "schola-b": "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreschola-bold.otf",
}
_cache = {}


def _font(key):
    if key not in _cache:
        _cache[key] = TTFont(FONTS[key])
    return _cache[key]


def text_path(key, text, size, x=0, y=0, tracking=0, sx=1.0, kern=None):
    """Outline `text` with its baseline at (x, y). Returns (d, advance_width).
    tracking in em/1000; sx squeezes horizontally; kern = {pair: em/1000} manual tweaks."""
    f = _font(key)
    upm = f["head"].unitsPerEm
    cmap = f.getBestCmap(); gs = f.getGlyphSet(); hmtx = f["hmtx"]
    s = size / upm
    pen = SVGPathPen(gs)
    cx = 0
    prev = None
    for ch in text:
        if kern and prev and (prev + ch) in kern:
            cx += kern[prev + ch]
        g = cmap[ord(ch)]
        tp = TransformPen(pen, (s * sx, 0, 0, -s, x + cx * s * sx, y))
        gs[g].draw(tp)
        cx += hmtx[g][0] + tracking
        prev = ch
    return pen.getCommands(), (cx - tracking) * s * sx


def horseshoe(cx, cy, r):
    """Horseshoe, toe down, heels up, about 2r wide. Draw `line` as a stroke of width 0.36r (butt caps).
    Returns (line_d, holes_svg): the centreline and eight nail holes along the fuller."""
    P = [(-0.60, -0.95), (-1.02, -0.45), (-0.98, 0.80), (0.0, 0.80), (0.98, 0.80), (1.02, -0.45), (0.60, -0.95)]
    P = [(cx + x * r, cy + y * r) for x, y in P]
    d = (f"M{P[0][0]:.1f},{P[0][1]:.1f} C{P[1][0]:.1f},{P[1][1]:.1f} {P[2][0]:.1f},{P[2][1]:.1f} {P[3][0]:.1f},{P[3][1]:.1f} "
         f"C{P[4][0]:.1f},{P[4][1]:.1f} {P[5][0]:.1f},{P[5][1]:.1f} {P[6][0]:.1f},{P[6][1]:.1f}")

    def bez(p0, p1, p2, p3, t):
        u = 1 - t
        pt = tuple(u**3 * p0[i] + 3 * u * u * t * p1[i] + 3 * u * t * t * p2[i] + t**3 * p3[i] for i in (0, 1))
        dt = tuple(3 * u * u * (p1[i] - p0[i]) + 6 * u * t * (p2[i] - p1[i]) + 3 * t * t * (p3[i] - p2[i]) for i in (0, 1))
        return pt, math.degrees(math.atan2(dt[1], dt[0]))
    holes = ""
    w, h = r * 0.075, r * 0.17
    for seg, ts in ((P[0:4], (0.14, 0.33, 0.52, 0.71)), (P[3:7], (0.29, 0.48, 0.67, 0.86))):
        for t in ts:
            (hx, hy), ang = bez(*seg, t)
            holes += (f'<rect x="{hx - h / 2:.1f}" y="{hy - w / 2:.1f}" width="{h:.1f}" height="{w:.1f}" rx="{w / 2.5:.1f}" '
                      f'transform="rotate({ang:.0f} {hx:.1f} {hy:.1f})"/>')
    return d, holes


def star(cx, cy, r):
    """Four-point sparkle."""
    k = r * 0.18
    return (f"M{cx},{cy - r} Q{cx + k},{cy - k} {cx + r},{cy} Q{cx + k},{cy + k} {cx},{cy + r} "
            f"Q{cx - k},{cy + k} {cx - r},{cy} Q{cx - k},{cy - k} {cx},{cy - r}Z")


def svg_to_png(svg_path, png_path, width, height=None, bg="transparent", t_ms=None):
    """Render an SVG file to PNG with Chromium. t_ms freezes CSS animations at that time."""
    from playwright.sync_api import sync_playwright
    import pathlib, tempfile
    svg_path = pathlib.Path(svg_path).resolve()
    html = (f'<html><body style="margin:0;background:{bg}"><img id="i" src="file://{svg_path}" style="display:block;width:{width}px">'
            f'</body></html>')
    tmp = pathlib.Path(tempfile.gettempdir()) / "_svg2png.html"; tmp.write_text(html)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": width, "height": height or width}, device_scale_factor=1)
        pg.goto(f"file://{tmp}"); pg.wait_for_timeout(250 if t_ms is None else t_ms)
        el = pg.query_selector("#i")
        el.screenshot(path=str(png_path), omit_background=(bg == "transparent"))
        b.close()


def glyph_path(key, ch, size):
    """Single glyph outline at the origin (baseline y=0). Returns (d, advance)."""
    return text_path(key, ch, size)


def arc_text(key, text, size, cx, cy, R, center_deg=-90, tracking=0, bottom=False):
    """Text set on a circle of radius R around (cx, cy), centred at center_deg (-90 = top).
    Top text reads clockwise with letters standing outward; bottom text reads left to right along the bottom."""
    import math as m
    advs = [glyph_path(key, c, size)[1] + tracking for c in text]
    total = sum(advs) - tracking
    span = total / R  # radians
    out = []
    pos = 0.0
    for c, a in zip(text, advs):
        d, adv = glyph_path(key, c, size)
        mid = pos + adv / 2
        if not bottom:
            ang = m.radians(center_deg) - span / 2 + mid / R
            deg = m.degrees(ang) + 90
        else:
            ang = m.radians(center_deg) + span / 2 - mid / R
            deg = m.degrees(ang) - 90
        x, y = cx + R * m.cos(ang), cy + R * m.sin(ang)
        if d:
            out.append(f'<path d="{d}" transform="translate({x:.2f} {y:.2f}) rotate({deg:.2f}) translate({-adv / 2:.2f} {size * 0.35 if not bottom else size * 0.35:.2f})"/>')
        pos += a
    return "".join(out)


def silhouette(name):
    """Path data and viewBox of a traced silhouette in img/src/sil/."""
    import re
    from pathlib import Path
    s = (Path(__file__).resolve().parent.parent / "img" / "src" / "sil" / f"{name}.svg").read_text()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
    d = re.search(r' d="([^"]+)"', s).group(1)
    return d, vb
