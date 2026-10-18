#!/usr/bin/env python3
"""
BDS Clinical Vault — Master Hub Generator & Compiler
Generates the consolidated, ultra-consistent index.html for BDS Clinical Vault.
Enforces:
- Solid full-bleed sticky header (64px) with single-color sans wordmark
- Slim segmented progress strip (<=56px) directly under hero
- Exactly 3 fixed-height portal cards with identical anatomy and 2x2 topic preview grid
- Topic Panel dialog (desktop popover anchored to button / mobile bottom sheet)
- Re-homed 15-mark rubrics and chairside cutoffs inside Quick Reference modal
- Calm design tokens (Surgery teal, Medicine indigo #6366f1, Pathology orchid)
- Accurate data-driven counts (23 Surgery + 20 Medicine + 20 Pathology = 63 University Monograph Essays)
- 20 stable data-testid hooks for Playwright consistency testing
"""

import json
import os
import re

HUB_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(HUB_DIR, "index.html")
SNAPSHOT_PATH = os.path.join(HUB_DIR, "topics.snapshot.json")
TOKENS_PATH = os.path.join(HUB_DIR, "portal-core", "design-tokens.json")

# 1. Load Registry Snapshot
with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
    snapshot = json.load(f)

portals = snapshot["portals"]

# Filter out non-essay types (e.g. cheat sheets) so topic counts reflect university monograph essays
surgery_topics = [t for t in portals.get("surgery", []) if t.get("type", "essay") == "essay"]
medicine_topics = [t for t in portals.get("medicine", []) if t.get("type", "essay") == "essay"]
pathology_topics = [t for t in portals.get("pathology", []) if t.get("type", "essay") == "essay"]

total_essays = len(surgery_topics) + len(medicine_topics) + len(pathology_topics)
print(f"Loaded verified essays: {total_essays} (Surgery: {len(surgery_topics)}, Medicine: {len(medicine_topics)}, Pathology: {len(pathology_topics)})")

# Helper for display titles
def get_short_title(title):
    cleaned = re.sub(r'^(Chapter\s*\d+[:.]*|\d+[\.:\s]+)', '', title, flags=re.IGNORECASE).strip()
    if ':' in cleaned:
        cleaned = cleaned.split(':')[0].strip()
    if ' & ' in cleaned and len(cleaned) > 24:
        parts = cleaned.split(' & ')
        cleaned = parts[0].strip()
    if len(cleaned) > 28:
        cleaned = cleaned[:26].strip() + '…'
    return cleaned

# 4 Topic Preview bubbles per card
surgery_previews = surgery_topics[:4]
medicine_previews = medicine_topics[:4]
pathology_previews = pathology_topics[:4]

# Comprehensive search array (63 essays + Spotters, Flashcards, Schematics)
all_search_topics = []
for t in surgery_topics:
    all_search_topics.append({
        "title": t["title"],
        "sub": "General Surgery Pro",
        "tag": "Paper I",
        "category": t.get("category", "General Surgery"),
        "type": "essay",
        "url": t["url"],
        "paper": "surgery"
    })
for t in medicine_topics:
    all_search_topics.append({
        "title": t["title"],
        "sub": "General Medicine Pro",
        "tag": "Paper II",
        "category": t.get("category", "General Medicine"),
        "type": "essay",
        "url": t["url"],
        "paper": "medicine"
    })
for t in pathology_topics:
    all_search_topics.append({
        "title": t["title"],
        "sub": "Oral Pathology Pro",
        "tag": "Paper III",
        "category": t.get("category", "Oral Pathology"),
        "type": "essay",
        "url": t["url"],
        "paper": "pathology"
    })

# Spotters
all_search_topics.extend([
    {
        "title": "Surgical Instruments, Specimen & Clinical Spotters",
        "sub": "General Surgery Pro",
        "tag": "Spotters",
        "category": "Clinical Spotters",
        "type": "spotters",
        "url": "https://krrish41.github.io/general-surgery/#/spotters",
        "paper": "surgery"
    },
    {
        "title": "Hemodynamic, ECG & Bedside Spotters",
        "sub": "General Medicine Pro",
        "tag": "Spotters",
        "category": "Clinical Spotters",
        "type": "spotters",
        "url": "https://krrish41.github.io/General-Medicine/#/spotters",
        "paper": "medicine"
    },
    {
        "title": "Microscopic Spotters & Histopathology Carousel (40 Cards)",
        "sub": "Oral Pathology Pro",
        "tag": "Spotters",
        "category": "Clinical Spotters",
        "type": "spotters",
        "url": "https://krrish41.github.io/Oral-Pathology/#/spotters",
        "paper": "pathology"
    }
])

# Flashcards
all_search_topics.extend([
    {
        "title": "General Surgery Rapid Recall Viva Flashcards",
        "sub": "General Surgery Pro",
        "tag": "Flashcards",
        "category": "Active Recall",
        "type": "flashcards",
        "url": "https://krrish41.github.io/general-surgery/#/simulator",
        "paper": "surgery"
    },
    {
        "title": "General Medicine Active Recall Flashcards",
        "sub": "General Medicine Pro",
        "tag": "Flashcards",
        "category": "Active Recall",
        "type": "flashcards",
        "url": "https://krrish41.github.io/General-Medicine/#/simulator",
        "paper": "medicine"
    },
    {
        "title": "Oral Pathology Active Recall Flashcards",
        "sub": "Oral Pathology Pro",
        "tag": "Flashcards",
        "category": "Active Recall",
        "type": "flashcards",
        "url": "https://krrish41.github.io/Oral-Pathology/#/simulator",
        "paper": "pathology"
    }
])

# Schematics
all_search_topics.extend([
    {
        "title": "Neck Triangles & Fascial Planes Surgical Schematics",
        "sub": "General Surgery Pro",
        "tag": "Schematics",
        "category": "Must-Draw Schematics",
        "type": "schematics",
        "url": "https://krrish41.github.io/general-surgery/#/spotters",
        "paper": "surgery"
    },
    {
        "title": "Cardiovascular Flow, Shock & Resuscitation Algorithms",
        "sub": "General Medicine Pro",
        "tag": "Schematics",
        "category": "Must-Draw Schematics",
        "type": "schematics",
        "url": "https://krrish41.github.io/General-Medicine/#/spotters",
        "paper": "medicine"
    },
    {
        "title": "Odontogenic Lesion & Salivary Microscopic Schematics",
        "sub": "Oral Pathology Pro",
        "tag": "Schematics",
        "category": "Must-Draw Schematics",
        "type": "schematics",
        "url": "https://krrish41.github.io/Oral-Pathology/#/spotters",
        "paper": "pathology"
    }
])

# Serialized dataset for inline JS
all_topics_json = json.dumps(all_search_topics)
surgery_topics_json = json.dumps(surgery_topics)
medicine_topics_json = json.dumps(medicine_topics)
pathology_topics_json = json.dumps(pathology_topics)

