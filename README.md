# jarysh.com

Jarysh, "Irad's #1 horse games portal": ulak scores and tables, Jarysh Odds, Aigyr Ulak Nights tickets, Jarysh Girls, Asphalt Cowboy style, Steppe Safari. Run by Jarysh Entertainment Group (CEO Nurlan "Nurik Jackpot" Baisalov), sponsored by Aigyr Lager. Part of the Irad worldbuilding project.

- `python3 tools/build.py` builds every page, `sitemap.xml` and `robots.txt` from `data/ulak-2026.json` (the season) and `content/` (pages in `content/pages/`, news in `content/news/`).
- **Ulak data** (`data/ulak-2026.json`, also read by other sites at jarysh.com/data/ulak-2026.json, so it is the one place ulak results live): both conferences with each team's ground; `before`, each team's record from rounds 1-4 [P, W, D, L, GF, GA]; `rounds` from round 5, every match with `conf` (`isez`/`hl`), `home`, `away`, `venue`, `time`, `score` (`null` until the sheet is in: a past match with `null` shows as NOT RECEIVED), `odds` [home, draw, away] for the coming round, and an optional `boost` (the Nurik Boost: `home`, `away`, `pick`, `was`, `now`, optional `quote`). The tables, results, byes, odds, the ticker, the home hero and the Ulak Nights card are all built from it: the latest round is the last with a score in, the next round the first from today (Irad Time) with none. Scores, odds and the boost are filled in automatically every morning at about 03:10 Irad Time and the site rebuilt (commits by "Web desk", "Results: 17 October 2026"); a score typed in by hand first is never changed. Rounds run to 11 (ISEZ, 21 Nov) and 13 (Highland, 5 Dec); the December play-off has no fixtures yet (`playoff`).
- Brand art, all redrawable from code (source photos and traced silhouettes live in `img/src/`):
  - `python3 tools/make_logo.py`: the animated Jarysh logo (`img/jarysh-logo.svg`) and PNG fallbacks.
  - `python3 tools/make_aigyr.py`: the Aigyr crest, wordmark and lockup.
  - `python3 tools/make_art.py`: the background tile and the labelled Aigyr can.
  - `python3 tools/render_ads.py [name]`: renders the HTML/CSS ads in `tools/ads/` to animated WebP in `img/ads/`.
  - `python3 tools/trace.py in.png out.svg`: traces a black silhouette to an SVG path.
- Brand and ad art uses fonts installed on the build machine (Inter Display, TeX Gyre Bonum / Heros Cn / Chorus); the pages themselves load Anton, Oswald and Roboto Condensed from Google Fonts.
- Photos were generated with Flux Krea; fake text was removed by hand.
- Served by GitHub Pages from `main` at jarysh.com (`CNAME`).
