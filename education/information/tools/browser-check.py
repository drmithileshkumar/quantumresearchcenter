#!/usr/bin/env python3
"""Optional Chrome checks. Requires websocket-client; no running web server needed."""
import base64
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from urllib.request import urlopen
import websocket

ROOT = Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix='qi-chrome-', ignore_cleanup_errors=True) as profile:
        chrome = subprocess.Popen([os.environ.get('CHROME', 'google-chrome'),
            '--headless', '--no-sandbox', '--disable-gpu', '--remote-debugging-port=0',
            '--remote-allow-origins=*', '--user-data-dir='+profile, 'about:blank'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ws = None
        try:
            portfile = Path(profile)/'DevToolsActivePort'
            for _ in range(100):
                if portfile.exists():
                    break
                time.sleep(.1)
            port = portfile.read_text().splitlines()[0]
            pages = json.load(urlopen(f'http://127.0.0.1:{port}/json/list'))
            ws = websocket.create_connection(next(p['webSocketDebuggerUrl'] for p in pages if p['type']=='page'), timeout=30)
            sequence = 0
            errors = []

            def send(method, **params):
                nonlocal sequence
                sequence += 1
                ws.send(json.dumps(dict(id=sequence, method=method, params=params)))
                while True:
                    msg = json.loads(ws.recv())
                    if msg.get('method') == 'Runtime.exceptionThrown':
                        errors.append(msg['params']['exceptionDetails'])
                    if msg.get('id') == sequence:
                        assert 'error' not in msg, msg
                        return msg.get('result', {})

            def evaluate(expression):
                result = send('Runtime.evaluate', expression=expression, returnByValue=True, awaitPromise=True)
                assert 'exceptionDetails' not in result, result
                return result['result'].get('value')

            def navigate(stem, fragment=''):
                send('Page.navigate', url=(ROOT/(stem+'.html')).as_uri()+fragment)
                for _ in range(150):
                    if evaluate("document.readyState==='complete' && document.documentElement.dataset.mathReady==='true'"):
                        return
                    time.sleep(.1)
                raise AssertionError('Page or MathJax did not load: '+stem)

            def check(expression, label):
                assert evaluate(expression), label

            send('Runtime.enable')
            send('Page.enable')
            send('Emulation.setDeviceMetricsOverride', width=1440, height=1000, deviceScaleFactor=1, mobile=False)
            chapters = json.loads((ROOT/'chapters.json').read_text())
            for chapter in chapters:
                navigate(chapter['stem'])
                check("document.querySelector('.chapter-header').nextElementSibling.matches('.chapter-mindmap')", 'Mind map begins chapter')
                for width in (1440,850,390,320):
                    send('Emulation.setDeviceMetricsOverride', width=width, height=1000, deviceScaleFactor=1, mobile=width<600)
                    check("(()=>{const c=document.querySelector('.chapter-mindmap .mindmap-canvas');return c.scrollWidth<=c.clientWidth+1})()", 'Chapter map fits reader width')
                    check("(()=>{const visible=[...document.querySelectorAll('.chapter-mindmap svg')].filter(s=>getComputedStyle(s).display!=='none');if(visible.length!==1)return false;const s=visible[0],v=s.viewBox.baseVal;return [...s.querySelectorAll('text')].every(t=>{const b=t.getBBox();return b.x>=0 && b.x+b.width<=v.width && b.y>=0 && b.y+b.height<=v.height})})()", 'All chapter labels fit diagram: '+chapter['stem'])
                    check("(()=>{const s=[...document.querySelectorAll('.chapter-mindmap svg')].find(s=>getComputedStyle(s).display!=='none');const a=[...s.querySelectorAll('a')];return a.length===9 && a.every(a=>document.getElementById(a.getAttribute('href').slice(1)))})()", 'Three section links and six topic links')
                    if chapter['stem'].startswith('01-') and width in (1440,390):
                        evaluate("document.querySelector('.chapter-mindmap').scrollIntoView({block:'start'})")
                        time.sleep(.2)
                        (Path(tempfile.gettempdir())/f'qi-chapter-map-{width}.png').write_bytes(base64.b64decode(send('Page.captureScreenshot',format='png')['data']))
                send('Emulation.setDeviceMetricsOverride', width=1440, height=1000, deviceScaleFactor=1, mobile=False)
                check("document.querySelectorAll('.reading-topic').length===6", 'Six linked subsections')
                check("!document.querySelector('mjx-merror, [data-mjx-error]')", 'Valid TeX: '+chapter['stem'])
                check("document.querySelectorAll('.problem-solution').length===4", 'Four solved problems')
                check("[...document.querySelectorAll('.probing-question')].every(d=>!d.open)", 'Problems initially closed')
                evaluate("Promise.all([...document.images].map(i=>{i.loading='eager';return i.decode()}))")
                check("[...document.images].every(i=>i.complete && i.naturalWidth>0)", 'Loaded drawings')
                send('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=1, mobile=True)
                check("document.documentElement.scrollWidth<=innerWidth+1", 'Mobile width: '+chapter['stem'])
                send('Emulation.setDeviceMetricsOverride', width=1440, height=1000, deviceScaleFactor=1, mobile=False)

            navigate('03-quantum-states')
            check("(()=>{const l=document.querySelector('[data-experiment=phase]'),s=l.querySelector('input');return [0,90,180,360].every((a,i)=>{s.value=a;s.dispatchEvent(new Event('input'));return Math.abs(Number(l.dataset.probability)-[1,.5,0,1][i])<1e-12})})()", 'Interference endpoints')
            navigate('06-quantum-operations')
            check("(()=>{const l=document.querySelector('[data-experiment=noise]'),s=l.querySelector('input');return [0,50,100].every((p,i)=>{s.value=p;s.dispatchEvent(new Event('input'));return Number(l.dataset.coherence)===[1,0,-1][i]})})()", 'Random and deterministic phase flips')
            navigate('08-state-discrimination')
            check("(()=>{const l=document.querySelector('[data-experiment=decision]');if(Math.abs(Number(l.dataset.success)-.75)>1e-12)return false;return [5,50,95].every(p=>{const s=l.querySelector('[data-prior]');s.value=p;s.dispatchEvent(new Event('input'));l.querySelector('[data-optimal]').click();return Math.abs(Number(l.dataset.success)-Number(l.dataset.optimum))<1e-12})})()", 'Decision bases attain the analytic optimum for unequal priors')
            evaluate("document.querySelector('[data-experiment=decision] [data-reset]').click();document.querySelector('[data-experiment=decision]').scrollIntoView()")
            time.sleep(.25)
            evaluate("document.querySelector('[data-experiment=decision]').scrollIntoView()")
            evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
            screenshot = Path(tempfile.gettempdir())/'qi-decision-desktop.png'
            screenshot.write_bytes(base64.b64decode(send('Page.captureScreenshot', format='png')['data']))
            evaluate("document.querySelector('#search-open').click();const input=document.querySelector('#book-search');input.value='teleportation';input.dispatchEvent(new Event('input'))")
            check("document.querySelector('#search-dialog').open && document.querySelectorAll('#search-results a').length>0", 'Search finds course content')
            evaluate("document.querySelector('#search-close').click();dispatchEvent(new Event('beforeprint'))")
            check("[...document.querySelectorAll('main details')].every(d=>d.open)", 'Print expands all problems and solutions')
            evaluate("dispatchEvent(new Event('afterprint'))")
            check("[...document.querySelectorAll('.problem-solution,.probing-question')].every(d=>!d.open)", 'Print restores disclosure state')
            navigate('08-state-discrimination', '#chapter-8-transfer')
            check("document.querySelector('#section-8-3-problems').open", 'Direct problem links reveal the problem')
            send('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=1, mobile=True)
            evaluate("document.querySelector('[data-experiment=decision]').scrollIntoView()")
            time.sleep(.25)
            evaluate("document.querySelector('[data-experiment=decision]').scrollIntoView()")
            evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
            (Path(tempfile.gettempdir())/'qi-decision-mobile.png').write_bytes(base64.b64decode(send('Page.captureScreenshot', format='png')['data']))
            check("!document.querySelector('#print-chapter').hidden", 'Print control available')
            # Progressive enhancement: the static manuscript and disclosures work without scripts.
            send('Emulation.setScriptExecutionDisabled', value=True)
            send('Page.navigate', url=(ROOT/'03-quantum-states.html').as_uri())
            time.sleep(1)
            send('Emulation.setScriptExecutionDisabled', value=False)
            check("document.querySelector('.lab-fallback img').naturalWidth>0 && document.querySelector('[data-experiment] [data-live]').hidden", 'No-JavaScript circuit fallback')
            assert not errors, errors
            print('PASS: 16 chapter maps; desktop/mobile layout, TeX, drawings, three experiments, search, deep links, print restoration, and no-JavaScript fallback.')
            print('Screenshots: '+str(screenshot)+' and /tmp/qi-decision-mobile.png')
        finally:
            if ws:
                ws.close()
            chrome.terminate()
            chrome.wait(timeout=10)


if __name__ == '__main__':
    main()
