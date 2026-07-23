#!/usr/bin/env python3
"""
Select Civil Group - service x suburb landing-page generator.

Deterministic. Reads one JSON per suburb from lp/_suburbs/*.json and renders one page per
priority service (retaining-walls, concrete-driveway, earthworks, site-cuts) for that suburb,
matching the EXISTING live city-LP template exactly. Then refreshes the LP block in sitemap.xml.

Run from the site root:  python3 .build/lp_render.py

Do NOT reuse the drifted _build_city_lps.py. This is the current generator.
Hard rules: NO em/en dashes anywhere (auto-normalised). Reuse only Tailwind classes already in
the compiled /styles.css (this file copies the template's classes verbatim). Unique local copy
per suburb (intro_context) so pages are not doorway clones.

See lp/_suburbs/README.md for the JSON schema.
"""

import html
import json
import os
import re

SITE = "https://selectcivilgroup.com.au"
PHONE_DISPLAY = "0483 092 615"
PHONE_TEL = "0483092615"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBURBS_DIR = os.path.join(ROOT, "lp", "_suburbs")
SITEMAP = os.path.join(ROOT, "sitemap.xml")


def nd(s):
    return s.replace("—", " - ").replace("–", "-").replace("&mdash;", "-").replace("&ndash;", "-")


def esc(s):
    return html.escape(nd(s), quote=True)


def catchment_sentence(items):
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


# --------------------------------------------------------------------------- service configs

SERVICES = {
    "retaining-walls": {
        "label": "Retaining Walls",
        "category": "Concrete Services", "category_slug": "concrete-services",
        "hero_img": "Assets/retaining-walls.jpeg",
        "og_img": "Assets/retaining-walls.jpeg",
        "title": "Retaining Walls {S} - Concrete Retaining Walls | Select Civil Group",
        "meta": "Concrete retaining walls in {S} and across {region_short}. Garden, structural and tiered walls built to engineering specs. Free quotes within 24 hours.",
        "hero_lede": "Engineered concrete retaining walls for {S} homeowners and builders. Blocks levelled, garden edges held back, structural walls built to engineering specs. Quotes back within 24 hours.",
        "intro_h2": "Retaining Walls, Built for {S}'s Terrain",
        "intro_delivery": "Select Civil Group is based in Geelong and works across {S} regularly. Whether you need a single garden wall, a structural wall holding back a building platform, or a multi-tier solution on a larger fall, we build to engineering specs with the right product for the load and the soil.",
        "cta_h2": "Got a Retaining Wall to Build in {S}?",
        "cta_lede": "Send the address and a quick description of the wall. We will come back with an obligation-free quote within 24 hours.",
        "faq": [
            ("Do you build retaining walls in {S} and around {region_name}?", "Yes. {catchment} are all within our regular service area. We are across {region_name} most weeks."),
            ("What does a retaining wall in {S} typically cost?", "Wall cost depends on length, height, soil retained, drainage requirements and access. A short garden wall is a different job to a structural wall holding a building platform. We give an obligation-free quote within 24 hours once we have the site details."),
            ("How long does a retaining wall job take?", "Most residential retaining walls take three to seven working days from site set-up through to clean-up, depending on length, height and the engineering involved. Larger structural and tiered walls can run longer. We confirm a programmed start and finish date as part of the quote."),
            ("Do you engage the engineer, or do I need to organise that?", "Either works. For straightforward residential walls we can recommend an engineer we have worked with locally and coordinate the design. If you already have an engineer or builder running the project, we work to their specifications and drawings."),
        ],
    },
    "concrete-driveway": {
        "label": "Concrete Driveways",
        "category": "Concrete Services", "category_slug": "concrete-services",
        "hero_img": "Assets/concrete-driveways.jpeg",
        "og_img": "Assets/concrete-driveways.jpeg",
        "title": "Concrete Driveways {S} - Plain, Exposed & Coloured | Select Civil Group",
        "meta": "Concrete driveways in {S} and across {region_short}. Plain, exposed aggregate, coloured and stencilled finishes, done right the first time. Free quotes within 24 hours.",
        "hero_lede": "Concrete driveways and crossovers for {S} homeowners and builders. Plain finishes, exposed aggregate, coloured or stencilled concrete, on a properly prepared base. Quotes back within 24 hours.",
        "intro_h2": "Concrete Driveways for {S} Homes",
        "intro_delivery": "Select Civil Group is based in Geelong and pours driveways across {S} and the surrounding suburbs. Plain, exposed aggregate, coloured or stencilled, laid on a properly prepared base with the drainage and crossover done right the first time.",
        "cta_h2": "Got a Driveway to Pour in {S}?",
        "cta_lede": "Send the address and the driveway size and finish. We will come back with an obligation-free quote within 24 hours.",
        "faq": [
            ("Do you pour concrete driveways in {S} and around {region_name}?", "Yes. {catchment} are all within our regular service area. We pour driveways and crossovers across {region_name} most weeks."),
            ("What does a concrete driveway in {S} cost?", "Driveway cost depends on area, finish (plain, exposed aggregate, coloured or stencilled), the base preparation required and access. We give an obligation-free quote within 24 hours once we have the size and finish."),
            ("How long does a concrete driveway take?", "Most residential driveways take a few days across base preparation, pour and cure, with the surface ready to take weight after the recommended cure time. We confirm the programme and the finish as part of the quote."),
            ("Do you handle the crossover and council requirements?", "Yes. Where a job involves a vehicle crossover to the street, we prepare and pour to council standards and can coordinate the requirements as part of the work."),
        ],
    },
    "earthworks": {
        "label": "Earthworks",
        "category": "Earthworks & Excavation", "category_slug": "earthworks-excavation",
        "hero_img": "Assets/earthworks.jpeg",
        "og_img": "Assets/earthworks.jpeg",
        "title": "Earthworks {S} - Site Preparation & Grading | Select Civil Group",
        "meta": "Earthworks in {S} and across {region_short}. Site clearing, bulk cut and fill, grading and compaction. Free quotes within 24 hours.",
        "hero_lede": "Site preparation, land clearing, bulk cut and fill, grading and compaction in {S}. Getting the ground right before anything else goes in. Quotes back within 24 hours.",
        "intro_h2": "Earthworks Built Around {S}",
        "intro_delivery": "Select Civil Group is based in Geelong and runs earthworks across {S} daily. Site clearing, bulk cut and fill, grading and compaction, with spoil cartage handled so the next trade arrives to a buildable site.",
        "cta_h2": "Got Earthworks to Move in {S}?",
        "cta_lede": "Send the address and a description of the site. We will come back with an obligation-free quote within 24 hours.",
        "faq": [
            ("Do you do earthworks in {S} and around {region_name}?", "Yes. {catchment} are all within our regular service area. We run earthworks across {region_name} daily."),
            ("What does an earthworks job in {S} cost?", "Earthworks cost depends on the volume of cut and fill, soil type, access and how much spoil has to be carted off site. We give an obligation-free quote within 24 hours once we have the site details and levels."),
            ("How long do earthworks take?", "Bulk earthworks on a residential lot are usually a matter of days depending on volume and access. Larger and staged sites run longer. We confirm a programmed start and finish date as part of the quote."),
            ("Do you handle spoil removal and compaction?", "Yes. Cartage and legal disposal of excess soil, and compaction of fill to the required levels, are handled as part of the job so the next trade arrives to a buildable site."),
        ],
    },
    "site-cuts": {
        "label": "Site Cuts",
        "category": "Earthworks & Excavation", "category_slug": "earthworks-excavation",
        "hero_img": "Assets/site-cuts.jpeg",
        "og_img": "Assets/site-cuts.jpeg",
        "title": "Site Cuts {S} - Level Building Platforms | Select Civil Group",
        "meta": "Site cuts in {S} and across {region_short}. Cut and fill to engineering levels, ready for footings and slabs. Free quotes within 24 hours.",
        "hero_lede": "A level building platform cut to your engineer's levels, ready for footings and slabs in {S}. Topsoil stripped, cut and fill balanced, spoil removed. Quotes back within 24 hours.",
        "intro_h2": "Building Platform Work in {S}",
        "intro_delivery": "Select Civil Group is based in Geelong and cuts building platforms across {S} and the surrounding estates. Topsoil stripped, cut and fill balanced to your engineer's levels, spoil removed, ready for footings and slab.",
        "cta_h2": "Got a Site to Cut in {S}?",
        "cta_lede": "Send the address and your levels or plans. We will come back with an obligation-free quote within 24 hours.",
        "faq": [
            ("Do you do site cuts in {S} and around {region_name}?", "Yes. {catchment} are all within our regular service area. We cut building platforms across {region_name} most weeks."),
            ("What does a site cut in {S} cost?", "A site cut is priced on the volume of cut and fill, the fall across the block, soil type, access and spoil disposal. Blocks with significant fall often pair a cut with retaining. We give an obligation-free quote within 24 hours once we have the levels."),
            ("How long does a site cut take?", "Most residential site cuts take one to a few days depending on the fall, soil and access. We confirm a programmed start and finish date, and coordinate with your builder or slab crew so the platform is ready when they are."),
            ("Do you cut to my engineer's levels?", "Yes. We cut and fill to your engineer's or surveyor's levels, balance the platform, remove spoil and hand over a level, compacted building platform ready for footings and slab."),
        ],
    },
}

