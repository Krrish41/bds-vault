#!/usr/bin/env python3
import json
import re
import os

HUB_DIR = r"c:\Users\Krrish\Desktop\Krrish\bds-vault"
INDEX_PATH = os.path.join(HUB_DIR, "index.html")
SNAPSHOT_PATH = os.path.join(HUB_DIR, "topics.snapshot.json")

with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
    snapshot = json.load(f)

portals = snapshot["portals"]
surgery_topics = portals["surgery"]
medicine_topics = portals["medicine"]
pathology_topics = portals["pathology"]

total_topics = len(surgery_topics) + len(medicine_topics) + len(pathology_topics)
print(f"Total topics: {total_topics} (Surgery: {len(surgery_topics)}, Medicine: {len(medicine_topics)}, Pathology: {len(pathology_topics)})")

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update Hero Trust and Filter chips
html = re.sub(
    r'3rd Year University Examination Syllabus • \d+ Curated Monograph Essays(?:\s*&amp;\s*Revision Units|\s*&\s*Revision Units)*',
    f'3rd Year University Examination Syllabus • {total_topics} Curated Monograph Essays &amp; Revision Units',
    html
)
html = html.replace('Paper I: Surgery (23)', f'Paper I: Surgery ({len(surgery_topics)})')
html = html.replace('Paper II: Medicine (20)', f'Paper II: Medicine ({len(medicine_topics)})')
html = html.replace('Paper III: Pathology (20)', f'Paper III: Pathology ({len(pathology_topics)})')

# 2. Update Cockpit stats
html = re.sub(
    r'<span class="deck-stat-val">\d+</span>\s*<span class="deck-stat-label">Total University Essays</span>',
    f'<span class="deck-stat-val">{total_topics}</span>\n                            <span class="deck-stat-label">Total University Essays</span>',
    html
)
html = re.sub(
    r'<span id="progressBarText">0 of \d+ Completed</span>',
    f'<span id="progressBarText">0 of {total_topics} Completed</span>',
    html
)

# 3. Update Surgery card counter and progress
html = re.sub(
    r'(<div class="bento-card col-span-4 specialty-bento surgery-card"[\s\S]*?<span class="counter-num">)\d+(</span>)',
    rf'\g<1>{len(surgery_topics)}\g<2>',
    html
)
html = re.sub(
    r'<span id="progressSurgeryText">0 of \d+ Done</span>',
    f'<span id="progressSurgeryText">0 of {len(surgery_topics)} Done</span>',
    html
)

# 4. Helper to build topic chips container HTML
def format_title(raw_title):
    cleaned = re.sub(r'^(Chapter\s*\d+[:.]*|\d+[\.:\s]+)', '', raw_title, flags=re.IGNORECASE).strip()
    # If title has colon or dash, keep first part if reasonable length
    if ':' in cleaned:
        cleaned = cleaned.split(':')[0].strip()
    if ' & ' in cleaned and len(cleaned) > 28:
        parts = cleaned.split(' & ')
        cleaned = parts[0].strip()
    if len(cleaned) > 30:
        cleaned = cleaned[:28].strip() + '…'
    return cleaned

def build_topic_chips_html(paper_key, topic_list):
    primary = topic_list[:3]
    more = topic_list[3:]
    more_count = len(more)
    
    html_parts = ['<div class="topic-chips-container">']
    for t in primary:
        short = format_title(t["title"])
        full = t["title"].replace('"', '&quot;')
        html_parts.append(f'    <a href="{t["url"]}" target="_blank" class="topic-chip-tag" title="{full}">{short}</a>')
    
    html_parts.append(f'    <button class="topic-chip-more" onclick="toggleTopicExpand(\'{paper_key}\', this)">+{more_count} more</button>')
    html_parts.append(f'    <div class="topics-expanded-drawer" id="topics-more-{paper_key}">')
    html_parts.append(f'        <div class="drawer-search-wrap"><input type="text" class="drawer-search-input" placeholder="Filter {paper_key} topics..." oninput="filterDrawerTopics(\'{paper_key}\', this.value)"></div>')
    html_parts.append(f'        <div class="drawer-topics-list" id="drawer-list-{paper_key}">')
    for t in more:
        short = format_title(t["title"])
        full = t["title"].replace('"', '&quot;')
        html_parts.append(f'            <a href="{t["url"]}" target="_blank" class="topic-chip-tag" title="{full}">{short}</a>')
    html_parts.append('        </div>')
    html_parts.append('    </div>')
    html_parts.append('</div>')
    return '\n'.join(html_parts)

