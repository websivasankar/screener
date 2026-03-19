import os
import shutil

# ==============================
# PATHS
# ==============================

source_folder = r"D:\PositionalSystem\screener\output\2026-03-19"
dest_folder = r"D:\PositionalSystem\screener\gitpublic"

# analysis pages
analysis_pages = [
    "breadth.html",
    "delivery_spike.html",
    "highlow.html",
    "momentum_ma.html",
    "recurring_entry.html",
    "sector_rotation.html"
]

# ==============================
# COPY FILES
# ==============================

for file in analysis_pages:

    src = os.path.join(source_folder, file)
    dst = os.path.join(dest_folder, file)

    if os.path.exists(src):
        shutil.copy(src, dst)
        print("Copied:", file)
    else:
        print("Missing:", file)


# ==============================
# GET AI REPORT FILES
# ==============================

files = [
    f for f in os.listdir(dest_folder)
    if f.startswith("ai_analysis") and f.endswith(".html")
]

files.sort(reverse=True)

report_links = ""

for f in files:
    
    report_links += f'<li><a href="{f}" target="_blank">{f}</a></li>\n'



# ==============================
# GENERATE INDEX.HTML
# ==============================

html = f"""
<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<title>AI EOD NSE Market Reports</title>

<style>

body {{
font-family: Arial;
margin:0;
background:#f5f7fb;
}}

header {{
  background-image: url("banner.png");
  height: 250px;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  color:white;
  padding:25px;
  text-align:center;
}}

nav {{
background:#0055aa;
padding:12px;
}}

nav a {{
color:white;
margin-right:20px;
text-decoration:none;
font-weight:bold;
}}

nav a:hover {{
text-decoration:underline;
}}

.container {{
max-width:1100px;
margin:auto;
padding:20px;
}}

.section-title {{
color:#003366;
margin-top:40px;
}}

.grid {{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
gap:20px;
margin-top:20px;
}}

.card {{
background:white;
padding:20px;
border-radius:8px;
box-shadow:0 3px 8px rgba(0,0,0,0.1);
}}

.card h3 {{
margin-top:0;
}}

.card a {{
color:#0055aa;
font-weight:bold;
text-decoration:none;
}}

footer {{
margin-top:40px;
background:#eaeaea;
padding:15px;
text-align:center;
}}

/* ==========================
   SUPPORT SECTION STYLE
========================== */

.support-box{{
background:#ffffff;
padding:25px;
margin-top:40px;
border-radius:10px;
box-shadow:0 3px 8px rgba(0,0,0,0.1);
}}

.support-highlight{{
background:#f0f6ff;
padding:15px;
border-left:5px solid #0055aa;
margin-top:15px;
}}

.contact{{
margin-top:15px;
font-weight:bold;
}}

</style>

</head>


<body class="container">

<header>
</header>


<nav>

<a href="#">Home</a>
<a href="#signals">Market Signals</a>
<a href="#oi">OI Charts</a>
<a href="#reports">AI Reports</a>
<a href="#how">How It Works</a>

</nav>


<div class="container">

<h2 id="signals" class="section-title">Market Signal Dashboards</h2>

<div class="grid">

<div class="card">
<h3>Breadth Analysis</h3>
<p>Market participation and strength analysis.</p>
<a href="breadth.html" target="_blank">Open →</a>
</div>

<div class="card">
<h3>Delivery Spike</h3>
<p>Institutional accumulation detection.</p>
<a href="delivery_spike.html" target="_blank">Open →</a>
</div>

<div class="card">
<h3>High vs Low</h3>
<p>Stocks hitting new highs and lows.</p>
<a href="highlow.html" target="_blank">Open →</a>
</div>

<div class="card">
<h3>Momentum MA</h3>
<p>Moving average trend momentum signals.</p>
<a href="momentum_ma.html" target="_blank">Open →</a>
</div>

<div class="card">
<h3>Recurring Entry</h3>
<p>Repeated institutional entry patterns.</p>
<a href="recurring_entry.html" target="_blank">Open →</a>
</div>

<div class="card">
<h3>Sector Rotation</h3>
<p>Capital rotation across sectors.</p>
<a href="sector_rotation.html" target="_blank">Open →</a>
</div>

</div>

<h2 id="oi" class="section-title">Options OI Charts</h2>

<div class="grid">

<div class="card">
<h3>Weekly OI Chart</h3>
<p>Nifty option open interest structure.</p>
<a href="options_oi_chart.html" target="_blank">Open →</a>
</div>

<div class="card">
<h3>Next Week OI Chart</h3>
<p>Next expiry positioning analysis.</p>
<a href="options_oi_chartnxtweek.html" target="_blank">Open →</a>
</div>

<div class="card">
<h3>Monthly OI Chart</h3>
<p>Monthly expiry option structure.</p>
<a href="options_oi_chartmonth.html" target="_blank">Open →</a>
</div>

<div class="card">
<h3>Next Month OI Chart</h3>
<p>Next month positioning data.</p>
<a href="options_oi_chartnxtmonth.html" target="_blank">Open →</a>
</div>

<div class="card">
<h3>OI Filter</h3>
<p>Weekly</p>
<a href="csvweek.html" target="_blank">Open →</a>
</div>

<div class="card">
<h3>OI Filter</h3>
<p>Monthly</p>
<a href="csvmonth.html" target="_blank">Open →</a>
</div>

<div class="card">
<h3>Option Change</h3>
<p>Weekly OI Changes.</p>
<a href="Dashboard.html" target="_blank">Open →</a>
</div>

<div class="card">
<h3>Option Change</h3>
<p>Monthly OI Changes.</p>
<a href="DashboardMonth.html" target="_blank">Open →</a>
</div>


</div>





<h2 id="reports" class="section-title">AI Daily Market Reports</h2>

<ul>

{report_links}

</ul>


<h2 id="how" class="section-title">How the System Works</h2>

<ol>
<li>End-of-day NSE market data collected.</li>
<li>Quant features derived (breadth, momentum, delivery, OI).</li>
<li>AI interprets the market regime.</li>
<li>Automated HTML report generated and published.</li>
</ol>


<h2 class="section-title">Support This Research</h2>

<div class="support-box">

<p>
This AI market intelligence project is independently developed and maintained.
If you find these insights useful for trading or research, consider supporting
this work through donations.
</p>

<div class="support-highlight">

<b>UPI Donation</b><br><br>

UPI ID: <b>websivasankar@okicici</b>

<p>Support helps maintain:</p>

<ul>
<li>Market data infrastructure</li>
<li>AI research and automation</li>
<li>Quant analytics development</li>
</ul>

</div>

<h3>Services Offered</h3>

<ul>
<li>Website Development (Static / Dynamic)</li>
<li>Drupal Development</li>
<li>Market Research & Quant Analysis</li>
<li>AI & Data Analysis Training</li>
</ul>

<div class="contact">

Contact / WhatsApp: (91)9884346789

</div>

</div>

</div>


<footer>

AI EOD NSE Market Reports – Educational Purpose Only

</footer>

</body>
</html>
"""


# write file
with open(os.path.join(dest_folder, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

print("index.html created successfully")