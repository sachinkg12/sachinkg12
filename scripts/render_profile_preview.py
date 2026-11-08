from pathlib import Path
import html
import re
import shutil
import argparse
import tempfile
import json

parser = argparse.ArgumentParser(description='Render a local preview of the GitHub profile README.')
parser.add_argument('--output-dir', type=Path, default=Path(tempfile.gettempdir()) / 'sachin-github-redesign')
args = parser.parse_args()
root = args.output_dir.resolve()
root.mkdir(parents=True, exist_ok=True)
source = Path(__file__).resolve().parent.parent / 'README.md'
text = source.read_text()
theme = json.loads((source.parent / 'assets/profile/theme.json').read_text())
link_number = 0

def inline(value):
    global link_number
    image_tags = []
    def image_tag(match):
        image_tags.append(match.group(0))
        return f'IMAGETOKEN{len(image_tags)-1}ENDTOKEN'
    value = re.sub(r'<img\s+[^>]*?/?>|</?(?:br|sub|sup|strong|code)\b[^>]*>', image_tag, value)
    value = html.escape(value, quote=False)
    def link(match):
        global link_number
        link_number += 1
        label, url = match.groups()
        url = html.unescape(url)
        slug = re.sub(r'[^a-z0-9]+', '-', re.sub(r'\*', '', label).lower()).strip('-')
        return f'<a id="{slug}-{link_number}" class="text-[#0969da] hover:underline" href="{html.escape(url, quote=True)}">{label}</a>'
    value = re.sub(r'\[([^\]]+)\]\((https://[^\s)]+)\)', link, value)
    value = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', value)
    for index, tag in enumerate(image_tags):
        value = value.replace(f'IMAGETOKEN{index}ENDTOKEN', tag)
    return value

lines = text.splitlines()
blocks = []
i = 0
while i < len(lines):
    line = lines[i]
    if not line.strip():
        i += 1
        continue
    if line.startswith(('<picture>', '<p ', '<p>')):
        close_tag = '</picture>' if line.startswith('<picture>') else '</p>'
        raw = [line]
        i += 1
        while close_tag not in raw[-1] and i < len(lines):
            raw.append(lines[i])
            i += 1
        blocks.append('\n'.join(raw))
    elif line.startswith('<img ') and line.endswith('/>'):
        blocks.append(line)
        i += 1
    elif line == '---':
        blocks.append('<hr class="my-6 border-0 bg-[#d1d9e0]"/>')
        i += 1
    elif line.startswith('#'):
        marker, content = line.split(' ', 1)
        level = len(marker)
        slug = re.sub(r'[^a-z0-9]+', '-', re.sub(r'<[^>]+>', '', content).lower()).strip('-')
        blocks.append(f'<h{level} id="{slug}">{inline(content)}</h{level}>')
        i += 1
    elif line.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].startswith('|'):
            rows.append([cell.strip() for cell in lines[i].strip().strip('|').split('|')])
            i += 1
        alignments = ['center' if cell.startswith(':') and cell.endswith(':') else 'right' if cell.endswith(':') else 'left' for cell in rows[1]]
        head = '<tr>' + ''.join(f'<th align="{alignments[col]}">{inline(cell)}</th>' for col, cell in enumerate(rows[0])) + '</tr>'
        body = ''.join('<tr>' + ''.join(f'<td align="{alignments[col]}">{inline(cell)}</td>' for col, cell in enumerate(row)) + '</tr>' for row in rows[2:])
        blocks.append(f'<div class="table-scroll"><table><thead>{head}</thead><tbody>{body}</tbody></table></div>')
    elif line.startswith('- '):
        items = []
        while i < len(lines) and lines[i].startswith('- '):
            items.append(f'<li>{inline(lines[i][2:])}</li>')
            i += 1
        blocks.append('<ul>' + ''.join(items) + '</ul>')
    elif line.startswith('<sub>') and line.endswith('</sub>'):
        blocks.append('<p class="small-note"><sub>' + inline(line[5:-6]) + '</sub></p>')
        i += 1
    else:
        paragraph = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(('#', '|', '- ', '<sub>', '---')):
            paragraph.append(lines[i])
            i += 1
        blocks.append('<p>' + inline(' '.join(paragraph)) + '</p>')

