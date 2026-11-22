#!/usr/bin/env python3
"""Build the GitHub-compatible artwork in the style of sachinkg12.github.io.

Install scripts/design-requirements.txt, then run this script. Fonts and the
reference site's original illustration are bundled; generation needs no network.
The README remains native Markdown, with its existing facts and links unchanged.
"""
from pathlib import Path
from html import escape
import base64
import json
from profile_typography import outline_svg
from profile_theme import THEME

repo = Path(__file__).resolve().parent.parent
out = repo / 'assets/profile'
FONT = 'IBM Plex Sans'
SERIF = 'Lora'
MONO = 'IBM Plex Mono'
INK, MUTED, LINE = THEME['ink'], THEME['slate'], THEME['border']
WHITE, SOFT = THEME['base'], THEME['mist']
LEAF, YELLOW, FOREST = THEME['leaf'], THEME['accent'], THEME['primary']
ART = 'data:image/webp;base64,' + base64.b64encode((out / 'desk-illustration.webp').read_bytes()).decode('ascii')


def save(name, width, height, label, content):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title"><title id="title">{escape(label)}</title>{content}</svg>'
    destination = out / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(outline_svg(svg))


def text(x, y, value, size=18, color=INK, weight=400, family=FONT, extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{family}" font-size="{size}" font-weight="{weight}" {extra}>{escape(value)}</text>'


def rect(x, y, width, height, fill=WHITE, stroke=LINE, radius=16):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'


def line(x1, y1, x2, y2, color=LINE):
    return f'<path d="M{x1} {y1}H{x2}" stroke="{color}"/>' if y1 == y2 else f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}"/>'


