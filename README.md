# jarysh.com

Jarysh, "Irad's #1 horse games portal": ulak scores and tables, Jarysh Odds, Aigyr Ulak Nights tickets, Jarysh Girls, Asphalt Cowboy style, Steppe Safari. Run by Jarysh Entertainment Group (CEO Nurlan "Nurik Jackpot" Baisalov), sponsored by Aigyr Lager. Part of the Irad worldbuilding project.

- `python3 tools/build.py` builds every page, `sitemap.xml` and `robots.txt` from `content/` (league tables and fixtures in `content/league.json`, pages in `content/pages/`, news in `content/news/`).
- `python3 tools/make_art.py` redraws the logo and the ad banners (`img/ads/`). It needs the source photos in `img/src/`.
- Photos were generated with Flux Krea; fake text was removed by hand.
- Served by GitHub Pages from `main` at jarysh.com (`CNAME`).
