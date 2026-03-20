"""
index.py  —  InfoAlpha ONE  |  Homepage Generator
==================================================
Reads the last 5 ai_analysis_v5.json files from screener/output/YYYY-MM-DD/
and generates a product-grade index.html for GitHub Pages.

Also copies the latest screener HTMLs and OI charts.

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
    "recurring_entry.html",
    "sector_rotation.html",
]

OI_FILES = [
    "options_oi_chart.html",
    "options_oi_chartnxtweek.html",
    "options_oi_chartmonth.html",
    "options_oi_chartnxtmonth.html",
    "csvweek.html",
    "csvmonth.html",
    "Dashboard.html",
    "DashboardMonth.html",
]


# ── HELPERS ───────────────────────────────────────────────────────────────────

def find_date_dirs(base: Path, n: int) -> list:
    """
    Return last n date folders that have an AI analysis JSON, newest first.
    Tries in order: ai_analysis_v4.json → ai_analysis.json → any ai_analysis*.json
    This handles the case where v4 wasn't run yet for the latest date.
    """
    candidates = sorted(
        [d for d in base.iterdir() if d.is_dir() and d.name[:4].isdigit()],
        key=lambda d: d.name,
        reverse=True,
    )
    result = []
    for d in candidates:
        # Priority 1: v4 JSON (primary going forward)
        j = d / AI_JSON_NAME
        # Priority 2: legacy plain JSON
        if not j.exists():
            j = d / "ai_analysis.json"
        # Priority 3: any ai_analysis*.json in the folder (catches custom names)
        if not j.exists():
            matches = sorted(d.glob("ai_analysis*.json"), reverse=True)
            j = matches[0] if matches else None
        if j and Path(j).exists():
            result.append((d.name, Path(j)))
            print(f"  Found: {d.name} → {Path(j).name}")
        else:
            print(f"  Skip : {d.name} — no ai_analysis*.json")
        if len(result) >= n:
            break
    return result   # [(date_str, json_path), ...]


def load_signal(date_str: str, json_path: Path) -> dict:
    """Load and normalise one day's AI analysis JSON."""
    try:
        raw = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  [warn] {date_str}: {e}")
        return {}

    # Support both v4 and legacy plain JSON schemas
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
        "ai_file":     f"ai_analysis_v4_{ymd}.html",
        "ai_file_old": f"ai_analysis_{dmy}.html",
        "has_json":    True,
    }


def load_html_only_signals(dest: Path, known_dates: set) -> list:
    """
    For dates that have no source JSON, build minimal history entries
    by scanning ai_analysis_v4_*.html files already in dest folder.
    Parses regime from the HTML <span class='reg'>...</span> tag.
    """
    import re as _re
    results = []
    for f in dest.glob("ai_analysis_v4_*.html"):
        # Extract YYYY_MM_DD from filename
        m = _re.search(r'ai_analysis_v4_(\d{4})_(\d{2})_(\d{2})\.html', f.name)
        if not m:
            continue
        date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        if date_str in known_dates:
            continue   # already loaded from JSON
        try:
            html_text = f.read_text(encoding="utf-8", errors="ignore")
            # Parse regime from <span class='reg'>BEAR</span>
            rm = _re.search(r"class=['\"]reg['\"][^>]*>([A-Z]+)<", html_text)
            regime = rm.group(1) if rm else "NEUTRAL"
            # Parse strength from "Strength N/10"
            sm = _re.search(r"Strength (\d+)/10", html_text)
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
            "ai_file":   f"ai_analysis_v4_{ymd}.html",
            "ai_file_old": f"ai_analysis_{dmy}.html",
            "has_json":  False,
        })
        print(f"  HTML-only: {date_str} → {regime} {strength}/10")

    return sorted(results, key=lambda x: x["date_raw"], reverse=True)


def copy_screener_files(src_date_dir: Path):
    for f in SCREENER_FILES:
        src = src_date_dir / f
        if src.exists():
            shutil.copy(src, DEST_FOLDER / f)
            print(f"  Copied: {f}")
        else:
            print(f"  Missing: {f}")

    # OI files live in NIFTYOPA/stockscreener/advanced  — skip if not found
    adv = Path(r"E:\stockscreener\advanced")
    for f in OI_FILES:
        src = adv / f
        if src.exists():
            shutil.copy(src, DEST_FOLDER / f)
            print(f"  Copied OI: {f}")

    # Copy v4 HTML reports and rename to date-stamped names for GitHub Pages
    for d in SOURCE_BASE.iterdir():
        if not d.is_dir():
            continue

        # Primary: ai_analysis_v4.html  →  ai_analysis_v4_YYYY_MM_DD.html
        v4h = d / "ai_analysis_v4.html"
        if v4h.exists():
            dst_name = f"ai_analysis_v4_{d.name.replace('-', '_')}.html"
            shutil.copy(v4h, DEST_FOLDER / dst_name)
            print(f"  Copied report: {dst_name}")

        # Legacy: ai_analysis.html  →  ai_analysis_YYYY_MM_DD.html (keep for old links)
        legacy = d / "ai_analysis.html"
        if legacy.exists():
            dst_name = f"ai_analysis_{d.name.replace('-', '_')}.html"
            dst = DEST_FOLDER / dst_name
            if not dst.exists():
                shutil.copy(legacy, dst)


# ── REGIME COLORS ─────────────────────────────────────────────────────────────

def regime_colors(regime: str) -> tuple:
    """Returns (bg_hex, text_hex, border_hex)"""
    r = regime.upper()
    if r in ("BULL", "BULLISH"):
        return "#0d3d1e", "#4cff8f", "#1a6b35"
    if r in ("BEAR", "BEARISH"):
        return "#3d0d0d", "#ff5e5e", "#6b1a1a"
    if r == "TRANSITION":
        return "#0d1a3d", "#79c0ff", "#1a3d6b"
    return "#2a2300", "#fde68a", "#4a3f00"   # NEUTRAL


