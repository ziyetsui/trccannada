"""Exercise every Oxford picture and recall view in the real offline browser app."""
import ast,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
module=ast.parse((ROOT/'tests/pronunciation_check.py').read_text())
FAKE=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FAKE' for t in n.targets))
manifest=json.loads((ROOT/'scripts/content/sentence-illustrations.json').read_text())
results={'lessons':0,'study_images':0,'recall_images':0,'mobile_scenes':0,'errors':[]}
with sync_playwright() as pw:
    browser=pw.chromium.launch()
    page=browser.new_page(viewport={'width':1440,'height':1100});page.add_init_script(FAKE)
    page.on('pageerror',lambda error:results['errors'].append(str(error)))
    url=(ROOT/'index.html').as_uri()
    page.goto(url+'#T01')
    payload=page.evaluate('JSON.parse(document.querySelector("#library-data").textContent)')
    oxford=[l for l in payload['lessons'] if l['book']=='take-off']
    assert len(oxford)==22
    assert sum(bool(e.get('illustration')) for l in payload['lessons'] for e in l['examples'])==163
    for lesson in oxford:
        lid=lesson['id'];page.evaluate('(id)=>location.hash=id',lid)
        page.wait_for_function('(id)=>document.querySelector("#lesson-breadcrumb").textContent.endsWith(id)',arg=lid)
        for i,e in enumerate(lesson['examples']):
            card=page.locator('.pronunciation-card').nth(i)
            img=card.locator('.sentence-illustration img');img.scroll_into_view_if_needed()
            img.evaluate('(im)=>im.decode()')
            assert img.get_attribute('src')==manifest[f'{lid}:{i+1}']['asset']
            assert img.evaluate('(im)=>im.naturalWidth>=512')
            assert img.get_attribute('loading')=='lazy'
            assert card.get_by_role('button',name='▶ 听整句，再跟一遍',exact=True).is_disabled()
            results['study_images']+=1
            card.locator('.pronunciation-tab').nth(4).click()
            recall=card.locator('.recall-prompt .sentence-illustration img')
            assert recall.get_attribute('src')==manifest[f'{lid}:{i+1}']['asset']
            assert e['fr'] not in recall.get_attribute('alt')
            assert not card.locator('.pronunciation-head .example-fr').is_visible()
            assert not card.locator('.recall-answer').is_visible()
            assert card.locator('.sentence-sound-joke').count()==0
            card.get_by_role('button',name='显示法语，核对一下',exact=True).click()
            assert card.locator('.recall-answer .example-fr').inner_text()==e['fr']
            results['recall_images']+=1
            card.locator('.pronunciation-tab').nth(0).click()
        results['lessons']+=1
    page.set_viewport_size({'width':390,'height':844});page.emulate_media(color_scheme='dark')
    for lesson in oxford:
        page.evaluate('(id)=>location.hash=id',lesson['id'])
        page.wait_for_function('(id)=>document.querySelector("#lesson-breadcrumb").textContent.endsWith(id)',arg=lesson['id'])
        for stage in range(5):
            page.locator('.pronunciation-card').first.locator('.pronunciation-tab').nth(stage).click()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(lesson['id'],stage)
            results['mobile_scenes']+=1
    page.goto(url+'#T01');page.evaluate('window.__voices()')
    first=page.locator('.pronunciation-card').first
    first.get_by_role('button',name='▶ 听整句，再跟一遍',exact=True).click()
    assert page.evaluate('window.__spoken.at(-1).text')=='Bonjour, Madame Chen.'
    first.locator('.sentence-illustration').screenshot(path=str(ROOT/'docs/illustration-mobile-dark.png'))
    page.set_viewport_size({'width':1440,'height':1100});page.emulate_media(color_scheme='light')
    first.locator('.sentence-memory').screenshot(path=str(ROOT/'docs/illustration-desktop.png'))
    first.locator('.pronunciation-tab').nth(4).click()
    first.locator('.recall-prompt').screenshot(path=str(ROOT/'docs/illustration-recall.png'))
    first.locator('.pronunciation-tab').nth(0).click()
    # An actual image load error must preserve the text and original French audio.
    first.locator('.sentence-illustration img').evaluate('(im)=>{im.loading="eager";im.src="assets/missing-picture.webp";}')
    first.locator('.illustration-fallback').wait_for(state='visible')
    assert first.locator('.sentence-sound-joke').is_visible()
    assert first.get_by_role('button',name='▶ 听整句，再跟一遍',exact=True).is_enabled()
    results['image_error_fallback']=True
    page.goto(url+'#G01');assert page.locator('.sentence-illustration').count()==0
    results['other_books_preserved']=True
    assert not results['errors'],results['errors']
    browser.close()
(ROOT/'docs/illustration-browser-verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False))
