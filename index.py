"""
index.py  —  InfoAlpha  |  Trading Tools Generator
==================================================
Reads the last N ai_analysis_v4.json files from screener/output/YYYY-MM-DD/
and generates tradingtool.html for GitHub Pages.

Also copies the latest screener HTMLs and OI charts.
The digital services homepage (index.html) is a separate static file — do NOT overwrite it.

CHANGELOG:
  v2 — Trader view (Intraday / Weekly / Monthly bias + levels) now shown
       in the featured signal card, matching ai_analysis_v4.html.
  v3 — Output renamed to tradingtool.html (index.html is now the digital-services page).
       Nav bar includes a "Digital Services" link back to index.html.
  v4 — White theme: background white, font black.
  v5 — Full SEO overhaul: optimised title, description, keywords, OG, Twitter,
       Schema.org (WebSite + Person + BreadcrumbList), canonical, robots meta,
       structured data for trading tools. Fixed output path to tradingtool.html.

Usage:
    python index.py
    python index.py --date 2026-03-19   # use specific date for screener files
    python index.py --days 5            # number of AI report days to show

Author: PositionalSystem / InfoAlpha
"""

import os, json, shutil, argparse
from pathlib import Path
from datetime import datetime

# ── PATHS ─────────────────────────────────────────────────────────────────────
SOURCE_BASE  = Path(r"D:\PositionalSystem\screener\output")
DEST_FOLDER  = Path(r"D:\PositionalSystem\screener\gitpublic")
AI_JSON_NAME = "ai_analysis_v4.json"   # primary; fallbacks: ai_analysis.json, any ai_analysis*.json

SCREENER_FILES = [
    "breadth.html",
    "delivery_spike.html",
    "highlow.html",
    "momentum_ma.html",
    #"recurring_entry.html",
    "sector_rotation.html",
]

OI_FILES = [
    #"options_oi_chart.html",
    #"options_oi_chartnxtweek.html",
    "options_oi_chartmonth.html",
    #"options_oi_chartnxtmonth.html",
    #"csvweek.html",
    #"csvmonth.html",
    #"Dashboard.html",
    "DashboardMonth.html",
]


# ── HELPERS ───────────────────────────────────────────────────────────────────

def find_date_dirs(base: Path, n: int) -> list:
    candidates = sorted(
        [d for d in base.iterdir() if d.is_dir() and d.name[:4].isdigit()],
        key=lambda d: d.name,
        reverse=True,
    )
    result = []
    for d in candidates:
        j = d / AI_JSON_NAME
        if not j.exists():
            j = d / "ai_analysis.json"
        if not j.exists():
            matches = sorted(d.glob("ai_analysis*.json"), reverse=True)
            j = matches[0] if matches else None
        if j and Path(j).exists():
            result.append((d.name, Path(j)))

        if len(result) >= n:
            break
    return result


def load_signal(date_str: str, json_path: Path) -> dict:
    """Load and normalise one day's AI analysis JSON — includes trader levels."""
    try:
        raw = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  [warn] {date_str}: {e}")
        return {}

    regime     = raw.get("regime",          raw.get("market_regime", {}).get("signal", "NEUTRAL"))
    conf       = raw.get("confidence",      raw.get("market_regime", {}).get("confidence", "LOW"))
    strength   = int(raw.get("strength",    0))
    cap        = raw.get("conviction_cap",  raw.get("market_regime", {}).get("conviction_cap", "MEDIUM"))
    vix_zone   = raw.get("vix_zone",        "")
    synthesis  = raw.get("synthesis",       raw.get("market_regime", {}).get("one_line", ""))
    action     = raw.get("action_plan",     "")
    risks      = raw.get("risk_flags",      [])
    fii_streak = raw.get("fii_divergence",  raw.get("fii_3d_streak", "—"))
    br_trend   = raw.get("breadth_trend",   "")
    anomalies  = raw.get("anomalies",       [])
    oi_narr    = raw.get("oi_narrative",    "")
    trader     = raw.get("trader", {})

    try:
        disp_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %d, %Y")
    except:
        disp_date = date_str

    ymd = date_str.replace('-', '_')
    dmy = "_".join(reversed(date_str.split('-')))
    return {
        "date_raw":    date_str,
        "date_disp":   disp_date,
        "regime":      regime,
        "conf":        conf,
        "strength":    strength,
        "cap":         cap,
        "vix_zone":    vix_zone,
        "synthesis":   synthesis[:380] + "…" if len(synthesis) > 380 else synthesis,
        "action":      action[:420]    + "…" if len(action)    > 420 else action,
        "risks":       risks[:4],
        "fii":         fii_streak,
        "breadth":     br_trend,
        "anomalies":   anomalies[:3],
        "oi_narr":     oi_narr,
        "trader":      trader,
        "ai_file":     f"ai_analysis_v4_{ymd}.html",
        "ai_file_old": f"ai_analysis_{dmy}.html",
        "has_json":    True,
    }


def load_html_only_signals(dest: Path, known_dates: set) -> list:
    import re as _re
    results = []
    for f in dest.glob("ai_analysis_v4_*.html"):
        m = _re.search(r'ai_analysis_v4_(\d{4})_(\d{2})_(\d{2})\.html', f.name)
        if not m:
            continue
        date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        if date_str in known_dates:
            continue
        try:
            html_text = f.read_text(encoding="utf-8", errors="ignore")
            rm = _re.search(r"class=['\"]reg['\"][^>]*>([A-Z]+)<", html_text)
            regime = rm.group(1) if rm else "NEUTRAL"
            sm = _re.search(r'(?:Strength|Signal Alignment) (\d+)/10', html_text)
            strength = int(sm.group(1)) if sm else 0
        except:
            regime, strength = "NEUTRAL", 0

        try:
            disp_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %d, %Y")
        except:
            disp_date = date_str

        ymd = date_str.replace('-', '_')
        dmy = "_".join(reversed(date_str.split('-')))
        results.append({
            "date_raw":  date_str,
            "date_disp": disp_date,
            "regime":    regime,
            "conf":      "—",
            "strength":  strength,
            "cap":       "—",
            "vix_zone":  "",
            "synthesis": "",
            "action":    "",
            "risks":     [],
            "fii":       "—",
            "breadth":   "",
            "anomalies": [],
            "oi_narr":   "",
            "trader":    {},
            "ai_file":   f"ai_analysis_v4_{ymd}.html",
            "ai_file_old": f"ai_analysis_{dmy}.html",
            "has_json":  False,
        })
        print(f"  HTML-only: {date_str} → {regime} {strength}/10")

    return sorted(results, key=lambda x: x["date_raw"], reverse=True)


def inject_brand(html_path: Path):
    try:
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        if "brand.js" in text:
            return
        tag = '<script src="brand.js"></script>'
        if "</body>" in text:
            text = text.replace("</body>", f"{tag}\n</body>", 1)
        else:
            text += f"\n{tag}\n"
        html_path.write_text(text, encoding="utf-8")
    except Exception as e:
        print(f"  [warn] inject_brand {html_path.name}: {e}")