# services-grid cards (all 4, page's own service rendered first)
CARDS = {
    "retaining-walls": ("Retaining Walls", "Assets/retaining-wall-1.jpg", "Engineered concrete retaining walls for residential and commercial blocks across {S}. Garden walls, structural walls holding back building platforms, or tiered solutions on larger falls. Designed to engineering specs and built to last."),
    "site-cuts": ("Site Cuts", "Assets/site-cut-1.jpg", "Precision cut and fill to engineering levels, ready for footings and slabs. Often paired with retaining walls when a block has significant fall. Spoil cartage and disposal handled as part of the job."),
    "concrete-driveway": ("Concrete Driveways", "Assets/concrete-driveways.jpeg", "Plain, exposed aggregate, coloured or stencilled driveways and crossovers across {S} and surrounding suburbs. Built for the weight of utes and trades, with proper drainage and finish."),
    "earthworks": ("Earthworks", "Assets/earthworks.jpeg", "Bulk earthworks, grading and levelling for new homes and infill development. We handle compaction and spoil disposal so the next trade arrives to a buildable site."),
}
CARD_ORDER = ["retaining-walls", "site-cuts", "concrete-driveway", "earthworks"]

SHARED_FAQ = [
    ("Do you work on residential jobs, or only large commercial sites?", "We work across residential, commercial and civil projects. For homeowners and small builders that is everything from a single retaining wall or driveway through to a full site cut and slab. For larger projects we partner with builders, developers and contractors across Geelong and the surrounding region."),
    ("Are you fully insured?", "Yes. Select Civil Group carries full public liability insurance and workers compensation cover on every job. Certificates of currency are available on request."),
]

# Per-suburb hub ("civil contractor <suburb>"): the broad landing page that links to the 4
# service pages as spokes. Same config shape as a SERVICES entry.
HUB = {
    "label": "Civil Contractor",
    "category": "Services", "category_slug": "services",
    "hero_img": "Assets/earthworks.jpeg",
    "og_img": "Assets/earthworks.jpeg",
    "title": "Civil Contractor {S} - Earthworks, Concrete & Retaining | Select Civil Group",
    "meta": "Civil contractor in {S}. Earthworks, site cuts, retaining walls and concrete driveways for {S} homes and builders. Free quotes within 24 hours.",
    "hero_lede": "Earthworks, site cuts, retaining walls and concrete driveways for {S} homeowners and builders. One local team from the first site cut to the final pour. Quotes back within 24 hours.",
    "intro_h2": "Civil Works Across {S}",
    "intro_delivery": "Select Civil Group is based in Geelong and works across {S} regularly, handling the earthworks, retaining and concrete on residential, commercial and civil projects. One team and one point of contact, from site preparation through to the finished driveway.",
    "cta_h2": "Got a Project in {S}?",
    "cta_lede": "Send the address and a quick description of the work. We will come back with an obligation-free quote within 24 hours.",
    "grid_heading": "Our {S} Civil Services",
    "faq": [
        ("Do you work across {S} and around {region_name}?", "Yes. {catchment} are all within our regular service area. We are across {region_name} most weeks."),
        ("What civil services do you offer in {S}?", "Retaining walls, concrete driveways, earthworks and site cuts are the services {S} homeowners and builders ask for most. We also handle raft slabs, paving, detail excavation and excess soil removal. If it is earthworks, concrete or retaining, we can quote it."),
        ("Do you do the whole job, or just one part?", "Either. Many {S} jobs pair a site cut with retaining and a driveway, and we can run the lot as one coordinated job. If you only need a single service, that is fine too."),
        ("How fast do you get a quote back?", "Most quotes come back within 24 hours once we have the site address and a description of the work. For larger jobs we walk the block first to check access, soil and levels."),
    ],
}

# --------------------------------------------------------------------------- chrome (verbatim from the live template; plain strings, no f-substitution)

STYLE = """  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    .skip-link { position: absolute; top: -40px; left: 0; background: #0a0a0a; color: #d4912a; padding: 0.75rem 1.25rem; font-weight: 700; font-size: 0.875rem; letter-spacing: 0.05em; text-transform: uppercase; z-index: 100; text-decoration: none; transition: top 200ms ease; }
    .skip-link:focus { top: 0; outline: 2px solid #e8a840; outline-offset: 0; }
    .heading-xl { font-weight: 900; letter-spacing: -0.04em; line-height: 0.95; text-transform: uppercase; }
    .heading-lg { font-weight: 800; letter-spacing: -0.03em; line-height: 1; text-transform: uppercase; }
    .heading-md { font-weight: 700; letter-spacing: -0.02em; line-height: 1.1; text-transform: uppercase; }
    .body-text { line-height: 1.7; color: #52525b; }
    .btn-fill { background: #d4912a; color: #0a0a0a; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; transition: transform 0.2s ease, opacity 0.2s ease; }
    .btn-fill:hover { transform: translateY(-2px); opacity: 0.9; }
    .btn-fill:active { transform: translateY(0); }
    .btn-fill:focus-visible { outline: 2px solid #e8a840; outline-offset: 2px; }
    .btn-outline { border: 2px solid #d4912a; color: #d4912a; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; transition: transform 0.2s ease, background 0.2s ease, color 0.2s ease; }
    .btn-outline:hover { background: #d4912a; color: #0a0a0a; transform: translateY(-2px); }
    .btn-outline:active { transform: translateY(0); }
    .btn-outline:focus-visible { outline: 2px solid #e8a840; outline-offset: 2px; }
    .nav-link { transition: color 0.2s ease; }
    .nav-link:hover { color: #d4912a; }
    .btn-nav-fill { background: #0a0a0a; color: #ffffff; font-weight: 600; border-radius: 8px; transition: background-color 0.2s ease, transform 0.2s ease; display: inline-flex; align-items: center; justify-content: center; }
    .btn-nav-fill:hover { background: #2e2e2e; }
    .btn-nav-fill:active { transform: scale(0.98); }
    .mega-trigger { position: relative; }
    .mega-dropdown { position: absolute; top: 100%; left: 0; opacity: 0; visibility: hidden; pointer-events: none; transform: translateY(8px); transition: opacity 0.25s ease, transform 0.25s ease, visibility 0.25s ease; z-index: 60; }
    .mega-trigger:hover .mega-dropdown, .mega-dropdown:hover { opacity: 1; visibility: visible; pointer-events: auto; transform: translateY(0); }
    .mega-trigger:hover .mega-dropdown { transition-delay: 0s; }
    .mega-dropdown::before { content: ''; position: absolute; top: -16px; left: 0; right: 0; height: 16px; }
    .mega-chevron { transition: transform 0.25s ease; }
    .mega-trigger:hover .mega-chevron { transform: rotate(180deg); }
    nav { transition: transform 0.3s ease, border-bottom-color 0.2s ease; }
    nav.nav-hidden { transform: translateY(-100%); }
    .mobile-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 40; opacity: 0; visibility: hidden; transition: opacity 0.3s ease, visibility 0.3s ease; }
    .mobile-backdrop.open { opacity: 1; visibility: visible; }
    .mobile-menu { transform: translateX(-100%); transition: transform 0.3s ease; }
    .mobile-menu.open { transform: translateX(0); }
    .mobile-services-list { max-height: 0; overflow: hidden; transition: max-height 0.3s ease; }
    .mobile-services-list.open { max-height: 600px; }
    .accent-bar { width: 48px; height: 4px; background: #d4912a; }
    .stripe-texture::before { content: ''; position: absolute; inset: 0; background-image: repeating-linear-gradient(90deg, transparent, transparent 3px, rgba(255,255,255,0.015) 3px, rgba(255,255,255,0.015) 4px); pointer-events: none; z-index: 1; }
  </style>
"""

