#!/usr/bin/env python3
"""Builds jarysh.com.   python3 tools/build.py

data/ulak-2026.json   the season: conferences and grounds, records from rounds 1-4 ("before"), every round from 5
                      with its matches (score once the sheet is in, odds for the coming round, optional "boost")
content/pages/*.html  pages: "key: value" header, blank line, HTML body with placeholders
content/news/*.txt    news: header (headline, date, image, tag, summary), blank line, paragraphs
Placeholders (body and header): {{isez_table}} {{hl_table}} {{results_isez}} {{results_hl}} {{odds_isez}} {{odds_hl}}
{{news_cards}} {{round_done}} {{done_date}} {{next_round}} {{next_date}} {{byes_isez}} {{byes_hl}} {{late_hl}}
{{hero_match}} {{hero_time}} {{nights_card}} {{boost}} {{playoff}} {{rel}}
The latest round is the last one with a score in; the next round is the first one from today (Irad Time) with none.
"""
import html, json, re, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://jarysh.com/"
BUILT = "2026-10-16"   # lastmod for the static pages; bump when they change
U = json.loads((ROOT / "data" / "ulak-2026.json").read_text(encoding="utf-8"))
TODAY = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=6)).date().isoformat()   # Irad Time
LR = None
for _r in U["rounds"]:
    if any(_m.get("score") is not None for _m in _r["matches"]):
        LR = _r
NR = next((_r for _r in U["rounds"] if _r["date"] >= TODAY and all(_m.get("score") is None for _m in _r["matches"])), None)
HIPPO = "State Hippodrome"
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


def standings(conf):
    """Records from rounds 1-4 plus every score in since: [name, P, W, D, L, GF, GA]."""
    rows = {t["name"]: [t["name"], *U["before"][conf].get(t["name"], [0] * 6)] for t in U["conferences"][conf]["teams"]}
    for r in U["rounds"]:
        for m in r["matches"]:
            if m["conf"] != conf or m.get("score") is None:
                continue
            for t, f, g in ((m["home"], *m["score"]), (m["away"], m["score"][1], m["score"][0])):
                x = rows[t]; x[1] += 1; x[5] += f; x[6] += g; x[2 if f > g else 3 if f == g else 4] += 1
    return list(rows.values())


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
    for m in (LR["matches"] if LR else []):
        if m["conf"] != conf:
            continue
        a, b = m["score"] if m.get("score") is not None else (None, None)
        sc = f'<span class="sc">{a} – {b}</span>' if a is not None else '<span class="nr">NOT RECEIVED</span>'
        li.append(f'<li><span class="h">{esc(m["home"])}</span>{sc}<span>{esc(m["away"])}</span></li>')
    return '<ul class="res">' + "".join(li) + "</ul>"


def byes(rnd, conf):
    if not rnd:
        return ""
    playing = {t for m in rnd["matches"] if m["conf"] == conf for t in (m["home"], m["away"])}
    if not playing:
        return ""
    out = [t["name"] for t in U["conferences"][conf]["teams"] if t["name"] not in playing]
    return ("Bye: " + ", ".join(out) + ".") if out else ""


def late_note(conf):
    n = sum(1 for m in (LR["matches"] if LR else []) if m["conf"] == conf and m.get("score") is None)
    if not n:
        return ""
    words = {1: "One result", 2: "Two results", 3: "Three results"}.get(n, f"{n} results")
    return f" {words} not yet received from the Directorate's match commissioners. Phone lines in the Moiynkum are, as usual, a disaster."


def odds(conf):
    tr = []
    for m in (NR["matches"] if NR else []):
        if m["conf"] != conf:
            continue
        o = m.get("odds") or [None] * 3
        cell = lambda x: f'<td><a class="odds" href="#partner">{x:.2f}</a></td>' if x else "<td>&ndash;</td>"  # noqa: E731
        tr.append(f'<tr><td>{m["time"]}</td><td>{esc(m["home"])} <span style="color:var(--muted)">v</span> {esc(m["away"])}<br><span class="tiny">{esc(m["venue"])}</span></td>'
                  + "".join(cell(x) for x in o) + "</tr>")
    if not tr:
        return '<p class="tiny">No league games this weekend. The play-off is at the State Hippodrome in December.</p>'
    return '<table class="t"><tr><th>TIME</th><th>MATCH</th><th>HOME</th><th>DRAW</th><th>AWAY</th></tr>' + "".join(tr) + "</table>"


