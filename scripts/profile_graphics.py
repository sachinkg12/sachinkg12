"""Shared SVG drawing and text wrapping for the profile's visual assets."""
from pathlib import Path
from html import escape
from profile_typography import outline_svg, font_for
from profile_theme import THEME

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets/profile'
INK, MUTED, LINE = THEME['ink'], THEME['slate'], THEME['border']
WHITE, LEAF, YELLOW, FOREST = THEME['base'], THEME['leaf'], THEME['accent'], THEME['primary']
FONT, SERIF, MONO = 'IBM Plex Sans', 'Lora', 'IBM Plex Mono'


def text(x, y, value, size=18, color=INK, weight=400, family=FONT, extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{family}" font-size="{size}" font-weight="{weight}" {extra}>{escape(value)}</text>'


def rect(x, y, width, height, fill=WHITE, stroke=LINE, radius=16):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'


def measure(value, size=18, weight=400, family=FONT, style='normal'):
    font, glyphs, cmap = font_for(family, weight, style)
    return sum(glyphs[cmap.get(ord(c), '.notdef')].width for c in value) * size / font['head'].unitsPerEm


def wrap(value, width, size=18, weight=400, family=FONT):
    lines, current = [], ''
    for word in value.split():
        candidate = f'{current} {word}'.strip()
        if current and measure(candidate, size, weight, family) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    return lines + ([current] if current else [])


def paragraph(x, y, value, width, size=22, leading=30, color=MUTED, weight=400, family=FONT):
    lines = wrap(value, width, size, weight, family)
    return ''.join(text(x, y+i*leading, line, size, color, weight, family) for i,line in enumerate(lines)), y+max(0,len(lines)-1)*leading


def pill(x, y, label, width=152, height=34, fill=WHITE, color=INK, border=LINE, size=17):
    return rect(x,y,width,height,fill,border,height/2)+text(x+width/2,y+height/2+size*.34,label,size,color,500,extra='text-anchor="middle"')


def document(width, height, label, content):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title"><title id="title">{escape(label)}</title>{content}</svg>'
    return outline_svg(svg)


def save(name, width, height, label, content):
    path=OUT/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(document(width,height,label,content))
