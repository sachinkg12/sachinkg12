#!/usr/bin/env python3
"""Build responsive research/project rows and the keynote highlight.

All links remain real HTML anchors in README.md; each image has a complete
accessible label. Research and project descriptions come from the existing record.
"""
from html import escape
import json,re
from profile_graphics import ROOT,OUT,text,rect,paragraph,pill,save,INK,MUTED,LINE,WHITE,LEAF,YELLOW,FOREST,MONO


def picture(name, alt, url=None):
    content=f'<picture><source media="(max-width: 600px)" srcset="./assets/profile/{name}-mobile.svg" /><img src="./assets/profile/{name}.svg" width="100%" alt="{escape(alt,quote=True)}" /></picture>'
    return '<p>'+ (f'<a href="{escape(url,quote=True)}">{content}</a>' if url else content) + '</p>'


def replace_section(source, marker, content, table=False):
    start,end=f'<!-- {marker}:start -->',f'<!-- {marker}:end -->'
    block=start+'\n'+content+'\n'+end
    if start in source:
        if end not in source:
            raise ValueError(f'Incomplete {marker} section markers in README.md.')
        return re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda _:block,source,flags=re.S)
    if table:
        titles={'research':'Research — 9 accepted papers','projects':'Open-source work','reviewing':'Reviewing & research service'}
        section=source.index(titles[marker])
        begin=source.index('\n| ',section)+1
        stop=source.index('\n\n',begin)
        return source[:begin]+block+source[stop:]
    heading='## <img src="./assets/profile/icon-speaking.svg" width="28" height="28" alt="" /> Speaking & sessions\n'
    assert heading in source
    return source.replace(heading,heading+'\n'+block+'\n',1)


def research_row(p,index,mobile=False):
    venue=p['display_venue']+' · '+p['display_track'].replace(' · ',' · ')
    status=p['status'].title()
    if mobile:
        desc,bottom=paragraph(26,135,p['focus'],548,29,40)
        venue_text,venue_bottom=paragraph(26,bottom+42,venue,548,26,34)
        footer=venue_bottom+28
        height=footer+72
        body=rect(1,1,598,height-2,radius=18)
        body+=text(26,37,p['category'],19,MUTED)
        body+=text(25,91,p['name'],39,weight=600,family='Arial')
        body+=desc+venue_text
        body+=pill(26,footer,status,143,38,'#f3f7ed' if status=='Published' else WHITE,FOREST if status=='Published' else INK,'#cad8c5' if status=='Published' else LINE,22)
        body+=pill(367,footer-2,'Read paper' if status=='Published' else 'Read arXiv',207,42,INK,WHITE,INK,26)
        return 600,height,body
    height=190
    body=rect(1,1,1198,height-2,radius=18)
    body+=text(28,31,p['category'],16,MUTED)
    body+=text(27,75,p['name'],34,weight=600,family='Arial')
    desc,_=paragraph(28,113,p['focus'],790,23,30)
    body+=desc+text(28,168,venue,18,MUTED)
    body+=pill(935,31,status,205,34,'#f3f7ed' if status=='Published' else WHITE,FOREST if status=='Published' else INK,'#cad8c5' if status=='Published' else LINE,17)
    body+=pill(935,108,'Read paper' if status=='Published' else 'Read arXiv',205,43,INK,WHITE,INK,21)
    return 1200,height,body


def project_row(p,index,mobile=False):
    if mobile:
        desc,bottom=paragraph(26,134,p['description'],548,29,40)
        height=bottom+109
        body=rect(1,1,598,height-2,radius=18)
        body+=text(26,37,p['category'],19,MUTED)+text(25,91,p['name'],40,weight=600,family='Arial')+desc
        body+=pill(26,bottom+30,'View code',190,44,INK,WHITE,INK,26)
        return 600,height,body
    desc,bottom=paragraph(28,111,p['description'],790,23,30)
    height=max(178,bottom+30)
    body=rect(1,1,1198,height-2,radius=18)
    body+=text(28,31,p['category'],16,MUTED)+text(27,73,p['name'],34,weight=600,family='Arial')+desc
    body+=pill(935,(height-43)/2,'View code',205,43,INK,WHITE,INK,21)
    return 1200,height,body


