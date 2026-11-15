# LTX2.5-SVS — Demo page

Static demo site for *LTX2.5-SVS: Joint Singing-Voice and Video Generation from Text and Music
Conditions via Three-Stage Distillation*. No build step, no framework — plain HTML/CSS/JS,
served directly by GitHub Pages.

**Live:** https://liyunlongaaa.github.io/ltx2-svs-demo/

## Layout

```
site/
├── index.html              # the whole page
├── assets/
│   ├── data/videos.js      # generated clip manifest (window.DEMO_VIDEOS)
│   ├── videos/             # web copies of the demo clips
│   ├── posters/            # cover frame per clip
│   ├── figures/            # paper figures rendered to PNG
│   └── ltx2-svs-source.zip # LaTeX source download
├── tools/build_media.py    # regenerates videos.js, videos/, posters/
└── .nojekyll
```

## Editing

**Swap or reorder clips.** Drop new `.mp4` files into `../videos/<lang>/<5s|10s|60s>/`,
then rebuild:

```sh
python3 tools/build_media.py --force
```

The script copies each clip (stream copy, `+faststart` so playback starts before the
file finishes downloading), extracts a 512×512 poster at ~30% of the clip, and rewrites
`assets/data/videos.js`. Clips are ordered alphabetically inside each language/length
group; the path shown on the page is `videos/<lang>/<group>/<n> - <duration>`.

**Edit text.** Everything is in `index.html`. The galleries are rendered at load time
from `assets/data/videos.js`; the filters (language × length) are client-side only.

**Figures.** `assets/figures/*.png` were rendered from the paper's PDFs at 3× with
`tools/render_pdf.swift` (macOS PDFKit, no extra dependencies):

```sh
swift tools/render_pdf.swift ../docs/figures/singing_pipeline_editable_v27.pdf \
      assets/figures/pipeline.png 3
swift tools/render_pdf.swift ../docs/figures/fig_error_recycling_comparison.pdf \
      assets/figures/error_recycling.png 3
```

## Run locally

```sh
cd site
python3 -m http.server 8765
# open http://localhost:8765
```

Video playback needs a server (opening `index.html` as `file://` works in some
browsers but not all). The page falls back to a muted preview if the browser's
autoplay policy blocks audio.

## Deploy

The site is a plain folder, so any static host works. For GitHub Pages:

```sh
git init
git add .
git commit -m "Add LTX2.5-SVS demo page"
git branch -M main
git remote add origin https://github.com/liyunlongaaa/ltx2-svs-demo.git
git push -u origin main
```

Then in the repo: **Settings → Pages → Source: Deploy from a branch → `main` / `/ (root)`**.
The first build takes about a minute.

> **Video weight.** The clips are ~78 MB in total, most of it the minute-long
> performances. That is fine for GitHub Pages (1 GB site limit, 100 MB per file),
> but the repo will be slow to clone. If that matters, move `assets/videos/` and
> `assets/posters/` to a release asset or object storage and point the paths in
> `assets/data/videos.js` there.