NAV = """  <a href="#main" class="skip-link">Skip to main content</a>

  <nav class="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-black/5">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="grid grid-cols-3 items-center h-16">
        <div class="flex items-center justify-start">
          <button onclick="toggleMobileMenu()" class="lg:hidden -ml-2 p-2 text-gray-700 hover:text-dark-950 focus-visible:outline-2 focus-visible:outline-brand-500" aria-label="Open menu">
            <svg id="hamburger-icon" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 6h16M4 12h16M4 18h16"/></svg>
            <svg id="close-icon" class="w-6 h-6 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
          <div class="hidden lg:flex items-center gap-8">
            <a href="projects" class="nav-link text-gray-700 text-[15px] font-medium">Projects</a>
            <a href="about" class="nav-link text-gray-700 text-[15px] font-medium">About</a>
            <a href="contact" class="nav-link text-gray-700 text-[15px] font-medium">Contact</a>
            <div class="mega-trigger">
              <a href="services" class="nav-link text-gray-700 text-[15px] font-medium flex items-center gap-1.5">Services<svg class="mega-chevron w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"/></svg></a>
              <div class="mega-dropdown" style="width: 520px; left: -40px;">
                <div class="bg-white border border-black/10 rounded-lg p-5" style="box-shadow: 0 25px 60px rgba(0,0,0,0.12), 0 0 0 1px rgba(0,0,0,0.04);">
                  <div class="grid grid-cols-2 gap-6">
                    <div>
                      <a href="concrete-services" class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-3 block hover:text-brand-400" style="transition: color 0.2s ease;">Concrete Services</a>
                      <div class="flex flex-col gap-0.5">
                        <a href="retaining-walls" class="mega-service-link text-gray-600 text-sm py-1.5 hover:text-dark-950" style="transition: color 0.2s ease;">Retaining Walls</a>
                        <a href="concrete-driveways" class="mega-service-link text-gray-600 text-sm py-1.5 hover:text-dark-950" style="transition: color 0.2s ease;">Concrete Driveways</a>
                        <a href="concrete-raft-slabs" class="mega-service-link text-gray-600 text-sm py-1.5 hover:text-dark-950" style="transition: color 0.2s ease;">Concrete Raft Slabs</a>
                        <a href="concrete-paving" class="mega-service-link text-gray-600 text-sm py-1.5 hover:text-dark-950" style="transition: color 0.2s ease;">Concrete Paving</a>
                        <a href="factory-tilt-panels" class="mega-service-link text-gray-600 text-sm py-1.5 hover:text-dark-950" style="transition: color 0.2s ease;">Factory Tilt Panels</a>
                        <a href="concrete-seating" class="mega-service-link text-gray-600 text-sm py-1.5 hover:text-dark-950" style="transition: color 0.2s ease;">Concrete Seating</a>
                        <a href="concrete-bench-drops" class="mega-service-link text-gray-600 text-sm py-1.5 hover:text-dark-950" style="transition: color 0.2s ease;">Concrete Bench Drops</a>
                      </div>
                    </div>
                    <div>
                      <a href="earthworks-excavation" class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-3 block hover:text-brand-400" style="transition: color 0.2s ease;">Earthworks &amp; Excavation</a>
                      <div class="flex flex-col gap-0.5">
                        <a href="earthworks" class="mega-service-link text-gray-600 text-sm py-1.5 hover:text-dark-950" style="transition: color 0.2s ease;">Earthworks</a>
                        <a href="site-cuts" class="mega-service-link text-gray-600 text-sm py-1.5 hover:text-dark-950" style="transition: color 0.2s ease;">Site Cuts</a>
                        <a href="detail-excavation" class="mega-service-link text-gray-600 text-sm py-1.5 hover:text-dark-950" style="transition: color 0.2s ease;">Detail Excavation</a>
                        <a href="excess-soil-removal" class="mega-service-link text-gray-600 text-sm py-1.5 hover:text-dark-950" style="transition: color 0.2s ease;">Excess Soil Removal</a>
                      </div>
                    </div>
                  </div>
                  <div class="border-t border-black/5 mt-4 pt-3">
                    <a href="services" class="text-gray-500 text-xs font-semibold hover:text-brand-500 flex items-center gap-1.5" style="transition: color 0.2s ease;">View all services <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg></a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <a href="/" class="flex items-center justify-center"><img src="Assets/Logo PNG.png" alt="Select Civil Group logo" width="2667" height="2106" class="h-11 w-auto"></a>
        <div class="flex items-center justify-end gap-5">
          <a href="tel:0483092615" class="hidden lg:inline nav-link text-gray-700 text-[15px] font-medium">0483 092 615</a>
          <span class="hidden lg:inline-block w-px h-5 bg-black/15" aria-hidden="true"></span>
          <a href="contact" class="btn-nav-fill text-[15px] px-4 py-2 lg:px-5 lg:py-2.5">Get a Quote</a>
        </div>
      </div>
    </div>
  </nav>
  <div id="mobile-backdrop" class="mobile-backdrop lg:hidden" onclick="toggleMobileMenu()"></div>
  <div id="mobile-menu" class="mobile-menu fixed top-16 left-0 bottom-0 w-full sm:w-80 bg-white sm:border-r border-black/5 p-8 lg:hidden z-50 overflow-y-auto">
    <div class="flex flex-col gap-1">
      <a href="projects" onclick="toggleMobileMenu()" class="text-gray-800 text-lg font-semibold hover:text-brand-500 py-3" style="transition: color 0.2s ease;">Projects</a>
      <a href="about" onclick="toggleMobileMenu()" class="text-gray-800 text-lg font-semibold hover:text-brand-500 py-3" style="transition: color 0.2s ease;">About</a>
      <a href="contact" onclick="toggleMobileMenu()" class="text-gray-800 text-lg font-semibold hover:text-brand-500 py-3" style="transition: color 0.2s ease;">Contact</a>
      <button onclick="toggleMobileServices()" class="flex items-center justify-between w-full text-gray-800 text-lg font-semibold hover:text-brand-500 py-3" style="transition: color 0.2s ease;">Services<svg id="mobile-services-chevron" class="w-5 h-5" style="transition: transform 0.3s ease;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"/></svg></button>
      <div id="mobile-services-list" class="mobile-services-list pl-4">
        <div class="border-l-2 border-brand-500/30 pl-4 flex flex-col gap-0.5 pb-3">
          <p class="text-brand-500 text-xs font-bold uppercase tracking-widest pt-1 pb-1">Concrete Services</p>
          <a href="retaining-walls" onclick="toggleMobileMenu()" class="text-gray-600 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Retaining Walls</a>
          <a href="concrete-driveways" onclick="toggleMobileMenu()" class="text-gray-600 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Concrete Driveways</a>
          <a href="concrete-raft-slabs" onclick="toggleMobileMenu()" class="text-gray-600 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Concrete Raft Slabs</a>
          <a href="concrete-paving" onclick="toggleMobileMenu()" class="text-gray-600 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Concrete Paving</a>
          <a href="factory-tilt-panels" onclick="toggleMobileMenu()" class="text-gray-600 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Factory Tilt Panels</a>
          <a href="concrete-seating" onclick="toggleMobileMenu()" class="text-gray-600 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Concrete Seating</a>
          <a href="concrete-bench-drops" onclick="toggleMobileMenu()" class="text-gray-600 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Concrete Bench Drops</a>
          <p class="text-brand-500 text-xs font-bold uppercase tracking-widest pt-3 pb-1">Earthworks &amp; Excavation</p>
          <a href="earthworks" onclick="toggleMobileMenu()" class="text-gray-600 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Earthworks</a>
          <a href="site-cuts" onclick="toggleMobileMenu()" class="text-gray-600 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Site Cuts</a>
          <a href="detail-excavation" onclick="toggleMobileMenu()" class="text-gray-600 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Detail Excavation</a>
          <a href="excess-soil-removal" onclick="toggleMobileMenu()" class="text-gray-600 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Excess Soil Removal</a>
          <a href="services" onclick="toggleMobileMenu()" class="text-gray-500 text-xs font-semibold pt-3 hover:text-brand-500 flex items-center gap-1.5" style="transition: color 0.2s ease;">View all services <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg></a>
        </div>
      </div>
      <div class="border-t border-black/10 mt-4 pt-4 flex flex-col gap-3">
        <a href="tel:0483092615" onclick="toggleMobileMenu()" class="text-gray-800 text-base font-medium text-center py-2">0483 092 615</a>
        <a href="contact" onclick="toggleMobileMenu()" class="btn-nav-fill text-center px-6 py-3">Get a Quote</a>
      </div>
    </div>
  </div>
"""

