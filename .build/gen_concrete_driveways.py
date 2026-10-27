#!/usr/bin/env python3
"""gen_concrete_driveways.py - Concrete Driveways pages for suburbs that have none.

Built for the WP HQ move of 2026-10-19 ("no organic visibility in 4 of 13 target
suburbs: Point Lonsdale, Lara, Leopold, Drysdale"). Point Lonsdale already has all five
pages and its gap is indexing, not coverage. Lara, Leopold and Drysdale had only a
civil hub and a retaining walls page each (Drysdale also excavation), and those pages
are indexed and still draw nothing, so the gap there is the service. Concrete Driveways
is the service with the widest suburb-level reach on this site (impressions in 5 of 13
suburbs, 125 in Geelong alone, 28 days to 2026-10-16) and both driveway enquiries on
file are crossover jobs for a second dwelling, so it is the strongest single page each.

Method: the page shell (head chrome, nav, footer, scripts) is lifted verbatim from
concrete-driveway-geelong.html, the deepest driveway page on the site and the one
published on 2026-09-15. The body is rebuilt per suburb from SUBURBS below.

Copy rule, which is what scripts/wphq-validate-site.py's duplication check enforces:
the finishes list, the quote factors, the six process steps and four FAQ answers are
the Geelong page's own words, carried VERBATIM so they read as a shared component (a
sentence on 4+ pages is chrome to the gate, and main() asserts each one still exists in
the template). Everything that names the suburb is written for that suburb. Never make
a "local" sentence by swapping the suburb into a Geelong sentence - that near-duplicate
is exactly what the gate exists to catch. No invented jobs, projects or credentials.

Also links the new pages in (homepage suburb index, the driveway parent page, the
Geelong driveway chips, each suburb's hub/sibling cards, services + concrete-services
grids) and adds them to sitemap.xml. Idempotent: a re-run rewrites the pages and finds
every link already in place.

Run from anywhere:  python3 .build/gen_concrete_driveways.py
"""

import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://selectcivilgroup.com.au"
TEMPLATE = os.path.join(ROOT, "concrete-driveway-geelong.html")
SITEMAP = os.path.join(ROOT, "sitemap.xml")
LASTMOD = "2026-10-19"
PHONE_TEL = "0483092615"
PHONE_DISPLAY = "0483 092 615"


def t(s):
    """Text content. Apostrophes stay literal, matching the live pages."""
    return html.escape(s, quote=False)


def a(s):
    return html.escape(s, quote=True)


def link(href, text):
    return f'<a href="{href}" class="text-brand-500 font-medium hover:underline">{t(text)}</a>'


# --------------------------------------------------------------------------- shared copy
# Verbatim from concrete-driveway-geelong.html. main() refuses to run if any of these
# has drifted from the template, because a near-copy is worse than either extreme.

FINISH_INTRO = ("The finish is the biggest choice you make on a driveway. It changes the look from the "
                "street, the grip underfoot and the final price, so it is worth knowing how the options "
                "compare before you ask for a quote.")
FINISHES = [
    ("Plain broom", "a light broom texture across the surface for grip. The most affordable option and the one most Geelong driveways end up with."),
    ("Exposed aggregate", "the surface is washed back to reveal the stone through the mix. More texture and grip than plain, at a higher price."),
    ("Coloured", "oxide mixed through the concrete so the driveway suits the house, fence or render. Usually sits between plain and exposed on cost."),
    ("Stencilled or stamped", "a pattern pressed or stencilled into the surface for a brick, slate or tile look. Priced at the higher end, alongside exposed aggregate."),
]
FINISH_OUTRO = ("Not sure which suits? Tell us about the property and how the driveway gets used, and we "
                "will talk the options through on site.")
QUOTE_INTRO = "Every quote we send is itemised, so you can see where the money goes."
FACTORS = [
    ("Size and shape", "Square metres set the concrete volume. Curves, a turning bay or a second parking space add formwork and labour."),
    ("Finish", "Plain broom costs least. Exposed aggregate, coloured and patterned surfaces each add to the price."),
    ("Ground and base", "Soft or reactive ground can need deeper excavation and more base material before the slab goes down."),
    ("Drainage", "Where falls alone will not shift water off the driveway, drainage is built in before the pour."),
    ("Crossover", "A new or widened crossover needs council approval and inspection, and it is priced in wherever it applies."),
    ("Access", "A clear run for the concrete truck keeps costs down. Narrow side access or a long pump line adds time."),
]
PROCESS_LEDE = "Six stages in the same order every time, with a programmed start date locked in when you accept the quote."
STEPS = [
    ("Measure-Up", "Send the address and roughly what you have in mind. We check the size, the falls toward the street and the access for the truck before pricing."),
    ("Itemised Quote", "Finish, base, steel, drainage and any crossover work are listed as separate lines, so you can see what each choice adds."),
    ("Excavation and Base", "The ground is dug out to depth, then base material is spread and compacted to give the slab a firm, even bed."),
    ("Formwork and Steel", "Forms are set to the finished levels and falls, and the steel reinforcement is placed before the pour."),
    ("Pour and Finish", "Poured, screeded and finished in the surface you picked. On a standard residential driveway the pour is usually a one-day job."),
    ("Handover", "Forms stripped and the site cleaned up. Before we leave, we tell you how long to keep cars off the new concrete."),
]
FAQ_COST_A = ("The price comes down to the area, the finish, what the ground needs before the pour, drainage, "
              "access for the concrete truck and whether a crossover is part of the job. Those vary so much "
              "between properties that we do not quote a flat square metre rate. Send the address and a rough "
              "size and we will come back with an itemised, obligation-free quote within 24 hours.")
FAQ_CROSSOVER = ("Do I need council approval for a new crossover?",
                 "Usually, yes. A new or widened vehicle crossing generally needs consent from the City of Greater "
                 "Geelong, and the council sets the levels and specifications it has to be built to. We let you know "
                 "what applies to your property before work starts, then pour the crossover to that standard, either "
                 "with the driveway or as a job on its own.")
FAQ_DURATION = ("How long does a driveway take from start to finish?",
                "Most residential driveways are finished inside a working week once you allow for excavation, the "
                "base, formwork, the pour and stripping the forms. The pour itself normally takes a single day. A "
                "larger driveway, a new crossover or a retaining wall alongside can stretch that out, and your "
                "programmed start date is confirmed with the quote.")
FAQ_INSURED = ("Are you fully insured?",
               "Yes. Select Civil Group carries full public liability insurance and workers compensation cover on "
               "every job. Certificates of currency are available on request.")
CTA_LEDE = ("Send the address, a rough size and the finish you are leaning toward. We will come back with an "
            "obligation-free quote within 24 hours.")
