"""Exercise authored coverage and the five-step tutor in an isolated test browser."""
from pathlib import Path
import sys, json, re, tempfile
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from pronunciation import enrich
from build_site import load_library
lessons=load_library(ROOT/'french')
report=enrich(lessons,ROOT/'scripts/content')
assert report=={'lessons':50,'examples':150,'words':305},report
pron=[l for l in lessons if l['category']=='发音']
assert all(e['pronunciation']['words'] and e['pronunciation']['chunks'] for l in pron for e in l['examples'])
f02=next(l for l in pron if l['id']=='F02')
notes=' '.join(n['reason'] for e in f02['examples'] for n in e['pronunciation']['links'])
assert '不加 /z/' in notes and '不把末尾 t' in notes and '本来存在' in notes
# Reject stale phrase annotations rather than silently assigning incorrect glosses.
import copy
bad=copy.deepcopy(lessons);next(l for l in bad if l['id']=='F02')['examples'][0]['fr']='Une phrase différente.'
try:enrich(bad,ROOT/'scripts/content');raise AssertionError('stale annotation not rejected')
except ValueError as e:assert 'reconstruct' in str(e)

FAKE=r'''(() => {
 window.__spoken=[];window.__cancelled=0;window.__pending=[];
 window.SpeechSynthesisUtterance=function(text){this.text=text};
 const synth={list:[],listeners:{},getVoices(){return this.list},addEventListener(k,f){this.listeners[k]=f},
 cancel(){window.__cancelled++},speak(u){window.__spoken.push({text:u.text,rate:u.rate,lang:u.lang});window.__pending.push(u);u.onstart?.();}};
 Object.defineProperty(window,'speechSynthesis',{value:synth,configurable:true});
 window.__finish=()=>window.__pending.shift()?.onend?.();
 window.__voices=()=>{synth.list=[{name:'France',lang:'fr-FR',voiceURI:'fr'},{name:'Canada',lang:'fr-CA',voiceURI:'ca'}];synth.listeners.voiceschanged?.();};
})();'''
PAGE=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'index.html'
results=[]
def check(name,condition):
 assert condition,name
 results.append(name);print('PASS',name)
