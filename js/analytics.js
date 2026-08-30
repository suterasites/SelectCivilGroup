/*
 * Select Civil Group - analytics + lead tracking (Sutera Sites)
 * ONE place for all measurement. Loaded on every page via:
 *   <script defer src="/js/analytics.js"></script>
 *
 * What fires from here:
 *   - GA4 events  : generate_lead (form) + click_to_call (tel: click)
 *   - Google Ads  : native conversions on AW-17941564943 (quote form + call click)
 *                   plus the call-from-ads forwarding number swap
 *   - Clarity     : the same two events, once a Clarity project ID is pasted below
 *
 * The GA4 library (gtag.js, G-R71LED1J87) is loaded by an inline snippet in the
 * <head> of every page, so window.gtag already exists by the time this runs. The
 * Google Ads destination is registered here as a SECOND config on that same
 * loaded library - that is the supported gtag pattern and does not double-count
 * GA4 pageviews. If a page ever ships without the inline GA4 snippet, the loader
 * below brings gtag.js in so the Ads conversions still send.
 *
 * =====================  ACTION REQUIRED (James)  =====================
 *   1. Clarity - create a project at clarity.microsoft.com and paste the
 *      project ID into CLARITY_ID below. Until then Clarity no-ops safely.
 *   2. In GA4 (Admin > Events), mark "generate_lead" and "click_to_call"
 *      as KEY EVENTS so they count as conversions.
 * =====================================================================
 */
(function () {
  "use strict";

  var GA4_ID = "G-R71LED1J87";     // live - also configured inline in each page <head>
  var CLARITY_ID = "CLARITY_ID";   // <-- replace with real Microsoft Clarity project ID

  // Google Ads conversion tracking (account 862-420-4721).
  var ADS_ID = "AW-17941564943";
  var ADS_CONV = {
    // Quote form completed. Fires on the thank-you page only - that page loads
    // solely after a successful Formspree post, so it is the confirmed lead.
    form: "AW-17941564943/f_hXCLLv6oIcEI-cmutC",
    // Visitor tapped a tel: link.
    call_click: "AW-17941564943/zH8XCJj86oIcEI-cmutC",
    // Call-from-ads: swaps the displayed number for a Google forwarding number
    // on ad clicks only. The number below must match the number rendered on the
    // page character for character, or no swap happens.
    call_forward: "AW-17941564943/n3BjCNL784IcEI-cmutC"
  };
  var PHONE_DISPLAY = "0483 092 615";

  var CLARITY_READY = CLARITY_ID && CLARITY_ID !== "CLARITY_ID";

  // ---- gtag bootstrap ----
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;

  // Load gtag.js only if the inline <head> snippet did not already do it.
  if (!document.querySelector('script[src*="googletagmanager.com/gtag/js"]')) {
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA4_ID;
    document.head.appendChild(s);
    window.gtag("js", new Date());
    window.gtag("config", GA4_ID);
  }

  // ---- Google Ads destination + call-from-ads number swap ----
  window.gtag("config", ADS_ID);
  window.gtag("config", ADS_CONV.call_forward, { phone_conversion_number: PHONE_DISPLAY });

  // ---- Microsoft Clarity (heatmaps + session recordings) ----
  if (CLARITY_READY) {
    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1;
      t.src = "https://www.clarity.ms/tag/" + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, "clarity", "script", CLARITY_ID);
  }

  function track(name, params) {
    try { window.gtag("event", name, params || {}); } catch (e) {}
    try { if (window.clarity) window.clarity("event", name); } catch (e) {}
  }

  function adsConversion(sendTo) {
    try { window.gtag("event", "conversion", { send_to: sendTo }); } catch (e) {}
  }

  document.addEventListener("DOMContentLoaded", function () {
    // 1. Click-to-call: any tel: link. GA4 event + Google Ads conversion.
    document.querySelectorAll('a[href^="tel:"]').forEach(function (a) {
      a.addEventListener("click", function () {
        track("click_to_call", { phone: a.getAttribute("href").replace("tel:", "") });
        adsConversion(ADS_CONV.call_click);
      });
    });

    // 2. Form submit - GA4 backup signal only. The Google Ads conversion is held
    //    back to the thank-you page below so a failed post never counts as a lead.
    document.querySelectorAll('form[action*="formspree.io"]').forEach(function (f) {
      f.addEventListener("submit", function () {
        var src = (f.querySelector('[name="_source_page"]') || {}).value || location.pathname;
        track("generate_lead", { method: "form", source_page: src });
      });
    });

    // 3. Confirmed conversion: the thank-you page only loads after a successful
    //    Formspree submit. This is the signal Google Ads bids against.
    if (/\/thank-you(\.html)?$/.test(location.pathname)) {
      track("generate_lead", { method: "form_confirmed" });
      adsConversion(ADS_CONV.form);
    }
  });
})();