SHARED = ([FINISH_INTRO, FINISH_OUTRO, QUOTE_INTRO, PROCESS_LEDE, FAQ_COST_A, CTA_LEDE]
          + [d for _, d in FINISHES] + [d for _, d in FACTORS] + [d for _, d in STEPS]
          + [q for q, _ in (FAQ_CROSSOVER, FAQ_DURATION, FAQ_INSURED)]
          + [x for _, x in (FAQ_CROSSOVER, FAQ_DURATION, FAQ_INSURED)])

HERO_IMG = "Assets/concrete-driveways.jpeg"
HERO_ALT = "Freshly poured concrete driveway by Select Civil Group with the formwork still in place beside a new home"

# --------------------------------------------------------------------------- per-suburb copy

SUBURBS = [
    {
        "slug": "lara", "name": "Lara", "lat": "-38.0236", "lng": "144.4088",
        "eyebrow": "Geelong North",
        "meta": "Concrete driveways and crossovers in Lara, from new estate homes to second dwellings. Plain, exposed aggregate and coloured finishes. Quotes in 24 hours.",
        "social": "Concrete driveways and crossovers across Lara and the northern Geelong suburbs.",
        "schema_desc": "Concrete driveways and crossovers across Lara and northern Geelong by Select Civil Group, in plain, exposed aggregate, coloured and stencilled finishes.",
        "offers": [
            ("Estate Home Driveways", "Driveways and crossovers for new homes in Lara's estates."),
            ("Second Dwelling Crossovers", "New vehicle crossings poured to the City of Greater Geelong's levels and specifications."),
            ("Rural-Residential Driveways", "Longer driveways, turning areas and shed aprons on larger lots."),
            ("Decorative Driveway Finishes", "Exposed aggregate, coloured and stencilled concrete."),
        ],
        "hero": "Concrete driveways for Lara's new estates, older town blocks and rural lots toward the You Yangs. Plain, exposed aggregate or coloured, crossover included. Quotes back within 24 hours.",
        "intro_h2": "Driveways for a Growing Lara",
        "intro": [
            t("Lara has grown quickly on the open land between Geelong and the You Yangs, and most driveway work here follows that growth. New homes in the estates need a driveway and crossover soon after the builder hands over the keys. Closer to the town centre, older blocks with room at the back can take a second dwelling, and a second home needs its own way to the street. Further out, rural-residential owners want a hard surface that stays put under trailers, caravans and farm vehicles."),
            t("Flat ground makes Lara look easy, but the soil tells a different story. Much of the area sits on clay weathered from the old basalt plain, and that clay swells when it is wet and shrinks as it dries. A driveway poured on a thin or poorly compacted base is the one that cracks and drops at the edges. Estate lots can also carry fill from the subdivision earthworks, which has to be found and dealt with before the base goes in. We excavate to depth, compact the base in layers and set the falls so water runs off toward the street instead of pooling at the garage door."),
            "Select Civil Group is based in Geelong, and Lara sits on our regular run through the northern suburbs with Corio and Norlane. If a boundary needs a "
            + link("retaining-walls-lara", "retaining wall") + " before the driveway goes down, or the whole block needs "
            + link("civil-works-lara", "site works") + " first, the same crew handles it.",
        ],
        "local_h3": "What Lara Driveway Jobs Usually Look Like",
        "local_lede": "Most enquiries from Lara fit one of these three. Each is priced differently, so it helps to know which one you have.",
        "local": [
            ("New estate homes", "The house is finished and the driveway is the last big job before the garden. Many estates set the finish, colour and timing of the driveway in their design guidelines, so check yours before you choose and we will pour to it. The crossover is normally poured as part of the same job."),
            ("Second dwellings", "A home at the rear of an existing block usually means a new crossover and a driveway running down the side of the first house. Council approval for the crossover comes first, and side access for the concrete truck is often what sets the price, so we look at both at the measure-up."),
            ("Rural-residential lots", "Longer driveways, turning circles and aprons in front of sheds, often replacing gravel that washes out every winter. On a long run the money goes into the base and the drainage, particularly where the driveway crosses lower ground that holds water."),
        ],
        "image": ("Assets/concrete-driveway-1.jpg", "Freshly poured charcoal concrete driveway at a new home, with the formwork and safety tape still in place"),
        "quote_tail": "These are the things that move the number most on a Lara driveway.",
        "related_lede": "Driveway work in Lara rarely happens on its own. These are the jobs that usually come before it on the same block.",
        "related": [
            ("retaining-walls-lara", "Retaining Walls Lara", "Concrete walls along boundaries and estate batters."),
            ("civil-works-lara", "Civil Contractor Lara", "Site cuts, earthworks and slab prep, one crew."),
            ("concrete-driveway-geelong", "Concrete Driveways Geelong", "Driveways and crossovers across the city."),
            ("concrete-paving", "Concrete Paving", "Paths and outdoor areas poured to match."),
        ],
        "chips_lede": "Lara is the centre of our work north of the city. We pour driveways through the suburbs between here and Geelong, and out to the rural blocks beyond.",
        "chips": ["Lara", "Corio", "Norlane", "North Shore", "North Geelong", "Bell Park", "Bell Post Hill",
                  "Hamlyn Heights", "Lovely Banks", "Little River", "Anakie", ("Geelong", "concrete-driveway-geelong")],
        "faq_lede": "Driveway questions we hear most from Lara homeowners and builders.",
        "faq": [
            ("Which areas around Lara do you pour driveways in?", "Lara and its newer estates, plus Corio, Norlane, North Shore, Bell Park, Lovely Banks and the rest of the northern suburbs between here and Geelong. We also take on rural-residential jobs out toward Little River, Anakie and the You Yangs."),
            ("How much does a concrete driveway cost in Lara?", FAQ_COST_A),
            FAQ_CROSSOVER,
            ("We are building a second dwelling. Can you add a crossover for it?", "Yes. A second home on the block is one of the most common reasons for a new crossover. The council has to approve it first and will set where it can sit and the levels it must meet, so that is the first thing we check. From there the crossover and the new driveway are poured together, and if the new layout cuts across the existing driveway we can rework that in the same job."),
            ("Can you pour a long driveway on a rural-residential block?", "Yes. On a longer driveway the cost sits mostly in the excavation, the base and the drainage rather than the surface, so we walk the length of it first and look at where water crosses before pricing. A plain broom finish is the practical choice over a long run, and a decorative finish can be kept to the section near the house if you want one."),
            FAQ_DURATION,
            FAQ_INSURED,
        ],
    },
    {
        "slug": "leopold", "name": "Leopold", "lat": "-38.1892", "lng": "144.4645",
        "eyebrow": "Bellarine Gateway",
        "meta": "Concrete driveways in Leopold: new estate pours, cracked old driveways replaced from the base up, and council-standard crossovers. Free quotes in 24 hours.",
        "social": "Concrete driveways and crossovers across Leopold and the Bellarine gateway.",
        "schema_desc": "Concrete driveways, driveway replacements and crossovers in Leopold by Select Civil Group, in plain, exposed aggregate, coloured and stencilled finishes.",
        "offers": [
            ("Driveway Replacement", "Old concrete broken out and removed, base rebuilt, new driveway poured."),
            ("New Home Driveways", "Driveways and crossovers for new homes in Leopold's estates."),
            ("Concrete Crossovers", "Vehicle crossings poured to the City of Greater Geelong's levels and specifications."),
            ("Driveway Widening", "Extra parking width for a second car, a boat or a caravan."),
        ],
        "hero": "Concrete driveways for Leopold's new estates and its established streets alike. New pours, cracked old driveways replaced from the base up, and crossovers built to council standard. Quotes back within 24 hours.",
        "intro_h2": "Leopold Driveways, Old and New",
        "intro": [
            t("Leopold sits on the Bellarine Highway at the gateway to the peninsula, and its driveway work splits two ways. The estates on the edge of town keep producing new homes that need a driveway once the builder is out. The established streets carry driveways that have been down for decades, and a fair number of them have cracked, lifted or sunk to the point where patching is no longer worth the money."),
            t("The ground is the reason so many older driveways fail here. Leopold is largely reactive clay, which moves with every wet winter and dry summer and finds any weak spot in a slab. That makes the base and the steel more important than the finish on top. On a replacement we break out and cart away the old concrete, look at what is underneath, and rebuild the base rather than pouring fresh concrete over ground that has already let one driveway down."),
            "We are based in Geelong and on the Bellarine most weeks, so Leopold, Newcomb, Moolap and Whittington are short trips for us. Where the driveway runs beside a change in level, a "
            + link("retaining-walls-leopold", "retaining wall") + " can go in first, and our "
            + link("civil-contractor-leopold", "Leopold civil page") + " covers the wider site work.",
        ],
        "local_h3": "What Leopold Driveway Jobs Usually Involve",
        "local_lede": "Most Leopold driveway work falls into one of three kinds, and each is priced on different things.",
        "local": [
            ("Replacing an old driveway", "The existing concrete is broken out, loaded and taken away before any new work starts. Removal and disposal sit on their own line of the quote, so you can see what the old driveway costs to get rid of."),
            ("New homes in the estates", "A driveway and crossover poured once the build is complete, in a finish your estate guidelines allow. If the front of the lot was left higher or lower than the garage slab, the levels are sorted out before we form up."),
            ("Wider driveways and parking", "Extra width for a second car, a boat or a caravan beside the house. More area means more concrete and steel, and the falls have to work across the full width so water does not pond against a fence or a neighbour's boundary."),
        ],
        "image": ("Assets/concrete-crossover.jpeg", "Freshly poured shared concrete driveway and footpath running in from the kerb past a row of brick units"),
        "quote_tail": "These are the things that move the number most on a Leopold driveway.",
        "related_lede": "If a driveway is part of a bigger job on your Leopold block, these pages cover the rest of it.",
        "related": [
            ("retaining-walls-leopold", "Retaining Walls Leopold", "Walls where the driveway meets a level change."),
            ("civil-contractor-leopold", "Civil Contractor Leopold", "Site cuts, earthworks and excavation, one crew."),
            ("concrete-driveway-drysdale", "Concrete Driveways Drysdale", "Driveways on the sloping blocks further east."),
            ("concrete-paving", "Concrete Paving", "Paths and outdoor areas poured to match."),
        ],
        "chips_lede": "Leopold is where Geelong meets the Bellarine, so our driveway work here runs both ways along the highway.",
        "chips": ["Leopold", "Newcomb", "Moolap", "Whittington", "St Albans Park", "Breakwater", "Wallington",
                  "Curlewis", ("Drysdale", "concrete-driveway-drysdale"), ("Ocean Grove", "concrete-driveway-ocean-grove"),
                  ("Portarlington", "concrete-driveway-portarlington"), ("Geelong", "concrete-driveway-geelong")],
        "faq_lede": "Driveway questions we hear most from Leopold homeowners and builders.",
        "faq": [
            ("Which parts of Leopold and the Bellarine do you cover?", "All of Leopold, from the older streets near the highway out to the newer estates, as well as Newcomb, Moolap, Whittington, Wallington and Curlewis. We pour driveways right across the rest of the Bellarine too, from Drysdale and Portarlington down to Ocean Grove."),
            ("How much does a concrete driveway cost in Leopold?", FAQ_COST_A),
            ("Can you remove my old driveway as part of the job?", "Yes. We break out the old concrete, load it and cart it away, then check the ground underneath before deciding how much new base it needs. A driveway that failed because of a weak base will fail again if new concrete goes over the same ground, so this is the step that makes a replacement last."),
            FAQ_CROSSOVER,
            ("Will a new driveway crack on Leopold clay?", "Concrete shrinks slightly as it cures, so we cut control joints to decide where any fine cracking shows rather than leaving it to chance. The damaging kind, where sections lift, drop or break apart, comes from the ground underneath. A deep, well compacted base, the right reinforcement and keeping water from soaking the clay at the edges are what prevent it, and they are the parts of the quote we will not cut corners on."),
            FAQ_DURATION,
            FAQ_INSURED,
        ],
    },
    {
        "slug": "drysdale", "name": "Drysdale", "lat": "-38.1728", "lng": "144.5711",
        "eyebrow": "Central Bellarine",
        "meta": "Concrete driveways in Drysdale, Clifton Springs and Curlewis, including sloping blocks. Plain, exposed aggregate and coloured finishes. Quotes in 24 hours.",
        "social": "Concrete driveways and crossovers across Drysdale and the central Bellarine.",
        "schema_desc": "Concrete driveways and crossovers in Drysdale, Clifton Springs and Curlewis by Select Civil Group, including driveways on sloping blocks.",
        "offers": [
            ("Sloping Block Driveways", "Driveways graded and drained for blocks that fall to or from the street."),
            ("New Home Driveways", "Driveways and crossovers for new homes around Drysdale and Clifton Springs."),
            ("Concrete Crossovers", "Vehicle crossings poured to the City of Greater Geelong's levels and specifications."),
            ("Decorative Driveway Finishes", "Exposed aggregate, coloured and stencilled concrete."),
        ],
        "hero": "Concrete driveways across Drysdale, Clifton Springs and Curlewis, including blocks that fall to or from the street. Graded and drained before the pour. Quotes back within 24 hours.",
        "intro_h2": "Drysdale Driveways on Falling Ground",
        "intro": [
            t("The Bellarine rises toward its middle and Drysdale is built across that rise, so plenty of blocks here fall toward the street or away from it. That shapes a driveway more than any choice of finish. A driveway climbing to a garage needs a grade a car can manage and a surface that grips on a wet morning, while one running down to the house needs the water caught and taken away before it reaches the garage door."),
            t("The town has grown in every direction, with new estates around Drysdale and Clifton Springs, infill through the established streets and larger semi-rural lots on the outskirts. Under most of it sits clay that moves through the seasons, so whatever the slope, the base is dug to depth and compacted properly before the steel goes in."),
            "We are based in Geelong and on the Bellarine every week. If the block needs "
            + link("excavation-drysdale", "excavation") + " or a " + link("retaining-walls-drysdale", "retaining wall")
            + " beside the driveway, they can be programmed into the same job, and the "
            + link("civil-contractor-drysdale", "Drysdale civil page") + " covers the rest of the site work.",
        ],
        "local_h3": "Getting a Sloping Driveway Right",
        "local_lede": "On a Drysdale block the slope decides most of the driveway, and these are the three situations it usually creates.",
        "local": [
            ("Driveways that climb", "A steep driveway wants a surface with grip, so exposed aggregate or a heavier broom texture beats a smooth finish. The changes in grade at the street and at the garage are shaped so a car does not scrape on the way in or out."),
            ("Driveways that fall to the house", "Water running toward the garage has to be stopped before it gets there, usually with a grated drain across the driveway connected to the property's stormwater. That is set out with the falls before the pour, not added later."),
            ("Walls beside the driveway", "On a cut block the driveway often runs alongside a change in level, so the retaining wall goes in first and the driveway is formed against it. Doing both in one job means the levels line up and nobody has to come back to fix the join."),
        ],
        "image": ("Assets/concrete-driveway-3.jpg", "Exposed aggregate concrete at the street end of a driveway, with the base prepared behind it for the next section"),
        "quote_tail": "These are the things that move the number most on a Drysdale driveway.",
        "related_lede": "On a sloping Drysdale block the driveway is tied to the site cut and the walls around it. These pages cover that work.",
        "related": [
            ("excavation-drysdale", "Excavation Drysdale", "Site cuts and detail digs before the build."),
            ("retaining-walls-drysdale", "Retaining Walls Drysdale", "Walls that hold the ground beside a driveway."),
            ("civil-contractor-drysdale", "Civil Contractor Drysdale", "The full civil package for a Bellarine build."),
            ("concrete-driveway-leopold", "Concrete Driveways Leopold", "New pours and replacements on the way into town."),
        ],
        "chips_lede": "Drysdale is the middle of our Bellarine work. From here we pour driveways out to the towns on every side of the peninsula.",
        "chips": ["Drysdale", "Clifton Springs", "Curlewis", "Wallington", "Bellarine", "St Leonards", "Indented Head",
                  ("Portarlington", "concrete-driveway-portarlington"), ("Leopold", "concrete-driveway-leopold"),
                  ("Ocean Grove", "concrete-driveway-ocean-grove"), ("Point Lonsdale", "concrete-driveway-point-lonsdale"),
                  ("Queenscliff", "concrete-driveway-queenscliff")],
        "faq_lede": "Driveway questions we hear most from Drysdale homeowners and builders.",
        "faq": [
            ("Do you pour driveways in Clifton Springs and Curlewis too?", "Yes. Drysdale, Clifton Springs, Curlewis, Wallington, St Leonards, Indented Head and Portarlington are all part of our regular Bellarine work, and Leopold and Ocean Grove are on the same runs."),
            ("How much does a concrete driveway cost in Drysdale?", FAQ_COST_A),
            ("How steep can a concrete driveway be?", "It depends on the block, and the transitions matter as much as the overall slope. A steep driveway can still work if the change in grade at the street and at the garage is gradual enough for a car to pass without scraping, and if the surface grips in the wet. We measure the fall on site before suggesting a layout, and where the grade is too much we will say so and talk through other options, such as a level parking area near the street."),
            FAQ_CROSSOVER,
            ("Can the driveway be done with the site cut and retaining wall?", "Yes, and on a sloping block it usually should be. The cut sets the garage level, the wall holds the ground beside the driveway, and the driveway ties both of them back to the street. Programming all three together means one set of levels and one crew answerable for how they meet."),
            FAQ_DURATION,
            FAQ_INSURED,
        ],
    },
]


