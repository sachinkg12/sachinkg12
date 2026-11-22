"""Render marketplace counts without mixing acquisitions, downloads and installs."""
from datetime import date
from html import escape
import re,json
from profile_graphics import ROOT,OUT,text,rect,document,INK,MUTED,LINE,WHITE,LEAF,MONO
from profile_headers import heading_markup

START,END='<!-- heaplens-stats:start -->','<!-- heaplens-stats:end -->'


def long_date(value):
    d=date.fromisoformat(value)
    return f'{d:%B} {d.day}, {d.year}'


def description(data):
    return (f"HeapLens — VS Code: {data['vscode_acquisitions']:,} acquisitions. "
            f"Open VSX: {data['openvsx_downloads']:,} downloads. IntelliJ IDEA: {data['jetbrains_downloads']:,} downloads.")


def render_assets(data):
    label=description(data)
    entries=[('VS Code',data['vscode_acquisitions'],'Acquisitions','Publisher dashboard',data['vscode_acquisitions_as_of']),
             ('Open VSX',data['openvsx_downloads'],'Downloads','Public API',data['as_of']),
             ('IntelliJ IDEA',data['jetbrains_downloads'],'Downloads','Public API',data['as_of'])]
    body=text(2,28,'HEAPLENS / MARKETPLACE ACTIVITY',15,MUTED,family=MONO)
    for i,(name,count,kind,source,recorded) in enumerate(entries):
        x=i*408
        body+=rect(x+1,52,382,196,LEAF if i==0 else WHITE,LEAF if i==0 else LINE,18)
        body+=text(x+25,89,name,23,weight=500)
        body+=text(x+23,152,f'{count:,}',53,weight=500)
        body+=text(x+25,186,kind+' · '+source,17,MUTED)
        body+=text(x+25,219,long_date(recorded),17,MUTED)
    desktop=document(1200,260,label,body)
    body=text(2,30,'HEAPLENS / MARKETPLACE ACTIVITY',18,MUTED,family=MONO)
    for i,(name,count,kind,source,recorded) in enumerate(entries):
        y=54+i*145
        body+=rect(1,y,598,130,LEAF if i==0 else WHITE,LEAF if i==0 else LINE,18)
        body+=text(25,y+35,name,24,weight=500)
        body+=text(23,y+100,f'{count:,}',57,weight=500)
        body+=text(297,y+37,kind,24,weight=500)
        body+=text(297,y+73,source,21,MUTED)
        body+=text(297,y+105,long_date(recorded),20,MUTED)
    return {'heaplens-adoption.svg':desktop,'heaplens-adoption-mobile.svg':document(600,494,label,body)}


def render_readme(data,readme):
    block=f'''{START}
{heading_markup('heaplens-marketplace-activity')}

<p>
  <a href="https://github.com/sachinkg12/heaplens"><picture><source media="(max-width: 600px)" srcset="./assets/profile/heaplens-adoption-mobile.svg" /><img src="./assets/profile/heaplens-adoption.svg" width="100%" alt="{escape(description(data),quote=True)}" /></picture></a>
</p>

{END}'''
    if START in readme:
        assert END in readme
        return re.sub(re.escape(START)+r'.*?'+re.escape(END),lambda _:block,readme,flags=re.S)
    image=readme.find('src="./assets/profile/heaplens-adoption.svg"')
    begin=readme.rfind('<p>',0,image)
    end=readme.find('</sub>',image)
    if image<0 or begin<0 or end<0 or '<sub>Snapshot:' not in readme[image:end]:
        raise ValueError('Could not find the HeapLens metrics block in README.md.')
    return readme[:begin]+block+readme[end+len('</sub>'):]


def write_metrics(data=None):
    data=data or json.loads((OUT/'heaplens-distribution.json').read_text())
    images=render_assets(data)
    readme=render_readme(data,(ROOT/'README.md').read_text())
    for name,svg in images.items():
        (OUT/name).write_text(svg)
    (ROOT/'README.md').write_text(readme)