def strength_color(s: int) -> str:
    if s >= 7: return "#4cff8f"
    if s >= 4: return "#fde68a"
    return "#ff5e5e"


def cap_color(c: str) -> str:
    c = c.upper()
    if c == "HIGH":       return "#4cff8f"
    if c == "AVOID_ALL":  return "#ff5e5e"
    return "#fde68a"


# ── HTML GENERATOR ────────────────────────────────────────────────────────────

def build_signal_card(sig: dict, is_featured: bool) -> str:
    if not sig:
        return ""
    rbg, rtx, rbd = regime_colors(sig["regime"])
    scol  = strength_color(sig["strength"])
    ccol  = cap_color(sig["cap"])
    vix   = sig.get("vix_zone", "")
    vix_c = "#ff5e5e" if vix in ("HIGH_FEAR", "CRISIS", "ELEVATED") else "#4cff8f" if vix in ("LOW", "NORMAL") else "#fde68a"

    if is_featured:
        return f"""
<div class="featured-signal">
  <div class="fs-header">
    <div class="fs-date">{sig["date_disp"]}</div>
    <div class="fs-regime-pill" style="background:{rbg};color:{rtx};border-color:{rbd}">
      {sig["regime"]}
    </div>
    <div class="fs-metrics">
      <div class="fs-metric">
        <span class="fs-metric-label">STRENGTH</span>
        <span class="fs-metric-val" style="color:{scol}">{sig["strength"]}/10</span>
      </div>
      <div class="fs-metric">
        <span class="fs-metric-label">CONVICTION</span>
        <span class="fs-metric-val" style="color:{ccol}">{sig["cap"]}</span>
      </div>
      <div class="fs-metric">
        <span class="fs-metric-label">VIX ZONE</span>
        <span class="fs-metric-val" style="color:{vix_c}">{vix or "—"}</span>
      </div>
      <div class="fs-metric">
        <span class="fs-metric-label">FII vs CLIENT</span>
        <span class="fs-metric-val" style="color:{'#ff5e5e' if 'SHORT_CLIENT_LONG' in sig.get('fii','') else '#4cff8f' if 'LONG_CLIENT_SHORT' in sig.get('fii','') else '#7d8590'}">{sig.get("fii","—").replace("FII_SHORT_CLIENT_LONG","SHORT ↓").replace("FII_LONG_CLIENT_SHORT","LONG ↑").replace("ALIGNED","ALIGNED")}</span>
      </div>
    </div>
  </div>

  {'<div class="fs-anomalies">' + "".join(f'<div class="anom-tag">&#x26A1; {a}</div>' for a in sig["anomalies"]) + '</div>' if sig["anomalies"] else ""}

  <div class="fs-body">
    <div class="fs-col">
      <div class="fs-section-title">AI Synthesis</div>
      <div class="fs-text">{sig["synthesis"] or "—"}</div>
    </div>
    <div class="fs-col">
      <div class="fs-section-title">Action Plan</div>
      <div class="fs-text">{sig["action"] or "—"}</div>
    </div>
  </div>

  {'<div class="fs-risks">' + "".join(f'<div class="risk-item">! {r}</div>' for r in sig["risks"]) + '</div>' if sig["risks"] else ""}

  <div class="fs-footer">
    <a href="{sig['ai_file']}" class="btn-outline" target="_blank">Full Report →</a>
  </div>
</div>"""
    else:
        # History card
        return f"""
<div class="hist-card" data-regime="{sig['regime'].lower()}">
  <div class="hist-top">
    <span class="hist-date">{sig["date_disp"]}</span>
    <span class="hist-regime" style="background:{rbg};color:{rtx};border:1px solid {rbd}">{sig["regime"]}</span>
  </div>
  <div class="hist-strength">
    <div class="str-bar-wrap"><div class="str-bar" style="width:{sig['strength']*10}%;background:{scol}"></div></div>
    <span style="color:{scol};font-size:11px">{sig['strength']}/10</span>
  </div>
  <div class="hist-snip">{sig["synthesis"][:160] + "…" if len(sig["synthesis"]) > 160 else sig["synthesis"]}</div>
  <div class="hist-links">
    <a href="{sig['ai_file']}" target="_blank">Full Report →</a>
  </div>
</div>"""


