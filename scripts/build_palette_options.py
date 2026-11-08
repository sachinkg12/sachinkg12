#!/usr/bin/env python3
"""Build local color studies from approved assets without changing the profile."""
from pathlib import Path
from html import escape
import argparse
import re
import json
import xml.etree.ElementTree as ET

from profile_typography import outline_svg

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=Path, required=True)
args = parser.parse_args()
output = args.output_dir.resolve()
repo = Path(__file__).resolve().parent.parent
assets = repo / 'assets/profile'
applied_theme = json.loads((assets / 'theme.json').read_text())
SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)

themes = [
    dict(id='navy-teal', name='Navy & teal', note='Recommended',
         why='A clear technical identity with warmth in the small details.',
         ink='#102333', base='#102333', base2='#0c1926', primary='#0f766e',
         highlight='#76dfd0', mist='#f3f8f7', border='#ccded9', accent='#f97316',
         light='#b9d9d4', cloud=['#76dfd0','#beddd8','#e5eef0']),
    dict(id='charcoal-orange', name='Charcoal & orange', note='More expressive',
         why='A sharper developer-tool feel, with orange concentrated in actions.',
         ink='#20282e', base='#20282e', base2='#151c22', primary='#f97316',
         highlight='#ffad75', mist='#f6f7f8', border='#d9dfe2', accent='#f97316',
         light='#cbd3d8', cloud=['#ffad75','#f1d6c3','#e7ecef']),
    dict(id='forest', name='Forest & slate', note='Quieter alternative',
         why='A composed, distinctive direction for research and community work.',
         ink='#163029', base='#163029', base2='#0e211c', primary='#176447',
         highlight='#8fdeb9', mist='#f3f7f4', border='#d0dfd4', accent='#facc15',
         light='#bfd7c8', cloud=['#8fdeb9','#bfd7c8','#e6eee8']),
]
for theme in themes:
    theme['note'] = 'Applied' if theme['id'] == applied_theme['id'] else 'Alternative'


def write_asset(theme, name, svg):
    destination = output / 'palette-options' / theme['id'] / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(svg)


def recolor(theme, name):
    root = ET.fromstring((assets / name).read_text())
    t = theme
    mapping = {
        '#101d33':t['base'], '#0b1425':t['base2'], '#101e34':t['base'], '#10192c':t['base2'],
        '#162b3a':t['base2'], '#18313e':t['base2'], '#31515e':t['primary'],
        '#4ac3b0':t['highlight'], '#5eead4':t['highlight'],
        '#0d9488':t['light'] if t['id']=='charcoal-orange' else t['primary'],
        '#38b6a4':t['light'] if t['id']=='charcoal-orange' else t['primary'],
        '#2c405c':t['primary'], '#2b405a':t['primary'],
        '#92a8be':t['light'], '#94a8bd':t['light'], '#c4d0df':t['light'],
        '#8ba6bf':t['light'], '#aabbd0':t['light'], '#91a7bf':t['light'],
    }
    mapping.update({applied_theme[token]:t[token] for token in ['ink','base','base2','primary','highlight','mist','border','accent','light']})
    if name.startswith('credentials'):
        mapping.update({c:t['mist'] for c in ['#fefce8','#fff7ed','#f0f9ff']})
        mapping.update({c:t['border'] for c in ['#fde047','#fdba74','#bae6fd']})
        mapping.update({c:t['ink'] for c in ['#0f766e','#ea580c','#075985']})
    if name.startswith('tables/'):
        mapping.update({'#101d33':t['ink'], '#f97316':t['primary'], '#fb923c':t['accent'],
                        '#d5f6ed':t['mist'], '#a7dfd2':t['border'], '#0f766e':t['ink'],
                        '#ffedd5':t['mist'], '#172033':t['ink'],
                        '#fef9c3':t['mist'], '#facc15':t['accent']})
    if name.startswith('wordcloud'):
        old=['#5eead4','#fb923c','#7dd3fc','#fde047','#ff6b5f','#a7f3d0','#e2e8f0']
        mapping.update({color:t['cloud'][i % 3] for i,color in enumerate(old)})
        mapping.update({color:t['cloud'][i] for i,color in enumerate(applied_theme['cloud'])})
    for element in root.iter():
        for attr in ['fill','stroke','stop-color']:
            color=element.get(attr)
            if color in mapping:
                element.set(attr,mapping[color])
        # The original hand remains yellow. The three decorative banner strokes
        # become a single accent, rather than a row of competing colors.
        if element.tag == f'{{{SVG}}}path' and re.match(r'M(?:48|86|124|32|64|96) 0h',element.get('d','')):
            element.set('stroke',t['primary'])
        if name.startswith('credentials') and element.tag == f'{{{SVG}}}rect' and element.get('width')=='3':
            element.set('fill',t['primary'])
    write_asset(t,name,ET.tostring(root,encoding='unicode'))