def hello_greeting(x, y):
    # Preserve the original self-contained wave and reduced-motion support.
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
{rect(.5, .5, 144, 48, radius=24)}
<g transform="translate(14 7) scale(.72)"><g class="greeting-wave">
<path d="M20 44C13 41 9 35 7 29L3 21C2 18 5 16 7 18L12 24L6 10C5 7 9 5 11 8L18 20L13 5C12 2 17 0 19 4L24 18L22 4C22 1 27 0 28 4L31 19L31 9C31 5 36 5 37 9L40 27C43 35 38 44 30 46Z" fill="#fde047" stroke="#fb923c" stroke-width="1.2" stroke-linejoin="round"/>
<path d="M12 24c3 1 5 4 5 7m7-1c0-4 4-6 8-5" fill="none" stroke="#f97316" stroke-width="1.4" stroke-linecap="round"/>
</g></g>'''
    return body + text(57, 32, 'Hello!', 22, weight=500) + '</g>'


# White, open hero: current words, with the site's illustration and serif accent.
cover = rect(0, 0, 1200, 472, stroke=WHITE, radius=0)
cover += text(24, 50, 'Sachin Gupta · San Jose, California', 22, MUTED)
cover += hello_greeting(1018, 14)
cover += text(20, 152, 'Reliable platforms.', 60, weight=600, family='Arial', extra='letter-spacing="-2"')
cover += text(22, 230, 'Trustworthy AI.', 59, family=SERIF, extra='font-style="italic" letter-spacing="-2"')
cover += text(24, 300, 'Backend & platform engineer', 23, MUTED)
cover += text(24, 335, 'Applied AI researcher · Speaker', 23, MUTED)
cover += text(24, 412, 'eBay', 20, weight=500)
cover += text(94, 412, 'Monetization', 20, MUTED)
cover += f'<image x="610" y="92" width="590" height="393.33" href="{ART}" preserveAspectRatio="xMidYMid meet"/>'
save('cover.svg', 1200, 472, 'Hello! I’m Sachin Gupta — Reliable platforms. Trustworthy AI. Backend and platform engineer, applied AI researcher and speaker. San Jose, California.', cover)

mobile = rect(0, 0, 600, 672, stroke=WHITE, radius=0)
mobile += text(16, 43, 'Sachin Gupta · San Jose, California', 18, MUTED)
mobile += hello_greeting(434, 13)
mobile += text(14, 123, 'Reliable platforms.', 57, weight=600, family='Arial', extra='letter-spacing="-2"')
mobile += text(16, 194, 'Trustworthy AI.', 56, family=SERIF, extra='font-style="italic" letter-spacing="-1.5"')
mobile += text(18, 249, 'Backend & platform engineer', 22, MUTED)
mobile += text(18, 284, 'Applied AI researcher · Speaker', 22, MUTED)
mobile += text(18, 329, 'eBay Monetization', 20, weight=500)
mobile += f'<image x="38" y="342" width="530" height="353.33" href="{ART}" preserveAspectRatio="xMidYMid meet"/>'
save('cover-mobile.svg', 600, 672, 'Hello! I’m Sachin Gupta — Reliable platforms. Trustworthy AI.', mobile)

strip = ''
for x, value, label in [(0, '15+', 'YEARS IN ENGINEERING'), (408, '9', 'ACCEPTED RESEARCH PAPERS'), (816, 'eBay', 'MONETIZATION')]:
    strip += rect(x+1, 1, 382, 109, radius=14)
    strip += text(x+25, 54, value, 37, weight=500)
    strip += text(x+25, 85, label, 13, MUTED, family=MONO)
save('credentials.svg', 1200, 112, '15+ years in engineering. 9 accepted research papers. eBay Monetization.', strip)

mobile = ''
for x, value, label in [(0, '15+', 'YEARS ENGINEERING'), (310, '9', 'ACCEPTED PAPERS')]:
    mobile += rect(x+1, 1, 288, 115, radius=14)
    mobile += text(x+24, 56, value, 44, weight=500)
    mobile += text(x+24, 89, label, 15, MUTED, family=MONO)
mobile += rect(1, 128, 598, 81, radius=14)
mobile += text(24, 180, 'eBay', 33, weight=500)
mobile += text(147, 177, 'Monetization', 20, MUTED)
save('credentials-mobile.svg', 600, 210, '15+ years engineering. 9 accepted papers. eBay Monetization.', mobile)

# All four original destinations remain clickable in the native README.
for key, label in [('website', 'My website'), ('sessionize', 'Sessionize'), ('scholar', 'Google Scholar'), ('linkedin', 'LinkedIn')]:
    primary = key == 'website'
    body = rect(.5, .5, 269, 49, INK if primary else WHITE, INK if primary else LINE, 25)
    body += text(135, 32, label, 19, WHITE if primary else INK, weight=500, extra='text-anchor="middle"')
    save(f'link-{key}.svg', 270, 50, label, body)

icons = {
    'engineering': '<path d="m10 10-4 4 4 4m8-8 4 4-4 4m-3-10-2 16"/>',
    'research': '<path d="M6 7h6c2 0 2 1 2 2 0-1 0-2 2-2h6v15h-6c-2 0-2 1-2 1s0-1-2-1H6zm8 2v14"/>',
    'speaking': '<rect x="11" y="5" width="6" height="12" rx="3"/><path d="M8 12v2a6 6 0 0 0 12 0v-2m-6 8v4m-3 0h6"/>',
    'writing': '<path d="M7 5h14v18H7zm4 5h6m-6 4h6m-6 4h4"/>',
    'opensource': '<rect x="5" y="7" width="18" height="15" rx="2"/><path d="m9 12 3 3-3 3m6 0h4"/>',
    'community': '<circle cx="14" cy="9" r="3"/><path d="M8 23v-3a6 6 0 0 1 12 0v3M7 9a3 3 0 0 0 0 6m14-6a3 3 0 0 1 0 6M4 22v-2a4 4 0 0 1 3-4m17 6v-2a4 4 0 0 0-3-4"/>',
    'personal': '<path d="M5 10h5l2-3h5l2 3h4v12H5z"/><circle cx="14" cy="16" r="4"/>',
}
for name, paths in icons.items():
    save(f'icon-{name}.svg', 28, 28, '', f'<g stroke="{INK}" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round">{paths}</g>')

# The same feature-card copy, with the reference site's pale yellow/leaf panels.
body = f'<defs><clipPath id="card"><rect x="1" y="1" width="1198" height="216" rx="22"/></clipPath></defs>'
body += rect(1, 1, 1198, 216, radius=22)
body += f'<rect x="825" y="1" width="374" height="216" fill="{YELLOW}" clip-path="url(#card)"/>'
body += text(34, 38, 'SPEAKING / SESSIONIZE', 13, MUTED, family=MONO)
body += text(32, 95, 'Practical talks.', 41, weight=600, family='Arial', extra='letter-spacing="-1"')
body += text(32, 147, 'Working demonstrations.', 41, family=SERIF, extra='font-style="italic" letter-spacing="-1"')
body += text(34, 187, 'Session abstracts · Event history · Speaking invitations', 20, MUTED)
body += f'<g stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round"><rect x="983" y="47" width="48" height="86" rx="24"/><path d="M965 102v10a42 42 0 0 0 84 0v-10m-42 52v25m-22 0h44"/></g>'
save('speaking-card.svg', 1200, 218, 'Sessionize — Practical talks and working demonstrations. View session abstracts, event history and speaking invitations.', body)

body = rect(1, 1, 598, 358, radius=22)
body += text(24, 37, 'SPEAKING / SESSIONIZE', 17, MUTED, family=MONO)
body += text(23, 103, 'Practical talks.', 46, weight=600, family='Arial', extra='letter-spacing="-1"')
body += text(23, 162, 'Working demonstrations.', 42, family=SERIF, extra='font-style="italic" letter-spacing="-1"')
body += text(24, 207, 'Session abstracts · Event history', 23, MUTED)
body += text(24, 240, 'Speaking invitations', 23, MUTED)
body += rect(18, 265, 564, 77, YELLOW, YELLOW, 12)
body += f'<g transform="translate(276 277)" stroke="{INK}" stroke-width="2" fill="none" stroke-linecap="round"><rect x="16" y="0" width="18" height="34" rx="9"/><path d="M8 23v7a17 17 0 0 0 34 0v-7M25 47v10m-10 0h20"/></g>'
save('speaking-card-mobile.svg', 600, 360, 'Sessionize — Practical talks and working demonstrations. View session abstracts, event history and speaking invitations.', body)

body = f'<defs><clipPath id="card"><rect x="1" y="1" width="1198" height="216" rx="22"/></clipPath></defs>'
body += rect(1, 1, 1198, 216, radius=22)
body += f'<rect x="825" y="1" width="374" height="216" fill="{LEAF}" clip-path="url(#card)"/>'
body += text(34, 39, 'WRITING / VISUALIZERS / RESEARCH', 13, MUTED, family=MONO)
body += text(31, 104, 'guptasachinn.com', 47, weight=600, family='Arial', extra='letter-spacing="-1.5"')
body += text(34, 152, 'Engineering ideas, explained through', 23, MUTED)
body += text(34, 183, 'examples you can explore.', 23, MUTED)
body += rect(894, 44, 230, 143, WHITE, '#bcc7a0', 12)
body += line(894, 73, 1124, 73, '#d5dac7')
for x in [910, 923, 936]:
    body += f'<circle cx="{x}" cy="59" r="3" fill="{MUTED}"/>'
body += text(913, 108, 'guptasachinn.com', 20, weight=500)
body += f'<path d="M914 130h165m-165 15h128m-128 15h147" stroke="{LINE}" stroke-width="5" stroke-linecap="round"/>'
save('website-card.svg', 1200, 218, 'Visit guptasachinn.com — Engineering writing, interactive visualizers and research.', body)

body = rect(1, 1, 598, 398, radius=22)
body += text(24, 38, 'WRITING / VISUALIZERS / RESEARCH', 17, MUTED, family=MONO)
body += text(22, 108, 'guptasachinn.com', 50, weight=600, family='Arial', extra='letter-spacing="-1.5"')
body += text(24, 159, 'Engineering ideas, explained through', 24, MUTED)
body += text(24, 194, 'examples you can explore.', 24, MUTED)
body += rect(18, 224, 564, 158, LEAF, LEAF, 12)
body += rect(165, 243, 270, 120, WHITE, '#bcc7a0', 10)
body += line(165, 272, 435, 272, '#d5dac7')
for x in [182, 195, 208]:
    body += f'<circle cx="{x}" cy="257" r="3" fill="{MUTED}"/>'
body += text(185, 307, 'guptasachinn.com', 23, weight=500)
body += f'<path d="M186 329h170m-170 16h139" stroke="{LINE}" stroke-width="5" stroke-linecap="round"/>'
save('website-card-mobile.svg', 600, 400, 'Visit guptasachinn.com — Engineering writing, interactive visualizers and research.', body)

# Portfolio website: separate destination from the engineering writing site.
body = '<defs><clipPath id="portfolio-card"><rect x="1" y="1" width="1198" height="216" rx="22"/></clipPath></defs>'
body += rect(1, 1, 1198, 216, radius=22)
body += f'<rect x="825" y="1" width="374" height="216" fill="{YELLOW}" clip-path="url(#portfolio-card)"/>'
body += text(34, 39, 'PROJECTS / RESEARCH / SPEAKING', 13, MUTED, family=MONO)
body += text(31, 104, 'sachinkg12.github.io', 45, weight=600, family='Arial', extra='letter-spacing="-1.5"')
body += text(34, 152, 'Projects, papers, talks, and career background.', 23, MUTED)
body += rect(892, 43, 240, 143, WHITE, '#d9bd66', 12)
body += text(915, 81, 'Sachin Gupta', 24, weight=500)
body += text(915, 117, 'Projects · Research', 18, MUTED)
body += text(915, 146, 'Speaking · About', 18, MUTED)
save('portfolio-card.svg', 1200, 218, 'sachinkg12.github.io — Projects, papers, talks, and career background.', body)

body = rect(1, 1, 598, 398, radius=22)
body += text(24, 38, 'PROJECTS / RESEARCH / SPEAKING', 17, MUTED, family=MONO)
body += text(22, 108, 'sachinkg12.github.io', 48, weight=600, family='Arial', extra='letter-spacing="-1.5"')
body += text(24, 159, 'Projects, papers, talks,', 24, MUTED)
body += text(24, 194, 'and career background.', 24, MUTED)
body += rect(18, 224, 564, 158, YELLOW, YELLOW, 12)
body += rect(165, 243, 270, 120, WHITE, '#d9bd66', 10)
body += text(185, 283, 'Sachin Gupta', 25, weight=500)
body += text(185, 318, 'Projects · Research', 22, MUTED)
body += text(185, 347, 'Speaking · About', 22, MUTED)
save('portfolio-card-mobile.svg', 600, 400, 'sachinkg12.github.io — Projects, papers, talks, and career background.', body)

from profile_metrics import write_metrics
write_metrics()

# Keep native, selectable tables. Small images supply the matching type and pills.
for name, label, width in [('work', 'WORK', 180), ('focus', 'RESEARCH FOCUS', 260), ('venue', 'VENUE & STATUS', 200), ('paper', 'PAPER', 112), ('project', 'PROJECT', 180), ('built', 'WHAT I BUILT', 400), ('code', 'CODE', 112), ('review-venue', 'VENUE', 180), ('review-role', 'RESEARCH SERVICE', 560)]:
    body = rect(0, 0, width, 36, WHITE, WHITE, 0)
    body += text(2, 24, label, 14, weight=500, family=MONO)
    save(f'tables/header-{name}.svg', width, 36, label, body)

for name, label, width in [('published', 'PUBLISHED', 102), ('accepted', 'ACCEPTED', 102), ('reviewer', 'REVIEWER', 100), ('area-chair', 'AREA CHAIR', 114), ('artifacts', 'ARTIFACT EVALUATION', 186)]:
    published = name in ['published', 'reviewer', 'area-chair']
    body = rect(.5, .5, width-1, 23, '#f3f7ed' if published else WHITE, '#cad8c5' if published else LINE, 4)
    body += text(width/2, 16, label, 11, FOREST if published else INK, weight=500, family=MONO, extra='text-anchor="middle"')
    save(f'tables/badge-{name}.svg', width, 24, label.title(), body)

for name, label in [('paper', 'Read paper'), ('arxiv', 'arXiv'), ('code', 'View code')]:
    primary = name == 'paper'
    body = rect(.5, .5, 115, 33, INK if primary else WHITE, INK if primary else LINE, 17)
    body += text(58, 22, label, 15, WHITE if primary else INK, weight=500, extra='text-anchor="middle"')
    save(f'tables/action-{name}.svg', 116, 34, label, body)

from profile_headers import build_headers
build_headers()

print(f'Created {len(list(out.rglob("*.svg")))} self-contained SVG assets in {out}')
