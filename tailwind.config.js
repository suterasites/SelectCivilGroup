/** Tailwind v3 config for Select Civil Group. Mirrors the former CDN inline config.
 *  Rebuild:  /path/to/tailwindcss -c tailwind.config.js -i input.css -o styles.css --minify
 */
module.exports = {
  content: ["./*.html"],
  theme: {
    extend: {
      colors: {
        dark:  { 950:'#0a0a0a', 900:'#111111', 800:'#1a1a1a', 700:'#242424', 600:'#2e2e2e' },
        brand: { 500:'#d4912a', 400:'#e8a840' },
      },
      fontFamily: {
        heading: ['"Inter"', 'system-ui', 'sans-serif'],
        body:    ['"Inter"', 'system-ui', 'sans-serif'],
      },
    },
  },
  safelist: ['hidden'],
}