def playoff():
    po = U.get("playoff") or {}
    if not po.get("rounds"):
        return ""
    names = {"isez": "ISEZ", "hl": "Highland"}
    def side(m, k):
        if m.get(k):
            return esc(m[k])
        kind, v = (m.get("seed_" + k) or "?:?").split(":")
        if kind == "win":
            return f'<span style="color:var(--muted)">Winner SF{v[-1]}</span>'
        return f'<span style="color:var(--muted)">{names.get(kind, kind)} {v}{ {"1": "st", "2": "nd"}.get(v, "th") }</span>'
    li = []
    for r in po["rounds"]:
        li.append(f'<li style="display:block;list-style:none;margin:10px 0 4px;border:0"><b>{esc(r["name"].upper())}</b> <span class="tiny">&middot; Saturday {nice(datetime.date.fromisoformat(r["date"]))}</span></li>')
        for m in r["matches"]:
            sc = (f'<span class="sc">{m["score"][0]} – {m["score"][1]}</span>' + ('<span class="tiny"> GG</span>' if m.get("golden_goal") else "")
                  if m.get("score") is not None else f'<span class="sc" style="background:none;color:var(--muted)">{m["time"]}</span>')
            li.append(f'<li><span class="h">{side(m, "home")}</span>{sc}<span>{side(m, "away")}</span></li>')
    return (f'<div class="box"><h2>PLAY-OFF: {esc(po.get("venue", "State Hippodrome").upper())}</h2>'
            f'<p class="tiny">{esc(po.get("note", ""))} GG = golden goal.</p><ul class="res">' + "".join(li) + "</ul></div>")


def hippodrome(rnd):
    return sorted([m for m in (rnd["matches"] if rnd else []) if m["venue"].startswith(HIPPO)], key=lambda m: m["time"])


def hero():
    hm = hippodrome(NR)
    if hm:
        return f'{hm[0]["home"]} v {hm[0]["away"]}', hm[0]["time"]
    if NR:
        m = NR["matches"][0]
        return f'{m["home"]} v {m["away"]}', m["time"]
    return "The play-off", "19:00"


def nights_card():
    hm = hippodrome(NR)
    if not hm:
        return "<p>No league game at the Hippodrome this Saturday. The bars are open anyway.</p>"
    games = " &middot; ".join((f'<b>{m["time"]} {esc(m["home"])} v {esc(m["away"])}</b>' if i == 0 else f'{m["time"]} {esc(m["home"])} v {esc(m["away"])}')
                              for i, m in enumerate(hm))
    return (f"<p>{games} &middot; Half-time: the <b>Aigyr Fan Pull</b> (amateurs grab a 20-kilo leather goat on foot, winner gets a crate) "
            "&middot; 22:30 live on the stage &middot; 00:00 buses to <b>Club Doran</b>.</p>")


def boost():
    b = NR and NR.get("boost")
    if not b:
        return ""
    q = f'<p>"{esc(b["quote"])}" <b>Nurik</b></p>' if b.get("quote") else ""
    return (f'<div class="boost"><span class="kick" style="background:var(--pink);color:#fff;font:700 12px Oswald;padding:2px 8px">&#128293; THE NURIK BOOST OF THE WEEK</span>'
            f'<h2 style="margin-top:8px">{esc(b["home"].upper())} v {esc(b["away"].upper())}: {esc(b["pick"])}</h2><span class="was">was {b["was"]:.2f}</span> &nbsp; <span class="now">NOW {b["now"]:.2f}</span>{q}</div>')


def short_date(d):
    d = datetime.date.fromisoformat(d)
    return f"{'MON TUE WED THU FRI SAT SUN'.split()[d.weekday()]} {d.day} {MONTHS[d.month - 1][:3].upper()}"


