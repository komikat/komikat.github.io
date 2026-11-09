# akshitkr.com

A small static notebook: Markdown notes, one Python script, plain HTML, and minimal CSS.

```sh
uv run --locked build.py
python3 -m http.server 8000 --directory dist
```

Edit `site/home.html`, `site/page.html`, and `site/style.css` for the homepage,
shared HTML, and styles. Posts stay in `_posts/` with their existing YAML metadata.
Selected work lives in `_data/projects.yml`. Files in `public/` are copied unchanged
to the site root, including images, the William demo, PDFs, and standalone pages.
The build preserves existing dated URLs, raw HTML in posts, and the Atom feed.

The homepage shows the five newest entries; `/notes/` has the full archive.
Short snippets and longer pieces use the same format. Existing
`hide_from_home: true` entries remain unlisted. For something published elsewhere,
add `external_url` and `source` to its metadata, with a short summary as the body.
It links directly to the original from the lists and feed, without a duplicate page.

`site/poem.html` holds saved samples from William. `public/poem.js` picks one when
the homepage opens; without JavaScript, the first sample is shown. The model only
loads on its own page.

Only Markdown and PyYAML are required at build time; `build.py.lock` pins both.
Jekyll, Ruby, Sass, and a frontend framework are not needed.

Inter is served locally from `public/assets/fonts/` under the included SIL Open
Font License. The theme follows the system preference until the light/dark
button is used; `public/theme.js` remembers that choice in local storage.

Deploy static files to Cloudflare Workers (no server code):

```sh
npx wrangler@4.159.0 login
npx wrangler@4.159.0 deploy
```

Wrangler runs the build before uploading `dist/` to `akshitkr.com`.
Generated output and local Wrangler credentials/state are not tracked.

## GitHub Actions

Pull requests build the site, validate the Wrangler configuration, and check
local links and the Atom feed. Pushes to `master` run the same checks, then deploy
to Cloudflare. The workflow can also be run manually; only `master` deploys.

In the repository's **Settings → Secrets and variables → Actions**, configure:

- Secret `CLOUDFARE_API_TOKEN`: a Cloudflare **Edit Cloudflare Workers** token,
  restricted to the deployment account and the `akshitkr.com` zone. It needs
  Workers Scripts edit, Workers Routes edit, and Zone read permissions for this
  static site and its custom domain. A Wrangler browser login or a token with
  only Zone Settings edit permission cannot be used for deployment. This is the
  existing GitHub secret name; the workflow maps it to Wrangler's
  `CLOUDFLARE_API_TOKEN` environment variable.
- Variable `CLOUDFLARE_ACCOUNT_ID`: the account that owns the Worker.

Run the page checks locally with `python3 scripts/check_site.py` after building.
The deployment credentials are passed only to the production deployment step.
