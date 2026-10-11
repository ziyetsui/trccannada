"""Check system defaults, manual override, persistence and mobile dark layout."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
URL=(ROOT/'index.html').as_uri()
results=[]
def check(name,condition):
 assert condition,name
 results.append({'name':name,'passed':True});print('PASS',name)
with sync_playwright() as p:
 browser=p.chromium.launch()
 context=browser.new_context(color_scheme='dark',viewport={'width':1440,'height':1000})
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(URL)
 check('first visit follows system dark',page.locator('html').get_attribute('data-theme')=='dark' and page.get_by_role('button',name='切换到明色模式').is_visible())
 check('dark surfaces applied',page.evaluate("getComputedStyle(document.body).backgroundColor==='rgb(23, 31, 28)'"))
 page.emulate_media(color_scheme='light');page.wait_for_function("document.documentElement.dataset.theme==='light'")
 check('system changes followed before manual choice',page.locator('html').get_attribute('data-theme')=='light')
 page.get_by_role('button',name='切换到暗色模式').click();page.emulate_media(color_scheme='light');page.reload()
 check('manual dark choice survives reload and overrides system',page.locator('html').get_attribute('data-theme')=='dark')
 page.goto(URL+'#G01');page.get_by_role('button',name='标记已学',exact=True).click();page.get_by_role('button',name='切换到明色模式').click();page.reload()
 check('theme preference preserves study progress',page.locator('html').get_attribute('data-theme')=='light' and page.get_by_role('button',name='已学 · 点击取消').is_visible())
 page.get_by_role('button',name='切换到暗色模式').click();page.screenshot(path=str(ROOT/'docs/dark-desktop.png'),full_page=True)
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(ROOT/'docs/dark-mobile.png'),full_page=True)
 check('dark mobile lesson has no overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
 page.goto(URL);check('dark mobile dashboard has no overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
 check('no theme JavaScript errors',not errors)
 context.close()
 blocked=browser.new_context(color_scheme='dark');blocked.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}})")
 page=blocked.new_page();page.goto(URL);page.get_by_role('button',name='切换到明色模式').click()
 check('theme switches when storage blocked',page.locator('html').get_attribute('data-theme')=='light')
 blocked.close();browser.close()
(ROOT/'docs/theme-verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