# Replace topic-chips-container in Surgery card
surg_chips = build_topic_chips_html('surgery', surgery_topics)
html = re.sub(
    r'<!-- Topic Chips: 3 Primary \+ Expandable Drawer -->\s*<div class="topic-chips-container">[\s\S]*?</div>\s*</div>\s*(?=<div class="paper-progress-strip">)',
    f'<!-- Topic Chips: 3 Primary + Expandable Drawer -->\n{surg_chips}\n',
    html,
    count=1
)

# Replace topic-chips-container in Medicine card
med_chips = build_topic_chips_html('medicine', medicine_topics)
# Target after medicine-card
med_marker = '<div class="bento-card col-span-4 specialty-bento medicine-card"'
med_idx = html.find(med_marker)
if med_idx != -1:
    before = html[:med_idx]
    after = html[med_idx:]
    after = re.sub(
        r'<!-- Topic Chips: 3 Primary \+ Expandable Drawer -->\s*<div class="topic-chips-container">[\s\S]*?</div>\s*</div>\s*(?=<div class="paper-progress-strip">)',
        f'<!-- Topic Chips: 3 Primary + Expandable Drawer -->\n{med_chips}\n',
        after,
        count=1
    )
    html = before + after

# Replace topic-chips-container in Pathology card
path_chips = build_topic_chips_html('pathology', pathology_topics)
path_marker = '<div class="bento-card col-span-4 specialty-bento pathology-card"'
path_idx = html.find(path_marker)
if path_idx != -1:
    before = html[:path_idx]
    after = html[path_idx:]
    after = re.sub(
        r'<!-- Topic Chips: 3 Primary \+ Expandable Drawer -->\s*<div class="topic-chips-container">[\s\S]*?</div>\s*</div>\s*(?=<div class="paper-progress-strip">)',
        f'<!-- Topic Chips: 3 Primary + Expandable Drawer -->\n{path_chips}\n',
        after,
        count=1
    )
    html = before + after

# 5. Add Drawer CSS styles
drawer_css = """
        .topic-chip-tag {
            text-decoration: none;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
        }
        .topic-chip-tag:hover {
            transform: translateY(-1px);
            filter: brightness(1.2);
        }
        .drawer-search-wrap {
            width: 100%;
            margin-bottom: 8px;
        }
        .drawer-search-input {
            width: 100%;
            padding: 6px 10px;
            font-size: 0.78rem;
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-primary);
            outline: none;
            font-family: inherit;
            box-sizing: border-box;
        }
        .drawer-search-input:focus {
            border-color: var(--accent-primary);
        }
        .drawer-topics-list {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            max-height: 220px;
            overflow-y: auto;
            padding-right: 4px;
            width: 100%;
        }
"""
if ".drawer-search-input" not in html:
    html = html.replace("/* Dynamic Topic Progress Strip */", drawer_css + "\n        /* Dynamic Topic Progress Strip */")

# 6. Build complete ALL_TOPICS JS array (all 64 topics)
all_topics_js = []
for t in surgery_topics:
    all_topics_js.append({
        "title": t["title"],
        "sub": "General Surgery",
        "tag": "Paper I",
        "url": t["url"]
    })
for t in medicine_topics:
    all_topics_js.append({
        "title": t["title"],
        "sub": "General Medicine",
        "tag": "Paper II",
        "url": t["url"]
    })
for t in pathology_topics:
    all_topics_js.append({
        "title": t["title"],
        "sub": "Oral Pathology",
        "tag": "Paper III",
        "url": t["url"]
    })

js_array_str = "const ALL_TOPICS = " + json.dumps(all_topics_js, indent=12) + ";"
html = re.sub(r'const ALL_TOPICS = \[[\s\S]*?\];', js_array_str, html, count=1)