FOOTER = """  <footer class="bg-dark-900 pt-20 pb-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col lg:flex-row justify-between gap-12 mb-10">
        <div class="max-w-xl">
          <h2 class="heading-xl text-4xl sm:text-5xl lg:text-6xl text-white mb-6">Let's Build Something Solid Together</h2>
          <p class="text-gray-400 text-base mb-8" style="line-height: 1.7;">From initial site assessment to final cleanup, we're here for your project.</p>
          <div class="flex flex-wrap gap-3">
            <a href="contact" class="btn-fill px-7 py-3 text-sm">Get a Quote</a>
            <a href="tel:0483092615" class="btn-outline px-7 py-3 text-sm">Call</a>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-x-12 gap-y-6">
          <div>
            <p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-4">Site</p>
            <div class="flex flex-col gap-3">
              <a href="/" class="text-white text-sm font-bold hover:text-brand-500" style="transition: color 0.2s ease;">Home</a>
              <a href="services" class="text-white text-sm font-bold hover:text-brand-500" style="transition: color 0.2s ease;">Services</a>
              <a href="about" class="text-white text-sm font-bold hover:text-brand-500" style="transition: color 0.2s ease;">About</a>
              <a href="projects" class="text-white text-sm font-bold hover:text-brand-500" style="transition: color 0.2s ease;">Projects</a>
              <a href="contact" class="text-white text-sm font-bold hover:text-brand-500" style="transition: color 0.2s ease;">Contact</a>
            </div>
          </div>
          <div>
            <p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-4">Contact</p>
            <div class="flex flex-col gap-3">
              <a href="tel:0483092615" class="text-gray-400 text-sm hover:text-brand-500" style="transition: color 0.2s ease;">0483 092 615</a>
              <a href="mailto:andrew@selectcivilgroup.com.au" class="text-gray-400 text-sm hover:text-brand-500 break-words" style="transition: color 0.2s ease;">andrew@selectcivilgroup.com.au</a>
              <a href="mailto:admin@selectcivilgroup.com.au" class="text-gray-400 text-sm hover:text-brand-500 break-words" style="transition: color 0.2s ease;">admin@selectcivilgroup.com.au</a>
              <p class="text-gray-400 text-sm">Geelong, VIC 3226</p>
              <p class="text-gray-400 text-sm">Mon-Fri 7:00am - 5:00pm</p>
            </div>
          </div>
        </div>
      </div>
      <div class="border-t border-white/5 pt-8 flex flex-col sm:flex-row justify-between items-center gap-6">
        <div class="flex items-center gap-4">
          <p class="text-gray-600 text-xs">&copy; 2026 Select Civil Group Pty Ltd. All rights reserved.</p>
          <a href="privacy" class="text-gray-500 text-xs hover:text-white" style="transition: color 0.2s ease;">Privacy Policy</a>
        </div>
        <a href="https://www.instagram.com/select_civil_group_pty_ltd/" target="_blank" rel="noopener noreferrer" class="text-gray-500 hover:text-white" style="transition: color 0.2s ease;" aria-label="Instagram"><svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg></a>
      </div>
    </div>
  </footer>
  <div class="lg:hidden h-20" aria-hidden="true"></div>
  <div class="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-black/10 grid grid-cols-2 gap-2 p-2" style="padding-bottom: max(0.5rem, env(safe-area-inset-bottom)); box-shadow: 0 -4px 16px rgba(0,0,0,0.06);">
    <a href="tel:0483092615" class="flex items-center justify-center gap-2 bg-dark-950 text-white text-sm font-bold uppercase tracking-wider py-3 rounded-md hover:bg-dark-800" style="transition: background-color 0.2s ease;" aria-label="Call Select Civil Group"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>Call</a>
    <a href="#contact" class="flex items-center justify-center gap-2 bg-brand-500 text-dark-950 text-sm font-bold uppercase tracking-wider py-3 rounded-md hover:bg-brand-400" style="transition: background-color 0.2s ease;" aria-label="Get a quote from Select Civil Group">Get a Quote</a>
  </div>
"""

SCRIPTS = """  <script>
    function toggleMobileMenu() {
      const menu = document.getElementById('mobile-menu');
      const backdrop = document.getElementById('mobile-backdrop');
      const hamburger = document.getElementById('hamburger-icon');
      const close = document.getElementById('close-icon');
      menu.classList.toggle('open');
      backdrop.classList.toggle('open');
      hamburger.classList.toggle('hidden');
      close.classList.toggle('hidden');
      document.body.style.overflow = menu.classList.contains('open') ? 'hidden' : '';
    }
    function toggleMobileServices() {
      const list = document.getElementById('mobile-services-list');
      const chevron = document.getElementById('mobile-services-chevron');
      list.classList.toggle('open');
      chevron.style.transform = list.classList.contains('open') ? 'rotate(180deg)' : 'rotate(0deg)';
    }
    function toggleFaq(btn) {
      const answer = btn.nextElementSibling;
      const chevron = btn.querySelector('.faq-chevron');
      const isOpen = answer.style.maxHeight !== '0px' && answer.style.maxHeight !== '';
      document.querySelectorAll('.faq-answer').forEach(a => { a.style.maxHeight = '0px'; a.style.opacity = '0'; });
      document.querySelectorAll('.faq-chevron').forEach(c => { c.style.transform = 'rotate(0deg)'; });
      if (!isOpen) { answer.style.maxHeight = answer.scrollHeight + 'px'; answer.style.opacity = '1'; chevron.style.transform = 'rotate(180deg)'; }
    }
    const nav = document.querySelector('nav');
    let lastScrollY = window.scrollY;
    window.addEventListener('scroll', () => {
      const currentScrollY = window.scrollY;
      if (currentScrollY > lastScrollY && currentScrollY > 80) { nav.classList.add('nav-hidden'); } else { nav.classList.remove('nav-hidden'); }
      nav.style.borderBottomColor = currentScrollY > 20 ? 'rgba(0,0,0,0.08)' : 'rgba(0,0,0,0.04)';
      lastScrollY = currentScrollY;
    });
  </script>
"""


