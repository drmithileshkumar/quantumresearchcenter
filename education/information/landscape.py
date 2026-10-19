"""Render the course's linked mind map from its canonical topic index."""
from html import escape
from bs4 import BeautifulSoup

MAP_STYLE = '''<style>
.topic-mindmap {background:#fff;font-family:Georgia,serif;}
.map-branch,.map-twig {fill:none;stroke-linecap:round;}
.map-branch {stroke-width:2.5;}
.map-twig {stroke-width:1.3;}
.map-domain {font-size:21px;font-weight:600;fill:#263f46;}
.map-topic {font-size:18px;fill:#234f68;}
.map-root {font-size:25px;font-weight:600;fill:#24483e;}
.topic-mindmap a:hover text,.topic-mindmap a:focus text {text-decoration:underline;fill:#102f43;}
</style>'''

# Layout and short labels; destinations come from content/landscape.html.
BRANCHES = [
    ('landscape-foundations', 'left', 210, '#527b98', 'Information and states',
     ['Messages & distinguishability', 'Probability & classical coding', 'Amplitudes & interference']),
    ('landscape-processing', 'left', 590, '#6a7b9c', 'Dynamics and observation',
     ['Ancillas & discarding', 'Quantum channels', 'Noise & composition', 'Measurements & instruments']),
    ('landscape-entropy', 'left', 980, '#987647', 'Entropy and compression',
     ['von Neumann entropy', 'Mutual & conditional entropy', 'Relative entropy & bounds', 'Typical subspaces & compression']),
    ('landscape-correlations', 'right', 150, '#58836c', 'Systems and correlations',
     ['Joint states & tensor products', 'Bell pairs & entanglement', 'Mixed states & reductions', 'Purification']),
    ('landscape-inference', 'right', 420, '#8e6e89', 'Learning and limits',
     ['State discrimination', 'Accessible information', 'No-cloning & no-broadcasting', 'No-signalling']),
    ('landscape-entanglement', 'right', 690, '#428287', 'Entanglement resources',
     ['Teleportation & dense coding', 'LOCC & Schmidt coefficients', 'Concentration & dilution', 'Mixed-state entanglement']),
    ('landscape-communication', 'right', 1010, '#a06d52', 'Communication and security',
     ['Error correction', 'Classical & assisted capacities', 'Quantum capacity', 'BB84 & privacy amplification', 'Authentication & security']),
]


def draw(soup, compact=False):
    """Lay out branches in two columns, or one readable column on narrow pages."""
    prefix = 'mindmap-compact' if compact else 'mindmap-wide'
    width, height = (400, 1800) if compact else (800, 1000)
    root_x = width/2
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="group" aria-labelledby="{prefix}-title {prefix}-description" class="topic-mindmap {prefix}">
<title id="{prefix}-title">Quantum information: domains and topics</title>
<desc id="{prefix}-description">Quantum information branches into seven domains, each with links to its topics. The complete diagram fits the page width.</desc>
{MAP_STYLE}''']
    order = ['landscape-foundations', 'landscape-correlations', 'landscape-processing',
             'landscape-inference', 'landscape-entropy', 'landscape-entanglement',
             'landscape-communication']
    branches = sorted(BRANCHES, key=lambda branch: order.index(branch[0]))
    spine_x = 26 if compact else 400
    last_y = 170+6*230 if compact else 170+3*205
    parts.append(f'<path class="map-twig" stroke="#bdcdc5" d="M {root_x} 105 Q {root_x} 130 {spine_x} 130 V {last_y+10}"/>')
    for index, (identity, side, _, color, title, labels) in enumerate(branches):
        links = soup.find(id=identity).select('ul a')
        if len(links) != len(labels):
            raise ValueError('Mind map labels and topic links disagree: '+identity)
        row = index if compact else index//2
        y = 170+row*(230 if compact else 205)
        x = 50 if compact else (20 if index%2==0 else 440)
        edge = 380 if compact else x+340
        twig_x = x+12
        text_x = x+28
        parts.append(f'<g id="{prefix}-{identity}" style="color:{color}">')
        attach = x if compact or index%2 else edge
        parts.append(f'<path class="map-branch" stroke="currentColor" d="M {spine_x} {y+10} H {attach} M {x} {y+10} H {edge}"/>')
        parts.append(f'<text class="map-domain" x="{x}" y="{y}">{escape(title)}</text>')
        for j, (link, label) in enumerate(zip(links, labels)):
            leaf_y = y+45+j*30
            parts.append(f'<path class="map-twig" stroke="currentColor" d="M {twig_x} {y+10} V {leaf_y-6} Q {twig_x} {leaf_y} {text_x-7} {leaf_y}"/>')
            parts.append(f'<a href="{escape(link["href"],quote=True)}"><text class="map-topic" x="{text_x}" y="{leaf_y+5}">{escape(label)}</text></a>')
        parts.append('</g>')
    parts.append(f'''<rect x="{root_x-115}" y="22" width="230" height="83" rx="22" fill="#edf4ef" stroke="#527a67" stroke-width="2"/>