def copy_screener_files(src_date_dir: Path):
    logo_src = Path(__file__).parent / "logo.png"
    if logo_src.exists() and logo_src.resolve() != (DEST_FOLDER / "logo.png").resolve():
        shutil.copy(logo_src, DEST_FOLDER / "logo.png")
        print("  Copied: logo.png")

    brand_src = Path(__file__).parent / "brand.js"
    if brand_src.exists() and brand_src.resolve() != (DEST_FOLDER / "brand.js").resolve():
        shutil.copy(brand_src, DEST_FOLDER / "brand.js")
        print("  Copied: brand.js")

    self_src = Path(__file__).resolve()
    self_dst = (DEST_FOLDER / "index.py").resolve()
    if self_src != self_dst:
        shutil.copy(self_src, self_dst)
        print("  Copied: index.py")

    for f in SCREENER_FILES:
        src = src_date_dir / f
        if src.exists():
            dst = DEST_FOLDER / f
            shutil.copy(src, dst)
            inject_brand(dst)
            print(f"  Copied + branded: {f}")
        else:
            print(f"  Missing: {f}")

    adv = Path(r"E:\stockscreener\advanced")
    for f in OI_FILES:
        continue
        src = adv / f
        if src.exists():
            dst = DEST_FOLDER / f
            shutil.copy(src, dst)
            inject_brand(dst)
            print(f"  Copied + branded OI: {f}")

    for d in SOURCE_BASE.iterdir():
        continue
        if not d.is_dir():
            continue
        v4h = d / "ai_analysis_v4.html"
        if v4h.exists():
            dst_name = f"ai_analysis_v4_{d.name.replace('-', '_')}.html"
            dst = DEST_FOLDER / dst_name

        legacy = d / "ai_analysis.html"
        if legacy.exists():
            dst_name = f"ai_analysis_{d.name.replace('-', '_')}.html"
            dst = DEST_FOLDER / dst_name


# ── REGIME COLORS (adjusted for white background) ─────────────────────────────

def regime_colors(regime: str) -> tuple:
    """Returns (bg, text_color, border) tuples — light versions for white theme."""
    r = regime.upper()
    if r in ("BULL", "BULLISH"):
        return "#dcfce7", "#15803d", "#bbf7d0"
    if r in ("BEAR", "BEARISH"):
        return "#fee2e2", "#b91c1c", "#fecaca"
    if r == "TRANSITION":
        return "#dbeafe", "#1d4ed8", "#bfdbfe"
    return "#fef9c3", "#92400e", "#fef08a"


def strength_color(s: int) -> str:
    if s >= 7: return "#15803d"
    if s >= 4: return "#92400e"
    return "#b91c1c"


def cap_color(c: str) -> str:
    c = c.upper()
    if c == "HIGH":       return "#15803d"
    if c == "AVOID_ALL":  return "#b91c1c"
    return "#92400e"


# ── TRADER VIEW HTML ──────────────────────────────────────────────────────────

_BIAS_COLORS = {
    "BEARISH": "#b91c1c", "BULLISH": "#15803d", "RANGE": "#92400e",
    "SHORT": "#b91c1c", "LONG": "#15803d",
}

_BIAS_DISPLAY_MAP = {
    "SHORT": "BEARISH", "LONG": "BULLISH", "RANGE": "RANGE",
    "BEARISH": "BEARISH", "BULLISH": "BULLISH",
}

def _bias_col(bias: str) -> str:
    return _BIAS_COLORS.get(str(bias).upper(), "#374151")

def _bias_label(bias: str) -> str:
    return _BIAS_DISPLAY_MAP.get(str(bias).upper(), str(bias).upper())

def _fmt(v) -> str:
    try:
        iv = int(v)
        return f"{iv:,}" if iv else "—"
    except:
        return "—"

def _trader_tf_card(tf_label: str, t: dict, card_id: str) -> str:
    if not t:
        return f"<div class='tv-tf'><div class='tv-tf-hdr'><span class='tv-tf-label'>{tf_label}</span></div><p class='tv-empty'>No data</p></div>"

    raw_bias = str(t.get("bias", "RANGE")).upper()
    bias     = _bias_label(raw_bias)
    bc       = _bias_col(raw_bias)
    res      = t.get("resistance", [0, 0])
    sup      = t.get("support",    [0, 0])
    r1       = _fmt(res[0] if res else 0)
    r2       = _fmt(res[1] if len(res) > 1 else 0)
    s1       = _fmt(sup[0] if sup else 0)
    s2       = _fmt(sup[1] if len(sup) > 1 else 0)
    note     = t.get("note", "")

    b_zone   = t.get("short_entry", "—") or "—"
    b_inv    = _fmt(t.get("short_stop", 0))
    b_mm1    = _fmt(t.get("short_t1",  0))
    b_mm2    = _fmt(t.get("short_t2",  0))
    b_inv_n  = t.get("invalidation_short", "—") or "—"

    u_zone   = t.get("long_entry", "—") or "—"
    u_inv    = _fmt(t.get("long_stop", 0))
    u_mm1    = _fmt(t.get("long_t1",  0))
    u_mm2    = _fmt(t.get("long_t2",  0))
    u_inv_n  = t.get("invalidation_long", "—") or "—"

    show_bear = bias in ("BEARISH", "RANGE")
    show_bull = bias in ("BULLISH", "RANGE")

    bear_html = ""
    if show_bear:
        bear_html = f"""
<div class='tv-setup tv-short'>
  <div class='tv-setup-title'>📉 BEAR PRESSURE ZONE</div>
  <div class='tv-row'><span class='tv-k'>Bear Strength At</span><span class='tv-v tv-entry-s'>{b_zone}</span></div>
  <div class='tv-row'><span class='tv-k'>Thesis Invalidates</span><span class='tv-v tv-stop'>{b_inv}</span></div>
  <div class='tv-row'><span class='tv-k'>Measured Move 1 / 2</span><span class='tv-v tv-tgt'>{b_mm1} / {b_mm2}</span></div>
  <div class='tv-row'><span class='tv-k'>Invalid When</span><span class='tv-v tv-inv'>{b_inv_n}</span></div>
</div>"""

    bull_html = ""
    if show_bull:
        bull_html = f"""
<div class='tv-setup tv-long'>
  <div class='tv-setup-title'>📈 BULL PRESSURE ZONE</div>
  <div class='tv-row'><span class='tv-k'>Bull Strength At</span><span class='tv-v tv-entry-l'>{u_zone}</span></div>
  <div class='tv-row'><span class='tv-k'>Thesis Invalidates</span><span class='tv-v tv-stop'>{u_inv}</span></div>
  <div class='tv-row'><span class='tv-k'>Measured Move 1 / 2</span><span class='tv-v tv-tgt'>{u_mm1} / {u_mm2}</span></div>
  <div class='tv-row'><span class='tv-k'>Invalid When</span><span class='tv-v tv-inv'>{u_inv_n}</span></div>
</div>"""

    note_html = ""
    if note and note != "—":
        note_html = f"<div class='tv-note' style='border-left-color:{bc}'>📌 {note}</div>"

    return f"""
<div class='tv-tf' id='{card_id}'>
  <div class='tv-tf-hdr'>
    <span class='tv-tf-label'>{tf_label}</span>
    <span class='tv-bias-pill' style='background:{bc}18;color:{bc};border:1px solid {bc}44'>{bias}</span>
  </div>
  <div class='tv-levels'>
    <div class='tv-level-row'>
      <span class='tv-lr-icon' style='color:#b91c1c'>R</span>
      <span class='tv-lr-vals' style='color:#b91c1c'>{r1} <span style='opacity:.4'>/</span> {r2}</span>
    </div>
    <div class='tv-level-row'>
      <span class='tv-lr-icon' style='color:#15803d'>S</span>
      <span class='tv-lr-vals' style='color:#15803d'>{s1} <span style='opacity:.4'>/</span> {s2}</span>
    </div>
  </div>
  <div class='tv-setups'>
    {bear_html}
    {bull_html}
  </div>
  {note_html}
</div>"""