def generate_index(featured: dict, history: list, all_ai_files: list) -> str:
    hist_html = "".join(build_signal_card(s, False) for s in history)
    feat_html = build_signal_card(featured, True) if featured else "<p style='color:#7d8590'>No analysis data available yet.</p>"

    # All AI report links
    report_links = "\n".join(
        f'<li><a href="{f}" target="_blank">{f}</a></li>'
        for f in all_ai_files
    )

    # ── Dynamic SEO values from today's signal ──────────────────────────────
    regime   = featured.get("regime",    "NEUTRAL")
    strength = featured.get("strength",  0)
    date_d   = featured.get("date_disp", "")
    vix      = featured.get("vix_zone",  "")
    synth    = featured.get("synthesis", "")
    # Build a crisp, keyword-rich description for Google + social cards
    regime_emoji = {"BULL":"🟢","BEAR":"🔴","NEUTRAL":"🟡","TRANSITION":"🔵"}.get(regime,"⚪")
    og_title  = f"InfoAlpha ONE — {regime_emoji} {regime} | Strength {strength}/10 | {date_d}"
    og_desc   = (
        f"NSE market regime: {regime} (strength {strength}/10, VIX {vix}). "
        f"{synth[:160].rstrip('…')}… "
        f"Daily institutional flow, FII OI, breadth & options positioning intelligence."
    ) if synth else (
        "InfoAlpha ONE — AI-powered NSE market regime engine. "
        "Institutional flow, FII OI, breadth, VIX, and options positioning — every trading day."
    )
    og_url    = "https://infoalpha.in/"
    og_image  = "https://infoalpha.in/banner.png"   # update if you have a dedicated OG image
    site_name = "InfoAlpha ONE"
    keywords  = (
        "NSE market regime, FII OI analysis, India VIX, Nifty options OI, "
        "market breadth, delivery spike screener, institutional flow, "
        "options open interest, BEAR BULL NEUTRAL signal, EOD analysis, "
        "InfoAlpha, infoalpha.in, Sivasankar"
    )

    return f"""<!DOCTYPE html>
<html lang="en" prefix="og: https://ogp.me/ns#">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<!-- ── PRIMARY SEO ── -->
<title>{og_title}</title>
<meta name="description"      content="{og_desc}">
<meta name="keywords"         content="{keywords}">
<meta name="author"           content="Sivasankar S — InfoAlpha ONE">
<meta name="robots"           content="index, follow">
<link rel="canonical"         href="{og_url}">

<!-- ── OPEN GRAPH (Facebook / LinkedIn / WhatsApp / Telegram previews) ── -->
<meta property="og:type"        content="website">
<meta property="og:site_name"   content="{site_name}">
<meta property="og:title"       content="{og_title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:url"         content="{og_url}">
<meta property="og:image"       content="{og_image}">
<meta property="og:image:width"  content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale"      content="en_IN">

<!-- ── TWITTER / X CARD ── -->
<meta name="twitter:card"        content="summary_large_image">
<meta name="twitter:site"        content="@ssankarsiva">
<meta name="twitter:creator"     content="@ssankarsiva">
<meta name="twitter:title"       content="{og_title}">
<meta name="twitter:description" content="{og_desc}">
<meta name="twitter:image"       content="{og_image}">

<!-- ── TELEGRAM link preview uses OG tags above — no extra tag needed ── -->

<!-- ── THEME / PWA ── -->
<meta name="theme-color" content="#080d14">
<meta name="application-name" content="InfoAlpha ONE">

<!-- ── STRUCTURED DATA (Google Rich Results) ── -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "InfoAlpha ONE",
  "url": "{og_url}",
  "description": "AI-powered NSE market regime engine — institutional flow, FII OI, breadth, VIX, and options positioning intelligence.",
  "author": {{
    "@type": "Person",
    "name": "Sivasankar S",
    "url": "https://www.linkedin.com/in/ssivasankar/",
    "sameAs": [
      "https://www.youtube.com/@InfoAlphain",
      "https://x.com/ssankarsiva",
      "https://www.linkedin.com/in/ssivasankar/",
      "https://t.me/volumepricemove"
    ]
  }},
  "potentialAction": {{
    "@type": "ReadAction",
    "target": "{og_url}"
  }}
}}
</script>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700;800&display=swap" rel="stylesheet">
<style>
:root{{
  --bg:#080d14;
  --bg2:#0d1520;
  --surface:#111923;
  --surface2:#172030;
  --border:#1e2d3d;
  --border2:#243547;
  --tx:#d4e4f7;
  --tx2:#8ca8c5;
  --tx3:#4d6a84;
  --accent:#3b9eff;
  --accent2:#1a6fcc;
  --bull:#2ecc71;
  --bear:#e74c3c;
  --neu:#f39c12;
  --mono:'Space Mono',monospace;
  --sans:'Sora',sans-serif;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{
  background:var(--bg);
  color:var(--tx);
  font-family:var(--sans);
  font-size:13px;
  min-height:100vh;
  background-image:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(59,158,255,.08) 0%, transparent 60%);
}}

/* ── NAV ── */
nav{{
  position:sticky;top:0;z-index:100;
  background:rgba(8,13,20,.92);
  backdrop-filter:blur(12px);
  border-bottom:1px solid var(--border);
  padding:0 28px;
  display:flex;align-items:center;justify-content:space-between;
  height:54px;
}}
.nav-brand{{
  display:flex;flex-direction:column;gap:1px;
  text-decoration:none;
}}
.nav-brand-name{{
  font-family:var(--mono);
  font-weight:700;font-size:14px;
  color:var(--accent);
  letter-spacing:.5px;
}}
.nav-brand-sub{{
  font-size:9px;color:var(--tx3);
  letter-spacing:1.5px;text-transform:uppercase;
}}
.nav-links{{
  display:flex;gap:24px;align-items:center;
}}
.nav-links a{{
  color:var(--tx2);text-decoration:none;
  font-size:12px;font-weight:600;
  letter-spacing:.3px;
  transition:color .15s;
}}
.nav-links a:hover{{color:var(--tx)}}
.nav-cta{{
  background:var(--accent);
  color:#000;font-weight:700;
  padding:6px 16px;border-radius:6px;
  font-size:11px;letter-spacing:.5px;
  text-decoration:none;
  transition:background .15s;
}}
.nav-cta:hover{{background:#5aabff;color:#000}}

/* ── HERO ── */
.hero{{
  padding:70px 28px 50px;
  max-width:1100px;margin:0 auto;
  text-align:center;
}}
.hero-tag{{
  display:inline-block;
  background:rgba(59,158,255,.12);
  border:1px solid rgba(59,158,255,.25);
  color:var(--accent);
  font-size:10px;font-weight:700;
  letter-spacing:2px;text-transform:uppercase;
  padding:4px 14px;border-radius:20px;
  margin-bottom:20px;
}}
.hero h1{{
  font-size:clamp(28px,5vw,48px);
  font-weight:800;
  line-height:1.15;
  color:#e8f4ff;
  margin-bottom:16px;
}}
.hero h1 span{{color:var(--accent)}}
.hero-sub{{
  color:var(--tx2);font-size:14px;
  max-width:600px;margin:0 auto 36px;
  line-height:1.7;
  font-weight:300;
}}
.hero-stats{{
  display:flex;gap:0;
  justify-content:center;
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:12px;
  overflow:hidden;
  max-width:680px;margin:0 auto;
}}
.hero-stat{{
  flex:1;padding:18px 12px;
  text-align:center;
  border-right:1px solid var(--border);
}}
.hero-stat:last-child{{border-right:none}}
.hs-val{{
  font-family:var(--mono);
  font-size:20px;font-weight:700;
  color:var(--tx);
}}
.hs-label{{
  font-size:9px;color:var(--tx3);
  letter-spacing:1.5px;text-transform:uppercase;
  margin-top:3px;
}}

/* ── SECTION WRAPPER ── */
.section{{
  max-width:1100px;margin:0 auto;
  padding:40px 28px;
}}
.section-label{{
  font-size:9px;font-weight:700;
  letter-spacing:2.5px;text-transform:uppercase;
  color:var(--tx3);
  margin-bottom:6px;
  display:flex;align-items:center;gap:8px;
}}
.section-label::before{{
  content:"";display:block;
  width:18px;height:1px;
  background:var(--border2);
}}
.section-title{{
  font-size:22px;font-weight:700;
  color:#e8f4ff;margin-bottom:24px;
}}

/* ── FEATURED SIGNAL ── */
.featured-signal{{
  background:var(--surface);
  border:1px solid var(--border2);
  border-radius:14px;
  overflow:hidden;
}}
.fs-header{{
  padding:20px 24px 16px;
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;
  flex-wrap:wrap;gap:16px;
}}
.fs-date{{
  font-family:var(--mono);
  font-size:11px;color:var(--tx2);
  letter-spacing:.5px;
}}
.fs-regime-pill{{
  padding:5px 16px;border-radius:8px;
  font-family:var(--mono);
  font-weight:700;font-size:14px;
  border:1px solid;
  letter-spacing:1px;
}}
.fs-metrics{{
  display:flex;gap:20px;
  margin-left:auto;flex-wrap:wrap;
}}
.fs-metric{{
  display:flex;flex-direction:column;
  align-items:center;gap:2px;
}}
.fs-metric-label{{
  font-size:8px;letter-spacing:1.5px;
  color:var(--tx3);text-transform:uppercase;
}}
.fs-metric-val{{
  font-family:var(--mono);
  font-size:13px;font-weight:700;
  color:var(--tx2);
}}
.fs-anomalies{{
  padding:12px 24px;
  background:rgba(243,156,18,.04);
  border-bottom:1px solid var(--border);
  display:flex;flex-wrap:wrap;gap:8px;
}}
.anom-tag{{
  background:rgba(243,156,18,.08);
  border:1px solid rgba(243,156,18,.2);
  color:#f39c12;
  font-size:10px;padding:3px 10px;
  border-radius:5px;line-height:1.5;
}}
.fs-body{{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:0;
}}
@media(max-width:700px){{.fs-body{{grid-template-columns:1fr}}}}
.fs-col{{
  padding:20px 24px;
  border-right:1px solid var(--border);
}}
.fs-col:last-child{{border-right:none}}
.fs-section-title{{
  font-size:9px;font-weight:700;
  letter-spacing:2px;text-transform:uppercase;
  color:var(--tx3);margin-bottom:10px;
}}
.fs-text{{
  color:var(--tx2);
  font-size:12px;line-height:1.8;
}}
.fs-risks{{
  padding:12px 24px;
  background:rgba(231,76,60,.03);
  border-top:1px solid var(--border);
  display:flex;flex-wrap:wrap;gap:8px;
}}
.risk-item{{
  background:rgba(231,76,60,.07);
  border:1px solid rgba(231,76,60,.15);
  color:#e74c3c;
  font-size:10px;padding:3px 10px;
  border-radius:5px;line-height:1.5;
}}
.fs-footer{{
  padding:14px 24px;
  border-top:1px solid var(--border);
  display:flex;gap:12px;
}}
.btn-outline{{
  border:1px solid var(--border2);
  color:var(--accent);
  padding:6px 16px;border-radius:6px;
  font-size:11px;font-weight:600;
  text-decoration:none;
  letter-spacing:.3px;
  transition:all .15s;
}}
.btn-outline:hover{{
  background:rgba(59,158,255,.1);
  border-color:var(--accent);
}}

/* ── HISTORY CARDS ── */
.hist-grid{{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(220px,1fr));
  gap:12px;
}}
.hist-card{{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:10px;
  padding:16px;
  transition:border-color .15s, transform .15s;
}}
.hist-card:hover{{
  border-color:var(--border2);
  transform:translateY(-2px);
}}
.hist-top{{
  display:flex;align-items:center;
  justify-content:space-between;margin-bottom:10px;
}}
.hist-date{{
  font-family:var(--mono);font-size:10px;color:var(--tx3);
}}
.hist-regime{{
  padding:2px 8px;border-radius:5px;
  font-family:var(--mono);font-size:10px;font-weight:700;
  letter-spacing:.5px;
}}
.str-bar-wrap{{
  height:3px;background:var(--border);border-radius:2px;
  flex:1;
}}
.str-bar{{
  height:3px;border-radius:2px;transition:width .4s;
}}
.hist-strength{{
  display:flex;align-items:center;gap:8px;margin-bottom:10px;
}}
.hist-snip{{
  color:var(--tx3);font-size:11px;line-height:1.65;
  margin-bottom:10px;
}}
.hist-links{{
  display:flex;gap:10px;
}}
.hist-links a{{
  color:var(--accent);font-size:10px;
  text-decoration:none;font-weight:600;
}}
.hist-links a:hover{{text-decoration:underline}}

/* ── SCREENER GRID ── */
.tool-grid{{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(200px,1fr));
  gap:10px;
}}
.tool-card{{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:10px;
  padding:16px 18px;
  text-decoration:none;
  transition:border-color .15s,background .15s;
  display:block;
}}
.tool-card:hover{{
  border-color:var(--accent2);
  background:var(--surface2);
}}
.tool-icon{{
  font-size:20px;margin-bottom:10px;
}}
.tool-name{{
  font-weight:700;font-size:13px;
  color:#e8f4ff;margin-bottom:4px;
}}
.tool-desc{{
  color:var(--tx3);font-size:11px;line-height:1.5;
}}
.tool-badge{{
  display:inline-block;
  margin-top:8px;
  background:rgba(59,158,255,.1);
  color:var(--accent);
  font-size:9px;padding:2px 7px;
  border-radius:4px;letter-spacing:.5px;
  font-weight:600;
}}

/* ── HOW IT WORKS ── */
.how-grid{{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(220px,1fr));
  gap:14px;
}}
.how-step{{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:10px;
  padding:20px 18px;
  position:relative;
  overflow:hidden;
}}
.how-step::before{{
  content:attr(data-num);
  position:absolute;top:-10px;right:14px;
  font-family:var(--mono);font-size:72px;font-weight:700;
  color:rgba(59,158,255,.04);line-height:1;
}}
.how-step-title{{
  font-weight:700;font-size:13px;
  color:#e8f4ff;margin-bottom:6px;
}}
.how-step-desc{{
  color:var(--tx3);font-size:11px;line-height:1.65;
}}

/* ── AI REPORTS LIST ── */
.reports-list{{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:10px;
  overflow:hidden;
}}
.reports-list li{{
  list-style:none;
  border-bottom:1px solid var(--border);
  padding:10px 18px;
  display:flex;align-items:center;gap:8px;
}}
.reports-list li:last-child{{border-bottom:none}}
.reports-list li::before{{
  content:"▸";color:var(--accent);font-size:11px;
}}
.reports-list li a{{
  color:var(--tx2);text-decoration:none;
  font-family:var(--mono);font-size:11px;
  transition:color .15s;
}}
.reports-list li a:hover{{color:var(--accent)}}

/* ── ABOUT / SOCIAL ── */
.about-grid{{
  display:grid;
  grid-template-columns:2fr 1fr;
  gap:20px;
}}
@media(max-width:700px){{.about-grid{{grid-template-columns:1fr}}}}
.about-card{{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:12px;
  padding:24px;
}}
.social-links{{
  display:flex;flex-direction:column;gap:10px;margin-top:16px;
}}
.social-link{{
  display:flex;align-items:center;gap:10px;
  text-decoration:none;
  background:var(--surface2);
  border:1px solid var(--border);
  border-radius:8px;padding:9px 14px;
  transition:border-color .15s;
}}
.social-link:hover{{border-color:var(--border2)}}
.social-link-icon{{font-size:16px;}}
.social-link-text{{
  color:var(--tx2);font-size:11px;font-weight:600;
}}

/* ── SUPPORT ── */
.support-box{{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:12px;
  padding:28px;
  margin-top:20px;
}}
.upi-block{{
  background:rgba(59,158,255,.06);
  border:1px solid rgba(59,158,255,.15);
  border-radius:8px;
  padding:16px 20px;
  margin-top:14px;
  font-family:var(--mono);
  font-size:13px;color:var(--accent);
}}

/* ── CTA BANNER ── */
.cta-banner{{
  background:linear-gradient(135deg,#0a1f3d 0%,#0d2848 100%);
  border:1px solid rgba(59,158,255,.2);
  border-radius:14px;
  padding:42px 32px;
  text-align:center;
  margin:40px 28px;
  max-width:1100px;
  margin-left:auto;margin-right:auto;
}}
.cta-title{{
  font-size:22px;font-weight:800;
  color:#e8f4ff;margin-bottom:10px;
}}
.cta-sub{{
  color:var(--tx2);font-size:13px;margin-bottom:22px;
}}
.cta-btn{{
  background:var(--accent);color:#000;
  padding:12px 32px;border-radius:8px;
  font-weight:700;font-size:13px;
  text-decoration:none;
  display:inline-block;
  transition:background .15s;
}}
.cta-btn:hover{{background:#5aabff;color:#000}}

/* ── FOOTER ── */
footer{{
  border-top:1px solid var(--border);
  padding:20px 28px;
  text-align:center;
  color:var(--tx3);
  font-size:11px;
}}
footer a{{color:var(--tx3);text-decoration:none;}}
footer a:hover{{color:var(--tx2)}}

/* ── DIVIDER ── */
.divider{{
  height:1px;background:var(--border);
  max-width:1100px;margin:0 auto;
}}

/* ── RESPONSIVE ── */
@media(max-width:600px){{
  .nav-links{{display:none}}
  .hero{{padding:48px 16px 36px}}
  .section{{padding:28px 16px}}
}}
</style>
</head>

<body>

<!-- NAV -->
<nav>
  <a href="#" class="nav-brand">
    <span class="nav-brand-name">InfoAlpha ONE</span>
    <span class="nav-brand-sub">Smart Signals · Better Trades</span>
  </a>
  <div class="nav-links">
    <a href="#signals">Signals</a>
    <a href="#oi">OI Charts</a>
    <a href="#reports">AI Reports</a>
    <a href="#about">About</a>
    <a href="https://t.me/volumepricemove" target="_blank" class="nav-cta" style="background:#229ED9">✈ Telegram</a>
    <a href="https://www.youtube.com/@InfoAlphain" target="_blank" class="nav-cta">▶ YouTube</a>
  </div>
</nav>

<!-- HERO -->
<div class="hero">
  <div class="hero-tag">NSE India · Institutional Intelligence</div>
  <h1>Institutional Flow &amp; Options<br><span>Positioning Intelligence</span></h1>
  <p class="hero-sub">
    A data-driven market regime engine that tells you when to trade,
    what side to favor, and when to stay out — powered by FII flow,
    OI structure, breadth, and VIX regime analysis.
  </p>
  <div class="hero-stats">
    <div class="hero-stat">
      <div class="hs-val">6+</div>
      <div class="hs-label">Screeners</div>
    </div>
    <div class="hero-stat">
      <div class="hs-val">4</div>
      <div class="hs-label">OI Expiries</div>
    </div>
    <div class="hero-stat">
      <div class="hs-val">AI</div>
      <div class="hs-label">Regime Engine</div>
    </div>
    <div class="hero-stat">
      <div class="hs-val">EOD</div>
      <div class="hs-label">Daily Update</div>
    </div>
  </div>
</div>

<div class="divider"></div>

<!-- FEATURED SIGNAL -->
<div class="section">
  <div class="section-label">Latest Analysis</div>
  <div class="section-title">Today's Market Regime Signal</div>
  {feat_html}
</div>

<!-- HISTORY -->
{'<div class="section"><div class="section-label">Recent History</div><div class="section-title">Last ' + str(len(history)) + ' Trading Days</div><div class="hist-grid">' + hist_html + '</div></div>' if history else ""}

<div class="divider"></div>

<!-- SCREENERS -->
<div class="section" id="signals">
  <div class="section-label">Market Screeners</div>
  <div class="section-title">Signal Dashboards</div>
  <div class="tool-grid">
    <a href="breadth.html" class="tool-card" target="_blank">
      <div class="tool-icon">📊</div>
      <div class="tool-name">Breadth Analysis</div>
      <div class="tool-desc">Advances/declines, EMA% and market participation across N50/N200/N500</div>
      <span class="tool-badge">60-day history</span>
    </a>
    <a href="delivery_spike.html" class="tool-card" target="_blank">
      <div class="tool-icon">📦</div>
      <div class="tool-name">Delivery Spike</div>
      <div class="tool-desc">Institutional accumulation detection — 2× delivery spikes filtered for HFT noise</div>
      <span class="tool-badge">smart money</span>
    </a>
    <a href="highlow.html" class="tool-card" target="_blank">
      <div class="tool-icon">📈</div>
      <div class="tool-name">High / Low Resilience</div>
      <div class="tool-desc">Position within 5D–200D range. Fully resilient = above 80% across all periods</div>
      <span class="tool-badge">5 periods</span>
    </a>
    <a href="momentum_ma.html" class="tool-card" target="_blank">
      <div class="tool-icon">🚀</div>
      <div class="tool-name">Momentum / MA</div>
      <div class="tool-desc">MA5/20/50/200 scores, ATR%, RSI, and relative strength vs NIFTYBEES</div>
      <span class="tool-badge">RS leaders tab</span>
    </a>
    <a href="recurring_entry.html" class="tool-card" target="_blank">
      <div class="tool-icon">🔁</div>
      <div class="tool-name">Recurring Entry</div>
      <div class="tool-desc">Stocks qualifying on 4+/6 score repeatedly — relative delivery vs own 60D avg</div>
      <span class="tool-badge">40-day scan</span>
    </a>
    <a href="sector_rotation.html" class="tool-card" target="_blank">
      <div class="tool-icon">⚡</div>
      <div class="tool-name">Sector Rotation</div>
      <div class="tool-desc">Smart money phase (Accumulation / Markup / Distribution) by sector and industry</div>
      <span class="tool-badge">SM signals</span>
    </a>
  </div>
</div>

<div class="divider"></div>

<!-- OI CHARTS -->
<div class="section" id="oi">
  <div class="section-label">Derivatives Intelligence</div>
  <div class="section-title">Options OI Structure</div>
  <div class="tool-grid">
    <a href="options_oi_chart.html" class="tool-card" target="_blank">
      <div class="tool-icon">🎯</div>
      <div class="tool-name">Weekly OI</div>
      <div class="tool-desc">CE vs PE open interest — current week expiry</div>
    </a>
    <a href="options_oi_chartnxtweek.html" class="tool-card" target="_blank">
      <div class="tool-icon">🎯</div>
      <div class="tool-name">Next Week OI</div>
      <div class="tool-desc">Next expiry positioning analysis</div>
    </a>
    <a href="options_oi_chartmonth.html" class="tool-card" target="_blank">
      <div class="tool-icon">📅</div>
      <div class="tool-name">Monthly OI</div>
      <div class="tool-desc">Monthly expiry option structure and max pain</div>
    </a>
    <a href="options_oi_chartnxtmonth.html" class="tool-card" target="_blank">
      <div class="tool-icon">📅</div>
      <div class="tool-name">Next Month OI</div>
      <div class="tool-desc">Next month institutional positioning data</div>
    </a>
    <a href="csvweek.html" class="tool-card" target="_blank">
      <div class="tool-icon">🔍</div>
      <div class="tool-name">OI Filter — Weekly</div>
      <div class="tool-desc">Filtered OI table with building/unwinding tags</div>
    </a>
    <a href="csvmonth.html" class="tool-card" target="_blank">
      <div class="tool-icon">🔍</div>
      <div class="tool-name">OI Filter — Monthly</div>
      <div class="tool-desc">Monthly OI table with change analysis</div>
    </a>
    <a href="Dashboard.html" class="tool-card" target="_blank">
      <div class="tool-icon">📉</div>
      <div class="tool-name">OI Changes — Weekly</div>
      <div class="tool-desc">4-day comparison of weekly OI movement</div>
    </a>
    <a href="DashboardMonth.html" class="tool-card" target="_blank">
      <div class="tool-icon">📉</div>
      <div class="tool-name">OI Changes — Monthly</div>
      <div class="tool-desc">4-day comparison of monthly OI movement</div>
    </a>
  </div>
</div>

<div class="divider"></div>

<!-- AI REPORTS ARCHIVE -->
<div class="section" id="reports">
  <div class="section-label">Archive</div>
  <div class="section-title">All AI Daily Reports</div>
  <ul class="reports-list">
    {report_links}
  </ul>
</div>

<div class="divider"></div>

<!-- HOW IT WORKS -->
<div class="section">
  <div class="section-label">Methodology</div>
  <div class="section-title">How the System Works</div>
  <div class="how-grid">
    <div class="how-step" data-num="01">
      <div class="how-step-title">NSE EOD Data Collection</div>
      <div class="how-step-desc">Daily bhav copy, FO participant OI (fao_participant_oi), FII cash stats, and VIX history downloaded from NSE archives.</div>
    </div>
    <div class="how-step" data-num="02">
      <div class="how-step-title">Quant Feature Extraction</div>
      <div class="how-step-desc">Breadth, delivery spikes, momentum MA, high/low resilience, sector rotation, and options OI structure computed per symbol.</div>
    </div>
    <div class="how-step" data-num="03">
      <div class="how-step-title">3-Day Footprint Analysis</div>
      <div class="how-step-desc">AI receives a 3-day footprint — full snapshot today, OI and FII deltas for yesterday and 2 days ago — to distinguish trend from noise.</div>
    </div>
    <div class="how-step" data-num="04">
      <div class="how-step-title">Regime Engine Output</div>
      <div class="how-step-desc">Python labels compute regime (BULL/BEAR/NEUTRAL/TRANSITION), VIX zone, conviction cap, and FII streak. Claude synthesizes the narrative.</div>
    </div>
    <div class="how-step" data-num="05">
      <div class="how-step-title">Static Site Publish</div>
      <div class="how-step-desc">All HTML reports and screeners are copied to GitHub Pages and served from infoalpha.in — no server, no login, no tracking.</div>
    </div>
  </div>
</div>

<div class="divider"></div>

<!-- ABOUT -->
<div class="section" id="about">
  <div class="section-label">About</div>
  <div class="section-title">Who Builds This</div>
  <div class="about-grid">
    <div class="about-card">
      <p style="color:var(--tx2);font-size:13px;line-height:1.9;margin-bottom:14px">
        InfoAlpha ONE is an independent market intelligence project built by
        <strong style="color:var(--tx)">Sivasankar S</strong> — a developer and quant analyst
        combining institutional flow data, options positioning, and AI interpretation
        to give retail traders an institutional-grade edge.
      </p>
      <p style="color:var(--tx2);font-size:13px;line-height:1.9;margin-bottom:14px">
        The system runs every trading day after NSE EOD — processing FII participant OI,
        breadth, delivery data, and 4-expiry options structure through a 3-day footprint
        model before feeding it to Claude for synthesis.
      </p>
      <p style="color:var(--tx3);font-size:11px;line-height:1.7">
        Services: Website Development · Drupal · Market Research · Quant Analysis · AI & Data Training
      </p>
      <div style="display:flex;gap:10px;margin-top:14px;flex-wrap:wrap">
        <a href="https://wa.me/919884346789" target="_blank"
           style="display:flex;align-items:center;gap:7px;background:#25D366;color:#000;
                  font-weight:700;font-size:12px;padding:8px 16px;border-radius:8px;
                  text-decoration:none;letter-spacing:.3px">
          💬 WhatsApp Me
        </a>
        <a href="https://t.me/volumepricemove" target="_blank"
           style="display:flex;align-items:center;gap:7px;background:#229ED9;color:#fff;
                  font-weight:700;font-size:12px;padding:8px 16px;border-radius:8px;
                  text-decoration:none;letter-spacing:.3px">
          ✈ Telegram Channel
        </a>
      </div>

      <!-- UPI -->
      <div class="support-box" style="margin-top:20px;padding:20px">
        <div style="color:var(--tx2);font-size:12px;line-height:1.7;margin-bottom:10px">
          If you find these signals useful, consider supporting the infrastructure and research:
        </div>
        <div class="upi-block">
          💸 UPI: <strong>websivasankar@okicici</strong>
        </div>
      </div>
    </div>

    <div>
      <div class="about-card" style="margin-bottom:12px">
        <div style="color:var(--tx3);font-size:9px;letter-spacing:2px;text-transform:uppercase;margin-bottom:14px">Connect</div>
        <div class="social-links">
          <a href="https://t.me/volumepricemove" class="social-link" target="_blank">
            <span class="social-link-icon">✈</span>
            <span class="social-link-text">Telegram @volumepricemove</span>
          </a>
          <a href="https://wa.me/919884346789" class="social-link" target="_blank">
            <span class="social-link-icon">💬</span>
            <span class="social-link-text">WhatsApp +91 98843 46789</span>
          </a>
          <a href="https://www.youtube.com/@InfoAlphain" class="social-link" target="_blank">
            <span class="social-link-icon">▶</span>
            <span class="social-link-text">YouTube @InfoAlphain</span>
          </a>
          <a href="https://www.linkedin.com/in/ssivasankar/" class="social-link" target="_blank">
            <span class="social-link-icon">in</span>
            <span class="social-link-text">LinkedIn · Sivasankar S</span>
          </a>
          <a href="https://x.com/ssankarsiva" class="social-link" target="_blank">
            <span class="social-link-icon">𝕏</span>
            <span class="social-link-text">@ssankarsiva</span>
          </a>
          <a href="https://www.drupal.org/u/ssankarsiva" class="social-link" target="_blank">
            <span class="social-link-icon">🔵</span>
            <span class="social-link-text">Drupal · ssankarsiva</span>
          </a>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- CTA BANNER -->
<div class="cta-banner">
  <div class="cta-title">Get Real-Time Signals &amp; Alerts</div>
  <div class="cta-sub">Subscribe on YouTube for live market commentary and EOD regime updates</div>
  <a href="https://www.youtube.com/@InfoAlphain" class="cta-btn" target="_blank">▶ Subscribe on YouTube</a>
</div>

<!-- FOOTER -->
<footer>
  <p>InfoAlpha ONE — AI EOD NSE Market Reports &nbsp;·&nbsp; Educational Purpose Only &nbsp;·&nbsp; Not SEBI-registered Investment Advice</p>
  <p style="margin-top:6px">
    <a href="https://t.me/volumepricemove" target="_blank">Telegram</a> &nbsp;·&nbsp;
    <a href="https://wa.me/919884346789" target="_blank">WhatsApp</a> &nbsp;·&nbsp;
    <a href="https://www.youtube.com/@InfoAlphain" target="_blank">YouTube</a> &nbsp;·&nbsp;
    <a href="https://www.linkedin.com/in/ssivasankar/" target="_blank">LinkedIn</a> &nbsp;·&nbsp;
    <a href="https://x.com/ssankarsiva" target="_blank">X</a> &nbsp;·&nbsp;
    <a href="https://infoalpha.in" target="_blank">infoalpha.in</a>
  </p>
</footer>

</body>
</html>"""


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", type=str, help="Source date for screener files (YYYY-MM-DD)")
    ap.add_argument("--days", type=int, default=5, help="Days of AI analysis to show (default 5)")
    args = ap.parse_args()

    DEST_FOLDER.mkdir(parents=True, exist_ok=True)

    # 1. Copy screener + OI files from latest (or specified) date
    if args.date:
        src_date = SOURCE_BASE / args.date
    else:
        # Use the most recent date folder
        dirs = sorted([d for d in SOURCE_BASE.iterdir() if d.is_dir()],
                      key=lambda d: d.name)
        src_date = dirs[-1] if dirs else None

    if src_date and src_date.exists():
        print(f"Copying screener files from: {src_date.name}")
        copy_screener_files(src_date)
    else:
        print("  [warn] No source date folder found — skipping screener copy")

    # 2. Load last N AI analysis JSONs
    day_pairs = find_date_dirs(SOURCE_BASE, args.days)
    if not day_pairs:
        print("  [warn] No ai_analysis_v4.json files found in output dir")
    signals = [load_signal(ds, jp) for ds, jp in day_pairs]
    signals = [s for s in signals if s]

    # 2b. Supplement with HTML-only entries from gitpublic for dates missing JSON
    known = {s["date_raw"] for s in signals}
    html_only = load_html_only_signals(DEST_FOLDER, known)
    # Merge: JSON signals first, then HTML-only, re-sort newest first, keep top N*2
    all_signals = sorted(signals + html_only, key=lambda x: x["date_raw"], reverse=True)
    featured  = all_signals[0] if all_signals else {}
    # For history show up to args.days-1 entries after featured
    history_signals = all_signals[1:args.days]
    print(f"Loaded {len(signals)} JSON signal(s) + {len(html_only)} HTML-only signal(s)")

    # 3. Collect all AI HTML files for the archive list, sorted by actual date newest first
    def _ai_file_date(fname: str) -> str:
        """
        Extract a sortable YYYY-MM-DD key from either filename format:
          ai_analysis_2026_03_19.html  →  2026-03-19
          ai_analysis_19_03_2026.html  →  2026-03-19
          ai_analysis_v5_2026_03_19.html → 2026-03-19
        Returns "0000-00-00" for unrecognised names so they sort last.
        """
        import re as _re
        # strip prefix and extension, work on the digit parts
        stem = fname.replace("ai_analysis_v5_", "").replace("ai_analysis_", "").replace(".html", "")
        parts = stem.split("_")
        parts = [p for p in parts if p.isdigit()]
        if len(parts) < 3:
            return "0000-00-00"
        a, b, c = parts[0], parts[1], parts[2]
        # YYYY_MM_DD  → a is 4-digit year
        if len(a) == 4:
            return f"{a}-{b.zfill(2)}-{c.zfill(2)}"
        # DD_MM_YYYY  → c is 4-digit year
        if len(c) == 4:
            return f"{c}-{b.zfill(2)}-{a.zfill(2)}"
        return "0000-00-00"

    # Deduplicate: prefer v5 file over plain file for the same date
    ai_candidates = [f.name for f in DEST_FOLDER.glob("ai_analysis*.html")]
    # Build date → preferred filename map  (prefer v4 file over plain legacy file)
    _date_map: dict = {}
    for fname in ai_candidates:
        key = _ai_file_date(fname)
        if key == "0000-00-00":
            continue
        existing = _date_map.get(key)
        if existing is None or ("v4" in fname and "v4" not in existing):
            _date_map[key] = fname
        # if both are v4 or both are plain, keep either (same date = same content)
    all_ai = [v for _, v in sorted(_date_map.items(), reverse=True)]

    # 4. Generate and write index.html
    html = generate_index(featured, history_signals, all_ai)
    out  = DEST_FOLDER / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"✅  index.html written → {out}")
    print(f"    Featured: {featured.get('date_raw','none')} {featured.get('regime','')}")
    print(f"    History:  {[s['date_raw'] for s in history_signals]}")


if __name__ == "__main__":
    main()