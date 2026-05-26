# Tejas Anilkumar — Portfolio

Personal portfolio site. Three pages: home, work, CV.

Pure HTML / CSS / JS. No build step. Deployed as a static site.

## Local preview

```bash
python3 -m http.server 8081
```

Then open <http://localhost:8081>.

## Updating the work-page decks

The work page renders each PDF deck as a stack of JPG slides served inline
by the in-page viewer. To refresh slides after editing a deck:

1. Drop the updated PDF into `assets/work/decks/` (keep the same filename:
   `01-hero-xoom.pdf`, `02-tata-red-dark.pdf`, etc.)
2. Run:

   ```bash
   python3 scripts/render-decks.py
   ```

   Optional flags: `--zoom 2.4` (sharper, larger files), `--quality 85`
   (slightly higher JPG quality).

3. Commit and push — the new slides + `manifest.json` get picked up
   automatically by the front-end.

`assets/work/decks/` is gitignored. Source PDFs stay local; only the
rendered slides ship.

## Deployment

Static-only. Works on any static host:

- Cloudflare Pages (recommended for performance, especially in India)
- GitHub Pages
- Netlify, Vercel — also fine

Build settings: framework none, output directory `/`.
