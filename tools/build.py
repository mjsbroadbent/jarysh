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
BUILT = "2026-10-16"   # lastmod for the static pages; bump when they change
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


def page(path, title, body, desc, depth, og=None, bodyclass="", og_title=None, og_type="website", og_alt="",
         noindex=False, ld=None, article=None):
    rel = "../" * depth
    canonical = SITE + (path[:-len("index.html")] if path.endswith("index.html") else path)
    extra = ""
    if article:
        extra += (f'<meta property="article:published_time" content="{article["published"]}">\n'
                  f'<meta property="article:section" content="{esc(article["section"])}">\n')
    if ld:
        graph = {"@context": "https://schema.org", "@graph": ld}
        extra += '<script type="application/ld+json">' + json.dumps(graph, ensure_ascii=False).replace("</", "<\\/") + "</script>\n"
    out = (TEMPLATE.replace("{{title}}", esc(title)).replace("{{desc}}", esc(desc)).replace("{{canonical}}", canonical)
           .replace("{{og_title}}", esc(og_title or title)).replace("{{og_type}}", og_type).replace("{{og_alt}}", esc(og_alt or title))
           .replace("{{robots}}", '<meta name="robots" content="noindex, follow">\n' if noindex else "")
           .replace("{{extra_head}}", extra)
           .replace("{{og_image}}", SITE + (og or "img/og.jpg")).replace("{{bodyclass}}", bodyclass)
           .replace("{{ticker}}", ticker()).replace("{{body}}", body).replace("{{rel}}", rel))
    # sidebar and in-page ads load lazily; the header leaderboard does not
    out = re.sub(r'(<div class="ad"><a [^>]*><img )', r'\1loading="lazy" decoding="async" ', out)
    t = ROOT / path
    t.parent.mkdir(parents=True, exist_ok=True)
    t.write_text(out, encoding="utf-8")
    images = sorted(set(re.findall(r'<img[^>]+src="(?:\.\./)*(img/(?!ads/|src/|jarysh-logo|aigyr-wordmark|aigyr-logo)[^"]+\.jpg)"', out)))
    return canonical, images


TZ = "+06:00"
ORG_ID, SITE_ID = SITE + "#org", SITE + "#website"
ORG = {"@type": "Organization", "@id": ORG_ID, "name": "Jarysh Entertainment Group", "alternateName": "JARYSH", "url": SITE,
       "logo": {"@type": "ImageObject", "url": SITE + "img/jarysh-logo@2x.png", "width": 560, "height": 180},
       "address": {"@type": "PostalAddress", "streetAddress": "14 Hippodrome Avenue", "addressLocality": "Talas", "addressCountry": "Irad"},
       "founder": {"@id": SITE + "boss.html#nurik"}, "foundingDate": "2017"}
WEBSITE = {"@type": "WebSite", "@id": SITE_ID, "url": SITE, "name": "JARYSH", "alternateName": "Jarysh", "inLanguage": "en", "publisher": {"@id": ORG_ID}}
HIPPODROME = {"@type": "Place", "name": "Irad State Hippodrome", "address": {"@type": "PostalAddress", "streetAddress": "Hippodrome Avenue", "addressLocality": "Talas", "addressCountry": "Irad"}}


def crumbs(*items):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i, "name": n, "item": u} for i, (n, u) in enumerate(items, 1)]}


def fixtures_ld():
    out = []
    for c, h, a, venue, time, *_ in L["fixtures"]:
        out.append({"@type": "SportsEvent", "name": f"{h} v {a}", "sport": "Ulak tartysh (kok-boru)",
                    "startDate": f'{L["next_date"]}T{time}:00{TZ}', "eventStatus": "https://schema.org/EventScheduled",
                    "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                    "location": {"@type": "Place", "name": venue},
                    "homeTeam": {"@type": "SportsTeam", "name": h}, "awayTeam": {"@type": "SportsTeam", "name": a},
                    "superEvent": {"@type": "SportsEvent", "name": "National Ulak Tartysh League 2026, Round 6"}})
    return out