# --------------------------------------------------------------------------- schema + head

def build_schema(svc, sub, canonical, faqs):
    area = [{"@type": "City", "name": n} for n in sub["catchment"]]
    graph = [
        {
            "@type": "Service",
            "serviceType": svc["label"],
            "name": f'{svc["label"]} {sub["name"]}',
            "description": nd(f'{svc["label"]} in {sub["name"]} and across {sub["region_short"]} by Select Civil Group.'),
            "provider": {
                "@type": "LocalBusiness",
                "@id": SITE + "/#business",
                "name": "Select Civil Group Pty Ltd",
                "telephone": "+61483092615",
                "url": SITE + "/",
            },
            "areaServed": area,
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": svc["category"], "item": f'{SITE}/{svc["category_slug"]}'},
                {"@type": "ListItem", "position": 3, "name": sub["name"], "item": canonical},
            ],
        },
        {
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": nd(q),
                 "acceptedAnswer": {"@type": "Answer", "text": nd(a)}}
                for q, a in faqs
            ],
        },
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2)


def head(*, title, meta, canonical, sub, og_img, schema):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(meta)}">
  <link rel="canonical" href="{canonical}">

  <meta name="geo.region" content="AU-VIC">
  <meta name="geo.placename" content="{esc(sub['name'])}">
  <meta name="geo.position" content="{sub['lat']};{sub['lng']}">
  <meta name="ICBM" content="{sub['lat']}, {sub['lng']}">

  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(meta)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="Select Civil Group">
  <meta property="og:locale" content="en_AU">
  <meta property="og:image" content="{SITE}/{og_img}">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(meta)}">
  <meta name="twitter:image" content="{SITE}/{og_img}">

  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <meta name="theme-color" content="#ffffff">
  <link rel="stylesheet" href="/styles.css">

  <link rel="preload" href="/Assets/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/Assets/fonts/fonts.css">

  <script type="application/ld+json">
{schema}
  </script>

{STYLE}  <script defer src="/js/analytics.js"></script>
</head>
<body class="bg-white text-dark-950 font-body">

"""


# --------------------------------------------------------------------------- section builders

def services_grid(page_key, sub, hub=False):
    """4-service grid. On a hub every card links to its <service>-<suburb> spoke. On a service
    page the own-service card goes to #contact and siblings link to their <service>-<suburb> page
    (when that page exists for the suburb), so the suburb's pages interlink."""
    slug = sub["slug"]
    generated = set(sub.get("services", list(SERVICES.keys())))
    order = CARD_ORDER if hub else [page_key] + [k for k in CARD_ORDER if k != page_key]
    cards = []
    for k in order:
        title, img, desc = CARDS[k]
        desc = esc(desc.replace("{S}", sub["name"]))
        if not hub and k == page_key:
            href, cta = "#contact", "Quote my job &rarr;"
        elif k in generated:
            href, cta = f"{k}-{slug}.html", f"{esc(title)} in {esc(sub['name'])} &rarr;"
        else:
            href, cta = "#contact", "Quote my job &rarr;"
        cards.append(f"""          <article class="bg-white border border-black/10 p-8 hover:border-brand-500/30" style="transition: border-color 0.3s ease;">
            <div class="relative overflow-hidden mb-6" style="aspect-ratio: 4/3;"><img src="{img}" alt="{esc(title)} by Select Civil Group in {esc(sub['name'])}" width="800" height="600" class="w-full h-full object-cover" loading="lazy" decoding="async"></div>
            <h3 class="heading-md text-xl sm:text-2xl text-dark-950 mb-3">{esc(title)}</h3>
            <p class="body-text text-sm mb-4">{desc}</p>
            <a href="{href}" class="text-brand-500 text-sm font-bold uppercase tracking-wider hover:text-brand-400" style="transition: color 0.2s ease;">{cta}</a>
          </article>""")
    return "\n".join(cards)


def process_section(name):
    steps = [
        ("Enquiry", "Send the site address, a quick description of the work, and any plans or photos you have. The more we know, the sharper the quote."),
        ("Site Walk", "For larger jobs, we visit the block to check access, soil, levels and obstacles the photos don't show. Most quotes come back within 24 hours."),
        ("Fixed Quote", "Itemised, written, and locked in. Spoil cartage, disposal and machinery are accounted for so there are no surprises at the end."),
        ("Programmed Start", "Confirmed start and finish dates that we hold to. We coordinate with your builder, engineer, or following trades so the ground is ready when they are."),
        ("On Site", "Machine and operator on the ground, working to your engineer's specs. Daily check-ins with whoever is coordinating the build."),
        ("Handover", "Final levels checked, site cleaned, and your site is ready for the next stage. We are still a phone call away if something comes up later."),
    ]
    cells = []
    for i, (t, d) in enumerate(steps, 1):
        cells.append(f'<div class="bg-sand border border-black/10 p-7"><p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-2">Step {i:02d}</p><h3 class="heading-md text-lg text-dark-950 mb-3">{esc(t)}</h3><p class="body-text text-sm">{esc(d)}</p></div>')
    return "\n          ".join(cells)


def chips_section(sub):
    chips = "\n          ".join(
        f'<div class="bg-white border border-black/10 px-4 py-3 text-center"><p class="text-gray-700 text-sm font-semibold">{esc(c)}</p></div>'
        for c in sub["catchment"]
    )
    return chips


def faq_section(faqs):
    rows = []
    for q, a in faqs:
        rows.append(f"""          <div class="faq-item">
            <button onclick="toggleFaq(this)" class="w-full flex items-center justify-between py-6 text-left group focus-visible:outline-2 focus-visible:outline-brand-500 focus-visible:outline-offset-2">
              <h3 class="text-dark-950 text-lg sm:text-xl font-semibold pr-8" style="letter-spacing: -0.01em;">{esc(q)}</h3>
              <svg class="faq-chevron w-5 h-5 text-gray-400 shrink-0" style="transition: transform 0.3s ease;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div class="faq-answer overflow-hidden" style="max-height: 0; transition: max-height 0.3s ease, opacity 0.3s ease; opacity: 0;">
              <p class="body-text text-base pb-6">{esc(a)}</p>
            </div>
          </div>""")
    return "\n".join(rows)


def service_options(selected):
    concrete = [("retaining-walls", "Retaining Walls"), ("concrete-driveways", "Concrete Driveways"),
                ("concrete-raft-slabs", "Concrete Raft Slabs"), ("concrete-paving", "Concrete Paving"),
                ("factory-tilt-panels", "Factory Tilt Panels"), ("concrete-seating", "Concrete Seating"),
                ("concrete-bench-drops", "Concrete Bench Drops")]
    earth = [("earthworks", "Earthworks"), ("site-cuts", "Site Cuts"),
             ("detail-excavation", "Detail Excavation"), ("excess-soil-removal", "Excess Soil Removal")]
    def opts(items):
        out = []
        for val, lab in items:
            sel = " selected" if val == selected else ""
            out.append(f'<option value="{val}"{sel}>{lab}</option>')
        return "\n                    ".join(out)
    return (f'<optgroup label="Concrete Services">\n                    {opts(concrete)}\n                  </optgroup>\n'
            f'                  <optgroup label="Earthworks &amp; Excavation">\n                    {opts(earth)}\n                  </optgroup>')


# --------------------------------------------------------------------------- page render

