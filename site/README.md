# Website

The public website. Every figure on it is computed by the engine; nothing is typed by hand.

1. `scripts/export_site_example.py` runs the engine on an illustrative mine and writes `site/data/example.json`.
2. `site/build.py` reads the export and writes the static site to `site/_site/`.
3. `.github/workflows/pages.yml` does both on every push to main that touches the engine, the priors or the site, checks the built page against the export (`tests/test_site.py`), and publishes it to GitHub Pages.

To build locally:

```
uv run python scripts/export_site_example.py
uv run python site/build.py
python -m http.server --directory site/_site 8000
```

`site/src/home.css` and `site/src/home.js` are the page's styles and script. The script only looks values up in the export and draws. The Inter font in `site/assets/fonts/` is under the SIL Open Font License (`OFL.txt`). See ADR 0056.
