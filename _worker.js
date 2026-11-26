// Site paused (non-payment). Every request gets a 503 holding page.
// 503 + Retry-After tells Google the outage is temporary, so the indexed
// pages are kept rather than replaced. No page files are touched.
// To bring the site back: delete this file and push.

const PAGE = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex">
<title>Site Temporarily Unavailable</title>
<style>
  html, body { height: 100%; margin: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: #f5f5f5;
    color: #1a1a1a;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 24px;
  }
  .wrap { max-width: 480px; }
  h1 { font-size: 1.75rem; font-weight: 600; margin: 0 0 12px; }
  p { font-size: 1rem; line-height: 1.6; margin: 0 0 8px; color: #555; }
</style>
</head>
<body>
  <div class="wrap">
    <h1>Site Temporarily Unavailable</h1>
    <p>This website is currently offline.</p>
    <p>Please check back soon.</p>
  </div>
</body>
</html>`;

export default {
  async fetch() {
    return new Response(PAGE, {
      status: 503,
      headers: {
        "Content-Type": "text/html; charset=utf-8",
        "Retry-After": "86400",
        "Cache-Control": "no-store",
      },
    });
  },
};