# --------------------------------------------------------------------------- template

def load_template():
    src = open(TEMPLATE, encoding="utf-8").read()
    for s in SHARED:
        if t(s) not in src:
            sys.exit(f"[gen_concrete_driveways] shared copy has drifted from {os.path.basename(TEMPLATE)}: {s[:70]!r}")
    anchors = ["  <title>", "  <!-- Styles (compiled Tailwind", "  <!-- JSON-LD", "  <style>",
               '  <main id="main">', "  </main>"]
    for an in anchors:
        if src.count(an) != 1:
            sys.exit(f"[gen_concrete_driveways] template anchor {an!r} found {src.count(an)} times, expected 1")
    return {
        "top": src[:src.index("  <title>")],
        "assets": src[src.index("  <!-- Styles (compiled Tailwind"):src.index("  <!-- JSON-LD")],
        "chrome": src[src.index("  <style>"):src.index('  <main id="main">')],
        "tail": src[src.index("  </main>"):],
    }


def schema(sub, canonical):
    name = sub["name"]
    area = []
    for c in sub["chips"]:
        area.append({"@type": "City", "name": c[0] if isinstance(c, tuple) else c})
    graph = [
        {
            "@type": "Service",
            "serviceType": "Concrete Driveways",
            "name": f"Concrete Driveways {name}",
            "description": sub["schema_desc"],
            "provider": {
                "@type": "LocalBusiness",
                "@id": SITE + "/#business",
                "name": "Select Civil Group Pty Ltd",
                "telephone": "+61483092615",
                "url": SITE + "/",
            },
            "areaServed": area,
            "hasOfferCatalog": {
                "@type": "OfferCatalog",
                "name": f"Concrete Driveway Services in {name}",
                "itemListElement": [
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "description": d}}
                    for n, d in sub["offers"]
                ],
            },
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Concrete Services", "item": SITE + "/concrete-services"},
                {"@type": "ListItem", "position": 3, "name": "Concrete Driveways", "item": SITE + "/concrete-driveways"},
                {"@type": "ListItem", "position": 4, "name": name, "item": canonical},
            ],
        },
        {
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}}
                for q, ans in sub["faq"]
            ],
        },
    ]
    body = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)
    return "\n".join("  " + line for line in body.split("\n"))


