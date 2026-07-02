/*
 * Select Civil Group - analytics + lead tracking (Sutera Sites)
 * ONE place for all measurement. Loaded on every page via:
 *   <script defer src="/js/analytics.js"></script>
 *
 * =====================  ACTION REQUIRED (James)  =====================
 * Paste the two real IDs below, then commit + push. Until then this
 * file no-ops safely (no tracking fires, nothing breaks).
 *
 *   1. GA4  - create a GA4 property at analytics.google.com,
 *             copy the Measurement ID (looks like "G-XXXXXXXXXX").
 *   2. Clarity - create a project at clarity.microsoft.com,
 *             copy the project ID (short alphanumeric string).
 *
 * After GA4 is live, mark "generate_lead" and "click_to_call" as
 * KEY EVENTS in GA4 (Admin > Events) so they count as conversions.
 * =====================================================================
 */
(function () {
  "use strict";

  var GA4_ID = "G-XXXXXXXXXX";     // <-- replace with real GA4 Measurement ID
  var CLARITY_ID = "CLARITY_ID";   // <-- replace with real Microsoft Clarity project ID

  var GA4_READY = GA4_ID && GA4_ID.indexOf("XXXX") === -1;
  var CLARITY_READY = CLARITY_ID && CLARITY_ID !== "CLARITY_ID";

  // ---- Google Analytics 4 (gtag) ----
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;

  if (GA4_READY) {
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA4_ID;
    document.head.appendChild(s);
    gtag("js", new Date());
    gtag("config", GA4_ID);
  }

  // ---- Microsoft Clarity (heatmaps + session recordings) ----
  if (CLARITY_READY) {
    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1;
      t.src = "https://www.clarity.ms/tag/" + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, "clarity", "script", CLARITY_ID);
  }

  // ---- Lead events (fire regardless of whether IDs are set; gtag queues safely) ----
  function track(name, params) {
    try { window.gtag("event", name, params || {}); } catch (e) {}
    try { if (window.clarity) window.clarity("event", name); } catch (e) {}
  }

  document.addEventListener("DOMContentLoaded", function () {
    // 1. Click-to-call: any tel: link
    document.querySelectorAll('a[href^="tel:"]').forEach(function (a) {
      a.addEventListener("click", function () {
        track("click_to_call", { phone: a.getAttribute("href").replace("tel:", "") });
      });
    });

    // 2. Form submit (backup signal - the primary signal is the thank-you page view below)
    document.querySelectorAll('form[action*="formspree.io"]').forEach(function (f) {
      f.addEventListener("submit", function () {
        var src = (f.querySelector('[name="_source_page"]') || {}).value || location.pathname;
        track("generate_lead", { method: "form", source_page: src });
      });
    });

    // 3. Confirmed conversion: the thank-you page only loads after a successful Formspree submit
    if (/\/thank-you(\.html)?$/.test(location.pathname)) {
      track("generate_lead", { method: "form_confirmed" });
    }
  });
})();
