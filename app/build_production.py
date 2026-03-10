#!/usr/bin/env python3
"""
Build script for Entrepreneurship Research Knowledge Base (Production)

This script creates a production-ready deployment by:
1. Embedding data.json into index.html (self-contained for GitHub Pages)
2. Adding Google Analytics and anti-scraping deterrents
3. Also copying data.json separately (for open-source users who want to swap data)
4. Optionally stripping fields from data.json you don't want exposed publicly

Usage:
    cd 4_app
    python3 build_production.py

Input:  index.html + data.json (in same directory)
Output: deploy/index.html (self-contained) + deploy/data.json (separate copy)

Architecture:
- Production (deploy/index.html): Data embedded as window.__ERKB_DATA — works on GitHub Pages
- Development (4_app/index.html + data.json): Loads via fetch() — requires local HTTP server
- Open source: Users get index.html (without embed) + data.json, run local server
"""

import json
import os
import shutil
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(SCRIPT_DIR, 'index.html')
DATA_PATH = os.path.join(SCRIPT_DIR, 'data.json')
DEPLOY_DIR = os.path.join(SCRIPT_DIR, 'deploy')

# Fields to REMOVE from public data (these will be stripped before copying)
# The app will still work — these fields just won't be available to public users
# Admin can still export full data via Excel (with password re-auth)
FIELDS_TO_STRIP = [
    # Uncomment any fields you want to hide from public view:
    # 'abstract',      # Full abstracts (large, valuable content)
    # 'notes',         # Your personal research notes
    # 'tags',          # Your custom tags
    # 'tDisc',         # Theory discipline
    # 'dsNamed',       # Named datasets
]

def main():
    if not os.path.exists(INDEX_PATH):
        print(f"ERROR: {INDEX_PATH} not found")
        sys.exit(1)
    if not os.path.exists(DATA_PATH):
        print(f"ERROR: {DATA_PATH} not found")
        sys.exit(1)

    # ── Process data.json ──
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    print(f"Loaded {len(papers)} papers from data.json")

    if FIELDS_TO_STRIP:
        for p in papers:
            for field in FIELDS_TO_STRIP:
                p.pop(field, None)
        print(f"Stripped fields: {FIELDS_TO_STRIP}")

    # Minify JSON
    data_json = json.dumps(papers, separators=(',', ':'), ensure_ascii=False)
    print(f"Data size: {len(data_json):,} chars ({len(data_json.encode('utf-8')):,} bytes)")

    # ── Process index.html ──
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # Google Analytics
    ga_tag = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-6KS7NJXM80"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-6KS7NJXM80');
</script>'''

    # Anti-scraping deterrents (UI-level deterrents, not true security)
    anti_scrape = '''<script>
/* Basic deterrents — won't stop determined users but raises the bar */
document.addEventListener('contextmenu', function(e) { e.preventDefault(); });
document.addEventListener('keydown', function(e) {
  if (e.ctrlKey && (e.key === 'u' || e.key === 'U' || e.key === 's' || e.key === 'S')) { e.preventDefault(); }
  if (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'i' || e.key === 'J' || e.key === 'j')) { e.preventDefault(); }
  if (e.key === 'F12') { e.preventDefault(); }
});
</script>'''

    # Insert Google Analytics right after <head>
    html = html.replace('<head>', f'<head>\n{ga_tag}', 1)

    # Embed data as window.__ERKB_DATA (so deployed version is self-contained)
    embed_script = f'<script>window.__ERKB_DATA={data_json};</script>'

    # Insert embedded data + anti-scraping BEFORE </body>
    if '</body>' in html:
        html = html.replace('</body>', f'{embed_script}\n{anti_scrape}\n</body>')
    else:
        html = html.replace('</html>', f'{embed_script}\n{anti_scrape}\n</html>')

    # ── Write output ──
    os.makedirs(DEPLOY_DIR, exist_ok=True)

    # 1. Self-contained version (data embedded) — for simple GitHub Pages deployment
    output_html = os.path.join(DEPLOY_DIR, 'index.html')
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)

    # 2. Lightweight version (no embedded data, loads data.json at runtime)
    #    Read original index.html again, only add GA + anti-scraping (no data embed)
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html_light = f.read()
    html_light = html_light.replace('<head>', f'<head>\n{ga_tag}', 1)
    if '</body>' in html_light:
        html_light = html_light.replace('</body>', f'{anti_scrape}\n</body>')
    else:
        html_light = html_light.replace('</html>', f'{anti_scrape}\n</html>')

    output_html_light = os.path.join(DEPLOY_DIR, 'index_light.html')
    with open(output_html_light, 'w', encoding='utf-8') as f:
        f.write(html_light)

    # 3. Data file (separate copy)
    output_data = os.path.join(DEPLOY_DIR, 'data.json')
    with open(output_data, 'w', encoding='utf-8') as f:
        f.write(data_json)

    def fmt_size(path):
        b = os.path.getsize(path)
        if b >= 1024 * 1024: return f"{b / (1024*1024):.1f} MB"
        return f"{b / 1024:.0f} KB"

    print(f"\nProduction build complete!")
    print(f"  deploy/index.html       ({fmt_size(output_html)}) — self-contained with embedded data")
    print(f"  deploy/index_light.html ({fmt_size(output_html_light)}) — lightweight, loads data.json dynamically")
    print(f"  deploy/data.json        ({fmt_size(output_data)}) — data file for dynamic loading")
    print(f"\nDeployment options:")
    print(f"  Option A (simple):  Push only index.html — everything in one file")
    print(f"  Option B (dynamic): Rename index_light.html → index.html, push with data.json")
    print(f"                      Update data by replacing data.json only (no app rebuild needed)")

if __name__ == '__main__':
    main()
