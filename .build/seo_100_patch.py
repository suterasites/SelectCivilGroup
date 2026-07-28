#!/usr/bin/env python3
"""seo_100_patch.py - idempotent on-page SEO patcher for the Select Civil Group site.

Brings the sitemap pages to a clean pass on Apps/sutera-seo/checklist.py. Safe to
re-run. Compiled-Tailwind site (styles.css), so no new utility classes are added -
only a <header> element is introduced and text attributes are edited. The LP build
script has drifted from the live pages, so this edits the committed .html directly
and never regenerates.

Fixes:
  - a11y_semantic: wrap the fixed site <nav> in a <header> on every page (pages had
    <main> + <footer>, only <header> was missing). Applied site-wide for nav parity.
  - trim 18 over-long titles + extend the privacy title into 40-65 chars
  - rewrite 4 over-long meta descriptions (home/services/concrete/earthworks) <=170
  - projects: mirror the homepage LocalBusiness identity node in (it had none)

Homepage breadcrumb is deliberately left as the only residual warn; the pooled
25-page score rounds to 100.
"""

import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TITLES = {
    "index.html": "Geelong Civil Contractor & Earthworks | Select Civil Group",
    "concrete-services.html": "Concrete Services Geelong | Driveways | Select Civil Group",
    "earthworks-excavation.html": "Earthworks & Excavation Geelong | Select Civil Group",
    "contact.html": "Contact Select Civil Group | Geelong Civil Contractor",
    "excavation-drysdale.html": "Excavation & Site Cuts Drysdale | Select Civil Group",
    "retaining-walls-leopold.html": "Engineered Retaining Walls Leopold | Select Civil Group",
    "concrete-driveway-ocean-grove.html": "Concrete Driveways Ocean Grove | Select Civil Group",
    "civil-contractor-torquay.html": "Civil Contractor Torquay - Earthworks | Select Civil Group",
    "excavation-bellarine.html": "Excavation Bellarine Peninsula | Select Civil Group",
    "concrete-driveway-highton.html": "Concrete Driveways Highton | Select Civil Group",
    "civil-works-lara.html": "Civil Contractor Lara - Earthworks | Select Civil Group",
    "privacy.html": "Privacy Policy | Select Civil Group, Geelong",
    "concrete-raft-slabs.html": "Concrete Raft Slabs Geelong | Select Civil Group",
    "factory-tilt-panels.html": "Factory Tilt Panels Geelong | Select Civil Group",
    "concrete-seating.html": "Concrete Seating Geelong | Select Civil Group",
    "concrete-bench-drops.html": "Concrete Bench Drops Geelong | Select Civil Group",
    "earthworks.html": "Earthworks Geelong & Bellarine | Select Civil Group",
    "site-cuts.html": "Site Cuts Geelong & Bellarine | Select Civil Group",
    "detail-excavation.html": "Detail Excavation Geelong | Select Civil Group",
}

METAS = {
    "index.html": "Select Civil Group delivers earthworks, concrete driveways, retaining walls and site cuts across Geelong, the Bellarine Peninsula and Torquay. Free quotes.",
    "services.html": "Retaining walls, concrete driveways, raft slabs, earthworks and site cuts across Geelong, the Bellarine Peninsula and Torquay. Free quotes from Select Civil.",
    "concrete-services.html": "Concrete driveways, retaining walls, raft slabs, paving and tilt panels across Geelong and the Bellarine Peninsula. Free quotes from Select Civil Group.",
    "earthworks-excavation.html": "Earthworks, site cuts, detail excavation and land clearing across Geelong and the Bellarine Peninsula. Civil earthworks by Select Civil Group. Free quotes.",
}


def business_node():
    h = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try:
            d = json.loads(m.group(1))
        except Exception:
            continue
        for node in (d.get("@graph", [d]) if isinstance(d, dict) else [d]):
            t = node.get("@type", "") if isinstance(node, dict) else ""
            tl = t if isinstance(t, list) else [t]
            if any(x in ("LocalBusiness", "Organization") or str(x).endswith("Business") for x in tl):
                node = dict(node)
                node.pop("@context", None)
                return node
    return None


def patch(path, biz):
    fn = os.path.basename(path)
    html = open(path, encoding="utf-8").read()
    orig = html
    did = []

    if fn in TITLES:
        h2 = re.sub(r"<title>.*?</title>", "<title>" + TITLES[fn] + "</title>",
                    html, count=1, flags=re.S)
        if h2 != html:
            html = h2
            did.append(f"title({len(TITLES[fn])})")

    if fn in METAS:
        new = METAS[fn]
        h2 = re.sub(r'(<meta name="description" content=")[^"]*(")',
                    lambda m: m.group(1) + new + m.group(2), html, count=1)
        if h2 != html:
            html = h2
            did.append(f"desc({len(new)})")

    # <header> landmark: wrap the fixed site nav
    if "<header" not in html:
        m = re.search(r'<nav class="fixed top-0', html)
        if m:
            close = html.find("</nav>", m.start())
            if close != -1:
                end = close + len("</nav>")
                html = html[:m.start()] + "<header>" + html[m.start():end] + "</header>" + html[end:]
                did.append("header")

    # projects: inject the homepage identity node (it carries no business schema)
    if fn == "projects.html" and biz and '"LocalBusiness"' not in html and '"Organization"' not in html:
        block = ('<script type="application/ld+json">\n'
                 + json.dumps({"@context": "https://schema.org", **biz}, ensure_ascii=False)
                 + "\n</script>\n")
        html = html.replace("</head>", block + "</head>", 1)
        did.append("org-schema")

    if html != orig:
        open(path, "w", encoding="utf-8").write(html)
    return did


def main():
    biz = business_node()
    print(f"business node: {'found' if biz else 'MISSING'}\n")
    for path in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        out = patch(path, biz)
        if out:
            print(f"  {os.path.basename(path):40s} {', '.join(out)}")
    print("\nDone. Idempotent.")


if __name__ == "__main__":
    main()