def head(tpl, sub):
    name, slug = sub["name"], f"concrete-driveway-{sub['slug']}"
    canonical = f"{SITE}/{slug}"
    title = f"Concrete Driveways {name} | Select Civil Group"
    og_title = f"Concrete Driveways {name} - Select Civil Group"
    assert len(title) <= 60, title
    assert len(sub["meta"]) <= 160, (len(sub["meta"]), sub["meta"])
    return (tpl["top"]
            + f"""  <title>{t(title)}</title>
  <meta name="description" content="{a(sub['meta'])}">
  <link rel="canonical" href="{canonical}">

  <!-- Geo meta -->
  <meta name="geo.region" content="AU-VIC">
  <meta name="geo.placename" content="{a(name)}">
  <meta name="geo.position" content="{sub['lat']};{sub['lng']}">
  <meta name="ICBM" content="{sub['lat']}, {sub['lng']}">

  <!-- Open Graph -->
  <meta property="og:title" content="{a(og_title)}">
  <meta property="og:description" content="{a(sub['meta'])}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="Select Civil Group">
  <meta property="og:locale" content="en_AU">
  <meta property="og:image" content="{SITE}/{HERO_IMG}">
  <meta property="og:image:width" content="1437">
  <meta property="og:image:height" content="1078">
  <meta property="og:image:alt" content="{a(HERO_ALT)}">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{a(og_title)}">
  <meta name="twitter:description" content="{a(sub['social'])}">
  <meta name="twitter:image" content="{SITE}/{HERO_IMG}">

"""
            + tpl["assets"]
            + "  <!-- JSON-LD: @graph (Service + BreadcrumbList + FAQPage) -->\n"
            + '  <script type="application/ld+json">\n'
            + schema(sub, canonical) + "\n"
            + "  </script>\n\n"
            + tpl["chrome"])


