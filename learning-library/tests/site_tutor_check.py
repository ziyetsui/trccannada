"""Verify all 814 lesson examples, with focused regression checks for I07."""
from pathlib import Path
import ast,copy,json,sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_site import load_library
from pronunciation import enrich,words,norm
from site_tutor import expand_library
lessons=load_library(ROOT/'french');enrich(lessons,ROOT/'scripts/content');report=expand_library(lessons,ROOT/'scripts/content')
assert report=={'lessons':230,'examples':814,'words':1394},report
byid={l['id']:l for l in lessons}
for lid,index in [('E27',2),('A21',2)]:
 p=byid[lid]['examples'][index]['pronunciation']
 assert next(w for w in p['words'] if w['fr']=='sens')['ipa']=='sɑ̃'
 assert not any(link['fr'].startswith('sens →') and '/s/' in link['label'] for link in p['links'])
assert next(w for w in byid['T02']['examples'][2]['pronunciation']['words'] if w['fr']=='droit')['zh']=='直；笔直地（tout droit：一直向前）'
assert next(w for w in byid['I19']['examples'][1]['pronunciation']['words'] if w['fr']=='sens')['ipa']=='sɑ̃s'
for l in lessons:
 assert l['pronunciation_guide']
 for e in l['examples']:
  p=e['pronunciation'];assert p['mnemonic'] and p['rule_memory'];assert all(w['ipa'] and w['zh'] and w['reason'] and w['picture'] for w in p['words'])
  assert p['sound_joke'] and p['mental_movie'] and p['sentence_memory_source']=='individually-authored'
  assert '句子小怪兽' not in p['mnemonic'] and '发光大招牌' not in p['mnemonic']
  assert list(map(norm,words(' '.join(c['fr'] for c in p['chunks']))))==list(map(norm,words(e['fr'])))
