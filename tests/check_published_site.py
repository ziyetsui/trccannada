"""Smoke-test the exact public tree, locally or after Pages deployment."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from html.parser import HTMLParser
from playwright.sync_api import sync_playwright
import argparse, functools, http.server, threading
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--url');args=p.parse_args()
class Links(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if 'id' in d:self.ids.append(d['id'])
  if t=='a' and 'href' in d:self.links.append(d['href'])
x=Links();x.feed((ROOT/'index.html').read_text());assert len(x.ids)==len(set(x.ids));assert 'draft-6' in x.ids
for h in x.links:
 u=urlsplit(h)
 if u.scheme or u.netloc:continue
 if not u.path:assert not u.fragment or unquote(u.fragment) in x.ids,h
 else:assert (ROOT/unquote(u.path)).exists(),h
server=None
if args.url:base=args.url.rstrip('/')+'/'
else:
 class Quiet(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*a):pass
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
 threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
with sync_playwright() as p:
 b=p.chromium.launch();c=b.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
 c.route('https://fonts.googleapis.com/**',lambda r:r.abort());c.route('https://fonts.gstatic.com/**',lambda r:r.abort())
 c.add_init_script("""window.__spoken=[];Object.defineProperty(window,'speechSynthesis',{value:{getVoices:()=>[{name:'French',lang:'fr-FR'}],cancel:()=>{},speak:u=>window.__spoken.push(u.text),addEventListener:()=>{}}});window.SpeechSynthesisUtterance=function(text){this.text=text};""")
 page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(base+'#draft-6',wait_until='domcontentloaded');assert page.locator('#draft-6').count()==1
 assert page.locator('.source-page').count()==373;assert page.locator('.source-block').count()==4250;assert page.locator('.example-note').count()==537
 page.evaluate("location.hash='C06-E009'");page.wait_for_function("document.getElementById('C06-E009').closest('details').open")
 page.locator('#C06-E009 .say').click();assert 'peut être lavé' in page.evaluate('window.__spoken.at(-1)')
 page.locator('#theme-choice').select_option('dark');page.reload(wait_until='domcontentloaded');assert page.locator('html').get_attribute('data-theme')=='dark'
 page.locator('#source-query').fill('patient uncommonly carefully');assert not page.locator('#source-p0143').get_attribute('hidden')
 page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.goto(base+'learning-library/',wait_until='domcontentloaded');assert page.locator('.book-card').count()==9;assert page.locator('.lesson-card').count()==230
 assert page.locator('a[href="../"]').count()==1
 for lid in ['S01','S27','S37','S40','T01','T06','T20','T22']:
  page.goto(base+'learning-library/#'+lid,wait_until='domcontentloaded');assert page.locator('#lesson-title').inner_text()
  page.get_by_role('button',name='练习',exact=True).click();page.get_by_role('button',name='检查答案',exact=True).click();assert page.locator('.quiz-feedback').count()>=2
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.goto(base+'learning-library/#S01',wait_until='domcontentloaded');page.get_by_role('button',name='原书全文',exact=True).click();assert '本机' in page.locator('#lesson-content').inner_text()
 assert not errors,errors;b.close()
if server:server.shutdown()
print('PASS: published root anchors, 373 pages / 4250 blocks / 537 groups, search, French TTS routing, theme persistence, mobile; 9 books / 230 lessons, 8 new course routes and quizzes, source fallback, return link, no JS errors')