def render(svc_key, sub):
    svc = SERVICES[svc_key]
    S = sub["name"]
    slug = f"{svc_key}-{sub['slug']}"
    canonical = f"{SITE}/{slug}"
    ctx = {"S": S, "region_name": sub["region_name"], "region_short": sub["region_short"],
           "catchment": catchment_sentence(sub["catchment"])}

    def fill(t):
        return t.format(**ctx)

    faqs = [(fill(q), fill(a)) for q, a in svc["faq"]] + SHARED_FAQ
    title = fill(svc["title"])
    meta = fill(svc["meta"])
    schema = build_schema(svc, sub, canonical, faqs)

    doc = head(title=title, meta=meta, canonical=canonical, sub=sub, og_img=svc["og_img"], schema=schema)
    doc += NAV
    doc += '\n  <main id="main">\n'
    # breadcrumb
    doc += f"""
    <nav aria-label="Breadcrumb" class="bg-sand border-b border-black/5 pt-20 lg:pt-24">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <ol class="flex items-center gap-2 text-xs text-gray-500">
          <li><a href="/" class="hover:text-brand-500" style="transition: color 0.2s ease;">Home</a></li>
          <li aria-hidden="true" class="text-gray-400">/</li>
          <li><a href="{svc['category_slug']}" class="hover:text-brand-500" style="transition: color 0.2s ease;">{esc(svc['category'])}</a></li>
          <li aria-hidden="true" class="text-gray-400">/</li>
          <li class="text-gray-700" aria-current="page">{esc(S)}</li>
        </ol>
      </div>
    </nav>

    <section class="relative">
      <div class="relative overflow-hidden" style="height: 420px;">
        <img src="{svc['hero_img']}" alt="{esc(svc['label'])} by Select Civil Group in {esc(S)}" width="1600" height="900" class="w-full h-full object-cover" fetchpriority="high">
        <div class="absolute inset-0 bg-black/60"></div>
        <div class="absolute inset-0 bg-gradient-to-t from-dark-950 via-transparent to-transparent"></div>
        <div class="absolute inset-0 flex items-center">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
            <div class="accent-bar mb-4"></div>
            <p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-3">{esc(sub['region_eyebrow'])}</p>
            <h1 class="heading-xl text-4xl sm:text-5xl md:text-6xl text-white mb-4">{esc(svc['label'])} in {esc(S)}</h1>
            <p class="text-gray-300 text-lg max-w-2xl" style="line-height: 1.7;">{esc(fill(svc['hero_lede']))}</p>
            <div class="flex flex-col sm:flex-row gap-3 mt-6">
              <a href="#contact" class="btn-fill px-7 py-3 text-sm">Get a {esc(S)} Quote</a>
              <a href="tel:{PHONE_TEL}" class="btn-outline px-7 py-3 text-sm">Call {PHONE_DISPLAY}</a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="bg-white py-20 lg:py-28">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-6">{esc(fill(svc['intro_h2']))}</h2>
          <div class="space-y-4 body-text text-lg">
            <p>{esc(sub['intro_context'])}</p>
            <p>{esc(fill(svc['intro_delivery']))}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="bg-sand border-t border-black/5 py-20 lg:py-28">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl mb-12">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-6">Wall, Slab and Site Services for {esc(S)} Projects</h2>
          <p class="body-text text-lg">The four services {esc(S)} homeowners and builders pair most often. Every job is quoted on the specifics of your site.</p>
          <p class="mt-3"><a href="civil-contractor-{sub['slug']}.html" class="text-brand-500 text-sm font-bold uppercase tracking-wider hover:text-brand-400" style="transition: color 0.2s ease;">All civil services in {esc(S)} &rarr;</a></p>
        </div>
        <div class="grid md:grid-cols-2 gap-6 lg:gap-8">
{services_grid(svc_key, sub)}
        </div>
      </div>
    </section>

    <section class="bg-white border-t border-black/5 py-20 lg:py-28">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl mb-12">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-6">How a {esc(S)} Job Runs</h2>
          <p class="body-text text-lg">Quote to handover, the same six steps on every job. No surprises, no scope creep, no chasing for updates.</p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          {process_section(S)}
        </div>
      </div>
    </section>

    <section class="bg-sand border-t border-black/5 py-16 lg:py-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl mb-10">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-2xl sm:text-3xl lg:text-4xl text-dark-950 mb-4">Around {esc(S)}</h2>
          <p class="body-text text-base">{esc(sub['chips_lede'])}</p>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {chips_section(sub)}
        </div>
      </div>
    </section>

    <section id="faq" class="bg-white border-t border-black/5 py-20 lg:py-28">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="mb-12">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-4">Frequently Asked</h2>
          <p class="body-text text-lg">The questions we get most from {esc(S)} homeowners and builders.</p>
        </div>
        <div class="divide-y divide-black/10 border-y border-black/10">
{faq_section(faqs)}
        </div>
      </div>
    </section>

    <section class="relative overflow-hidden py-20 lg:py-24 bg-brand-500 stripe-texture">
      <div class="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-4">{esc(fill(svc['cta_h2']))}</h2>
        <p class="text-dark-950/70 text-lg mb-8 max-w-2xl mx-auto" style="line-height: 1.7;">{esc(fill(svc['cta_lede']))}</p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <a href="#contact" class="bg-dark-950 text-white font-bold uppercase tracking-wider px-8 py-4 text-base text-center hover:bg-dark-800" style="transition: background 0.2s ease;">Get a Free Quote</a>
          <a href="tel:{PHONE_TEL}" class="border-2 border-dark-950 text-dark-950 font-bold uppercase tracking-wider px-8 py-4 text-base text-center hover:bg-dark-950 hover:text-white" style="transition: background 0.2s ease, color 0.2s ease;">Call {PHONE_DISPLAY}</a>
        </div>
      </div>
    </section>

    <section id="contact" class="bg-sand py-20 lg:py-28 border-t border-black/5">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid lg:grid-cols-2 gap-12 lg:gap-20">
          <div>
            <div class="accent-bar mb-4"></div>
            <h2 class="heading-lg text-3xl sm:text-4xl text-dark-950 mb-6">Get a {esc(S)} Quote</h2>
            <p class="body-text text-lg mb-8">Tell us about your site and we will get back to you within 24 hours. Fill out the form, call us on <a href="tel:{PHONE_TEL}" class="text-brand-500 font-medium hover:underline">{PHONE_DISPLAY}</a>, or email <a href="mailto:andrew@selectcivilgroup.com.au" class="text-brand-500 font-medium hover:underline">andrew@selectcivilgroup.com.au</a> or <a href="mailto:admin@selectcivilgroup.com.au" class="text-brand-500 font-medium hover:underline">admin@selectcivilgroup.com.au</a></p>
            <div class="space-y-5">
              <div class="border-l-2 border-black/10 pl-5"><p class="text-dark-950 text-sm font-bold">Phone</p><a href="tel:{PHONE_TEL}" class="text-gray-600 text-sm hover:text-brand-500" style="transition: color 0.2s ease;">{PHONE_DISPLAY}</a></div>
              <div class="border-l-2 border-black/10 pl-5"><p class="text-dark-950 text-sm font-bold">Email</p><a href="mailto:andrew@selectcivilgroup.com.au" class="text-gray-600 text-sm hover:text-brand-500 block" style="transition: color 0.2s ease;">andrew@selectcivilgroup.com.au</a><a href="mailto:admin@selectcivilgroup.com.au" class="text-gray-600 text-sm hover:text-brand-500 block" style="transition: color 0.2s ease;">admin@selectcivilgroup.com.au</a></div>
              <div class="border-l-2 border-black/10 pl-5"><p class="text-dark-950 text-sm font-bold">Service Area</p><p class="text-gray-600 text-sm">{esc(S)}, Geelong, {esc(sub['region_short'])}</p></div>
              <div class="border-l-2 border-black/10 pl-5"><p class="text-dark-950 text-sm font-bold">Hours</p><p class="text-gray-600 text-sm">Monday - Friday: 7:00 AM - 5:00 PM</p></div>
            </div>
          </div>
          <div class="bg-white border border-black/10 p-8" style="box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 12px 32px rgba(0,0,0,0.06);">
            <form action="https://formspree.io/f/xdawnnyp" method="POST" class="space-y-5">
              <input type="hidden" name="_next" value="https://selectcivilgroup.com.au/thank-you">
              <input type="hidden" name="_subject" value="New enquiry from selectcivilgroup.com.au - {esc(svc['label'])} {esc(S)} page">
              <input type="hidden" name="_source_page" value="{slug}.html">
              <div class="grid sm:grid-cols-2 gap-5">
                <div><label for="name" class="block text-dark-950 text-sm font-bold uppercase tracking-wider mb-2">Name</label><input type="text" id="name" name="name" required placeholder="Your full name" class="w-full bg-white border border-black/10 px-4 py-3 text-dark-950 text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500" style="transition: border-color 0.2s ease;"></div>
                <div><label for="phone" class="block text-dark-950 text-sm font-bold uppercase tracking-wider mb-2">Phone</label><input type="tel" id="phone" name="phone" placeholder="Your phone number" class="w-full bg-white border border-black/10 px-4 py-3 text-dark-950 text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500" style="transition: border-color 0.2s ease;"></div>
              </div>
              <div><label for="email" class="block text-dark-950 text-sm font-bold uppercase tracking-wider mb-2">Email</label><input type="email" id="email" name="email" required placeholder="your@email.com" class="w-full bg-white border border-black/10 px-4 py-3 text-dark-950 text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500" style="transition: border-color 0.2s ease;"></div>
              <div><label for="suburb" class="block text-dark-950 text-sm font-bold uppercase tracking-wider mb-2">Suburb</label><input type="text" id="suburb" name="suburb" placeholder="{esc(S)}, surrounding suburbs..." value="{esc(S)}" class="w-full bg-white border border-black/10 px-4 py-3 text-dark-950 text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500" style="transition: border-color 0.2s ease;"></div>
              <div><label for="service" class="block text-dark-950 text-sm font-bold uppercase tracking-wider mb-2">Service</label><select id="service" name="service" class="w-full bg-white border border-black/10 px-4 py-3 text-dark-950 text-sm focus:outline-none focus:border-brand-500" style="transition: border-color 0.2s ease;"><option value="">Select a service</option>
                  {service_options(svc_key if svc_key != 'concrete-driveway' else 'concrete-driveways')}
                <option value="other">Other</option>
              </select></div>
              <div><label for="message" class="block text-dark-950 text-sm font-bold uppercase tracking-wider mb-2">Project Details</label><textarea id="message" name="message" rows="5" required placeholder="Tell us about your project - location, scope, timeline..." class="w-full bg-white border border-black/10 px-4 py-3 text-dark-950 text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500 resize-none" style="transition: border-color 0.2s ease;"></textarea></div>
              <button type="submit" class="btn-fill w-full py-4 text-base">Send Enquiry</button>
              <p class="text-gray-600 text-xs text-center">We respond within 24 hours on business days.</p>
            </form>
          </div>
        </div>
      </div>
    </section>

  </main>

"""
    doc += FOOTER
    doc += SCRIPTS
    doc += "\n</body>\n</html>\n"
    return nd(doc)


