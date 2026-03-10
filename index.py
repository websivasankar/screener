import os

# Get all AI report files
files = [f for f in os.listdir() if f.startswith("ai_analysis") and f.endswith(".html")]
files.sort(reverse=True)  # latest first

# Start HTML
html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AI EOD NSE Market Reports</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f9f9f9;
            color: #333;
        }
        header {
            background-color: #004080;
            color: white;
            padding: 20px;
            text-align: center;
        }
        main {
            max-width: 900px;
            margin: 20px auto;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1, h2 {
            color: #004080;
        }
        ul {
            list-style-type: disc;
            padding-left: 20px;
        }
        a {
            color: #004080;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        footer {
            text-align: center;
            padding: 15px;
            margin-top: 20px;
            background-color: #e6e6e6;
            font-size: 0.9em;
        }
    </style>
</head>
<body>

        <h2>AI Market Analysis Reports</h2>
        <p>
            This site provides <strong>daily AI-generated End-of-Day (EOD) market reports</strong> for the Indian NSE. Each report summarizes key market conditions, breadth, sector rotation, institutional activity, and stock insights based on the latest available data.
        </p>
<div class="report-list">
"""

# Add links
for f in files:
    html += f'<a href="{f}">{f}</a><br>\n'

# End HTML
html += """
    <section id="how-it-works">
        <h2>How It Works</h2>
        <ol>
            <li><strong>Data Collection:</strong> Market data is gathered at EOD — indices, stock performance, volatility, breadth, futures & options OI, delivery trends.</li>
            <li><strong>AI Interpretation:</strong> An AI model analyzes the data to identify market regime (Bull/Bear/Neutral), sector rotation, institutional activity, and stock-specific patterns.</li>
            <li><strong>Report Generation:</strong> A structured HTML report is automatically generated with commentary, key metrics, and charts.</li>
            <li><strong>Publication:</strong> The report is published daily as a dated HTML file on this site.</li>
        </ol>
    </section>

    <section id="why-use">
        <h2>Why Use It</h2>
        <ul>
            <li>Saves time — ready-made, data-driven market summary.</li>
            <li>AI contextual analysis of multiple signals for better insight.</li>
            <li>Daily reports archived for historical reference and tracking market evolution.</li>
        </ul>
    </section>
</main>

<footer>
    &copy; 2026 AI EOD NSE Market Reports. For educational purposes only, not financial advice.
</footer>
</div>
</body>
</html>
"""

# Write to index.html
with open("index.html", "w") as f:
    f.write(html)