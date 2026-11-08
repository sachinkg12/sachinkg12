#!/usr/bin/env python3
"""Build the static SVG assets used by the GitHub profile design.

Run from this repository with: python3 scripts/build_profile_design.py
Update the dated facts and labels here when the profile changes.
Install scripts/design-requirements.txt first. Uses bundled fonts; no network requests.
"""
from pathlib import Path
from html import escape
import base64
import json
from profile_typography import outline_svg
from profile_theme import THEME, apply_theme

repo = Path(__file__).resolve().parent.parent
out = repo / 'assets/profile'
out.mkdir(exist_ok=True)
FONT = 'Manrope'
DISPLAY = 'Space Grotesk'
MONO = 'IBM Plex Mono'
# Selected palette is stored in assets/profile/theme.json. Legacy canvas colors
# below are normalized by apply_theme before export; regenerating keeps the selection.
PORTRAIT = "data:image/png;base64," + base64.b64encode((out / "portrait.png").read_bytes()).decode("ascii")

def save(name, width, height, label, content):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title"><title id="title">{escape(label)}</title>{content}</svg>'
    destination = out / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(outline_svg(apply_theme(svg, name)))

def text(x, y, value, size=18, color='#172033', weight=400, family=FONT, extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{family}" font-size="{size}" font-weight="{weight}" {extra}>{escape(value)}</text>'

def hello_greeting(x, y):
    # An original vector hand keeps the greeting self-contained and animated
    # inside the banner image. Reduced-motion viewers see a still greeting.
    body = f'''<style>
@keyframes greeting-wave {{
  0%,52%,100% {{transform:rotate(0deg)}}
  8%,24% {{transform:rotate(18deg)}}
  16%,32% {{transform:rotate(-12deg)}}
  40% {{transform:rotate(12deg)}}
}}
.greeting-wave {{transform-origin:24px 40px;animation:greeting-wave 3.2s ease-in-out infinite}}
@media (prefers-reduced-motion:reduce) {{.greeting-wave {{animation:none}}}}
</style><g transform="translate({x} {y})" role="img" aria-label="Hello! A friendly waving hand.">
<rect x=".5" y=".5" width="144" height="48" rx="24" fill="#162b3a" stroke="#31515e"/>
<g transform="translate(14 7) scale(.72)"><g class="greeting-wave">
<path d="M20 44C13 41 9 35 7 29L3 21C2 18 5 16 7 18L12 24L6 10C5 7 9 5 11 8L18 20L13 5C12 2 17 0 19 4L24 18L22 4C22 1 27 0 28 4L31 19L31 9C31 5 36 5 37 9L40 27C43 35 38 44 30 46Z" fill="#fde047" stroke="#fb923c" stroke-width="1.2" stroke-linejoin="round"/>
<path d="M12 24c3 1 5 4 5 7m7-1c0-4 4-6 8-5" fill="none" stroke="#f97316" stroke-width="1.4" stroke-linecap="round"/>
</g></g>'''
    body += text(57, 32, 'Hello!', 22, '#f8fafc', 600, DISPLAY)
    return body + '</g>'

cover = '''<defs>
<linearGradient id="base" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#101d33"/><stop offset="1" stop-color="#0b1425"/></linearGradient>
<radialGradient id="glow"><stop stop-color="#0d9488" stop-opacity=".18"/><stop offset="1" stop-color="#0d9488" stop-opacity="0"/></radialGradient>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#8da4be" opacity=".13"/></pattern>
</defs>
<rect width="1200" height="274" rx="18" fill="url(#base)"/>
<rect width="1200" height="274" rx="18" fill="url(#grid)"/>
<ellipse cx="1010" cy="140" rx="290" ry="230" fill="url(#glow)"/>
<path d="M48 0h38" stroke="#f97316" stroke-width="5"/><path d="M86 0h38" stroke="#ef4444" stroke-width="5"/><path d="M124 0h36" stroke="#facc15" stroke-width="5"/>
'''
cover += f'<defs><clipPath id="portrait"><rect x="947" y="26" width="210" height="222" rx="23"/></clipPath></defs><rect x="939" y="18" width="226" height="238" rx="29" fill="#18313e" stroke="#4ac3b0" stroke-opacity=".6"/><image x="947" y="26" width="210" height="222" href="{PORTRAIT}" preserveAspectRatio="xMidYMid slice" clip-path="url(#portrait)"/>'
cover += text(48, 44, 'ENGINEERING  /  RESEARCH  /  SPEAKING', 13, '#92a8be', 500, MONO, 'letter-spacing="2"')
cover += text(46, 112, 'Sachin Gupta', 57, '#f8fafc', 650, DISPLAY, extra='letter-spacing="-1.5"')
cover += text(48, 157, 'Reliable platforms. Trustworthy AI.', 28, '#5eead4', 500, DISPLAY)
cover += text(48, 195, 'Backend & platform engineer · Applied AI researcher · Speaker', 19, '#c4d0df')
cover += text(48, 239, 'EBAY MONETIZATION', 12, '#94a8bd', 400, MONO, 'letter-spacing="1.5"')
cover += hello_greeting(759, 31)
save('cover.svg', 1200, 274, 'Hello! I’m Sachin Gupta — Reliable platforms. Trustworthy AI. Backend and platform engineer, applied AI researcher and speaker. San Jose, California.', cover)

strip = ''
for x, value, label, color, bg, stroke in [
    (0, '15+', 'YEARS IN ENGINEERING', '#0f766e', '#fefce8', '#fde047'),
    (408, '9', 'ACCEPTED RESEARCH PAPERS', '#ea580c', '#fff7ed', '#fdba74'),
    (816, 'eBay', 'MONETIZATION', '#075985', '#f0f9ff', '#bae6fd'),
]:
    strip += f'<rect x="{x+1}" y="1" width="382" height="109" rx="12" fill="{bg}" stroke="{stroke}"/>'
    strip += f'<rect x="{x+22}" y="25" width="3" height="62" rx="1.5" fill="{color}"/>'
    strip += text(x+43, 54, value, 34, color, 650, DISPLAY)
    strip += text(x+43, 83, label, 13, '#546377', 500, MONO, 'letter-spacing=".5"')
save('credentials.svg', 1200, 112, '15+ years in engineering. 9 accepted research papers. eBay Monetization.', strip)

for key, label, marker in [
    ('website', 'My website', THEME['primary']),
    ('sessionize', 'Sessionize', '#facc15'),
    ('scholar', 'Google Scholar', '#f97316'),
    ('linkedin', 'LinkedIn', '#0a66c2'),
]:
    primary = key == 'website'
    color = THEME['primary'] if primary else '#ffffff'
    border = THEME['primary'] if primary else THEME['border']
    ink = '#ffffff' if primary else THEME['ink']
    body = f'<rect x=".5" y=".5" width="269" height="49" rx="9" fill="{color}" stroke="{border}"/>'
    if not primary:
        body += f'<rect x="1" y="12" width="3" height="26" rx="1.5" fill="{marker}"/>'
    body += text(17, 31, label, 17, ink, 550)
    body += f'<path d="M231 25h18m-6-6 6 6-6 6" stroke="{ink}" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    save(f'link-{key}.svg', 270, 50, label, body)

icons = {
'engineering': ('#0f766e', '#d5f6ed', '<path d="m10 10-4 4 4 4m8-8 4 4-4 4m-3-10-2 16"/>'),
'research': ('#ea580c', '#fff7ed', '<path d="M6 7h6c2 0 2 1 2 2 0-1 0-2 2-2h6v15h-6c-2 0-2 1-2 1s0-1-2-1H6zm8 2v14"/>'),
'speaking': ('#172033', '#fde047', '<rect x="11" y="5" width="6" height="12" rx="3"/><path d="M8 12v2a6 6 0 0 0 12 0v-2m-6 8v4m-3 0h6"/>'),
'writing': ('#075985', '#e0f2fe', '<path d="M7 5h14v18H7zm4 5h6m-6 4h6m-6 4h4"/>'),
'opensource': ('#0f766e', '#d5f6ed', '<rect x="5" y="7" width="18" height="15" rx="2"/><path d="m9 12 3 3-3 3m6 0h4"/>'),
'community': ('#dc2626', '#f1f5f9', '<circle cx="14" cy="9" r="3"/><path d="M8 23v-3a6 6 0 0 1 12 0v3M7 9a3 3 0 0 0 0 6m14-6a3 3 0 0 1 0 6M4 22v-2a4 4 0 0 1 3-4m17 6v-2a4 4 0 0 0-3-4"/>'),
'personal': ('#172033', '#fde047', '<path d="M5 10h5l2-3h5l2 3h4v12H5z"/><circle cx="14" cy="16" r="4"/>'),
}
for name, (color, bg, paths) in icons.items():
    body = f'<rect width="28" height="28" rx="7" fill="{bg}"/><g stroke="{color}" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round">{paths}</g>'
    save(f'icon-{name}.svg', 28, 28, '', body)

body = '<rect x="1" y="1" width="1198" height="161" rx="14" fill="#fff7ed" stroke="#fdba74"/><rect x="1" y="1" width="6" height="161" rx="3" fill="#f97316"/>'
body += text(36, 35, 'SPEAKING / SESSIONIZE', 12, '#475569', 550, MONO, 'letter-spacing="1.3"')
body += text(35, 83, 'Practical talks. Working demonstrations.', 32, '#172033', 600, DISPLAY, extra='letter-spacing="-.5"')
body += text(36, 122, 'Session abstracts · Event history · Speaking invitations', 18, '#475569')
body += '<circle cx="1118" cy="81" r="28" fill="#ffedd5"/><path d="M1104 81h28m-9-9 9 9-9 9" stroke="#ea580c" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
save('speaking-card.svg', 1200, 164, 'Sessionize — Practical talks and working demonstrations. View session abstracts, event history and speaking invitations.', body)

body = '<rect x="1" y="1" width="1198" height="171" rx="14" fill="#edf8f7" stroke="#b8dfda"/><rect x="1" y="1" width="6" height="171" rx="3" fill="#0f766e"/>'
body += text(36, 36, 'WRITING / VISUALIZERS / RESEARCH', 12, '#0f766e', 550, MONO, 'letter-spacing="1.3"')
body += text(34, 87, 'guptasachinn.com', 36, '#134e4a', 650, DISPLAY, extra='letter-spacing="-.7"')
body += text(36, 128, 'Engineering ideas, explained through examples you can explore.', 19, '#466966')
body += '<rect x="1009" y="31" width="110" height="96" rx="8" fill="#d0ebe6" stroke="#9dcfc5"/><rect x="1033" y="45" width="110" height="96" rx="8" fill="#ffffff" stroke="#9dcfc5"/><path d="M1052 68h69m-69 17h48m-48 17h61m-61 17h38" stroke="#59a598" stroke-width="4" stroke-linecap="round"/>'
save('website-card.svg', 1200, 174, 'Visit guptasachinn.com — Engineering writing, interactive visualizers and research.', body)
mobile = '<rect width="600" height="330" rx="16" fill="#101d33"/><path d="M32 0h32" stroke="#f97316" stroke-width="5"/><path d="M64 0h32" stroke="#ef4444" stroke-width="5"/><path d="M96 0h32" stroke="#facc15" stroke-width="5"/>'
mobile += f'<defs><clipPath id="portrait-mobile"><rect x="430" y="97" width="138" height="177" rx="16"/></clipPath></defs><rect x="424" y="91" width="150" height="189" rx="21" fill="#18313e" stroke="#4ac3b0" stroke-opacity=".6"/><image x="430" y="97" width="138" height="177" href="{PORTRAIT}" preserveAspectRatio="xMidYMid slice" clip-path="url(#portrait-mobile)"/>'
mobile += text(32, 51, 'ENGINEERING / RESEARCH / SPEAKING', 14, '#92a8be', 500, MONO, 'letter-spacing="1"')
mobile += text(29, 127, 'Sachin Gupta', 57, '#f8fafc', 650, DISPLAY, extra='letter-spacing="-1.5"')
mobile += text(32, 184, 'Reliable platforms.', 32, '#5eead4', 500, DISPLAY)
mobile += text(32, 225, 'Trustworthy AI.', 32, '#5eead4', 500, DISPLAY)
mobile += text(32, 281, 'BACKEND & PLATFORM ENGINEER', 15, '#c4d0df', 400, MONO)
mobile += text(32, 307, 'EBAY MONETIZATION', 13, '#94a8bd', 400, MONO, 'letter-spacing="1"')
mobile += hello_greeting(423, 24)
save('cover-mobile.svg', 600, 330, 'Hello! I’m Sachin Gupta — Reliable platforms. Trustworthy AI.', mobile)
for slug, family in [('space-grotesk', 'Space Grotesk'), ('manrope', 'Manrope'), ('sora', 'Sora')]:
    save(f'font-options/{slug}.svg', 1200, 274, f'{family} — Sachin Gupta profile banner', cover.replace(f'font-family="{DISPLAY}"', f'font-family="{family}"'))
    save(f'font-options/{slug}-mobile.svg', 600, 330, f'{family} — Sachin Gupta profile banner', mobile.replace(f'font-family="{DISPLAY}"', f'font-family="{family}"'))
mobile = ''
for x, value, label, color, bg, stroke in [(0,'15+','YEARS ENGINEERING','#0f766e','#fefce8','#fde047'),(310,'9','ACCEPTED PAPERS','#ea580c','#fff7ed','#fdba74')]:
    mobile += f'<rect x="{x+1}" y="1" width="288" height="115" rx="12" fill="{bg}" stroke="{stroke}"/>'
    mobile += text(x+24, 56, value, 44, color, 650, DISPLAY)
    mobile += text(x+24, 89, label, 15, '#546377', 500, MONO)
mobile += '<rect x="1" y="128" width="598" height="81" rx="12" fill="#f0f9ff" stroke="#bae6fd"/>'
mobile += text(24, 180, 'eBay', 33, '#075985', 650, DISPLAY)
mobile += text(147, 177, 'Monetization', 18, '#546377')
save('credentials-mobile.svg', 600, 210, '15+ years engineering. 9 accepted papers. eBay Monetization.', mobile)


# Distribution counts are a dated public-marketplace snapshot, not unique users.
metrics = json.loads((out / 'heaplens-distribution.json').read_text())
body = '<rect x="1" y="1" width="1198" height="169" rx="14" fill="#edf8f7" stroke="#b8dfda"/>'
body += text(32, 33, 'HEAPLENS / MARKETPLACE DOWNLOADS', 12, '#0f766e', 550, MONO, 'letter-spacing="1"')
body += text(30, 99, f"{metrics['total_downloads']:,}", 47, '#134e4a', 650)
body += text(32, 137, 'Snapshot · November 6, 2026', 15, '#466966')
for x, value, label in [(450,metrics['vscode_downloads'],'VS CODE'),(705,metrics['openvsx_downloads'],'OPEN VSX'),(960,metrics['jetbrains_downloads'],'JETBRAINS')]:
    body += f'<path d="M{x-28} 61v78" stroke="#b8dfda"/>'
    body += text(x, 96, f'{value:,}', 31, '#0f766e', 600)
    body += text(x, 130, label, 12, '#466966', 500, MONO)
save('heaplens-adoption.svg', 1200, 172, f"HeapLens: {metrics['total_downloads']:,} marketplace downloads on November 6, 2026. VS Code {metrics['vscode_downloads']:,}, Open VSX {metrics['openvsx_downloads']:,}, JetBrains {metrics['jetbrains_downloads']:,}.", body)

# Native Markdown tables retain selectable text and real links. These small SVGs
# add typography, color and action affordances that survive GitHub sanitization.
for name, label, width, accent in [
    ('work', 'WORK', 180, '#f97316'),
    ('focus', 'RESEARCH FOCUS', 260, '#f97316'),
    ('venue', 'VENUE & STATUS', 200, '#f97316'),
    ('paper', 'PAPER', 112, '#f97316'),
    ('project', 'PROJECT', 180, '#0d9488'),
    ('built', 'WHAT I BUILT', 400, '#0d9488'),
    ('code', 'CODE', 112, '#0d9488'),
    ('review-venue', 'VENUE', 180, '#ef4444'),
    ('review-role', 'RESEARCH SERVICE', 560, '#ef4444'),
]:
    body = f'<rect width="{width}" height="36" rx="6" fill="#101d33"/><rect x="0" y="7" width="3" height="22" rx="1.5" fill="{accent}"/>'
    body += text(14, 23, label, 12, '#f8fafc', 600, MONO, 'letter-spacing=".5"')
    save(f'tables/header-{name}.svg', width, 36, label, body)

for name, label, width, color, background, border in [
    ('published', 'PUBLISHED', 102, '#0f766e', '#d5f6ed', '#a7dfd2'),
    ('accepted', 'ACCEPTED', 102, '#172033', '#ffedd5', '#fb923c'),
    ('reviewer', 'REVIEWER', 100, '#0f766e', '#d5f6ed', '#a7dfd2'),
    ('area-chair', 'AREA CHAIR', 114, '#ffffff', '#dc2626', '#dc2626'),
    ('artifacts', 'ARTIFACT EVALUATION', 186, '#075985', '#e0f2fe', '#bae6fd'),
]:
    body = f'<rect x=".5" y=".5" width="{width-1}" height="23" rx="6" fill="{background}" stroke="{border}"/>'
    body += text(10, 16, label, 11, color, 600, MONO, 'letter-spacing=".4"')
    save(f'tables/badge-{name}.svg', width, 24, label.title(), body)

for name, label, background, ink, accent, border in [
    ('paper', 'Read paper', '#101d33', '#ffffff', '#fb923c', '#101d33'),
    ('arxiv', 'arXiv', '#fef9c3', '#172033', '#172033', '#facc15'),
    ('code', 'View code', '#e0f2fe', '#075985', '#0369a1', '#bae6fd'),
]:
    body = f'<rect x=".5" y=".5" width="115" height="33" rx="7" fill="{background}" stroke="{border}"/>'
    body += text(11, 22, label, 13, ink, 600)
    body += f'<path d="M96 23V13m-6 0h6v6m-8 3 8-9" fill="none" stroke="{accent}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
    save(f'tables/action-{name}.svg', 116, 34, label, body)

print(f'Created {len(list(out.rglob("*.svg")))} self-contained SVG assets in {out}')