def page_ld(stem, m, canonical):
    home = ("Home", SITE)
    name = m.get("title", m["headline"]).split(" | ")[0]
    if stem == "index":
        return [WEBSITE, ORG]
    ld = [crumbs(home, (name, canonical)),
          {"@type": "WebPage", "@id": canonical, "url": canonical, "name": m.get("title", m["headline"]), "description": m.get("dek", ""),
           "isPartOf": {"@id": SITE_ID}, "inLanguage": "en"}]
    if stem == "ulak-nights":
        nd = L["next_date"]
        ld.append({"@type": "Event", "name": "Aigyr Ulak Nights: Talas v Kara-Bulak", "startDate": f"{nd}T17:30:00{TZ}",
                   "endDate": f"{nd}T23:59:00{TZ}", "eventStatus": "https://schema.org/EventScheduled",
                   "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode", "location": HIPPODROME,
                   "image": [SITE + "img/crowd.jpg", SITE + "img/hero.jpg"], "organizer": {"@id": ORG_ID},
                   "description": "Round 6 of the National Ulak Tartysh League under the lights, the Aigyr Beer Deck and the afterparty. Gates 17:30, first game 19:00.",
                   "performer": [{"@type": "SportsTeam", "name": "Talas"}, {"@type": "SportsTeam", "name": "Kara-Bulak"}]})
    elif stem in ("scores", "odds"):
        ld += fixtures_ld()
    elif stem == "aigyr":
        ld.append({"@type": "Brewery", "name": "Aigyr Brewing Company", "url": canonical, "logo": SITE + "img/aigyr-crest.png",
                   "image": SITE + "img/aigyr-can.jpg", "foundingDate": "2009", "slogan": "Ride Hard. Drink Aigyr.",
                   "address": {"@type": "PostalAddress", "addressLocality": "Kara-Bulak", "addressCountry": "Irad"},
                   "brand": {"@type": "Brand", "name": "Aigyr", "logo": SITE + "img/aigyr-crest.png"}})
    elif stem == "boss":
        ld.append({"@type": "ProfilePage", "url": canonical, "mainEntity": {"@type": "Person", "@id": SITE + "boss.html#nurik",
                   "name": "Nurlan Baisalov", "alternateName": ["Nurik", "Nurik Jackpot"], "birthDate": "1979",
                   "birthPlace": {"@type": "Place", "name": "Talas"}, "jobTitle": "Founder and CEO", "worksFor": {"@id": ORG_ID},
                   "image": SITE + "img/ceo.jpg"}})
    elif stem == "girls":
        ld.append({"@type": "ImageGallery", "name": "Jarysh Girls and Aigyr Girls", "url": canonical, "about": "Promotional models of Aigyr Ulak Nights"})
    elif stem == "steppe":
        ld.append({"@type": "TouristTrip", "name": "Jarysh Steppe Safari", "description": "Day trip from Talas to the Highland Conference games with a guide, kymyz tasting and a yurt lunch.",
                   "provider": {"@id": ORG_ID}, "offers": {"@type": "Offer", "price": "185", "priceCurrency": "USD", "url": canonical}})
    return ld


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
<aside><div class="ad"><a href="../odds.html#partner"><img src="../img/ads/steppe-300.webp" width="300" height="250" alt="Steppe Gaming"></a></div>
<div class="box"><h2>MORE NEWS</h2>{"".join(f'<p><a href="{o["slug"]}.html">{esc(o["headline"])}</a></p>' for o in news if o is not n)}</div>
<div class="ad"><a href="../style.html"><img src="../img/ads/hats-300.webp" width="300" height="250" alt="Texas Hat House"></a></div><div class="ad"><a href="../go.html"><img src="../img/ads/pinkfilly-300.webp" width="300" height="250" alt="The Pink Filly gentlemen\'s club"></a></div></aside></div>'''
        url = SITE + f'news/{n["slug"]}.html'
        stitle = n.get("title", n["headline"])
        by = n.get("byline", "Jarysh Staff")
        author = {"@type": "Organization", "name": "Jarysh", "url": SITE} if by == "Jarysh Staff" else {"@type": "Person", "name": by}
        pub = f'{n["date"]}T09:00:00{TZ}'
        ld = [crumbs(("Home", SITE), ("News", SITE + "news/"), (stitle, url)),
              {"@type": "NewsArticle", "headline": stitle, "description": n.get("summary", ""), "image": [SITE + "img/" + n["image"]],
               "datePublished": pub, "dateModified": pub, "author": author, "publisher": {"@id": ORG_ID},
               "mainEntityOfPage": url, "articleSection": n.get("tag", "News"), "inLanguage": "en"}, ORG]
        full = f'{stitle} | JARYSH' if len(stitle) <= 51 else stitle
        c, imgs = page(f'news/{n["slug"]}.html', full, body, n.get("summary", ""), 1, og="img/" + n["image"],
                       og_title=stitle, og_type="article", og_alt=n.get("caption", stitle), ld=ld,
                       article={"published": pub, "section": n.get("tag", "News")})
        urls.append((c, n["date"], imgs))
    nl = [crumbs(("Home", SITE), ("News", SITE + "news/")),
          {"@type": "CollectionPage", "url": SITE + "news/", "name": "Jarysh News", "isPartOf": {"@id": SITE_ID},
           "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i, "url": SITE + f'news/{n["slug"]}.html'} for i, n in enumerate(news, 1)]}}]
    c, imgs = page("news/index.html", "Ulak News, Ulak Nights & Gossip | JARYSH", "<h1>NEWS</h1>" + cards("../", news),
                   "Ulak results, Ulak Nights news, the Boss, the girls and the gossip from Jarysh, Talas.", 1, ld=nl)
    urls.append((c.replace("news/index.html", "news/"), news[0]["date"], imgs))

    for p in sorted((ROOT / "content" / "pages").glob("*.html")):
        m = parse(p)
        rep = {"{{isez_table}}": table(L["isez"]), "{{hl_table}}": table(L["highland"]), "{{results_isez}}": results("isez"),
               "{{results_hl}}": results("hl"), "{{odds_isez}}": odds("isez"), "{{odds_hl}}": odds("hl"),
               "{{news_cards}}": cards("", news[:6]), "{{next_date}}": nice(datetime.date.fromisoformat(L["next_date"]))}
        body = m["body"]
        for k, v in rep.items():
            body = body.replace(k, v)
        path = f"{p.stem}.html"
        noindex = m.get("noindex") == "yes"
        canonical = SITE + ("" if path == "index.html" else path)
        title = m.get("title", m["headline"])
        c, imgs = page(path, title, body, m.get("dek", ""), 0, og=m.get("og"), bodyclass=m.get("bodyclass", ""),
                       og_title=m["headline"] if p.stem != "index" else title, noindex=noindex,
                       ld=None if noindex else page_ld(p.stem, m, canonical))
        if not noindex:
            urls.append((c, BUILT, imgs))
    def entry(u, d, imgs):
        im = "".join(f"<image:image><image:loc>{SITE}{i}</image:loc></image:image>" for i in imgs)
        return f"  <url><loc>{u}</loc><lastmod>{d}</lastmod>{im}</url>"
    sm = "\n".join(entry(*x) for x in urls)
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                                      f'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n{sm}\n</urlset>\n', encoding="utf-8")
    (ROOT / "robots.txt").write_text("User-agent: *\nAllow: /\n# build sources, not pages\nDisallow: /tools/\nDisallow: /content/\nDisallow: /img/src/\n\n"
                                     f"Sitemap: {SITE}sitemap.xml\n", encoding="utf-8")
    print(f"built {len(urls)} pages")


if __name__ == "__main__":
    main()