content = '\n'.join(blocks)
demo = '''<section class="cloud-demo" data-cloud-demo aria-label="Try the word cloud locally">
<div class="cloud-demo-heading"><strong>Try the cloud</strong><span>LOCAL PREVIEW</span></div>
<form><label for="cloud-word">Add a topic or shared interest</label><div class="cloud-form-row"><input id="cloud-word" name="word" maxlength="60" placeholder="e.g. AI Agents, Photography" autocomplete="off" required/><button type="submit">Add my word <span aria-hidden="true">↗</span></button></div></form>
<div class="cloud-demo-actions"><button type="button" data-shuffle-cloud>Shuffle arrangement</button><button type="button" data-reset-cloud>Reset demo</button></div>
<p role="status" aria-live="polite">Try adding a word. Preview changes stay in this browser.</p>
</section>'''
content = re.sub(r'(<picture>\s*<source[^>]+wordcloud-mobile\.svg[^>]+/>\s*<img[^>]+wordcloud\.svg[^>]+/>\s*</picture>)', lambda m: m.group(1).replace('<picture>', '<picture data-cloud-picture>') + demo, content)
css = '''
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f6f8fa;color:#1f2328}.preview-root{min-height:100vh;padding:30px 24px 48px}.preview-shell{max-width:1012px;margin:auto}.preview-label{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;font-size:13px;color:#59636e}.draft-tag{font:11px ui-monospace,SFMono-Regular,monospace;letter-spacing:.08em;background:#fef9c3;color:#172033;border:1px solid #facc15;padding:5px 9px;border-radius:20px}.readme-panel{background:#fff;border:1px solid #d1d9e0;border-radius:12px;overflow:hidden}.file-header{padding:13px 32px;border-bottom:1px solid #d1d9e0;background:#f6f8fa;font:13px ui-monospace,SFMono-Regular,monospace;display:flex;align-items:center;gap:10px}.file-dot{display:inline-block;width:9px;height:11px;border:1px solid #59636e;border-radius:1px}.markdown-body{padding:28px 32px 32px;font-size:16px;line-height:1.6;overflow-wrap:break-word}.markdown-body>:first-child{margin-top:0}.markdown-body h1,.markdown-body h2,.markdown-body h3{line-height:1.25;font-weight:600;margin:24px 0 16px}.markdown-body h1{font-size:32px;border-bottom:1px solid #d8dee4;padding-bottom:9px;letter-spacing:-.5px}.markdown-body h2{font-size:24px;border-bottom:1px solid #d8dee4;padding-bottom:7px;letter-spacing:-.25px}.markdown-body h3{font-size:20px}.markdown-body p{margin:0 0 16px}.markdown-body a{color:#0969da;text-decoration:none}.markdown-body a:hover{text-decoration:underline}.markdown-body strong{font-weight:600}.markdown-body hr{height:3px;border:0;background:#d1d9e0;margin:24px 0}.markdown-body sub{font-size:12px;line-height:1.5;color:#59636e;vertical-align:baseline}.markdown-body ul{padding-left:2em;margin-top:0;margin-bottom:16px}.markdown-body li+li{margin-top:4px}.table-scroll{overflow:auto;margin-bottom:16px}.markdown-body table{width:100%;border-collapse:collapse;font-size:14px;line-height:1.5}.markdown-body th,.markdown-body td{padding:10px 12px;border:1px solid #d1d9e0;text-align:left;vertical-align:top}.markdown-body th{font-weight:600;background:#f6f8fa}.markdown-body tr:nth-child(even){background:#f6f8fa}.markdown-body th:first-child{width:22%}.markdown-body th:last-child{width:21%}.preview-footer{padding:16px 0;font-size:12px;color:#59636e;text-align:center}@media(max-width:650px){.preview-root{padding:14px 10px}.markdown-body{padding:20px 18px}.file-header{padding:12px 18px}.markdown-body h1{font-size:28px}.markdown-body h2{font-size:22px}.markdown-body table{font-size:13px;min-width:540px}.preview-label{font-size:11px}.draft-tag{font-size:10px}}
'''
css += '.markdown-body img[align="right"]{float:right;margin:0 0 18px 24px;max-width:120px;height:auto}.markdown-body h2{clear:both}.markdown-body h1{margin-top:0}.markdown-body th:first-child{width:24%}.markdown-body th:last-child{width:auto}@media(max-width:650px){.markdown-body img[align="right"]{width:84px;margin-left:14px}.markdown-body h3{font-size:18px}}'
css += '''
.markdown-body>picture{display:block;margin:0 0 14px;clear:both}.markdown-body>picture>img{display:block;max-width:100%;height:auto}.markdown-body p>a>img{max-width:100%;vertical-align:middle}.markdown-body p[align="left"]{line-height:2.8}.markdown-body h2 img{vertical-align:middle;margin-right:5px}.markdown-body p>a>img[width="100%"]{display:block;height:auto}.preview-controls{display:flex;align-items:center;gap:10px}.theme-toggle{border:1px solid #d1d9e0;background:#fff;color:#334155;border-radius:7px;padding:5px 10px;font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;cursor:pointer}.dark-preview{background:#010409;color:#e6edf3}.dark-preview .preview-root{background:#010409;color:#e6edf3}.dark-preview .readme-panel{background:#0d1117;border-color:#30363d}.dark-preview .file-header{background:#161b22;border-color:#30363d}.dark-preview .preview-label,.dark-preview .preview-footer,.dark-preview .markdown-body sub{color:#8b949e}.dark-preview .markdown-body h1,.dark-preview .markdown-body h2{border-color:#30363d}.dark-preview .markdown-body hr{background:#30363d}.dark-preview .markdown-body a{color:#58a6ff}.dark-preview .markdown-body th,.dark-preview .markdown-body td{border-color:#30363d}.dark-preview .markdown-body th,.dark-preview .markdown-body tr:nth-child(even){background:#161b22}.dark-preview .theme-toggle{background:#161b22;border-color:#30363d;color:#e6edf3}.dark-preview .draft-tag{background:#172033;border-color:#facc15;color:#fde047}@media(max-width:650px){.draft-tag{font-size:9px}.preview-controls{gap:5px}.preview-label{gap:8px}.theme-toggle{font-size:11px;padding:5px 7px}.markdown-body p[align="left"] img{width:calc(50% - 5px);height:auto}}
'''
css += '''
.cloud-demo{padding:20px 22px;border:1px solid #b8e3d9;border-radius:12px;background:#f0fdfa;margin:-2px 0 18px}.cloud-demo-heading{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}.cloud-demo-heading strong{font-size:17px}.cloud-demo-heading>span{font:10px ui-monospace,Consolas,monospace;letter-spacing:1.2px;color:#0f766e}.cloud-demo label{display:block;font-size:13px;font-weight:600;margin-bottom:7px}.cloud-form-row{display:flex;gap:9px}.cloud-form-row input{flex:1;min-width:0;padding:11px 12px;border:1px solid #b6cdc9;border-radius:7px;background:white;color:#172033;font:14px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.cloud-form-row input:focus{outline:2px solid #0d9488;outline-offset:2px}.cloud-form-row button{white-space:nowrap;background:#0f766e;color:white;border:0;border-radius:7px;padding:10px 16px;font-size:14px;font-weight:600;cursor:pointer}.cloud-demo-actions{display:flex;gap:16px;margin-top:11px}.cloud-demo-actions button{padding:0;background:none;border:0;color:#0f766e;text-decoration:underline;text-underline-offset:3px;cursor:pointer;font-size:12px}.cloud-demo p[role="status"]{font-size:12px;color:#526b66;line-height:1.5;margin:12px 0 0;min-height:18px}.markdown-body picture[data-cloud-picture]{display:block;margin-bottom:14px}.markdown-body picture[data-cloud-picture] img{display:block;width:100%;height:auto}.dark-preview .cloud-demo{background:#102625;border-color:#23574e}.dark-preview .cloud-demo-heading>span,.dark-preview .cloud-demo-actions button{color:#5eead4}.dark-preview .cloud-demo p[role="status"]{color:#adc8c2}.dark-preview .cloud-form-row input{background:#0d1a1f;border-color:#356059;color:#e6edf3}.font-link{color:#0f766e;text-decoration:none;font-size:12px}.font-link:hover{text-decoration:underline}.dark-preview .font-link{color:#5eead4}.preview-label{flex-wrap:wrap;row-gap:10px}@media(max-width:650px){.cloud-demo{padding:16px}.cloud-form-row{flex-wrap:wrap}.cloud-form-row input{width:100%;flex-basis:100%}.cloud-form-row button{width:100%}.cloud-demo-actions{justify-content:space-between;gap:10px}.font-link{font-size:11px}}
'''
css += '.markdown-body th[align="center"],.markdown-body td[align="center"]{text-align:center}.markdown-body th[align="right"],.markdown-body td[align="right"]{text-align:right}'
for old, new in {
    '#0f766e':theme['primary'], '#0d9488':theme['primary'], '#5eead4':theme['highlight'],
    '#172033':theme['ink'], '#f0fdfa':theme['mist'], '#b8e3d9':theme['border'],
    '#b6cdc9':theme['border'], '#526b66':theme['slate'], '#102625':theme['base2'],
    '#23574e':theme['primary'], '#adc8c2':theme['light'], '#0d1a1f':theme['base2'],
    '#356059':theme['primary'], '#fef9c3':theme['mist'], '#facc15':theme['border'],
    '#fde047':theme['highlight'],
}.items():
    css = css.replace(old, new)
page = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sachin Gupta — GitHub profile preview</title><style>{css}</style></head>
<body><div class="preview-root min-h-screen bg-[#f6f8fa] text-[#1f2328]"><div class="preview-shell mx-auto max-w-[1012px]">
<div class="preview-label flex items-center justify-between"><span>sachinkg12 / profile</span><span class="preview-controls"><a class="font-link" href="./font-options.html">Fonts</a><a class="font-link" href="./palette-options.html">Colors</a><button class="theme-toggle" type="button" onclick="document.body.classList.toggle('dark-preview');this.textContent=document.body.classList.contains('dark-preview')?'Light preview':'Dark preview'">Dark preview</button><span class="draft-tag rounded-full">LOCAL PREVIEW</span></span></div>
<main class="readme-panel overflow-hidden rounded-xl border border-[#d1d9e0] bg-white"><div class="file-header flex items-center gap-2"><span class="file-dot"></span>README.md</div><article class="markdown-body">{content}</article></main>
<div class="preview-footer">GitHub README preview · Native text, tables and SVG assets</div>
</div></div><script type="module" src="./assets/profile/wordcloud-preview.mjs"></script></body></html>'''
def version_asset(match):
    attribute, path = match.groups()
    stamp = (source.parent / path).stat().st_mtime_ns
    if path.endswith('/wordcloud-preview.mjs'):
        stamp = max((source.parent / 'assets/profile' / name).stat().st_mtime_ns for name in ['wordcloud-preview.mjs','wordcloud.mjs','theme.json'])
    return f'{attribute}="{path}?v={stamp}"'
page = re.sub(r'(src|srcset)="(\./assets/profile/[^\"]+)"', version_asset, page)
(root / 'index.html').write_text(page)
(root / 'github-profile-preview.html').write_text(page)
(root / 'README.md').write_text(text)
shutil.copytree(source.parent / 'assets/profile', root / 'assets/profile', dirs_exist_ok=True)
font_cards = []
for slug, name, note in [
    ('space-grotesk', 'Space Grotesk', 'Recommended · distinct, technical, and restrained. Currently applied to the banner and display text.'),
    ('manrope', 'Manrope', 'Softer and more understated. Currently used for supporting text in the visual cards.'),
    ('sora', 'Sora', 'A wider, more geometric alternative with a stronger visual presence.'),
]:
    font_cards.append(f'''<section class="option"><div class="option-heading"><h2>{name}</h2><span>{'APPLIED' if slug == 'space-grotesk' else 'ALTERNATIVE'}</span></div><p>{note}</p><picture><source media="(max-width:600px)" srcset="./assets/profile/font-options/{slug}-mobile.svg"/><img src="./assets/profile/font-options/{slug}.svg" alt="Sachin Gupta banner in {name}" width="1200" height="274"/></picture></section>''')
font_page = '''<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Sachin Gupta — font comparison</title><style>*{box-sizing:border-box}body{margin:0;background:#f4f7fa;color:#172033;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}.shell{max-width:1040px;margin:0 auto;padding:30px 22px 44px}a{color:#0f766e;text-decoration:none}h1{font-size:28px;letter-spacing:-.7px;margin:18px 0 8px}.intro{max-width:760px;color:#536278;margin:0 0 22px}.option{background:#fff;border:1px solid #d8e0e8;border-radius:14px;margin:0 0 20px;padding:20px}.option-heading{display:flex;align-items:center;justify-content:space-between;gap:12px}.option h2{font-size:20px;margin:0}.option-heading span{font:10px ui-monospace,Consolas,monospace;letter-spacing:1.3px;color:#0f766e}.option p{font-size:14px;color:#536278;margin:8px 0 16px}.option picture,.option img{display:block;width:100%;height:auto}.note{font-size:13px;color:#536278}@media(max-width:600px){.shell{padding:20px 12px}.option{padding:16px}h1{font-size:25px}.option p{font-size:13px}}</style></head><body><main class="shell"><a href="./index.html">← Back to the profile preview</a><h1>Three fonts. The same profile.</h1><p class="intro">The portrait, colors, content, and layout stay the same so you can compare the typography. My choice is Space Grotesk for display text, Manrope for supporting text, and IBM Plex Mono for small technical labels.</p>'''+''.join(font_cards)+'''<p class="note">These are the actual SVG assets, with the fonts converted to vector outlines. GitHub's normal README text retains GitHub's font. This comparison is a local preview.</p></main></body></html>'''
(root / 'font-options.html').write_text(re.sub(r'(src|srcset)="(\./assets/profile/[^\"]+)"', version_asset, font_page))
print(f'Wrote preview: {root}/index.html')
print(f'{len(text.split())} words; {link_number} descriptive links; {len(lines)} lines')