# 7. Update calculateOverallProgress and toggleTopicExpand
updated_js_functions = """
        // --- 3. Topic Expansion Drawer Toggle & Filter ---
        function toggleTopicExpand(paper, btn) {
            const drawer = document.getElementById(`topics-more-${paper}`);
            if (!drawer) return;
            const isOpen = drawer.classList.contains('open');
            const totalRemaining = paper === 'surgery' ? 21 : 17;
            if (isOpen) {
                drawer.classList.remove('open');
                btn.textContent = `+${totalRemaining} more`;
            } else {
                drawer.classList.add('open');
                btn.textContent = 'Hide';
                const input = drawer.querySelector('.drawer-search-input');
                if (input) setTimeout(() => input.focus(), 50);
            }
        }

        function filterDrawerTopics(paper, query) {
            const list = document.getElementById(`drawer-list-${paper}`);
            if (!list) return;
            const q = query.toLowerCase().trim();
            const chips = list.querySelectorAll('.topic-chip-tag');
            chips.forEach(chip => {
                const text = chip.textContent.toLowerCase() + ' ' + (chip.getAttribute('title') || '').toLowerCase();
                chip.style.display = (!q || text.includes(q)) ? 'inline-flex' : 'none';
            });
        }

        // --- 4. Live Progress Calculation from localStorage across All 3 Portals ---
        function calculateOverallProgress() {
            try {
                const getCount = (k1, k2) => {
                    const raw = localStorage.getItem(k1) || localStorage.getItem(k2) || '{}';
                    try { return Object.keys(JSON.parse(raw)).length; } catch(e) { return 0; }
                };

                const surgDone = getCount('bds.surgery.progress', 'surgery_completed_topics');
                const medDone = getCount('bds.medicine.progress', 'medicine_completed_topics');
                const pathDone = getCount('bds.pathology.progress', 'oral_pathology_completed_topics');

                const totalCompleted = surgDone + medDone + pathDone;
                const totalTopics = 64;
                const pct = Math.min(100, Math.round((totalCompleted / totalTopics) * 100));

                const countEl = document.getElementById('totalCompletedDisplay');
                const pctEl = document.getElementById('overallPercentDisplay');
                const barEl = document.getElementById('deckProgressBar');
                const textEl = document.getElementById('progressBarText');

                if (countEl) countEl.textContent = totalCompleted;
                if (pctEl) pctEl.textContent = `${pct}%`;
                if (barEl) barEl.style.width = `${pct}%`;
                if (textEl) textEl.textContent = `${totalCompleted} of ${totalTopics} Completed`;

                // Update individual card progress bars
                const surgPct = Math.min(100, Math.round((surgDone / 24) * 100));
                const surgBar = document.getElementById('progressSurgeryFill');
                const surgTxt = document.getElementById('progressSurgeryText');
                if (surgBar) surgBar.style.width = `${surgPct}%`;
                if (surgTxt) surgTxt.textContent = `${surgDone} of 24 Done`;

                const medPct = Math.min(100, Math.round((medDone / 20) * 100));
                const medBar = document.getElementById('progressMedicineFill');
                const medTxt = document.getElementById('progressMedicineText');
                if (medBar) medBar.style.width = `${medPct}%`;
                if (medTxt) medTxt.textContent = `${medDone} of 20 Done`;

                const pathPct = Math.min(100, Math.round((pathDone / 20) * 100));
                const pathBar = document.getElementById('progressPathologyFill');
                const pathTxt = document.getElementById('progressPathologyText');
                if (pathBar) pathBar.style.width = `${pathPct}%`;
                if (pathTxt) pathTxt.textContent = `${pathDone} of 20 Done`;

            } catch (e) {
                console.log('Error calculating study progress:', e);
            }
        }
"""

html = re.sub(
    r'// --- 3\. Topic Expansion Drawer Toggle ---[\s\S]*?// --- 5\. Theme Switching Logic ---',
    updated_js_functions.strip() + '\n\n        // --- 5. Theme Switching Logic ---',
    html,
    count=1
)

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully updated bds-vault/index.html!")