FAQ_CHEVRON = '<svg class="faq-chevron w-5 h-5 text-gray-400 shrink-0" style="transition: transform 0.3s ease;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>'


def chip(c):
    if isinstance(c, tuple):
        label, href = c
        return (f'<a href="{href}" class="block bg-sand border border-black/10 px-4 py-3 text-center hover:border-brand-500/30" '
                f'style="transition: border-color 0.2s ease;"><p class="text-gray-700 text-sm font-semibold">{t(label)}</p></a>')
    return f'<div class="bg-sand border border-black/10 px-4 py-3 text-center"><p class="text-gray-700 text-sm font-semibold">{t(c)}</p></div>'


def main_body(sub):
    name, slug = sub["name"], f"concrete-driveway-{sub['slug']}"
    img, img_alt = sub["image"]
    intro = "\n".join(f"            <p>{p}</p>" for p in sub["intro"])
    local = "\n".join(
        f'            <div class="bg-sand border border-black/10 p-7"><h4 class="heading-md text-lg text-dark-950 mb-3">{t(h)}</h4><p class="body-text text-sm">{t(d)}</p></div>'
        for h, d in sub["local"])
    finishes = "\n".join(
        f'              <li><span class="text-dark-950 font-semibold">{t(h)}</span> - {t(d)}</li>' for h, d in FINISHES)
    factors = "\n".join(
        f"""          <div class="border-l-2 border-brand-500/40 pl-5">
            <h3 class="text-dark-950 text-sm font-bold mb-1">{t(h)}</h3>
            <p class="body-text text-sm">{t(d)}</p>
          </div>""" for h, d in FACTORS)
    steps = "\n".join(
        f'          <div class="bg-sand border border-black/10 p-7"><p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-2">Step {i:02d}</p><h3 class="heading-md text-lg text-dark-950 mb-3">{t(h)}</h3><p class="body-text text-sm">{t(d)}</p></div>'
        for i, (h, d) in enumerate(STEPS, 1))
    related = "\n".join(
        f"""          <a href="{href}" class="group block bg-white border border-black/10 p-6 hover:border-brand-500/30" style="transition: border-color 0.3s ease;">
            <h3 class="heading-md text-lg text-dark-950 mb-2">{t(h)}</h3>
            <p class="body-text text-sm mb-4">{t(d)}</p>
            <span class="text-brand-500 text-sm font-bold uppercase tracking-wider">View &rarr;</span>
          </a>""" for href, h, d in sub["related"])
    chips = "\n".join("          " + chip(c) for c in sub["chips"])
    faqs = "\n".join(
        f"""          <div class="faq-item">
            <button onclick="toggleFaq(this)" class="w-full flex items-center justify-between py-6 text-left group focus-visible:outline-2 focus-visible:outline-brand-500 focus-visible:outline-offset-2">
              <h3 class="text-dark-950 text-lg sm:text-xl font-semibold pr-8" style="letter-spacing: -0.01em;">{t(q)}</h3>
              {FAQ_CHEVRON}
            </button>
            <div class="faq-answer overflow-hidden" style="max-height: 0; transition: max-height 0.3s ease, opacity 0.3s ease; opacity: 0;">
              <p class="body-text text-base pb-6">{t(ans)}</p>
            </div>
          </div>""" for q, ans in sub["faq"])
    options = """                  <optgroup label="Concrete Services">
                    <option value="retaining-walls">Retaining Walls</option>
                    <option value="concrete-driveways" selected>Concrete Driveways</option>
                    <option value="concrete-raft-slabs">Concrete Raft Slabs</option>
                    <option value="concrete-paving">Concrete Paving</option>
                    <option value="factory-tilt-panels">Factory Tilt Panels</option>
                    <option value="concrete-seating">Concrete Seating</option>
                    <option value="concrete-bench-drops">Concrete Bench Drops</option>
                  </optgroup>
                  <optgroup label="Earthworks &amp; Excavation">
                    <option value="earthworks">Earthworks</option>
                    <option value="site-cuts">Site Cuts</option>
                    <option value="detail-excavation">Detail Excavation</option>
                    <option value="excess-soil-removal">Excess Soil Removal</option>
                  </optgroup>"""
    field = "w-full bg-white border border-black/10 px-4 py-3 text-dark-950 text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500"
    label = "block text-dark-950 text-sm font-bold uppercase tracking-wider mb-2"
    return f"""  <main id="main">
    <!-- Breadcrumbs -->
    <nav aria-label="Breadcrumb" class="bg-sand border-b border-black/5 pt-20 lg:pt-24">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <ol class="flex flex-wrap items-center gap-2 text-xs text-gray-500">
          <li><a href="/" class="hover:text-brand-500" style="transition: color 0.2s ease;">Home</a></li>
          <li aria-hidden="true" class="text-gray-400">/</li>
          <li><a href="concrete-services" class="hover:text-brand-500" style="transition: color 0.2s ease;">Concrete Services</a></li>
          <li aria-hidden="true" class="text-gray-400">/</li>
          <li><a href="concrete-driveways" class="hover:text-brand-500" style="transition: color 0.2s ease;">Concrete Driveways</a></li>
          <li aria-hidden="true" class="text-gray-400">/</li>
          <li class="text-gray-700" aria-current="page">{t(name)}</li>
        </ol>
      </div>
    </nav>

    <!-- ========== HERO ========== -->
    <section class="relative">
      <div class="relative overflow-hidden" style="height: 420px;">
        <img src="{HERO_IMG}" alt="{a(HERO_ALT)}" width="1600" height="900" class="w-full h-full object-cover" fetchpriority="high">
        <div class="absolute inset-0 bg-black/60"></div>
        <div class="absolute inset-0 bg-gradient-to-t from-dark-950 via-transparent to-transparent"></div>
        <div class="absolute inset-0 flex items-center">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
            <div class="accent-bar mb-4"></div>
            <p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-3">{t(sub['eyebrow'])}</p>
            <h1 class="heading-xl text-4xl sm:text-5xl md:text-6xl text-white mb-4">Concrete Driveways in {t(name)}</h1>
            <p class="text-gray-300 text-lg max-w-2xl" style="line-height: 1.7;">{t(sub['hero'])}</p>
            <div class="flex flex-col sm:flex-row gap-3 mt-6">
              <a href="#contact" class="btn-fill px-7 py-3 text-sm">Get a {t(name)} Quote</a>
              <a href="tel:{PHONE_TEL}" class="btn-outline px-7 py-3 text-sm">Call {PHONE_DISPLAY}</a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ========== INTRO + LOCAL JOBS ========== -->
    <section class="bg-white py-20 lg:py-28">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-6">{t(sub['intro_h2'])}</h2>
          <div class="space-y-4 body-text text-lg">
{intro}
          </div>
        </div>
        <div class="max-w-3xl mt-16 mb-10">
          <h3 class="heading-md text-2xl text-dark-950 mb-3">{t(sub['local_h3'])}</h3>
          <p class="body-text text-base">{t(sub['local_lede'])}</p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
{local}
        </div>
      </div>
    </section>

    <!-- ========== FINISHES ========== -->
    <section class="bg-sand border-t border-black/5 py-20 lg:py-28">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col lg:flex-row gap-12 lg:gap-20 items-center">
          <div class="lg:w-1/2 w-full">
            <div class="relative overflow-hidden" style="aspect-ratio: 4/3;">
              <img src="{img}" alt="{a(img_alt)}" width="800" height="600" class="w-full h-full object-cover" loading="lazy" decoding="async">
            </div>
          </div>
          <div class="lg:w-1/2">
            <div class="accent-bar mb-4"></div>
            <h2 class="heading-lg text-3xl sm:text-4xl text-dark-950 mb-6">Choosing a Finish for Your Driveway</h2>
            <div class="space-y-4 body-text">
              <p>{t(FINISH_INTRO)}</p>
            </div>
            <h3 class="heading-md text-base text-brand-500 mt-8 mb-3" style="letter-spacing: 0.05em; text-transform: uppercase;">Driveway finishes we pour</h3>
            <ul class="body-text text-sm space-y-2">
{finishes}
            </ul>
            <p class="body-text text-base mt-6">{t(FINISH_OUTRO)} Paths and outdoor areas can be poured to match with our <a href="concrete-paving" class="text-brand-500 font-medium hover:underline">concrete paving</a>.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ========== WHAT SETS THE PRICE ========== -->
    <section class="bg-white border-t border-black/5 py-20 lg:py-28">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl mb-12">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-6">What Goes Into a Driveway Quote</h2>
          <p class="body-text text-lg">{t(QUOTE_INTRO)} {t(sub['quote_tail'])}</p>
        </div>
        <div class="max-w-4xl grid sm:grid-cols-2 gap-x-10 gap-y-5">
{factors}
        </div>
      </div>
    </section>

    <!-- ========== PROCESS ========== -->
    <section class="bg-sand border-t border-black/5 py-20 lg:py-28">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl mb-12">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-6">How a {t(name)} Driveway Job Runs</h2>
          <p class="body-text text-lg">{t(PROCESS_LEDE)}</p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
{steps}
        </div>
      </div>
    </section>

    <!-- ========== RELATED {t(name).upper()} SERVICES ========== -->
    <section class="bg-white border-t border-black/5 py-20 lg:py-28">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl mb-12">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl text-dark-950 mb-4">More {t(name)} Services</h2>
          <p class="body-text text-lg">{t(sub['related_lede'])}</p>
        </div>
        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
{related}
        </div>
      </div>
    </section>

    <!-- ========== SUBURB CHIPS ========== -->
    <section class="bg-sand border-t border-black/5 py-16 lg:py-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl mb-10">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-2xl sm:text-3xl lg:text-4xl text-dark-950 mb-4">Driveways Around {t(name)}</h2>
          <p class="body-text text-base">{t(sub['chips_lede'])}</p>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
{chips}
        </div>
      </div>
    </section>

    <!-- ========== FAQ ========== -->
    <section id="faq" class="bg-white border-t border-black/5 py-20 lg:py-28">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="mb-12">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-4">Frequently Asked</h2>
          <p class="body-text text-lg">{t(sub['faq_lede'])}</p>
        </div>
        <div class="divide-y divide-black/10 border-y border-black/10">
{faqs}
        </div>
      </div>
    </section>

    <!-- ========== CTA BANNER ========== -->
    <section class="relative overflow-hidden py-20 lg:py-24 bg-brand-500 stripe-texture">
      <div class="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-4">Planning a Driveway in {t(name)}?</h2>
        <p class="text-dark-950/70 text-lg mb-8 max-w-2xl mx-auto" style="line-height: 1.7;">{t(CTA_LEDE)}</p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <a href="#contact" class="bg-dark-950 text-white font-bold uppercase tracking-wider px-8 py-4 text-base text-center hover:bg-dark-800" style="transition: background 0.2s ease;">Get a Free Quote</a>
          <a href="tel:{PHONE_TEL}" class="border-2 border-dark-950 text-dark-950 font-bold uppercase tracking-wider px-8 py-4 text-base text-center hover:bg-dark-950 hover:text-white" style="transition: background 0.2s ease, color 0.2s ease;">Call {PHONE_DISPLAY}</a>
        </div>
      </div>
    </section>

    <!-- ========== CONTACT FORM ========== -->
    <section id="contact" class="bg-sand py-20 lg:py-28 border-t border-black/5">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid lg:grid-cols-2 gap-12 lg:gap-20">
          <div>
            <div class="accent-bar mb-4"></div>
            <h2 class="heading-lg text-3xl sm:text-4xl text-dark-950 mb-6">Get a {t(name)} Driveway Quote</h2>
            <p class="body-text text-lg mb-8">Tell us about your site and we will get back to you within 24 hours. Fill out the form, call us on <a href="tel:{PHONE_TEL}" class="text-brand-500 font-medium hover:underline">{PHONE_DISPLAY}</a>, or email <a href="mailto:andrew@selectcivilgroup.com.au" class="text-brand-500 font-medium hover:underline">andrew@selectcivilgroup.com.au</a> or <a href="mailto:admin@selectcivilgroup.com.au" class="text-brand-500 font-medium hover:underline">admin@selectcivilgroup.com.au</a></p>
            <div class="space-y-5">
              <div class="border-l-2 border-black/10 pl-5"><p class="text-dark-950 text-sm font-bold">Phone</p><a href="tel:{PHONE_TEL}" class="text-gray-600 text-sm hover:text-brand-500" style="transition: color 0.2s ease;">{PHONE_DISPLAY}</a></div>
              <div class="border-l-2 border-black/10 pl-5"><p class="text-dark-950 text-sm font-bold">Email</p><a href="mailto:andrew@selectcivilgroup.com.au" class="text-gray-600 text-sm hover:text-brand-500 block" style="transition: color 0.2s ease;">andrew@selectcivilgroup.com.au</a><a href="mailto:admin@selectcivilgroup.com.au" class="text-gray-600 text-sm hover:text-brand-500 block" style="transition: color 0.2s ease;">admin@selectcivilgroup.com.au</a></div>
              <div class="border-l-2 border-black/10 pl-5"><p class="text-dark-950 text-sm font-bold">Service Area</p><p class="text-gray-600 text-sm">{t(name)}, Geelong, Bellarine Peninsula</p></div>
              <div class="border-l-2 border-black/10 pl-5"><p class="text-dark-950 text-sm font-bold">Hours</p><p class="text-gray-600 text-sm">Monday - Friday: 7:00 AM - 5:00 PM</p></div>
            </div>
          </div>
          <div class="bg-white border border-black/10 p-8" style="box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 12px 32px rgba(0,0,0,0.06);">
            <form action="https://formspree.io/f/xdawnnyp" method="POST" data-no-lead class="space-y-5">
              <input type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true" style="display:none">
              <input type="hidden" name="_next" value="https://selectcivilgroup.com.au/thank-you">
              <input type="hidden" name="_subject" value="New enquiry from selectcivilgroup.com.au - Concrete Driveways {a(name)} page">
              <input type="hidden" name="_source_page" value="{slug}.html">
              <div class="grid sm:grid-cols-2 gap-5">
                <div><label for="name" class="{label}">Name</label><input type="text" id="name" name="name" required placeholder="Your full name" class="{field}" style="transition: border-color 0.2s ease;"></div>
                <div><label for="phone" class="{label}">Phone</label><input type="tel" id="phone" name="phone" placeholder="Your phone number" class="{field}" style="transition: border-color 0.2s ease;"></div>
              </div>
              <div><label for="email" class="{label}">Email</label><input type="email" id="email" name="email" required placeholder="your@email.com" class="{field}" style="transition: border-color 0.2s ease;"></div>
              <div><label for="suburb" class="{label}">Suburb</label><input type="text" id="suburb" name="suburb" placeholder="{a(name)}, surrounding suburbs..." value="{a(name)}" class="{field}" style="transition: border-color 0.2s ease;"></div>
              <div><label for="service" class="{label}">Service</label><select id="service" name="service" class="w-full bg-white border border-black/10 px-4 py-3 text-dark-950 text-sm focus:outline-none focus:border-brand-500" style="transition: border-color 0.2s ease;"><option value="">Select a service</option>
{options}
                <option value="other">Other</option>
              </select></div>
              <div><label for="message" class="{label}">Project Details</label><textarea id="message" name="message" rows="5" required placeholder="Tell us about your project - location, scope, timeline..." class="{field} resize-none" style="transition: border-color 0.2s ease;"></textarea></div>
              <button type="submit" class="btn-fill w-full py-4 text-base">Send Enquiry</button>
              <p class="text-gray-600 text-xs text-center">We respond within 24 hours on business days.</p>
            </form>
          </div>
        </div>
      </div>
    </section>

"""


