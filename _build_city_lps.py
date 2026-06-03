#!/usr/bin/env python3
"""Build city landing pages for Select Civil Group.

Uses excavation-drysdale.html (Phase B1) as the structural template.
Generates 6 city LPs (Phase B2-B7) with per-suburb config.
Run once. Idempotent (overwrites). Keep the script for adding more
suburbs in future Phase 5 rollouts.

Usage:
    python _build_city_lps.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ============================================================
# SHARED BOILERPLATE (identical across all city LPs)
# ============================================================

# Tailwind config + Google Fonts + inline styles. All 8 pages on this
# site already share this exact block (lifted from earthworks-excavation.html).
HEAD_TAIL_AND_STYLES = r"""
  <!-- Tailwind -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            dark: { 950: '#0a0a0a', 900: '#111111', 800: '#1a1a1a', 700: '#242424', 600: '#2e2e2e' },
            brand: { 500: '#d4912a', 400: '#e8a840' }
          },
          fontFamily: { heading: ['"Inter"', 'system-ui', 'sans-serif'], body: ['"Inter"', 'system-ui', 'sans-serif'] }
        }
      }
    }
  </script>

  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
"""

STYLE_BLOCK = r"""
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    .skip-link { position: absolute; top: -40px; left: 0; background: #0a0a0a; color: #d4912a; padding: 0.75rem 1.25rem; font-weight: 700; font-size: 0.875rem; letter-spacing: 0.05em; text-transform: uppercase; z-index: 100; text-decoration: none; transition: top 200ms ease; }
    .skip-link:focus { top: 0; outline: 2px solid #e8a840; outline-offset: 0; }
    .heading-xl { font-weight: 900; letter-spacing: -0.04em; line-height: 0.95; text-transform: uppercase; }
    .heading-lg { font-weight: 800; letter-spacing: -0.03em; line-height: 1; text-transform: uppercase; }
    .heading-md { font-weight: 700; letter-spacing: -0.02em; line-height: 1.1; text-transform: uppercase; }
    .body-text { line-height: 1.7; color: #a0a0a0; }
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
    .mobile-menu { transform: translateX(100%); transition: transform 0.3s ease; }
    .mobile-menu.open { transform: translateX(0); }
    .mobile-services-list { max-height: 0; overflow: hidden; transition: max-height 0.3s ease; }
    .mobile-services-list.open { max-height: 600px; }
    .accent-bar { width: 48px; height: 4px; background: #d4912a; }
    .stripe-texture::before { content: ''; position: absolute; inset: 0; background-image: repeating-linear-gradient(90deg, transparent, transparent 3px, rgba(255,255,255,0.015) 3px, rgba(255,255,255,0.015) 4px); pointer-events: none; z-index: 1; }
  </style>
"""

NAV_AND_MOBILE_MENU = r"""
  <!-- ========== NAVBAR ========== -->
  <nav class="fixed top-0 left-0 right-0 z-50 bg-dark-950/95 backdrop-blur-sm border-b border-white/5">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <a href="index.html" class="flex items-center">
          <img src="Assets/Logo PNG.png" alt="Select Civil Group logo" width="2667" height="2106" class="h-10 w-auto">
        </a>
        <div class="hidden lg:flex items-center gap-8">
          <div class="mega-trigger">
            <a href="services.html" class="nav-link text-brand-500 text-sm font-semibold uppercase tracking-wider flex items-center gap-1.5">
              Services
              <svg class="mega-chevron w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"/></svg>
            </a>
            <div class="mega-dropdown" style="width: 520px; left: -120px;">
              <div class="bg-dark-900 border border-white/10 shadow-2xl p-5" style="box-shadow: 0 25px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.05);">
                <div class="grid grid-cols-2 gap-6">
                  <div>
                    <a href="concrete-services.html" class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-3 block hover:text-brand-400" style="transition: color 0.2s ease;">Concrete Services</a>
                    <div class="flex flex-col gap-0.5">
                      <a href="services.html#retaining-walls" class="text-gray-400 text-sm py-1.5 hover:text-white" style="transition: color 0.2s ease;">Retaining Walls</a>
                      <a href="services.html#concrete-driveways" class="text-gray-400 text-sm py-1.5 hover:text-white" style="transition: color 0.2s ease;">Concrete Driveways</a>
                      <a href="services.html#concrete-raft-slabs" class="text-gray-400 text-sm py-1.5 hover:text-white" style="transition: color 0.2s ease;">Concrete Raft Slabs</a>
                      <a href="services.html#concrete-paving" class="text-gray-400 text-sm py-1.5 hover:text-white" style="transition: color 0.2s ease;">Concrete Paving</a>
                      <a href="services.html#factory-tilt-panels" class="text-gray-400 text-sm py-1.5 hover:text-white" style="transition: color 0.2s ease;">Factory Tilt Panels</a>
                      <a href="services.html#concrete-seating" class="text-gray-400 text-sm py-1.5 hover:text-white" style="transition: color 0.2s ease;">Concrete Seating</a>
                      <a href="services.html#concrete-bench-drops" class="text-gray-400 text-sm py-1.5 hover:text-white" style="transition: color 0.2s ease;">Concrete Bench Drops</a>
                    </div>
                  </div>
                  <div>
                    <a href="earthworks-excavation.html" class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-3 block hover:text-brand-400" style="transition: color 0.2s ease;">Earthworks &amp; Excavation</a>
                    <div class="flex flex-col gap-0.5">
                      <a href="services.html#earthworks" class="text-gray-400 text-sm py-1.5 hover:text-white" style="transition: color 0.2s ease;">Earthworks</a>
                      <a href="services.html#site-cuts" class="text-gray-400 text-sm py-1.5 hover:text-white" style="transition: color 0.2s ease;">Site Cuts</a>
                      <a href="services.html#detail-excavation" class="text-gray-400 text-sm py-1.5 hover:text-white" style="transition: color 0.2s ease;">Detail Excavation</a>
                      <a href="services.html#removal-of-excess-oil" class="text-gray-400 text-sm py-1.5 hover:text-white" style="transition: color 0.2s ease;">Removal of Excess Oil</a>
                    </div>
                  </div>
                </div>
                <div class="border-t border-white/5 mt-4 pt-3">
                  <a href="services.html" class="text-gray-500 text-xs font-semibold hover:text-brand-500 flex items-center gap-1.5" style="transition: color 0.2s ease;">View all services <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg></a>
                </div>
              </div>
            </div>
          </div>
          <a href="about.html" class="nav-link text-gray-400 text-sm font-semibold uppercase tracking-wider">About</a>
          <a href="projects.html" class="nav-link text-gray-400 text-sm font-semibold uppercase tracking-wider">Projects</a>
          <a href="contact.html" class="nav-link text-gray-400 text-sm font-semibold uppercase tracking-wider">Contact</a>
          <a href="tel:0483092615" class="btn-outline px-5 py-2 text-sm">0483 092 615</a>
          <a href="contact.html" class="btn-fill px-6 py-2.5 text-sm">Get a Quote</a>
        </div>
        <button onclick="toggleMobileMenu()" class="lg:hidden p-2 text-gray-400 hover:text-white focus-visible:outline-2 focus-visible:outline-brand-500" aria-label="Open menu">
          <svg id="hamburger-icon" class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 6h16M4 12h16M4 18h16"/></svg>
          <svg id="close-icon" class="w-7 h-7 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>
    </div>
  </nav>
  <div id="mobile-backdrop" class="mobile-backdrop lg:hidden" onclick="toggleMobileMenu()"></div>
  <div id="mobile-menu" class="mobile-menu fixed top-16 right-0 bottom-0 w-full sm:w-80 bg-dark-900 sm:border-l border-white/5 p-8 lg:hidden z-50 overflow-y-auto">
    <div class="flex flex-col gap-1">
      <button onclick="toggleMobileServices()" class="flex items-center justify-between w-full text-brand-500 text-lg font-bold uppercase tracking-wider py-3" style="transition: color 0.2s ease;">
        Services
        <svg id="mobile-services-chevron" class="w-5 h-5" style="transition: transform 0.3s ease;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"/></svg>
      </button>
      <div id="mobile-services-list" class="mobile-services-list pl-4">
        <div class="border-l-2 border-brand-500/30 pl-4 flex flex-col gap-0.5 pb-3">
          <p class="text-brand-500 text-xs font-bold uppercase tracking-widest pt-1 pb-1">Concrete Services</p>
          <a href="services.html#retaining-walls" onclick="toggleMobileMenu()" class="text-gray-400 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Retaining Walls</a>
          <a href="services.html#concrete-driveways" onclick="toggleMobileMenu()" class="text-gray-400 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Concrete Driveways</a>
          <a href="services.html#concrete-raft-slabs" onclick="toggleMobileMenu()" class="text-gray-400 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Concrete Raft Slabs</a>
          <a href="services.html#concrete-paving" onclick="toggleMobileMenu()" class="text-gray-400 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Concrete Paving</a>
          <a href="services.html#factory-tilt-panels" onclick="toggleMobileMenu()" class="text-gray-400 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Factory Tilt Panels</a>
          <a href="services.html#concrete-seating" onclick="toggleMobileMenu()" class="text-gray-400 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Concrete Seating</a>
          <a href="services.html#concrete-bench-drops" onclick="toggleMobileMenu()" class="text-gray-400 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Concrete Bench Drops</a>
          <p class="text-brand-500 text-xs font-bold uppercase tracking-widest pt-3 pb-1">Earthworks &amp; Excavation</p>
          <a href="services.html#earthworks" onclick="toggleMobileMenu()" class="text-gray-400 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Earthworks</a>
          <a href="services.html#site-cuts" onclick="toggleMobileMenu()" class="text-gray-400 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Site Cuts</a>
          <a href="services.html#detail-excavation" onclick="toggleMobileMenu()" class="text-gray-400 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Detail Excavation</a>
          <a href="services.html#removal-of-excess-oil" onclick="toggleMobileMenu()" class="text-gray-400 text-sm py-1.5 hover:text-brand-500" style="transition: color 0.2s ease;">Removal of Excess Oil</a>
          <a href="services.html" onclick="toggleMobileMenu()" class="text-gray-500 text-xs font-semibold pt-3 hover:text-brand-500 flex items-center gap-1.5" style="transition: color 0.2s ease;">View all services <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg></a>
        </div>
      </div>
      <a href="about.html" onclick="toggleMobileMenu()" class="text-gray-300 text-lg font-bold uppercase tracking-wider hover:text-brand-500 py-3" style="transition: color 0.2s ease;">About</a>
      <a href="projects.html" onclick="toggleMobileMenu()" class="text-gray-300 text-lg font-bold uppercase tracking-wider hover:text-brand-500 py-3" style="transition: color 0.2s ease;">Projects</a>
      <a href="contact.html" onclick="toggleMobileMenu()" class="text-gray-300 text-lg font-bold uppercase tracking-wider hover:text-brand-500 py-3" style="transition: color 0.2s ease;">Contact</a>
      <a href="tel:0483092615" onclick="toggleMobileMenu()" class="btn-outline text-center px-6 py-3">0483 092 615</a>
      <a href="contact.html" onclick="toggleMobileMenu()" class="btn-fill text-center px-6 py-3 mt-4">Get a Quote</a>
    </div>
  </div>
"""

FOOTER_AND_SCRIPTS = r"""
  <!-- ========== FOOTER ========== -->
  <footer class="bg-dark-900 pt-20 pb-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col lg:flex-row justify-between gap-12 mb-10">
        <div class="max-w-xl">
          <h2 class="heading-xl text-4xl sm:text-5xl lg:text-6xl text-white mb-6">Let's Build Something Solid Together</h2>
          <p class="text-gray-400 text-base mb-8" style="line-height: 1.7;">From initial site assessment to final cleanup, we're here for your project.</p>
          <div class="flex flex-wrap gap-3">
            <a href="contact.html" class="btn-fill px-7 py-3 text-sm">Get a Quote</a>
            <a href="tel:0483092615" class="btn-outline px-7 py-3 text-sm">Call</a>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-x-12 gap-y-6">
          <div>
            <p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-4">Site</p>
            <div class="flex flex-col gap-3">
              <a href="index.html" class="text-white text-sm font-bold hover:text-brand-500" style="transition: color 0.2s ease;">Home</a>
              <a href="services.html" class="text-white text-sm font-bold hover:text-brand-500" style="transition: color 0.2s ease;">Services</a>
              <a href="about.html" class="text-white text-sm font-bold hover:text-brand-500" style="transition: color 0.2s ease;">About</a>
              <a href="projects.html" class="text-white text-sm font-bold hover:text-brand-500" style="transition: color 0.2s ease;">Projects</a>
              <a href="contact.html" class="text-white text-sm font-bold hover:text-brand-500" style="transition: color 0.2s ease;">Contact</a>
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
        <p class="text-gray-600 text-xs">&copy; 2026 Select Civil Group Pty Ltd. All rights reserved.</p>
        <a href="https://www.instagram.com/select_civil_group_pty_ltd/" target="_blank" rel="noopener noreferrer" class="text-gray-500 hover:text-white" style="transition: color 0.2s ease;" aria-label="Instagram">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
        </a>
      </div>
    </div>
  </footer>
  <!-- Sticky mobile CTA bar (Phase A1) -->
  <div class="lg:hidden h-20" aria-hidden="true"></div>
  <div class="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-dark-900 border-t border-white/10 grid grid-cols-2 gap-2 p-2" style="padding-bottom: max(0.5rem, env(safe-area-inset-bottom));">
    <a href="tel:0483092615" class="flex items-center justify-center gap-2 bg-dark-800 border border-white/10 text-white text-sm font-bold uppercase tracking-wider py-3 rounded-md hover:bg-dark-700" style="transition: background-color 0.2s ease;" aria-label="Call Select Civil Group">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
      Call
    </a>
    <a href="#contact" class="flex items-center justify-center gap-2 bg-brand-500 text-dark-950 text-sm font-bold uppercase tracking-wider py-3 rounded-md hover:bg-brand-400" style="transition: background-color 0.2s ease;" aria-label="Get a quote from Select Civil Group">
      Get a Quote
    </a>
  </div>
  <script>
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
      nav.style.borderBottomColor = currentScrollY > 20 ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.03)';
      lastScrollY = currentScrollY;
    });
  </script>
"""

# ============================================================
# PER-SUBURB CONFIG (Phase B2-B7)
# ============================================================

SUBURBS = [
    {
        "slug": "retaining-walls-leopold",
        "primary_service": "Retaining Walls",
        "h1": "Retaining Walls in Leopold",
        "suburb": "Leopold",
        "region_pill": "Geelong East",
        "geo_lat": "-38.182200", "geo_lon": "144.466400",
        "title": "Retaining Walls Leopold - Engineered Concrete Walls | Select Civil Group",
        "description": "Engineered concrete retaining walls in Leopold and across Geelong East. Garden, structural and tiered walls built to engineering specs. Free quotes within 24 hours.",
        "og_short": "Retaining Walls Leopold - Engineered Concrete Walls",
        "twitter_desc": "Engineered concrete retaining walls in Leopold and across the Geelong region.",
        "og_image": "retaining-walls.jpeg",
        "og_image_alt": "Concrete retaining wall by Select Civil Group on a Leopold residential block",
        "hero_lead": "Engineered concrete retaining walls for Leopold homeowners and builders. Sloping blocks turned buildable, garden levels held back, structural walls done to engineering specs. Quotes back within 24 hours.",
        "parent_slug": "concrete-services", "parent_name": "Concrete Services",
        "schema_service_type": "Retaining Walls",
        "schema_service_description": "Engineered concrete retaining walls in Leopold and across Geelong East by Select Civil Group.",
        "schema_offer_catalog_name": "Retaining Wall Services in Leopold",
        "schema_offers": [
            ("Retaining Walls", "Engineered concrete retaining walls for Leopold residential and commercial blocks."),
            ("Site Cuts", "Cut and fill for building platforms, often paired with retaining walls on sloping Leopold blocks."),
            ("Concrete Driveways", "Plain, exposed aggregate and coloured driveways across Leopold."),
            ("Earthworks", "Bulk earthworks for new builds and infill development across Leopold."),
        ],
        "schema_area_served": ["Leopold", "Geelong", "Whittington", "Newcomb", "Moolap", "Marshall", "Bellarine Peninsula"],
        "intro_h2": "Retaining Walls, Built for Leopold's Terrain",
        "intro_paragraphs": [
            "Leopold sits east of central Geelong, with a mix of established streets and growing infill estates. Plenty of blocks step down to gully lines or run off to creeks, and a lot of new builds need retaining before the slab can go in. Wherever there is a level change, there is a wall to engineer.",
            "Select Civil Group is based in Geelong and works across Leopold and the eastern suburbs daily. Whether you need a single garden wall, a structural wall holding back a building platform, or a multi-tier solution on a steep block, we deliver to engineering specs with the right product for the load and the soil.",
        ],
        "services_grid_h2": "Wall, Slab and Site Services for Leopold Projects",
        "services_grid_intro": "The four services Leopold homeowners and builders pair most often. Every job is quoted on the specifics of your site.",
        "service_cards": [
            ("Retaining Walls", "retaining-wall-1.jpg", "Concrete retaining wall on a sloping Leopold block", "Engineered concrete retaining walls for residential and commercial blocks across Leopold. Garden walls, structural walls holding back building platforms, or tiered solutions on steep falls. Designed to engineering specs and built to last."),
            ("Site Cuts", "site-cut-1.jpg", "Site cut for a new build in Leopold", "Precision cut and fill to engineering levels, ready for footings and slabs. Often paired with retaining walls when a block has significant fall. Spoil cartage and disposal handled as part of the job."),
            ("Concrete Driveways", "concrete-driveways.jpeg", "Concrete driveway poured in Leopold", "Plain, exposed aggregate, coloured or stencilled driveways and crossovers across Leopold and surrounding suburbs. Built for the weight of utes and trades, with proper drainage and finish."),
            ("Earthworks", "earthworks.jpeg", "Bulk earthworks on a Leopold residential lot", "Bulk earthworks, grading and levelling for new homes and infill development. We handle compaction and spoil disposal so the next trade arrives to a buildable site."),
        ],
        "around_h2": "Around Leopold",
        "around_intro": "Leopold sits at the gateway to the Bellarine. Most weeks we are working across the surrounding eastern Geelong suburbs and the broader peninsula too.",
        "suburb_chips": ["Leopold", "Geelong", "East Geelong", "Whittington", "Newcomb", "Moolap", "Marshall", "Bellarine", "Drysdale", "Wallington", "Curlewis", "Belmont"],
        "faq": [
            ("Do you build retaining walls in Leopold and across the Geelong region?",
             "Yes. Leopold, Whittington, Newcomb, Moolap, Marshall and the surrounding Geelong East suburbs are all within our core service area. We also work across the Bellarine Peninsula and into central Geelong daily."),
            ("What does a retaining wall in Leopold typically cost?",
             "Wall cost depends on length, height, soil retained, drainage requirements and access. A short garden wall is a different job to a structural wall holding a building platform. We give an obligation-free quote within 24 hours once we have the site details."),
            ("How long does a retaining wall job take?",
             "Most residential retaining walls take three to seven working days from site set-up through to clean-up, depending on length, height and the engineering involved. Larger structural walls and tiered solutions can run longer. We confirm a programmed start and finish date as part of the quote."),
            ("Do you engage the engineer, or do I need to organise that?",
             "Either works. For straightforward residential walls we can recommend an engineer we have worked with locally and coordinate the design. If you already have an engineer or builder running the project, we work to their specifications and drawings."),
            ("Do you work on residential jobs, or only large commercial sites?",
             "We work across residential, commercial and civil projects. For homeowners and small builders that is everything from a single retaining wall or driveway through to a full site cut and slab. For larger projects we partner with builders, developers and contractors across the Bellarine and Geelong region."),
            ("Are you fully insured?",
             "Yes. Select Civil Group carries full public liability insurance and workers compensation cover on every job. Certificates of currency are available on request."),
        ],
        "cta_banner_h2": "Got a Retaining Wall to Build in Leopold?",
        "cta_banner_body": "Send the address and a quick description of the wall. We will come back with an obligation-free quote within 24 hours.",
        "cta_banner_quote_label": "Get a Free Quote",
        "contact_h2": "Get a Leopold Quote",
        "contact_body_extra": "site",
        "form_suburb_default": "Leopold",
        "form_service_default": "retaining-walls",
        "form_subject": "New enquiry from selectcivilgroup.com.au - Retaining Walls Leopold page",
        "form_service_options_order": "concrete-first",
    },
    {
        "slug": "concrete-driveway-ocean-grove",
        "primary_service": "Concrete Driveways",
        "h1": "Concrete Driveways in Ocean Grove",
        "suburb": "Ocean Grove",
        "region_pill": "Bellarine Peninsula",
        "geo_lat": "-38.258900", "geo_lon": "144.524700",
        "title": "Concrete Driveways Ocean Grove - Plain, Exposed & Coloured | Select Civil Group",
        "description": "Concrete driveways and crossovers in Ocean Grove and across the Bellarine. Plain, exposed aggregate, coloured and stencilled finishes. Free quotes within 24 hours.",
        "og_short": "Concrete Driveways Ocean Grove - Select Civil Group",
        "twitter_desc": "Concrete driveways and crossovers across Ocean Grove and the Bellarine Peninsula.",
        "og_image": "concrete-driveways.jpeg",
        "og_image_alt": "Concrete driveway poured by Select Civil Group on a property in Ocean Grove",
        "hero_lead": "Concrete driveways and crossovers for Ocean Grove homeowners and builders. Plain finishes, exposed aggregate, coloured or stencilled concrete. Built for the coastal climate. Quotes back within 24 hours.",
        "parent_slug": "concrete-services", "parent_name": "Concrete Services",
        "schema_service_type": "Concrete Driveways",
        "schema_service_description": "Concrete driveways and crossovers in Ocean Grove and across the Bellarine Peninsula by Select Civil Group.",
        "schema_offer_catalog_name": "Concrete Driveway Services in Ocean Grove",
        "schema_offers": [
            ("Concrete Driveways", "Plain, exposed aggregate, coloured and stencilled driveways across Ocean Grove."),
            ("Concrete Crossovers", "Council-approved concrete crossovers connecting the street to the driveway."),
            ("Concrete Paving", "Coordinated paving for paths, patios and outdoor areas across Ocean Grove."),
            ("Site Cuts", "Site preparation and levelling for new driveway pours on sloping Ocean Grove blocks."),
        ],
        "schema_area_served": ["Ocean Grove", "Barwon Heads", "Connewarre", "Wallington", "Point Lonsdale", "Drysdale", "Bellarine Peninsula"],
        "intro_h2": "Concrete Driveways for Ocean Grove Homes",
        "intro_paragraphs": [
            "Ocean Grove has grown fast. New estates running back from the beach, established streets ageing into replacement-driveway territory, and a steady run of crossovers needed for builds along Wallington Road and the surrounding catchment. Concrete is the long-game choice for the climate down here, and getting the mix, the prep, and the finish right matters when salt air is part of the equation.",
            "Select Civil Group pours concrete driveways across Ocean Grove, Barwon Heads, Connewarre and the wider Bellarine. From plain broom finishes through to exposed aggregate, coloured and stencilled work. Every job includes proper site prep, drainage planning and a finish chosen to suit the property.",
        ],
        "services_grid_h2": "Concrete and Site Services for Ocean Grove",
        "services_grid_intro": "The driveway is rarely the only concrete job on a site. Here is what Ocean Grove homeowners ask us for most.",
        "service_cards": [
            ("Concrete Driveways", "concrete-driveways.jpeg", "Concrete driveway by Select Civil Group in Ocean Grove", "Plain broom, exposed aggregate, coloured or stencilled finishes. Built for the weight of vehicles, the coastal climate, and the look you want at the front of the property. We coordinate the crossover with the council where required."),
            ("Concrete Paving", "concrete-paving.jpeg", "Concrete paving in an Ocean Grove backyard", "Paths, patios, pool surrounds and outdoor areas in matching or contrasting finishes. Often poured at the same time as the driveway to keep colours and finishes consistent across the property."),
            ("Site Cuts", "site-cut-1.jpg", "Site cut for a new build in Ocean Grove", "Precision cut and fill to engineering levels, ready for footings and slabs. Useful on Ocean Grove blocks with fall or established gardens that need levelling before the driveway can be poured."),
            ("Retaining Walls", "retaining-wall-1.jpg", "Retaining wall on an Ocean Grove block", "Concrete retaining walls where a driveway needs supporting earth beside it, or where landscaping changes the level. Engineered for the load and the soil."),
        ],
        "around_h2": "Around Ocean Grove",
        "around_intro": "Ocean Grove is our regular base on the southern Bellarine. Most weeks we are working across the surrounding beachside suburbs and into the peninsula's inland towns.",
        "suburb_chips": ["Ocean Grove", "Barwon Heads", "Connewarre", "Wallington", "Marcus Hill", "Point Lonsdale", "Drysdale", "Leopold", "Geelong", "Torquay", "Curlewis", "Bellarine"],
        "faq": [
            ("Do you pour concrete driveways in Ocean Grove and across the Bellarine?",
             "Yes. Ocean Grove, Barwon Heads, Connewarre, Wallington, Point Lonsdale and the surrounding Bellarine suburbs are all within our core service area. We pour driveways across the southern peninsula weekly."),
            ("What does a concrete driveway in Ocean Grove typically cost?",
             "Cost depends on the size, the finish (plain broom is the cheapest, exposed aggregate and stencilled are higher), site access, drainage requirements and whether a new crossover is needed. We give an obligation-free quote within 24 hours once we have the site details."),
            ("How long does a driveway pour take from start to finish?",
             "Most residential driveways take two to five working days from site set-up to clean-up, including formwork, prep, pour and curing. Larger driveways or jobs that involve a new crossover or retaining can run longer. We confirm a programmed start and finish date as part of the quote."),
            ("What finishes do you offer for driveways?",
             "Plain broom, exposed aggregate, coloured (oxide), and stencilled or stamped patterns. Each has different cost, look and maintenance profiles. We can show finished examples that suit Ocean Grove streetscapes and help you pick what works for the property."),
            ("Do you handle the council crossover approval?",
             "Yes. Where a new or upgraded crossover is required, we coordinate the application with the City of Greater Geelong and pour the crossover to council spec. Existing compliant crossovers we can work with as they are."),
            ("Are you fully insured?",
             "Yes. Select Civil Group carries full public liability insurance and workers compensation cover on every job. Certificates of currency are available on request."),
        ],
        "cta_banner_h2": "Need a Concrete Driveway in Ocean Grove?",
        "cta_banner_body": "Send the address and a quick description. We will come back with an obligation-free quote within 24 hours.",
        "cta_banner_quote_label": "Get a Free Quote",
        "contact_h2": "Get an Ocean Grove Quote",
        "contact_body_extra": "driveway",
        "form_suburb_default": "Ocean Grove",
        "form_service_default": "concrete-driveways",
        "form_subject": "New enquiry from selectcivilgroup.com.au - Concrete Driveway Ocean Grove page",
        "form_service_options_order": "concrete-first",
    },
    {
        "slug": "civil-contractor-torquay",
        "primary_service": "Civil Contracting",
        "h1": "Civil Contractor in Torquay",
        "suburb": "Torquay",
        "region_pill": "Surf Coast",
        "geo_lat": "-38.329000", "geo_lon": "144.326100",
        "title": "Civil Contractor Torquay - Earthworks, Concrete & Site Cuts | Select Civil Group",
        "description": "Local civil contractor in Torquay and the Surf Coast. Earthworks, site cuts, retaining walls, concrete driveways and slabs. Free quotes within 24 hours.",
        "og_short": "Civil Contractor Torquay - Select Civil Group",
        "twitter_desc": "Earthworks, site cuts, retaining walls, concrete driveways and slabs in Torquay and across the Surf Coast.",
        "og_image": "site-cuts.jpeg",
        "og_image_alt": "Civil contracting and earthworks by Select Civil Group on a Torquay development site",
        "hero_lead": "Full civil contracting for Torquay builds and developments. Earthworks, site cuts, retaining walls, concrete slabs and driveways. One crew, start to finish. Quotes back within 24 hours.",
        "parent_slug": "services", "parent_name": "Services",
        "schema_service_type": "Civil Contracting",
        "schema_service_description": "Full civil contracting services in Torquay and the Surf Coast, including earthworks, site cuts, concrete and retaining walls.",
        "schema_offer_catalog_name": "Civil Contracting Services in Torquay",
        "schema_offers": [
            ("Earthworks", "Bulk earthworks, grading and land clearing across Torquay and the Surf Coast."),
            ("Site Cuts", "Precision site cuts for new builds, sheds and developments."),
            ("Concrete Driveways", "Driveways and crossovers in plain, exposed and coloured finishes."),
            ("Retaining Walls", "Engineered concrete retaining walls for sloping Surf Coast blocks."),
        ],
        "schema_area_served": ["Torquay", "Jan Juc", "Bellbrae", "Anglesea", "Connewarre", "Mount Duneed", "Surf Coast"],
        "intro_h2": "Civil Contracting Across the Surf Coast",
        "intro_paragraphs": [
            "Torquay has been one of the fastest-growing pockets on the Surf Coast for a decade now. New estates rolling out from Spring Creek to The Sands, infill builds through the older streets, and a steady stream of larger commercial work along the Surf Coast Highway. Civil work down here needs to handle coastal soils, tight access on small lots, and a constant flow of trades coordinating around each other.",
            "Select Civil Group is based in the Geelong region and works the Surf Coast weekly. From a single site cut on a residential lot through to multi-stage development earthworks, we bring the right machinery, the right operators, and the experience to keep the program moving for whoever is running the build.",
        ],
        "services_grid_h2": "Civil Services for Torquay Projects",
        "services_grid_intro": "The four services Torquay builders and developers ask us for most often. Quoted on the specifics of your site, not a flat rate.",
        "service_cards": [
            ("Site Cuts", "site-cut-1.jpg", "Precision site cut on a Torquay residential block", "Precision cut and fill to engineering levels, ready for footings and slabs. Surf Coast blocks vary from flat sand-pad to significant fall, and we handle the full range with laser-guided levels and spoil cartage included."),
            ("Earthworks & Land Clearing", "earthworks-1.jpg", "Bulk earthworks on a Surf Coast development site", "Bulk earthworks, grading, levelling and land clearing for residential lots, rural-residential blocks and subdivisions. We work to engineering specs and handle compaction so the next trade arrives to a buildable site."),
            ("Detail Excavation", "site-cut-2.jpg", "Detail excavation for footings and trenching", "Footings, service trenches, stormwater lines and tight-access digs to engineering drawings. The precise work that has to be right before concrete and services go in."),
            ("Retaining Walls", "retaining-wall-1.jpg", "Concrete retaining wall on a sloping Torquay block", "Concrete retaining walls engineered for the Surf Coast's mixed terrain. From short garden walls through to engineered structural walls for sloping blocks. Often paired with site cuts when a level platform is the end goal."),
        ],
        "around_h2": "Around Torquay",
        "around_intro": "Torquay anchors our Surf Coast catchment. Most weeks we are working across the surrounding coastal townships and out through the Geelong region too.",
        "suburb_chips": ["Torquay", "Jan Juc", "Bellbrae", "Connewarre", "Mount Duneed", "Breamlea", "Anglesea", "Geelong", "Ocean Grove", "Barwon Heads", "Mount Moriac", "Belmont"],
        "faq": [
            ("Do you work as a civil contractor in Torquay and across the Surf Coast?",
             "Yes. Torquay, Jan Juc, Bellbrae, Anglesea, Connewarre and the surrounding Surf Coast suburbs are all within our core service area. We are based in the Geelong region and work the coast weekly."),
            ("What does a civil package in Torquay typically cost?",
             "Civil costs depend on the scope. A standalone site cut sits at one end; a full package of site cut, earthworks, retaining and slab prep sits at the other. We quote each line itemised so you can see exactly where the money goes and where to trim if you need to."),
            ("Can you coordinate with our builder, engineer and other trades?",
             "Yes. On most jobs we are the first trade on site, so we lock dates with whoever is running the program and hand over to the next trade ready to go. We can deal directly with the engineer if specs change mid-job."),
            ("Do you take on smaller residential jobs, or only large developments?",
             "Both. For homeowners and small builders that is everything from a single retaining wall or driveway through to a full site cut and slab. For larger projects we partner with builders, developers and contractors across the Surf Coast and Geelong region."),
            ("How quickly can you get on site?",
             "Lead time varies with the season and our current run of work. We give you a programmed start date when we quote, and we hold to it. If something is genuinely urgent, ring us directly so we can talk through what is possible."),
            ("Are you fully insured?",
             "Yes. Select Civil Group carries full public liability insurance and workers compensation cover on every job. Certificates of currency are available on request."),
        ],
        "cta_banner_h2": "Got a Torquay Project Coming Up?",
        "cta_banner_body": "Send a quick scope of the work and the site address. We will come back with an obligation-free quote within 24 hours.",
        "cta_banner_quote_label": "Get a Free Quote",
        "contact_h2": "Get a Torquay Quote",
        "contact_body_extra": "project",
        "form_suburb_default": "Torquay",
        "form_service_default": "",
        "form_subject": "New enquiry from selectcivilgroup.com.au - Civil Contractor Torquay page",
        "form_service_options_order": "earthworks-first",
    },
    {
        "slug": "excavation-bellarine",
        "primary_service": "Excavation",
        "h1": "Excavation on the Bellarine Peninsula",
        "suburb": "Bellarine Peninsula",
        "region_pill": "Bellarine Wide",
        "geo_lat": "-38.220800", "geo_lon": "144.566700",
        "title": "Excavation Bellarine Peninsula - Site Cuts, Earthworks, Retaining | Select Civil Group",
        "description": "Site cuts, earthworks, detail excavation and retaining walls across the full Bellarine Peninsula. Drysdale to Point Lonsdale. Free quote within 24 hours.",
        "og_short": "Excavation Bellarine Peninsula - Select Civil Group",
        "twitter_desc": "Site cuts, detail excavation, earthworks and retaining walls across the full Bellarine Peninsula.",
        "og_image": "earthworks.jpeg",
        "og_image_alt": "Earthworks by Select Civil Group on a Bellarine Peninsula development site",
        "hero_lead": "Site cuts, detail excavation, earthworks and retaining walls across the full Bellarine Peninsula. From Drysdale through to Point Lonsdale. Quotes back within 24 hours.",
        "parent_slug": "earthworks-excavation", "parent_name": "Earthworks & Excavation",
        "schema_service_type": "Excavation",
        "schema_service_description": "Excavation services across the Bellarine Peninsula by Select Civil Group, including site cuts, detail excavation, earthworks and retaining walls.",
        "schema_offer_catalog_name": "Excavation Services on the Bellarine",
        "schema_offers": [
            ("Site Cuts", "Precision cut and fill for new builds across the Bellarine."),
            ("Earthworks", "Bulk earthworks and land clearing for residential and commercial sites."),
            ("Detail Excavation", "Footings, trenching and service excavation to engineering specs."),
            ("Retaining Walls", "Engineered concrete retaining walls for the Bellarine's mixed terrain."),
        ],
        "schema_area_served": ["Drysdale", "Clifton Springs", "Curlewis", "Portarlington", "St Leonards", "Ocean Grove", "Barwon Heads", "Bellarine Peninsula"],
        "intro_h2": "Bellarine Excavation, End to End",
        "intro_paragraphs": [
            "The Bellarine is one big growth corridor at this point. New estates running through Curlewis and Drysdale, infill builds across the older coastal townships, and a steady run of commercial and council work. Excavation here means knowing the soils, the access constraints of beachside streets, and how to coordinate with the rest of a peninsula build.",
            "Select Civil Group works the full Bellarine Peninsula. Drysdale, Clifton Springs, Curlewis, Portarlington, St Leonards, Indented Head on the bay side; Ocean Grove, Barwon Heads, Point Lonsdale on the ocean side; Leopold, Wallington, Marcus Hill in between. One crew, one quote, one accountable team across the lot.",
        ],
        "services_grid_h2": "Excavation Services Across the Peninsula",
        "services_grid_intro": "The core excavation work we deliver weekly across the Bellarine. Every job quoted on the specifics of your site.",
        "service_cards": [
            ("Site Cuts", "site-cut-1.jpg", "Precision site cut on a Bellarine residential block", "Precision cut and fill to engineering levels, ready for footings and slabs. Suited to new homes, sheds and extensions across the peninsula's flat and sloping blocks. Laser-guided, spoil included."),
            ("Earthworks & Land Clearing", "earthworks-1.jpg", "Bulk earthworks on a Bellarine subdivision", "Bulk earthworks, grading, levelling and land clearing for residential lots, rural-residential blocks and subdivisions across the Bellarine. We work to engineering specs and handle compaction."),
            ("Detail Excavation", "site-cut-2.jpg", "Detail excavation for footings on a Bellarine site", "Footings, service trenches, stormwater lines and tight-access digs to engineering drawings. The precise work that has to be right before concrete and services go in."),
            ("Retaining Walls", "retaining-wall-1.jpg", "Concrete retaining wall on a Bellarine block", "Concrete retaining walls engineered for the Bellarine's mixed terrain. From short garden walls through to engineered structural walls for sloping blocks."),
        ],
        "around_h2": "Suburbs We Cover",
        "around_intro": "The full Bellarine Peninsula sits inside our core service area. Whether you are bay side, ocean side, or in between, we are within easy reach.",
        "suburb_chips": ["Drysdale", "Clifton Springs", "Curlewis", "Portarlington", "St Leonards", "Indented Head", "Ocean Grove", "Barwon Heads", "Point Lonsdale", "Leopold", "Wallington", "Marcus Hill"],
        "faq": [
            ("Do you cover the full Bellarine Peninsula for excavation?",
             "Yes. The full peninsula sits inside our core service area, from Drysdale and Clifton Springs on the bay side through to Ocean Grove, Barwon Heads and Point Lonsdale on the ocean side. We work the peninsula weekly."),
            ("What does a Bellarine excavation job typically cost?",
             "Every site is different. Costs depend on the volume of material to be moved, access conditions, soil type, spoil disposal and how level the existing block is. We give an obligation-free quote within 24 hours once we have the site details."),
            ("How long does a site cut take on the Bellarine?",
             "Most residential site cuts take one to three days depending on the volume of cut and fill, access, and whether spoil needs to be removed. Larger commercial and subdivision works can run longer. We confirm a programmed start and finish date as part of the quote."),
            ("Do you handle spoil removal and disposal?",
             "Yes. Spoil cartage and disposal are handled as part of the job unless the client wants to retain material on site. We work with licensed disposal sites and account for cartage in the quote so there are no surprise costs at the end."),
            ("Can you coordinate with builders, engineers and councils?",
             "Yes. On most jobs we are the first trade on site, so we lock dates with whoever is running the program. Where engineering specs change mid-job, we deal direct with the engineer. Where council crossovers or permits are involved, we coordinate the paperwork."),
            ("Are you fully insured?",
             "Yes. Select Civil Group carries full public liability insurance and workers compensation cover on every job. Certificates of currency are available on request."),
        ],
        "cta_banner_h2": "Bellarine Project Needs Excavation?",
        "cta_banner_body": "Send the address and a quick description of the work. We will come back with an obligation-free quote within 24 hours.",
        "cta_banner_quote_label": "Get a Free Quote",
        "contact_h2": "Get a Bellarine Quote",
        "contact_body_extra": "site",
        "form_suburb_default": "Bellarine Peninsula",
        "form_service_default": "earthworks",
        "form_subject": "New enquiry from selectcivilgroup.com.au - Excavation Bellarine page",
        "form_service_options_order": "earthworks-first",
    },
    {
        "slug": "concrete-driveway-highton",
        "primary_service": "Concrete Driveways",
        "h1": "Concrete Driveways in Highton",
        "suburb": "Highton",
        "region_pill": "Geelong West",
        "geo_lat": "-38.185800", "geo_lon": "144.333100",
        "title": "Concrete Driveways Highton - Plain, Exposed & Coloured Finishes | Select Civil Group",
        "description": "Concrete driveways and crossovers in Highton and across western Geelong. Plain, exposed aggregate, coloured and stencilled. Free quotes within 24 hours.",
        "og_short": "Concrete Driveways Highton - Select Civil Group",
        "twitter_desc": "Concrete driveways and crossovers across Highton and western Geelong suburbs.",
        "og_image": "concrete-driveways.jpeg",
        "og_image_alt": "Concrete driveway poured by Select Civil Group on a Highton property",
        "hero_lead": "Concrete driveways and crossovers for Highton homeowners and builders. Plain, exposed aggregate, coloured or stencilled finishes. Quotes back within 24 hours.",
        "parent_slug": "concrete-services", "parent_name": "Concrete Services",
        "schema_service_type": "Concrete Driveways",
        "schema_service_description": "Concrete driveways and crossovers in Highton and across western Geelong by Select Civil Group.",
        "schema_offer_catalog_name": "Concrete Driveway Services in Highton",
        "schema_offers": [
            ("Concrete Driveways", "Plain, exposed aggregate, coloured and stencilled driveways across Highton."),
            ("Concrete Crossovers", "Council-approved concrete crossovers connecting the street to the driveway."),
            ("Concrete Paving", "Coordinated paving for paths and outdoor areas across Highton properties."),
            ("Site Cuts", "Site preparation and levelling for new driveway pours on sloping Highton blocks."),
        ],
        "schema_area_served": ["Highton", "Wandana Heights", "Belmont", "Waurn Ponds", "Grovedale", "Newtown", "Geelong"],
        "intro_h2": "Concrete Driveways for Highton Homes",
        "intro_paragraphs": [
            "Highton sits west of central Geelong, climbing up into Wandana Heights with its mix of established homes, larger blocks and a steady run of replacement work. Driveways here range from straightforward plain pours on flat front yards to more involved work on sloping driveways with retaining beside them. The quality of the prep, the mix and the finish is what separates a driveway that lasts twenty years from one that cracks in five.",
            "Select Civil Group pours concrete driveways across Highton, Wandana Heights, Belmont, Waurn Ponds and surrounding western Geelong suburbs. Plain broom, exposed aggregate, coloured or stencilled, paired with proper site prep, drainage planning, and an honest opinion on what will work for the property.",
        ],
        "services_grid_h2": "Concrete and Site Services for Highton",
        "services_grid_intro": "The driveway is rarely the only concrete job on a property. Here is what Highton homeowners ask us for most.",
        "service_cards": [
            ("Concrete Driveways", "concrete-driveways.jpeg", "Concrete driveway by Select Civil Group in Highton", "Plain broom, exposed aggregate, coloured or stencilled finishes. Built for the weight of vehicles and the look you want at the front of the property. We coordinate the council crossover where needed."),
            ("Concrete Paving", "concrete-paving.jpeg", "Concrete paving in a Highton backyard", "Paths, patios, pool surrounds and outdoor areas in matching or contrasting finishes. Often poured at the same time as the driveway to keep colours and finishes consistent across the property."),
            ("Site Cuts", "site-cut-1.jpg", "Site cut for a new build in Highton", "Precision cut and fill to engineering levels, ready for footings and slabs. Useful on Highton's sloping blocks where the driveway sits below the house and needs supporting earthworks."),
            ("Retaining Walls", "retaining-wall-1.jpg", "Retaining wall beside a driveway in Highton", "Concrete retaining walls where a sloping driveway needs supporting earth beside it. Engineered for the load and the soil, often poured in the same program as the driveway."),
        ],
        "around_h2": "Around Highton",
        "around_intro": "Highton anchors our western Geelong catchment. Most weeks we are working across the surrounding suburbs and out towards the Surf Coast.",
        "suburb_chips": ["Highton", "Wandana Heights", "Belmont", "Waurn Ponds", "Grovedale", "Newtown", "Geelong West", "Marshall", "Mount Duneed", "Charlemont", "Mount Moriac", "Torquay"],
        "faq": [
            ("Do you pour concrete driveways in Highton and across western Geelong?",
             "Yes. Highton, Wandana Heights, Belmont, Waurn Ponds, Grovedale, Newtown and the surrounding western Geelong suburbs are all within our core service area. We pour driveways across the west weekly."),
            ("What does a concrete driveway in Highton typically cost?",
             "Cost depends on the size, the finish (plain broom is the cheapest, exposed aggregate and stencilled are higher), site access, drainage requirements and whether a new crossover is needed. We give an obligation-free quote within 24 hours once we have the site details."),
            ("How long does a driveway pour take from start to finish?",
             "Most residential driveways take two to five working days from site set-up to clean-up, including formwork, prep, pour and curing. Larger driveways or jobs that involve retaining or a new crossover can run longer. We confirm a programmed start and finish date as part of the quote."),
            ("What finishes do you offer for driveways?",
             "Plain broom, exposed aggregate, coloured (oxide), and stencilled or stamped patterns. Each has different cost, look and maintenance profiles. We can show finished examples that suit Highton streetscapes and help you pick what works for the property."),
            ("Do you handle the council crossover approval?",
             "Yes. Where a new or upgraded crossover is required, we coordinate the application with the City of Greater Geelong and pour the crossover to council spec. Existing compliant crossovers we can work with as they are."),
            ("Are you fully insured?",
             "Yes. Select Civil Group carries full public liability insurance and workers compensation cover on every job. Certificates of currency are available on request."),
        ],
        "cta_banner_h2": "Need a New Driveway in Highton?",
        "cta_banner_body": "Send the address and a quick description. We will come back with an obligation-free quote within 24 hours.",
        "cta_banner_quote_label": "Get a Free Quote",
        "contact_h2": "Get a Highton Quote",
        "contact_body_extra": "driveway",
        "form_suburb_default": "Highton",
        "form_service_default": "concrete-driveways",
        "form_subject": "New enquiry from selectcivilgroup.com.au - Concrete Driveway Highton page",
        "form_service_options_order": "concrete-first",
    },
    {
        "slug": "civil-works-lara",
        "primary_service": "Civil Contracting",
        "h1": "Civil Contractor in Lara",
        "suburb": "Lara",
        "region_pill": "Geelong North",
        "geo_lat": "-38.026900", "geo_lon": "144.406300",
        "title": "Civil Contractor Lara - Earthworks, Site Cuts & Concrete | Select Civil Group",
        "description": "Local civil contractor in Lara and across the Geelong north corridor. Earthworks, site cuts, retaining walls, concrete driveways and slabs. Free quotes within 24 hours.",
        "og_short": "Civil Contractor Lara - Select Civil Group",
        "twitter_desc": "Earthworks, site cuts, retaining walls and concrete in Lara and across the Geelong north corridor.",
        "og_image": "earthworks.jpeg",
        "og_image_alt": "Civil contracting and earthworks by Select Civil Group on a Lara development site",
        "hero_lead": "Full civil contracting for Lara builds and developments. Earthworks, site cuts, retaining walls, concrete slabs and driveways. Servicing Geelong north through to the Werribee corridor. Quotes back within 24 hours.",
        "parent_slug": "services", "parent_name": "Services",
        "schema_service_type": "Civil Contracting",
        "schema_service_description": "Full civil contracting services in Lara and across the Geelong north corridor.",
        "schema_offer_catalog_name": "Civil Contracting Services in Lara",
        "schema_offers": [
            ("Earthworks", "Bulk earthworks, grading and land clearing across Lara and northern Geelong."),
            ("Site Cuts", "Precision site cuts for new builds, sheds and developments."),
            ("Concrete Driveways", "Driveways and crossovers in plain, exposed and coloured finishes."),
            ("Retaining Walls", "Engineered concrete retaining walls for residential and commercial blocks."),
        ],
        "schema_area_served": ["Lara", "Norlane", "Corio", "Bell Park", "Bell Post Hill", "Hamlyn Heights", "Little River", "Geelong"],
        "intro_h2": "Civil Contracting in Lara and Northern Geelong",
        "intro_paragraphs": [
            "Lara sits in the growth corridor between Geelong and Werribee. Light industrial along the highway, new residential estates expanding north, rural-residential lots out towards the You Yangs. Civil work in this stretch needs to handle a mix of fast-moving subdivisions, individual builds, and the occasional larger commercial pad.",
            "Select Civil Group works Lara, Norlane, Corio and the surrounding northern Geelong suburbs. Whether you are a homeowner adding a shed, a builder cutting a new lot, or a developer running multi-stage earthworks, we have the right machinery and the right crew for the job.",
        ],
        "services_grid_h2": "Civil Services for Lara Projects",
        "services_grid_intro": "The four services Lara builders, developers and homeowners ask us for most often. Every job quoted on the specifics of your site.",
        "service_cards": [
            ("Site Cuts", "site-cut-1.jpg", "Precision site cut on a Lara residential block", "Precision cut and fill to engineering levels, ready for footings and slabs. Lara's mix of flat estate lots and undulating rural-residential blocks both fit our setup, with laser levels and spoil cartage included."),
            ("Earthworks & Land Clearing", "earthworks-1.jpg", "Bulk earthworks on a Lara development site", "Bulk earthworks, grading, levelling and land clearing for residential lots, rural-residential blocks and subdivisions across Lara and the northern corridor."),
            ("Concrete Driveways", "concrete-driveways.jpeg", "Concrete driveway poured at a Lara property", "Plain, exposed aggregate, coloured or stencilled driveways and crossovers across Lara and surrounding suburbs. Built for the weight of utes and trades, with proper drainage and finish."),
            ("Retaining Walls", "retaining-wall-1.jpg", "Concrete retaining wall on a Lara block", "Concrete retaining walls for residential and commercial blocks. Designed to engineering specs and built to last, often paired with site cuts when a level platform is the end goal."),
        ],
        "around_h2": "Around Lara",
        "around_intro": "Lara anchors our northern Geelong catchment. Most weeks we are working across the surrounding suburbs and out towards the Werribee corridor.",
        "suburb_chips": ["Lara", "Norlane", "Corio", "Bell Park", "Bell Post Hill", "Hamlyn Heights", "Anakie", "Little River", "Avalon", "Werribee", "Geelong", "Manor Lakes"],
        "faq": [
            ("Do you work in Lara and across the northern Geelong region?",
             "Yes. Lara, Norlane, Corio, Bell Park, Hamlyn Heights, Little River and the surrounding northern Geelong suburbs are all within our core service area. We work the northern corridor weekly."),
            ("What does a civil package in Lara typically cost?",
             "Civil costs depend on the scope. A standalone site cut sits at one end; a full package of site cut, earthworks, retaining and slab prep sits at the other. We quote each line itemised so you can see exactly where the money goes."),
            ("Can you coordinate with our builder, engineer and other trades?",
             "Yes. On most jobs we are the first trade on site, so we lock dates with whoever is running the program and hand over to the next trade ready to go. We can deal directly with the engineer if specs change mid-job."),
            ("Do you take on smaller residential jobs, or only large developments?",
             "Both. For homeowners and small builders that is everything from a single retaining wall or driveway through to a full site cut and slab. For larger projects we partner with builders, developers and contractors across the northern Geelong region."),
            ("How quickly can you get on site?",
             "Lead time varies with the season and our current run of work. We give you a programmed start date when we quote, and we hold to it. If something is genuinely urgent, ring us directly so we can talk through what is possible."),
            ("Are you fully insured?",
             "Yes. Select Civil Group carries full public liability insurance and workers compensation cover on every job. Certificates of currency are available on request."),
        ],
        "cta_banner_h2": "Got a Lara Project to Quote?",
        "cta_banner_body": "Send a quick scope of the work and the site address. We will come back with an obligation-free quote within 24 hours.",
        "cta_banner_quote_label": "Get a Free Quote",
        "contact_h2": "Get a Lara Quote",
        "contact_body_extra": "project",
        "form_suburb_default": "Lara",
        "form_service_default": "",
        "form_subject": "New enquiry from selectcivilgroup.com.au - Civil Contractor Lara page",
        "form_service_options_order": "earthworks-first",
    },
]


# ============================================================
# BUILDER
# ============================================================

CONCRETE_OPTIONS = """                  <optgroup label="Concrete Services">
                    <option value="retaining-walls"{retaining_sel}>Retaining Walls</option>
                    <option value="concrete-driveways"{driveways_sel}>Concrete Driveways</option>
                    <option value="concrete-raft-slabs">Concrete Raft Slabs</option>
                    <option value="concrete-paving">Concrete Paving</option>
                    <option value="factory-tilt-panels">Factory Tilt Panels</option>
                    <option value="concrete-seating">Concrete Seating</option>
                    <option value="concrete-bench-drops">Concrete Bench Drops</option>
                  </optgroup>"""

EARTHWORKS_OPTIONS = """                  <optgroup label="Earthworks &amp; Excavation">
                    <option value="earthworks"{earthworks_sel}>Earthworks</option>
                    <option value="site-cuts">Site Cuts</option>
                    <option value="detail-excavation">Detail Excavation</option>
                    <option value="removal-excess-oil">Removal of Excess Oil</option>
                  </optgroup>"""


def build_service_options(default_value, order):
    sel_map = {
        "earthworks": " selected",
        "retaining-walls": " selected",
        "concrete-driveways": " selected",
    }
    earthworks_sel = sel_map.get("earthworks", "") if default_value == "earthworks" else ""
    retaining_sel = " selected" if default_value == "retaining-walls" else ""
    driveways_sel = " selected" if default_value == "concrete-driveways" else ""
    concrete = CONCRETE_OPTIONS.format(retaining_sel=retaining_sel, driveways_sel=driveways_sel)
    earthworks = EARTHWORKS_OPTIONS.format(earthworks_sel=earthworks_sel)
    if order == "earthworks-first":
        return earthworks + "\n" + concrete
    return concrete + "\n" + earthworks


def build_service_offers_json(offers):
    parts = []
    for name, desc in offers:
        parts.append(
            f'            {{ "@type": "Offer", "itemOffered": {{ "@type": "Service", "name": "{name}", "description": "{desc}" }} }}'
        )
    return ",\n".join(parts)


def build_area_served_json(places):
    items = []
    for p in places:
        if "Peninsula" in p or p == "Surf Coast":
            items.append(f'          {{ "@type": "Place", "name": "{p}" }}')
        else:
            items.append(f'          {{ "@type": "City", "name": "{p}" }}')
    return ",\n".join(items)


def build_faq_json(faq_entries):
    parts = []
    for q, a in faq_entries:
        parts.append(
            '          {\n'
            '            "@type": "Question",\n'
            f'            "name": "{q}",\n'
            '            "acceptedAnswer": { "@type": "Answer", "text": '
            f'"{a}" }}\n'
            '          }'
        )
    return ",\n".join(parts)


def build_service_cards_html(cards):
    out = []
    for name, img, alt, copy in cards:
        out.append(f"""
          <article class="bg-dark-800 border border-white/5 p-8 hover:border-brand-500/30" style="transition: border-color 0.3s ease;">
            <div class="relative overflow-hidden mb-6" style="aspect-ratio: 4/3;">
              <img src="Assets/{img}" alt="{alt}" width="800" height="600" class="w-full h-full object-cover">
            </div>
            <h3 class="heading-md text-xl sm:text-2xl text-white mb-3">{name}</h3>
            <p class="body-text text-sm mb-4">{copy}</p>
            <a href="#contact" class="text-brand-500 text-sm font-bold uppercase tracking-wider hover:text-brand-400" style="transition: color 0.2s ease;">Quote my job &rarr;</a>
          </article>""")
    return "".join(out)


def build_chips_html(chips):
    out = []
    for c in chips:
        out.append(f'          <div class="bg-dark-800 border border-white/5 px-4 py-3 text-center"><p class="text-gray-300 text-sm font-semibold">{c}</p></div>')
    return "\n".join(out)


def build_faq_html(faq_entries):
    out = []
    for q, a in faq_entries:
        out.append(f"""
          <div class="faq-item">
            <button onclick="toggleFaq(this)" class="w-full flex items-center justify-between py-6 text-left group focus-visible:outline-2 focus-visible:outline-brand-500 focus-visible:outline-offset-2">
              <h3 class="text-white text-lg sm:text-xl font-semibold pr-8" style="letter-spacing: -0.01em;">{q}</h3>
              <svg class="faq-chevron w-5 h-5 text-gray-400 shrink-0" style="transition: transform 0.3s ease;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div class="faq-answer overflow-hidden" style="max-height: 0; transition: max-height 0.3s ease, opacity 0.3s ease; opacity: 0;">
              <p class="body-text text-base pb-6">{a}</p>
            </div>
          </div>""")
    return "".join(out)


def build_page(s):
    canonical = f"https://selectcivilgroup.com.au/{s['slug']}.html"
    img_url = f"https://selectcivilgroup.com.au/Assets/{s['og_image']}"

    service_options = build_service_options(s["form_service_default"], s["form_service_options_order"])
    schema_offers = build_service_offers_json(s["schema_offers"])
    schema_area = build_area_served_json(s["schema_area_served"])
    schema_faq = build_faq_json(s["faq"])
    service_cards_html = build_service_cards_html(s["service_cards"])
    chips_html = build_chips_html(s["suburb_chips"])
    faq_html = build_faq_html(s["faq"])

    intro_paras = "\n            ".join(f"<p>{p}</p>" for p in s["intro_paragraphs"])

    parent_url = f"https://selectcivilgroup.com.au/{s['parent_slug']}.html"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{s['title']}</title>
  <meta name="description" content="{s['description']}">
  <link rel="canonical" href="{canonical}">

  <!-- Geo meta -->
  <meta name="geo.region" content="AU-VIC">
  <meta name="geo.placename" content="{s['suburb']}">
  <meta name="geo.position" content="{s['geo_lat']};{s['geo_lon']}">
  <meta name="ICBM" content="{s['geo_lat']}, {s['geo_lon']}">

  <!-- Open Graph -->
  <meta property="og:title" content="{s['og_short']}">
  <meta property="og:description" content="{s['description']}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="Select Civil Group">
  <meta property="og:locale" content="en_AU">
  <meta property="og:image" content="{img_url}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{s['og_image_alt']}">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{s['og_short']}">
  <meta name="twitter:description" content="{s['twitter_desc']}">
  <meta name="twitter:image" content="{img_url}">
{HEAD_TAIL_AND_STYLES}
  <!-- JSON-LD: @graph (Service + BreadcrumbList + FAQPage) -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "Service",
        "serviceType": "{s['schema_service_type']}",
        "name": "{s['schema_service_type']} {s['suburb']}",
        "description": "{s['schema_service_description']}",
        "provider": {{
          "@type": "LocalBusiness",
          "@id": "https://selectcivilgroup.com.au/#business",
          "name": "Select Civil Group Pty Ltd",
          "telephone": "+61483092615",
          "url": "https://selectcivilgroup.com.au/"
        }},
        "areaServed": [
{schema_area}
        ],
        "hasOfferCatalog": {{
          "@type": "OfferCatalog",
          "name": "{s['schema_offer_catalog_name']}",
          "itemListElement": [
{schema_offers}
          ]
        }}
      }},
      {{
        "@type": "BreadcrumbList",
        "itemListElement": [
          {{ "@type": "ListItem", "position": 1, "name": "Home", "item": "https://selectcivilgroup.com.au/" }},
          {{ "@type": "ListItem", "position": 2, "name": "{s['parent_name']}", "item": "{parent_url}" }},
          {{ "@type": "ListItem", "position": 3, "name": "{s['suburb']}", "item": "{canonical}" }}
        ]
      }},
      {{
        "@type": "FAQPage",
        "mainEntity": [
{schema_faq}
        ]
      }}
    ]
  }}
  </script>
{STYLE_BLOCK}</head>
<body class="bg-dark-950 text-white font-body">

  <a href="#main" class="skip-link">Skip to main content</a>
{NAV_AND_MOBILE_MENU}

  <main id="main">

    <!-- Breadcrumbs -->
    <nav aria-label="Breadcrumb" class="bg-dark-900 border-b border-white/5 pt-20 lg:pt-24">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <ol class="flex items-center gap-2 text-xs text-gray-500">
          <li><a href="index.html" class="hover:text-brand-500" style="transition: color 0.2s ease;">Home</a></li>
          <li aria-hidden="true" class="text-gray-700">/</li>
          <li><a href="{s['parent_slug']}.html" class="hover:text-brand-500" style="transition: color 0.2s ease;">{s['parent_name']}</a></li>
          <li aria-hidden="true" class="text-gray-700">/</li>
          <li class="text-gray-300" aria-current="page">{s['suburb']}</li>
        </ol>
      </div>
    </nav>

    <!-- ========== HERO ========== -->
    <section class="relative">
      <div class="relative overflow-hidden" style="height: 420px;">
        <img src="Assets/{s['og_image']}" alt="{s['og_image_alt']}" width="1600" height="900" class="w-full h-full object-cover">
        <div class="absolute inset-0 bg-black/60"></div>
        <div class="absolute inset-0 bg-gradient-to-t from-dark-950 via-transparent to-transparent"></div>
        <div class="absolute inset-0 flex items-center">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
            <div class="accent-bar mb-4"></div>
            <p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-3">{s['region_pill']}</p>
            <h1 class="heading-xl text-4xl sm:text-5xl md:text-6xl text-white mb-4">{s['h1']}</h1>
            <p class="text-gray-300 text-lg max-w-2xl" style="line-height: 1.7;">{s['hero_lead']}</p>
            <div class="flex flex-col sm:flex-row gap-3 mt-6">
              <a href="#contact" class="btn-fill px-7 py-3 text-sm">{s['contact_h2']}</a>
              <a href="tel:0483092615" class="btn-outline px-7 py-3 text-sm">Call 0483 092 615</a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ========== INTRO ========== -->
    <section class="bg-dark-950 py-20 lg:py-28">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-white mb-6">{s['intro_h2']}</h2>
          <div class="space-y-4 body-text text-lg">
            {intro_paras}
          </div>
        </div>
      </div>
    </section>

    <!-- ========== SERVICES GRID ========== -->
    <section class="bg-dark-900 border-t border-white/5 py-20 lg:py-28">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl mb-12">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-white mb-6">{s['services_grid_h2']}</h2>
          <p class="body-text text-lg">{s['services_grid_intro']}</p>
        </div>
        <div class="grid md:grid-cols-2 gap-6 lg:gap-8">{service_cards_html}
        </div>
      </div>
    </section>

    <!-- ========== PROCESS ========== -->
    <section class="bg-dark-950 border-t border-white/5 py-20 lg:py-28">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl mb-12">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-white mb-6">How a {s['suburb']} Job Runs</h2>
          <p class="body-text text-lg">Quote to handover, the same six steps on every job. No surprises, no scope creep, no chasing for updates.</p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          <div class="bg-dark-800 border border-white/5 p-7"><p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-2">Step 01</p><h3 class="heading-md text-lg text-white mb-3">Enquiry</h3><p class="body-text text-sm">Send the site address, a quick description of the work, and any plans or photos you have. The more we know, the sharper the quote.</p></div>
          <div class="bg-dark-800 border border-white/5 p-7"><p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-2">Step 02</p><h3 class="heading-md text-lg text-white mb-3">Site Walk</h3><p class="body-text text-sm">For larger jobs, we visit the block to check access, soil, levels and obstacles the photos don't show. Most quotes come back within 24 hours.</p></div>
          <div class="bg-dark-800 border border-white/5 p-7"><p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-2">Step 03</p><h3 class="heading-md text-lg text-white mb-3">Fixed Quote</h3><p class="body-text text-sm">Itemised, written, and locked in. Spoil cartage, disposal and machinery are accounted for so there are no surprises at the end.</p></div>
          <div class="bg-dark-800 border border-white/5 p-7"><p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-2">Step 04</p><h3 class="heading-md text-lg text-white mb-3">Programmed Start</h3><p class="body-text text-sm">Confirmed start and finish dates that we hold to. We coordinate with your builder, engineer, or following trades so the ground is ready when they are.</p></div>
          <div class="bg-dark-800 border border-white/5 p-7"><p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-2">Step 05</p><h3 class="heading-md text-lg text-white mb-3">On Site</h3><p class="body-text text-sm">Machine and operator on the ground, working to your engineer's specs. Daily check-ins with whoever is coordinating the build.</p></div>
          <div class="bg-dark-800 border border-white/5 p-7"><p class="text-brand-500 text-xs font-bold uppercase tracking-widest mb-2">Step 06</p><h3 class="heading-md text-lg text-white mb-3">Handover</h3><p class="body-text text-sm">Final levels checked, site cleaned, and your site is ready for the next stage. We are still a phone call away if something comes up later.</p></div>
        </div>
      </div>
    </section>

    <!-- ========== SUBURB CHIPS ========== -->
    <section class="bg-dark-900 border-t border-white/5 py-16 lg:py-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl mb-10">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-2xl sm:text-3xl lg:text-4xl text-white mb-4">{s['around_h2']}</h2>
          <p class="body-text text-base">{s['around_intro']}</p>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
{chips_html}
        </div>
      </div>
    </section>

    <!-- ========== FAQ ========== -->
    <section id="faq" class="bg-dark-950 border-t border-white/5 py-20 lg:py-28">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="mb-12">
          <div class="accent-bar mb-4"></div>
          <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-white mb-4">Frequently Asked</h2>
          <p class="body-text text-lg">The questions we get most from {s['suburb']} homeowners and builders.</p>
        </div>
        <div class="divide-y divide-white/5 border-y border-white/5">{faq_html}
        </div>
      </div>
    </section>

    <!-- ========== CTA BANNER ========== -->
    <section class="relative overflow-hidden py-20 lg:py-24 bg-brand-500 stripe-texture">
      <div class="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="heading-lg text-3xl sm:text-4xl lg:text-5xl text-dark-950 mb-4">{s['cta_banner_h2']}</h2>
        <p class="text-dark-950/70 text-lg mb-8 max-w-2xl mx-auto" style="line-height: 1.7;">{s['cta_banner_body']}</p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <a href="#contact" class="bg-dark-950 text-white font-bold uppercase tracking-wider px-8 py-4 text-base text-center hover:bg-dark-800" style="transition: background 0.2s ease;">{s['cta_banner_quote_label']}</a>
          <a href="tel:0483092615" class="border-2 border-dark-950 text-dark-950 font-bold uppercase tracking-wider px-8 py-4 text-base text-center hover:bg-dark-950 hover:text-white" style="transition: background 0.2s ease, color 0.2s ease;">Call 0483 092 615</a>
        </div>
      </div>
    </section>

    <!-- ========== CONTACT FORM ========== -->
    <section id="contact" class="bg-dark-900 py-20 lg:py-28 border-t border-white/5">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid lg:grid-cols-2 gap-12 lg:gap-20">
          <div>
            <div class="accent-bar mb-4"></div>
            <h2 class="heading-lg text-3xl sm:text-4xl text-white mb-6">{s['contact_h2']}</h2>
            <p class="body-text text-lg mb-8">Tell us about your {s['contact_body_extra']} and we will get back to you within 24 hours. Fill out the form, call us on <a href="tel:0483092615" class="text-brand-500 font-medium hover:underline">0483 092 615</a>, or email <a href="mailto:andrew@selectcivilgroup.com.au" class="text-brand-500 font-medium hover:underline">andrew@selectcivilgroup.com.au</a> or <a href="mailto:admin@selectcivilgroup.com.au" class="text-brand-500 font-medium hover:underline">admin@selectcivilgroup.com.au</a></p>
            <div class="space-y-5">
              <div class="border-l-2 border-white/10 pl-5"><p class="text-white text-sm font-bold">Phone</p><a href="tel:0483092615" class="text-gray-400 text-sm hover:text-brand-500" style="transition: color 0.2s ease;">0483 092 615</a></div>
              <div class="border-l-2 border-white/10 pl-5"><p class="text-white text-sm font-bold">Email</p><a href="mailto:andrew@selectcivilgroup.com.au" class="text-gray-400 text-sm hover:text-brand-500 block" style="transition: color 0.2s ease;">andrew@selectcivilgroup.com.au</a><a href="mailto:admin@selectcivilgroup.com.au" class="text-gray-400 text-sm hover:text-brand-500 block" style="transition: color 0.2s ease;">admin@selectcivilgroup.com.au</a></div>
              <div class="border-l-2 border-white/10 pl-5"><p class="text-white text-sm font-bold">Service Area</p><p class="text-gray-400 text-sm">{s['suburb']}, Geelong, Bellarine</p></div>
              <div class="border-l-2 border-white/10 pl-5"><p class="text-white text-sm font-bold">Hours</p><p class="text-gray-400 text-sm">Monday - Friday: 7:00 AM - 5:00 PM</p></div>
            </div>
          </div>
          <div class="bg-dark-700 border border-white/10 p-8">
            <form action="https://formspree.io/f/xdawnnyp" method="POST" class="space-y-5">
              <input type="hidden" name="_next" value="https://selectcivilgroup.com.au/thank-you.html">
              <input type="hidden" name="_subject" value="{s['form_subject']}">
              <input type="hidden" name="_source_page" value="{s['slug']}.html">
              <div class="grid sm:grid-cols-2 gap-5">
                <div><label for="name" class="block text-white text-sm font-bold uppercase tracking-wider mb-2">Name</label><input type="text" id="name" name="name" required placeholder="Your full name" class="w-full bg-dark-900 border border-white/10 px-4 py-3 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500" style="transition: border-color 0.2s ease;"></div>
                <div><label for="phone" class="block text-white text-sm font-bold uppercase tracking-wider mb-2">Phone</label><input type="tel" id="phone" name="phone" placeholder="Your phone number" class="w-full bg-dark-900 border border-white/10 px-4 py-3 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500" style="transition: border-color 0.2s ease;"></div>
              </div>
              <div><label for="email" class="block text-white text-sm font-bold uppercase tracking-wider mb-2">Email</label><input type="email" id="email" name="email" required placeholder="your@email.com" class="w-full bg-dark-900 border border-white/10 px-4 py-3 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500" style="transition: border-color 0.2s ease;"></div>
              <div><label for="suburb" class="block text-white text-sm font-bold uppercase tracking-wider mb-2">Suburb</label><input type="text" id="suburb" name="suburb" placeholder="{s['suburb']}, surrounding suburbs..." value="{s['form_suburb_default']}" class="w-full bg-dark-900 border border-white/10 px-4 py-3 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500" style="transition: border-color 0.2s ease;"></div>
              <div><label for="service" class="block text-white text-sm font-bold uppercase tracking-wider mb-2">Service</label><select id="service" name="service" class="w-full bg-dark-900 border border-white/10 px-4 py-3 text-white text-sm focus:outline-none focus:border-brand-500" style="transition: border-color 0.2s ease;"><option value="">Select a service</option>
{service_options}
                <option value="other">Other</option>
              </select></div>
              <div><label for="message" class="block text-white text-sm font-bold uppercase tracking-wider mb-2">Project Details</label><textarea id="message" name="message" rows="5" required placeholder="Tell us about your project - location, scope, timeline..." class="w-full bg-dark-900 border border-white/10 px-4 py-3 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500 resize-none" style="transition: border-color 0.2s ease;"></textarea></div>
              <button type="submit" class="btn-fill w-full py-4 text-base">Send Enquiry</button>
              <p class="text-gray-600 text-xs text-center">We respond within 24 hours on business days.</p>
            </form>
          </div>
        </div>
      </div>
    </section>

  </main>
{FOOTER_AND_SCRIPTS}
</body>
</html>
"""


# ============================================================
# MAIN
# ============================================================

def main():
    for s in SUBURBS:
        out_path = ROOT / f"{s['slug']}.html"
        html = build_page(s)
        out_path.write_text(html, encoding="utf-8")
        line_count = html.count("\n") + 1
        print(f"Wrote {s['slug']}.html  ({line_count} lines, {len(html)} chars)")


if __name__ == "__main__":
    main()