def build_trader_section(trader: dict) -> str:
    if not trader:
        return ""

    intra   = trader.get("intraday", {})
    weekly  = trader.get("weekly",   {})
    monthly = trader.get("monthly",  {})

    cards = (
        _trader_tf_card("Intraday", intra,   "tv-intraday") +
        _trader_tf_card("Weekly",   weekly,  "tv-weekly") +
        _trader_tf_card("Monthly",  monthly, "tv-monthly")
    )

    return f"""
<div class='fs-trader-section'>
  <div class='tv-cards'>
    {cards}
  </div>
</div>
<script>
(function(){{
  var first = document.querySelector('.tv-tab');
  if(first) tvTab(first);
}})();
</script>"""


# ── SIGNAL CARD ───────────────────────────────────────────────────────────────

def build_signal_card(sig: dict, is_featured: bool) -> str:
    if not sig:
        return ""
    rbg, rtx, rbd = regime_colors(sig["regime"])
    scol  = strength_color(sig["strength"])
    ccol  = cap_color(sig["cap"])
    vix   = sig.get("vix_zone", "")
    vix_c = "#b91c1c" if vix in ("HIGH_FEAR", "CRISIS", "ELEVATED") else "#15803d" if vix in ("LOW", "NORMAL") else "#92400e"

    if is_featured:
        trader_html = build_trader_section(sig.get("trader", {}))

        return f"""
<div class="featured-signal">
  <div class="fs-header">
    <div class="fs-date">{sig["date_disp"]}</div>
    <div class="fs-regime-pill" style="background:{rbg};color:{rtx};border-color:{rbd}">
      {sig["regime"]}
    </div>
    <div class="fs-metrics">
      <div class="fs-metric">
        <span class="fs-metric-label" title="Signal alignment score — 10 = all data sources confirm same structural bias">SIGNAL ALIGNMENT ⓘ</span>
        <span class="fs-metric-val" style="color:{scol}">{sig["strength"]}/10</span>
      </div>
      <div class="fs-metric">
        <span class="fs-metric-label">OI SIGNAL</span>
        <span class="fs-metric-val" style="color:{ccol}">{sig["cap"]}</span>
      </div>
      <div class="fs-metric">
        <span class="fs-metric-label">VIX ZONE</span>
        <span class="fs-metric-val" style="color:{vix_c}">{vix or "—"}</span>
      </div>
      <div class="fs-metric">
        <span class="fs-metric-label">FII vs RETAIL OI</span>
        <span class="fs-metric-val" style="color:{{'#b91c1c' if 'SHORT_CLIENT_LONG' in sig.get('fii','') else '#15803d' if 'LONG_CLIENT_SHORT' in sig.get('fii','') else '#6b7280'}}">{sig.get("fii","—").replace("FII_SHORT_CLIENT_LONG","Diverge ↓").replace("FII_LONG_CLIENT_SHORT","Diverge ↑").replace("ALIGNED","Aligned")}</span>
      </div>
    </div>
  </div>

{'<div class="fs-anomalies">' + "".join(f'<div class="anom-tag">⚡ {a}</div>' for a in sig["anomalies"]) + '</div>' if sig["anomalies"] else ""}

  <div class="fs-body">
    <div class="fs-col">
      <div class="fs-section-title">Market Structure Summary</div>
      <div class="fs-text">{sig["synthesis"] or "—"}</div>
    </div>
    <div class="fs-col">
      <div class="fs-section-title">Key Data Points to Watch</div>
      <div class="fs-text">{sig["action"] or "—"}</div>
    </div>
  </div>

 {'<div class="fs-risks">' + "".join(f'<div class="risk-item">⚠ {r}</div>' for r in sig["risks"]) + '</div>' if sig["risks"] else ""}

  {trader_html}

  <div style="padding:10px 24px 14px;border-top:1px solid var(--border);background:#fafafa">
    <p style="font-size:10px;color:var(--tx3);line-height:1.6">
      ⓘ <strong style="color:var(--tx3)">Educational data only.</strong>
      Technical levels derived from public NSE OI, FII participant data &amp; VIX.
      Not investment advice. Not SEBI-registered. All decisions are solely your own responsibility.
    </p>
  </div>

  <div class="fs-footer">
    <a href="{sig['ai_file']}" class="btn-outline" target="_blank">Full Technical Report →</a>
  </div>
</div>"""
    else:
        return f"""
<div class="hist-card" data-regime="{sig['regime'].lower()}">
  <div class="hist-top">
    <span class="hist-date">{sig["date_disp"]}</span>
    <span class="hist-regime" style="background:{rbg};color:{rtx};border:1px solid {rbd}">{sig["regime"]}</span>
  </div>
  <div class="hist-strength">
    <div class="str-bar-wrap" title="Signal clarity — 10 = all signals aligned"><div class="str-bar" style="width:{sig['strength']*10}%;background:{scol}"></div></div>
    <span style="color:{scol};font-size:11px" title="Clarity">{sig['strength']}/10 clarity</span>
  </div>
  <div class="hist-snip">{sig["synthesis"][:160] + "…" if len(sig["synthesis"]) > 160 else sig["synthesis"]}</div>
  <div class="hist-links">
    <a href="{sig['ai_file']}" target="_blank">Full Report →</a>
  </div>
</div>"""


# ── SEO HELPERS ───────────────────────────────────────────────────────────────

# Primary site identity — matches your <meta> snippet exactly
_SITE_TITLE       = "InfoAlpha | NSE Stock Screener India, Momentum Stocks & Institutional Flow Analysis"
_SITE_DESCRIPTION = (
    "InfoAlpha provides NSE stock screeners, momentum stock analysis, market breadth indicators, "
    "institutional flow tracking, FII options OI analysis and sector rotation insights for "
    "Indian traders and investors."
)
_SITE_KEYWORDS = (
    "NSE stock screener India, momentum stocks India, institutional flow analysis NSE, "
    "FII OI analysis, India VIX analysis, Nifty options open interest, market breadth NSE, "
    "delivery spike screener, sector rotation NSE, FII vs retail OI, "
    "market regime BULL BEAR NEUTRAL, EOD market analysis India, "
    "NSE technical analysis, options OI chart Nifty, "
    "InfoAlpha, infoalpha.in, Sivasankar S, PositionalSystem"
)
_SITE_URL         = "https://infoalpha.in/"
_SITE_CANONICAL   = "https://infoalpha.in/"
_SITE_IMAGE       = "https://infoalpha.in/banner.png"
_SITE_NAME        = "InfoAlpha"
_AUTHOR_NAME      = "Sivasankar S"
_AUTHOR_LINKEDIN  = "https://www.linkedin.com/in/ssivasankar/"
_AUTHOR_YOUTUBE   = "https://www.youtube.com/@InfoAlphain"
_AUTHOR_TWITTER   = "@ssankarsiva"
_AUTHOR_TELEGRAM  = "https://t.me/volumepricemove"