html_content = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="description" content="BDS Clinical Vault — 3rd Year BDS University Examination Compendium & Clinical Command Suite for General Surgery, General Medicine, and Oral Pathology.">
    <meta name="theme-color" content="#090a12">
    <title>BDS Clinical Vault — 3rd Year University Examination Command Suite</title>
    
    <!-- PWA & Device Support -->
    <link rel="manifest" href="manifest.json">
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="apple-touch-icon.png">
    
    <!-- Typography -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=JetBrains+Mono:wght@400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;0,6..72,700;1,6..72,400&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <!-- Zero-Flash Pre-Paint Script -->
    <script>
        (function() {{
            var saved = localStorage.getItem('bds_hub_theme') || localStorage.getItem('bds_theme') || 'dark';
            document.documentElement.setAttribute('data-theme', saved);
            document.documentElement.style.backgroundColor = saved === 'light' ? '#f8fafc' : '#090a12';
            document.documentElement.style.colorScheme = saved;
        }})();
    </script>

    <style>
        /* =============================================================
           1. ECOSYSTEM DESIGN TOKENS (CALIBRATED ACCENT HUES & NEUTRALS)
           ============================================================= */
        :root {{
            --bg-base: #090a12;
            --bg-surface: #101322;
            --bg-surface-elevated: #161a2e;
            --bg-card: #101322;
            --bg-card-hover: #15192d;
            
            --border-color: rgba(255, 255, 255, 0.08);
            --border-strong: rgba(255, 255, 255, 0.16);
            --border-subtle: rgba(255, 255, 255, 0.05);

            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;

            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;

            /* Paper I: General Surgery (Clinical Surgical Teal) */
            --surgery-accent: #14b8a6;
            --surgery-accent-dark: #0d9488;
            --surgery-tag-bg: rgba(20, 184, 166, 0.12);
            --surgery-tag-border: rgba(20, 184, 166, 0.30);
            --surgery-tag-text: #5eead4;
            --surgery-btn: #0d9488;
            --surgery-btn-hover: #0f766e;

            /* Paper II: General Medicine (Diagnostic Clinical Indigo) */
            --medicine-accent: #6366f1;
            --medicine-accent-dark: #4f46e5;
            --medicine-tag-bg: rgba(99, 102, 241, 0.12);
            --medicine-tag-border: rgba(99, 102, 241, 0.30);
            --medicine-tag-text: #c7d2fe;
            --medicine-btn: #4f46e5;
            --medicine-btn-hover: #4338ca;

            /* Paper III: Oral Pathology (Histological Orchid / Magenta) */
            --pathology-accent: #c084fc;
            --pathology-accent-dark: #9333ea;
            --pathology-tag-bg: rgba(192, 132, 252, 0.12);
            --pathology-tag-border: rgba(192, 132, 252, 0.30);
            --pathology-tag-text: #f3e8ff;
            --pathology-btn: #9333ea;
            --pathology-btn-hover: #7e22ce;

            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.35);
            --shadow-md: 0 8px 24px -6px rgba(0, 0, 0, 0.55);
            --shadow-lg: 0 16px 40px -8px rgba(0, 0, 0, 0.75);

            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-pill: 9999px;
        }}

        [data-theme="light"] {{
            --bg-base: #f8fafc;
            --bg-surface: #ffffff;
            --bg-surface-elevated: #f1f5f9;
            --bg-card: #ffffff;
            --bg-card-hover: #f8fafc;
            
            --border-color: #e2e8f0;
            --border-strong: #cbd5e1;
            --border-subtle: #f1f5f9;

            --text-primary: #0f172a;
            --text-secondary: #475569;
            --text-muted: #64748b;

            --surgery-accent: #0d9488;
            --surgery-tag-bg: rgba(13, 148, 136, 0.08);
            --surgery-tag-border: rgba(13, 148, 136, 0.25);
            --surgery-tag-text: #0f766e;
            --surgery-btn: #0d9488;
            --surgery-btn-hover: #115e59;

            --medicine-accent: #4f46e5;
            --medicine-tag-bg: rgba(79, 70, 229, 0.08);
            --medicine-tag-border: rgba(79, 70, 229, 0.25);
            --medicine-tag-text: #3730a3;
            --medicine-btn: #4f46e5;
            --medicine-btn-hover: #4338ca;

            --pathology-accent: #9333ea;
            --pathology-tag-bg: rgba(147, 51, 234, 0.08);
            --pathology-tag-border: rgba(147, 51, 234, 0.25);
            --pathology-tag-text: #6b21a8;
            --pathology-btn: #9333ea;
            --pathology-btn-hover: #7e22ce;

            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.06);
            --shadow-md: 0 6px 18px -4px rgba(0, 0, 0, 0.08);
            --shadow-lg: 0 14px 34px -6px rgba(0, 0, 0, 0.12);
        }}

        @supports (color: oklch(0 0 0)) {{
            :root {{
                --surgery-accent: oklch(0.68 0.11 180);
                --medicine-accent: oklch(0.58 0.11 275);
                --pathology-accent: oklch(0.66 0.11 315);
            }}
        }}

        /* Reset & Base Setup */
        html {{
            scroll-padding-top: 76px;
            scroll-behavior: smooth;
            background-color: var(--bg-base);
            color-scheme: dark;
        }}
        [data-theme="light"], body.light {{
            color-scheme: light;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
            scrollbar-width: thin;
            scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
        }}
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: transparent;
        }}
        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            border: 2px solid transparent;
            background-clip: content-box;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.35);
            background-clip: content-box;
        }}
        ::-webkit-scrollbar-button {{
            display: none;
        }}
        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-primary);
            line-height: 1.6;
            font-size: 15px;
            min-height: 100dvh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            width: 100%;
            -webkit-font-smoothing: antialiased;
        }}

        /* Utility Typography */
        .editorial-heading {{
            font-family: 'Newsreader', Georgia, serif;
            font-weight: 600;
        }}
        .cinzel-brand {{
            font-family: 'Cinzel', serif;
            letter-spacing: 0.04em;
        }}
        .mono-num {{
            font-family: 'JetBrains Mono', monospace;
            font-variant-numeric: tabular-nums;
        }}
        .sr-only {{
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border-width: 0;
        }}

        /* =============================================================
           2. SOLID FULL-BLEED STICKY HEADER (64px, NEVER OVERFLOWS)
           ============================================================= */
        .header-solid {{
            position: sticky;
            top: 0;
            z-index: 1000;
            height: 64px;
            width: 100%;
            background-color: var(--bg-base);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            box-sizing: border-box;
            min-width: 0;
        }}

        .brand-link {{
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
            color: inherit;
            flex-shrink: 0;
            min-width: 0;
        }}
        .brand-logo-tile {{
            width: 38px;
            height: 38px;
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid var(--border-color);
            background: rgba(255, 255, 255, 0.04);
            flex-shrink: 0;
        }}
        .brand-logo-tile img {{
            width: 24px;
            height: 24px;
            display: block;
        }}
        .brand-wordmark-group {{
            display: flex;
            flex-direction: column;
            line-height: 1.15;
            min-width: 0;
            overflow: hidden;
        }}
        .brand-wordmark {{
            font-size: 0.95rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            color: var(--text-primary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .brand-sub {{
            font-size: 0.68rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            white-space: nowrap;
        }}

        /* Center Search with Inline Dropdown */
        .header-search-wrap {{
            flex: 1;
            max-width: 440px;
            margin: 0 16px;
            position: relative;
            min-width: 0;
        }}
        .hub-search-box {{
            width: 100%;
            height: 38px;
            padding: 0 12px;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-pill);
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-muted);
            transition: all 0.2s ease;
        }}
        .hub-search-box:focus-within {{
            border-color: var(--accent-primary, #6366f1);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
        }}
        .hub-search-input {{
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            font-family: inherit;
            font-size: 0.84rem;
            color: var(--text-primary);
            min-width: 0;
        }}
        .hub-search-input::placeholder {{
            color: var(--text-muted);
        }}
        .hub-search-clear {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            padding: 2px 6px;
            font-size: 0.8rem;
            border-radius: 50%;
        }}
        .hub-search-clear:hover {{
            color: var(--text-primary);
        }}
        .search-back-btn {{
            display: none;
            align-items: center;
            justify-content: center;
            width: 38px;
            height: 38px;
            border-radius: var(--radius-sm);
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            flex-shrink: 0;
        }}
        .search-back-btn:hover {{
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.08);
        }}

        .hub-search-results {{
            position: absolute;
            top: calc(100% + 6px);
            left: 0;
            right: 0;
            max-height: 440px;
            overflow-y: auto;
            background: var(--bg-surface-elevated, #101322);
            border: 1px solid var(--border-strong, rgba(255, 255, 255, 0.18));
            border-radius: var(--radius-md, 12px);
            padding: 8px;
            box-shadow: var(--shadow-lg);
            z-index: 1050;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        /* Mobile Trigger Buttons (<768px) */
        .mobile-search-btn,
        .mobile-overflow-btn {{
            display: none;
            align-items: center;
            justify-content: center;
            width: 44px;
            height: 44px;
            border-radius: var(--radius-sm);
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            cursor: pointer;
            position: relative;
            flex-shrink: 0;
            transition: all 0.15s ease;
        }}
        .mobile-search-btn:hover,
        .mobile-overflow-btn:hover {{
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-primary);
        }}
        .overflow-timer-dot {{
            position: absolute;
            top: 9px;
            right: 9px;
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--text-muted);
            opacity: 0;
            transition: all 0.2s ease;
        }}
        .mobile-overflow-btn.running .overflow-timer-dot {{
            opacity: 1;
            background: var(--accent-emerald, #10b981);
            box-shadow: 0 0 8px var(--accent-emerald, #10b981);
        }}

        /* Mobile Overflow Scrim & Menu */
        .hub-overflow-scrim {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.55);
            z-index: 1040;
            backdrop-filter: none;
            -webkit-backdrop-filter: none;
        }}
        .hub-overflow-scrim.open {{
            display: block;
        }}

        .hub-overflow-menu {{
            display: none;
            background: var(--bg-surface-elevated, #161a2e);
            border: 1px solid var(--border-strong);
            box-shadow: var(--shadow-lg);
            z-index: 1050;
            box-sizing: border-box;
            flex-direction: column;
            gap: 12px;
        }}
        .hub-overflow-menu.open {{
            display: flex;
        }}

        .overflow-header-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border-color);
        }}
        .overflow-menu-title {{
            font-size: 0.80rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
        }}
        .overflow-close-btn {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 1.1rem;
            padding: 4px;
        }}

        .overflow-timer-card {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .overflow-timer-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--text-muted);
        }}
        .overflow-timer-digits {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.8rem;
            font-weight: 800;
            color: var(--text-primary);
            text-align: center;
        }}
        .overflow-timer-actions {{
            display: flex;
            gap: 6px;
        }}
        .overflow-timer-btn {{
            flex: 1;
            min-height: 38px;
            border-radius: var(--radius-sm);
            font-size: 0.8rem;
            font-weight: 700;
            cursor: pointer;
            border: 1px solid var(--border-color);
            background: var(--bg-surface-2, rgba(255, 255, 255, 0.04));
            color: var(--text-secondary);
            transition: all 0.15s ease;
        }}
        .overflow-timer-btn.primary {{
            background: var(--accent-emerald, #10b981);
            color: #090a12;
            border-color: var(--accent-emerald, #10b981);
            flex: 1.4;
        }}
        .overflow-timer-btn.active {{
            border-color: var(--accent-emerald, #10b981);
            color: var(--accent-emerald, #10b981);
        }}

        .overflow-action-row {{
            width: 100%;
            min-height: 46px;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 0 14px;
            border-radius: var(--radius-sm);
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            font-size: 0.88rem;
            font-weight: 600;
            cursor: pointer;
            text-align: left;
            transition: all 0.15s ease;
            box-sizing: border-box;
        }}
        .overflow-action-row:hover {{
            background: rgba(255, 255, 255, 0.07);
        }}
        .hub-search-group {{
            margin-bottom: 6px;
        }}
        .hub-search-group-title {{
            font-size: 0.70rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            padding: 6px 10px 4px 10px;
        }}
        .hub-search-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 12px;
            border-radius: var(--radius-sm, 8px);
            text-decoration: none;
            color: var(--text-secondary);
            font-size: 0.84rem;
            transition: all 0.15s ease;
            gap: 10px;
        }}
        .hub-search-item:hover, .hub-search-item.selected {{
            background: rgba(255, 255, 255, 0.06);
            color: var(--text-primary);
        }}
        .hub-search-item-title {{
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .hub-search-item-tag {{
            font-size: 0.68rem;
            font-family: 'JetBrains Mono', monospace;
            padding: 2px 6px;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-muted);
            white-space: nowrap;
            flex-shrink: 0;
        }}

        /* Collapsible Category Accordions for Topic Panel */
        .panel-category-group {{
            margin-bottom: 8px;
        }}
        .panel-category-header {{
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            color: var(--text-secondary);
            font-size: 0.76rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .panel-category-header:hover {{
            background: rgba(255, 255, 255, 0.06);
            color: var(--text-primary);
        }}
        .panel-category-chevron {{
            transition: transform 0.2s ease;
            font-size: 0.7rem;
            color: var(--text-muted);
        }}
        .panel-category-group.collapsed .panel-category-chevron {{
            transform: rotate(-90deg);
        }}
        .panel-category-group.collapsed .panel-category-items {{
            display: none;
        }}
        .panel-category-items {{
            display: flex;
            flex-direction: column;
            gap: 2px;
            margin-top: 4px;
        }}

        /* Right Nav Tools */
        .header-right-tools {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-shrink: 0;
        }}
        .nav-btn {{
            height: 36px;
            padding: 0 12px;
            border-radius: var(--radius-sm);
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            font-size: 0.82rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            box-sizing: border-box;
        }}
        .nav-btn:hover {{
            background: var(--bg-surface-elevated);
            color: var(--text-primary);
            border-color: var(--border-strong);
        }}

        /* Focus Timer Station Pill & Popover */
        .focus-timer-container {{
            position: relative;
        }}
        .timer-nav-pill {{
            padding: 0 10px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            gap: 6px;
        }}
        .timer-nav-pill.running {{
            border-color: var(--accent-emerald);
            color: var(--accent-emerald);
        }}
        .timer-chip-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--text-muted);
            transition: all 0.2s ease;
        }}
        .timer-nav-pill.running .timer-chip-dot {{
            background: var(--accent-emerald);
            box-shadow: 0 0 6px var(--accent-emerald);
        }}
        .timer-popover-card {{
            display: none;
            position: absolute;
            top: calc(100% + 8px);
            right: 0;
            width: 240px;
            background: var(--bg-surface-elevated);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-md);
            padding: 16px;
            box-shadow: var(--shadow-lg);
            z-index: 1050;
        }}
        .timer-popover-card.open {{
            display: block;
        }}
        .timer-popover-header {{
            font-size: 0.72rem;
            text-transform: uppercase;
            font-weight: 700;
            color: var(--text-muted);
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }}
        .timer-popover-digits {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 12px;
            color: var(--text-primary);
        }}
        .timer-popover-controls {{
            display: flex;
            gap: 6px;
        }}
        .timer-ctrl-btn {{
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 700;
            cursor: pointer;
            border: 1px solid var(--border-color);
            background: rgba(255, 255, 255, 0.04);
            color: var(--text-secondary);
            transition: all 0.15s ease;
        }}
        .timer-ctrl-btn:hover {{
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-primary);
        }}
        .timer-ctrl-btn.primary {{
            background: var(--text-primary);
            color: var(--bg-base);
            border: none;
            flex: 1;
        }}

        /* =============================================================
           3. MAIN CONTAINER & HERO BANNER
           ============================================================= */
        .main-content {{
            max-width: 1400px;
            width: 100%;
            margin: 0 auto;
            padding: 24px 24px 40px 24px;
            flex: 1;
        }}

        .hero-banner {{
            margin-bottom: 18px;
        }}
        .hero-trust-bar {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 0.78rem;
            color: var(--text-muted);
            margin-bottom: 8px;
            flex-wrap: wrap;
        }}
        .trust-badge {{
            background: rgba(20, 184, 166, 0.10);
            color: var(--surgery-tag-text);
            border: 1px solid var(--surgery-tag-border);
            padding: 2px 8px;
            border-radius: var(--radius-pill);
            font-weight: 700;
            font-size: 0.70rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .hero-title {{
            font-size: 2.1rem;
            font-weight: 600;
            color: var(--text-primary);
            letter-spacing: -0.01em;
            line-height: 1.18;
            margin-bottom: 6px;
        }}
        .hero-sub {{
            font-size: 0.95rem;
            color: var(--text-secondary);
            max-width: 820px;
            line-height: 1.5;
        }}

        /* =============================================================
           4. SLIM PROGRESS STRIP (<=56px, DIRECTLY UNDER HERO)
           ============================================================= */
        .progress-strip-container {{
            position: relative;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 10px 18px;
            margin-bottom: 24px;
            box-shadow: var(--shadow-sm);
        }}
        .progress-strip-inner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            height: 32px;
        }}
        .progress-strip-left {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--text-primary);
            white-space: nowrap;
        }}
        .progress-pulse-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-emerald);
            box-shadow: 0 0 6px var(--accent-emerald);
        }}
        .progress-strip-track {{
            flex: 1;
            height: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: var(--radius-pill);
            display: flex;
            overflow: hidden;
            gap: 2px;
            cursor: pointer;
        }}
        .progress-strip-segment {{
            height: 100%;
            background: rgba(255, 255, 255, 0.04);
            position: relative;
            overflow: hidden;
        }}
        .segment-fill {{
            height: 100%;
            transition: width 0.5s ease;
            border-radius: var(--radius-pill);
        }}
        .segment-surgery .segment-fill {{ background: var(--surgery-accent); }}
        .segment-medicine .segment-fill {{ background: var(--medicine-accent); }}
        .segment-pathology .segment-fill {{ background: var(--pathology-accent); }}

        .progress-strip-right {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--text-secondary);
            white-space: nowrap;
        }}

        /* Progress Breakdown Popover Tooltip */
        .progress-breakdown-popover {{
            display: none;
            position: absolute;
            top: calc(100% + 6px);
            left: 50%;
            transform: translateX(-50%);
            background: var(--bg-surface-elevated);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-sm);
            padding: 10px 14px;
            box-shadow: var(--shadow-md);
            z-index: 1020;
            gap: 12px;
            white-space: nowrap;
        }}
        .progress-breakdown-popover.open {{
            display: flex;
        }}
        .breakdown-row {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.78rem;
            font-family: 'JetBrains Mono', monospace;
        }}
        .breakdown-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
        }}
        .surgery-row .breakdown-dot {{ background: var(--surgery-accent); }}
        .medicine-row .breakdown-dot {{ background: var(--medicine-accent); }}
        .pathology-row .breakdown-dot {{ background: var(--pathology-accent); }}

        /* =============================================================
           5. FIXED-HEIGHT PORTAL CARDS (IDENTICAL ANATOMY, BALANCED GRID)
           ============================================================= */
        .portal-cards-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            align-items: stretch;
            margin-bottom: 24px;
        }}

        .portal-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 22px;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow-sm);
            transition: border-color 0.2s ease, transform 0.2s ease;
        }}
        .portal-card:hover {{
            border-color: var(--border-strong);
            transform: translateY(-2px);
        }}

        /* Subtle Corner Watermarks */
        .corner-watermark {{
            position: absolute;
            bottom: -15px;
            right: -15px;
            width: 120px;
            height: 120px;
            pointer-events: none;
            opacity: 0.04;
            z-index: 0;
        }}

        /* 1. Header Row */
        .card-header-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
            z-index: 1;
        }}
        .card-paper-tag {{
            font-size: 0.72rem;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: var(--radius-pill);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            white-space: nowrap;
        }}
        .card-essay-count {{
            display: flex;
            align-items: baseline;
            gap: 4px;
            font-family: 'JetBrains Mono', monospace;
        }}
        .essay-count-num {{
            font-size: 1.35rem;
            font-weight: 800;
            color: var(--text-primary);
            line-height: 1;
        }}
        .essay-count-label {{
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
        }}

        /* 2. Identity Row */
        .card-identity-row {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 10px;
            z-index: 1;
        }}
        .card-logo-box {{
            width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
        }}
        .card-logo-box svg {{
            width: 44px;
            height: 44px;
            display: block;
        }}
        .card-title-stack {{
            display: flex;
            flex-direction: column;
            line-height: 1.2;
        }}
        .card-portal-title {{
            font-size: 1.38rem;
            font-weight: 700;
            color: var(--text-primary);
        }}
        .card-specialty-sub {{
            font-size: 0.74rem;
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        /* 3. Description Clamped to 3 Lines */
        .card-desc {{
            font-size: 0.88rem;
            color: var(--text-secondary);
            line-height: 1.45;
            margin-bottom: 12px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 4.45em;
            max-height: 4.45em;
            z-index: 1;
        }}

        /* 4. Single Common Feature Chips Row (Same 5 chips everywhere) */
        .card-features-row {{
            display: flex;
            align-items: center;
            gap: 5px;
            margin-bottom: 14px;
            flex-wrap: wrap;
            z-index: 1;
        }}
        .feature-chip {{
            font-size: 0.72rem;
            font-weight: 600;
            padding: 2px 7px;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            white-space: nowrap;
        }}

        /* 5. Fixed-Height Topic Preview Area (2x2 Grid + View All Button) */
        .card-topic-preview-box {{
            margin-bottom: 14px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            z-index: 1;
        }}
        .preview-bubbles-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
        }}
        .preview-bubble {{
            display: block;
            padding: 6px 9px;
            border-radius: 6px;
            font-size: 0.76rem;
            font-weight: 600;
            text-decoration: none;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            border: 1px solid var(--border-color);
            background: rgba(255, 255, 255, 0.03);
            color: var(--text-secondary);
            transition: all 0.15s ease;
        }}
        .preview-bubble:hover {{
            background: rgba(255, 255, 255, 0.06);
            color: var(--text-primary);
            border-color: var(--border-strong);
        }}
        .card-surgery .preview-bubble:hover {{ border-color: var(--surgery-accent); color: var(--surgery-tag-text); }}
        .card-medicine .preview-bubble:hover {{ border-color: var(--medicine-accent); color: var(--medicine-tag-text); }}
        .card-pathology .preview-bubble:hover {{ border-color: var(--pathology-accent); color: var(--pathology-tag-text); }}

        .btn-view-all-topics {{
            width: 100%;
            height: 32px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 700;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.15s ease;
        }}
        .btn-view-all-topics:hover {{
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-primary);
            border-color: var(--border-strong);
        }}
        .card-surgery .btn-view-all-topics:hover {{ border-color: var(--surgery-accent); color: var(--surgery-tag-text); }}
        .card-medicine .btn-view-all-topics:hover {{ border-color: var(--medicine-accent); color: var(--medicine-tag-text); }}
        .card-pathology .btn-view-all-topics:hover {{ border-color: var(--pathology-accent); color: var(--pathology-tag-text); }}

        /* 6. Card Progress Row */
        .card-progress-row {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 14px;
            font-size: 0.74rem;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-muted);
            z-index: 1;
        }}
        .card-track {{
            flex: 1;
            height: 5px;
            background: rgba(255, 255, 255, 0.06);
            border-radius: var(--radius-pill);
            overflow: hidden;
        }}
        .card-fill {{
            height: 100%;
            border-radius: var(--radius-pill);
            transition: width 0.4s ease;
        }}
        .card-surgery .card-fill {{ background: var(--surgery-accent); }}
        .card-medicine .card-fill {{ background: var(--medicine-accent); }}
        .card-pathology .card-fill {{ background: var(--pathology-accent); }}

        /* 7. Action Dock (Pinned Flush via margin-top: auto) */
        .card-actions-dock {{
            margin-top: auto;
            display: flex;
            gap: 8px;
            padding-top: 12px;
            border-top: 1px solid var(--border-subtle);
            z-index: 1;
        }}
        .btn-launch {{
            flex: 1;
            height: 44px;
            padding: 0 16px;
            border-radius: var(--radius-sm);
            color: #ffffff;
            font-size: 0.88rem;
            font-weight: 700;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            border: none;
            cursor: pointer;
            transition: transform 0.15s ease, filter 0.15s ease;
        }}
        .btn-launch:hover {{
            transform: translateY(-1px);
            filter: brightness(1.08);
        }}
        .card-surgery .btn-launch {{ background: var(--surgery-btn); }}
        .card-medicine .btn-launch {{ background: var(--medicine-btn); }}
        .card-pathology .btn-launch {{ background: var(--pathology-btn); }}

        .btn-pdf {{
            height: 44px;
            padding: 0 14px;
            border-radius: var(--radius-sm);
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            font-size: 0.82rem;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.15s ease;
        }}
        .btn-pdf:hover {{
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-primary);
            border-color: var(--border-strong);
            transform: translateY(-1px);
        }}

        /* Distinct Portal Accents */
        .card-surgery .card-paper-tag {{ background: var(--surgery-tag-bg); color: var(--surgery-tag-text); border: 1px solid var(--surgery-tag-border); }}
        .card-medicine .card-paper-tag {{ background: var(--medicine-tag-bg); color: var(--medicine-tag-text); border: 1px solid var(--medicine-tag-border); }}
        .card-pathology .card-paper-tag {{ background: var(--pathology-tag-bg); color: var(--pathology-tag-text); border: 1px solid var(--pathology-tag-border); }}

        /* =============================================================
           6. TOPIC PANEL OVERLAY (DESKTOP POPOVER & MOBILE BOTTOM SHEET)
           ============================================================= */
        .topic-panel-scrim {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.65);
            backdrop-filter: none;
            -webkit-backdrop-filter: none;
            z-index: 1090;
        }}
        .topic-panel-scrim.open {{
            display: block;
        }}

        .topic-panel {{
            display: none;
            background: var(--bg-surface-elevated);
            border: 1px solid var(--border-strong);
            box-shadow: var(--shadow-lg);
            flex-direction: column;
            z-index: 1100;
            overflow: hidden;
            box-sizing: border-box;
        }}
        .topic-panel.open {{
            display: flex;
        }}

        /* Desktop Popover Style (>=768px) */
        @media (min-width: 768px) {{
            .topic-panel {{
                position: fixed;
                border-radius: var(--radius-md);
                width: min(420px, calc(100vw - 32px));
                max-height: min(70vh, 520px);
                overscroll-behavior: contain;
                animation: popoverFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            }}
            .bottom-sheet-handle {{
                display: none;
            }}
        }}

        @keyframes popoverFadeIn {{
            from {{ opacity: 0; transform: scale(0.97); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}

        /* Mobile Bottom Sheet Style (<768px) */
        @media (max-width: 767px) {{
            .topic-panel {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                width: 100%;
                max-height: 85dvh;
                border-radius: 20px 20px 0 0;
                border-bottom: none;
                animation: sheetSlideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1);
                padding-bottom: env(safe-area-inset-bottom, 16px);
            }}
            .bottom-sheet-handle {{
                width: 36px;
                height: 4px;
                border-radius: 999px;
                background: var(--border-strong);
                margin: 10px auto 4px auto;
                cursor: grab;
                flex-shrink: 0;
            }}
        }}

        @keyframes sheetSlideUp {{
            from {{ transform: translateY(100%); }}
            to {{ transform: translateY(0); }}
        }}

        /* Panel Internal Anatomy */
        .panel-header {{
            padding: 14px 18px 10px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border-subtle);
            flex-shrink: 0;
        }}
        .panel-header-info {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .panel-paper-badge {{
            font-size: 0.70rem;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: var(--radius-pill);
            text-transform: uppercase;
        }}
        .panel-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-primary);
        }}
        .panel-count {{
            font-size: 0.74rem;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-muted);
        }}
        .panel-close-btn {{
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            transition: all 0.15s ease;
        }}
        .panel-close-btn:hover {{
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
        }}

        /* Filter Box */
        .panel-filter-row {{
            padding: 10px 18px;
            border-bottom: 1px solid var(--border-subtle);
            position: relative;
            flex-shrink: 0;
        }}
        .panel-filter-input {{
            width: 100%;
            height: 36px;
            padding: 0 32px 0 12px;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            color: var(--text-primary);
            font-size: 0.84rem;
            font-family: inherit;
            outline: none;
            box-sizing: border-box;
        }}
        .panel-filter-input:focus {{
            border-color: var(--border-strong);
        }}
        .filter-clear-btn {{
            position: absolute;
            right: 26px;
            top: 50%;
            transform: translateY(-50%);
            background: transparent;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 0.9rem;
            padding: 4px;
        }}

        /* Topics Scroll List */
        .panel-topics-list {{
            flex: 1;
            overflow-y: auto;
            padding: 8px 12px;
            display: flex;
            flex-direction: column;
            gap: 4px;
            overscroll-behavior: contain;
        }}
        .panel-topic-row {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 12px;
            border-radius: var(--radius-sm);
            text-decoration: none;
            color: var(--text-secondary);
            font-size: 0.84rem;
            min-height: 44px;
            box-sizing: border-box;
            transition: all 0.15s ease;
            border: 1px solid transparent;
        }}
        .panel-topic-row:hover {{
            background: rgba(255, 255, 255, 0.04);
            color: var(--text-primary);
            border-color: var(--border-subtle);
        }}
        .panel-topic-num {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            color: var(--text-muted);
            width: 22px;
            flex-shrink: 0;
        }}
        .panel-topic-title {{
            flex: 1;
            line-height: 1.35;
        }}
        .panel-topic-tick {{
            font-size: 0.85rem;
            color: var(--text-muted);
            opacity: 0.4;
            flex-shrink: 0;
        }}
        .panel-topic-tick.completed {{
            color: var(--accent-emerald);
            opacity: 1;
            font-weight: 700;
        }}

        .panel-empty-state {{
            padding: 28px 16px;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
        .panel-empty-state button {{
            margin-top: 10px;
            padding: 6px 12px;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            cursor: pointer;
        }}

        .panel-footer-bar {{
            padding: 10px 18px;
            border-top: 1px solid var(--border-subtle);
            display: flex;
            justify-content: flex-end;
            flex-shrink: 0;
        }}
        .panel-launch-link {{
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--text-primary);
            text-decoration: none;
        }}
        .panel-launch-link:hover {{
            text-decoration: underline;
        }}

        /* =============================================================
           7. QUICK REFERENCE MODAL (LAB NORMS, CUTOFFS, 15-MARK RUBRICS)
           ============================================================= */
        .lab-modal-overlay {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: none;
            -webkit-backdrop-filter: none;
            z-index: 2000;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .lab-modal-overlay.open {{
            display: flex;
        }}
        .lab-modal-card {{
            background: var(--bg-surface-elevated);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-md);
            max-width: 860px;
            width: 100%;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: var(--shadow-lg);
        }}
        .lab-modal-header {{
            padding: 16px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border-color);
        }}
        .lab-modal-tabs {{
            display: flex;
            border-bottom: 1px solid var(--border-color);
            background: rgba(0, 0, 0, 0.15);
            overflow-x: auto;
        }}
        .lab-tab-btn {{
            padding: 11px 18px;
            background: transparent;
            border: none;
            border-bottom: 2px solid transparent;
            color: var(--text-muted);
            font-size: 0.84rem;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
        }}
        .lab-tab-btn.active {{
            color: var(--text-primary);
            border-bottom-color: var(--surgery-accent);
            background: rgba(255, 255, 255, 0.03);
        }}
        .lab-modal-body {{
            padding: 20px;
            overflow-y: auto;
            flex: 1;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.84rem;
        }}
        .data-table th, .data-table td {{
            padding: 10px 14px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
            vertical-align: top;
        }}
        .data-table th {{
            font-weight: 700;
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.02);
            position: sticky;
            top: 0;
        }}

        /* 15-Mark Rubric Grid Inside Modal */
        .rubric-modal-wrap {{
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}
        .rubric-segmented-bar {{
            display: inline-flex;
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: 3px;
            gap: 4px;
            align-self: flex-start;
        }}
        .rubric-tab-btn {{
            padding: 6px 14px;
            border-radius: 6px;
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 0.80rem;
            font-weight: 700;
            cursor: pointer;
        }}
        .rubric-tab-btn.active {{
            background: var(--text-primary);
            color: var(--bg-base);
        }}
        .rubric-steps-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }}
        .rubric-step-box {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .rubric-step-num {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.70rem;
            font-weight: 700;
            color: var(--surgery-accent);
        }}
        .rubric-step-name {{
            font-size: 0.84rem;
            font-weight: 700;
            color: var(--text-primary);
        }}
        .rubric-step-marks {{
            font-size: 0.74rem;
            color: var(--text-muted);
        }}

        /* =============================================================
           8. CMDK COMMAND PALETTE OVERLAY


        /* =============================================================
           9. COMPACT FOOTER WITH QUICK-REFERENCE SHORTCUTS
           ============================================================= */
        .hub-footer {{
            border-top: 1px solid var(--border-color);
            background: var(--bg-surface);
            padding: 24px;
            margin-top: auto;
        }}
        .footer-inner {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}
        .footer-links-row {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 0.82rem;
        }}
        .footer-link {{
            color: var(--text-muted);
            text-decoration: none;
            transition: color 0.15s ease;
        }}
        .footer-link:hover {{
            color: var(--text-primary);
        }}
        .footer-meta-row {{
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            gap: 8px;
            font-size: 0.75rem;
            color: var(--text-muted);
            flex-wrap: wrap;
        }}

        /* =============================================================
           10. RESPONSIVE BREAKPOINTS & ADAPTIVE LAYOUTS
           ============================================================= */
        /* Desktop Large (>=1024px) */
        @media (min-width: 1024px) {{
            .mobile-search-btn,
            .mobile-overflow-btn,
            .search-back-btn {{
                display: none !important;
            }}
            .header-search-wrap {{
                display: flex;
                flex: 1 1 auto;
                max-width: 380px;
                min-width: 0;
            }}
            .header-right-tools {{
                display: flex;
            }}
        }}

        /* Tablet Portrait (768px - 1023px) */
        @media (max-width: 1023px) and (min-width: 768px) {{
            .brand-sub {{
                display: none;
            }}
            .mobile-search-btn,
            .mobile-overflow-btn,
            .search-back-btn {{
                display: none !important;
            }}
            .header-search-wrap {{
                display: flex;
                flex: 1 1 auto;
                max-width: 240px;
                min-width: 0;
                margin: 0 10px;
            }}
            .header-right-tools {{
                display: flex;
                gap: 6px;
            }}
            [data-testid="quick-reference"] span {{
                display: none;
            }}
            .timer-nav-pill #navTimerStateText {{
                display: none;
            }}
            .portal-cards-grid {{
                grid-template-columns: 1fr;
                gap: 16px;
            }}
        }}

        /* Mobile (<768px) */
        @media (max-width: 767px) {{
            .header-solid {{
                padding: 0 14px;
                padding-left: max(14px, env(safe-area-inset-left));
                padding-right: max(14px, env(safe-area-inset-right));
            }}
            .brand-link {{
                min-width: 0;
                flex-shrink: 1;
            }}
            .brand-wordmark-group {{
                min-width: 0;
            }}
            .brand-wordmark {{
                font-size: 1.05rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .brand-sub {{
                display: none;
            }}
            .header-search-wrap {{
                display: none;
            }}
            .header-right-tools {{
                display: none;
            }}
            .mobile-search-btn,
            .mobile-overflow-btn {{
                display: inline-flex;
            }}

            /* Search Expanded Mode on Mobile */
            .header-solid.search-expanded .brand-link,
            .header-solid.search-expanded .mobile-search-btn,
            .header-solid.search-expanded .mobile-overflow-btn {{
                display: none !important;
            }}
            .header-solid.search-expanded .header-search-wrap {{
                display: flex !important;
                flex: 1 1 100% !important;
                max-width: 100% !important;
                margin: 0 !important;
                min-width: 0 !important;
            }}
            .header-solid.search-expanded .search-back-btn {{
                display: inline-flex !important;
            }}
            .header-solid.search-expanded .hub-search-results {{
                position: fixed;
                top: 64px;
                left: 0;
                right: 0;
                width: 100%;
                max-height: calc(100dvh - 64px);
                border-radius: 0;
                border-top: none;
            }}

            .main-content {{
                padding: 16px 14px 32px 14px;
            }}
            .hero-title {{
                font-size: 1.55rem;
                line-height: 1.25;
            }}
            .hero-sub {{
                font-size: 0.88rem;
                line-height: 1.45;
            }}
            .portal-cards-grid {{
                grid-template-columns: 1fr;
                gap: 16px;
            }}
            .portal-card {{
                padding: 18px 16px;
            }}
            .corner-watermark {{
                top: 10px;
                right: 10px;
                bottom: auto;
                left: auto;
                opacity: 0.035;
                pointer-events: none;
                width: 80px;
                height: 80px;
            }}

            /* Compact 2-row progress strip */
            .progress-strip-container {{
                padding: 12px 14px;
            }}
            .progress-strip-inner {{
                flex-direction: column;
                height: auto;
                align-items: stretch;
                gap: 8px;
            }}
            .progress-strip-left {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 4px;
                width: 100%;
                min-width: 0;
            }}
            .progress-strip-track {{
                width: 100%;
                height: 7px;
            }}
            .progress-strip-right {{
                font-size: 0.78rem;
                white-space: normal;
                word-break: break-word;
            }}

            /* Card Actions Dock: 48px stacked primary buttons */
            .card-actions-dock {{
                flex-direction: column;
                gap: 8px;
            }}
            .btn-launch, .btn-pdf {{
                width: 100%;
                height: 48px;
                min-height: 48px;
                font-size: 0.92rem;
                border-radius: var(--radius-sm);
            }}

            /* Topic preview bubbles on phones: exactly 2 bubbles */
            .preview-bubbles-grid {{
                grid-template-columns: 1fr 1fr;
                gap: 6px;
            }}
            .preview-bubbles-grid .preview-bubble:nth-child(n+3) {{
                display: none;
            }}

            /* Minimum 12px text across mobile cards */
            .card-paper-tag, .card-specialty-sub, .feature-chip, .preview-bubble, .essay-count-label {{
                font-size: 0.75rem; /* 12px */
            }}
        }}

        /* Anchored Popover for 480px - 767px */
        @media (min-width: 480px) and (max-width: 767px) {{
            .hub-overflow-menu {{
                position: absolute;
                top: calc(100% + 8px);
                right: 14px;
                width: 320px;
                border-radius: var(--radius-md);
                padding: 16px;
                transform-origin: top right;
                animation: popoverFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            }}
        }}

        /* Bottom Sheet for <480px */
        @media (max-width: 479px) {{
            .brand-wordmark {{
                max-width: 150px;
                font-size: 0.98rem;
            }}
            .hub-overflow-menu {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                width: 100%;
                max-height: 85dvh;
                border-radius: 20px 20px 0 0;
                border-bottom: none;
                padding: 16px 18px env(safe-area-inset-bottom, 20px) 18px;
                animation: sheetSlideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1);
                overflow-y: auto;
            }}
        }}

        /* Very Small Phones (<=359px down to 280px) */
        @media (max-width: 359px) {{
            .header-solid {{
                padding: 0 10px;
            }}
            .brand-wordmark {{
                max-width: 110px;
                font-size: 0.88rem;
            }}
            .brand-logo-tile {{
                width: 32px;
                height: 32px;
            }}
            .mobile-search-btn, .mobile-overflow-btn {{
                width: 40px;
                height: 40px;
            }}
            .progress-strip-left {{
                flex-direction: column;
                align-items: flex-start;
                gap: 2px;
            }}
            .preview-bubbles-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        /* Respect Reduced Motion */
        @media (prefers-reduced-motion: reduce) {{
            *, ::before, ::after {{
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }}
        }}
    </style>
</head>
<body>

    <!-- 1. SOLID FULL-BLEED STICKY HEADER -->
    <header class="header-solid" data-testid="hub-header" id="hubHeader">
        <a href="#" class="brand-link" onclick="window.scrollTo({{top:0, behavior:'smooth'}})" aria-label="BDS Clinical Vault Home">
            <div class="brand-logo-tile">
                <img src="favicon.svg" width="26" height="26" alt="BDS Clinical Vault Shield Logo">
            </div>
            <div class="brand-wordmark-group">
                <span class="brand-wordmark cinzel-brand">BDS CLINICAL VAULT</span>
                <span class="brand-sub">3rd Year University Command Suite</span>
            </div>
        </a>

        <!-- Ordinary Search with Inline Dropdown -->
        <div class="header-search-wrap" id="hubSearchContainer">
            <button type="button" class="search-back-btn" id="hubSearchBackBtn" onclick="closeMobileSearch()" aria-label="Back to navigation">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
            </button>
            <div class="hub-search-box">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                <input type="search" id="hubSearchInput" class="hub-search-input" data-testid="search" placeholder="Search essays, spotters, cutoffs... (/)" autocomplete="off" oninput="onHubSearchInput(this.value)" onfocus="onHubSearchFocus()">
                <button type="button" class="hub-search-clear" id="hubSearchClear" style="display:none;" onclick="clearHubSearch()" aria-label="Clear search">✕</button>
            </div>
            <div class="hub-search-results" id="hubSearchResults" style="display:none;"></div>
        </div>

        <!-- Desktop Right Nav Tools -->
        <div class="header-right-tools">
            <!-- Focus Study Timer -->
            <div class="focus-timer-container">
                <button class="nav-btn timer-nav-pill" id="navTimerPill" data-testid="focus-timer" onclick="toggleTimerPopover(event)" title="Toggle Focus Study Timer" aria-haspopup="dialog" aria-expanded="false">
                    <span class="timer-chip-dot"></span>
                    <span id="navTimerDisplay" class="mono-num">25:00</span>
                    <span id="navTimerStateText">Focus</span>
                </button>
                <div class="timer-popover-card" id="timerPopover" onclick="event.stopPropagation()">
                    <div class="timer-popover-header" id="timerModeLabel">High-Yield Focus Block</div>
                    <div class="timer-popover-digits" id="timerMainDigits">25:00</div>
                    <div class="timer-popover-controls">
                        <button class="timer-ctrl-btn primary" id="timerStartBtn" onclick="toggleTimer()">Start Focus</button>
                        <button class="timer-ctrl-btn" onclick="resetTimer(25)">25m</button>
                        <button class="timer-ctrl-btn" onclick="resetTimer(50)">50m</button>
                    </div>
                </div>
            </div>

            <!-- Quick Reference Modal Trigger -->
            <button class="nav-btn" data-testid="quick-reference" onclick="toggleLabModal('norm')" title="Quick Reference &amp; Clinical Safety Margins">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/><path d="M6 6h10M6 10h10"/></svg>
                <span>Quick Reference</span>
            </button>

            <!-- Theme Toggle -->
            <button class="nav-btn" data-testid="theme-toggle" id="themeBtn" onclick="toggleTheme()" aria-label="Toggle Dark and Light Mode" title="Toggle Theme">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
            </button>
        </div>

        <!-- Mobile Action Buttons (<768px) -->
        <button type="button" class="mobile-search-btn" id="hubSearchIconBtn" onclick="openMobileSearch()" aria-label="Open search">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        </button>
        <button type="button" class="mobile-overflow-btn" id="hubOverflowBtn" onclick="toggleHubOverflow(event)" aria-label="Open menu" aria-haspopup="dialog" aria-expanded="false">
            <span class="overflow-timer-dot" id="overflowTimerDot"></span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><circle cx="5" cy="12" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="19" cy="12" r="2"/></svg>
        </button>

        <!-- Mobile Overflow Scrim & Menu -->
        <div class="hub-overflow-scrim" id="hubOverflowScrim" onclick="closeHubOverflow()"></div>
        <div class="hub-overflow-menu" id="hubOverflowMenu" role="dialog" aria-modal="true" aria-labelledby="overflowMenuTitle">
            <div class="overflow-header-row">
                <span class="overflow-menu-title" id="overflowMenuTitle">Ecosystem Controls</span>
                <button type="button" class="overflow-close-btn" id="hubOverflowCloseBtn" onclick="closeHubOverflow()" aria-label="Close menu">&times;</button>
            </div>
            
            <!-- Focus Study Timer Card -->
            <div class="overflow-timer-card">
                <div class="overflow-timer-header">
                    <span>Study Focus Block</span>
                    <span id="overflowTimerState" style="color:var(--text-muted);">25m Preset</span>
                </div>
                <div class="overflow-timer-digits mono-num" id="overflowTimerDigits">25:00</div>
                <div class="overflow-timer-actions">
                    <button type="button" class="overflow-timer-btn primary" id="overflowTimerStartBtn" onclick="toggleTimer()">Start Focus</button>
                    <button type="button" class="overflow-timer-btn" onclick="resetTimer(25)">25m</button>
                    <button type="button" class="overflow-timer-btn" onclick="resetTimer(50)">50m</button>
                </div>
            </div>

            <!-- Quick Reference Action -->
            <button type="button" class="overflow-action-row" onclick="closeHubOverflow(); toggleLabModal('norm')">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/><path d="M6 6h10M6 10h10"/></svg>
                <span>Quick Reference &amp; Lab Norms</span>
            </button>

            <!-- Theme Toggle Action -->
            <button type="button" class="overflow-action-row" id="overflowThemeBtn" onclick="toggleTheme()">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
                <span id="overflowThemeLabel">Toggle Theme</span>
            </button>
        </div>
    </header>

    <!-- 2. MAIN HUB CONTENT -->
    <main class="main-content" id="appRoot">
        <!-- Hero Banner -->
        <section class="hero-banner">
            <div class="hero-trust-bar">
                <span class="trust-badge">Accredited Standard</span>
                <span>3rd-year university syllabus · {total_essays} essays · Accredited</span>
            </div>
            <h1 class="hero-title editorial-heading">Dental Surgery &amp; Clinical Sciences</h1>
            <p class="hero-sub">Consolidated high-yield examination portals: 15-mark university essay blueprints, bedside emergency protocols, microscopic spotters, and continuous audio walk islands.</p>
        </section>

        <!-- 3. SLIM OVERALL PROGRESS STRIP (<=56px) -->
        <section class="progress-strip-container" data-testid="progress-strip">
            <div class="progress-strip-inner">
                <div class="progress-strip-left">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span class="progress-pulse-dot"></span>
                        <span>Overall Progress</span>
                    </div>
                    <div class="progress-strip-right">
                        <span id="progressOverallStats">0 of {total_essays} completed · 0%</span>
                    </div>
                </div>
                <div class="progress-strip-track" id="progressStripTrack" title="Click for paper breakdown">
                    <div class="progress-strip-segment segment-surgery" data-testid="progress-strip-segment-surgery" style="width: calc(23 / 63 * 100%);">
                        <div class="segment-fill" id="stripFillSurgery" style="width: 0%;"></div>
                    </div>
                    <div class="progress-strip-segment segment-medicine" data-testid="progress-strip-segment-medicine" style="width: calc(20 / 63 * 100%);">
                        <div class="segment-fill" id="stripFillMedicine" style="width: 0%;"></div>
                    </div>
                    <div class="progress-strip-segment segment-pathology" data-testid="progress-strip-segment-pathology" style="width: calc(20 / 63 * 100%);">
                        <div class="segment-fill" id="stripFillPathology" style="width: 0%;"></div>
                    </div>
                </div>
            </div>

            <!-- Hover/Tap Breakdown Tooltip -->
            <div class="progress-breakdown-popover" id="progressBreakdownPopover">
                <div class="breakdown-row surgery-row">
                    <span class="breakdown-dot"></span>
                    <span>Surgery: <strong id="breakdownValSurgery">0/23</strong></span>
                </div>
                <div class="breakdown-row medicine-row">
                    <span class="breakdown-dot"></span>
                    <span>Medicine: <strong id="breakdownValMedicine">0/20</strong></span>
                </div>
                <div class="breakdown-row pathology-row">
                    <span class="breakdown-dot"></span>
                    <span>Pathology: <strong id="breakdownValPathology">0/20</strong></span>
                </div>
            </div>
        </section>

        <!-- 4. FIXED-HEIGHT PORTAL CARDS (3 COLUMNS AT DESKTOP) -->
        <div class="portal-cards-grid">
            
            <!-- CARD 1: GENERAL SURGERY PRO -->
            <div class="portal-card card-surgery" id="surgery" data-testid="hub-card-surgery">
                <svg class="corner-watermark" viewBox="0 0 100 100" fill="none" stroke="currentColor">
                    <circle cx="50" cy="50" r="40" stroke-width="1.5" stroke-dasharray="4 4"/>
                    <line x1="50" y1="10" x2="50" y2="90" stroke-width="1.5"/>
                    <line x1="10" y1="50" x2="90" y2="50" stroke-width="1.5"/>
                </svg>

                <div class="card-header-row">
                    <span class="card-paper-tag">Paper I · Surgery</span>
                    <div class="card-essay-count">
                        <span class="essay-count-num">{len(surgery_topics)}</span>
                        <span class="essay-count-label">essays</span>
                    </div>
                </div>

                <div class="card-identity-row">
                    <div class="card-logo-box" title="General Surgery Pro">
                        <svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
                            <defs>
                                <linearGradient id="surgBgCard" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" stop-color="#0f766e"/>
                                    <stop offset="100%" stop-color="#042f2e"/>
                                </linearGradient>
                            </defs>
                            <rect width="512" height="512" rx="112" fill="url(#surgBgCard)" stroke="rgba(255,255,255,0.20)" stroke-width="16"/>
                            <g fill="none" stroke="#f8fafc" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M128 384 L244 268" stroke-width="28"/>
                                <line x1="148" y1="336" x2="164" y2="352" stroke="#5eead4" stroke-width="10"/>
                                <line x1="172" y1="312" x2="188" y2="328" stroke="#5eead4" stroke-width="10"/>
                                <line x1="196" y1="288" x2="212" y2="304" stroke="#5eead4" stroke-width="10"/>
                                <path d="M236 276 L252 260" stroke="#f8fafc" stroke-width="34"/>
                                <path d="M244 268 L384 128 C416 148 400 200 364 236 C324 276 276 280 244 268 Z" fill="#5eead4" fill-opacity="0.25" stroke="#ffffff" stroke-width="24"/>
                                <line x1="272" y1="240" x2="324" y2="188" stroke="#5eead4" stroke-width="12"/>
                            </g>
                        </svg>
                    </div>
                    <div class="card-title-stack">
                        <h2 class="card-portal-title editorial-heading">Surgery Pro</h2>
                        <span class="card-specialty-sub">Clinical Surgical Oncology &amp; Trauma</span>
                    </div>
                </div>

                <p class="card-desc">
                    Surgical anatomy, wound healing, shock resuscitation, Parkland burns formula, cervical triangles, and thyroid oncology monographs.
                </p>

                <div class="card-features-row">
                    <span class="feature-chip">🎧 Voice Walk</span>
                    <span class="feature-chip">⏱️ Exam Simulator</span>
                    <span class="feature-chip">🔬 Spotters</span>
                    <span class="feature-chip">🃏 Flashcards</span>
                    <span class="feature-chip">📄 Monograph</span>
                </div>

                <div class="card-topic-preview-box">
                    <div class="preview-bubbles-grid">
                        <a href="{surgery_previews[0]['url']}" target="_blank" class="preview-bubble" title="{surgery_previews[0]['title']}" data-testid="hub-topic-bubble">{get_short_title(surgery_previews[0]['title'])}</a>
                        <a href="{surgery_previews[1]['url']}" target="_blank" class="preview-bubble" title="{surgery_previews[1]['title']}" data-testid="hub-topic-bubble">{get_short_title(surgery_previews[1]['title'])}</a>
                        <a href="{surgery_previews[2]['url']}" target="_blank" class="preview-bubble" title="{surgery_previews[2]['title']}" data-testid="hub-topic-bubble">{get_short_title(surgery_previews[2]['title'])}</a>
                        <a href="{surgery_previews[3]['url']}" target="_blank" class="preview-bubble" title="{surgery_previews[3]['title']}" data-testid="hub-topic-bubble">{get_short_title(surgery_previews[3]['title'])}</a>
                    </div>
                    <button class="btn-view-all-topics" data-testid="hub-view-all" onclick="openTopicPanel('surgery', this)" aria-haspopup="dialog" aria-expanded="false" aria-controls="topicPanel">
                        View all {len(surgery_topics)} topics ▸
                    </button>
                </div>

                <div class="card-progress-row">
                    <div class="card-track">
                        <div class="card-fill" id="cardProgressFillSurgery" style="width: 0%;"></div>
                    </div>
                    <span id="cardProgressTextSurgery">0 of {len(surgery_topics)} done</span>
                </div>

                <div class="card-actions-dock">
                    <a href="https://krrish41.github.io/general-surgery/" target="_blank" class="btn-launch" data-testid="launch-portal">
                        Launch Portal →
                    </a>
                    <a href="https://krrish41.github.io/general-surgery/General_Surgery_Master_Notes.pdf" target="_blank" class="btn-pdf" data-testid="portal-pdf" title="Download Master PDF">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
                        PDF
                    </a>
                </div>
            </div>

            <!-- CARD 2: GENERAL MEDICINE PRO -->
            <div class="portal-card card-medicine" id="medicine" data-testid="hub-card-medicine">
                <svg class="corner-watermark" viewBox="0 0 100 100" fill="none" stroke="currentColor">
                    <path d="M0 50h25l5-15 10 35 10-40 10 30 5-10h35" stroke-width="2" stroke-linecap="round"/>
                </svg>

                <div class="card-header-row">
                    <span class="card-paper-tag">Paper II · Medicine</span>
                    <div class="card-essay-count">
                        <span class="essay-count-num">{len(medicine_topics)}</span>
                        <span class="essay-count-label">essays</span>
                    </div>
                </div>

                <div class="card-identity-row">
                    <div class="card-logo-box" title="General Medicine Pro">
                        <svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
                            <defs>
                                <linearGradient id="medBgCard" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" stop-color="#1e3a8a"/>
                                    <stop offset="100%" stop-color="#0f172a"/>
                                </linearGradient>
                            </defs>
                            <rect width="512" height="512" rx="112" fill="url(#medBgCard)" stroke="rgba(255,255,255,0.20)" stroke-width="16"/>
                            <g fill="none" stroke="#f8fafc" stroke-linecap="round" stroke-linejoin="round" stroke-width="26">
                                <circle cx="180" cy="130" r="14" fill="#93c5fd" stroke="none"/>
                                <circle cx="332" cy="130" r="14" fill="#93c5fd" stroke="none"/>
                                <path d="M180 144 V180 C180 220 220 250 256 250 C292 250 332 220 332 180 V144"/>
                                <path d="M256 250 V290 C256 360 190 390 190 340 C190 290 290 300 290 370 C290 410 320 410 336 410"/>
                                <circle cx="356" cy="410" r="30" fill="#93c5fd" fill-opacity="0.25" stroke="#ffffff" stroke-width="24"/>
                                <circle cx="356" cy="410" r="12" fill="#38bdf8" stroke="none"/>
                            </g>
                        </svg>
                    </div>
                    <div class="card-title-stack">
                        <h2 class="card-portal-title editorial-heading">Medicine Pro</h2>
                        <span class="card-specialty-sub">Internal Medicine &amp; Therapeutics</span>
                    </div>
                </div>

                <p class="card-desc">
                    Internal medicine diagnostics: modified Duke criteria for IE, Jones criteria, viral hepatitis, diabetic ketoacidosis, and chairside pharmacotherapy.
                </p>

                <div class="card-features-row">
                    <span class="feature-chip">🎧 Voice Walk</span>
                    <span class="feature-chip">⏱️ Exam Simulator</span>
                    <span class="feature-chip">🔬 Spotters</span>
                    <span class="feature-chip">🃏 Flashcards</span>
                    <span class="feature-chip">📄 Monograph</span>
                </div>

                <div class="card-topic-preview-box">
                    <div class="preview-bubbles-grid">
                        <a href="{medicine_previews[0]['url']}" target="_blank" class="preview-bubble" title="{medicine_previews[0]['title']}" data-testid="hub-topic-bubble">{get_short_title(medicine_previews[0]['title'])}</a>
                        <a href="{medicine_previews[1]['url']}" target="_blank" class="preview-bubble" title="{medicine_previews[1]['title']}" data-testid="hub-topic-bubble">{get_short_title(medicine_previews[1]['title'])}</a>
                        <a href="{medicine_previews[2]['url']}" target="_blank" class="preview-bubble" title="{medicine_previews[2]['title']}" data-testid="hub-topic-bubble">{get_short_title(medicine_previews[2]['title'])}</a>
                        <a href="{medicine_previews[3]['url']}" target="_blank" class="preview-bubble" title="{medicine_previews[3]['title']}" data-testid="hub-topic-bubble">{get_short_title(medicine_previews[3]['title'])}</a>
                    </div>
                    <button class="btn-view-all-topics" data-testid="hub-view-all" onclick="openTopicPanel('medicine', this)" aria-haspopup="dialog" aria-expanded="false" aria-controls="topicPanel">
                        View all {len(medicine_topics)} topics ▸
                    </button>
                </div>

                <div class="card-progress-row">
                    <div class="card-track">
                        <div class="card-fill" id="cardProgressFillMedicine" style="width: 0%;"></div>
                    </div>
                    <span id="cardProgressTextMedicine">0 of {len(medicine_topics)} done</span>
                </div>

                <div class="card-actions-dock">
                    <a href="https://krrish41.github.io/General-Medicine/" target="_blank" class="btn-launch" data-testid="launch-portal">
                        Launch Portal →
                    </a>
                    <a href="https://krrish41.github.io/General-Medicine/General_Medicine_Master_Notes.pdf" target="_blank" class="btn-pdf" data-testid="portal-pdf" title="Download Master PDF">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
                        PDF
                    </a>
                </div>
            </div>

            <!-- CARD 3: ORAL PATHOLOGY PRO -->
            <div class="portal-card card-pathology" id="pathology" data-testid="hub-card-pathology">
                <svg class="corner-watermark" viewBox="0 0 100 100" fill="none" stroke="currentColor">
                    <polygon points="50,15 80,32 80,68 50,85 20,68 20,32" stroke-width="1.5"/>
                    <circle cx="50" cy="50" r="14" stroke-width="1.5" stroke-dasharray="3 3"/>
                </svg>

                <div class="card-header-row">
                    <span class="card-paper-tag">Paper III · Pathology</span>
                    <div class="card-essay-count">
                        <span class="essay-count-num">{len(pathology_topics)}</span>
                        <span class="essay-count-label">essays</span>
                    </div>
                </div>

                <div class="card-identity-row">
                    <div class="card-logo-box" title="Oral Pathology Pro">
                        <svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
                            <defs>
                                <linearGradient id="pathBgCard" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" stop-color="#581c87"/>
                                    <stop offset="100%" stop-color="#1e102d"/>
                                </linearGradient>
                            </defs>
                            <rect width="512" height="512" rx="112" fill="url(#pathBgCard)" stroke="rgba(255,255,255,0.20)" stroke-width="16"/>
                            <g fill="none" stroke="#f8fafc" stroke-linecap="round" stroke-linejoin="round" stroke-width="24">
                                <path d="M140 420 H372" stroke-width="28"/>
                                <path d="M290 420 C290 340 370 330 370 230 C370 170 320 150 280 150"/>
                                <path d="M190 310 H310" stroke-width="26" stroke="#c084fc"/>
                                <path d="M280 150 L200 230" stroke-width="32" stroke="#ffffff"/>
                                <circle cx="196" cy="234" r="16" fill="#c084fc" stroke="#ffffff" stroke-width="18"/>
                            </g>
                        </svg>
                    </div>
                    <div class="card-title-stack">
                        <h2 class="card-portal-title editorial-heading">Pathology Pro</h2>
                        <span class="card-specialty-sub">Maxillofacial Pathology &amp; Oncology</span>
                    </div>
                </div>

                <p class="card-desc">
                    Microscopic H&amp;E criteria, Vickers-Gorlin sign, Broders grading for OSCC, odontogenic cysts (OKC/KCOT), ameloblastoma variants, and caries histopathology.
                </p>

                <div class="card-features-row">
                    <span class="feature-chip">🎧 Voice Walk</span>
                    <span class="feature-chip">⏱️ Exam Simulator</span>
                    <span class="feature-chip">🔬 Spotters</span>
                    <span class="feature-chip">🃏 Flashcards</span>
                    <span class="feature-chip">📄 Monograph</span>
                </div>

                <div class="card-topic-preview-box">
                    <div class="preview-bubbles-grid">
                        <a href="{pathology_previews[0]['url']}" target="_blank" class="preview-bubble" title="{pathology_previews[0]['title']}" data-testid="hub-topic-bubble">{get_short_title(pathology_previews[0]['title'])}</a>
                        <a href="{pathology_previews[1]['url']}" target="_blank" class="preview-bubble" title="{pathology_previews[1]['title']}" data-testid="hub-topic-bubble">{get_short_title(pathology_previews[1]['title'])}</a>
                        <a href="{pathology_previews[2]['url']}" target="_blank" class="preview-bubble" title="{pathology_previews[2]['title']}" data-testid="hub-topic-bubble">{get_short_title(pathology_previews[2]['title'])}</a>
                        <a href="{pathology_previews[3]['url']}" target="_blank" class="preview-bubble" title="{pathology_previews[3]['title']}" data-testid="hub-topic-bubble">{get_short_title(pathology_previews[3]['title'])}</a>
                    </div>
                    <button class="btn-view-all-topics" data-testid="hub-view-all" onclick="openTopicPanel('pathology', this)" aria-haspopup="dialog" aria-expanded="false" aria-controls="topicPanel">
                        View all {len(pathology_topics)} topics ▸
                    </button>
                </div>

                <div class="card-progress-row">
                    <div class="card-track">
                        <div class="card-fill" id="cardProgressFillPathology" style="width: 0%;"></div>
                    </div>
                    <span id="cardProgressTextPathology">0 of {len(pathology_topics)} done</span>
                </div>

                <div class="card-actions-dock">
                    <a href="https://krrish41.github.io/Oral-Pathology/" target="_blank" class="btn-launch" data-testid="launch-portal">
                        Launch Portal →
                    </a>
                    <a href="https://krrish41.github.io/Oral-Pathology/Oral_Pathology_Master_Notes.pdf" target="_blank" class="btn-pdf" data-testid="portal-pdf" title="Download Master PDF">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
                        PDF
                    </a>
                </div>
            </div>

        </div>
    </main>

    <!-- 5. TOPIC PANEL OVERLAY (DESKTOP POPOVER & MOBILE BOTTOM SHEET) -->
    <div class="topic-panel-scrim" id="topicPanelScrim" data-testid="topic-panel-scrim" onclick="closeTopicPanel()"></div>
    
    <div class="topic-panel" id="topicPanel" data-testid="topic-panel" role="dialog" aria-modal="true" aria-labelledby="topicPanelTitle">
        <div class="bottom-sheet-handle"></div>
        <div class="panel-header">
            <div class="panel-header-info">
                <span class="panel-paper-badge" id="topicPanelBadge">Paper I</span>
                <span class="panel-title" id="topicPanelTitle">Surgery Pro</span>
                <span class="panel-count" id="topicPanelCount">23 topics</span>
            </div>
            <button class="panel-close-btn" data-testid="topic-panel-close" onclick="closeTopicPanel()" aria-label="Close topics panel">&times;</button>
        </div>

        <div class="panel-filter-row">
            <input type="text" id="topicPanelFilter" data-testid="topic-panel-filter" class="panel-filter-input" placeholder="Filter topics…" oninput="onFilterTopicPanel(this.value)" autocomplete="off">
            <button class="filter-clear-btn" id="topicFilterClear" onclick="clearTopicPanelFilter()" style="display:none;" aria-label="Clear filter">&times;</button>
            <div id="topicPanelLiveRegion" class="sr-only" aria-live="polite">23 topics shown</div>
        </div>

        <div class="panel-topics-list" id="topicPanelList" data-testid="topic-panel-list">
            <!-- Populated Dynamically by JS -->
        </div>

        <div class="panel-empty-state" id="topicPanelEmpty" style="display:none;">
            <span>No topics match your filter.</span><br>
            <button onclick="clearTopicPanelFilter()">Clear Filter</button>
        </div>

        <div class="panel-footer-bar">
            <a href="#" id="topicPanelLaunchLink" target="_blank" class="panel-launch-link">Launch Portal →</a>
        </div>
    </div>

    <!-- 6. QUICK REFERENCE MODAL (NORMS, CUTOFFS & 15-MARK RUBRICS) -->
    <div class="lab-modal-overlay" id="labModal" onclick="handleModalBackdropClick(event)">
        <div class="lab-modal-card" onclick="event.stopPropagation()">
            <div class="lab-modal-header">
                <div>
                    <h3 style="font-size:1.15rem; font-weight:700;">Quick Reference &amp; Clinical Blueprints</h3>
                    <div style="font-size:0.75rem; color:var(--text-muted);">Dental Chairside Safety Margins &amp; Preoperative Screening Parameters</div>
                </div>
                <button class="nav-btn" onclick="toggleLabModal()" style="padding:6px 12px;">Close</button>
            </div>
            <div class="lab-modal-tabs">
                <button class="lab-tab-btn active" id="labTabBtn-norm" onclick="switchLabTab('norm')">Normal Laboratory Reference</button>
                <button class="lab-tab-btn" id="labTabBtn-cutoffs" onclick="switchLabTab('cutoffs')">Chairside Surgical Cutoffs</button>
                <button class="lab-tab-btn" id="labTabBtn-rubric" onclick="switchLabTab('rubric')">15-Mark University Blueprints</button>
            </div>
            <div class="lab-modal-body">
                <!-- Tab 1: Normal Lab Norms -->
                <div id="labTabContent-norm">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Investigation</th>
                                <th>Reference Normal Range</th>
                                <th>Chairside Dental Implications</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td><strong>Hemoglobin (Hb)</strong></td><td>M: 13.5–17.5 g/dL<br>F: 12.0–15.5 g/dL</td><td>Elective surgery postponed if Hb &lt; 10 g/dL</td></tr>
                            <tr><td><strong>Platelet Count</strong></td><td>150,000 – 450,000 /mm³</td><td>Safe for routine extraction: &gt; 50,000 /mm³<br>Major maxillofacial: &gt; 80,000–100,000 /mm³</td></tr>
                            <tr><td><strong>Prothrombin Time / INR</strong></td><td>PT: 11–13.5 sec<br>INR: 0.8 – 1.1</td><td>Minor dental surgery safe: INR &le; 2.5 – 3.0 (with local hemostatics)</td></tr>
                            <tr><td><strong>Bleeding Time (Ivy)</strong></td><td>2 – 7 minutes</td><td>Abnormal: &gt; 10 mins (suspect platelet dysfunction/vWD)</td></tr>
                            <tr><td><strong>Clotting Time (Lee-White)</strong></td><td>5 – 11 minutes</td><td>Abnormal: &gt; 15 mins (suspect coagulation factor deficiency)</td></tr>
                            <tr><td><strong>Fasting Blood Glucose</strong></td><td>70 – 99 mg/dL</td><td>Impaired: 100–125 mg/dL<br>Diabetes: &ge; 126 mg/dL</td></tr>
                            <tr><td><strong>HbA1c (Glycated Hb)</strong></td><td>Normal: &lt; 5.7%</td><td>Well controlled: &lt; 7.0%<br>Poor control (&gt; 8.5%): higher infection &amp; delayed healing risk</td></tr>
                            <tr><td><strong>Absolute Neutrophil Count (ANC)</strong></td><td>1,500 – 8,000 /mm³</td><td>Safe chairside: &gt; 1,000 /mm³<br>Severe neutropenia (&lt; 500 /mm³): postpone elective care</td></tr>
                            <tr><td><strong>Serum Creatinine</strong></td><td>0.6 – 1.2 mg/dL</td><td>Elevated (&gt; 1.5 mg/dL): caution with NSAIDs, dose-reduce antibiotics</td></tr>
                            <tr><td><strong>Blood Pressure (JNC-7)</strong></td><td>Normal: &lt; 120 / 80 mmHg</td><td>Stage 1: 140–159 / 90–99 mmHg<br>Stage 2: &ge; 160 / &ge; 100 mmHg (limit epinephrine)</td></tr>
                        </tbody>
                    </table>
                </div>

                <!-- Tab 2: Chairside Cutoffs -->
                <div id="labTabContent-cutoffs" style="display: none;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Clinical Parameter</th>
                                <th>Safe Chairside Cutoff</th>
                                <th>Action If Beyond Cutoff</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td><strong>Platelet Count</strong></td><td>&gt; 50,000 /mm³ (routine)<br>&gt; 80,000 /mm³ (major)</td><td>Postpone surgery; hematology consult; consider platelet transfusion</td></tr>
                            <tr><td><strong>PT / INR</strong></td><td>&le; 2.5 – 3.0</td><td>Consult physician for anticoagulant tapering; local hemostatic agents</td></tr>
                            <tr><td><strong>Fasting Blood Glucose</strong></td><td>&lt; 126 mg/dL (target &lt; 180 postprandial)</td><td>Risk of surgical wound infection; treat acute odontogenic infection first</td></tr>
                            <tr><td><strong>Glycated Hb (HbA1c)</strong></td><td>&lt; 7.0% (moderately safe &lt; 8.0%)</td><td>Avoid elective major flaps if &gt; 8.5%; antimicrobial prophylaxis considered</td></tr>
                            <tr><td><strong>Absolute Neutrophil Count (ANC)</strong></td><td>&gt; 1,000 /mm³</td><td>Antibiotic prophylaxis if 500–1,000; defer elective procedures if &lt; 500</td></tr>
                            <tr><td><strong>Blood Pressure</strong></td><td>&lt; 160 / 100 mmHg</td><td>Stage 2 (&ge; 160/100): defer elective surgery; avoid high-dose adrenaline</td></tr>
                            <tr><td><strong>Bleeding Time</strong></td><td>&lt; 10 minutes</td><td>Investigate for antiplatelet therapy (aspirin/clopidogrel) or vWD</td></tr>
                        </tbody>
                    </table>
                </div>

                <!-- Tab 3: Re-homed 15-Mark University Rubrics -->
                <div id="labTabContent-rubric" style="display: none;">
                    <div class="rubric-modal-wrap">
                        <div class="rubric-segmented-bar">
                            <button class="rubric-tab-btn active" id="rubricTabBtn-surgery" onclick="switchRubric('surgery')">Paper I: Surgery</button>
                            <button class="rubric-tab-btn" id="rubricTabBtn-medicine" onclick="switchRubric('medicine')">Paper II: Medicine</button>
                            <button class="rubric-tab-btn" id="rubricTabBtn-pathology" onclick="switchRubric('pathology')">Paper III: Pathology</button>
                        </div>
                        <p id="rubricDescText" style="font-size:0.86rem; color:var(--text-secondary); line-height:1.5;">
                            General Surgery 15-mark essay structure: applied surgical anatomy, operative steps, surgical instruments, and postoperative complication protocols.
                        </p>
                        <div class="rubric-steps-grid" id="rubricGridContainer">
                            <!-- Populated Dynamically by switchRubric() -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 8. STREAMLINED FOOTER WITH QUICK-REFERENCE SHORTCUTS -->
    <footer class="hub-footer">
        <div class="footer-inner">
            <div class="footer-links-row">
                <a href="javascript:void(0)" class="footer-link" onclick="toggleLabModal('rubric')">15-Mark University Blueprints</a>
                <span>•</span>
                <a href="javascript:void(0)" class="footer-link" onclick="toggleLabModal('cutoffs')">Chairside Surgical Cutoffs</a>
                <span>•</span>
                <a href="javascript:void(0)" class="footer-link" onclick="toggleLabModal('norm')">Laboratory Reference Norms</a>
                <span>•</span>
                <a href="javascript:void(0)" class="footer-link" onclick="focusHubSearch()">Quick Search (/)</a>
            </div>
            <div class="footer-meta-row">
                <span class="cinzel-brand" style="font-weight:700;">BDS CLINICAL VAULT</span>
                <span>•</span>
                <span>Consolidated 3rd Year Dental Surgery &amp; Clinical Sciences Command Suite</span>
                <span>•</span>
                <span>Version 2.2.0 • Zero Clinical Omission</span>
            </div>
        </div>
    </footer>

    <!-- 9. SCRIPT ENGINE -->
    <script>
        // --- 1. Dataset Constants ---
        const ALL_TOPICS = {all_topics_json};
        const SURGERY_TOPICS = {surgery_topics_json};
        const MEDICINE_TOPICS = {medicine_topics_json};
        const PATHOLOGY_TOPICS = {pathology_topics_json};

        const PORTAL_DATA = {{
            surgery: {{
                name: "Surgery Pro",
                badge: "Paper I",
                tagColor: "var(--surgery-accent)",
                url: "https://krrish41.github.io/general-surgery/",
                topics: SURGERY_TOPICS
            }},
            medicine: {{
                name: "Medicine Pro",
                badge: "Paper II",
                tagColor: "var(--medicine-accent)",
                url: "https://krrish41.github.io/General-Medicine/",
                topics: MEDICINE_TOPICS
            }},
            pathology: {{
                name: "Pathology Pro",
                badge: "Paper III",
                tagColor: "var(--pathology-accent)",
                url: "https://krrish41.github.io/Oral-Pathology/",
                topics: PATHOLOGY_TOPICS
            }}
        }};

        // --- 2. Live Progress Calculation from localStorage across All 3 Portals ---
        function calculateOverallProgress() {{
            try {{
                const getCount = (k1, k2) => {{
                    const raw = localStorage.getItem(k1) || localStorage.getItem(k2) || '{{}}';
                    try {{ return Object.keys(JSON.parse(raw)).length; }} catch(e) {{ return 0; }}
                }};

                const surgDone = getCount('bds.surgery.progress', 'surgery_completed_topics');
                const medDone = getCount('bds.medicine.progress', 'medicine_completed_topics');
                const pathDone = getCount('bds.pathology.progress', 'oral_pathology_completed_topics');

                const totalCompleted = surgDone + medDone + pathDone;
                const totalTopics = {total_essays};
                const pct = Math.min(100, Math.round((totalCompleted / totalTopics) * 100));

                const overallEl = document.getElementById('progressOverallStats');
                if (overallEl) overallEl.textContent = `${{totalCompleted}} of ${{totalTopics}} completed · ${{pct}}%`;

                // Segment fills in overall strip
                const surgPct = Math.min(100, Math.round((surgDone / {len(surgery_topics)}) * 100));
                const medPct = Math.min(100, Math.round((medDone / {len(medicine_topics)}) * 100));
                const pathPct = Math.min(100, Math.round((pathDone / {len(pathology_topics)}) * 100));

                const fillSurg = document.getElementById('stripFillSurgery');
                const fillMed = document.getElementById('stripFillMedicine');
                const fillPath = document.getElementById('stripFillPathology');
                if (fillSurg) fillSurg.style.width = `${{surgPct}}%`;
                if (fillMed) fillMed.style.width = `${{medPct}}%`;
                if (fillPath) fillPath.style.width = `${{pathPct}}%`;

                // Tooltip breakdown numbers
                const bdSurg = document.getElementById('breakdownValSurgery');
                const bdMed = document.getElementById('breakdownValMedicine');
                const bdPath = document.getElementById('breakdownValPathology');
                if (bdSurg) bdSurg.textContent = `${{surgDone}} / {len(surgery_topics)}`;
                if (bdMed) bdMed.textContent = `${{medDone}} / {len(medicine_topics)}`;
                if (bdPath) bdPath.textContent = `${{pathDone}} / {len(pathology_topics)}`;

                // Individual Card progress bars
                const cardFillSurg = document.getElementById('cardProgressFillSurgery');
                const cardTxtSurg = document.getElementById('cardProgressTextSurgery');
                if (cardFillSurg) cardFillSurg.style.width = `${{surgPct}}%`;
                if (cardTxtSurg) cardTxtSurg.textContent = `${{surgDone}} of {len(surgery_topics)} done`;

                const cardFillMed = document.getElementById('cardProgressFillMedicine');
                const cardTxtMed = document.getElementById('cardProgressTextMedicine');
                if (cardFillMed) cardFillMed.style.width = `${{medPct}}%`;
                if (cardTxtMed) cardTxtMed.textContent = `${{medDone}} of {len(medicine_topics)} done`;

                const cardFillPath = document.getElementById('cardProgressFillPathology');
                const cardTxtPath = document.getElementById('cardProgressTextPathology');
                if (cardFillPath) cardFillPath.style.width = `${{pathPct}}%`;
                if (cardTxtPath) cardTxtPath.textContent = `${{pathDone}} of {len(pathology_topics)} done`;

            }} catch (e) {{
                console.log('Error calculating study progress:', e);
            }}
        }}

        calculateOverallProgress();
        window.addEventListener('focus', calculateOverallProgress);

        // --- 3. Topic Panel Logic (Popover on Desktop, Bottom Sheet on Mobile) ---
        let currentPanelPortal = null;

        function openTopicPanel(portalKey, triggerBtn) {{
            if (currentPanelPortal === portalKey && isTopicPanelOpen()) {{
                closeTopicPanel();
                return;
            }}
            currentPanelPortal = portalKey;
            const data = PORTAL_DATA[portalKey];
            if (!data) return;

            // Update Header & Badge
            const badgeEl = document.getElementById('topicPanelBadge');
            const titleEl = document.getElementById('topicPanelTitle');
            const countEl = document.getElementById('topicPanelCount');
            const launchEl = document.getElementById('topicPanelLaunchLink');
            const filterInput = document.getElementById('topicPanelFilter');

            if (badgeEl) {{
                badgeEl.textContent = data.badge;
                badgeEl.style.backgroundColor = data.tagColor;
                badgeEl.style.color = '#ffffff';
            }}
            if (titleEl) titleEl.textContent = data.name;
            if (countEl) countEl.textContent = `${{data.topics.length}} topics`;
            if (launchEl) {{
                launchEl.href = data.url;
                launchEl.textContent = `Launch ${{data.name}} →`;
            }}
            if (filterInput) {{
                filterInput.placeholder = `Filter ${{data.name}} topics…`;
                filterInput.value = '';
            }}

            // Render topics
            renderTopicPanelItems(data.topics, portalKey);

            // Open overlay
            const scrim = document.getElementById('topicPanelScrim');
            const panel = document.getElementById('topicPanel');
            if (scrim) scrim.classList.add('open');
            if (panel) panel.classList.add('open');

            // ARIA states
            document.querySelectorAll('.btn-view-all-topics').forEach(b => b.setAttribute('aria-expanded', 'false'));
            if (triggerBtn) triggerBtn.setAttribute('aria-expanded', 'true');

            // Check viewport
            if (window.innerWidth < 768) {{
                document.body.style.overflow = 'hidden';
                try {{ history.pushState({{ topicPanelOpen: true }}, ''); }} catch(e) {{}}
            }} else {{
                positionPopover(panel, triggerBtn);
                if (filterInput) setTimeout(() => filterInput.focus(), 50);
            }}
        }}

        function renderTopicPanelItems(topicList, portalKey) {{
            const listEl = document.getElementById('topicPanelList');
            if (!listEl) return;

            // Read completion status from localStorage
            let completedObj = {{}};
            try {{
                const key1 = `bds.${{portalKey}}.progress`;
                const key2 = `${{portalKey}}_completed_topics`;
                const raw = localStorage.getItem(key1) || localStorage.getItem(key2) || '{{}}';
                completedObj = JSON.parse(raw);
            }} catch(e) {{}}

            // Group by category
            const categories = {{}};
            topicList.forEach((t, idx) => {{
                const cat = t.category || 'Curriculum Topics';
                if (!categories[cat]) categories[cat] = [];
                categories[cat].push({{ ...t, globalIdx: idx }});
            }});

            const catKeys = Object.keys(categories);
            if (catKeys.length <= 1) {{
                listEl.innerHTML = topicList.map((t, idx) => {{
                    const isDone = !!completedObj[t.id];
                    const numStr = String(idx + 1).padStart(2, '0');
                    return `
                        <a href="${{t.url}}" target="_blank" class="panel-topic-row" data-title="${{t.title.toLowerCase()}}" onclick="closeTopicPanel(false)">
                            <span class="panel-topic-num">${{numStr}}</span>
                            <span class="panel-topic-title">${{t.title}}</span>
                            <span class="panel-topic-tick ${{isDone ? 'completed' : ''}}" title="${{isDone ? 'Completed' : 'Not completed'}}">${{isDone ? '✓' : '○'}}</span>
                        </a>
                    `;
                }}).join('');
            }} else {{
                listEl.innerHTML = catKeys.map(cat => {{
                    const items = categories[cat];
                    const catDoneCount = items.filter(t => !!completedObj[t.id]).length;
                    return `
                        <div class="panel-category-group">
                            <button type="button" class="panel-category-header" onclick="this.parentElement.classList.toggle('collapsed')">
                                <span>${{cat}} (${{catDoneCount}}/${{items.length}})</span>
                                <span class="panel-category-chevron">▾</span>
                            </button>
                            <div class="panel-category-items">
                                ${{items.map(t => {{
                                    const isDone = !!completedObj[t.id];
                                    const numStr = String(t.globalIdx + 1).padStart(2, '0');
                                    return `
                                        <a href="${{t.url}}" target="_blank" class="panel-topic-row" data-title="${{t.title.toLowerCase()}}" onclick="closeTopicPanel(false)">
                                            <span class="panel-topic-num">${{numStr}}</span>
                                            <span class="panel-topic-title">${{t.title}}</span>
                                            <span class="panel-topic-tick ${{isDone ? 'completed' : ''}}" title="${{isDone ? 'Completed' : 'Not completed'}}">${{isDone ? '✓' : '○'}}</span>
                                        </a>
                                    `;
                                }}).join('')}}
                            </div>
                        </div>
                    `;
                }}).join('');
            }}

            const liveReg = document.getElementById('topicPanelLiveRegion');
            if (liveReg) liveReg.textContent = `${{topicList.length}} topics shown`;

            const emptyEl = document.getElementById('topicPanelEmpty');
            if (emptyEl) emptyEl.style.display = 'none';
        }}

        function positionPopover(panel, triggerBtn) {{
            if (!triggerBtn || window.innerWidth < 768) return;
            const rect = triggerBtn.getBoundingClientRect();
            const panelWidth = Math.min(420, window.innerWidth - 32);
            const panelHeight = Math.min(520, window.innerHeight * 0.7);

            let left = rect.left + (rect.width / 2) - (panelWidth / 2);
            if (left + panelWidth > window.innerWidth - 16) {{
                left = window.innerWidth - 16 - panelWidth;
            }}
            if (left < 16) left = 16;

            const spaceBelow = window.innerHeight - rect.bottom;
            const spaceAbove = rect.top;
            let top;

            if (spaceBelow >= panelHeight || spaceBelow >= spaceAbove) {{
                top = rect.bottom + 8;
                if (top + panelHeight > window.innerHeight - 16) {{
                    top = Math.max(16, window.innerHeight - 16 - panelHeight);
                }}
            }} else {{
                top = rect.top - panelHeight - 8;
                if (top < 16) top = 16;
            }}

            panel.style.top = `${{top}}px`;
            panel.style.left = `${{left}}px`;
            panel.style.width = `${{panelWidth}}px`;
            panel.style.maxHeight = `${{panelHeight}}px`;
        }}

        function isTopicPanelOpen() {{
            const p = document.getElementById('topicPanel');
            return p && p.classList.contains('open');
        }}

        function closeTopicPanel(shouldPopHistory = true) {{
            const scrim = document.getElementById('topicPanelScrim');
            const panel = document.getElementById('topicPanel');
            if (scrim) scrim.classList.remove('open');
            if (panel) panel.classList.remove('open');
            document.body.style.overflow = '';

            const trigger = document.querySelector(`.card-${{currentPanelPortal}} .btn-view-all-topics`);
            if (trigger) {{
                trigger.setAttribute('aria-expanded', 'false');
                trigger.focus();
            }}

            if (shouldPopHistory && history.state && history.state.topicPanelOpen) {{
                try {{ history.back(); }} catch(e) {{}}
            }}
            currentPanelPortal = null;
        }}

        function onFilterTopicPanel(val) {{
            const q = val.toLowerCase().trim();
            const list = document.getElementById('topicPanelList');
            const empty = document.getElementById('topicPanelEmpty');
            const clearBtn = document.getElementById('topicFilterClear');
            const liveReg = document.getElementById('topicPanelLiveRegion');
            if (!list) return;

            if (clearBtn) clearBtn.style.display = q ? 'block' : 'none';

            const items = list.querySelectorAll('.panel-topic-row');
            let visibleCount = 0;
            items.forEach(item => {{
                const title = item.getAttribute('data-title') || '';
                const match = !q || title.includes(q);
                item.style.display = match ? 'flex' : 'none';
                if (match) visibleCount++;
            }});

            // Adjust category groups
            list.querySelectorAll('.panel-category-group').forEach(grp => {{
                const grpItems = grp.querySelectorAll('.panel-topic-row');
                const hasVisible = Array.from(grpItems).some(i => i.style.display !== 'none');
                grp.style.display = hasVisible ? 'block' : 'none';
                if (q && hasVisible) {{
                    grp.classList.remove('collapsed');
                }}
            }});

            if (empty) empty.style.display = visibleCount === 0 ? 'block' : 'none';
            if (liveReg) liveReg.textContent = `${{visibleCount}} topics shown`;
        }}

        function clearTopicPanelFilter() {{
            const input = document.getElementById('topicPanelFilter');
            if (input) {{
                input.value = '';
                input.focus();
            }}
            onFilterTopicPanel('');
        }}

        // Popover repositioning on scroll/resize
        window.addEventListener('resize', () => {{
            if (isTopicPanelOpen() && window.innerWidth >= 768) {{
                const trigger = document.querySelector(`.card-${{currentPanelPortal}} .btn-view-all-topics`);
                const panel = document.getElementById('topicPanel');
                if (trigger && panel) positionPopover(panel, trigger);
            }}
        }});
        window.addEventListener('scroll', () => {{
            if (isTopicPanelOpen() && window.innerWidth >= 768) {{
                const trigger = document.querySelector(`.card-${{currentPanelPortal}} .btn-view-all-topics`);
                const panel = document.getElementById('topicPanel');
                if (trigger && panel) positionPopover(panel, trigger);
            }}
        }}, {{ passive: true }});

        // Mobile back button closes bottom sheet
        window.addEventListener('popstate', (e) => {{
            if (isTopicPanelOpen()) {{
                closeTopicPanel(false);
            }}
        }});

        // --- 4. Deep Work Pomodoro Study Timer (Synchronized via BdsTimer) ---
        function toggleTimer() {{
            if (window.BdsTimer) {{
                window.BdsTimer.toggle();
            }}
        }}

        function resetTimer(minutes) {{
            if (window.BdsTimer) {{
                window.BdsTimer.reset(minutes);
                window.BdsTimer.start(minutes);
            }}
        }}

        function toggleTimerPopover(event) {{
            event.stopPropagation();
            const popover = document.getElementById('timerPopover');
            const btn = document.getElementById('navTimerPill');
            if (!popover) return;
            const isOpen = popover.classList.contains('open');
            if (isOpen) {{
                popover.classList.remove('open');
                if (btn) btn.setAttribute('aria-expanded', 'false');
            }} else {{
                popover.classList.add('open');
                if (btn) btn.setAttribute('aria-expanded', 'true');
            }}
        }}

        function closeTimerPopover() {{
            const popover = document.getElementById('timerPopover');
            const btn = document.getElementById('navTimerPill');
            if (popover) popover.classList.remove('open');
            if (btn) btn.setAttribute('aria-expanded', 'false');
        }}

        document.addEventListener('click', (e) => {{
            if (!e.target.closest('.focus-timer-container')) {{
                closeTimerPopover();
            }}
        }});

        // --- 5. Theme Switching Logic ---
        function toggleTheme() {{
            const current = document.documentElement.getAttribute('data-theme') || 'dark';
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('bds_vault_theme', next);
            updateThemeIcon(next);
        }}

        function updateThemeIcon(theme) {{
            const btn = document.getElementById('themeBtn');
            const overBtn = document.getElementById('overflowThemeBtn');
            const overLabel = document.getElementById('overflowThemeLabel');
            if (btn) {{
                if (theme === 'light') {{
                    btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>';
                }} else {{
                    btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>';
                }}
            }}
            if (overLabel) {{
                overLabel.textContent = theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode';
            }}
        }}

        const savedTheme = localStorage.getItem('bds_vault_theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);

        // --- 5b. Mobile Header Search & Overflow Handlers ---
        function openMobileSearch() {{
            const header = document.getElementById('hubHeader');
            const input = document.getElementById('hubSearchInput');
            if (header) header.classList.add('search-expanded');
            if (input) {{
                setTimeout(() => {{
                    input.focus();
                    onHubSearchFocus();
                }}, 50);
            }}
        }}

        function closeMobileSearch() {{
            const header = document.getElementById('hubHeader');
            if (header) header.classList.remove('search-expanded');
            clearHubSearch();
        }}

        function toggleHubOverflow(event) {{
            if (event) event.stopPropagation();
            const scrim = document.getElementById('hubOverflowScrim');
            const menu = document.getElementById('hubOverflowMenu');
            const btn = document.getElementById('hubOverflowBtn');
            const isOpen = menu && menu.classList.contains('open');
            if (isOpen) {{
                closeHubOverflow();
            }} else {{
                if (scrim) scrim.classList.add('open');
                if (menu) menu.classList.add('open');
                if (btn) btn.setAttribute('aria-expanded', 'true');
                if (window.innerWidth < 480) {{
                    document.body.style.overflow = 'hidden';
                }}
                syncOverflowTimerDisplay();
            }}
        }}

        function closeHubOverflow() {{
            const scrim = document.getElementById('hubOverflowScrim');
            const menu = document.getElementById('hubOverflowMenu');
            const btn = document.getElementById('hubOverflowBtn');
            if (scrim) scrim.classList.remove('open');
            if (menu) menu.classList.remove('open');
            if (btn) btn.setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
        }}

        function syncOverflowTimerDisplay() {{
            if (!window.BdsTimer) return;
            const state = window.BdsTimer.getState ? window.BdsTimer.getState() : null;
            if (!state) return;
            const digitsEl = document.getElementById('overflowTimerDigits');
            const stateEl = document.getElementById('overflowTimerState');
            const startBtn = document.getElementById('overflowTimerStartBtn');
            const overBtn = document.getElementById('hubOverflowBtn');

            const m = Math.floor(state.remaining / 60);
            const s = state.remaining % 60;
            const str = `${{String(m).padStart(2, '0')}}:${{String(s).padStart(2, '0')}}`;
            if (digitsEl) digitsEl.textContent = str;
            if (stateEl) stateEl.textContent = state.isRunning ? 'Running' : (state.remaining === state.total ? `${{Math.round(state.total/60)}}m Preset` : 'Paused');
            if (startBtn) {{
                startBtn.textContent = state.isRunning ? 'Pause Focus' : 'Start Focus';
                if (state.isRunning) {{
                    startBtn.style.background = 'var(--accent-amber, #f59e0b)';
                }} else {{
                    startBtn.style.background = 'var(--accent-emerald, #10b981)';
                }}
            }}
            if (overBtn) {{
                if (state.isRunning) overBtn.classList.add('running');
                else overBtn.classList.remove('running');
            }}
        }}

        window.addEventListener('bds:timer-tick', syncOverflowTimerDisplay);
        window.addEventListener('bds:timer-state', syncOverflowTimerDisplay);

        // --- 6. Quick Reference Modal Tabs & Rubrics ---
        const RUBRIC_MODELS = {{
            surgery: {{
                desc: "General Surgery 15-mark essay structure: applied surgical anatomy, operative steps, surgical instruments, and postoperative complication protocols.",
                steps: [
                    {{ num: "01", name: "Definition & Classification", marks: "2.0 Marks" }},
                    {{ num: "02", name: "Surgical Anatomy & Relations", marks: "2.5 Marks" }},
                    {{ num: "03", name: "Etiopathogenesis", marks: "1.5 Marks" }},
                    {{ num: "04", name: "Clinical Presentation & Signs", marks: "2.5 Marks" }},
                    {{ num: "05", name: "Diagnostic Workup & Staging", marks: "2.0 Marks" }},
                    {{ num: "06", name: "Operative Steps & Technique", marks: "3.0 Marks" }},
                    {{ num: "07", name: "Complications & Viva Pearls", marks: "1.5 Marks" }}
                ]
            }},
            medicine: {{
                desc: "General Medicine 15-mark essay structure: diagnostic criteria matrices (Duke/Jones), bedside physical examination signs, and emergency pharmacotherapy.",
                steps: [
                    {{ num: "01", name: "Definition & Etiology", marks: "2.0 Marks" }},
                    {{ num: "02", name: "Pathophysiology & Hemodynamics", marks: "2.5 Marks" }},
                    {{ num: "03", name: "Clinical Signs & Stages", marks: "2.5 Marks" }},
                    {{ num: "04", name: "Diagnostic Criteria & Labs", marks: "2.5 Marks" }},
                    {{ num: "05", name: "Emergency Pharmacotherapy", marks: "3.0 Marks" }},
                    {{ num: "06", name: "Supportive Care & Monitoring", marks: "1.5 Marks" }},
                    {{ num: "07", name: "Prognosis & Chairside Pearls", marks: "1.0 Mark" }}
                ]
            }},
            pathology: {{
                desc: "Oral Pathology 15-mark essay structure: WHO histological classification, microscopic pathognomonics, Broders grading, and microscopic spotter features.",
                steps: [
                    {{ num: "01", name: "Definition & WHO Classification", marks: "2.0 Marks" }},
                    {{ num: "02", name: "Histopathogenesis & Origins", marks: "2.0 Marks" }},
                    {{ num: "03", name: "Clinical & Radiographic Features", marks: "2.5 Marks" }},
                    {{ num: "04", name: "Microscopic H&E Criteria", marks: "3.5 Marks" }},
                    {{ num: "05", name: "Histological Grading (Broders)", marks: "2.0 Marks" }},
                    {{ num: "06", name: "Differential Diagnosis Table", marks: "2.0 Marks" }},
                    {{ num: "07", name: "Must-Draw Schematics & Pearls", marks: "1.0 Mark" }}
                ]
            }}
        }};

        function switchRubric(paper) {{
            document.querySelectorAll('.rubric-tab-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = document.getElementById(`rubricTabBtn-${{paper}}`);
            if (activeBtn) activeBtn.classList.add('active');

            const model = RUBRIC_MODELS[paper];
            if (!model) return;

            const descEl = document.getElementById('rubricDescText');
            if (descEl) descEl.textContent = model.desc;

            const grid = document.getElementById('rubricGridContainer');
            if (grid) {{
                grid.innerHTML = model.steps.map(s => `
                    <div class="rubric-step-box">
                        <span class="rubric-step-num">Step ${{s.num}}</span>
                        <span class="rubric-step-name">${{s.name}}</span>
                        <span class="rubric-step-marks">${{s.marks}} Allocated</span>
                    </div>
                `).join('');
            }}
        }}

        function toggleLabModal(defaultTab = 'norm') {{
            const modal = document.getElementById('labModal');
            if (!modal) return;
            const isOpen = modal.classList.contains('open');
            if (isOpen) {{
                modal.classList.remove('open');
                document.body.style.overflow = '';
            }} else {{
                modal.classList.add('open');
                document.body.style.overflow = 'hidden';
                switchLabTab(defaultTab);
            }}
        }}

        function switchLabTab(tab) {{
            document.querySelectorAll('.lab-tab-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = document.getElementById(`labTabBtn-${{tab}}`);
            if (activeBtn) activeBtn.classList.add('active');

            const normView = document.getElementById('labTabContent-norm');
            const cutoffsView = document.getElementById('labTabContent-cutoffs');
            const rubricView = document.getElementById('labTabContent-rubric');

            if (normView) normView.style.display = tab === 'norm' ? 'block' : 'none';
            if (cutoffsView) cutoffsView.style.display = tab === 'cutoffs' ? 'block' : 'none';
            if (rubricView) rubricView.style.display = tab === 'rubric' ? 'block' : 'none';

            if (tab === 'rubric') {{
                switchRubric('surgery');
            }}
        }}

        function handleModalBackdropClick(e) {{
            if (e.target.id === 'labModal') {{
                toggleLabModal();
            }}
        }}

        // --- 7. Inline Header Search Logic ---
        function focusHubSearch() {{
            const input = document.getElementById('hubSearchInput');
            if (input) {{
                input.focus();
                onHubSearchFocus();
            }}
        }}

        function onHubSearchFocus() {{
            const input = document.getElementById('hubSearchInput');
            if (input && input.value.trim().length > 0) {{
                onHubSearchInput(input.value);
            }} else {{
                renderHubSearchResults(ALL_TOPICS.slice(0, 8), '');
            }}
        }}

        function onHubSearchInput(query) {{
            const q = query.toLowerCase().trim();
            const clearBtn = document.getElementById('hubSearchClear');
            const resultsBox = document.getElementById('hubSearchResults');
            if (clearBtn) clearBtn.style.display = q ? 'inline-block' : 'none';

            if (!q) {{
                renderHubSearchResults(ALL_TOPICS.slice(0, 8), '');
                return;
            }}

            const filtered = ALL_TOPICS.filter(t =>
                t.title.toLowerCase().includes(q) ||
                (t.category && t.category.toLowerCase().includes(q)) ||
                (t.sub && t.sub.toLowerCase().includes(q)) ||
                (t.tag && t.tag.toLowerCase().includes(q))
            );
            renderHubSearchResults(filtered, q);
        }}

        function clearHubSearch() {{
            const input = document.getElementById('hubSearchInput');
            const resultsBox = document.getElementById('hubSearchResults');
            const clearBtn = document.getElementById('hubSearchClear');
            if (input) {{
                input.value = '';
                input.focus();
            }}
            if (clearBtn) clearBtn.style.display = 'none';
            if (resultsBox) resultsBox.style.display = 'none';
        }}

        function renderHubSearchResults(list, query) {{
            const box = document.getElementById('hubSearchResults');
            if (!box) return;

            if (list.length === 0) {{
                box.innerHTML = '<div style="padding:14px; text-align:center; color:var(--text-muted); font-size:0.84rem;">No matching curriculum essays or tools found.</div>';
                box.style.display = 'flex';
                return;
            }}

            // Group by category / type
            const groups = {{
                'surgery': {{ label: '📖 General Surgery Essays', items: [] }},
                'medicine': {{ label: '🩺 General Medicine Essays', items: [] }},
                'pathology': {{ label: '🔬 Oral Pathology Essays', items: [] }},
                'spotters': {{ label: '🎯 Microscopic & Surgical Spotters', items: [] }},
                'flashcards': {{ label: '🎴 Active Recall Flashcards', items: [] }},
                'schematics': {{ label: '📐 Schematics & Algorithms', items: [] }}
            }};

            list.forEach(item => {{
                if (item.type === 'spotters') groups['spotters'].items.push(item);
                else if (item.type === 'flashcards') groups['flashcards'].items.push(item);
                else if (item.type === 'schematics') groups['schematics'].items.push(item);
                else if (item.paper === 'surgery') groups['surgery'].items.push(item);
                else if (item.paper === 'medicine') groups['medicine'].items.push(item);
                else if (item.paper === 'pathology') groups['pathology'].items.push(item);
            }});

            let html = '';
            for (const key of ['surgery', 'medicine', 'pathology', 'spotters', 'flashcards', 'schematics']) {{
                const g = groups[key];
                if (g.items.length > 0) {{
                    html += `
                        <div class="hub-search-group">
                            <div class="hub-search-group-title">${{g.label}}</div>
                            ${{g.items.slice(0, 6).map(it => `
                                <a href="${{it.url}}" target="_blank" class="hub-search-item" onclick="document.getElementById('hubSearchResults').style.display='none'">
                                    <span class="hub-search-item-title">${{it.title}}</span>
                                    <span class="hub-search-item-tag">${{it.tag}}</span>
                                </a>
                            `).join('')}}
                        </div>
                    `;
                }}
            }}

            box.innerHTML = html;
            box.style.display = 'flex';
        }}

        // Close search results when clicking outside
        document.addEventListener('click', (e) => {{
            if (!e.target.closest('#hubSearchContainer')) {{
                const box = document.getElementById('hubSearchResults');
                if (box) box.style.display = 'none';
            }}
        }});

        // Global Keyboard Shortcut Handler (/ to search, Esc to close)
        window.addEventListener('keydown', (e) => {{
            if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {{
                e.preventDefault();
                focusHubSearch();
            }} else if (e.key === 'Escape') {{
                if (isTopicPanelOpen()) closeTopicPanel();
                const labModal = document.getElementById('labModal');
                if (labModal && labModal.classList.contains('open')) toggleLabModal();
                clearHubSearch();
                closeTimerPopover();
            }}
        }});
    </script>
    <script src="portal-core/core-engine.js"></script>
</body>
</html>
"""

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully generated clean, unified BDS Clinical Vault Hub -> {INDEX_PATH}")
