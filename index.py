import os

files = [f for f in os.listdir() if f.startswith("ai_analysis") and f.endswith(".html")]
files.sort(reverse=True)

html = "<h1>AI Market Analysis Reports</h1>\n"

for f in files:
    html += f'<a href="{f}">{f}</a><br>\n'

with open("index.html","w") as f:
    f.write(html)