def ticker():
    out = []
    for m in (LR["matches"] if LR else []):
        s = f'{m["score"][0]}–{m["score"][1]}' if m.get("score") is not None else "n/r"
        out.append(f'<span>{esc(m["home"])} <b>{s}</b> {esc(m["away"])}</span>')
    if NR:
        hm, tm = hero()
        out.append(f'<span>&#9733; ROUND {NR["round"]} {short_date(NR["date"])}: {esc(" v ".join(x.upper() for x in hm.split(" v ")))}, {tm}, STATE HIPPODROME &#9733;</span>')
        if NR.get("boost"):
            out.append(f'<span>{esc(NR["boost"]["home"].upper())} v {esc(NR["boost"]["away"].upper())}: THE NURIK BOOST &#128293;</span>')
    out.append('<span>AIGYR GOLD 2-FOR-1 ON THE BEER DECK TILL 20:00</span>')
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
           .replace("{{ticker}}", ticker()).replace("{{ticker_label}}", f'ROUND {LR["round"]} &#9679; FT' if LR else "ULAK").replace("{{body}}", body).replace("{{rel}}", rel))
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
    for m in (NR["matches"] if NR else []):
        h, a = m["home"], m["away"]
        out.append({"@type": "SportsEvent", "name": f"{h} v {a}", "sport": "Ulak tartysh (kok-boru)",
                    "startDate": f'{NR["date"]}T{m["time"]}:00{TZ}', "eventStatus": "https://schema.org/EventScheduled",
                    "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                    "location": {"@type": "Place", "name": m["venue"]},
                    "homeTeam": {"@type": "SportsTeam", "name": h}, "awayTeam": {"@type": "SportsTeam", "name": a},
                    "superEvent": {"@type": "SportsEvent", "name": f"National Ulak Tartysh League {U['season']}, Round {NR['round']}"}})
    return out


def page_ld(stem, m, canonical):
    home = ("Home", SITE)
    name = m.get("title", m["headline"]).split(" | ")[0]
    if stem == "index":
        return [WEBSITE, ORG]
    ld = [crumbs(home, (name, canonical)),
          {"@type": "WebPage", "@id": canonical, "url": canonical, "name": m.get("title", m["headline"]), "description": m.get("dek", ""),
           "isPartOf": {"@id": SITE_ID}, "inLanguage": "en"}]
    if stem == "ulak-nights" and NR:
        nd, (hm, _t) = NR["date"], hero()
        teams_ = hm.split(" v ")
        ld.append({"@type": "Event", "name": f"Aigyr Ulak Nights: {hm}", "startDate": f"{nd}T17:30:00{TZ}",
                   "endDate": f"{nd}T23:59:00{TZ}", "eventStatus": "https://schema.org/EventScheduled",
                   "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode", "location": HIPPODROME,
                   "image": [SITE + "img/crowd.jpg", SITE + "img/hero.jpg"], "organizer": {"@id": ORG_ID},
                   "description": f"Round {NR['round']} of the National Ulak Tartysh League under the lights, the Aigyr Beer Deck and the afterparty. Gates 17:30, first game 19:00.",
                   "performer": [{"@type": "SportsTeam", "name": t} for t in teams_]})
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
        hm, ht = hero()
        rep = {"{{isez_table}}": table(standings("isez")), "{{hl_table}}": table(standings("hl")), "{{results_isez}}": results("isez"),
               "{{results_hl}}": results("hl"), "{{odds_isez}}": odds("isez"), "{{odds_hl}}": odds("hl"),
               "{{news_cards}}": cards("", news[:6]),
               "{{round_done}}": str(LR["round"]) if LR else "", "{{done_date}}": nice(datetime.date.fromisoformat(LR["date"])).rsplit(" ", 1)[0] if LR else "",
               "{{next_round}}": str(NR["round"]) if NR else "PLAY-OFF", "{{next_date}}": nice(datetime.date.fromisoformat(NR["date"])) if NR else "December",
               "{{byes_isez}}": byes(LR, "isez"), "{{byes_hl}}": byes(LR, "hl"), "{{late_hl}}": late_note("hl"),
               "{{hero_match}}": esc(hm), "{{hero_time}}": ht, "{{nights_card}}": nights_card(), "{{boost}}": boost(),
               "{{playoff}}": playoff()}
        body = m["body"]
        for k, v in rep.items():
            body = body.replace(k, v)
            for f in ("title", "headline", "dek"):
                if f in m:
                    m[f] = m[f].replace(k, re.sub(r"<[^>]+>", "", v))
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
