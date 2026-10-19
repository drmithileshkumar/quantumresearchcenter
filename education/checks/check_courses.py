#!/usr/bin/env python3
"""Validate the developed course readers without regenerating other pages."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[2]
COURSES=('algorithms','programming','information','hardware')
parsed={}

def soup(path):
    path=path.resolve()
    if path not in parsed:parsed[path]=BeautifulSoup(path.read_text(),'html.parser')
    return parsed[path]


def main(courses=None):
    pages=0;chapters_count=0
    for course in COURSES if courses is None else courses:
        folder=ROOT/'education'/course
        manifest=json.loads((folder/'chapters.json').read_text())
        assert len({c['stem'] for c in manifest})==len(manifest)
        index=soup(folder/'index.html')
        for c in manifest:
            chapters_count+=1
            path=folder/f'{c["stem"]}.html'
            assert index.find('a',href=path.name),path
            manuscript=soup(folder/'content'/path.name)
            assert c['status']=='draft'
            if course=='algorithms':
                # Parts and topics are authored compactly and expanded by build.py.
                reader=soup(path)
                for sec in c['sections']:
                    part=manuscript.find('section',id=sec['id']);assert part and part['data-title']==sec['title'],(path,sec['id'])
                    for topic in sec['topics']:
                        art=manuscript.find('article',id=topic['id']);assert art and art['data-title']==topic['title'],(path,topic['id'])
                        assert len(art.get_text().split())>200,(path,topic['id'])
                        rendered=reader.find(id=topic['id']);assert rendered,(path,topic['id'])
                        assert len(rendered.select('.probing-question li details.problem-solution'))==3,(path,topic['id'])
                assert len(reader.select('#practice .exercise'))==10,path
                continue
            for sec in c['sections']:
                el=manuscript.find(id=sec['id']);assert el,(path,sec)
                assert el.h2.get_text()==sec['number']+' '+sec['title']
                headings=el.find_all('h3')
                assert [h.get_text().removesuffix('§').split(' ',1)[1] for h in headings]==sec['subsections']
                for heading in headings:
                    following=heading.find_next_sibling()
                    assert following and following.name not in ('h2','h3'),(path,heading)
                assert len(el.get_text().split())>100,(path,sec['id'])
            if course!='algorithms':assert len(manuscript.select('details.problem-solution'))>=3,path
            exercises=soup(path).select('#practice .exercise')
            assert len(exercises)==10 and all(e.select('.exercise-hint') and e.select('.exercise-solution') for e in exercises),path
            if course=='programming':
                number=manifest.index(c)+1
                source=(folder/f'examples/chapter_{number:02}.py').read_text()
                assert any(source==code.get_text() for code in manuscript.select('pre code')),path
        extra=[folder/'glossary.html',folder/'study-guide.html'] if course=='algorithms' else []
        for page in [folder/'index.html',*[folder/f'{c["stem"]}.html' for c in manifest],*extra]:
            pages+=1;doc=soup(page)
            ids=[n['id'] for n in doc.select('[id]')]
            assert len(ids)==len(set(ids)),page
            assert doc.title and doc.find('h1') and doc.find('main'),page
            assert 'chapter is an outline' not in doc.get_text(),page
            for el in doc.select('[href], [src]'):
                url=urlsplit(el.get('href') or el.get('src') or '')
                if url.scheme or url.netloc:continue
                target=(page.parent/unquote(url.path)).resolve() if url.path else page.resolve()
                assert target.exists(),(page,target)
                if url.fragment and target.suffix=='.html':
                    assert soup(target).find(id=unquote(url.fragment)),(page,target,url.fragment)
            for image in doc.select('main img'):assert image.get('alt'),(page,image)
    print(f'PASS: {chapters_count} developed chapters; {pages} reader pages; headings, solutions, embedded code, local links, fragments, and image alternatives.')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--course',action='append',choices=COURSES,
                        help='Check only this course; may be repeated.')
    main(parser.parse_args().course)