def render(tpl, sub):
    doc = head(tpl, sub) + main_body(sub) + tpl["tail"]
    if re.search("[–—]|&mdash;|&ndash;", doc):
        sys.exit(f"[gen_concrete_driveways] dash found in {sub['slug']}")
    return doc


# --------------------------------------------------------------------------- link-in patches

def patch(fn, old, new, *, done_marker):
    """Replace old with new exactly once, unless done_marker shows it already ran."""
    path = os.path.join(ROOT, fn)
    src = open(path, encoding="utf-8").read()
    if done_marker in src:
        return False
    if src.count(old) != 1:
        sys.exit(f"[gen_concrete_driveways] {fn}: expected 1 match for {old[:80]!r}, found {src.count(old)}")
    open(path, "w", encoding="utf-8").write(src.replace(old, new))
    return True


def link_in():
    changed = set()
    names = {s["slug"]: s["name"] for s in SUBURBS}

    # 1. The driveway parent page's area chips.
    for slug, name in names.items():
        old = f'<div class="bg-white border border-black/10 px-4 py-3 text-center"><p class="text-gray-700 text-sm font-semibold">{name}</p></div>'
        new = (f'<a href="concrete-driveway-{slug}" class="block bg-white border border-black/10 px-4 py-3 text-center hover:border-brand-500/40" '
               f'style="transition: border-color 0.2s ease;"><p class="text-gray-700 text-sm font-semibold">{name}</p></a>')
        if patch("concrete-driveways.html", old, new, done_marker=f'href="concrete-driveway-{slug}"'):
            changed.add("concrete-driveways")

    # 2. The Geelong driveway page's chips (it lists Lara and Leopold, not Drysdale).
    for slug in ("lara", "leopold"):
        name = names[slug]
        old = f'<div class="bg-sand border border-black/10 px-4 py-3 text-center"><p class="text-gray-700 text-sm font-semibold">{name}</p></div>'
        new = (f'<a href="concrete-driveway-{slug}" class="block bg-sand border border-black/10 px-4 py-3 text-center hover:border-brand-500/30" '
               f'style="transition: border-color 0.2s ease;"><p class="text-gray-700 text-sm font-semibold">{name}</p></a>')
        if patch("concrete-driveway-geelong.html", old, new, done_marker=f'href="concrete-driveway-{slug}"'):
            changed.add("concrete-driveway-geelong")

    # 3. Each suburb's existing pages: the Concrete Driveways card stops pointing at #contact.
    card_pages = {"lara": ["civil-works-lara", "retaining-walls-lara"],
                  "leopold": ["retaining-walls-leopold"],
                  "drysdale": ["retaining-walls-drysdale"]}
    card_re = re.compile(r'(Concrete Driveways</h3>\s*<p class="body-text text-sm mb-4">[^<]*</p>\s*)'
                         r'<a href="#contact"( class="[^"]*" style="[^"]*")>Quote my job &rarr;</a>')
    for slug, pages in card_pages.items():
        for page in pages:
            path = os.path.join(ROOT, page + ".html")
            src = open(path, encoding="utf-8").read()
            if f'href="concrete-driveway-{slug}"' in src:
                continue
            new_src, n = card_re.subn(
                lambda m: f'{m.group(1)}<a href="concrete-driveway-{slug}"{m.group(2)}>Concrete Driveways in {names[slug]} &rarr;</a>', src)
            if n != 1:
                sys.exit(f"[gen_concrete_driveways] {page}: expected 1 driveway card, found {n}")
            open(path, "w", encoding="utf-8").write(new_src)
            changed.add(page)

    # 4. The Leopold and Drysdale hubs have no driveway card; link the word in their FAQ.
    for slug in ("leopold", "drysdale"):
        page = f"civil-contractor-{slug}.html"
        old = '<p class="body-text text-base pb-6">Both. For homeowners and small builders that is everything from a single retaining wall or driveway through'
        new = (f'<p class="body-text text-base pb-6">Both. For homeowners and small builders that is everything from a single retaining wall or '
               f'<a href="concrete-driveway-{slug}" class="text-brand-500 font-medium hover:underline">driveway</a> through')
        if patch(page, old, new, done_marker=f'href="concrete-driveway-{slug}"'):
            changed.add(page[:-5])

    # 5. Homepage suburb index: a Concrete driveways link after each card's Civil contractor link.
    hubs = {"lara": "civil-works-lara", "leopold": "civil-contractor-leopold", "drysdale": "civil-contractor-drysdale"}
    path = os.path.join(ROOT, "index.html")
    src = open(path, encoding="utf-8").read()
    start, end = src.index("<!-- SUBURB-INDEX:START"), src.index("<!-- SUBURB-INDEX:END -->")
    block = src[start:end]
    for slug, hub in hubs.items():
        if f'href="concrete-driveway-{slug}"' in block:
            continue
        m = re.search(rf'( *)<a href="{hub}"( class="[^"]*" style="[^"]*")>Civil contractor</a>\n', block)
        if not m:
            sys.exit(f"[gen_concrete_driveways] index.html: no Civil contractor link for {hub} in the suburb index")
        add = f'{m.group(1)}<a href="concrete-driveway-{slug}"{m.group(2)}>Concrete driveways</a>\n'
        block = block[:m.end()] + add + block[m.end():]
        changed.add("index")
    open(path, "w", encoding="utf-8").write(src[:start] + block + src[end:])

    # 6. Services index + concrete-services: cards after the Geelong driveway card.
    eyebrow = {s["slug"]: s["eyebrow"] for s in SUBURBS}
    blurb = {"lara": "Driveways &amp; crossovers north of the city",
             "leopold": "New pours &amp; replacements at the Bellarine gateway",
             "drysdale": "Driveways for sloping Bellarine blocks"}
    for fn, bg in (("services.html", "bg-white"), ("concrete-services.html", "bg-sand")):
        path = os.path.join(ROOT, fn)
        src = open(path, encoding="utf-8").read()
        if 'href="concrete-driveway-lara"' in src:
            continue
        anchor = re.search(r'<a href="concrete-driveway-geelong" class="[^"]*"[^>]*>.*?</a>\n', src, re.S)
        if not anchor:
            sys.exit(f"[gen_concrete_driveways] {fn}: no Geelong driveway card to anchor on")
        cards = "".join(
            f"""        <a href="concrete-driveway-{slug}" class="{bg} border border-black/10 hover:border-brand-500/30 p-6 group" style="transition: border-color 0.3s ease;">
          <p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-2">{eyebrow[slug]}</p>
          <h3 class="heading-md text-xl text-dark-950 mb-1 group-hover:text-brand-500" style="transition: color 0.2s ease;">Concrete Driveways {names[slug]}</h3>
          <p class="body-text text-sm">{blurb[slug]}</p>
        </a>
""" for slug in names)
        open(path, "w", encoding="utf-8").write(src[:anchor.end()] + cards + src[anchor.end():])
        changed.add(fn[:-5])
    return changed