def link_button(theme,key,label,marker):
    t=theme
    primary=key=='website'
    fill=t['primary'] if primary else '#ffffff'
    ink=(t['ink'] if t['id']=='charcoal-orange' else '#ffffff') if primary else t['ink']
    border=t['primary'] if primary else t['border']
    body=f'<rect x=".5" y=".5" width="269" height="49" rx="9" fill="{fill}" stroke="{border}"/>'
    if not primary:
        body+=f'<rect x="1" y="12" width="3" height="26" rx="1.5" fill="{marker}"/>'
    body+=f'<text x="17" y="31" fill="{ink}" font-family="Manrope" font-size="17" font-weight="550">{escape(label)}</text>'
    body+=f'<path d="M231 25h18m-6-6 6 6-6 6" stroke="{ink}" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    write_asset(t,f'link-{key}.svg',outline_svg(f'<svg xmlns="{SVG}" width="270" height="50" viewBox="0 0 270 50" role="img"><title>{escape(label)}</title>{body}</svg>'))


link_specs=[('website','My website','#0f766e','https://www.guptasachinn.com/'),
            ('sessionize','Sessionize','#facc15','https://sessionize.com/sachin-gupta/'),
            ('scholar','Google Scholar','#f97316','https://scholar.google.com/citations?user=sVZi4aoAAAAJ&hl=en'),
            ('linkedin','LinkedIn','#0a66c2','https://www.linkedin.com/in/guptasachin1/')]
names=['cover.svg','cover-mobile.svg','credentials.svg','credentials-mobile.svg','wordcloud.svg','wordcloud-mobile.svg']
names += [f'tables/{name}.svg' for name in ['header-work','header-focus','header-venue','header-paper','badge-published','badge-accepted','action-paper','action-arxiv']]
index=(output/'index.html').read_text()
research=re.search(r'<div class="table-scroll"><table>.*?</table></div>',index,re.S).group(0)
approved_intro=''.join(re.findall(r'<p>.*?</p>',index,re.S)[:2]).replace('<p>','<p class="sample-intro">')
panels=[]
tabs=[]
for i,t in enumerate(themes):
    for name in names: recolor(t,name)
    for key,label,marker,url in link_specs: link_button(t,key,label,marker)
    base=f'./palette-options/{t["id"]}/'
    def picture(name,alt):
        stem=name.removesuffix('.svg')
        return f'<picture><source media="(max-width:600px)" srcset="{base}{stem}-mobile.svg"/><img src="{base}{name}" alt="{escape(alt)}" width="100%"/></picture>'
    links=''.join(f'<a href="{escape(url,quote=True)}"><img src="{base}link-{key}.svg" alt="{label}" width="270" height="50"/></a>' for key,label,marker,url in link_specs)
    table=re.sub(r'\./assets/profile/([^"?]+)(?:\?v=\d+)?',lambda m:base+m.group(1),research)
    swatches=''.join(f'<span><i style="background:{t[k]}"></i>{label}<code>{t[k].upper()}</code></span>' for k,label in [('base','Foundation'),('primary','Primary'),('mist','Surface'),('accent','Small accent')])
    active = t['id'] == applied_theme['id']
    tabs.append(f'<button type="button" data-theme="{t["id"]}" aria-pressed="{"true" if active else "false"}"><i style="background:{t["primary"]}"></i><span>{t["name"]}<small>{t["note"]}</small></span></button>')
    panels.append(f'''<section class="palette-panel" id="{t['id']}" {'' if active else 'hidden'}>
<div class="direction"><h2>{t['name']}</h2><p>{t['why']}</p><div class="swatches">{swatches}</div></div>
<div class="sample">{picture('cover.svg','Sachin Gupta banner — '+t['name'])}{picture('credentials.svg','15+ years, 9 accepted papers, eBay Monetization')}
{approved_intro}
<div class="profile-links">{links}</div>
<details><summary>Research table in this palette</summary>{table}</details>
<details><summary>Word cloud in this palette</summary>{picture('wordcloud.svg','Community word cloud — '+t['name'])}</details>
</div></section>''')

