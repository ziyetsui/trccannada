"""Exercise the rendered offline app and browser-only failure paths."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
assert (ROOT/'index.html').exists(),'Standalone index.html has not been built'
URL=(ROOT/'index.html').as_uri()
FAKE_VOICES=r'''(() => {
  window.__spoken=[]; window.__cancelled=0;
  window.SpeechSynthesisUtterance=function(text){this.text=text};
  const synth = {list:[], listeners:{}, getVoices(){return this.list},
    addEventListener(type, fn){this.listeners[type]=fn},
    cancel(){window.__cancelled++},
    speak(u){window.__spoken.push({text:u.text,lang:u.lang,voice:u.voice.name,rate:u.rate}); if(u.onstart)u.onstart(); if(u.onend)u.onend();}};
  Object.defineProperty(window,'speechSynthesis',{value:synth,configurable:true});
  window.__setVoices=()=>{synth.list=[{name:'English',lang:'en-US',voiceURI:'en'},{name:'France',lang:'fr-FR',voiceURI:'fr'},{name:'Canada',lang:'fr-CA',voiceURI:'ca'}];if(synth.listeners.voiceschanged)synth.listeners.voiceschanged()};
})();'''
results=[]
def check(name,fn):
 result=fn();assert result is not False,name;results.append({'name':name,'passed':True});print('PASS',name)
with sync_playwright() as p:
 browser=p.chromium.launch()
 context=browser.new_context(viewport={'width':1440,'height':1000})
 context.add_init_script(FAKE_VOICES)
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(URL)
 check('nine books and 230 lessons',lambda: (page.locator('.book-card').count()==9 and page.locator('.lesson-card').count()==230) or (_ for _ in ()).throw(AssertionError('catalogue counts')))
 check('missing French voices disables playback',lambda: page.get_by_role('button',name='播放今日例句',exact=True).is_disabled() or (_ for _ in ()).throw(AssertionError('play should be unavailable')))
 page.evaluate('window.__setVoices()')
 page.get_by_label('法语声音').select_option('ca');page.get_by_label('播放速度').fill('0.75')
 page.get_by_role('button',name='播放今日例句',exact=True).click()
 check('late voices, fr-CA and rate',lambda: page.evaluate('window.__spoken.at(-1).lang === "fr-CA" && window.__spoken.at(-1).rate === 0.75'))
 page.get_by_label('搜索课程').fill('rendez-vous')
 check('French search',lambda: page.locator('.lesson-card').count()>0 and page.locator('.lesson-card').count()<230)
 page.get_by_label('搜索课程').fill('虚拟式')
 check('Chinese search',lambda: page.locator('.lesson-card').count()>0)
 page.get_by_label('搜索课程').fill('etre')
 check('accent-insensitive search',lambda: page.locator('.lesson-card').count()>0)
 page.get_by_label('搜索课程').fill('');page.locator('#book-grid .book-card').first.click();page.wait_for_function("document.querySelectorAll('.lesson-card').length===42")
 check('book filter',lambda: page.locator('.lesson-card').count()==42)
 page.locator('#category-tabs').get_by_role('button',name='发音',exact=True).click()
 check('category filter',lambda: page.locator('.lesson-card').count()==50)
 page.get_by_label('搜索课程').fill('xyzunlikely');check('empty search feedback',lambda: page.locator('#empty').is_visible());page.get_by_role('button',name='清除筛选',exact=True).click()
 check('clear filters restores catalogue',lambda: page.locator('.lesson-card').count()==230)
 page.goto(URL+'#G01');page.get_by_role('button',name='练习',exact=True).click()
 page.locator('input[name="q0"]').nth(0).check();page.locator('input[name="q1"]').nth(0).check()
 page.get_by_role('button',name='检查答案',exact=True).click()
 check('exercise feedback reveals explanations',lambda: page.locator('.quiz-feedback').count()==2 and page.locator('#quiz-score').inner_text()!='')
 page.get_by_role('button',name='标记已学',exact=True).click();page.reload()
 check('progress restored',lambda: page.get_by_role('button',name='已学 · 点击取消',exact=True).is_visible())
 page.evaluate('window.__setVoices()');check('late voices restore saved fr-CA preference',lambda: page.get_by_label('法语声音').input_value()=='ca');page.get_by_role('button',name='讲解',exact=True).click();page.get_by_role('button',name='▶ 听完整句',exact=True).first.click()
 check('only French selected voice is used',lambda: all(x['lang'].startswith('fr') for x in page.evaluate('window.__spoken')))
 page.keyboard.press('Control+k');page.wait_for_function("document.activeElement.id==='search'");check('keyboard search opens visible catalogue',lambda: page.locator('#dashboard').is_visible());page.goto(URL+'#G01')
 page.get_by_role('button',name='停止播放',exact=True).click()
 check('stop calls speech cancellation',lambda: page.evaluate('window.__cancelled > 0'))
 page.get_by_role('button',name='学习路线',exact=True).click();page.wait_for_function("document.querySelector('#document-title').textContent==='学习路线与自测'")
 check('study document navigation',lambda: page.locator('#document-title').inner_text()=='学习路线与自测')
 page.goto(URL+'#coverage');check('coverage navigation',lambda: page.locator('.coverage-row').count()==145)
 page.get_by_label('选择原书').select_option('pronunciation-introduction');check('excerpt source warning',lambda: page.locator('.coverage-row').count()==60 and '正文未提供' in page.locator('#document-body').inner_text())
 page.goto(URL+'#G01')
 with page.expect_download() as download_info:page.get_by_role('button',name='下载本课 Markdown',exact=True).click()
 download=download_info.value
 check('Markdown download preserves content',lambda: '谁在做事' in Path(download.path()).read_text())
 page.goto(URL+'#P03');page.screenshot(path=str(ROOT/'docs/desktop.png'),full_page=True)
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(ROOT/'docs/mobile.png'),full_page=True)
 check('mobile has no horizontal overflow',lambda: page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
 check('no JavaScript errors',lambda: not errors)
 context.close()
 blocked=browser.new_context();blocked.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}})")
 bp=blocked.new_page();bp.goto(URL+'#G02');bp.get_by_role('button',name='标记已学',exact=True).click()
 check('blocked storage allows in-memory progress',lambda: bp.get_by_role('button',name='已学 · 点击取消',exact=True).is_visible())
 blocked.close()
 corrupt=browser.new_context();corrupt.add_init_script("try{localStorage.setItem('francais.practice.v1','{broken')}catch(e){}")
 cp=corrupt.new_page();cp.goto(URL+'#G03')
 check('corrupt progress does not break lesson',lambda: cp.locator('#lesson-title').inner_text().startswith('规律动作'))
 corrupt.close();browser.close()
(ROOT/'docs/browser-verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print('%d browser checks passed'%len(results))
