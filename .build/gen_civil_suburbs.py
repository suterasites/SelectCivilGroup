#!/usr/bin/env python3
"""
Generate "Civil Contractor <Suburb>" landing pages for Select Civil Group.

Clones the committed civil-contractor-torquay.html (the site's stale
_build_city_lps.py must NOT be run - it no longer matches the live LPs, see
CRM memory project_select_civil_build_script_drift). This script keeps the page
chrome (nav, footer, styles, scripts, hero/services/process/cta/contact shells)
byte-for-byte from Torquay and only swaps the localizable tokens, regenerating
the four high-differentiation blocks (JSON-LD @graph, intro, area chips, FAQ)
from hand-authored per-suburb copy so each page carries genuine local content,
not a name-swap (doorway/scaled-content safe).

Idempotent: rewrites the target pages + patches sitemap.xml + services.html hub.
Run:  python3 .build/gen_civil_suburbs.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "civil-contractor-torquay.html"

# ---- generic FAQ answers (genuinely the same everywhere) --------------------
A_COST = ("Civil costs depend on the scope. A standalone site cut sits at one end; "
          "a full package of site cut, earthworks, retaining and slab prep sits at the "
          "other. We quote each line itemised so you can see exactly where the money "
          "goes and where to trim if you need to.")
A_COORD = ("Yes. On most jobs we are the first trade on site, so we lock dates with "
           "whoever is running the program and hand over to the next trade ready to go. "
           "We can deal directly with the engineer if specs change mid-job.")
A_LEAD = ("Lead time varies with the season and our current run of work. We give you a "
          "programmed start date when we quote, and we hold to it. If something is "
          "genuinely urgent, ring us directly so we can talk through what is possible.")
A_INS = ("Yes. Select Civil Group carries full public liability insurance and workers "
         "compensation cover on every job. Certificates of currency are available on request.")

# ---- per-suburb data --------------------------------------------------------
SUBURBS = [
    {
        "slug": "geelong", "name": "Geelong", "postcode": "3220",
        "lat": "-38.149900", "lng": "144.361700",
        "eyebrow": "Central Geelong", "region_place": "Geelong",
        "region_the": "the wider region", "wider": "the surrounding suburbs",
        "region_poss": "Geelong's", "slope_area": "Geelong",
        "area_word": "Geelong suburbs",
        "partner_region": "Geelong and the Bellarine",
        "service_area": "Geelong, Bellarine, Surf Coast",
        "card_blurb": "Earthworks, concrete, site cuts &amp; retaining",
        "intro_h2": "Civil Contracting Across Geelong",
        "intro_p1": ("Geelong is the second-largest city in Victoria and it is still growing "
                     "hard. Infill builds through the established suburbs, new estates pushing "
                     "out at Armstrong Creek and Fyansford, warehouse and commercial work "
                     "through the northern industrial belt, and a constant run of renovations "
                     "across Newtown, Belmont and Highton. Civil work in the city has to deal "
                     "with everything from reactive clay through to the basalt that runs under "
                     "a lot of the western suburbs."),
        "intro_p2": ("Select Civil Group is based in the Geelong region and works right across "
                     "the city. From a single site cut on a suburban block through to "
                     "multi-stage development earthworks, we bring the right machinery, the "
                     "right operators, and the local knowledge to keep the program moving for "
                     "whoever is running the build."),
        "around_lede": ("Geelong is the centre of everything we do. Most weeks we are working "
                        "across the city and out to the Bellarine and Surf Coast too."),
        "terrain_desc": "Geelong blocks range from flat suburban pads to sloping falls",
        "neighbours": ["Newtown", "Belmont", "Highton", "Grovedale", "Waurn Ponds", "Corio", "Bell Post Hill"],
        "chips": ["Geelong", "Newtown", "Belmont", "Highton", "Grovedale", "Waurn Ponds",
                  "Bell Post Hill", "Herne Hill", "Hamlyn Heights", "Corio", "Norlane", "Geelong West"],
    },
    {
        "slug": "ocean-grove", "name": "Ocean Grove", "postcode": "3226",
        "lat": "-38.266700", "lng": "144.533300",
        "eyebrow": "Bellarine Peninsula", "region_place": "Bellarine Peninsula",
        "region_the": "the Bellarine", "wider": "the Bellarine",
        "region_poss": "the Bellarine's", "slope_area": "Bellarine",
        "area_word": "Bellarine towns",
        "partner_region": "the Bellarine and the Geelong region",
        "service_area": "Ocean Grove, Bellarine, Geelong",
        "card_blurb": "Earthworks, concrete &amp; site cuts for coastal builds",
        "intro_h2": "Civil Contracting Across the Bellarine",
        "intro_p1": ("Ocean Grove is the largest town on the Bellarine and it has been growing "
                     "steadily for years. New estates rolling out on the northern edge towards "
                     "Grubb Road, infill through the older beachside streets, and a steady run "
                     "of knockdown-rebuilds close to the river and the surf. Civil work here "
                     "has to handle sandy coastal soils, high water tables in the low-lying "
                     "pockets, and tight access on the original holiday-block subdivisions."),
        "intro_p2": ("Select Civil Group is based in the Geelong region and works the Bellarine "
                     "weekly. From a single site cut on a residential lot through to multi-stage "
                     "estate earthworks, we bring the right machinery, the right operators, and "
                     "the experience to keep the program moving for whoever is running the build."),
        "around_lede": ("Ocean Grove anchors our Bellarine work. Most weeks we are across the "
                        "surrounding coastal towns and back through the Geelong region too."),
        "terrain_desc": "Bellarine blocks vary from flat coastal pads to gently sloping rises",
        "neighbours": ["Barwon Heads", "Wallington", "Marcus Hill", "Collendina", "Point Lonsdale", "Drysdale", "Leopold"],
        "chips": ["Ocean Grove", "Barwon Heads", "Wallington", "Marcus Hill", "Collendina",
                  "Point Lonsdale", "Queenscliff", "Drysdale", "Leopold", "Clifton Springs",
                  "Connewarre", "Geelong"],
    },
    {
        "slug": "barwon-heads", "name": "Barwon Heads", "postcode": "3227",
        "lat": "-38.273900", "lng": "144.489400",
        "eyebrow": "Bellarine Peninsula", "region_place": "Bellarine Peninsula",
        "region_the": "the Bellarine", "wider": "the Bellarine",
        "region_poss": "the Bellarine's", "slope_area": "Bellarine",
        "area_word": "Bellarine towns",
        "partner_region": "the Bellarine and the Geelong region",
        "service_area": "Barwon Heads, Bellarine, Geelong",
        "card_blurb": "Earthworks, concrete &amp; site cuts",
        "intro_h2": "Civil Contracting in Barwon Heads",
        "intro_p1": ("Barwon Heads sits at the mouth of the Barwon River, and demand for "
                     "building here has not let up. Premium knockdown-rebuilds close to the "
                     "river and Thirteenth Beach, infill through the village, and new work "
                     "spilling across the bridge from Ocean Grove. Civil work in the town deals "
                     "with sandy soils, coastal wind exposure, and tight heritage-sensitive "
                     "streets where access and spoil management matter."),
        "intro_p2": ("Select Civil Group is based in the Geelong region and works the coast "
                     "weekly. From a single site cut on a residential lot through to a full "
                     "package of earthworks, retaining and slab prep, we bring the right "
                     "machinery, the right operators, and the experience to keep the program "
                     "moving for whoever is running the build."),
        "around_lede": ("Barwon Heads sits at the heart of our coastal catchment. Most weeks we "
                        "are working the surrounding Bellarine towns and back into Geelong."),
        "terrain_desc": "Barwon Heads blocks vary from flat riverside pads to gently sloping rises",
        "neighbours": ["Ocean Grove", "Thirteenth Beach", "Breamlea", "Connewarre", "Armstrong Creek", "Wallington", "Marcus Hill"],
        "chips": ["Barwon Heads", "Ocean Grove", "Thirteenth Beach", "Breamlea", "Connewarre",
                  "Wallington", "Marcus Hill", "Armstrong Creek", "Mount Duneed", "Drysdale",
                  "Leopold", "Geelong"],
    },
    {
        "slug": "point-lonsdale", "name": "Point Lonsdale", "postcode": "3225",
        "lat": "-38.289400", "lng": "144.611900",
        "eyebrow": "Bellarine Peninsula", "region_place": "Bellarine Peninsula",
        "region_the": "the Bellarine", "wider": "the Bellarine",
        "region_poss": "the Bellarine's", "slope_area": "Bellarine",
        "area_word": "Bellarine towns",
        "partner_region": "the Bellarine and the Geelong region",
        "service_area": "Point Lonsdale, Bellarine, Geelong",
        "card_blurb": "Earthworks, concrete &amp; site cuts",
        "intro_h2": "Civil Contracting in Point Lonsdale",
        "intro_p1": ("Point Lonsdale sits on the tip of the Bellarine looking across the Rip to "
                     "Queenscliff. It is a mix of long-held family holiday homes and a steady "
                     "stream of high-end rebuilds making the most of the ocean and bay "
                     "frontages. Civil work here contends with sandy coastal soils, exposed "
                     "sites near the front beach, and narrow older streets where getting "
                     "machinery and trucks in takes planning."),
        "intro_p2": ("Select Civil Group is based in the Geelong region and works the Bellarine "
                     "coast weekly. From a single site cut on a residential lot through to a "
                     "full earthworks, retaining and slab package, we bring the right "
                     "machinery, the right operators, and the experience to keep the program "
                     "moving for whoever is running the build."),
        "around_lede": ("Point Lonsdale anchors the southern tip of our Bellarine catchment. We "
                        "work the surrounding coastal towns and back through Geelong most weeks."),
        "terrain_desc": "Point Lonsdale blocks vary from flat coastal pads to gently sloping rises",
        "neighbours": ["Queenscliff", "Ocean Grove", "Swan Bay", "St Leonards", "Bellarine", "Indented Head"],
        "chips": ["Point Lonsdale", "Queenscliff", "Ocean Grove", "Swan Bay", "St Leonards",
                  "Indented Head", "Drysdale", "Portarlington", "Leopold", "Barwon Heads",
                  "Bellarine", "Geelong"],
    },
    {
        "slug": "queenscliff", "name": "Queenscliff", "postcode": "3225",
        "lat": "-38.266700", "lng": "144.661400",
        "eyebrow": "Bellarine Peninsula", "region_place": "Bellarine Peninsula",
        "region_the": "the Bellarine", "wider": "the Bellarine",
        "region_poss": "the Bellarine's", "slope_area": "Bellarine",
        "area_word": "Bellarine towns",
        "partner_region": "the Bellarine and the Geelong region",
        "service_area": "Queenscliff, Bellarine, Geelong",
        "card_blurb": "Earthworks, concrete &amp; site cuts",
        "intro_h2": "Civil Contracting in Queenscliff",
        "intro_p1": ("Queenscliff is one of the most tightly held towns on the coast, a "
                     "historic borough where most work is careful renovation, extension and "
                     "rebuild rather than greenfield estate. Heritage overlays, narrow streets "
                     "and premium bay-front blocks mean civil work here has to be precise and "
                     "tidy. Sandy soils and a high water table close to the harbour add another "
                     "layer to the ground conditions."),
        "intro_p2": ("Select Civil Group is based in the Geelong region and works the Bellarine "
                     "coast weekly. From a single site cut through to a full earthworks, "
                     "retaining and slab package, we bring the right machinery, the right "
                     "operators, and the experience to keep the program moving for whoever is "
                     "running the build."),
        "around_lede": ("Queenscliff sits at the end of the Bellarine and well within our patch. "
                        "We work the surrounding towns and back through Geelong most weeks."),
        "terrain_desc": "Queenscliff blocks vary from flat bay-front pads to gently sloping rises",
        "neighbours": ["Point Lonsdale", "Swan Bay", "St Leonards", "Ocean Grove", "Bellarine", "Indented Head"],
        "chips": ["Queenscliff", "Point Lonsdale", "Swan Bay", "St Leonards", "Indented Head",
                  "Ocean Grove", "Portarlington", "Drysdale", "Bellarine", "Barwon Heads",
                  "Leopold", "Geelong"],
    },
    {
        "slug": "portarlington", "name": "Portarlington", "postcode": "3223",
        "lat": "-38.111900", "lng": "144.652800",
        "eyebrow": "Bellarine Peninsula", "region_place": "Bellarine Peninsula",
        "region_the": "the Bellarine", "wider": "the Bellarine",
        "region_poss": "the Bellarine's", "slope_area": "Bellarine",
        "area_word": "Bellarine towns",
        "partner_region": "the Bellarine and the Geelong region",
        "service_area": "Portarlington, Bellarine, Geelong",
        "card_blurb": "Earthworks, concrete &amp; site cuts",
        "intro_h2": "Civil Contracting in Portarlington",
        "intro_p1": ("Portarlington faces north across Port Phillip, and it has shifted from a "
                     "quiet fishing and holiday town into one of the busier growth pockets on "
                     "the Bellarine. New estates on the town's edge, a steady run of sea-change "
                     "rebuilds along the foreshore, and rural-residential blocks back towards "
                     "Drysdale. Civil work here handles a mix of flat coastal ground and the "
                     "gentle rise up off the bay, plus the sandy-to-clay soils common across "
                     "the northern Bellarine."),
        "intro_p2": ("Select Civil Group is based in the Geelong region and works the Bellarine "
                     "weekly. From a single site cut on a residential lot through to multi-stage "
                     "estate earthworks, we bring the right machinery, the right operators, and "
                     "the experience to keep the program moving for whoever is running the build."),
        "around_lede": ("Portarlington anchors the northern Bellarine for us. Most weeks we are "
                        "working the surrounding towns and back through the Geelong region."),
        "terrain_desc": "Portarlington blocks vary from flat foreshore ground to the gentle rise off the bay",
        "neighbours": ["Indented Head", "St Leonards", "Drysdale", "Clifton Springs", "Curlewis", "Bellarine", "Leopold"],
        "chips": ["Portarlington", "Indented Head", "St Leonards", "Drysdale", "Clifton Springs",
                  "Curlewis", "Bellarine", "Leopold", "Ocean Grove", "Point Lonsdale",
                  "Queenscliff", "Geelong"],
    },
    {
        "slug": "leopold", "name": "Leopold", "postcode": "3224",
        "lat": "-38.189700", "lng": "144.463600",
        "eyebrow": "Bellarine Gateway", "region_place": "Bellarine Peninsula",
        "region_the": "the Bellarine", "wider": "the Bellarine",
        "region_poss": "the Bellarine's", "slope_area": "Bellarine",
        "area_word": "Bellarine towns",
        "partner_region": "the Bellarine and the Geelong region",
        "service_area": "Leopold, Bellarine, Geelong",
        "card_blurb": "Earthworks, concrete &amp; site cuts for estate builds",
        "intro_h2": "Civil Contracting in Leopold",
        "intro_p1": ("Leopold is the gateway to the Bellarine and one of the fastest-growing "
                     "suburbs in the Geelong region. Large residential estates rolling out from "
                     "Gateway Sanctuary through to Estuary, commercial development along the "
                     "Bellarine Highway, and a steady stream of individual builds. Civil work "
                     "here deals mostly with reactive clay soils and the cut-and-fill that comes "
                     "with estate land, so getting levels and compaction right is everything."),
        "intro_p2": ("Select Civil Group is based in the Geelong region and works Leopold and "
                     "the wider Bellarine weekly. From a single site cut on a residential lot "
                     "through to multi-stage estate earthworks, we bring the right machinery, "
                     "the right operators, and the experience to keep the program moving for "
                     "whoever is running the build."),
        "around_lede": ("Leopold is the gateway between Geelong and the Bellarine, right in the "
                        "middle of our patch. We work the surrounding suburbs most weeks."),
        "terrain_desc": "Leopold estate blocks are mostly flat cut-and-fill on reactive clay",
        "neighbours": ["Newcomb", "Moolap", "Whittington", "Curlewis", "Drysdale", "Clifton Springs", "Wallington"],
        "chips": ["Leopold", "Newcomb", "Moolap", "Whittington", "Curlewis", "Drysdale",
                  "Clifton Springs", "Wallington", "Ocean Grove", "Portarlington", "Bellarine", "Geelong"],
    },
    {
        "slug": "drysdale", "name": "Drysdale", "postcode": "3222",
        "lat": "-38.174700", "lng": "144.563600",
        "eyebrow": "Central Bellarine", "region_place": "Bellarine Peninsula",
        "region_the": "the Bellarine", "wider": "the Bellarine",
        "region_poss": "the Bellarine's", "slope_area": "Bellarine",
        "area_word": "Bellarine towns",
        "partner_region": "the Bellarine and the Geelong region",
        "service_area": "Drysdale, Bellarine, Geelong",
        "card_blurb": "Earthworks, concrete &amp; site cuts",
        "intro_h2": "Civil Contracting in Drysdale",
        "intro_p1": ("Drysdale and neighbouring Clifton Springs sit at the centre of the "
                     "Bellarine, and the area has been one of the peninsula's steady growth "
                     "stories. New estates expanding around the town, established "
                     "rural-residential blocks on the outskirts, and a mix of residential and "
                     "light commercial work along the main road. Civil work here mostly means "
                     "reactive clay soils and estate cut-and-fill, where accurate levels and "
                     "proper compaction decide whether the slab sits right."),
        "intro_p2": ("Select Civil Group is based in the Geelong region and works the Bellarine "
                     "weekly. From a single site cut on a residential lot through to multi-stage "
                     "estate earthworks, we bring the right machinery, the right operators, and "
                     "the experience to keep the program moving for whoever is running the build."),
        "around_lede": ("Drysdale sits at the centre of the Bellarine and our peninsula work. We "
                        "are across the surrounding towns and back through Geelong most weeks."),
        "terrain_desc": "Drysdale blocks are mostly flat-to-gentle estate land on reactive clay",
        "neighbours": ["Clifton Springs", "Curlewis", "Portarlington", "Wallington", "Ocean Grove", "Leopold", "Bellarine"],
        "chips": ["Drysdale", "Clifton Springs", "Curlewis", "Portarlington", "Wallington",
                  "Marcus Hill", "Ocean Grove", "Leopold", "Bellarine", "Indented Head",
                  "St Leonards", "Geelong"],
    },
    {
        "slug": "highton", "name": "Highton", "postcode": "3216",
        "lat": "-38.174700", "lng": "144.320000",
        "eyebrow": "Geelong West", "region_place": "Geelong",
        "region_the": "western Geelong", "wider": "western Geelong",
        "region_poss": "Highton's", "slope_area": "Highton",
        "area_word": "Geelong suburbs",
        "partner_region": "Geelong and the Surf Coast",
        "service_area": "Highton, Geelong, Bellarine",
        "card_blurb": "Site cuts &amp; retaining for sloping blocks",
        "intro_h2": "Civil Contracting in Highton",
        "intro_p1": ("Highton sits on the rise above the Barwon River in Geelong's south-west, "
                     "spreading up into the Barrabool Hills. It is an established, sought-after "
                     "part of the city with a constant run of knockdown-rebuilds, extensions and "
                     "sloping-block builds. Civil work in Highton is defined by the fall of the "
                     "land, so retaining and site cuts on sloping blocks are the bread and "
                     "butter, often on reactive clay that needs careful drainage."),
        "intro_p2": ("Select Civil Group is based in the Geelong region and works Highton and "
                     "the western suburbs regularly. From a single retaining wall on a sloping "
                     "block through to a full site cut and slab, we bring the right machinery, "
                     "the right operators, and the experience to keep the program moving for "
                     "whoever is running the build."),
        "around_lede": ("Highton is one of our core Geelong suburbs. Most weeks we are working "
                        "the surrounding western suburbs and out to the Barrabool Hills."),
        "terrain_desc": "Highton blocks often carry significant fall down towards the river",
        "neighbours": ["Wandana Heights", "Belmont", "Waurn Ponds", "Ceres", "Newtown", "Grovedale", "Barrabool"],
        "chips": ["Highton", "Wandana Heights", "Belmont", "Waurn Ponds", "Ceres", "Newtown",
                  "Grovedale", "Barrabool", "Mount Duneed", "Marshall", "Geelong", "Fyansford"],
    },
    {
        "slug": "bellarine", "name": "Bellarine", "postcode": "3223",
        "lat": "-38.150000", "lng": "144.550000",
        "eyebrow": "Bellarine Peninsula", "region_place": "Bellarine Peninsula",
        "region_the": "the Bellarine", "wider": "the peninsula",
        "region_poss": "the Bellarine's", "slope_area": "Bellarine",
        "area_word": "Bellarine towns",
        "partner_region": "the Bellarine and the Geelong region",
        "service_area": "Bellarine, Geelong, Surf Coast",
        "card_blurb": "Peninsula-wide earthworks, concrete &amp; site cuts",
        "intro_h2": "Civil Contracting Across the Bellarine",
        "intro_p1": ("The Bellarine Peninsula has grown from a string of quiet coastal towns "
                     "into one of the busiest building areas in the Geelong region. From Leopold "
                     "and Drysdale through to Ocean Grove, Portarlington and the coast, there is "
                     "a constant mix of new estates, sea-change rebuilds and rural-residential "
                     "work. Civil work across the peninsula spans sandy coastal soils near the "
                     "beaches and reactive clay inland, so knowing the ground matters."),
        "intro_p2": ("Select Civil Group is based in the Geelong region and works the whole "
                     "Bellarine weekly. From a single site cut on a residential lot through to "
                     "multi-stage estate earthworks, we bring the right machinery, the right "
                     "operators, and the experience to keep the program moving for whoever is "
                     "running the build."),
        "around_lede": ("We cover the whole Bellarine Peninsula, from Leopold and Drysdale "
                        "through to the coast. Most weeks we are somewhere across the peninsula "
                        "and back through Geelong."),
        "terrain_desc": "Bellarine blocks vary from flat coastal pads to gently sloping inland rises",
        "neighbours": ["Drysdale", "Portarlington", "Leopold", "Ocean Grove", "St Leonards", "Indented Head", "Marcus Hill"],
        "chips": ["Drysdale", "Portarlington", "Leopold", "Ocean Grove", "Barwon Heads",
                  "Point Lonsdale", "Queenscliff", "St Leonards", "Indented Head",
                  "Clifton Springs", "Marcus Hill", "Geelong"],
    },
]


# ---- block renderers --------------------------------------------------------
def render_jsonld(s):
    faqs = build_faqs(s)
    area = ([{"@type": "City", "name": s["name"]}]
            + [{"@type": "City", "name": n} for n in s["neighbours"]]
            + [{"@type": "Place", "name": s["region_place"]}])
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Service",
                "serviceType": "Civil Contracting",
                "name": f"Civil Contracting {s['name']}",
                "description": (f"Full civil contracting services in {s['name']} and "
                                f"{s['region_the']}, including earthworks, site cuts, concrete "
                                f"and retaining walls."),
                "provider": {
                    "@type": "LocalBusiness",
                    "@id": "https://selectcivilgroup.com.au/#business",
                    "name": "Select Civil Group Pty Ltd",
                    "telephone": "+61483092615",
                    "url": "https://selectcivilgroup.com.au/",
                },
                "areaServed": area,
                "hasOfferCatalog": {
                    "@type": "OfferCatalog",
                    "name": f"Civil Contracting Services in {s['name']}",
                    "itemListElement": [
                        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Earthworks",
                         "description": f"Bulk earthworks, grading and land clearing across {s['name']} and {s['wider']}."}},
                        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Site Cuts",
                         "description": "Precision site cuts for new builds, sheds and developments."}},
                        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Concrete Driveways",
                         "description": "Driveways and crossovers in plain, exposed and coloured finishes."}},
                        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Retaining Walls",
                         "description": f"Engineered concrete retaining walls for sloping {s['slope_area']} blocks."}},
                    ],
                },
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://selectcivilgroup.com.au/"},
                    {"@type": "ListItem", "position": 2, "name": "Services", "item": "https://selectcivilgroup.com.au/services"},
                    {"@type": "ListItem", "position": 3, "name": s["name"], "item": f"https://selectcivilgroup.com.au/civil-contractor-{s['slug']}"},
                ],
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in faqs
                ],
            },
        ],
    }
    body = json.dumps(graph, indent=2, ensure_ascii=False)
    return '<script type="application/ld+json">\n' + body + '\n  </script>'


def build_faqs(s):
    n = s["neighbours"]
    q1a = (f"Yes. {s['name']}, {n[0]}, {n[1]} and {n[2]} and the surrounding {s['area_word']} "
           f"are all within our core service area. We are based in the Geelong region and work "
           f"{s['region_the']} regularly.")
    q4a = ("Both. For homeowners and small builders that is everything from a single retaining "
           "wall or driveway through to a full site cut and slab. For larger projects we partner "
           f"with builders, developers and contractors across {s['partner_region']}.")
    return [
        (f"Do you work as a civil contractor in {s['name']} and across {s['region_the']}?", q1a),
        (f"What does a civil package in {s['name']} typically cost?", A_COST),
        ("Can you coordinate with our builder, engineer and other trades?", A_COORD),
        ("Do you take on smaller residential jobs, or only large developments?", q4a),
        ("How quickly can you get on site?", A_LEAD),
        ("Are you fully insured?", A_INS),
    ]


def render_intro(s):
    return (
        '    <!-- ========== INTRO ========== -->\n'
        '    <section class="bg-white py-20 lg:py-28">\n'
        '      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">\n'
        '        <div class="max-w-3xl">\n'
        '          <div class="accent-bar mb-4"></div>\n'
        f'          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-6">{s["intro_h2"]}</h2>\n'
        '          <div class="space-y-4 body-text text-lg">\n'
        f'            <p>{s["intro_p1"]}</p>\n'
        f'            <p>{s["intro_p2"]}</p>\n'
        '          </div>\n'
        '        </div>\n'
        '      </div>\n'
        '    </section>'
    )


def render_chips(s):
    chip_html = "\n".join(
        f'          <div class="bg-white border border-black/10 px-4 py-3 text-center"><p class="text-gray-700 text-sm font-semibold">{c}</p></div>'
        for c in s["chips"]
    )
    return (
        '    <!-- ========== SUBURB CHIPS ========== -->\n'
        '    <section class="bg-sand border-t border-black/5 py-16 lg:py-20">\n'
        '      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">\n'
        '        <div class="max-w-3xl mb-10">\n'
        '          <div class="accent-bar mb-4"></div>\n'
        f'          <h2 class="heading-lg text-2xl sm:text-3xl lg:text-4xl text-dark-950 mb-4">Around {s["name"]}</h2>\n'
        f'          <p class="body-text text-base">{s["around_lede"]}</p>\n'
        '        </div>\n'
        '        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">\n'
        f'{chip_html}\n'
        '        </div>\n'
        '      </div>\n'
        '    </section>'
    )


def render_faq(s):
    faqs = build_faqs(s)
    items = []
    for q, a in faqs:
        items.append(
            '          <div class="faq-item">\n'
            '            <button onclick="toggleFaq(this)" class="w-full flex items-center justify-between py-6 text-left group focus-visible:outline-2 focus-visible:outline-brand-500 focus-visible:outline-offset-2">\n'
            f'              <h3 class="text-dark-950 text-lg sm:text-xl font-semibold pr-8" style="letter-spacing: -0.01em;">{q}</h3>\n'
            '              <svg class="faq-chevron w-5 h-5 text-gray-400 shrink-0" style="transition: transform 0.3s ease;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>\n'
            '            </button>\n'
            '            <div class="faq-answer overflow-hidden" style="max-height: 0; transition: max-height 0.3s ease, opacity 0.3s ease; opacity: 0;">\n'
            f'              <p class="body-text text-base pb-6">{a}</p>\n'
            '            </div>\n'
            '          </div>'
        )
    inner = "\n".join(items)
    return (
        '    <!-- ========== FAQ ========== -->\n'
        '    <section id="faq" class="bg-white border-t border-black/5 py-20 lg:py-28">\n'
        '      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">\n'
        '        <div class="mb-12">\n'
        '          <div class="accent-bar mb-4"></div>\n'
        '          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-4">Frequently Asked</h2>\n'
        f'          <p class="body-text text-lg">The questions we get most from {s["name"]} homeowners and builders.</p>\n'
        '        </div>\n'
        '        <div class="divide-y divide-black/10 border-y border-black/10">\n'
        f'{inner}\n'
        '        </div>\n'
        '      </div>\n'
        '    </section>'
    )


# ---- template build ---------------------------------------------------------
def build_template(src):
    """Tokenize the Torquay page into a template with @@TOKENS@@."""
    t = src

    def sub1(pattern, token, flags=re.S):
        nonlocal t
        new, n = re.subn(pattern, token, t, count=1, flags=flags)
        assert n == 1, f"section pattern not found: {pattern[:40]}"
        t = new

    # 1. Whole-block regeneration targets -> tokens
    sub1(r'<script type="application/ld\+json">.*?</script>', '@@JSONLD@@')
    sub1(r'    <!-- ========== INTRO ========== -->.*?</section>', '@@INTRO_SECTION@@')
    sub1(r'    <!-- ========== SUBURB CHIPS ========== -->.*?</section>', '@@CHIPS_SECTION@@')
    sub1(r'    <!-- ========== FAQ ========== -->.*?</section>', '@@FAQ_SECTION@@')

    # 2. Simple field tokens (explicit, unique strings)
    def rep(old, new):
        nonlocal t
        assert old in t, f"expected string not found: {old[:60]}"
        t = t.replace(old, new)

    rep('<title>Civil Contractor Torquay - Earthworks | Select Civil Group</title>',
        '<title>@@TITLE@@</title>')
    rep('<meta name="description" content="Local civil contractor in Torquay and the Surf Coast. Earthworks, site cuts, retaining walls, concrete driveways and slabs. Free quotes within 24 hours.">',
        '<meta name="description" content="@@META_DESC@@">')
    rep('<meta property="og:title" content="Civil Contractor Torquay - Select Civil Group">',
        '<meta property="og:title" content="@@OGTITLE@@">')
    rep('<meta property="og:description" content="Local civil contractor in Torquay and the Surf Coast. Earthworks, site cuts, retaining walls, concrete driveways and slabs. Free quotes within 24 hours.">',
        '<meta property="og:description" content="@@META_DESC@@">')
    rep('<meta name="twitter:title" content="Civil Contractor Torquay - Select Civil Group">',
        '<meta name="twitter:title" content="@@OGTITLE@@">')
    rep('<meta name="twitter:description" content="Earthworks, site cuts, retaining walls, concrete driveways and slabs in Torquay and across the Surf Coast.">',
        '<meta name="twitter:description" content="@@TW_DESC@@">')
    # coords (2 occurrences each)
    t = t.replace('-38.329000', '@@LAT@@').replace('144.326100', '@@LNG@@')
    # hero eyebrow
    rep('<p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-3">Surf Coast</p>',
        '<p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-3">@@EYEBROW@@</p>')
    # contact service-area line (before global Name swap to avoid "Geelong, Geelong")
    rep('<p class="text-gray-600 text-sm">Torquay, Geelong, Bellarine</p>',
        '<p class="text-gray-600 text-sm">@@SERVICE_AREA@@</p>')
    # services grid: site-cut terrain sentence
    rep('Surf Coast blocks vary from flat sand-pad to significant fall',
        '@@TERRAIN_DESC@@')
    # services grid: earthworks image alt
    rep('Bulk earthworks on a Surf Coast development site',
        'Bulk earthworks on a @@NAME@@ development site')
    # services grid: retaining "mixed terrain" possessive
    rep("engineered for the Surf Coast's mixed terrain",
        "engineered for @@REGION_POSS@@ mixed terrain")

    # 3. Global suburb-name / slug swaps (Torquay only ever means the target)
    t = t.replace('Torquay', '@@NAME@@').replace('torquay', '@@SLUG@@')

    # 4. Guards: nothing Torquay/Surf-Coast-specific should survive
    for leftover in ('Torquay', 'torquay', 'Surf Coast', 'Jan Juc', 'Bellbrae',
                     'Connewarre', 'Mount Duneed', 'Breamlea', 'Anglesea'):
        assert leftover not in t, f"leftover template token: {leftover}"
    return t


def render_page(tpl, s):
    tokens = {
        '@@TITLE@@': f"Civil Contractor {s['name']} | Select Civil Group",
        '@@OGTITLE@@': f"Civil Contractor {s['name']} - Select Civil Group",
        '@@META_DESC@@': (f"Local civil contractor in {s['name']} and {s['region_the']}. "
                          "Earthworks, site cuts, retaining walls, concrete driveways and slabs. "
                          "Free quotes within 24 hours."),
        '@@TW_DESC@@': (f"Earthworks, site cuts, retaining walls and concrete driveways in "
                        f"{s['name']} and across {s['region_the']}."),
        '@@LAT@@': s['lat'],
        '@@LNG@@': s['lng'],
        '@@EYEBROW@@': s['eyebrow'],
        '@@SERVICE_AREA@@': s['service_area'],
        '@@TERRAIN_DESC@@': s['terrain_desc'],
        '@@REGION_POSS@@': s['region_poss'],
        '@@JSONLD@@': render_jsonld(s),
        '@@INTRO_SECTION@@': render_intro(s),
        '@@CHIPS_SECTION@@': render_chips(s),
        '@@FAQ_SECTION@@': render_faq(s),
        '@@NAME@@': s['name'],
        '@@SLUG@@': s['slug'],
    }
    page = tpl
    for k, v in tokens.items():
        page = page.replace(k, v)
    # validation
    assert '@@' not in page, f"unfilled token in {s['slug']}: {page[page.find('@@'):page.find('@@')+40]}"
    assert page.count('<h1') == 1, f"{s['slug']}: expected 1 h1, got {page.count('<h1')}"
    for bad in ('—', '–', '&mdash;', '&ndash;'):
        assert bad not in page, f"{s['slug']}: em/en dash present"
    assert 'civil-contractor-' + s['slug'] in page
    return page


# ---- sitemap + services hub patchers ---------------------------------------
def patch_sitemap(entries):
    p = ROOT / "sitemap.xml"
    xml = p.read_text()
    blocks = []
    for slug in entries:
        loc = f"https://selectcivilgroup.com.au/civil-contractor-{slug}"
        if loc in xml:
            continue
        blocks.append(
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            "    <lastmod>2026-08-07</lastmod>\n"
            "    <changefreq>monthly</changefreq>\n"
            "    <priority>0.8</priority>\n"
            "  </url>\n"
        )
    if not blocks:
        return 0
    xml = xml.replace("</urlset>", "".join(blocks) + "</urlset>")
    p.write_text(xml)
    return len(blocks)


def patch_services_hub(subs):
    p = ROOT / "services.html"
    html = p.read_text()
    cards = []
    for s in subs:
        href = f"civil-contractor-{s['slug']}"
        if f'href="{href}"' in html:
            continue
        cards.append(
            f'        <a href="{href}" class="bg-white border border-black/10 hover:border-brand-500/30 p-6 group" style="transition: border-color 0.3s ease;">\n'
            f'          <p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-2">{s["eyebrow"]}</p>\n'
            f'          <h3 class="heading-md text-xl text-dark-950 mb-1 group-hover:text-brand-500" style="transition: color 0.2s ease;">Civil Contractor {s["name"]}</h3>\n'
            f'          <p class="body-text text-sm">{s["card_blurb"]}</p>\n'
            f'        </a>'
        )
    if not cards:
        return 0
    # insert before the closing </div> that ends the hub grid (the grid that holds civil-works-lara)
    anchor = '''        <a href="civil-works-lara" class="bg-white border border-black/10 hover:border-brand-500/30 p-6 group" style="transition: border-color 0.3s ease;">
          <p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-2">Geelong North</p>
          <h3 class="heading-md text-xl text-dark-950 mb-1 group-hover:text-brand-500" style="transition: color 0.2s ease;">Civil Contractor Lara</h3>
          <p class="body-text text-sm">Earthworks, concrete &amp; civil works</p>
        </a>'''
    assert anchor in html, "services.html hub anchor card not found"
    html = html.replace(anchor, anchor + "\n" + "\n".join(cards))
    p.write_text(html)
    return len(cards)


def main():
    src = BASE.read_text()
    tpl = build_template(src)
    written = []
    for s in SUBURBS:
        page = render_page(tpl, s)
        out = ROOT / f"civil-contractor-{s['slug']}.html"
        out.write_text(page)
        written.append((s['slug'], len(page.split())))
    n_sm = patch_sitemap([s['slug'] for s in SUBURBS])
    n_hub = patch_services_hub(SUBURBS)
    print(f"Wrote {len(written)} civil-contractor pages:")
    for slug, words in written:
        print(f"  civil-contractor-{slug}.html  (~{words} words in source)")
    print(f"sitemap.xml: +{n_sm} url entries")
    print(f"services.html hub: +{n_hub} location cards")


if __name__ == "__main__":
    main()
