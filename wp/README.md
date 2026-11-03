# ekam vets on WordPress

Block-theme port of the static site. Nothing here touches the static site or the live server.

| Path | What it is |
|---|---|
| `theme/ekam-vets/` | Block theme. `assets/site.css` is a verbatim copy of `../style.css`; `assets/wp-compat.css` only re-targets selectors for block markup. |
| `convert.py` | Static pages to block markup: writes `content/en/*.html`, `content/hi/*.html`, `content/manifest.json`. Stdlib only. |
| `import.php` | Creates or updates pages, posts, menu, front page and permalinks from `content/en`. Safe to re-run. |
| `blueprint.json` | Playground setup: activate the theme, run `import.php`. |
| `plugin/ekam-site/` | What `build.py` did for the static site: 301s from every old `.html` URL (which also makes `send.php` work unchanged), Open Graph, `VeterinaryCare` JSON-LD, `/sitemap.xml` alias, thanks page out of the sitemap, no author archives. |

## Local preview (WordPress Playground, no PHP needed)

```bash
cd /Users/sg/Documents/Claude/Projects/ekam-vets-site
python3 wp/convert.py            # only after editing the static pages
npx @wp-playground/cli@latest server --port=9400 \
  --mount=./wp/theme/ekam-vets:/wordpress/wp-content/themes/ekam-vets \
  --mount=./wp:/wordpress/ekam-src \
  --blueprint=./wp/blueprint.json --login
```

Open http://127.0.0.1:9400 for the site and http://127.0.0.1:9400/wp-admin/ for the editor (already logged in).
Each start is a fresh install, so the blueprint imports the content again.

## On a real WordPress site

1. Upload `theme/ekam-vets` to `wp-content/themes/` and activate it. Upload `plugin/ekam-site` to `wp-content/plugins/` and activate it.
2. `wp eval-file wp/import.php --user=<admin>` from a folder that holds `import.php` and `content/`.
3. Copy `send.php` to the WordPress root as is. The plugin 301s its `/thanks.html` and `/visit.html?e=1` targets to `/thanks/` and `/visit/?e=1`.

## URLs

`index.html` becomes `/`, `rates.html` becomes `/rates/`, `blog-heat-stroke.html` becomes `/blog-heat-stroke/`.
Hindi pages link to `/hi/<slug>/`. `blog` is the posts page. The Query Loop in `templates/home.html` draws the cards.

## Hindi

`content/hi` is converted and passes block validation. It is not imported yet.
Once the translation plugin is chosen: add `'hi'` to `EKAM_LANGS` in `import.php`, link translations in `ekam_after_upsert()`,
and swap the menu item with class `lang-switcher-placeholder` for the plugin's language switcher.

## Editor notes

- Button styles Dark, Line and Ghost are in the block sidebar under Styles.
- The homeopathy "never used for" paragraphs and the indicative-pricing paragraph are locked. Only administrators can unlock them.
- Section icons, the booking form and the mobile tab bar are Custom HTML blocks.

## Rules the converter enforces

- Pages in `build.py`'s `HIDDEN` set are skipped, so `blog-vet-cost-jaipur` stays off WordPress too. One list, two sites.
- Theme image paths are written root-relative, so content imported on staging works unchanged on ekamvets.com.
- Run `python3 wp/convert.py` after every static edit. Content converted before 18 Oct 2026 carried prices and the comparison lines.
