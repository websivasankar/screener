import os
import shutil
import subprocess

# ==============================
# PATHS
# ==============================

base_output = r"D:\PositionalSystem\screener\output"
git_folder = r"D:\PositionalSystem\screener\gitpublic"

# analysis pages to publish
analysis_pages = [
    "breadth.html",
    "delivery_spike.html",
    "highlow.html",
    "momentum_ma.html",
    "recurring_entry.html",
    "sector_rotation.html"
]

# ==============================
# FIND LATEST OUTPUT FOLDER
# ==============================

folders = sorted(os.listdir(base_output))
latest_folder = folders[-1]

source_folder = os.path.join(base_output, latest_folder)

print("\n==============================")
print("AI RESEARCH PUBLISH PIPELINE")
print("==============================")
print("Source Folder :", source_folder)
print("Destination   :", git_folder)
print("------------------------------")

# ==============================
# COPY FILES
# ==============================

copied = 0

for file in analysis_pages:

    src = os.path.join(source_folder, file)
    dst = os.path.join(git_folder, file)

    if os.path.exists(src):

        shutil.copy(src, dst)
        copied += 1
        print(f"✔ Copied: {file}")

    else:
        print(f"✖ Missing: {file}")

print("------------------------------")
print(f"SUCCESS: {copied} analysis files copied")

# ==============================
# FIND AI REPORTS
# ==============================

reports = [
    f for f in os.listdir(git_folder)
    if f.startswith("ai_analysis") and f.endswith(".html")
]

reports.sort(reverse=True)

report_links = ""

for r in reports:

    name = r.replace("ai_analysis_", "").replace(".html", "")
    report_links += f'<li><a href="{r}" target="_blank">{name}</a></li>\n'

latest_report = reports[0] if reports else ""

# ==============================
# BUILD INDEX.HTML
# ==============================

html = f"""
<!DOCTYPE html>
<html>
<head>

<title>AI NSE Market Intelligence</title>

<style>

body {{
font-family:Arial;
margin:0;
background:#f4f6fb;
}}

header {{
background:#002b5c;
color:white;
padding:30px;
text-align:center;
}}

nav {{
background:#0050a0;
padding:12px;
}}

nav a {{
color:white;
margin-right:25px;
text-decoration:none;
font-weight:bold;
}}

.container {{
max-width:1100px;
margin:auto;
padding:20px;
}}

.grid {{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
gap:20px;
}}

.card {{
background:white;
padding:20px;
border-radius:8px;
box-shadow:0 2px 10px rgba(0,0,0,0.1);
}}

.highlight {{
background:#e8f2ff;
padding:15px;
border-radius:8px;
margin-bottom:20px;
}}

footer {{
background:#eee;
text-align:center;
padding:15px;
margin-top:40px;
}}

</style>

</head>

<body>

<header>
<h1>AI EOD NSE Market Intelligence</h1>
<p>Automated Quant Research Dashboard</p>
</header>

<nav>

<a href="#">Home</a>
<a href="#signals">Market Signals</a>
<a href="#reports">AI Reports</a>
<a href="#how">How It Works</a>

</nav>

<div class="container">

<div class="highlight">
<b>Latest Report:</b>
<a href="{latest_report}" target="_blank">{latest_report}</a>
</div>

<h2 id="signals">Market Signal Dashboards</h2>

<div class="grid">

<div class="card"><h3>Breadth</h3><a href="breadth.html">Open</a></div>
<div class="card"><h3>Delivery Spike</h3><a href="delivery_spike.html">Open</a></div>
<div class="card"><h3>High Low</h3><a href="highlow.html">Open</a></div>
<div class="card"><h3>Momentum MA</h3><a href="momentum_ma.html">Open</a></div>
<div class="card"><h3>Recurring Entry</h3><a href="recurring_entry.html">Open</a></div>
<div class="card"><h3>Sector Rotation</h3><a href="sector_rotation.html">Open</a></div>

</div>

<h2 id="reports">AI Daily Reports</h2>

<ul>

{report_links}

</ul>

<h2 id="how">How It Works</h2>

<ol>
<li>EOD NSE data collected</li>
<li>Quant signals generated</li>
<li>AI interprets market regime</li>
<li>HTML report auto generated</li>
</ol>

</div>

<footer>

Educational Purpose Only • Not Financial Advice

</footer>

</body>
</html>
"""

index_path = os.path.join(git_folder, "index.html")

with open(index_path, "w", encoding="utf-8") as f:
    f.write(html)

print("✔ index.html built")

# ==============================
# GIT COMMIT + PUSH
# ==============================

print("------------------------------")
print("Publishing to GitHub...")

os.chdir(git_folder)

subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", f"Auto publish {latest_folder}"])
subprocess.run(["git", "push"])

print("------------------------------")
print("🚀 WEBSITE UPDATED SUCCESSFULLY")
print("https://websivasankar.github.io/screener/")