def _build_seo_head(featured: dict) -> str:
    """
    Build the full <head> SEO block.

    - Static title & description always use the primary brand copy.
    - OG / Twitter cards are enriched with today's regime signal when available
      (good for rich previews when shared on social) but the <title> and
      meta description remain stable for Google indexing.
    """
    # featured dict still passed in — reserved for future dynamic enrichment

    # OG / Twitter title — fixed brand copy, consistent for all social platforms
    og_title = "InfoAlpha | NSE Stock Screener India, Momentum Stocks & Institutional Flow Analysis"

    # OG / Twitter description — clear, compelling, under 160 chars for social previews
    og_desc = (
        "Free NSE stock screeners for Indian traders — market breadth, delivery spikes, "
        "momentum & MA scoring, FII options OI analysis and sector rotation. "
        "Daily EOD updates. Educational purpose only."
    )

    # Schema.org structured data
    schema_website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": _SITE_NAME,
        "url": "https://infoalpha.in/",
        "description": _SITE_DESCRIPTION,
        "inLanguage": "en-IN",
        "author": {
            "@type": "Person",
            "name": _AUTHOR_NAME,
            "url": _AUTHOR_LINKEDIN,
            "sameAs": [
                _AUTHOR_YOUTUBE,
                _AUTHOR_TWITTER,
                _AUTHOR_LINKEDIN,
                _AUTHOR_TELEGRAM,
                "https://x.com/ssankarsiva",
                "https://www.drupal.org/u/ssankarsiva"
            ]
        }
    }

    schema_webpage = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": _SITE_TITLE,
        "description": _SITE_DESCRIPTION,
        "url": _SITE_CANONICAL,
        "isPartOf": {"@type": "WebSite", "url": "https://infoalpha.in/"},
        "breadcrumb": {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://infoalpha.in/"},
                {"@type": "ListItem", "position": 2, "name": "Trading Tools", "item": _SITE_CANONICAL}
            ]
        }
    }

    schema_tools = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "NSE Market Screeners — InfoAlpha",
        "description": "Free NSE stock screeners for Indian traders: breadth analysis, delivery spikes, momentum/MA scoring, high-low resilience and sector rotation.",
        "url": _SITE_CANONICAL,
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Market Breadth Analysis",     "url": "https://infoalpha.in/breadth.html"},
            {"@type": "ListItem", "position": 2, "name": "Delivery Spike Screener",     "url": "https://infoalpha.in/delivery_spike.html"},
            {"@type": "ListItem", "position": 3, "name": "High / Low Resilience",       "url": "https://infoalpha.in/highlow.html"},
            {"@type": "ListItem", "position": 4, "name": "Momentum & Moving Average",   "url": "https://infoalpha.in/momentum_ma.html"},
            {"@type": "ListItem", "position": 5, "name": "Sector Rotation",             "url": "https://infoalpha.in/sector_rotation.html"},
        ]
    }

    return f"""<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<!-- ═══ PRIMARY SEO ═══════════════════════════════════════════════════════ -->
<title>{_SITE_TITLE}</title>
<meta name="description"   content="{_SITE_DESCRIPTION}">
<meta name="keywords"      content="{_SITE_KEYWORDS}">
<meta name="author"        content="{_AUTHOR_NAME} — InfoAlpha">
<meta name="robots"        content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<meta name="googlebot"     content="index, follow">
<link rel="canonical"      href="{_SITE_CANONICAL}">

<!-- ═══ OPEN GRAPH (Facebook / WhatsApp / LinkedIn) ══════════════════════ -->
<meta property="og:type"         content="website">
<meta property="og:site_name"    content="{_SITE_NAME}">
<meta property="og:title"        content="{og_title}">
<meta property="og:description"  content="{og_desc}">
<meta property="og:url"          content="{_SITE_CANONICAL}">
<meta property="og:image"        content="{_SITE_IMAGE}">
<meta property="og:image:width"  content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt"    content="InfoAlpha — NSE Stock Screener & Institutional Flow Analysis">
<meta property="og:locale"       content="en_IN">

<!-- ═══ TWITTER / X CARD ════════════════════════════════════════════════ -->
<meta name="twitter:card"        content="summary_large_image">
<meta name="twitter:site"        content="{_AUTHOR_TWITTER}">
<meta name="twitter:creator"     content="{_AUTHOR_TWITTER}">
<meta name="twitter:title"       content="{og_title}">
<meta name="twitter:description" content="{og_desc}">
<meta name="twitter:image"       content="{_SITE_IMAGE}">
<meta name="twitter:image:alt"   content="InfoAlpha NSE Trading Tools">

<!-- ═══ MOBILE / APP META ════════════════════════════════════════════════ -->
<meta name="theme-color"         content="#ffffff">
<meta name="application-name"    content="InfoAlpha">
<meta name="mobile-web-app-capable"      content="yes">
<meta name="apple-mobile-web-app-title"  content="InfoAlpha">

<!-- ═══ SCHEMA.ORG STRUCTURED DATA ══════════════════════════════════════ -->
<script type="application/ld+json">{json.dumps(schema_website,  ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(schema_webpage,  ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(schema_tools,    ensure_ascii=False)}</script>"""


# ── TRADINGTOOL HTML ──────────────────────────────────────────────────────────

