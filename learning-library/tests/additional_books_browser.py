# -*- coding: utf-8 -*-
"""Verify added books in the real self-contained file:// app."""
from pathlib import Path
import json,ast
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
module=ast.parse((ROOT/'tests/browser_check.py').read_text())
FAKE=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FAKE_VOICES' for t in n.targets))
url=(ROOT/'index.html').as_uri();results=[]
def check(name,condition):
 assert condition,name
 results.append({'name':name,'passed':True});print('PASS',name,flush=True)
with sync_playwright() as p:
 browser=p.chromium.launch();context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce');context.add_init_script(FAKE)
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(url);check('nine books, 230 lessons',page.locator('.book-card').count()==9 and page.locator('.lesson-card').count()==230)
 page.locator('#book-grid .book-card').filter(has_text='故事阅读').click();check('40 stories book filter',page.locator('.lesson-card').count()==40)
 page.locator('#book-grid .book-card').filter(has_text='生活法语').click();check('22 Oxford sections book filter',page.locator('.lesson-card').count()==22)
 page.goto(url+'#S01');page.get_by_role('button',name='原书全文',exact=True).click()
 check('global source quality reminder visible on any story','原书核对说明' in page.locator('#lesson-content').inner_text())
 check('French original disabled until voices arrive',page.locator('[aria-label^="朗读原文段落"]').first.is_disabled())
 page.evaluate('window.__setVoices()');page.locator('[aria-label^="朗读原文段落"]').first.click()
 check('original story uses French TTS',page.evaluate("window.__spoken.at(-1).lang==='fr-FR' && window.__spoken.at(-1).text.includes('C’était')"))
 reader=json.loads((ROOT/'sources/french-stories/reader.json').read_text())
 blocks=reader['units'][0]['blocks']
 actual=page.locator('.source-text').all_text_contents()
 check('all first story, vocab, questions and answer blocks retained',actual==[b['text'] for b in blocks])
 page.goto(url+'#T01');page.get_by_role('button',name='原书全文',exact=True).click();page.evaluate('window.__setVoices()')
 page.locator('.source-group summary').first.click()
 page.evaluate('''()=>{const n=Array.from(document.querySelectorAll('.source-text')).find(n=>n.textContent.includes('Bonjour!'));const r=document.createRange();r.setStart(n.firstChild,n.textContent.indexOf('Bonjour!'));r.setEnd(n.firstChild,n.textContent.indexOf('Bonjour!')+8);const s=getSelection();s.removeAllRanges();s.addRange(r);}''')
 page.get_by_role('button',name='朗读选中的法语',exact=True).click()
 check('French selection in mixed Oxford page can be spoken',page.evaluate("window.__spoken.at(-1).text==='Bonjour!' && window.__spoken.at(-1).lang==='fr-FR'"))
 ox=json.loads((ROOT/'sources/oxford-take-off/reader.json').read_text())
 check('all first Oxford source blocks retained',page.locator('.source-text').all_text_contents()==[b['text'] for b in ox['units'][0]['blocks']])
 check('scan links resolve',page.locator('a[href^="sources/oxford-take-off/images/"]').count()>0)
 page.goto(url+'#S04');check('source answer defect visibly flagged','原书核对说明' in page.locator('#lesson-content').inner_text())
 page.goto(url+'#S40');check('last story direct link',page.locator('#lesson-title').inner_text()!='')
 page.get_by_role('button',name='练习',exact=True).click();page.get_by_role('button',name='检查答案',exact=True).click();check('new exercise explanations',page.locator('.quiz-feedback').count()>=2)
 page.goto(url+'#T22');page.get_by_role('button',name='原书全文',exact=True).click();check('Oxford appendices available',page.locator('.source-text').count()>0)
 page.goto(url+'#sources');check('source front matter renders without schema mismatch','undefined' not in page.locator('#document-body').inner_text() and page.locator('#document-body .source-text').count()>0)
 page.goto(url+'#coverage');page.get_by_label('选择原书').select_option('french-stories');check('all 40 story mappings',page.locator('.coverage-row').count()==40)
 page.get_by_label('选择原书').select_option('oxford-take-off');check('all 22 Oxford mappings',page.locator('.coverage-row').count()==22)
 page.goto(url+'#S01');page.get_by_role('button',name='原书全文',exact=True).click();page.get_by_role('button',name='切换到暗色模式').click()
 page.screenshot(path=str(ROOT/'docs/added-stories-desktop.png'))
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(ROOT/'docs/added-stories-mobile.png'))
 check('dark source reading has no mobile overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
 page.goto(url+'#T01');page.get_by_role('button',name='原书全文',exact=True).click();page.screenshot(path=str(ROOT/'docs/added-oxford-mobile.png'))
 check('mixed Oxford source has no mobile overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
 page.goto(url);check('nine-book mobile dashboard has no overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
 check('no JavaScript errors',not errors)
 browser.close()
(ROOT/'docs/additional-browser-verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
