/**
 * brand.js — InfoAlpha Shared Header & Footer
 * =============================================
 * Add ONE line to any page's <body> to get the full branded nav + footer:
 *
 *   <script src="brand.js"></script>
 *
 * The script auto-detects the current page filename and highlights the
 * active nav link. Works on GitHub Pages (static, no server needed).
 *
 * Pages supported: breadth, delivery_spike, highlow, momentum_ma,
 *   recurring_entry, sector_rotation, options_oi_chart*, Dashboard*,
 *   csvweek, csvmonth, ai_analysis_v4_*, index
 */

(function () {

  /* ── 1. STYLES ──────────────────────────────────────────────────────────── */
  const CSS = `
  .ia-nav {
    position: sticky; top: 0; z-index: 9999;
    background: rgba(8,13,20,.96);
    backdrop-filter: blur(14px);
    border-bottom: 1px solid #1e2d3d;
    padding: 0 20px;
    display: flex; align-items: center; justify-content: space-between;
    height: 52px;
    font-family: 'Segoe UI', system-ui, sans-serif;
    box-sizing: border-box;
  }
  .ia-brand {
    display: flex; align-items: center; gap: 10px;
    text-decoration: none;
  }
  .ia-brand img {
    height: 36px; width: 36px; object-fit: contain; border-radius: 4px;
  }
  .ia-brand-text { display: flex; flex-direction: column; gap: 1px; }
  .ia-brand-name {
    font-family: 'Space Mono', monospace, 'Courier New';
    font-weight: 700; font-size: 13px; color: #3b9eff; letter-spacing: .4px;
    line-height: 1;
  }
  .ia-brand-sub {
    font-size: 8px; color: #4d6a84;
    letter-spacing: 1.5px; text-transform: uppercase;
  }
  .ia-nav-links {
    display: flex; align-items: center; gap: 4px; flex-wrap: nowrap;
  }
  .ia-nav-links a {
    color: #8ca8c5; text-decoration: none;
    font-size: 11px; font-weight: 600;
    padding: 5px 10px; border-radius: 6px;
    transition: color .15s, background .15s;
    white-space: nowrap;
  }
  .ia-nav-links a:hover { color: #d4e4f7; background: rgba(59,158,255,.08); }
  .ia-nav-links a.ia-active { color: #3b9eff; background: rgba(59,158,255,.1); }
  .ia-nav-cta {
    padding: 5px 13px !important;
    border-radius: 6px !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: .3px !important;
  }
  .ia-nav-cta-tg  { background: #229ED9 !important; color: #fff !important; }
  .ia-nav-cta-yt  { background: #ff0000 !important; color: #fff !important; }
  .ia-nav-cta-tg:hover  { background: #1a8abd !important; }
  .ia-nav-cta-yt:hover  { background: #cc0000 !important; }
  @media (max-width: 720px) {
    .ia-nav-links .ia-hide-mobile { display: none; }
  }
  @media (max-width: 500px) {
    .ia-brand-sub { display: none; }
    .ia-nav-links a:not(.ia-nav-cta) { padding: 5px 6px; font-size: 10px; }
  }

  /* ── footer ── */
  .ia-footer {
    margin-top: 48px;
    border-top: 1px solid #1e2d3d;
    background: #080d14;
    padding: 24px 20px 20px;
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 11px;
    color: #4d6a84;
    box-sizing: border-box;
  }
  .ia-footer-inner {
    max-width: 1100px; margin: 0 auto;
    display: flex; flex-wrap: wrap;
    align-items: center; justify-content: space-between;
    gap: 14px;
  }
  .ia-footer-brand {
    display: flex; align-items: center; gap: 8px;
    text-decoration: none;
  }
  .ia-footer-brand img {
    height: 28px; width: 28px; object-fit: contain; border-radius: 3px; opacity: .85;
  }
  .ia-footer-brand-name {
    font-weight: 700; font-size: 12px; color: #3b9eff;
    font-family: 'Space Mono', monospace, 'Courier New';
  }
  .ia-footer-links {
    display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
  }
  .ia-footer-links a {
    color: #4d6a84; text-decoration: none;
    font-size: 10px; padding: 3px 8px;
    border: 1px solid #1e2d3d; border-radius: 4px;
    transition: color .15s, border-color .15s;
    white-space: nowrap;
  }
  .ia-footer-links a:hover { color: #8ca8c5; border-color: #243547; }
  .ia-footer-disc {
    width: 100%; font-size: 10px; color: #2a3d50;
    text-align: center; margin-top: 10px;
    border-top: 1px solid #111923; padding-top: 10px;
  }
  `;

  /* ── 2. ACTIVE PAGE DETECTION ───────────────────────────────────────────── */
  const page = window.location.pathname.split('/').pop() || 'index.html';

  function isActive(keys) {
    return keys.some(k => page.includes(k)) ? ' ia-active' : '';
  }

  /* ── 3. NAV HTML ────────────────────────────────────────────────────────── */
  const nav = `
  <nav class="ia-nav">
    <a href="index.html" class="ia-brand">
      <img src="logo.png" alt="InfoAlpha logo">
      <div class="ia-brand-text">
        <span class="ia-brand-name">InfoAlpha</span>
        <span class="ia-brand-sub">Smart Signals · Better Trades</span>
      </div>
    </a>
    <div class="ia-nav-links">
      <a href="index.html"${isActive(['index'])} class="ia-hide-mobile">Home</a>
      <a href="index.html#signals"${isActive(['breadth','delivery','highlow','momentum','recurring','sector'])} class="ia-hide-mobile">Screeners</a>
      <a href="index.html#oi"${isActive(['options_oi','Dashboard','csvweek','csvmonth'])} class="ia-hide-mobile">OI Charts</a>
      <a href="index.html#reports"${isActive(['ai_analysis'])} class="ia-hide-mobile">AI Reports</a>
      <a href="https://t.me/volumepricemove" target="_blank" class="ia-nav-cta ia-nav-cta-tg">✈ Telegram</a>
      <a href="https://www.youtube.com/@InfoAlphain" target="_blank" class="ia-nav-cta ia-nav-cta-yt">▶ YouTube</a>
    </div>
  </nav>`;

  /* ── 4. FOOTER HTML ─────────────────────────────────────────────────────── */
  const footer = `
  <footer class="ia-footer">
    <div class="ia-footer-inner">
      <a href="index.html" class="ia-footer-brand">
        <img src="logo.png" alt="InfoAlpha">
        <span class="ia-footer-brand-name">InfoAlpha</span>
      </a>
      <div class="ia-footer-links">
        <a href="https://t.me/volumepricemove" target="_blank">✈ Telegram</a>
        <a href="https://wa.me/919884346789" target="_blank">💬 WhatsApp</a>
        <a href="https://www.youtube.com/@InfoAlphain" target="_blank">▶ YouTube</a>
        <a href="https://www.linkedin.com/in/ssivasankar/" target="_blank">in LinkedIn</a>
        <a href="https://x.com/ssankarsiva" target="_blank">𝕏 Twitter</a>
        <a href="https://infoalpha.in" target="_blank">🌐 infoalpha.in</a>
      </div>
      <div class="ia-footer-disc">
        InfoAlpha — AI EOD NSE Market Intelligence &nbsp;·&nbsp;
        Educational Purpose Only &nbsp;·&nbsp;
        Not SEBI-registered Investment Advice &nbsp;·&nbsp;
        © 2026 Sivasankar S
      </div>
    </div>
  </footer>`;

  /* ── 5. INJECT ──────────────────────────────────────────────────────────── */
  // Inject CSS
  const style = document.createElement('style');
  style.textContent = CSS;
  document.head.appendChild(style);

  // Inject Google Fonts (Space Mono for brand name)
  if (!document.querySelector('link[href*="Space+Mono"]')) {
    const font = document.createElement('link');
    font.rel  = 'stylesheet';
    font.href = 'https://fonts.googleapis.com/css2?family=Space+Mono:wght@700&display=swap';
    document.head.appendChild(font);
  }

  // Insert nav at very top of body
  document.body.insertAdjacentHTML('afterbegin', nav);

  // Insert footer at very end of body
  document.body.insertAdjacentHTML('beforeend', footer);

  // Add top padding to body so sticky nav doesn't cover content
  document.body.style.paddingTop = (document.body.style.paddingTop
    ? parseInt(document.body.style.paddingTop) + 52
    : 0) + 'px';

})();
