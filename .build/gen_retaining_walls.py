#!/usr/bin/env python3
"""gen_retaining_walls.py - fill the missing Retaining Walls x suburb pages.

Retaining Walls is 14,800/mo of demand and was the emptiest row on Select Civil's
coverage matrix: 7 of 13 target suburbs built, and the six missing ones are the
whole Geelong side (Geelong, Highton, Lara, Drysdale, Torquay, Bellarine).

Method: clone retaining-walls-ocean-grove.html, which is the CURRENT shape of these
pages (og:image dimensions + alt, the full @graph with FAQPage, compiled-Tailwind
head). Deliberately NOT built off _build_city_lps.py - that script has drifted from
the live pages and regenerating from it would roll them back. The older
retaining-walls-armstrong-creek.html is on the earlier, thinner shape, so it is not
a valid base either.

URL note: the site 308-redirects /page.html to /page, and the committed pages
already use extension-less canonicals and hrefs. Keep it that way.

Idempotent: re-running overwrites the generated pages and skips sitemap URLs that
are already listed. Output: retaining-walls-<slug>.html
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://selectcivilgroup.com.au"
TEMPLATE = os.path.join(ROOT, "retaining-walls-ocean-grove.html")
SITEMAP = os.path.join(ROOT, "sitemap.xml")
LASTMOD = "2026-08-28"

# Everything that is Ocean-Grove-specific in the template and has to be replaced
# rather than blanket-substituted. Ground conditions are the real differentiator
# between these pages: a wall on Torquay sand is not a wall on Highton clay.
SUBURBS = [
    {
        "slug": "geelong", "name": "Geelong",
        "region": "Geelong Region",
        "area_line": "the Geelong region",
        "geo": ("-38.1499", "144.3617"),
        "hero": "Engineered concrete retaining walls for Geelong homeowners and builders. Sloping blocks levelled, garden edges held back, structural walls built to engineering specs. Quotes back within 24 hours.",
        "intro1": "Geelong is our home base, and it is a city built across a fall. The older suburbs step down toward Corio Bay and the Barwon River, so level changes are the norm rather than the exception, and a lot of renovation and infill work runs into a retaining problem before it runs into anything else.",
        "intro2": "Select Civil Group is based here, which means we are on Geelong sites constantly and we know what the ground does. Whether it is a single garden wall on a Newtown block, a structural wall holding a building platform, or a tiered solution on a steeper site, we build to engineering specs with the right product for the load and the soil.",
        "nearby": "Geelong is where we are based. Most weeks we are working across the city and out through the surrounding suburbs and the Bellarine.",
        "faq_area": "Yes. Geelong, Newtown, Belmont, Highton, Grovedale, Waurn Ponds, Corio, Lara, Leopold, Drysdale, the Bellarine and the Surf Coast are all within our regular service area. Geelong is our base, so we are here every week.",
        "areas": ["Geelong", "Newtown", "Belmont", "Highton", "Grovedale", "Waurn Ponds",
                  "Corio", "Lara", "Leopold", "Drysdale", "Bellarine", "Torquay"],
        "meta_region": "the Geelong region",
    },
    {
        "slug": "highton", "name": "Highton",
        "region": "Geelong Region",
        "area_line": "the Geelong region",
        "geo": ("-38.1750", "144.3230"),
        "hero": "Engineered concrete retaining walls for Highton homeowners and builders. Sloping blocks levelled, split-level sites held, structural walls built to engineering specs. Quotes back within 24 hours.",
        "intro1": "Highton sits on the rise above the Barwon River, and it is the most genuinely sloping suburb in Geelong. Split-level houses, stepped driveways and terraced back yards are everywhere here, which means a retaining wall is often not a nice-to-have but the thing that makes the block usable at all.",
        "intro2": "Select Civil Group is based a few minutes away in Geelong and works across Highton and Wandana Heights regularly. On this kind of ground the wall height, the drainage behind it and the engineering are the whole job, so we build to specs rather than to a rule of thumb.",
        "nearby": "Highton is one of the steepest parts of Geelong. Most weeks we are working across the surrounding suburbs and down through the river flats.",
        "faq_area": "Yes. Highton, Wandana Heights, Newtown, Belmont, Grovedale, Waurn Ponds, Geelong, Ceres, Barrabool and the surrounding area are all within our regular service area. We are based minutes away in Geelong.",
        "areas": ["Highton", "Wandana Heights", "Newtown", "Belmont", "Grovedale",
                  "Waurn Ponds", "Geelong", "Ceres", "Barrabool", "Leopold", "Bellarine", "Torquay"],
        "meta_region": "Geelong",
    },
    {
        "slug": "lara", "name": "Lara",
        "region": "Geelong Region",
        "area_line": "the Geelong region",
        "geo": ("-38.0230", "144.4060"),
        "hero": "Engineered concrete retaining walls for Lara homeowners and builders. Estate blocks levelled, garden edges held back, structural walls built to engineering specs. Quotes back within 24 hours.",
        "intro1": "Lara sits on the flat volcanic plain between Geelong and the You Yangs, and it has been growing fast on new estate land. The ground is mostly level, so the retaining work here tends to come from what the developer did rather than what nature did: pad levels between neighbouring lots, batters left from the estate earthworks, and garden terracing on blocks that were cut and filled before anyone moved in.",
        "intro2": "Select Civil Group works Lara out of our Geelong base. On estate ground the important thing is knowing where the fill stops, because a wall founded in loose fill is a wall that moves, so we build to the engineer's design with drainage behind it.",
        "nearby": "Lara sits between Geelong and the You Yangs. Most weeks we are working across the northern suburbs and back through the city.",
        "faq_area": "Yes. Lara, Corio, Norlane, North Shore, Little River, Anakie, Geelong and the northern suburbs are all within our regular service area. Lara is a short run from our Geelong base.",
        "areas": ["Lara", "Corio", "Norlane", "North Shore", "Little River", "Anakie",
                  "Geelong", "Newtown", "Bellarine", "Leopold", "Highton", "Torquay"],
        "meta_region": "the Geelong region",
    },
    {
        "slug": "drysdale", "name": "Drysdale",
        "region": "Bellarine Peninsula",
        "area_line": "the Bellarine",
        "geo": ("-38.1740", "144.5640"),
        "hero": "Engineered concrete retaining walls for Drysdale homeowners and builders. Sloping rural blocks levelled, estate lots held, structural walls built to engineering specs. Quotes back within 24 hours.",
        "intro1": "Drysdale sits on the rise in the middle of the Bellarine, looking down toward Corio Bay, so the blocks here genuinely fall. It is a mix of established township streets, new estate releases and larger semi-rural lots, and on all three the level change usually has to be dealt with before anything gets built.",
        "intro2": "Select Civil Group is based in Geelong and works Drysdale, Clifton Springs and Curlewis regularly. On a sloping block the wall and the cut are the same decision, so we set the levels and the wall position together rather than building whatever fits after the dig.",
        "nearby": "Drysdale sits on the high ground in the middle of the Bellarine. Most weeks we are working across the surrounding towns and the peninsula.",
        "faq_area": "Yes. Drysdale, Clifton Springs, Curlewis, Portarlington, Leopold, Ocean Grove, Point Lonsdale, Queenscliff, the Bellarine and Geelong are all within our regular service area. We are on the Bellarine most weeks.",
        "areas": ["Drysdale", "Clifton Springs", "Curlewis", "Portarlington", "Leopold",
                  "Ocean Grove", "Point Lonsdale", "Queenscliff", "Bellarine", "Geelong", "Highton", "Barwon Heads"],
        "meta_region": "the Bellarine",
    },
    {
        "slug": "torquay", "name": "Torquay",
        "region": "Surf Coast",
        "area_line": "the Surf Coast",
        "geo": ("-38.3320", "144.3220"),
        "hero": "Engineered concrete retaining walls for Torquay homeowners and builders. Coastal blocks levelled, dune slopes held, structural walls built to engineering specs. Quotes back within 24 hours.",
        "intro1": "Torquay is the Surf Coast's biggest town and one of the fastest-growing in the region, with new estates pushing north and established streets running down toward the beach. The ground here is sandy, which digs easily and holds a face badly, so the drainage and the footing detail matter more on a Torquay wall than they would inland.",
        "intro2": "Select Civil Group works Torquay and Jan Juc out of our Geelong base. Sandy coastal ground and salt exposure both change what a wall needs, so we build to the engineer's design with the right product for the conditions rather than the cheapest one that fits.",
        "nearby": "Torquay is the biggest town on the Surf Coast. Most weeks we are working across the coastal strip and back through Geelong.",
        "faq_area": "Yes. Torquay, Jan Juc, Bellbrae, Breamlea, Connewarre, Armstrong Creek, Mount Duneed, Grovedale, Geelong and the Surf Coast are all within our regular service area.",
        "areas": ["Torquay", "Jan Juc", "Bellbrae", "Breamlea", "Connewarre", "Armstrong Creek",
                  "Mount Duneed", "Grovedale", "Geelong", "Highton", "Barwon Heads", "Ocean Grove"],
        "meta_region": "the Surf Coast",
    },
    {
        "slug": "bellarine", "name": "Bellarine",
        "region": "Bellarine Peninsula",
        "area_line": "the Bellarine Peninsula",
        "geo": ("-38.1800", "144.6000"),
        "hero": "Engineered concrete retaining walls across the Bellarine Peninsula. Coastal and rural blocks levelled, garden edges held back, structural walls built to engineering specs. Quotes back within 24 hours.",
        "intro1": "The Bellarine covers a lot of different ground in a small area: sandy coastal blocks at Ocean Grove and Point Lonsdale, the rise through Drysdale and Wallington, rural lots out toward Portarlington, and the bay frontages around Clifton Springs and Curlewis. What a retaining wall needs changes across all of it.",
        "intro2": "Select Civil Group is based in Geelong and is on the peninsula most weeks. Rather than treating the Bellarine as one job type, we look at what the block is actually made of, because sand, clay and bay-side ground each want a different footing and a different drainage detail behind the wall.",
        "nearby": "The Bellarine covers coastal, rural and bayside ground. Most weeks we are working somewhere across the peninsula.",
        "faq_area": "Yes. Ocean Grove, Barwon Heads, Point Lonsdale, Queenscliff, Portarlington, Drysdale, Clifton Springs, Curlewis, Leopold, Wallington, Marcus Hill and Connewarre are all within our regular service area. We are on the Bellarine most weeks.",
        "areas": ["Ocean Grove", "Barwon Heads", "Point Lonsdale", "Queenscliff", "Portarlington",
                  "Drysdale", "Clifton Springs", "Curlewis", "Leopold", "Wallington", "Bellarine", "Geelong"],
        "meta_region": "the Bellarine",
    },
]

# The Ocean Grove strings each field replaces.
OG = {
    "name": "Ocean Grove",
    "slug": "ocean-grove",
    "region": "Bellarine Peninsula",
    "geo": ("-38.2667", "144.5333"),
    "meta": "Concrete retaining walls in Ocean Grove and across the Bellarine. Garden, structural and tiered walls built to engineering specs. Free quotes within 24 hours.",
    "tw_desc": "Concrete retaining walls in Ocean Grove and across the Bellarine Peninsula region.",
    "hero": "Engineered concrete retaining walls for Ocean Grove homeowners and builders. Coastal blocks levelled, garden edges held back, structural walls built to engineering specs. Quotes back within 24 hours.",
    "intro1": "Ocean Grove is the Bellarine's largest town, a mix of established coastal streets and growing new estates on sandy, low-lying ground near the Barwon River and the surf coast. New residential development is active across the town, and whether you are working on an established block or a new estate lot, level changes need to be managed before building can start.",
    "intro2": "Select Civil Group is based in Geelong and works across Ocean Grove and the Bellarine regularly. Whether you need a single garden wall on a sandy coastal block, a structural wall holding back a building platform, or a multi-tier solution on a larger site, we deliver to engineering specs with the right product for the load and the soil conditions.",
    "nearby": "Ocean Grove is the Bellarine's biggest coastal town. Most weeks we are working across the surrounding suburbs and the broader peninsula.",
    "faq_area": "Yes. Ocean Grove, Barwon Heads, Wallington, Marcus Hill, Connewarre, Point Lonsdale, Leopold, Drysdale, Curlewis, Clifton Springs, Bellarine and Geelong are all within our regular service area. We are on the Bellarine most weeks.",
    "areas": ["Ocean Grove", "Barwon Heads", "Wallington", "Marcus Hill", "Connewarre",
              "Point Lonsdale", "Leopold", "Drysdale", "Curlewis", "Clifton Springs", "Bellarine", "Geelong"],
    "intro_h2": "Retaining Walls, Built for Ocean Grove's Terrain",
}


def rep(html, old, new, label, count=None):
    n = html.count(old)
    if n == 0:
        raise SystemExit(f"[{label}] anchor not found:\n  {old[:110]}...")
    if count is not None and n != count:
        raise SystemExit(f"[{label}] expected {count} occurrences, found {n}")
    return html.replace(old, new)


def build_page(sub):
    html = open(TEMPLATE, encoding="utf-8").read()
    name, slug = sub["name"], sub["slug"]
    art = "an" if name[0].lower() in "aeiou" else "a"

    meta = (f"Concrete retaining walls in {name} and across {sub['meta_region']}. "
            "Garden, structural and tiered walls built to engineering specs. Free quotes within 24 hours.")
    if not 120 <= len(meta) <= 170:
        raise SystemExit(f"[{slug}] meta description is {len(meta)} chars (need 120-170)")
    title = f"Retaining Walls {name} - Concrete Retaining Walls | Select Civil Group"

    # Step 1: lift every block we are replacing out behind a sentinel, so the blanket
    # name swap in step 2 cannot touch the new copy. The Bellarine page legitimately
    # names Ocean Grove as one of its towns; without this it gets swapped out.
    slots = {
        "META": (OG["meta"], meta),
        "TWDESC": (OG["tw_desc"], f"Concrete retaining walls in {name} and across {sub['meta_region']}."),
        "HERO": (OG["hero"], sub["hero"]),
        "INTRO1": (OG["intro1"], sub["intro1"]),
        "INTRO2": (OG["intro2"], sub["intro2"]),
        "NEARBY": (OG["nearby"], sub["nearby"]),
        "FAQAREA": (OG["faq_area"], sub["faq_area"]),
        "INTROH2": (OG["intro_h2"], f"Retaining Walls, Built for {name}'s Terrain"),
        "TITLE": ("<title>Retaining Walls Ocean Grove - Concrete Retaining Walls | Select Civil Group</title>",
                  f"<title>{title}</title>"),
        "EYEBROW": ('<p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-3">Bellarine Peninsula</p>',
                    f'<p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-3">{sub["region"]}</p>'),
        "PLACENAME": ('<meta name="geo.placename" content="Ocean Grove">',
                      f'<meta name="geo.placename" content="{name}">'),
    }
    for key, (old_text, _) in slots.items():
        if old_text not in html:
            raise SystemExit(f"[{slug}] anchor missing for {key}:\n  {old_text[:110]}...")
        html = html.replace(old_text, f"\x00{key}\x00")

    # areaServed list + the visible nearby-suburb chips
    for og_area, new_area in zip(OG["areas"], sub["areas"]):
        html = html.replace(f'{{ "@type": "City", "name": "{og_area}" }}',
                            f'{{ "@type": "City", "name": "{new_area}" }}')

    html = html.replace(f'content="{OG["geo"][0]};{OG["geo"][1]}"', f'content="{sub["geo"][0]};{sub["geo"][1]}"')
    html = html.replace(f'content="{OG["geo"][0]}, {OG["geo"][1]}"', f'content="{sub["geo"][0]}, {sub["geo"][1]}"')
    html = html.replace(f"{BASE}/retaining-walls-{OG['slug']}", f"{BASE}/retaining-walls-{slug}")

    # Step 2: blanket-swap the remaining page furniture (CTA labels, alt text,
    # headings). Article first, so "an Ocean Grove Quote" does not become
    # "an Geelong Quote".
    html = html.replace("an Ocean Grove", f"{art} {name}")
    html = html.replace("Ocean Grove", name)

    # Step 3: put the new copy back.
    for key, (_, new_text) in slots.items():
        html = html.replace(f"\x00{key}\x00", new_text)
    if "\x00" in html:
        raise SystemExit(f"[{slug}] unreplaced sentinel left in output")

    out = os.path.join(ROOT, f"retaining-walls-{slug}.html")
    open(out, "w", encoding="utf-8").write(html)
    return out


def patch_sitemap():
    xml = open(SITEMAP, encoding="utf-8").read()
    anchor = f"    <loc>{BASE}/retaining-walls-ocean-grove</loc>"
    if anchor not in xml:
        raise SystemExit("sitemap: retaining-walls-ocean-grove entry not found")
    end = xml.index("</url>", xml.index(anchor)) + len("</url>\n")
    block, added = "", []
    for s in SUBURBS:
        loc = f"{BASE}/retaining-walls-{s['slug']}"
        if f"<loc>{loc}</loc>" in xml:
            continue
        added.append(s["slug"])
        block += (f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{LASTMOD}</lastmod>\n"
                  f"    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n")
    if not block:
        return "sitemap: all suburb URLs already listed"
    open(SITEMAP, "w", encoding="utf-8").write(xml[:end] + block + xml[end:])
    return f"sitemap: added {len(added)} URLs"


def patch_hub():
    """Link the new pages from the Retaining Walls service page.

    The hub's service-area grid mixes linked <a> tiles (suburbs that have a page) with
    dead <div> tiles (suburbs that do not). Convert the matching <div> to a link rather
    than appending a second tile, or the suburb shows up twice in the grid.
    """
    hub = os.path.join(ROOT, "retaining-walls.html")
    html = open(hub, encoding="utf-8").read()
    TILE = 'bg-white border border-black/10 px-4 py-3 text-center'
    linked, converted, appended = [], [], []

    for sub in SUBURBS:
        name, slug = sub["name"], sub["slug"]
        if f'href="retaining-walls-{slug}"' in html:
            linked.append(slug)
            continue
        dead = (f'<div class="{TILE}"><p class="text-gray-700 text-sm font-semibold">{name}</p></div>')
        live = (f'<a href="retaining-walls-{slug}" class="block {TILE} hover:border-brand-500/40" '
                f'style="transition: border-color 0.2s ease;">'
                f'<p class="text-gray-700 text-sm font-semibold">{name}</p></a>')
        if dead in html:
            html = html.replace(dead, live, 1)
            converted.append(slug)
        else:
            m = re.search(r'<a href="retaining-walls-[a-z-]+"[^>]*>.*?</a>', html, re.S)
            if not m:
                return "hub: no tile pattern found, add links by hand"
            html = html[:m.end()] + "\n          " + live + html[m.end():]
            appended.append(slug)

    open(hub, "w", encoding="utf-8").write(html)
    return (f"hub: {len(converted)} dead tiles linked ({', '.join(converted) or '-'}), "
            f"{len(appended)} appended ({', '.join(appended) or '-'}), "
            f"{len(linked)} already linked")


def main():
    for sub in SUBURBS:
        print("  built", os.path.basename(build_page(sub)))
    print(patch_sitemap())
    print(patch_hub())
    print(f"\nDone. {len(SUBURBS)} pages. Idempotent.")


if __name__ == "__main__":
    main()
