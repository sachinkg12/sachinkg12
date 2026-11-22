"""Website-style section headings that also work in GitHub profile READMEs.

GitHub's h3 elements have no mandatory underline. Named anchors preserve the
existing section links; the heading lettering is outlined for consistent fonts.
"""
from html import escape
import re
from profile_graphics import ROOT, text, rect, measure, save, WHITE, INK

HEADINGS = [
    ('engineering-technical-leadership','Engineering','& technical leadership','Engineering & technical leadership'),
    ('research-9-accepted-papers','Research','— 9 accepted papers','Research — 9 accepted papers'),
    ('speaking-sessions','Speaking','& sessions','Speaking & sessions'),
    ('my-website-guptasachinn-com','Websites','& writing','Websites & writing'),
    ('open-source-work','Open-source','work','Open-source work'),
    ('reviewing-research-service','Reviewing','& research service','Reviewing & research service'),
    ('mentoring-community','Mentoring','& community','Mentoring & community'),
    ('community-word-cloud','Community','word cloud','Community word cloud'),
    ('beyond-engineering','Beyond','engineering','Beyond engineering'),
    ('heaplens-marketplace-activity','HeapLens','marketplace activity','HeapLens marketplace activity'),
]


def heading_markup(slug):
    _,lead,tail,label=next(item for item in HEADINGS if item[0]==slug)
    return f'''<a name="{slug}"></a>
<h3 class="section-heading" id="{slug}">
<picture><source media="(max-width: 600px)" srcset="./assets/profile/headings/{slug}-mobile.svg" /><img src="./assets/profile/headings/{slug}.svg" width="100%" alt="{escape(label,quote=True)}" /></picture>
</h3>'''


def build_headers():
    source=(ROOT/'README.md').read_text()
    for slug,lead,tail,label in HEADINGS:
        for mobile in [False,True]:
            width,size,leading=(600,56,70) if mobile else (1200,44,58)
            x,y=2,size+6
            runs=[]
            for phrase,family,weight,style in [(lead,'Arial',500,'normal'),(tail,'Lora',400,'italic')]:
                if mobile and phrase==tail and x>2 and x+measure(' '+phrase,size,weight,family,style)>width-2 and measure(phrase,size,weight,family,style)<=width-4:
                    x,y=2,y+leading
                for word in phrase.split():
                    candidate=(' ' if x>2 else '')+word
                    word_width=measure(candidate,size,weight,family,style)
                    if x+word_width>width-2:
                        x,y=2,y+leading
                        candidate=word
                        word_width=measure(candidate,size,weight,family,style)
                    runs.append(text(x,y,candidate,size,INK,weight,family,extra=f'font-style="{style}"'))
                    x+=word_width
            height=y+18
            body=rect(0,0,width,height,WHITE,WHITE,0)+''.join(runs)
            save('headings/'+slug+('-mobile' if mobile else '')+'.svg',width,height,label,body)
        if slug=='heaplens-marketplace-activity':
            continue  # The count generator owns its marked README block.
        start,end=f'<!-- heading:{slug}:start -->',f'<!-- heading:{slug}:end -->'
        block=start+'\n'+heading_markup(slug)+'\n'+end
        if start in source:
            source=re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda _:block,source,flags=re.S)
        else:
            old_label='My website — guptasachinn.com' if slug=='my-website-guptasachinn-com' else label
            pattern=r'^## <img[^>]+/> '+re.escape(old_label)+r'$'
            source,count=re.subn(pattern,lambda _:block,source,count=1,flags=re.M)
            if count!=1:
                raise ValueError('Could not find section heading: '+old_label)
    (ROOT/'README.md').write_text(source)


if __name__=='__main__':
    build_headers()
