"""Apply the selected color tokens consistently to every profile SVG."""
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

THEME = json.loads((Path(__file__).resolve().parent.parent / 'assets/profile/theme.json').read_text())
SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)


def apply_theme(svg, name):
    # Link buttons are composed directly with these tokens and retain their small
    # per-destination identity markers. All other assets share one color system.
    if name.startswith('link-'):
        return svg
    t = THEME
    root = ET.fromstring(svg)
    mapping = {
        '#172033':t['ink'], '#101d33':t['base'], '#0b1425':t['base2'],
        '#162b3a':t['base2'], '#18313e':t['base2'], '#31515e':t['primary'],
        '#4ac3b0':t['highlight'], '#5eead4':t['highlight'], '#0d9488':t['primary'],
        '#8da4be':t['light'], '#92a8be':t['light'], '#94a8bd':t['light'], '#c4d0df':t['light'],
        '#0f766e':t['primary'], '#ea580c':t['primary'], '#075985':t['primary'],
        '#0369a1':t['primary'], '#dc2626':t['primary'], '#ef4444':t['primary'],
        '#f97316':t['primary'], '#fb923c':t['accent'], '#fde047':t['mist'],
        '#fefce8':t['mist'], '#fff7ed':t['mist'], '#f0f9ff':t['mist'],
        '#d5f6ed':t['mist'], '#e0f2fe':t['mist'], '#ffedd5':t['mist'],
        '#fef9c3':t['mist'], '#f1f5f9':t['mist'], '#edf8f7':t['mist'],
        '#fdba74':t['border'], '#bae6fd':t['border'], '#a7dfd2':t['border'],
        '#b8dfda':t['border'], '#9dcfc5':t['border'], '#d0ebe6':'#e6eee8',
        '#59a598':t['primary'], '#134e4a':t['ink'], '#466966':t['slate'],
        '#475569':t['slate'], '#546377':t['slate'],
    }
    if name.startswith('credentials'):
        mapping.update({color:t['ink'] for color in ['#0f766e','#ea580c','#075985']})
        mapping['#fde047']=t['border']
    # Preserve the original yellow hand, including its orange finger details.
    protected = {id(e) for hand in root.findall(f'.//{{{SVG}}}g[@class="greeting-wave"]') for e in hand.iter()}
    for element in root.iter():
        if id(element) in protected:
            continue
        for attribute in ['fill','stroke','stop-color']:
            color=element.get(attribute)
            if color in mapping:
                element.set(attribute,mapping[color])
        if element.tag==f'{{{SVG}}}path' and re.match(r'M(?:48|86|124|32|64|96) 0h',element.get('d','')):
            element.set('stroke',t['primary'])
        if name.startswith('credentials') and element.tag==f'{{{SVG}}}rect' and element.get('width')=='3':
            element.set('fill',t['primary'])
    return ET.tostring(root,encoding='unicode')