css='''*{box-sizing:border-box}[hidden]{display:none!important}body{margin:0;background:#f5f7f9;color:#172033;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}.shell{max-width:1080px;margin:auto;padding:26px 24px 48px}a{color:#0f766e;text-decoration:none}h1{font-size:30px;letter-spacing:-.8px;line-height:1.2;margin:16px 0 12px}.intro{max-width:820px;color:#536278;margin:0 0 20px}.eyebrow{font:10px ui-monospace,Consolas,monospace;letter-spacing:1.2px;color:#526570}.feedback{padding:16px 20px;border:1px solid #ccded9;border-left:4px solid #0f766e;border-radius:10px;background:#fff;margin-bottom:22px;font-size:14px}.feedback p{margin:0}.feedback p+p{margin-top:7px}.theme-tabs{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:20px}.theme-tabs button{display:flex;align-items:center;gap:12px;text-align:left;background:#fff;border:1px solid #d3dce2;border-radius:10px;padding:14px 16px;color:#172033;font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;cursor:pointer}.theme-tabs button[aria-pressed="true"]{border:2px solid #0f766e;padding:13px 15px;background:#f3f8f7}.theme-tabs i{width:24px;height:24px;border-radius:50%;flex-shrink:0}.theme-tabs small{display:block;font-size:11px;font-weight:400;color:#64748b;margin-top:3px}.palette-panel{border:1px solid #d3dce2;border-radius:14px;background:#fff;overflow:hidden}.direction{padding:20px 24px;border-bottom:1px solid #e2e8ee}.direction h2{font-size:21px;margin:0 0 4px}.direction p{color:#536278;font-size:14px;margin:0 0 16px}.swatches{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.swatches>span{font-size:12px;display:grid;grid-template-columns:30px 1fr;column-gap:9px;align-items:center}.swatches i{width:30px;height:30px;border-radius:7px;border:1px solid #d4dde3;grid-row:span 2}.swatches code{font-size:10px;color:#64748b}.sample{padding:24px}.sample picture,.sample picture img{display:block;width:100%;height:auto}.sample picture{margin-bottom:12px}.sample-intro{font-size:15px;margin:18px 0}.profile-links{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:18px 0 22px}.profile-links img{display:block;width:100%;height:auto}.sample details{border-top:1px solid #e2e8ee;padding:14px 0 0;margin-top:14px}.sample summary{cursor:pointer;font-size:14px;font-weight:600;color:#334155}.sample details[open] summary{margin-bottom:14px}.table-scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:13px;line-height:1.5}td,th{border:1px solid #d1d9e0;padding:10px 12px;text-align:left;vertical-align:top}th,tr:nth-child(even){background:#f6f8fa}td[align="center"],th[align="center"]{text-align:center}table sub{font-size:11px;color:#59636e;vertical-align:baseline}table strong{font-weight:600}.footer{font-size:12px;color:#64748b;margin-top:16px}@media(max-width:650px){.shell{padding:20px 12px}.theme-tabs{grid-template-columns:1fr}.theme-tabs button{padding:11px 13px}.theme-tabs button[aria-pressed="true"]{padding:10px 12px}.direction,.sample{padding:18px}.swatches{grid-template-columns:repeat(2,1fr)}.profile-links{grid-template-columns:repeat(2,minmax(0,1fr))}h1{font-size:26px}}'''
page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sachin Gupta — color directions</title><style>{css}</style></head><body><main class="shell"><a href="./index.html">← Current profile preview</a><h1>Color directions for your profile</h1><p class="intro">The same portrait, typography, content, and layout with a more deliberate use of color. Select a direction below to compare.</p><aside class="feedback"><p><strong>Applied direction:</strong> Forest &amp; Slate. Deep forest backgrounds, slate text, neutral stat cards, and restrained accents.</p><p><strong>Compare alternatives:</strong> use the tabs below to inspect the other directions. The main profile keeps your chosen Forest &amp; Slate palette.</p></aside><div class="theme-tabs" aria-label="Choose a color direction">{''.join(tabs)}</div>{''.join(panels)}<p class="footer">Forest &amp; Slate is applied to the profile draft. These comparisons do not change it. Nothing is published.</p></main><script>for(const button of document.querySelectorAll('[data-theme]')){{button.addEventListener('click',()=>{{for(const tab of document.querySelectorAll('[data-theme]'))tab.setAttribute('aria-pressed',String(tab===button));for(const panel of document.querySelectorAll('.palette-panel'))panel.hidden=panel.id!==button.dataset.theme;}});}}</script></body></html>'''
def version(match):
    attr,path=match.groups()
    stamp=(output/path.removeprefix('./')).stat().st_mtime_ns
    return f'{attr}="{path}?v={stamp}"'
page=re.sub(r'(src|srcset)="(\./palette-options/[^"?]+)"',version,page)
(output/'palette-options.html').write_text(page)
print(f'Built {len(themes)} independent color studies: {output / "palette-options.html"}')