<text class="map-root" x="{root_x}" y="57" text-anchor="middle">Quantum<tspan x="{root_x}" dy="30">information</tspan></text>
</svg>''')
    return '\n'.join(parts)


def render(manuscript):
    soup = BeautifulSoup(manuscript, 'html.parser')
    wide, compact = draw(soup), draw(soup, compact=True)
    placeholder = '<div data-topic-map></div>'
    if placeholder not in manuscript:
        raise ValueError('Missing mind map placeholder')
    return manuscript.replace(placeholder, wide+compact), wide


def chapter_map(chapter):
    """Build chapter → section → subsection maps from the navigation manifest."""
    from textwrap import wrap

    def text_lines(label, x, y, limit, line_height, css, anchor='start'):
        lines = wrap(label, width=limit, break_long_words=False, break_on_hyphens=False)
        spans = ''.join(f'<tspan x="{x}" dy="{0 if i==0 else line_height}">{escape(line)}</tspan>'
                        for i,line in enumerate(lines))
        return f'<text class="{css}" x="{x}" y="{y}" text-anchor="{anchor}">{spans}</text>', len(lines)

    def diagram(compact):
        variant = 'compact' if compact else 'wide'
        prefix = chapter['stem']+'-map-'+variant
        width = 400 if compact else 800
        center = width/2
        title, title_count = text_lines(chapter['title'],center,55,22 if compact else 30,30,'map-root','middle')
        root_bottom = 75+(title_count-1)*30
        start_y = root_bottom+65
        spine = 26 if compact else center
        parts=[]
        colors=['#527b98','#58836c','#987647']
        row_heights={}
        for index,section in enumerate(chapter['sections']):
            row=index if compact else index//2
            heading_lines=wrap(section['title'],width=27,break_long_words=False,break_on_hyphens=False)
            topic_height=sum(24*len(wrap(topic,width=32,break_long_words=False,break_on_hyphens=False))+18
                             for topic in section['subsections'])
            row_heights[row]=max(row_heights.get(row,0),len(heading_lines)*26+topic_height+45)
        row_tops={};cursor=start_y
        for row,height in row_heights.items():
            row_tops[row]=cursor;cursor+=height
        height=cursor+10
        last_y=row_tops[max(row_tops)]
        parts.append(f'<path class="map-twig" stroke="#bdcdc5" d="M {center} {root_bottom} Q {center} {root_bottom+20} {spine} {root_bottom+20} V {last_y+10}"/>')
        for index,section in enumerate(chapter['sections']):
            row=index if compact else index//2
            y=row_tops[row]
            x=50 if compact else (20 if index%2==0 else 440)
            edge=380 if compact else x+340
            heading, count=text_lines(section['title'],x,y,27,26,'map-domain')
            baseline=y+(count-1)*26+10
            attach=x if compact or index%2 else edge
            parts.append(f'<g style="color:{colors[index%len(colors)]}">')
            parts.append(f'<path class="map-branch" stroke="currentColor" d="M {spine} {y+10} H {attach} M {x} {baseline} H {edge}"/>')
            parts.append(f'<a href="#{section["id"]}">{heading}</a>')
            leaf_y=baseline+34
            for j,topic in enumerate(section['subsections'],1):
                target=section['id'].replace('section-','topic-')+f'-{j}'
                label,lines=text_lines(topic,x+28,leaf_y,32,24,'map-topic')
                parts.append(f'<path class="map-twig" stroke="currentColor" d="M {x+12} {baseline} V {leaf_y-12} Q {x+12} {leaf_y-6} {x+21} {leaf_y-6}"/>')
                parts.append(f'<a href="#{target}">{label}</a>')
                leaf_y+=lines*24+18
            parts.append('</g>')
        parts.append(f'<rect x="{center-(175 if compact else 235)}" y="22" width="{350 if compact else 470}" height="{root_bottom-22}" rx="22" fill="#edf4ef" stroke="#527a67" stroke-width="2"/>')
        parts.append(title)
        description=escape(chapter['title']+' branches into '+', '.join(s['title'] for s in chapter['sections'])+'. Section and topic labels link to their explanations.')
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" class="topic-mindmap mindmap-{variant}" role="group" aria-labelledby="{prefix}-title {prefix}-description">
<title id="{prefix}-title">{escape(chapter['title'])}: chapter mind map</title>
<desc id="{prefix}-description">{description}</desc>
{MAP_STYLE}
{''.join(parts)}
</svg>'''

    return f'''<figure class="landscape-mindmap chapter-mindmap" aria-labelledby="chapter-map-caption">
<div class="mindmap-canvas">{diagram(False)}{diagram(True)}</div>
<figcaption id="chapter-map-caption">Chapter map · Follow a branch from {escape(chapter['title'])} to a section and its topics. Select a label to jump to the explanation.</figcaption>
</figure>'''
