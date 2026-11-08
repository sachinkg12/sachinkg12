"""Outline locally bundled fonts so profile SVGs render consistently as images."""
from functools import lru_cache
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)
FONTS = Path(__file__).resolve().parent.parent / 'assets/profile/fonts'


@lru_cache(maxsize=24)
def font_for(family, weight):
    name = {'Space Grotesk': 'SpaceGrotesk.ttf', 'Sora': 'Sora.ttf',
            'IBM Plex Mono': 'IBMPlexMono-Regular.ttf'}.get(family, 'Manrope.ttf')
    font = TTFont(FONTS / name)
    location = {'wght': weight} if 'fvar' in font else None
    return font, font.getGlyphSet(location=location), font.getBestCmap()


def outline_svg(svg):
    """Keep accessible labels; replace font-dependent text with vector paths."""
    root = ET.fromstring(svg)
    for parent in root.iter():
        for index, element in enumerate(list(parent)):
            if element.tag != f'{{{SVG}}}text':
                continue
            label = ''.join(element.itertext())
            family = element.get('font-family', 'Manrope').split(',')[0].strip(" '\"")
            weight = float(element.get('font-weight', '400'))
            font, glyphs, cmap = font_for(family, weight)
            size = float(element.get('font-size', '18'))
            scale = size / font['head'].unitsPerEm
            spacing = float(re.sub(r'px$', '', element.get('letter-spacing', '0'))) / scale
            pen = SVGPathPen(glyphs, ntos=lambda n: format(n, '.2f').rstrip('0').rstrip('.') or '0')
            cursor = 0
            for char in label:
                glyph = glyphs[cmap.get(ord(char), '.notdef')]
                glyph.draw(TransformPen(pen, (1, 0, 0, 1, cursor, 0)))
                cursor += glyph.width + spacing
            x, y = float(element.get('x', 0)), float(element.get('y', 0))
            anchor = element.get('text-anchor')
            if anchor == 'middle':
                x -= (cursor-spacing) * scale / 2
            elif anchor == 'end':
                x -= (cursor-spacing) * scale
            group = ET.Element(f'{{{SVG}}}g', {
                'fill': element.get('fill', '#172033'), 'role': 'img',
                'aria-label': label,
                'transform': f'translate({x:g} {y:g}) scale({scale:.7f} {-scale:.7f})',
            })
            ET.SubElement(group, f'{{{SVG}}}path', {'d': pen.getCommands()})
            parent.remove(element)
            parent.insert(index, group)
    return ET.tostring(root, encoding='unicode')
