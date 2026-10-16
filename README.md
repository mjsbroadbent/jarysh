# jarysh.com

Jarysh, "Irad's #1 horse games portal": ulak scores and tables, Jarysh Odds, Aigyr Ulak Nights tickets, Jarysh Girls, Asphalt Cowboy style, Steppe Safari. Run by Jarysh Entertainment Group (CEO Nurlan "Nurik Jackpot" Baisalov), sponsored by Aigyr Lager. Part of the Irad worldbuilding project.

- `python3 tools/build.py` builds every page, `sitemap.xml` and `robots.txt` from `content/` (league tables and fixtures in `content/league.json`, pages in `content/pages/`, news in `content/news/`).
- Brand art, all redrawable from code (source photos and traced silhouettes live in `img/src/`):
  - `python3 tools/make_logo.py`: the animated Jarysh logo (`img/jarysh-logo.svg`) and PNG fallbacks.
  - `python3 tools/make_aigyr.py`: the Aigyr crest, wordmark and lockup.
  - `python3 tools/make_art.py`: the background tile and the labelled Aigyr can.
  - `python3 tools/render_ads.py [name]`: renders the HTML/CSS ads in `tools/ads/` to animated WebP in `img/ads/`.
  - `python3 tools/trace.py in.png out.svg`: traces a black silhouette to an SVG path.
- Brand and ad art uses fonts installed on the build machine (Inter Display, TeX Gyre Bonum / Heros Cn / Chorus); the pages themselves load Anton, Oswald and Roboto Condensed from Google Fonts.
- Photos were generated with Flux Krea; fake text was removed by hand.
- Served by GitHub Pages from `main` at jarysh.com (`CNAME`).
