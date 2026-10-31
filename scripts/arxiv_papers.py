#!/usr/bin/env python3
"""Fetch an arXiv review inbox, or approve explicitly selected curated papers."""
import argparse
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import re
import sys
import urllib.error
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from paper_news import load_papers, save_papers, validate

ROOT = Path(__file__).resolve().parents[1]
ATOM = '{http://www.w3.org/2005/Atom}'

def parse_feed(payload):
    feed = ET.fromstring(payload)
    if feed.tag != ATOM+'feed': raise ValueError('Expected an arXiv Atom feed')
    papers = []
    for entry in feed.findall(ATOM+'entry'):
        def text(name): return ' '.join(entry.findtext(ATOM+name, '').split())
        raw_id = text('id').split('/abs/')[-1]
        if not re.fullmatch(r'(?:\d{4}\.\d{4,5}|[a-z-]+/\d{7})v\d+', raw_id):
            raise ValueError('Unexpected arXiv entry: '+text('title'))
        papers.append({'id': re.sub(r'v\d+$', '', raw_id), 'version': 'v'+raw_id.rsplit('v',1)[1],
            'title':text('title'), 'authors':'; '.join(a.findtext(ATOM+'name','') for a in entry.findall(ATOM+'author')),
            'submitted':text('published')[:10], 'updated':text('updated')[:10],
            'abstract':text('summary'), 'url':'https://arxiv.org/abs/'+raw_id,
            'categories':[c.attrib['term'] for c in entry.findall(ATOM+'category')], 'status':'unreviewed'})
    return papers

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    fetch=sub.add_parser('fetch',help='Fetch recent quant-ph metadata into a separate review inbox')
    fetch.add_argument('--days',type=int,default=30)
    fetch.add_argument('--limit',type=int,default=50)
    fetch.add_argument('--as-of',type=date.fromisoformat,default=date.today())
    fetch.add_argument('--output',type=Path,default=ROOT/'content/arxiv-inbox.json')
    approve=sub.add_parser('approve',help='Approve IDs explicitly chosen by the editor; rebuild afterward')
    approve.add_argument('ids',nargs='+')
    approve.add_argument('--date',type=date.fromisoformat,required=True,help='Editorial approval date, YYYY-MM-DD')
    args=parser.parse_args()
    if args.command=='approve':
        data=load_papers(ROOT); validate(data)
        missing=set(args.ids)-{p['id'] for p in data['papers']}
        if missing: parser.error('Unknown IDs: '+', '.join(sorted(missing)))
        for p in data['papers']:
            if p['id'] in args.ids and p['status']!='approved':
                p.update(status='approved',approved_on=args.date.isoformat())
        validate(data)
        save_papers(ROOT,data)
        print('Approval saved. Run python3 scripts/build_all.py to generate news articles.')
        return
    if not 1<=args.days<=366 or not 1<=args.limit<=200: parser.error('Use 1–366 days and 1–200 results')
    if args.output.resolve().parent==(ROOT/'content/papers').resolve(): parser.error('The inbox must not overwrite curated papers')
    start=(args.as_of-timedelta(days=args.days-1)).strftime('%Y%m%d')+'0000'
    end=args.as_of.strftime('%Y%m%d')+'2359'
    params={'search_query':f'cat:quant-ph AND submittedDate:[{start} TO {end}]', 'start':0,
        'max_results':args.limit,'sortBy':'submittedDate','sortOrder':'descending'}
    req=Request('https://export.arxiv.org/api/query?'+urlencode(params),headers={'User-Agent':'QRC-LiteratureDesk/1.0 (mailto:mail.qrc@gmail.com)'})
    try:
        with urlopen(req,timeout=45) as response: papers=parse_feed(response.read())
    except (urllib.error.URLError,TimeoutError,ET.ParseError,ValueError) as exc:
        sys.exit(f'arXiv fetch failed; existing files were not changed: {exc}')
    data={'fetched_at':datetime.now(timezone.utc).isoformat(),'query':params,'papers':papers}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    temporary=args.output.with_suffix(args.output.suffix+'.tmp')
    temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');temporary.replace(args.output)
    print(f'{len(papers)} unreviewed papers written to {args.output}. Curated summaries and approvals were preserved.')
    if len(papers)==args.limit: print('Result limit reached; narrow the date range or raise --limit for wider coverage.')
if __name__=='__main__': main()