# --------------------------------------------------------------------------- hub page

def render_hub(sub):
    S = sub["name"]
    slug = f"civil-contractor-{sub['slug']}"
    canonical = f"{SITE}/{slug}"
    ctx = {"S": S, "region_name": sub["region_name"], "region_short": sub["region_short"],
           "catchment": catchment_sentence(sub["catchment"])}

    def fill(t):
        return t.format(**ctx)

    faqs = [(fill(q), fill(a)) for q, a in HUB["faq"]] + SHARED_FAQ
    title = fill(HUB["title"])
    meta = fill(HUB["meta"])
    schema = build_schema(HUB, sub, canonical, faqs)

    doc = head(title=title, meta=meta, canonical=canonical, sub=sub, og_img=HUB["og_img"], schema=schema)
    doc += NAV
    doc += '\n  <main id="main">\n'
    doc += f"""
    <nav aria-label="Breadcrumb" class="bg-sand border-b border-black/5 pt-20 lg:pt-24">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <ol class="flex items-center gap-2 text-xs text-gray-500">
          <li><a href="/" class="hover:text-brand-500" style="transition: color 0.2s ease;">Home</a></li>
          <li aria-hidden="true" class="text-gray-400">/</li>
          <li><a href="services" class="hover:text-brand-500" style="transition: color 0.2s ease;">Services</a></li>
          <li aria-hidden="true" class="text-gray-400">/</li>
          <li class="text-gray-700" aria-current="page">{esc(S)}</li>
        </ol>
      </div>
    </nav>

    <section class="relative">
      <div class="relative overflow-hidden" style="height: 420px;">
        <img src="{HUB['hero_img']}" alt="Civil contracting by Select Civil Group in {esc(S)}" width="1600" height="900" class="w-full h-full object-cover" fetchpriority="high">
        <div class="absolute inset-0 bg-black/60"></div>
        <div class="absolute inset-0 bg-gradient-to-t from-dark-950 via-transparent to-transparent"></div>
        <div class="absolute inset-0 flex items-center">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
            <div class="accent-bar mb-4"></div>
            <p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-3">{esc(sub['region_eyebrow'])}</p>
            <h1 class="heading-xl text-4xl sm:text-5xl md:text-6xl text-white mb-4">Civil Contractor in {esc(S)}</h1>
            <p class="text-gray-300 text-lg max-w-2xl" style="line-height: 1.7;">{esc(fill(HUB['hero_lede']))}</p>
            <div class="flex flex-col sm:flex-row gap-3 mt-6">
              <a href="#contact" class="btn-fill px-7 py-3 text-sm">Get a {esc(S)} Quote</a>
              <a href="tel:{PHONE_TEL}" class="btn-outline px-7 py-3 text-sm">Call {PHONE_DISPLAY}</a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="bg-white py-20 lg:py-28">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-6">{esc(fill(HUB['intro_h2']))}</h2>
          <div class="space-y-4 body-text text-lg">
            <p>{esc(sub['intro_context'])}</p>
            <p>{esc(fill(HUB['intro_delivery']))}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="bg-sand border-t border-black/5 py-20 lg:py-28">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl mb-12">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-6">{esc(fill(HUB['grid_heading']))}</h2>
          <p class="body-text text-lg">Every service we run in {esc(S)}, from the site cut to the final pour. Pick a service for the detail, or send us the whole job.</p>
        </div>
        <div class="grid md:grid-cols-2 gap-6 lg:gap-8">
{services_grid(None, sub, hub=True)}
        </div>
      </div>
    </section>

    <section class="bg-white border-t border-black/5 py-20 lg:py-28">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl mb-12">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-6">How a {esc(S)} Job Runs</h2>
          <p class="body-text text-lg">Quote to handover, the same six steps on every job. No surprises, no scope creep, no chasing for updates.</p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          {process_section(S)}
        </div>
      </div>
    </section>

    <section class="bg-sand border-t border-black/5 py-16 lg:py-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl mb-10">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-2xl sm:text-3xl lg:text-4xl text-dark-950 mb-4">Around {esc(S)}</h2>
          <p class="body-text text-base">{esc(sub['chips_lede'])}</p>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {chips_section(sub)}
        </div>
      </div>
    </section>

    <section id="faq" class="bg-white border-t border-black/5 py-20 lg:py-28">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="mb-12">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-4">Frequently Asked</h2>
          <p class="body-text text-lg">The questions we get most from {esc(S)} homeowners and builders.</p>
        </div>
        <div class="divide-y divide-black/10 border-y border-black/10">
{faq_section(faqs)}
        </div>
      </div>
    </section>

    <section class="relative overflow-hidden py-20 lg:py-24 bg-brand-500 stripe-texture">
      <div class="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-4">{esc(fill(HUB['cta_h2']))}</h2>
        <p class="text-dark-950/70 text-lg mb-8 max-w-2xl mx-auto" style="line-height: 1.7;">{esc(fill(HUB['cta_lede']))}</p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <a href="#contact" class="bg-dark-950 text-white font-bold uppercase tracking-wider px-8 py-4 text-base text-center hover:bg-dark-800" style="transition: background 0.2s ease;">Get a Free Quote</a>
          <a href="tel:{PHONE_TEL}" class="border-2 border-dark-950 text-dark-950 font-bold uppercase tracking-wider px-8 py-4 text-base text-center hover:bg-dark-950 hover:text-white" style="transition: background 0.2s ease, color 0.2s ease;">Call {PHONE_DISPLAY}</a>
        </div>
      </div>
    </section>

    <section id="contact" class="bg-sand py-20 lg:py-28 border-t border-black/5">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid lg:grid-cols-2 gap-12 lg:gap-20">
          <div>
            <div class="accent-bar mb-4"></div>
            <h2 class="heading-lg text-3xl sm:text-4xl text-dark-950 mb-6">Get a {esc(S)} Quote</h2>
            <p class="body-text text-lg mb-8">Tell us about your site and we will get back to you within 24 hours. Fill out the form, call us on <a href="tel:{PHONE_TEL}" class="text-brand-500 font-medium hover:underline">{PHONE_DISPLAY}</a>, or email <a href="mailto:andrew@selectcivilgroup.com.au" class="text-brand-500 font-medium hover:underline">andrew@selectcivilgroup.com.au</a> or <a href="mailto:admin@selectcivilgroup.com.au" class="text-brand-500 font-medium hover:underline">admin@selectcivilgroup.com.au</a></p>
            <div class="space-y-5">
              <div class="border-l-2 border-black/10 pl-5"><p class="text-dark-950 text-sm font-bold">Phone</p><a href="tel:{PHONE_TEL}" class="text-gray-600 text-sm hover:text-brand-500" style="transition: color 0.2s ease;">{PHONE_DISPLAY}</a></div>
              <div class="border-l-2 border-black/10 pl-5"><p class="text-dark-950 text-sm font-bold">Email</p><a href="mailto:andrew@selectcivilgroup.com.au" class="text-gray-600 text-sm hover:text-brand-500 block" style="transition: color 0.2s ease;">andrew@selectcivilgroup.com.au</a><a href="mailto:admin@selectcivilgroup.com.au" class="text-gray-600 text-sm hover:text-brand-500 block" style="transition: color 0.2s ease;">admin@selectcivilgroup.com.au</a></div>
              <div class="border-l-2 border-black/10 pl-5"><p class="text-dark-950 text-sm font-bold">Service Area</p><p class="text-gray-600 text-sm">{esc(S)}, Geelong, {esc(sub['region_short'])}</p></div>
              <div class="border-l-2 border-black/10 pl-5"><p class="text-dark-950 text-sm font-bold">Hours</p><p class="text-gray-600 text-sm">Monday - Friday: 7:00 AM - 5:00 PM</p></div>
            </div>
          </div>
          <div class="bg-white border border-black/10 p-8" style="box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 12px 32px rgba(0,0,0,0.06);">
            <form action="https://formspree.io/f/xdawnnyp" method="POST" class="space-y-5">
              <input type="hidden" name="_next" value="https://selectcivilgroup.com.au/thank-you">
              <input type="hidden" name="_subject" value="New enquiry from selectcivilgroup.com.au - Civil Contractor {esc(S)} page">
              <input type="hidden" name="_source_page" value="{slug}.html">
              <div class="grid sm:grid-cols-2 gap-5">
                <div><label for="name" class="block text-dark-950 text-sm font-bold uppercase tracking-wider mb-2">Name</label><input type="text" id="name" name="name" required placeholder="Your full name" class="w-full bg-white border border-black/10 px-4 py-3 text-dark-950 text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500" style="transition: border-color 0.2s ease;"></div>
                <div><label for="phone" class="block text-dark-950 text-sm font-bold uppercase tracking-wider mb-2">Phone</label><input type="tel" id="phone" name="phone" placeholder="Your phone number" class="w-full bg-white border border-black/10 px-4 py-3 text-dark-950 text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500" style="transition: border-color 0.2s ease;"></div>
              </div>
              <div><label for="email" class="block text-dark-950 text-sm font-bold uppercase tracking-wider mb-2">Email</label><input type="email" id="email" name="email" required placeholder="your@email.com" class="w-full bg-white border border-black/10 px-4 py-3 text-dark-950 text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500" style="transition: border-color 0.2s ease;"></div>
              <div><label for="suburb" class="block text-dark-950 text-sm font-bold uppercase tracking-wider mb-2">Suburb</label><input type="text" id="suburb" name="suburb" placeholder="{esc(S)}, surrounding suburbs..." value="{esc(S)}" class="w-full bg-white border border-black/10 px-4 py-3 text-dark-950 text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500" style="transition: border-color 0.2s ease;"></div>
              <div><label for="service" class="block text-dark-950 text-sm font-bold uppercase tracking-wider mb-2">Service</label><select id="service" name="service" class="w-full bg-white border border-black/10 px-4 py-3 text-dark-950 text-sm focus:outline-none focus:border-brand-500" style="transition: border-color 0.2s ease;"><option value="">Select a service</option>
                  {service_options("")}
                <option value="other">Other</option>
              </select></div>
              <div><label for="message" class="block text-dark-950 text-sm font-bold uppercase tracking-wider mb-2">Project Details</label><textarea id="message" name="message" rows="5" required placeholder="Tell us about your project - location, scope, timeline..." class="w-full bg-white border border-black/10 px-4 py-3 text-dark-950 text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500 resize-none" style="transition: border-color 0.2s ease;"></textarea></div>
              <button type="submit" class="btn-fill w-full py-4 text-base">Send Enquiry</button>
              <p class="text-gray-600 text-xs text-center">We respond within 24 hours on business days.</p>
            </form>
          </div>
        </div>
      </div>
    </section>

  </main>

"""
    doc += FOOTER
    doc += SCRIPTS
    doc += "\n</body>\n</html>\n"
    return nd(doc)


