#!/usr/bin/env python3
"""Background tile and the labelled Aigyr can photo.   python3 tools/make_art.py
Needs img/src/can.png (plain gold can photo) and the Aigyr renders from tools/make_aigyr.py."""
import math, random
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "img"; SRC = IMG / "src"
BLACK = (12, 10, 18)


def bg():
    im = Image.new("RGB", (240, 240), BLACK); d = ImageDraw.Draw(im)
    r = random.Random(7)
    for _ in range(26):
        d.point((r.randrange(240), r.randrange(240)), fill=r.choice([(60, 48, 80), (90, 70, 20), (50, 40, 70)]))
    im.save(IMG / "bg-stars.png")


def trim(im):
    return im.crop(im.getchannel("A").getbbox())


def can():
    """Print the Aigyr crest and wordmark onto the plain can, wrapped round the cylinder."""
    base = Image.open(SRC / "can.png").convert("RGB")
    W, H = base.size
    x0, x1, band0, band1 = 222, 612, 605, 745        # can edges and dark band on jr/can_00001_
    cx, R = (x0 + x1) / 2, (x1 - x0) / 2
    flat = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    crest = trim(Image.open(SRC / "aigyr-crest.png").convert("RGBA")).resize((268, 268), Image.LANCZOS)
    flat.alpha_composite(crest, (int(cx - 134), 300))
    wm = trim(Image.open(SRC / "aigyr-wordmark.png").convert("RGBA"))
    # keep just the script and swash (drop the tagline line under it)
    wm = wm.crop((0, 0, wm.width, int(wm.height * 0.80)))
    s = 300 / wm.width; wm = wm.resize((300, int(wm.height * s)), Image.LANCZOS)
    flat.alpha_composite(wm, (int(cx - 150), band0 + (band1 - band0 - wm.height) // 2 + 6))
    # small print above and below the band
    from PIL import ImageFont
    G = "/usr/share/texmf/fonts/opentype/public/tex-gyre/"
    d = ImageDraw.Draw(flat)
    d.text((cx, 585), "IRADI GOLD LAGER", font=ImageFont.truetype(G + "texgyreheroscn-bold.otf", 22), fill=(70, 38, 6, 235), anchor="mm")
    d.text((cx, 775), "RIDE HARD. DRINK AIGYR.", font=ImageFont.truetype(G + "texgyreheroscn-bold.otf", 22), fill=(70, 38, 6, 235), anchor="mm")
    d.text((cx, 805), "4.8% ALC/VOL · 500 ml · BREWED IN KARA-BULAK", font=ImageFont.truetype(G + "texgyreheroscn-regular.otf", 15), fill=(70, 38, 6, 220), anchor="mm")
    # cylinder wrap: output x sees flat label at cx + R * asin(t) * (2 / pi) ... scaled so the centre is 1:1
    f = np.array(flat).astype(np.float32)
    mapx = np.tile(np.arange(W, dtype=np.float32), (H, 1)); mapy = np.tile(np.arange(H, dtype=np.float32)[:, None], (1, W))
    t = np.clip((mapx - cx) / R, -0.999, 0.999)
    inside = (mapx >= x0) & (mapx <= x1)
    mapx = np.where(inside, cx + R * np.arcsin(t), -10).astype(np.float32)
    warped = cv2.remap(f, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    rgb, a = warped[..., :3], warped[..., 3:] / 255.0
    # edge falloff so the print turns away from the light
    edge = np.clip(1 - np.abs(t) ** 4 * 0.85, 0, 1)[..., None]
    a = a * edge
    can_np = np.array(base).astype(np.float32)
    lum = cv2.cvtColor(can_np.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)[..., None] / 255.0
    lit = rgb * (0.45 + 0.85 * lum)                       # can lighting carried into the ink
    out = can_np * (1 - a) + np.clip(lit, 0, 255) * a
    # condensation and highlights back on top
    hi = np.clip((lum - 0.62) * 2.6, 0, 1)
    out = out * (1 - hi * 0.32) + can_np * hi * 0.32
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(IMG / "aigyr-can.jpg", quality=88)


if __name__ == "__main__":
    bg()
    can()
    print("art done")