def keynote_card(data,mobile=False):
    if mobile:
        title,bottom=paragraph(26,141,data['title'],548,40,50,INK,600,'Arial')
        summary,summary_bottom=paragraph(26,bottom+51,data['summary'],548,29,40,INK)
        height=summary_bottom+111
        body=rect(1,1,598,height-2,LEAF,LEAF,22)
        body+=pill(26,24,'KEYNOTE SPEAKER',236,34,YELLOW,INK,YELLOW,17)
        body+=text(26,91,data['event']+' · '+data['conference_dates'],21,INK)
        body+=title+summary+pill(26,summary_bottom+33,'Conference talk record',300,44,INK,WHITE,INK,25)
        return 600,height,body
    title,bottom=paragraph(34,113,data['title'],850,46,58,INK,600,'Arial')
    summary,summary_bottom=paragraph(34,bottom+43,data['summary'],850,23,32,INK)
    height=summary_bottom+91
    body=rect(1,1,1198,height-2,LEAF,LEAF,22)
    body+=pill(34,24,'KEYNOTE SPEAKER',218,34,YELLOW,INK,YELLOW,17)
    body+=text(278,48,data['event']+' · '+data['conference_dates'],21,INK)
    body+=title+summary+pill(34,summary_bottom+29,'Conference talk record',271,42,INK,WHITE,INK,19)
    body+=f'<g transform="translate(990 116)" stroke="{FOREST}" stroke-width="4" fill="none" stroke-linecap="round"><rect x="0" y="0" width="52" height="90" rx="26"/><path d="M-20 62v12a46 46 0 0 0 92 0V62M26 120v38m-29 0h58"/></g>'
    return 1200,height,body


def build():
    papers=json.loads((OUT/'papers.json').read_text())['papers']
    projects=json.loads((OUT/'projects.json').read_text())
    services=json.loads((OUT/'reviewing.json').read_text())
    keynote=json.loads((OUT/'keynote.json').read_text())
    research=[]
    for i,p in enumerate(papers):
        name=f'research/paper-{i+1:02d}'
        alt=f"{p['name']} — {p['category']}. {p['focus']}. {p['display_venue']} · {p['display_track']}. {p['status'].title()}. Read paper."
        for mobile in [False,True]:
            width,height,body=research_row(p,i,mobile)
            save(name+('-mobile' if mobile else '')+'.svg',width,height,alt,body)
        research.append(picture(name,alt,p['paper_url']))
    project_cards=[]
    for i,p in enumerate(projects):
        name=f'projects/project-{i+1:02d}'
        alt=f"{p['name']} — {p['category']}. {p['description']} View code."
        for mobile in [False,True]:
            width,height,body=project_row(p,i,mobile)
            save(name+('-mobile' if mobile else '')+'.svg',width,height,alt,body)
        project_cards.append(picture(name,alt,p['code_url']))
    service_blocks=[]
    for service in services:
        content=service['body'].replace('<br><br>','\n\n').replace('<br>',' ')
        content=re.sub(r'<img[^>]+alt="([^"]+)"[^>]*?/>',r'**\1** · ',content)
        service_blocks.append('### '+service['venue']+'\n\n'+service['scope']+'\n\n'+content)
    for mobile in [False,True]:
        width,height,body=keynote_card(keynote,mobile)
        save('keynote-card'+('-mobile' if mobile else '')+'.svg',width,height,keynote['role']+' · '+keynote['event']+' · '+keynote['title']+' · '+keynote['conference_dates'],body)
    readme=(ROOT/'README.md').read_text()
    readme=replace_section(readme,'research','\n\n'.join(research),table=True)
    readme=replace_section(readme,'projects','\n\n'.join(project_cards),table=True)
    readme=replace_section(readme,'reviewing','\n\n'.join(service_blocks),table=True)
    readme=replace_section(readme,'keynote',picture('keynote-card',keynote['role']+' · '+keynote['event']+' · '+keynote['title']+' · '+keynote['conference_dates'],keynote['url']))
    (ROOT/'README.md').write_text(readme)
    print(f'Built {len(papers)} research rows, {len(projects)} project rows and the keynote highlight.')


if __name__=='__main__':
    build()
