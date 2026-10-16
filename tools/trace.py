#!/usr/bin/env python3
"""Trace a black-on-white silhouette PNG into a smooth SVG path.
python3 tools/trace.py in.png out.svg [--eps 1.2] [--flip]
Prints the path's viewBox. Contours via OpenCV, smoothed with Catmull-Rom curves."""
import sys, argparse
import cv2, numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--eps", type=float, default=1.2)
ap.add_argument("--flip", action="store_true", help="mirror horizontally")
ap.add_argument("--min-area", type=float, default=120)
a = ap.parse_args()

im = cv2.imread(a.src, cv2.IMREAD_GRAYSCALE)
im = cv2.resize(im, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
im = cv2.GaussianBlur(im, (5, 5), 0)
_, bw = cv2.threshold(im, 128, 255, cv2.THRESH_BINARY_INV)
if a.flip:
    bw = cv2.flip(bw, 1)
cs, hier = cv2.findContours(bw, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)


def smooth(pts):
    n = len(pts)
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d + "Z"


parts = []; xs = []; ys = []
for c in cs:
    if cv2.contourArea(c) < a.min_area:
        continue
    ap_ = cv2.approxPolyDP(c, a.eps * 2, True).reshape(-1, 2) / 2.0
    if len(ap_) < 3:
        continue
    parts.append(smooth([tuple(p) for p in ap_]))
    xs += list(ap_[:, 0]); ys += list(ap_[:, 1])
x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
vb = f"{x0 - 2:.0f} {y0 - 2:.0f} {x1 - x0 + 4:.0f} {y1 - y0 + 4:.0f}"
open(a.out, "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"><path fill-rule="evenodd" d="{"".join(parts)}"/></svg>\n')
print(vb, len(parts), "contours")