# --------------------------------------------------------------------------- sitemap

def update_sitemap(slugs):
    with open(SITEMAP, encoding="utf-8") as f:
        xml = f.read()
    xml = re.sub(r"\n  <!-- LP:START -->.*?<!-- LP:END -->", "", xml, flags=re.DOTALL)
    lines = ["\n  <!-- LP:START -->"]
    for slug, lastmod in slugs:
        lines.append(f"  <url>\n    <loc>{SITE}/{slug}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <priority>0.7</priority>\n  </url>")
    lines.append("  <!-- LP:END -->")
    xml = xml.replace("</urlset>", "\n".join(lines) + "\n</urlset>")
    with open(SITEMAP, "w", encoding="utf-8") as f:
        f.write(xml)


# --------------------------------------------------------------------------- main

def main():
    subs = []
    if os.path.isdir(SUBURBS_DIR):
        for fn in sorted(os.listdir(SUBURBS_DIR)):
            if fn.endswith(".json"):
                with open(os.path.join(SUBURBS_DIR, fn), encoding="utf-8") as f:
                    subs.append(json.load(f))

    slugs = []
    for sub in subs:
        lastmod = sub.get("lastmod", "2026-07-22")
        if sub.get("hub", True):
            fn = f"civil-contractor-{sub['slug']}.html"
            with open(os.path.join(ROOT, fn), "w", encoding="utf-8") as f:
                f.write(render_hub(sub))
            print(f"[lp_render] wrote {fn}")
            slugs.append((fn[:-5], lastmod))
        for svc_key in sub.get("services", list(SERVICES.keys())):
            fn = f"{svc_key}-{sub['slug']}.html"
            with open(os.path.join(ROOT, fn), "w", encoding="utf-8") as f:
                f.write(render(svc_key, sub))
            print(f"[lp_render] wrote {fn}")
            slugs.append((fn[:-5], lastmod))

    update_sitemap(slugs)
    print(f"[lp_render] updated sitemap.xml ({len(slugs)} LP url(s))")


if __name__ == "__main__":
    main()

