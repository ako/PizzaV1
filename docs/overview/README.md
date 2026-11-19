# Build overview deck

```bash
python3 docs/overview/collect.py              # evidence: data/{lane0,m1..m4,summary}.json (add --no-build to skip mxbuild)
python3 docs/overview/deck.py                 # layout: build-overview.html + frames.json
node docs/overview/render.js /tmp/render      # one PNG per frame, to check the layout
node docs/overview/capture.js                 # fresh phone screenshots (app running on :8080)
```

`PRD_DIR=<package-lite>` on `collect.py` refreshes `data/prd-epics.json` from the PRD's epic tables.
`kit/` holds the sketch-deck skill's Pen & Marker kit and page template. After a rebuild,
republish `build-overview.html` to the same artifact. Only if frames moved, write
`frames.json` to the deck's `frames` collection.
