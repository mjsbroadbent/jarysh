#!/usr/bin/env python3
"""Logo, favicon, background and the in-house ad banners for jarysh.com.  python3 tools/make_art.py
Needs img/src/can.png (the Aigyr can photo) for the Aigyr ads."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "img"; ADS = IMG / "ads"; ADS.mkdir(parents=True, exist_ok=True)
G = "/usr/share/texmf/fonts/opentype/public/tex-gyre/"
CN = G + "texgyreheroscn-bold.otf"; HB = G + "texgyreheros-bold.otf"; HR = G + "texgyreheros-regular.otf"; TB = G + "texgyretermes-bold.otf"
F = lambda p, s: ImageFont.truetype(p, s)
GOLD = (246, 184, 0); GOLD2 = (255, 216, 77); RED = (227, 23, 30); PINK = (255, 45, 135); BLACK = (12, 10, 18)


def gradient_text(size, text, font, top, bottom, stroke=0, stroke_fill=(0, 0, 0), skew=0.0):
    w, h = size
    mask = Image.new("L", size, 0); d = ImageDraw.Draw(mask)
    d.text((w // 2, h // 2), text, font=font, anchor="mm", fill=255, stroke_width=stroke, stroke_fill=255)
    inner = Image.new("L", size, 0); ImageDraw.Draw(inner).text((w // 2, h // 2), text, font=font, anchor="mm", fill=255)
    grad = Image.new("RGB", size)
    for y in range(h):
        t = y / max(h - 1, 1)
        grad.paste(tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)), (0, y, w, y + 1))
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(Image.new("RGB", size, stroke_fill), (0, 0), mask)
    out.paste(grad, (0, 0), inner)
    if skew:
        out = out.transform(size, Image.AFFINE, (1, skew, -skew * h / 2, 0, 1, 0), Image.BICUBIC)
    return out


def horse_head(size, fill):
    """A horseshoe, open end up (luck in), with nail holes."""
    S = size * 4
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    t = S * 0.17
    box = (S * 0.1, S * 0.12, S * 0.9, S * 0.92)
    d.arc(box, -200, 20, fill=fill, width=int(t))
    hole = (0, 0, 0, 0)
    cx, cy, r = S / 2, (box[1] + box[3]) / 2, (box[2] - box[0]) / 2 - t / 2
    import math as m
    for a in (-185, -150, -115, -65, -30, 5):
        x, y = cx + r * m.cos(m.radians(a)), cy + r * m.sin(m.radians(a))
        d.ellipse((x - t * 0.14, y - t * 0.2, x + t * 0.14, y + t * 0.2), fill=hole)
    # calkins
    for a in (-200, 20):
        x, y = cx + r * m.cos(m.radians(a)), cy + r * m.sin(m.radians(a))
        d.rectangle((x - t * 0.55, y - t * 0.15, x + t * 0.55, y + t * 0.35), fill=fill)
    im = im.rotate(180, resample=Image.BICUBIC)
    return im.resize((size, size), Image.LANCZOS)


def logo():
    W, H = 460, 128
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hh = horse_head(104, GOLD + (255,)).rotate(-14, resample=Image.BICUBIC); im.alpha_composite(hh, (0, 10))
    t = gradient_text((360, 128), "JARYSH", F(CN, 112), (255, 236, 140), (214, 140, 0), stroke=5, stroke_fill=(20, 10, 0), skew=0.18)
    im.alpha_composite(t, (96, 2))
    d = ImageDraw.Draw(im)
    d.polygon([(110, 112), (440, 104), (436, 114), (106, 122)], fill=RED + (255,))
    d.text((452, 10), ".com", font=F(HB, 20), fill=GOLD2, anchor="ra")
    im.resize((W // 2, H // 2), Image.LANCZOS).save(IMG / "jarysh-logo.png")
    im.save(IMG / "jarysh-logo@2x.png")
    fav = Image.new("RGBA", (64, 64), BLACK + (255,)); fav.alpha_composite(horse_head(60, GOLD + (255,)), (2, 2))
    fav.save(IMG / "favicon.png")


def bg():
    im = Image.new("RGB", (240, 240), BLACK); d = ImageDraw.Draw(im)
    import random; r = random.Random(7)
    for _ in range(26):
        x, y = r.randrange(240), r.randrange(240); c = r.choice([(60, 48, 80), (90, 70, 20), (50, 40, 70)])
        d.point((x, y), fill=c)
    im.save(IMG / "bg-stars.png")


def starburst(d, cx, cy, r1, r2, n, fill):
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n; r = r1 if i % 2 == 0 else r2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


def can_cut():
    src = Image.open(IMG / "src" / "can.png").convert("RGB")
    return src


def aigyr_label(can, w):
    """AIGYR label on the plain can photo: wordmark on the dark band, horseshoe and GOLD LAGER above."""
    im = can.convert("RGBA"); W, H = im.size
    x0, x1, y0, y1 = 222, 612, 605, 745          # band on jr/can_00001_
    cx = (x0 + x1) // 2
    lab = Image.new("RGBA", im.size, (0, 0, 0, 0))
    word = gradient_text((x1 - x0, y1 - y0), "AIGYR", F(CN, 118), (255, 230, 140), (205, 140, 20))
    lab.alpha_composite(word, (x0, y0 + 2))
    hs = horse_head(150, (60, 30, 5, 235)); lab.alpha_composite(hs, (cx - 75, 330))
    d = ImageDraw.Draw(lab)
    d.text((cx, 512), "IRADIAN GOLD LAGER", font=F(HB, 26), fill=(60, 30, 5, 235), anchor="mm")
    d.text((cx, 552), "KARA-BULAK · EST. 2009", font=F(HR, 18), fill=(60, 30, 5, 220), anchor="mm")
    d.text((cx, 800), "RIDE HARD. DRINK AIGYR.", font=F(HB, 22), fill=(60, 30, 5, 230), anchor="mm")
    d.text((cx, 840), "4.8% ALC/VOL · 500 ml", font=F(HR, 18), fill=(60, 30, 5, 220), anchor="mm")
    # curve the print slightly darker at the can's edges
    edge = Image.new("L", im.size, 0); ed = ImageDraw.Draw(edge)
    for x in range(x0, x1):
        t = abs((x - cx) / ((x1 - x0) / 2)); ed.line((x, 0, x, H), fill=int(255 * (1 - 0.55 * t ** 3)))
    lab.putalpha(ImageChops.multiply(lab.getchannel("A"), edge))
    lab = lab.filter(ImageFilter.GaussianBlur(0.7))
    return Image.alpha_composite(im, lab).convert("RGB")


def aigyr_ads():
    can = aigyr_label(can_cut(), 0)
    can.save(IMG / "aigyr-can.jpg", quality=86)
    # 728x90
    W, H = 728, 90
    im = Image.new("RGB", (W, H), (20, 12, 0)); d = ImageDraw.Draw(im)
    for x in range(W):
        t = x / W; d.line((x, 0, x, H), fill=(int(40 + 180 * t ** 2), int(20 + 110 * t ** 2), 0))
    c = can.crop((int(can.width * 0.18), int(can.height * 0.12), int(can.width * 0.82), int(can.height * 0.92))).resize((72, 90))
    im.paste(c, (W - 72, 0))
    im.alpha_composite = None
    rgba = im.convert("RGBA")
    rgba.alpha_composite(gradient_text((260, 90), "AIGYR", F(CN, 76), (255, 236, 140), (214, 140, 0), stroke=3, stroke_fill=(30, 10, 0), skew=0.15), (10, 0))
    d = ImageDraw.Draw(rgba)
    d.text((280, 22), "RIDE HARD.", font=F(CN, 34), fill=(255, 255, 255))
    d.text((282, 58), "Official beer of Aigyr Ulak Nights · 2-for-1 till 20:00", font=F(HR, 14), fill=GOLD2)
    rgba.convert("RGB").save(ADS / "aigyr-728.png")
    # 300x250
    W, H = 300, 250
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line((0, y, W, y), fill=(int(70 * (1 - t) + 10), int(35 * (1 - t) + 5), 0, 255))
    starburst(d, 238, 60, 52, 38, 16, RED + (255,))
    d.text((238, 50), "2 for 1", font=F(CN, 24), fill="white", anchor="mm"); d.text((238, 74), "TILL 20:00", font=F(HB, 11), fill="white", anchor="mm")
    c = can.crop((int(can.width * 0.15), int(can.height * 0.05), int(can.width * 0.85), int(can.height * 0.95))).resize((130, 176))
    im.paste(c, (14, 60))
    im.alpha_composite(gradient_text((300, 70), "AIGYR", F(CN, 62), (255, 236, 140), (214, 140, 0), stroke=3, stroke_fill=(30, 10, 0), skew=0.15), (-50, -6))
    d = ImageDraw.Draw(im)
    d.text((158, 118), "RIDE", font=F(CN, 40), fill="white"); d.text((158, 156), "HARD.", font=F(CN, 40), fill=GOLD2)
    d.text((158, 206), "Gold · Strong · Light", font=F(HR, 11), fill=(220, 200, 150))
    d.text((158, 222), "Drink responsibly. 18+", font=F(HR, 9), fill=(150, 130, 100))
    im.convert("RGB").save(ADS / "aigyr-300.png")
    # badge
    S = 280
    b = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(b)
    d.ellipse((4, 4, S - 4, S - 4), fill=GOLD + (255,)); d.ellipse((16, 16, S - 16, S - 16), fill=(20, 10, 0, 255)); d.ellipse((24, 24, S - 24, S - 24), outline=GOLD + (255,), width=3)
    b.alpha_composite(horse_head(120, GOLD + (255,)), (S // 2 - 60, 44))
    # aviators on Big Aigyr
    d.text((S // 2, 196), "AIGYR", font=F(CN, 46), fill=GOLD + (255,), anchor="mm")
    d.text((S // 2, 230), "OFFICIAL BEER OF JARYSH", font=F(HB, 10), fill=GOLD2 + (255,), anchor="mm")
    b.resize((140, 140), Image.LANCZOS).save(ADS / "aigyr-badge.png")
    b.resize((200, 200), Image.LANCZOS).save(ADS / "aigyr-badge-200.png")


def steppe_ad():
    W, H = 300, 250
    im = Image.new("RGBA", (W, H), (40, 0, 60, 255)); d = ImageDraw.Draw(im)
    for r in range(220, 0, -4):
        t = r / 220; d.ellipse((150 - r, 90 - r, 150 + r, 90 + r), fill=(int(120 * (1 - t) + 30), 0, int(140 * (1 - t) + 40), 255))
    # coins
    import random; rr = random.Random(3)
    for _ in range(14):
        x, y, s = rr.randrange(0, 300), rr.randrange(120, 250), rr.randrange(18, 34)
        d.ellipse((x, y, x + s, y + s * 0.7), fill=GOLD + (255,), outline=(150, 100, 0, 255), width=2)
    # roulette wheel
    cx, cy, R = 240, 70, 46
    for i in range(18):
        a0, a1 = 360 / 18 * i, 360 / 18 * (i + 1)
        d.pieslice((cx - R, cy - R, cx + R, cy + R), a0, a1, fill=(RED if i % 2 else (10, 10, 10)) + (255,))
    d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=GOLD + (255,))
    im.alpha_composite(gradient_text((300, 80), "200%", F(CN, 80), (255, 255, 200), (255, 170, 0), stroke=4, stroke_fill=(80, 0, 40)), (-48, 4))
    d = ImageDraw.Draw(im)
    d.text((14, 88), "WELCOME BONUS", font=F(CN, 30), fill="white")
    d.text((14, 122), "UP TO 5,000 SOM", font=F(CN, 24), fill=GOLD2)
    d.rounded_rectangle((14, 160, 170, 196), 18, fill=(0, 200, 90, 255), outline=(255, 255, 255, 255), width=2)
    d.text((92, 178), "PLAY NOW »", font=F(CN, 22), fill="white", anchor="mm")
    d.text((14, 206), "STEPPE GAMING", font=F(CN, 18), fill="white")
    d.text((14, 228), "Ulak · Casino · Slots · Live dealers   18+ T&Cs", font=F(HR, 9), fill=(220, 200, 240))
    im.convert("RGB").save(ADS / "steppe-300.png")


def hats_ad():
    W, H = 300, 250
    src = Image.open(IMG / "src" / "hats.png").convert("RGB")
    sw, sh = src.size; s = max(W / sw, H / sh); src = src.resize((int(sw * s) + 1, int(sh * s) + 1)).crop((0, 0, W, H))
    im = src.convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((0, 0, W, 70), fill=(60, 30, 10, 220)); d.rectangle((0, 190, W, H), fill=(0, 0, 0, 200))
    d.text((W // 2, 24), "TEXAS HAT HOUSE", font=F(TB, 30), fill=(255, 230, 180), anchor="mm")
    d.text((W // 2, 54), "Chuy Avenue · Talas · since 2003", font=F(HR, 12), fill=(240, 210, 160), anchor="mm")
    starburst(d, 248, 120, 44, 32, 14, RED + (255,))
    d.text((248, 112), "-30%", font=F(CN, 24), fill="white", anchor="mm"); d.text((248, 134), "BOOTS", font=F(HB, 11), fill="white", anchor="mm")
    d.text((W // 2, 208), "REAL FELT. REAL COWBOY.", font=F(CN, 22), fill=GOLD2, anchor="mm")
    d.text((W // 2, 232), "Show your Ulak Nights ticket: free hat band", font=F(HR, 11), fill="white", anchor="mm")
    im.convert("RGB").save(ADS / "hats-300.png")


def power_ad():
    W, H = 300, 250
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line((0, y, W, y), fill=(int(10 + 30 * t), int(20 + 60 * t), int(60 + 120 * t), 255))
    # capsule bottle
    d.rounded_rectangle((196, 70, 270, 220), 12, fill=(240, 240, 240, 255)); d.rectangle((204, 56, 262, 74), fill=(20, 20, 20, 255))
    d.rectangle((196, 110, 270, 180), fill=RED + (255,)); d.text((233, 132), "CHONGTOR", font=F(CN, 15), fill="white", anchor="mm"); d.text((233, 152), "POWER", font=F(CN, 22), fill=GOLD2, anchor="mm")
    im.alpha_composite(horse_head(70, (255, 255, 255, 60)), (200, 160))
    d.text((14, 16), "FEEL LIKE A", font=F(CN, 26), fill="white")
    im.alpha_composite(gradient_text((190, 70), "STALLION", F(CN, 50), (255, 240, 150), (230, 140, 0), stroke=3, stroke_fill=(0, 0, 0)), (2, 42))
    d = ImageDraw.Draw(im)
    for i, t in enumerate(["More energy", "More stamina", "More confidence", "100% herbal*"]):
        y = 120 + i * 20; d.line((16, y + 8, 20, y + 13, 28, y + 2), fill=(0, 230, 90), width=3)
        d.text((34, y), t, font=F(HB, 14), fill="white")
    d.rounded_rectangle((14, 204, 170, 236), 16, fill=GOLD + (255,)); d.text((92, 220), "ORDER DISCREETLY", font=F(CN, 16), fill=(20, 10, 0), anchor="mm")
    d.text((180, 238), "*not evaluated by anyone", font=F(HR, 8), fill=(200, 200, 220))
    im.convert("RGB").save(ADS / "power-300.png")


if __name__ == "__main__":
    logo(); bg()
    if (IMG / "src" / "can.png").exists():
        aigyr_ads()
    steppe_ad(); power_ad()
    if (IMG / "src" / "hats.png").exists():
        hats_ad()
    print("art done")
