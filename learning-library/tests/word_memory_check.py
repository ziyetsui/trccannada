"""Check sound-picture mnemonics and selection, without relying on a device voice."""
from pathlib import Path
import ast,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
module=ast.parse((ROOT/'tests/pronunciation_check.py').read_text())
FAKE=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FAKE' for t in n.targets))
with sync_playwright() as pw:
 browser=pw.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1100});page.add_init_script(FAKE)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto((ROOT/'index.html').as_uri()+'#I07')
 coverage=page.evaluate('''() => {
  const data=JSON.parse(document.querySelector('#library-data').textContent),seen=new Set();let count=0;
  for(const lesson of data.lessons)for(const example of lesson.examples)for(const w of example.pronunciation.words){
   const m=window.wordPronunciationMemory(w);
   if(!m.hook||!m.line||!m.cue||!m.route||!m.steps.length||!m.avoid||JSON.stringify(m).includes('undefined'))throw Error('Missing sound hook or memory: '+w.fr);
   const key=w.fr.toLowerCase().replaceAll('’',"'");
   if(m.kind!=='逐词编写'||!window.wordMemoryCatalog[key]||m.line!==window.wordMemoryCatalog[key].line)throw Error('Uncurated memory: '+key);
   const sounds=w.ipa.match(/(?:[ɛɑɔœa]̃)|[iyueɛøœəaɑoɔjwɥʁʃʒɲŋlnmpbtdkɡgfvszɪʊɒθ]/gu)||[];
   if(sounds.join('')!==w.ipa)throw Error('Unexplained sound: '+w.fr+' '+w.ipa);
   seen.add(w.fr.toLowerCase().replaceAll('’',"'"));count++;
  }return {forms:seen.size,occurrences:count};
 }''')
 assert coverage['forms']==1394,coverage
 assert page.evaluate('Object.keys(window.wordMemoryCatalog).length')==1394
 assert page.evaluate('''() => {
  const saved=window.wordMemoryCatalog.yeux;delete window.wordMemoryCatalog.yeux;
  try {window.wordPronunciationMemory({fr:'yeux',ipa:'jø'});return false;}
  catch(e){return e.message.includes('Missing authored');}
  finally{window.wordMemoryCatalog.yeux=saved;}
 }''')
 first=page.locator('.pronunciation-card').first
 for i,word in enumerate(['Ce','billet','coûte','les','yeux','de','la','tête']):
  first.locator('.word-select').nth(i).click()
  box=first.locator('.word-memory')
  assert box.get_attribute('aria-label')==word+' 的发音巧记'
  assert box.locator('li').count()>=3
  assert box.locator('.word-memory-line').is_visible()
  assert box.locator('.word-memory-hook').is_visible()
  assert first.locator('.word-detail').get_by_role('heading',name='发音规则（保留）',exact=True).is_visible()
 first.locator('.word-select').nth(4).click()
 assert '眼睛喊耶，嘴巴亲亲。' in first.locator('.word-memory').inner_text()
 assert '开心喊“耶”' in first.locator('.word-memory').inner_text()
 assert not first.locator('.word-memory-steps').is_visible()
 first.locator('.word-memory-practice summary').click()
 assert first.locator('.word-memory-steps').is_visible()
 assert '别直接读成中文“哟”' in first.locator('.word-memory').inner_text()
 assert first.locator('.word-memory button').is_disabled()
 page.evaluate('window.__voices()')
 first.locator('.word-memory button').click()
 assert page.evaluate('window.__spoken.at(-1).text==="yeux" && window.__spoken.at(-1).rate===0.65')
 first.locator('.word-memory-practice summary').click()
 first.locator('.word-detail').screenshot(path=str(ROOT/'docs/word-memory-yeux.png'))
 first.locator('.word-select').nth(1).click()
 assert '毕业了，买票回家！' in first.locator('.word-memory').inner_text()
 assert '毕业帽' in first.locator('.word-memory').inner_text()
 assert not first.locator('.word-memory-steps').is_visible()
 first.locator('.word-detail').screenshot(path=str(ROOT/'docs/word-memory-billet.png'))
 page.set_viewport_size({'width':390,'height':844})
 for i in range(8):
  first.locator('.word-select').nth(i).click()
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 first.locator('.word-select').nth(4).click()
 first.locator('.word-detail').screenshot(path=str(ROOT/'docs/word-memory-yeux-mobile.png'))
 for step in [1,2]:
  first.locator('.pronunciation-tab').nth(step).click()
  first.locator('.word-select').nth(4).click()
  assert '眼睛喊耶' in first.locator('.word-memory').inner_text()
 first.locator('.pronunciation-tab').nth(4).click()
 assert first.locator('.word-memory').count()==0
 page.goto((ROOT/'index.html').as_uri()+'#T02')
 target=page.locator('.pronunciation-card').nth(2)
 for i in range(5):
  target.locator('.word-select').nth(i).click()
  assert target.locator('.word-memory-hook').is_visible()
  assert target.locator('.word-memory-cue').inner_text().startswith('小画面：')
 target.locator('.word-select').nth(2).click()
 assert '一直向前' in target.locator('.word-detail').inner_text()
 target.locator('.word-select').first.click()
 assert '继续画线' not in target.locator('.word-memory').inner_text()
 target.locator('.word-detail').screenshot(path=str(ROOT/'docs/word-memory-continuez-mobile.png'))
 page.set_viewport_size({'width':1440,'height':1100})
 target.locator('.word-detail').screenshot(path=str(ROOT/'docs/word-memory-continuez.png'))
 assert not errors,errors
 browser.close()
report={**coverage,'checks':['all word occurrences use the authored 1394-entry catalog','missing authored entry fails explicitly','all word occurrences have explicit sound hooks, scenes and articulation routes','all eight I07 selections update the mnemonic','yeux has sound-picture mnemonic and pronunciation warning','billet links graduation to a ticket','mouth practice is collapsed initially and can be expanded','rules retained','no-voice access and French slow playback','mobile fit','three word views supported','recall hides word hints','no JavaScript errors']}
(ROOT/'docs/word-memory-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
