"""Check the exact encrypted textbook edition locally or on live Pages."""
import argparse
import functools
import http.server
import json
from pathlib import Path
import tempfile
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url', help='Full textbook directory URL')
parser.add_argument('--password-file', required=True, type=Path)
args = parser.parse_args()
password = args.password_file.read_text().strip()
server = None
if args.url:
    url = args.url.rstrip('/')+'/'
else:
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/learning-library/textbooks/'

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(viewport={'width':390,'height':844},accept_downloads=True)
    context.add_init_script("""window.__spoken=[];Object.defineProperty(window,'speechSynthesis',{value:{getVoices:()=>[{name:'French',lang:'fr-CA',voiceURI:'fr-ca'}],cancel(){},speak:u=>window.__spoken.push(u.text),addEventListener(){}}});window.SpeechSynthesisUtterance=function(t){this.text=t};""")
    page = context.new_page()
    errors=[]; page.on('pageerror',lambda e:errors.append(str(e)))
    response = page.goto(url+'#NA201')
    assert response.status == 200
    assert '你好！法语2 · A2中文伴学' not in response.text()
    assert password not in response.text()
    page.get_by_label('访问码',exact=True).wait_for()
    assert page.locator('.lesson-card').count()==0
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.get_by_label('访问码',exact=True).fill('incorrect-access-code')
    page.get_by_role('button',name='进入学习室',exact=True).click()
    page.get_by_role('alert').filter(has_text='访问码不正确').wait_for()
    assert page.locator('#lesson-title').count()==0
    page.evaluate("localStorage.setItem('francais.textbooks.v1',JSON.stringify({done:['NA101'],last:'NA101',reviews:{NA101:{step:1,due:1}}}))")
    page.get_by_label('访问码',exact=True).fill(password)
    page.get_by_label('记住此设备 7 天').check()
    page.get_by_role('button',name='进入学习室',exact=True).click()
    page.locator('#lesson-title').wait_for()
    assert 'NA201' in page.locator('#breadcrumb').inner_text()
    assert page.locator('#textbook-data').evaluate('(n)=>JSON.parse(n.textContent).lessons.length')==289
    assert page.locator('.book-card').count()==8
    page.locator('#back').click()
    page.wait_for_function("document.querySelectorAll('.lesson-card').length===289")
    page.locator('#search').fill('NA201')
    assert page.locator('.lesson-card').count()==1
    page.locator('.lesson-card').click()
    page.wait_for_function("document.querySelector('#anchor-image').complete && document.querySelector('#anchor-image').naturalWidth>0")
    french=page.locator('#anchor-fr').inner_text()
    page.locator('#listen').click()
    assert page.evaluate('window.__spoken.at(-1)')==french
    page.locator('#recall').click()
    assert not page.locator('#anchor-fr').is_visible()
    page.locator('#reveal').click()
    assert page.locator('#anchor-fr').is_visible()
    page.locator('#check-answers').click()
    assert page.locator('.quiz-feedback').count()>=2
    task=page.locator('#self-check input').first; task.check()
    with page.expect_download() as download:
        page.locator('#download').click()
    downloaded=download.value
    assert downloaded.suggested_filename=='NA201.md'
    assert '## 讲解' in Path(downloaded.path()).read_text()
    page.reload(); page.locator('#lesson-title').wait_for()
    assert page.locator('#self-check input').first.is_checked()
    assert 'NA101' in json.loads(page.evaluate("localStorage.getItem('francais.textbooks.v1')"))['done']
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    expiry=int(page.evaluate("localStorage.getItem('textbooks.access.expiration')"))
    now=page.evaluate('Date.now()')
    assert 6.9*86400000 < expiry-now <= 7*86400000
    page.get_by_role('button',name='退出学习室',exact=True).click()
    page.get_by_label('访问码',exact=True).wait_for()
    assert page.locator('.lesson-card').count()==0
    assert 'NA101' in page.evaluate("localStorage.getItem('francais.textbooks.v1')")
    for path in ['lessons/NA0A.md','content/nihao-a2.json','template.html','app.js','build.py','illustrations.json','source-coverage.json']:
        assert context.request.get(url+path).status==404,path
    page.get_by_role('link',name='返回公开学习库 →').click()
    page.wait_for_url(url.removesuffix('textbooks/'))
    page.wait_for_function("document.querySelectorAll('.book-card').length===9")
    assert page.locator('.book-card').count()==9
    assert not errors,errors
    context.close()
    # A fresh browser still asks for a code.
    fresh=browser.new_page();fresh.goto(url);fresh.get_by_label('访问码',exact=True).wait_for();fresh.close()
    browser.close()
if server: server.shutdown();server.server_close()
print('PASS: locked HTML, wrong/right access codes, 289 lessons, deep link, images, French TTS, recall, quizzes, Markdown download, saved progress/tasks, seven-day remember, logout, mobile, fresh browser, raw source paths 404, public library intact, no JS errors.')