with sync_playwright() as pw:
 browser=pw.chromium.launch()
 page=browser.new_page(viewport={'width':1440,'height':1000});page.add_init_script(FAKE)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(PAGE.as_uri()+'#F02')
 check('three examples, five views each',page.locator('.pronunciation-card').count()==3 and page.locator('.pronunciation-tab').count()==15)
 check('no voice: playback disabled, meanings still accessible',page.locator('.word-card').count()>0 and page.locator('[data-speak="words"]').count()==0 and page.get_by_role('button',name='▶ 听完整句',exact=True).first.is_disabled())
 first=page.locator('.pronunciation-card').first
 check('sentence has distinct connection marks',first.locator('.connection-flow').count()==1 and first.locator('.connection-optional').count()==1 and first.locator('.connection-blocked').count()==1)
 first.locator('.connection-flow').click()
 check('connection mark explains existing consonant without a voice','本来存在' in first.locator('.inline-connection-detail').inner_text())
 first.locator('.word-select').nth(1).click()
 check('word meaning works without voices','rendez-vous' in first.locator('.word-detail').inner_text())
 page.evaluate('window.__voices()');page.get_by_label('法语声音').select_option('ca')
 first.locator('.word-select').nth(1).click()
 check('word clicks speak French slowly',page.evaluate('window.__spoken.at(-1).text==="rendez-vous" && window.__spoken.at(-1).rate===0.65 && window.__spoken.at(-1).lang==="fr-CA"'))
 first.get_by_role('button',name='2 为什么这样读',exact=True).click()
 first.locator('.word-select').nth(4).click()
 check('word-specific spelling and mouth explanation','quinze' in first.locator('.word-detail').inner_text() and '/ɛ̃/' in first.locator('.word-detail').inner_text())
 first.get_by_role('button',name='3 逐词慢读',exact=True).click()
 first.get_by_label('例句 1 每项重复次数').select_option('2');page.evaluate('window.__pending=[]')
 first.get_by_role('button',name='▶ 逐词跟读',exact=True).click();page.evaluate('window.__finish()')
 page.wait_for_timeout(1500)
 check('repeat selected word before moving on',page.evaluate('window.__spoken.at(-1).text==="Le" && window.__spoken.at(-2).text==="Le"'))
 page.evaluate('window.__finish()');page.get_by_role('button',name='停止播放',exact=True).click()
 n=page.evaluate('window.__spoken.length');page.wait_for_timeout(1550)
 check('stop cancels scheduled follow-up',page.evaluate('window.__spoken.length')==n)
 first.get_by_role('button',name='4 一点点连起来',exact=True).click()
 check('F02 has connection-specific no-liaison guidance','不加 /z/' in first.locator('.connection-notes').inner_text() and '本来存在' in first.locator('.connection-notes').inner_text())
 first.get_by_role('button',name='▶ 只听这个连接',exact=True).last.click()
 check('pair player sends only French',page.evaluate('window.__spoken.at(-1).text==="quinze heures"'))
 first.get_by_role('button',name='▶ 正常速度核对整句',exact=True).click()
 check('normal full sentence uses rate 1',page.evaluate('window.__spoken.at(-1).text==="Le rendez-vous est à quinze heures." && window.__spoken.at(-1).rate===1'))
 first.get_by_role('button',name='5 自己说一次',exact=True).click()
 check('recall initially hides French sentence',not first.locator('.pronunciation-head .example-fr').is_visible() and not first.locator('.recall-answer').is_visible())
 check('recall hides connection hints',not first.locator('.connection-legend').is_visible() and not first.locator('.inline-connection-detail').is_visible())
 first.get_by_role('button',name='显示法语，核对一下',exact=True).click()
 check('reveal gives original and grouping',first.locator('.recall-answer').is_visible())
 check('hearing does not automatically mark lesson complete',page.get_by_role('button',name='标记已学',exact=True).is_visible())
 page.goto(PAGE.as_uri()+'#F02');page.evaluate('window.__voices()')
 for lesson in pron:
  page.evaluate('(id)=>location.hash=id',lesson['id']);page.wait_for_function('(id)=>document.querySelector("#lesson-breadcrumb").textContent.endsWith(id)',arg=lesson['id'])
  check(lesson['id']+' all three examples render with drawings',page.locator('.pronunciation-card').count()==3 and page.locator('.word-card svg').count()==sum(len(e['pronunciation']['words']) for e in lesson['examples']))
  page.set_viewport_size({'width':390,'height':844})
  for step in [2,3,4,0]:
   page.locator('.pronunciation-card').first.locator('.pronunciation-tab').nth(step).click()
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(lesson['id'],step,'mobile overflow')
 page.goto(PAGE.as_uri()+'#F02');page.evaluate('window.__voices()')
 page.screenshot(path=str(ROOT/'docs/pronunciation-mobile.png'),full_page=True)
 page.set_viewport_size({'width':1440,'height':1100});page.screenshot(path=str(ROOT/'docs/pronunciation-desktop.png'),full_page=True)
 page.locator('.pronunciation-card').first.screenshot(path=str(ROOT/'docs/pronunciation-example.png'))
 page.locator('.pronunciation-card').first.get_by_role('button',name='4 一点点连起来',exact=True).click()
 page.screenshot(path=str(ROOT/'docs/pronunciation-connected.png'),full_page=True)
 page.get_by_role('button',name='切换到暗色模式',exact=True).click()
 check('dark theme retained',page.locator('html').get_attribute('data-theme')=='dark')
 check('no JavaScript errors',not errors)
 browser.close()
(ROOT/'docs/pronunciation-verification.json').write_text(json.dumps({'coverage':report,'checks':results},ensure_ascii=False,indent=2))
