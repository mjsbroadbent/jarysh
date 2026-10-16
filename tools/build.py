#!/usr/bin/env python3
"""Builds jarysh.com.   python3 tools/build.py

content/league.json   tables, last round's results, next round's fixtures with odds
content/pages/*.html  pages: "key: value" header, blank line, HTML body with placeholders
content/news/*.txt    news: header (headline, date, image, tag, summary), blank line, paragraphs
Placeholders: {{isez_table}} {{hl_table}} {{results_isez}} {{results_hl}} {{odds_isez}} {{odds_hl}}
{{news_cards}} {{news_list}} {{next_date}} {{rel}}
"""
import html, json, re, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://jarysh.com/"
L = json.loads((ROOT / "content" / "league.json").read_text(encoding="utf-8"))
MONTHS = "January February March April May June July August September October November December".split()
esc = lambda s: html.escape(str(s), quote=True)
nice = lambda d: f"{d.day} {MONTHS[d.month - 1]} {d.year}"
TEMPLATE = (ROOT / "tools" / "page.html").read_text(encoding="utf-8")


def parse(p):
    t = p.read_text(encoding="utf-8").replace("\r\n", "\n")
    head, _, body = t.partition("\n\n")
    m = {k.strip(): v.strip() for k, v in (l.split(":", 1) for l in head.split("\n") if ":" in l)}
    m["body"], m["slug"] = body.strip(), p.stem
    if "date" in m:
        m["d"] = datetime.date.fromisoformat(m["date"])
    return m


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    return re.sub(r"\[(.+?)\]\((.+?)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', s)


def paras(body):
    out = []
    for b in re.split(r"\n\s*\n", body):
        b = b.strip()
        if not b:
            continue
        if b.startswith("## "):
            out.append(f"<h2>{inline(b[3:])}</h2>")
        elif b.startswith("<"):
            out.append(b)
        else:
            out.append(f"<p>{inline(' '.join(b.split()))}</p>")
    return "\n".join(out)


def table(rows):
    srt = sorted(rows, key=lambda t: (-(3 * t[2] + t[3]), -(t[5] - t[6]), -t[5]))
    tr = []
    for i, t in enumerate(srt, 1):
        name, p, w, d, l, gf, ga = t
        cls = "top" if i <= 2 else ("low" if i == len(srt) else "")
        tr.append(f'<tr class="{cls}"><td>{i}</td><td>{esc(name)}</td><td>{p}</td><td>{w}</td><td>{d}</td><td>{l}</td><td class="hide-m">{gf}</td><td class="hide-m">{ga}</td><td>{gf - ga:+d}</td><td class="pts">{3 * w + d}</td></tr>')
    return ('<table class="t"><tr><th>#</th><th>TEAM</th><th>P</th><th>W</th><th>D</th><th>L</th><th class="hide-m">GF</th><th class="hide-m">GA</th><th>GD</th><th>PTS</th></tr>'
            + "".join(tr) + "</table>")


def results(conf):
    li = []
    for c, h, a, b, aw in L["results"]:
        if c != conf:
            continue
        sc = f'<span class="sc">{a} – {b}</span>' if a is not None else '<span class="nr">NOT RECEIVED</span>'
        li.append(f'<li><span class="h">{esc(h)}</span>{sc}<span>{esc(aw)}</span></li>')
    return '<ul class="res">' + "".join(li) + "</ul>"


def odds(conf):
    tr = []
    for c, h, a, venue, time, oh, od, oa in L["fixtures"]:
        if c != conf:
            continue
        tr.append(f'<tr><td>{time}</td><td>{esc(h)} <span style="color:var(--muted)">v</span> {esc(a)}<br><span class="tiny">{esc(venue)}</span></td>'
                  f'<td><a class="odds" href="#partner">{oh:.2f}</a></td><td><a class="odds" href="#partner">{od:.2f}</a></td><td><a class="odds" href="#partner">{oa:.2f}</a></td></tr>')
    return '<table class="t"><tr><th>TIME</th><th>MATCH</th><th>HOME</th><th>DRAW</th><th>AWAY</th></tr>' + "".join(tr) + "</table>"


def ticker():
    out = []
    for c, h, a, b, aw in L["results"]:
        s = f"{a}–{b}" if a is not None else "n/r"
        out.append(f'<span>{esc(h)} <b>{s}</b> {esc(aw)}</span>')
    out.append('<span>&#9733; ROUND 6 SAT 17 OCT: TALAS v KARA-BULAK, 19:00, STATE HIPPODROME &#9733;</span><span>BOZTORGOY v KARAKOYUN: THE BIG ONE &#128293;</span><span>AIGYR GOLD 2-FOR-1 ON THE BEER DECK TILL 20:00</span>')
    return "".join(out)


def page(path, title, body, desc, depth, og=None, bodyclass=""):
    rel = "../" * depth
    canonical = SITE + ("" if path == "index.html" else path)
    out = (TEMPLATE.replace("{{title}}", esc(title)).replace("{{desc}}", esc(desc)).replace("{{canonical}}", canonical)
           .replace("{{og_image}}", SITE + (og or "img/og.jpg")).replace("{{bodyclass}}", bodyclass)
           .replace("{{ticker}}", ticker()).replace("{{body}}", body).replace("{{rel}}", rel))
    t = ROOT / path
    t.parent.mkdir(parents=True, exist_ok=True)
    t.write_text(out, encoding="utf-8")
    return canonical


def main():
    news = sorted((parse(p) for p in (ROOT / "content" / "news").glob("*.txt")), key=lambda n: n["date"], reverse=True)
    urls = []
    def cards(rel, items):
        return '<div class="cards">' + "".join(
            f'<div class="card"><a href="{rel}news/{n["slug"]}.html"><img src="{rel}img/{n["image"]}" alt="" loading="lazy"></a><div class="in"><span class="tag">{esc(n.get("tag", "NEWS"))}</span><h3><a href="{rel}news/{n["slug"]}.html">{esc(n["headline"])}</a></h3><p>{esc(n.get("summary", ""))}</p></div></div>'
            for n in items) + "</div>"
    for n in news:
        cm = ""
        if n.get("comments"):
            cm = '<div class="comments"><h3>COMMENTS (' + str(len(n["comments"].split(" || "))) + ')</h3>' + "".join(
                f'<div class="cm"><b>{esc(c.split("::")[0])}</b> <span class="up">&#9650; {c.split("::")[1]}</span><br>{esc(c.split("::")[2])}</div>' for c in n["comments"].split(" || ")) + "</div>"
        body = f'''<div class="grid"><div><article class="article"><span class="tag" style="color:var(--pink);font:700 12px Oswald">{esc(n.get("tag", "NEWS"))}</span><h1>{esc(n["headline"])}</h1>
<p class="meta">By {esc(n.get("byline", "Jarysh Staff"))} &middot; {nice(n["d"])}</p>
<figure><img src="../img/{n["image"]}" alt="{esc(n.get("caption", ""))}"><figcaption>{inline(n.get("caption", ""))}</figcaption></figure>
{paras(n["body"])}</article>{cm}</div>
<aside><div class="ad"><a href="../odds.html#partner"><img src="../img/ads/steppe-300.png" width="300" height="250" alt="Steppe Gaming"></a></div>
<div class="box"><h2>MORE NEWS</h2>{"".join(f'<p><a href="{o["slug"]}.html">{esc(o["headline"])}</a></p>' for o in news if o is not n)}</div>
<div class="ad"><a href="../style.html"><img src="../img/ads/hats-300.png" width="300" height="250" alt="Texas Hat House"></a></div></aside></div>'''
        urls.append((page(f'news/{n["slug"]}.html', f'{n["headline"]} | JARYSH', body, n.get("summary", ""), 1, og="img/" + n["image"]), n["date"]))
    urls.append((page("news/index.html", "News | JARYSH", "<h1>NEWS</h1>" + cards("../", news), "Ulak, horse games and Ulak Nights news from Jarysh.", 1), news[0]["date"]))

    for p in sorted((ROOT / "content" / "pages").glob("*.html")):
        m = parse(p)
        rep = {"{{isez_table}}": table(L["isez"]), "{{hl_table}}": table(L["highland"]), "{{results_isez}}": results("isez"),
               "{{results_hl}}": results("hl"), "{{odds_isez}}": odds("isez"), "{{odds_hl}}": odds("hl"),
               "{{news_cards}}": cards("", news[:6]), "{{next_date}}": nice(datetime.date.fromisoformat(L["next_date"]))}
        body = m["body"]
        for k, v in rep.items():
            body = body.replace(k, v)
        path = f"{p.stem}.html"
        c = page(path, m["headline"], body, m.get("dek", ""), 0, og=m.get("og"), bodyclass=m.get("bodyclass", ""))
        if p.stem != "404":
            urls.append((c, "2026-10-16"))
    sm = "\n".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}\n</urlset>\n', encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n", encoding="utf-8")
    print(f"built {len(urls)} pages")


if __name__ == "__main__":
    main()