# Edited French must trigger a review of the stored sentence annotations.
bad=load_library(ROOT/'french');enrich(bad,ROOT/'scripts/content');next(l for l in bad if l['id']=='I07')['examples'][0]['fr']='Un billet différent.'
try:expand_library(bad,ROOT/'scripts/content');raise AssertionError('stale annotation accepted')
except ValueError as e:assert 'stale sentence' in str(e)
module=ast.parse((ROOT/'tests/pronunciation_check.py').read_text())
FAKE=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FAKE' for t in n.targets))
results=[]
def check(name,condition):
 assert condition,name
 results.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1100});page.add_init_script(FAKE)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto((ROOT/'index.html').as_uri()+'#I07')
 check('I07 all examples use five views',page.locator('.pronunciation-card').count()==3 and page.locator('.pronunciation-tab').count()==15)
 first=page.locator('.pronunciation-card').first
 check('I07 sound pun and meaning scene','售票员' in first.locator('.sound-mnemonic').inner_text() and '眼睛' in first.locator('.sound-mnemonic').inner_text())
 check('I07 exact idiom grouping preserved','coûte les yeux de la tête' in first.locator('.memory-rhythm').inner_text() and '贵得惊人' in first.locator('.phrase-meanings').inner_text())
 check('I07 les yeux has z marker',first.locator('.connection-liaison').filter(has_text='z').count()==1)
 third=page.locator('.pronunciation-card').nth(2)
 check('I07 vingt euros has t, not z',third.get_by_role('button',name='vingt → euros：联诵 · /t/，查看原因并慢读',exact=True).count()==1 and '万特油螺' in third.locator('.sound-mnemonic').inner_text())
 first.get_by_role('button',name='2 为什么这样读',exact=True).click()
 check('rule mnemonic opens in explanation view',first.locator('.memory-rules').get_attribute('open') is not None)
 page.evaluate('window.__voices()');first.locator('.word-select').nth(1).click()
 check('I07 word click speaks French, not phonetic joke',page.evaluate('window.__spoken.at(-1).text==="billet" && window.__spoken.at(-1).rate===0.65'))
 first.get_by_role('button',name='▶ 听整句，再跟一遍',exact=True).click()
 check('sentence memory slow button speaks the original French sentence',page.evaluate('window.__spoken.at(-1).text==="Ce billet coûte les yeux de la tête." && window.__spoken.at(-1).rate===0.65'))
 check('extended IPA is clearly identified','合成参考' in first.locator('.word-detail').inner_text())
 page.set_viewport_size({'width':390,'height':844})
 rendered=0;clicked=0
 for l in lessons:
  page.evaluate('(id)=>location.hash=id',l['id']);page.wait_for_function('(id)=>document.querySelector("#lesson-breadcrumb").textContent.endsWith(id)',arg=l['id'])
  expected=len(l['examples']);assert page.locator('.pronunciation-card').count()==expected,l['id']
  assert page.locator('.sound-mnemonic').count()==expected,l['id']
  assert page.locator('.sentence-sound-joke').count()==expected,l['id']
  assert page.locator('.sentence-mental-movie').count()==expected,l['id']
  assert page.get_by_role('button',name='▶ 听整句，再跟一遍',exact=True).count()==expected,l['id']
  for i,e in enumerate(l['examples']):
   card=page.locator('.pronunciation-card').nth(i)
   assert card.locator('.sentence-sound-joke').text_content()=='谐音梗 · '+e['pronunciation']['sound_joke'],(l['id'],i)
   assert card.locator('.sentence-mental-movie').text_content()=='脑内电影 · '+e['pronunciation']['mental_movie'],(l['id'],i)
  assert page.locator('.sound-rule-memory').count()==expected,l['id']
  assert page.locator('.word-card svg').count()==sum(len(e['pronunciation']['words']) for e in l['examples']),l['id']
  assert page.locator('.connection-legend').count()==expected,l['id']
  clicked+=page.evaluate('''() => {
   let count=0;
   for(const card of document.querySelectorAll('.pronunciation-card'))
    for(const button of card.querySelectorAll('.word-select')){
     button.click();const word=button.querySelector('strong').textContent;
     const box=card.querySelector('.word-memory');
     const key=word.toLowerCase().replaceAll('’',"'");
     if(box.getAttribute('aria-label')!==word+' 的发音巧记' || box.querySelector('.word-memory-line').textContent!==window.wordMemoryCatalog[key].line || box.querySelector('.word-memory-hook').textContent!=='谐音钩子：'+window.wordMemoryCatalog[key].hook || box.querySelector('.word-memory-cue').textContent!=='小画面：'+window.wordMemoryCatalog[key].cue.replace(/^(?:小画面|小动作)[：:]/,''))throw Error('Wrong clicked word or missing sound hook: '+word);
     count++;
    }
   return count;
  }''')
  for step in range(5):
   first=page.locator('.pronunciation-card').first;first.locator('.pronunciation-tab').nth(step).click()
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(l['id'],step,'mobile overflow')
  assert not first.locator('.sound-memory').count(),l['id']
  rendered+=expected
 check('230 lessons, all 814 examples render with word drawings, jokes and retained rules',rendered==814)
 check('all 814 examples show their own separate sound joke and mental movie',True)
 check('every word occurrence opens its own authored mnemonic',clicked==4485)
 check('all five mobile views fit every lesson',True)
 page.goto((ROOT/'index.html').as_uri()+'#I07');page.locator('.pronunciation-card').first.screenshot(path=str(ROOT/'docs/site-tutor-I07-mobile.png'))
 page.set_viewport_size({'width':1440,'height':1100});page.locator('.pronunciation-card').first.screenshot(path=str(ROOT/'docs/site-tutor-I07.png'))
 page.get_by_role('button',name='切换到暗色模式',exact=True).click();check('dark mode keeps readable tutor',page.locator('html').get_attribute('data-theme')=='dark')
 check('no JavaScript errors',not errors);browser.close()
(ROOT/'docs/site-tutor-verification.json').write_text(json.dumps({'coverage':report,'checks':results,'ipa_note':'Extended IPA is machine generated, not auditory validation.'},ensure_ascii=False,indent=2))