def update_sitemap(changed):
    src = open(SITEMAP, encoding="utf-8").read()
    for slug in sorted(changed):
        loc = f"{SITE}/" if slug == "index" else f"{SITE}/{slug}"
        pat = re.compile(rf"(<loc>{re.escape(loc)}</loc>\s*<lastmod>)[0-9-]+(</lastmod>)")
        src, n = pat.subn(rf"\g<1>{LASTMOD}\g<2>", src)
        if n != 1:
            sys.exit(f"[gen_concrete_driveways] sitemap: expected 1 entry for {loc}, found {n}")
    anchor = re.search(r"  <url>\n    <loc>https://selectcivilgroup\.com\.au/concrete-driveway-geelong</loc>.*?</url>\n", src, re.S)
    if not anchor:
        sys.exit("[gen_concrete_driveways] sitemap: no concrete-driveway-geelong entry to anchor on")
    add = ""
    for s in SUBURBS:
        loc = f"{SITE}/concrete-driveway-{s['slug']}"
        if f"<loc>{loc}</loc>" in src:
            continue
        add += f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{LASTMOD}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n"
    src = src[:anchor.end()] + add + src[anchor.end():]
    open(SITEMAP, "w", encoding="utf-8").write(src)


def main():
    tpl = load_template()
    for sub in SUBURBS:
        fn = f"concrete-driveway-{sub['slug']}.html"
        open(os.path.join(ROOT, fn), "w", encoding="utf-8").write(render(tpl, sub))
        print(f"[gen_concrete_driveways] wrote {fn}")
    changed = link_in()
    update_sitemap(changed)
    print(f"[gen_concrete_driveways] linked in from: {', '.join(sorted(changed)) or 'nothing new'}")


if __name__ == "__main__":
    main()
