# Select Civil Group suburb LP sources

Each `*.json` here is one suburb. `python3 .build/lp_render.py` (from the site root) renders one
page per priority service for that suburb (retaining-walls, concrete-driveway, earthworks,
site-cuts) matching the live city-LP template, and refreshes the `<!-- LP -->` block in sitemap.xml.

Do NOT hand-edit generated HTML or re-run the old `_build_city_lps.py`. Edit the JSON (or the
shared chrome/copy in `.build/lp_render.py`) and re-run.

Hard rules: NO em/en dashes anywhere (auto-normalised). Unique `intro_context` per suburb so
pages are not doorway clones. Target-plan + rollout order: `CRM/clients/Select Civil Group/lp-target-plan.md`.

## Schema

```json
{
  "name": "Armstrong Creek",
  "slug": "armstrong-creek",
  "postcode": "3217",
  "lat": "-38.2380",
  "lng": "144.3230",
  "lastmod": "2026-07-22",
  "region_eyebrow": "Geelong Growth Corridor",   // hero pill
  "region_name": "Geelong",                       // prose: "across <region_name>"
  "region_short": "the Surf Coast",               // meta + service-area third label
  "catchment": ["Armstrong Creek", "Charlemont", "..."],  // chips + areaServed + FAQ list (~12)
  "intro_context": "One unique paragraph about the suburb (terrain, growth, soil, character).",
  "chips_lede": "One sentence intro for the 'Around <suburb>' band.",
  "services": ["retaining-walls", "concrete-driveway", "earthworks", "site-cuts"]  // optional; omit = all 4
}
```

For partial suburbs (Leopold, Highton, Drysdale, etc.) set `services` to only the missing ones
so existing pages are not overwritten. Order/priority: see the target plan.