def generate_tradingtool(featured: dict, history: list) -> str:
    hist_html = "".join(build_signal_card(s, False) for s in history)
    feat_html = (
        build_signal_card(featured, True)
        if featured
        else "<p style='color:#6b7280'>No analysis data available yet.</p>"
    )

    seo_head = _build_seo_head(featured)

    return f"""<!DOCTYPE html>
<html lang="en" prefix="og: https://ogp.me/ns#">
<head>
{seo_head}

<!-- ═══ ANALYTICS ════════════════════════════════════════════════════════ -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-TEBE4BLSYD"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-TEBE4BLSYD');
</script>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700;800&display=swap" rel="stylesheet">
<style>
:root{{
  --bg:#ffffff;--bg2:#f8f9fa;--surface:#f0f2f5;--surface2:#e8eaed;
  --border:#d1d5db;--border2:#9ca3af;--tx:#111827;--tx2:#374151;--tx3:#6b7280;
  --accent:#1a6fcc;--accent2:#1558a8;--bull:#15803d;--bear:#b91c1c;--neu:#92400e;
  --mono:'Space Mono',monospace;--sans:'Sora',sans-serif;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--tx);font-family:var(--sans);font-size:13px;min-height:100vh;background-image:radial-gradient(ellipse 80% 50% at 50% -20%, rgba(26,111,204,.04) 0%, transparent 60%);}}
nav{{position:sticky;top:0;z-index:100;background:rgba(255,255,255,.95);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);box-shadow:0 1px 4px rgba(0,0,0,.06);padding:0 28px;display:flex;align-items:center;justify-content:space-between;height:54px;}}
.nav-brand{{display:flex;flex-direction:row;align-items:center;gap:10px;text-decoration:none}}
.nav-brand-name{{font-family:var(--mono);font-weight:700;font-size:14px;color:var(--accent);letter-spacing:.5px}}
.nav-brand-sub{{font-size:9px;color:var(--tx3);letter-spacing:1.5px;text-transform:uppercase}}
.nav-links{{display:flex;gap:22px;align-items:center}}
.nav-links a{{color:var(--tx2);text-decoration:none;font-size:12px;font-weight:600;letter-spacing:.3px;transition:color .15s}}
.nav-links a:hover{{color:var(--tx)}}
.nav-cta{{background:var(--accent);color:#fff!important;font-weight:700!important;padding:6px 16px;border-radius:6px;font-size:11px!important;letter-spacing:.5px;text-decoration:none;transition:background .15s}}
.nav-cta:hover{{background:var(--accent2)!important}}
.nav-home-link{{display:flex;align-items:center;gap:6px;background:rgba(26,111,204,.08);border:1px solid rgba(26,111,204,.2);color:var(--accent)!important;padding:5px 12px;border-radius:6px;font-size:11px!important;font-weight:700!important;letter-spacing:.3px;text-decoration:none;transition:all .15s;}}
.nav-home-link:hover{{background:rgba(26,111,204,.14)!important}}
.hero{{padding:56px 28px 42px;max-width:1100px;margin:0 auto;text-align:center}}
.hero-tag{{display:inline-block;background:rgba(26,111,204,.07);border:1px solid rgba(26,111,204,.18);color:var(--accent);font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;padding:4px 14px;border-radius:20px;margin-bottom:20px}}
.hero h1{{font-size:clamp(26px,4.5vw,44px);font-weight:800;line-height:1.15;color:var(--tx);margin-bottom:14px}}
.hero h1 span{{color:var(--accent)}}
.hero-sub{{color:var(--tx2);font-size:14px;max-width:600px;margin:0 auto 32px;line-height:1.7;font-weight:300}}
.hero-stats{{display:flex;gap:0;justify-content:center;background:var(--surface);border:1px solid var(--border);border-radius:12px;overflow:hidden;max-width:680px;margin:0 auto}}
.hero-stat{{flex:1;padding:18px 12px;text-align:center;border-right:1px solid var(--border)}}
.hero-stat:last-child{{border-right:none}}
.hs-val{{font-family:var(--mono);font-size:20px;font-weight:700;color:var(--tx)}}
.hs-label{{font-size:9px;color:var(--tx3);letter-spacing:1.5px;text-transform:uppercase;margin-top:3px}}
.section{{max-width:1100px;margin:0 auto;padding:40px 28px}}
.section-label{{font-size:9px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:var(--tx3);margin-bottom:6px;display:flex;align-items:center;gap:8px}}
.section-label::before{{content:"";display:block;width:18px;height:1px;background:var(--border2)}}
.section-title{{font-size:22px;font-weight:700;color:var(--tx);margin-bottom:24px}}
.featured-signal{{background:var(--bg);border:1px solid var(--border2);border-radius:14px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.06)}}
.fs-header{{padding:20px 24px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;flex-wrap:wrap;gap:16px;background:var(--bg)}}
.fs-date{{font-family:var(--mono);font-size:11px;color:var(--tx2);letter-spacing:.5px}}
.fs-regime-pill{{padding:5px 16px;border-radius:8px;font-family:var(--mono);font-weight:700;font-size:14px;border:1px solid;letter-spacing:1px}}
.fs-metrics{{display:flex;gap:20px;margin-left:auto;flex-wrap:wrap}}
.fs-metric{{display:flex;flex-direction:column;align-items:center;gap:2px}}
.fs-metric-label{{font-size:8px;letter-spacing:1.5px;color:var(--tx3);text-transform:uppercase}}
.fs-metric-val{{font-family:var(--mono);font-size:13px;font-weight:700;color:var(--tx2)}}
.fs-anomalies{{padding:12px 24px;background:#fffbeb;border-bottom:1px solid var(--border);display:flex;flex-wrap:wrap;gap:8px}}
.anom-tag{{background:rgba(217,119,6,.08);border:1px solid rgba(217,119,6,.2);color:#d97706;font-size:10px;padding:3px 10px;border-radius:5px;line-height:1.5}}
.fs-body{{display:grid;grid-template-columns:1fr 1fr;gap:0}}
@media(max-width:700px){{.fs-body{{grid-template-columns:1fr}}}}
.fs-col{{padding:20px 24px;border-right:1px solid var(--border)}}
.fs-col:last-child{{border-right:none}}
.fs-section-title{{font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--tx3);margin-bottom:10px}}
.fs-text{{color:var(--tx2);font-size:12px;line-height:1.8}}
.fs-risks{{padding:12px 24px;background:#fef2f2;border-top:1px solid var(--border);display:flex;flex-wrap:wrap;gap:8px}}
.risk-item{{background:rgba(185,28,28,.06);border:1px solid rgba(185,28,28,.15);color:#b91c1c;font-size:10px;padding:3px 10px;border-radius:5px;line-height:1.5}}
.fs-footer{{padding:14px 24px;border-top:1px solid var(--border);display:flex;gap:12px;background:var(--bg2)}}
.btn-outline{{border:1px solid var(--border2);color:var(--accent);padding:6px 16px;border-radius:6px;font-size:11px;font-weight:600;text-decoration:none;letter-spacing:.3px;transition:all .15s}}
.btn-outline:hover{{background:rgba(26,111,204,.07);border-color:var(--accent)}}
.fs-trader-section{{border-top:1px solid var(--border);padding:16px 24px 20px;background:var(--surface);}}
.tv-tabs{{display:flex;gap:6px;flex-wrap:wrap}}
.tv-tab{{background:var(--bg);border:1px solid var(--border);color:var(--tx3);font-size:11px;font-weight:600;padding:5px 12px;border-radius:6px;cursor:pointer;display:flex;align-items:center;gap:6px;transition:all .15s;--tv-active:#92400e;}}
.tv-tab:hover{{border-color:var(--border2);color:var(--tx2)}}
.tv-tab.tv-active{{border-color:var(--tv-active);color:var(--tv-active);background:rgba(146,64,14,.05);}}
.tv-cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
@media(max-width:800px){{.tv-cards{{grid-template-columns:1fr}}}}
.tv-tf{{background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:12px 14px;display:none;}}
.tv-tf.tv-visible{{display:block}}
.tv-tf-hdr{{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;}}
.tv-tf-label{{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--tx3);}}
.tv-bias-pill{{font-family:var(--mono);font-size:10px;font-weight:700;padding:2px 8px;border-radius:5px;}}
.tv-levels{{background:var(--surface);border-radius:6px;padding:8px 10px;margin-bottom:10px;border:1px solid var(--border)}}
.tv-level-row{{display:flex;align-items:center;gap:8px;padding:3px 0;}}
.tv-lr-icon{{font-family:var(--mono);font-size:10px;font-weight:700;min-width:14px;}}
.tv-lr-vals{{font-family:var(--mono);font-size:11px;font-weight:600;letter-spacing:.3px;}}
.tv-setups{{display:flex;flex-direction:column;gap:8px}}
.tv-setup{{border-radius:6px;padding:8px 10px;font-size:11px;}}
.tv-short{{background:rgba(185,28,28,.04);border:1px solid rgba(185,28,28,.12)}}
.tv-long{{background:rgba(21,128,61,.04);border:1px solid rgba(21,128,61,.12)}}
.tv-setup-title{{font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;}}
.tv-short .tv-setup-title{{color:#b91c1c}}
.tv-long .tv-setup-title{{color:#15803d}}
.tv-row{{display:flex;justify-content:space-between;padding:2px 0;border-bottom:1px solid rgba(0,0,0,.05)}}
.tv-row:last-child{{border-bottom:none}}
.tv-k{{color:var(--tx3);font-size:10px}}
.tv-v{{font-size:10px;font-weight:600;text-align:right;max-width:60%;word-break:break-word}}
.tv-entry-s{{color:#b91c1c}}.tv-entry-l{{color:#15803d}}.tv-stop{{color:#d97706}}.tv-tgt{{color:#1a6fcc}}.tv-inv{{color:var(--tx3);font-size:9px}}
.tv-note{{margin-top:8px;border-left:2px solid #92400e;padding:5px 8px;font-size:10px;color:var(--tx3);line-height:1.6;border-radius:0 4px 4px 0;background:rgba(146,64,14,.03);}}
.tv-empty{{color:var(--tx3);font-size:11px;font-style:italic;padding:8px 0}}
.hist-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}}
.hist-card{{background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:16px;transition:border-color .15s,transform .15s,box-shadow .15s}}
.hist-card:hover{{border-color:var(--border2);transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.07)}}
.hist-top{{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}}
.hist-date{{font-family:var(--mono);font-size:10px;color:var(--tx3)}}
.hist-regime{{padding:2px 8px;border-radius:5px;font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.5px}}
.str-bar-wrap{{height:3px;background:var(--border);border-radius:2px;flex:1}}
.str-bar{{height:3px;border-radius:2px;transition:width .4s}}
.hist-strength{{display:flex;align-items:center;gap:8px;margin-bottom:10px}}
.hist-snip{{color:var(--tx3);font-size:11px;line-height:1.65;margin-bottom:10px}}
.hist-links{{display:flex;gap:10px}}
.hist-links a{{color:var(--accent);font-size:10px;text-decoration:none;font-weight:600}}
.hist-links a:hover{{text-decoration:underline}}
.tool-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}}
.tool-card{{background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:16px 18px;text-decoration:none;transition:border-color .15s,background .15s,box-shadow .15s;display:block}}
.tool-card:hover{{border-color:var(--accent2);background:var(--surface);box-shadow:0 2px 8px rgba(0,0,0,.07)}}
.tool-icon{{font-size:20px;margin-bottom:10px}}
.tool-name{{font-weight:700;font-size:13px;color:var(--tx);margin-bottom:4px}}
.tool-desc{{color:var(--tx3);font-size:11px;line-height:1.5}}
.tool-badge{{display:inline-block;margin-top:8px;background:rgba(26,111,204,.07);color:var(--accent);font-size:9px;padding:2px 7px;border-radius:4px;letter-spacing:.5px;font-weight:600}}
.how-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}}
.how-step{{background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:20px 18px;position:relative;overflow:hidden}}
.how-step::before{{content:attr(data-num);position:absolute;top:-10px;right:14px;font-family:var(--mono);font-size:72px;font-weight:700;color:rgba(26,111,204,.04);line-height:1}}
.how-step-title{{font-weight:700;font-size:13px;color:var(--tx);margin-bottom:6px}}
.how-step-desc{{color:var(--tx3);font-size:11px;line-height:1.65}}
.reports-list{{background:var(--bg);border:1px solid var(--border);border-radius:10px;overflow:hidden}}
.reports-list li{{list-style:none;border-bottom:1px solid var(--border);padding:10px 18px;display:flex;align-items:center;gap:8px}}
.reports-list li:last-child{{border-bottom:none}}
.reports-list li::before{{content:"▸";color:var(--accent);font-size:11px}}
.reports-list li a{{color:var(--tx2);text-decoration:none;font-family:var(--mono);font-size:11px;transition:color .15s}}
.reports-list li a:hover{{color:var(--accent)}}
.about-grid{{display:grid;grid-template-columns:2fr 1fr;gap:20px}}
@media(max-width:700px){{.about-grid{{grid-template-columns:1fr}}}}
.about-card{{background:var(--bg);border:1px solid var(--border);border-radius:12px;padding:24px}}
.social-links{{display:flex;flex-direction:column;gap:10px;margin-top:16px}}
.social-link{{display:flex;align-items:center;gap:10px;text-decoration:none;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:9px 14px;transition:border-color .15s}}
.social-link:hover{{border-color:var(--border2)}}
.social-link-icon{{font-size:16px}}
.social-link-text{{color:var(--tx2);font-size:11px;font-weight:600}}
.support-box{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:28px;margin-top:20px}}
.upi-block{{background:rgba(26,111,204,.06);border:1px solid rgba(26,111,204,.15);border-radius:8px;padding:16px 20px;margin-top:14px;font-family:var(--mono);font-size:13px;color:var(--accent)}}
.cta-banner{{background:linear-gradient(135deg,#eff6ff 0%,#dbeafe 100%);border:1px solid rgba(26,111,204,.2);border-radius:14px;padding:42px 32px;text-align:center;margin:40px 28px;max-width:1100px;margin-left:auto;margin-right:auto}}
.cta-title{{font-size:22px;font-weight:800;color:var(--tx);margin-bottom:10px}}
.cta-sub{{color:var(--tx2);font-size:13px;margin-bottom:22px}}
.cta-btn{{background:var(--accent);color:#fff;padding:12px 32px;border-radius:8px;font-weight:700;font-size:13px;text-decoration:none;display:inline-block;transition:background .15s}}
.cta-btn:hover{{background:var(--accent2);color:#fff}}
footer{{border-top:1px solid var(--border);padding:20px 28px;text-align:center;color:var(--tx3);font-size:11px;background:var(--bg2)}}
footer a{{color:var(--tx3);text-decoration:none}}
footer a:hover{{color:var(--accent)}}
.divider{{height:1px;background:var(--border);max-width:1100px;margin:0 auto}}
@media(max-width:600px){{.nav-links{{display:none}}.hero{{padding:48px 16px 36px}}.section{{padding:28px 16px}}}}
</style>
</head>

<body>

<!-- NAV -->
<nav>
  <a href="index.html" class="nav-brand" aria-label="InfoAlpha — NSE Market Intelligence Home">
    <img src="logo.png" alt="InfoAlpha NSE Stock Screener Logo" width="40" height="40" style="object-fit:contain;border-radius:4px">
    <div>
      <span class="nav-brand-name">InfoAlpha</span>
      <span class="nav-brand-sub">NSE Structure · Data Intelligence</span>
    </div>
  </a>
  <div class="nav-links">
    <a href="#signals">Signals</a>
    <a href="#oi">OI Charts</a>
    <a href="#about">About</a>
    <a href="digital.html" class="nav-home-link">🌐 Digital Services</a>
    <a href="https://t.me/volumepricemove" target="_blank" rel="noopener" class="nav-cta" style="background:#229ED9">✈ Telegram</a>
    <a href="https://www.youtube.com/@InfoAlphain" target="_blank" rel="noopener" class="nav-cta">▶ YouTube</a>
  </div>
</nav>

<!-- HERO -->
<header class="hero">
  <img src="logo.png" alt="InfoAlpha — NSE Stock Screener India" width="90" height="90"
       style="display:block;object-fit:contain;margin:0 auto 20px;border-radius:8px">
  <div class="hero-tag">NSE India · Institutional Intelligence</div>
  <h1>NSE Stock Screener &amp; <span>Institutional Flow Analysis</span></h1>
  <p class="hero-sub">
    Free NSE stock screeners — market breadth, delivery spikes, momentum,
    FII options OI and sector rotation. Understand <em>what the data shows</em>,
    not what to trade.
  </p>
  <div class="hero-stats" aria-label="Site statistics">
    <div class="hero-stat"><div class="hs-val">5+</div><div class="hs-label">Screeners</div></div>
    <div class="hero-stat"><div class="hs-val">Monthly</div><div class="hs-label">OI Expiry</div></div>
    <div class="hero-stat"><div class="hs-val">EOD</div><div class="hs-label">Daily Update</div></div>
  </div>
</header>

<!-- SCREENERS -->
<main>
<section class="section" id="signals" aria-labelledby="screeners-heading">
  <div class="section-label">Market Screeners</div>
  <h2 class="section-title" id="screeners-heading">NSE Signal Dashboards</h2>
  <div class="tool-grid">
    <a href="breadth.html" class="tool-card" target="_blank" rel="noopener"
       aria-label="NSE Market Breadth Analysis screener">
      <div class="tool-icon">📊</div>
      <div class="tool-name">Breadth Analysis</div>
      <div class="tool-desc">Advances/declines, EMA% and market participation across N50/N200/N500</div>
      <span class="tool-badge">60-day history</span>
    </a>
    <a href="delivery_spike.html" class="tool-card" target="_blank" rel="noopener"
       aria-label="NSE Delivery Spike screener — institutional accumulation">
      <div class="tool-icon">📦</div>
      <div class="tool-name">Delivery Spike Screener</div>
      <div class="tool-desc">Institutional accumulation detection — 2× delivery spikes filtered for HFT noise</div>
      <span class="tool-badge">smart money</span>
    </a>
    <a href="highlow.html" class="tool-card" target="_blank" rel="noopener"
       aria-label="NSE High Low Resilience screener">
      <div class="tool-icon">📈</div>
      <div class="tool-name">High / Low Resilience</div>
      <div class="tool-desc">Position within 5D–200D range. Fully resilient = above 80% across all periods</div>
      <span class="tool-badge">5 periods</span>
    </a>
    <a href="momentum_ma.html" class="tool-card" target="_blank" rel="noopener"
       aria-label="NSE Momentum and Moving Average screener">
      <div class="tool-icon">🚀</div>
      <div class="tool-name">Momentum / MA Screener</div>
      <div class="tool-desc">MA5/20/50/200 scores, ATR%, RSI, and relative strength vs NIFTYBEES</div>
      <span class="tool-badge">RS leaders tab</span>
    </a>
    <a href="sector_rotation.html" class="tool-card" target="_blank" rel="noopener"
       aria-label="NSE Sector Rotation screener">
      <div class="tool-icon">⚡</div>
      <div class="tool-name">Sector Rotation</div>
      <div class="tool-desc">Smart money phase (Accumulation / Markup / Distribution) by sector and industry</div>
      <span class="tool-badge">SM signals</span>
    </a>
  </div>
</section>

<div class="divider"></div>

<!-- OI CHARTS -->
<section class="section" id="oi" aria-labelledby="oi-heading">
  <div class="section-label">Derivatives Intelligence</div>
  <h2 class="section-title" id="oi-heading">Nifty Options OI Structure</h2>
  <div class="tool-grid">
    <a href="options_oi_chartmonth.html" class="tool-card" target="_blank" rel="noopener"
       aria-label="Nifty monthly options OI chart">
      <div class="tool-icon">📅</div>
      <div class="tool-name">Monthly OI Chart</div>
      <div class="tool-desc">Monthly expiry option structure and max pain analysis</div>
    </a>
    <a href="institutional_oi_dashboard.html" class="tool-card" target="_blank" rel="noopener"
       aria-label="Institutional OI dashboard">
      <div class="tool-icon">🏛</div>
      <div class="tool-name">Institutional OI Dashboard</div>
      <div class="tool-desc">FII vs retail OI positioning — divergence signals and flow analysis</div>
    </a>
  </div>
</section>

<div class="divider"></div>

<!-- ABOUT -->
<section class="section" id="about" aria-labelledby="about-heading">
  <div class="section-label">About</div>
  <h2 class="section-title" id="about-heading">Who Builds This</h2>
  <div class="about-grid">
    <div class="about-card">
      <p style="color:var(--tx2);font-size:13px;line-height:1.9;margin-bottom:14px">
        InfoAlpha is an independent NSE market intelligence project built by
        <strong style="color:var(--tx)">Sivasankar S</strong> — a developer and quant analyst
        combining institutional flow data, options positioning and breadth analytics
        to help Indian traders understand market structure.
      </p>
      <p style="color:var(--tx3);font-size:11px;line-height:1.7">
        Also offers: Website Development · Drupal · AWS Cloud · Digital Marketing · Training →
        <a href="index.html" style="color:var(--accent);text-decoration:none;font-weight:700">infoalpha.in</a>
      </p>
      <div style="display:flex;gap:10px;margin-top:14px;flex-wrap:wrap">
        <a href="https://wa.me/919884346789" target="_blank" rel="noopener"
           style="display:flex;align-items:center;gap:7px;background:#25D366;color:#fff;font-weight:700;font-size:12px;padding:8px 16px;border-radius:8px;text-decoration:none"
           aria-label="WhatsApp Sivasankar S">💬 WhatsApp Me</a>
        <a href="https://t.me/volumepricemove" target="_blank" rel="noopener"
           style="display:flex;align-items:center;gap:7px;background:#229ED9;color:#fff;font-weight:700;font-size:12px;padding:8px 16px;border-radius:8px;text-decoration:none"
           aria-label="Telegram channel volumepricemove">✈ Telegram</a>
        <a href="digital.html"
           style="display:flex;align-items:center;gap:7px;background:rgba(26,111,204,.1);border:1px solid rgba(26,111,204,.25);color:var(--accent);font-weight:700;font-size:12px;padding:8px 16px;border-radius:8px;text-decoration:none">🌐 Digital Services</a>
      </div>
      <div class="support-box" style="margin-top:20px;padding:20px">
        <div style="color:var(--tx2);font-size:12px;line-height:1.7;margin-bottom:10px">If you find these signals useful, consider supporting the infrastructure and research:</div>
        <div class="upi-block">💸 UPI: <strong>websivasankar@okicici</strong></div>
      </div>
    </div>
      <div class="about-card" style="margin-bottom:12px">
        <div style="color:var(--tx3);font-size:9px;letter-spacing:2px;text-transform:uppercase;margin-bottom:14px">Connect with InfoAlpha</div>
        <nav class="social-links" aria-label="InfoAlpha social media links">
          <a href="https://t.me/volumepricemove" class="social-link" target="_blank" rel="noopener me"><span class="social-link-icon">✈</span><span class="social-link-text">Telegram @volumepricemove</span></a>
          <a href="https://wa.me/919884346789" class="social-link" target="_blank" rel="noopener"><span class="social-link-icon">💬</span><span class="social-link-text">WhatsApp +91 98843 46789</span></a>
          <a href="https://www.youtube.com/@InfoAlphain" class="social-link" target="_blank" rel="noopener me"><span class="social-link-icon">▶</span><span class="social-link-text">YouTube @InfoAlphain</span></a>
          <a href="https://www.linkedin.com/in/ssivasankar/" class="social-link" target="_blank" rel="noopener me"><span class="social-link-icon">in</span><span class="social-link-text">LinkedIn · Sivasankar S</span></a>
          <a href="https://x.com/ssankarsiva" class="social-link" target="_blank" rel="noopener me"><span class="social-link-icon">𝕏</span><span class="social-link-text">@ssankarsiva</span></a>
          <a href="https://www.drupal.org/u/ssankarsiva" class="social-link" target="_blank" rel="noopener me"><span class="social-link-icon">🔵</span><span class="social-link-text">Drupal · ssankarsiva</span></a>
        </nav>
      </div>

  </div>
</section>
</main>

<!-- CTA BANNER -->
<div class="cta-banner">
<section class="quant-training" style="padding:24px;border-radius:14px;background:#111827;color:#f3f4f6;line-height:1.8;border:1px solid #1f2937;">
  <h2 style="margin-bottom:10px;font-size:30px;font-weight:700;color:#ffffff;">
    Quant Trading Online Training + Top Momentum Stocks Access
  </h2>
  <p style="font-size:20px;color:#fbbf24;margin-bottom:18px;font-weight:600;">
    Program Fee: ₹8,000 (Full Program)
  </p>
  <p style="font-size:16px;color:#d1d5db;margin-bottom:16px;">
    NSE Screener Dashboard, Quant Research Demo,
    and <strong>12 Months Top Sector + Stock Score Access via Email</strong>.
  </p>
  <div style="margin-top:18px;padding:16px;border-radius:10px;background:#0f172a;border:1px solid #1e293b;">
    <h3 style="font-size:18px;color:#ffffff;margin-bottom:10px;">
      Optional Training Sessions
    </h3>
    <p style="font-size:15px;color:#cbd5e1;margin-bottom:0;">
      Price Action Trading, Technical Analysis, Multi-Timeframe Trading,
      Options OI Analytics, and Market Regime Identification.
    </p>
    <p style="font-size:14px;color:#94a3b8;margin-top:10px;margin-bottom:0;">
      Training sessions are provided only on subscriber request.
    </p>
    <p style="font-size:14px;color:#94a3b8;margin-top:10px;margin-bottom:0;">
      Educational Purpose Only. This is not investment advice or SEBI-registered research service.
    </p>
  </div>
</section>
</div>

<!-- FOOTER -->
<footer>
  <p>InfoAlpha — NSE Stock Screener India &amp; Market Intelligence &nbsp;·&nbsp; Educational / Informational Purpose Only &nbsp;·&nbsp; Not Investment Advice &nbsp;·&nbsp; Not SEBI-Registered</p>
  <p style="margin-top:5px;font-size:10px;color:#9ca3af;max-width:860px;margin-left:auto;margin-right:auto;line-height:1.6">
    All data presented is derived from publicly available NSE EOD information.
    Technical levels shown represent structural observations only and do not constitute buy/sell recommendations or investment advice.
    InfoAlpha and Sivasankar S are not registered with SEBI as investment advisers or research analysts.
    Individuals are solely responsible for their own financial decisions.
  </p>
  <p style="margin-top:8px">
    <a href="https://t.me/volumepricemove" target="_blank" rel="noopener">Telegram</a> &nbsp;·&nbsp;
    <a href="https://wa.me/919884346789" target="_blank" rel="noopener">WhatsApp</a> &nbsp;·&nbsp;
    <a href="https://www.youtube.com/@InfoAlphain" target="_blank" rel="noopener">YouTube</a> &nbsp;·&nbsp;
    <a href="https://www.linkedin.com/in/ssivasankar/" target="_blank" rel="noopener">LinkedIn</a> &nbsp;·&nbsp;
    <a href="https://x.com/ssankarsiva" target="_blank" rel="noopener">X / Twitter</a> &nbsp;·&nbsp;
    <a href="digital.html">← Digital Services</a> &nbsp;·&nbsp;
    <a href="https://infoalpha.in" target="_blank" rel="noopener">infoalpha.in</a>
  </p>
</footer>

<!-- Trader View Tab JS -->
<script>
function tvTab(btn) {{
  var target = btn.getAttribute('data-target');
  document.querySelectorAll('.tv-tab').forEach(function(b) {{ b.classList.remove('tv-active'); }});
  document.querySelectorAll('.tv-tf').forEach(function(c) {{ c.classList.remove('tv-visible'); }});
  btn.classList.add('tv-active');
  var card = document.getElementById(target);
  if (card) card.classList.add('tv-visible');
}}
document.addEventListener('DOMContentLoaded', function() {{
  var first = document.querySelector('.tv-tab');
  if (first) tvTab(first);
}});
</script>

</body>
</html>"""


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", type=str, help="Source date for screener files (YYYY-MM-DD)")
    ap.add_argument("--days", type=int, default=5, help="Days of AI analysis to show (default 5)")
    args = ap.parse_args()

    DEST_FOLDER.mkdir(parents=True, exist_ok=True)

    if args.date:
        src_date = SOURCE_BASE / args.date
    else:
        dirs = sorted([d for d in SOURCE_BASE.iterdir() if d.is_dir()],
                      key=lambda d: d.name)
        src_date = dirs[-1] if dirs else None

    if src_date and src_date.exists():
        print(f"Copying screener files from: {src_date.name}")
        copy_screener_files(src_date)
    else:
        print("  [warn] No source date folder found — skipping screener copy")

    day_pairs = find_date_dirs(SOURCE_BASE, args.days)
    if not day_pairs:
        print("  [warn] No ai_analysis_v4.json files found in output dir")
    signals = [load_signal(ds, jp) for ds, jp in day_pairs]
    signals = [s for s in signals if s]

    known = {s["date_raw"] for s in signals}
    html_only = load_html_only_signals(DEST_FOLDER, known)
    all_signals = sorted(signals + html_only, key=lambda x: x["date_raw"], reverse=True)
    featured  = all_signals[0] if all_signals else {}
    history_signals = all_signals[1:args.days]
    print(f"Loaded {len(signals)} JSON signal(s) + {len(html_only)} HTML-only signal(s)")

    html = generate_tradingtool(featured, history_signals)

    # ── Write to index.html (the stock screener / trading tool homepage) ────────
    out = DEST_FOLDER / "index.html"
    out.write_text(html, encoding="utf-8")

    print("Injecting brand into existing HTML files …")
    for f in DEST_FOLDER.glob("*.html"):
        if f.name in ("digital.html", "index.html"):
            continue
        inject_brand(f)

    print(f"✅  index.html written → {out}")
    print(f"    Featured: {featured.get('date_raw','none')} {featured.get('regime','')}")
    print(f"    History:  {[s['date_raw'] for s in history_signals]}")


if __name__ == "__main__":
    main()