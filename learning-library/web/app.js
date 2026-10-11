'use strict';
(() => {
const data=JSON.parse(document.getElementById('library-data').textContent), lessons=data.lessons, byId=new Map(lessons.map(l=>[l.id,l]));
window.LESSONS=lessons;
const $=s=>document.querySelector(s), el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n}, button=(text,fn,cls)=>{const n=el('button',text,cls);n.type='button';n.onclick=fn;return n};
// Theme preference is separate from study progress and applies before first paint.
const root=document.documentElement,themeToggle=$('#theme-toggle');
function applyTheme(theme){
 root.dataset.theme=theme;
 const dark=theme==='dark';
 themeToggle.textContent=dark?'☀ 明色':'☾ 暗色';
 themeToggle.setAttribute('aria-label',dark?'切换到明色模式':'切换到暗色模式');
 themeToggle.setAttribute('aria-pressed',String(dark));
 $('meta[name="theme-color"]').content=dark?'#171f1c':'#f7f5ef';
}
applyTheme(root.dataset.theme||'light');
themeToggle.onclick=()=>{
 const theme=root.dataset.theme==='dark'?'light':'dark';
 root.dataset.themePreference=theme;applyTheme(theme);
 try{localStorage.setItem('francais.theme.v1',theme);}
 catch(e){themeToggle.title='本次切换已生效，浏览器未能保存此设置。';}
};
if(window.matchMedia){
 const systemTheme=matchMedia('(prefers-color-scheme: dark)');
 systemTheme.addEventListener('change',e=>{
  if(root.dataset.themePreference==='system')applyTheme(e.matches?'dark':'light');
 });
}
const books=[...new Set(lessons.map(l=>l.book))].map(id=>({...lessons.find(l=>l.book===id),id,lessons:lessons.filter(l=>l.book===id)}));
const key='francais.practice.v1';let saved={};
function warn(){ $('#storage-status').hidden=false;$('#storage-status').textContent='浏览器未能保存进度；本次学习仍可继续。'; }
try{saved=JSON.parse(localStorage.getItem(key)||'{}');if(!saved||typeof saved!=='object'||Array.isArray(saved))saved={};}catch(e){warn();saved={};}
let done=new Set((Array.isArray(saved.done)?saved.done:[]).filter(x=>byId.has(x))),last=byId.has(saved.last)?saved.last:null,voiceURI=typeof saved.voice==='string'?saved.voice:'',rate=typeof saved.rate==='number'&&saved.rate>=.65&&saved.rate<=1.15?saved.rate:.85;
let filter={book:'all',category:'all',level:'all',progress:'all',search:''},current=null,mode='learn',answers=new Map(),submitted=new Set(),voices=[],generation=0;
function persist(){try{localStorage.setItem(key,JSON.stringify({done:[...done],last,voice:voiceURI,rate}));}catch(e){warn();}}
function go(id=''){if(location.hash.slice(1)===id)route();else location.hash=id;}
function announce(t){$('#live').textContent=t;}
const norm=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[’‘]/g,"'").replace(/\s+/g," ").toLowerCase();
const categoryNames={阅读:'阅读',情景:'情景',all:'全部','语法':'语法','表达':'表达','发音':'发音','习语':'习语'};
function updateProgress(){ $('#top-progress').textContent=`已学 ${done.size} / ${lessons.length}`;$('#continue').textContent=last?`继续学习 · ${last}`:'从第一课开始'; }
function filterBook(id){filter.book=id;filter.category='all';go();renderCatalogue();$('#catalogue-section').scrollIntoView({behavior:'auto'});}
function renderCatalogue(){
 $('#book-nav').replaceChildren(button(`全部课程 · ${lessons.length}`,()=>filterBook('all'),'book-nav-button'+(filter.book==='all'?' active':'')));
 for(const b of books){const n=button(`${b.book_title} · ${b.lessons.length}`,()=>filterBook(b.id),'book-nav-button'+(filter.book===b.id?' active':''));n.setAttribute('aria-pressed',String(filter.book===b.id));$('#book-nav').append(n);}
 $('#category-tabs').replaceChildren();for(const [id,name]of Object.entries(categoryNames)){const n=button(name,()=>{filter.category=id;filter.book='all';renderCatalogue()});n.setAttribute('aria-pressed',String(id===filter.category));$('#category-tabs').append(n);}
 const query=norm(filter.search.trim());const found=lessons.filter(l=>(filter.book==='all'||l.book===filter.book)&&(filter.category==='all'||l.category===filter.category)&&(filter.level==='all'||l.level===filter.level)&&(filter.progress==='all'||(filter.progress==='done')===done.has(l.id))&&(!query||norm([l.id,l.title,l.goal,l.explanation,l.source_reader?(sourceUnit(l)?.blocks||[]).map(b=>b.text).join(' '):'',...l.examples.map(e=>e.fr+' '+e.zh)].join(' ')).includes(query)));
 $('#result-count').textContent=`${found.length} 课`;$('#empty').hidden=found.length>0;$('#catalogue').replaceChildren();
 for(const l of found){const n=button('',()=>go(l.id),'lesson-card');const top=el('div',undefined,'card-top');top.append(el('span',`${l.id} · ${l.level}`),el('span',done.has(l.id)?'已学 ✓':l.book_title));n.append(top,el('h3',l.title),el('p',l.goal));$('#catalogue').append(n);}
 updateProgress();
}
let playbackTimer=null;
function stop(){generation++;clearTimeout(playbackTimer);playbackTimer=null;if(window.speechSynthesis)window.speechSynthesis.cancel();document.querySelectorAll('.playing').forEach(n=>n.classList.remove('playing'));if(voices.length)$('#voice-status').textContent='点击例句即可听';}
function refreshVoices(){
 voices=window.speechSynthesis?window.speechSynthesis.getVoices().filter(v=>/^fr(?:[-_]|$)/i.test(v.lang)):[];
 if(voices.length&&!voices.some(v=>v.voiceURI===voiceURI))voiceURI=(voices.find(v=>v.lang.toLowerCase()==='fr-fr')||voices[0]||{}).voiceURI||'';
 $('#voice').replaceChildren();if(!voices.length){const o=el('option','设备暂未提供法语声音');o.value='';$('#voice').append(o);}else for(const v of voices){const o=el('option',`${v.name} · ${v.lang}`);o.value=v.voiceURI;$('#voice').append(o);}
 $('#voice').value=voiceURI;$('#voice').disabled=!voices.length;$('#voice-status').textContent=voices.length?'点击例句即可听':'请在设备语音设置中添加法语声音';
 document.querySelectorAll('[data-speak]').forEach(n=>n.disabled=!voices.length);
}
function speakSequence(steps,control){
 const v=voices.find(v=>v.voiceURI===voiceURI);stop();if(!v||!window.SpeechSynthesisUtterance)return;
 const token=generation;let i=0;
 const clearPlaying=()=>{control?.classList.remove('playing');document.querySelectorAll('.word-select.playing').forEach(n=>n.classList.remove('playing'));};
 const fail=()=>{if(token!==generation)return;clearTimeout(playbackTimer);clearPlaying();$('#voice-status').textContent='播放未完成，请再试一次或更换法语声音';};
 const next=()=>{
  if(token!==generation)return;
  if(i>=steps.length){clearPlaying();$('#voice-status').textContent='播放完成 · 试着自己说一次';return;}
  const s=steps[i++],u=new SpeechSynthesisUtterance(s.text);u.voice=v;u.lang=v.lang.replace('_','-');u.rate=s.rate??rate;
  u.onstart=()=>{if(token!==generation)return;control?.classList.add('playing');s.node?.classList.add('playing');$('#voice-status').textContent=`正在播放 ${i} / ${steps.length} · ${s.text}`;};
  u.onend=()=>{if(token!==generation)return;s.node?.classList.remove('playing');if(s.gap){$('#voice-status').textContent=`轮到你跟读 · ${s.text}`;playbackTimer=setTimeout(next,s.gap);}else next();};
  u.onerror=fail;try{window.speechSynthesis.speak(u);}catch(e){fail();}
 };next();
}
function speak(text,n,customRate){speakSequence([{text,rate:customRate}],n);}
function playButton(text,index){const n=button('▶',()=>speak(text,n),'round');n.dataset.speak=text;n.setAttribute('aria-label',`播放例句 ${index}`);n.disabled=!voices.length;return n;}
function block(title,text,cls='lesson-block'){const n=el('section',undefined,cls);n.append(el('h2',title));for(const p of text.split(/\n\n/))n.append(el('p',p));return n;}
function sourceUnit(l){return data.sources?.[l.source_reader?.book_id]?.units.find(u=>u.unit===l.source_reader.unit);}
function showIssues(l,target){const issues=data.sources?.[l.source_reader?.book_id]?.issues||[];for(const issue of issues.filter(i=>i.unit===0||i.unit===l.source_reader.unit))target.append(block('原书核对说明',issue.message,'notice'));}
function sourceBlock(b,index){const row=el('div',undefined,'source-block');row.id=b.id;const ref=el('p',`${b.id} · ${b.source_ref||''}`,'small muted');row.append(ref);const text=el('p',b.text,'source-text');if(b.lang==='fr')text.lang='fr';row.append(text);if(b.lang==='fr'){const play=playButton(b.text,index);play.setAttribute('aria-label',`朗读原文段落 ${index}`);row.append(play);}if(b.image_file){const a=el('a','核对扫描原图 ↗');a.href=b.image_file;a.target='_blank';a.rel='noopener';row.append(a);}if(b.source_ref?.startsWith('OEBPS/')){const a=el('a','打开原始 EPUB 文档 ↗');a.href='sources/french-stories/raw/'+b.source_ref;a.target='_blank';a.rel='noopener';row.append(a);}return row;}
function sourceGroups(blocks,target){const labels={story:'故事原文',vocabulary:'原书词表',exercise:'原书练习',answer:'原书答案',summary:'原书摘要',source:'完整机器转录',other:'原书其他内容'};let previous='',group=null;for(const [i,b]of blocks.entries()){const role=b.role||'other';if(role!==previous){group=el('details',undefined,'source-group');group.append(el('summary',labels[role]||role));if(role==='story')group.open=true;target.append(group);previous=role;}group.append(sourceBlock(b,i+1));}}
function renderSource(l,target){const book=data.sources?.[l.source_reader?.book_id],unit=sourceUnit(l);target.append(el('h2','本课原书全文'));if(!unit){target.append(el('p','此课程包只含新编教学。完整原书阅读请打开本机 learning-library/index.html。'));return;}target.append(el('p',book.notice||'用户提供原书的本地转录。来源正文、词表、原题和原答案均照存；后者可能含原书错误。新编中文讲解与练习在讲解／练习页。','small'));showIssues(l,target);const controls=el('div',undefined,'source-controls');controls.append(button('朗读选中的法语',()=>{const selection=window.getSelection();if(!selection||!selection.toString().trim()||!target.contains(selection.anchorNode)||!target.contains(selection.focusNode)){announce('请先在本课原文中选中一段法语。');return;}const text=selection.toString().trim();if(text.length>3500){announce('请每次选择不超过3500个字符。');return;}speak(text,controls.querySelector('button'));},'quiet'));controls.querySelector('button').dataset.speak='selection';controls.querySelector('button').disabled=!voices.length;target.append(controls);sourceGroups(unit.blocks,target);}
function renderSourceCatalogue(target){target.append(el('p','新增资料全文保留在本机。EPUB按spine顺序转换；Oxford扫描本按PDF物理页保存，并另按左右半页识别以定位原单元。原文转录不等于人工校订，TTS不等于原书CD。'));for(const id of ['french-stories','oxford-take-off']){const book=data.sources?.[id],section=el('section',undefined,'lesson-block');section.append(el('h2',book?.title||id));if(book){const a=el('a','完整来源 Markdown ↗');a.href=`sources/${id}/book.md`;a.target='_blank';section.append(a);}if(book){for(const issue of (book.issues||[]).filter(i=>i.unit===0))section.append(block('全书核对说明',issue.message,'notice'));const front=el('details');front.append(el('summary','前言、书目信息与卷间材料'));sourceGroups((book.front_matter||[]).flatMap(b=>b.blocks||[b]),front);section.append(front);for(const u of book.units){const lesson=lessons.find(l=>l.source_reader?.book_id===id&&l.source_reader.unit===u.unit);if(lesson)section.append(button(`${lesson.id} · ${u.title}`,()=>{go(lesson.id);},'related-link'));}}else section.append(el('p','分享课程包不含原书全文，请使用本机完整版。'));target.append(section);}}
function renderLesson(){
 const l=current;$('#source-tab').hidden=!l.source_reader;$('#lesson-title').textContent=l.title;$('#lesson-breadcrumb').textContent=`${l.book_title} / ${l.id}`;$('#lesson-meta').textContent=`${l.level} · 约 ${l.minutes} 分钟 · ${done.has(l.id)?'已学':'待学习'}`;$('#mark').textContent=done.has(l.id)?'已学 · 点击取消':'标记已学';$('#side-goal').textContent=l.goal;
 $('#related').replaceChildren();for(const id of l.prerequisites)$('#related').append(button(`${id} ${byId.get(id).title}`,()=>go(id),'related-link'));if(!l.prerequisites.length)$('#related').append(el('p','可以从这里开始。','small'));
 const siblings=lessons.filter(x=>x.book===l.book),i=siblings.findIndex(x=>x.id===l.id);$('#lesson-position').textContent=`本册 ${i+1} / ${siblings.length}`;$('#previous').disabled=i===0;$('#next').disabled=i===siblings.length-1;$('#previous').onclick=()=>go(siblings[i-1].id);$('#next').onclick=()=>go(siblings[i+1].id);
 document.querySelectorAll('[data-view]').forEach(n=>n.setAttribute('aria-pressed',String(n.dataset.view===mode)));
 const content=$('#lesson-content');content.replaceChildren();
 if(mode==='learn'){
 if(l.source_reader){const link=button('打开本课完整原文、词表、原题与答案 →',()=>{mode='source';renderLesson()},'source-open');content.append(link);showIssues(l,content);}
 content.append(block('这一课，你会学到',l.goal,'goal-box'),block('把规则说清楚',l.explanation),block('给小朋友的比喻',l.analogy,'analogy-box'));
 const examples=el('section',undefined,l.pronunciation_guide?'pronunciation-examples':'lesson-block');examples.append(el('h2',l.pronunciation_guide?'看懂、拆开、连起来，再自己说':'听一句，说一句'));
 if(l.pronunciation_guide)examples.append(el('p','每句都有五种学习视图。先用慢速词音认清楚，再回到短语和正常语速。音标采用宽式学习标注；声音仍来自所选设备语音，不能保证演出全部口语缩减或地区变体。','small muted'));
 l.examples.forEach((e,j)=>{if(e.pronunciation){examples.append(window.createPronunciationExample(e,j+1,{el,button,stop,speak,sequence:speakSequence,available:()=>voices.length>0}));return;}const row=el('div',undefined,'example'),copy=el('div'),fr=el('p',e.fr,'example-fr');fr.lang='fr';copy.append(fr,el('p',e.zh,'example-zh'));row.append(copy,playButton(e.fr,j+1));examples.append(row)});content.append(examples,block('一分钟，把它用起来',l.application));
 const refs=el('section',undefined,'refs');refs.append(el('h2','参考资料'));for(const r of l.references){const a=el('a',r.label);a.href=r.url;a.target='_blank';a.rel='noopener noreferrer';refs.append(a,el('br'));}content.append(refs);
 }else if(mode==='source'){renderSource(l,content);
 }else if(mode==='practice'){
 content.append(el('h2','试着自己选一选'));const selected=answers.get(l.id)||[];
 l.quiz.forEach((q,j)=>{const field=el('fieldset',undefined,'quiz');field.append(el('legend',`${j+1}. ${q.prompt}`));q.choices.forEach((choice,k)=>{const label=el('label'),radio=el('input');radio.type='radio';radio.name=`q${j}`;radio.value=k;radio.checked=selected[j]===k;radio.onchange=()=>{selected[j]=k;answers.set(l.id,selected);submitted.delete(l.id);content.querySelectorAll('.quiz-feedback').forEach(n=>n.remove());const s=$('#quiz-score');if(s)s.textContent='选择已更新，请重新检查答案。';};label.append(radio,document.createTextNode(choice));field.append(label)});if(submitted.has(l.id))field.append(el('p',`${selected[j]===undefined?'还没有选择':selected[j]===q.answer?'答对了':'再想一想'}。${q.reason}`,'quiz-feedback'+(selected[j]===q.answer?'':' wrong')));content.append(field)});
 const score=el('p',submitted.has(l.id)?`${l.quiz.filter((q,j)=>selected[j]===q.answer).length} / ${l.quiz.length} 题正确。读一读原因，再用自己的话说一次。`:'');score.id='quiz-score';score.setAttribute('role','status');content.append(button('检查答案',()=>{submitted.add(l.id);renderLesson()},'primary'),score);
 }else{content.append(el('h2','答案与原因'));l.quiz.forEach((q,j)=>content.append(block(`${j+1}. ${q.prompt}`,`${String.fromCharCode(65+q.answer)}. ${q.choices[q.answer]}\n\n${q.reason}`,'answer-card')));}
}
function inline(n,text){const pattern=/\[([^\]]+)\]\((https:\/\/[^)]+)\)|\b([GEAPMFIST]\d{2})\b/g;let m,lastIndex=0;while((m=pattern.exec(text))){n.append(document.createTextNode(text.slice(lastIndex,m.index)));if(m[1]){const a=el('a',m[1]);a.href=m[2];a.target='_blank';a.rel='noopener noreferrer';n.append(a);}else if(byId.has(m[3]))n.append(button(m[3],()=>go(m[3]),'text-button'));else n.append(document.createTextNode(m[0]));lastIndex=pattern.lastIndex;}n.append(document.createTextNode(text.slice(lastIndex)));}
function markdown(text,target){const lines=text.split('\n');let container=target,list=null;for(let i=0;i<lines.length;i++){const line=lines[i].trim();if(!line||line.startsWith('# ')){list=null;continue;}if(/^#{2,4} /.test(line)){const level=line.match(/^#+/)[0].length,title=line.replace(/^#+ /,'');if(level===2){container=target;if(/答案/.test(title)){const d=el('details');d.append(el('summary',title));target.append(d);container=d;list=null;continue;}}const h=el('h'+level);inline(h,title);container.append(h);list=null;continue;}if(line.startsWith('|')){const wrap=el('div',undefined,'table-scroll'),table=el('table');let first=true;while(i<lines.length&&lines[i].trim().startsWith('|')){const cells=lines[i].trim().split('|').slice(1,-1).map(s=>s.trim());if(!cells.every(c=>/^:?-+:?$/.test(c))){const tr=el('tr');for(const c of cells){const td=el(first?'th':'td');inline(td,c);tr.append(td)}table.append(tr);first=false;}i++;}i--;wrap.append(table);container.append(wrap);list=null;continue;}if(/^[-*] /.test(line)||/^\d+\. /.test(line)){if(!list){list=el('ul');container.append(list)}const li=el('li');inline(li,line.replace(/^[-*] /,''));list.append(li);}else{list=null;const p=el('p');inline(p,line);container.append(p);}}}
function renderDocument(id){const titles={'study-guide':'学习路线与自测',reference:'随手查 · 法语参考表',review:'综合复习',coverage:'原书框架对应',sources:'新增来源资料 · 原文与教学分开'};$('#document-title').textContent=titles[id];const target=$('#document-body');target.replaceChildren();if(id==='sources'){renderSourceCatalogue(target);return;}if(id!=='coverage'){markdown(data.documents[id],target);return;}
 target.append(el('p',`原书 ${data.coverage.records.length} 个框架条目已对应到 ${lessons.length} 个学习单元。重复目标合并，英语特有项目改为法语所需知识；这是编号级框架对应，不表示逐句、逐题或原音频全部复刻。发音入门 Introduction PDF 只有 19 页，后续单元仅有目录信息。新增两份资料按原序保留全部法语原文，另编中文辅助与练习。`));
 const select=el('select');select.className='coverage-select';select.setAttribute('aria-label','选择原书');for(const [b,c]of Object.entries(data.coverage.source_counts)){const o=el('option',`${b} · ${c} 单元`);o.value=b;select.append(o)}const rows=el('div');const show=()=>{rows.replaceChildren();for(const r of data.coverage.records.filter(r=>r.source_book===select.value)){const n=el('div',undefined,'coverage-row');n.append(el('strong',r.source_title||`原书单元 ${r.source_unit}`),el('p',r.adaptation));for(const id of r.targets)n.append(button(`${id} ${byId.get(id).title}`,()=>go(id),'related-link'));if(r.source_body_available===false)n.append(el('p','来源范围：目录可见，正文未提供。','small'));rows.append(n)}};select.onchange=show;target.append(select,rows);show();
}
function route(){stop();let id;try{id=decodeURIComponent(location.hash.slice(1));}catch(e){id='';}if(id==='main')return;current=byId.get(id)||null;$('#dashboard').hidden=!!current||id in data.documents||id==='coverage'||id==='sources';$('#lesson').hidden=!current;$('#document').hidden=!(id in data.documents||id==='coverage'||id==='sources');if(current){last=current.id;persist();mode='learn';renderLesson();$('#lesson-title').focus();}else if(!$('#document').hidden){renderDocument(id);$('#document-title').focus();}else renderCatalogue();updateProgress();window.scrollTo(0,0);}
function download(text,name){const url=URL.createObjectURL(new Blob([text],{type:'text/markdown;charset=utf-8'})),a=el('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
$('#home').onclick=()=>go();$('#back-library').onclick=()=>go();$('#back-doc').onclick=()=>go();document.querySelectorAll('[data-doc]').forEach(n=>n.onclick=()=>go(n.dataset.doc));document.querySelectorAll('[data-view]').forEach(n=>n.onclick=()=>{mode=n.dataset.view;stop();renderLesson()});
$('#mark').onclick=()=>{if(done.has(current.id))done.delete(current.id);else done.add(current.id);persist();renderLesson();updateProgress();announce(done.has(current.id)?'本课已标记为已学':'本课已取消已学标记')};$('#download-lesson').onclick=()=>download(current.markdown,`${current.id}.md`);$('#download-book').onclick=()=>download(lessons.filter(l=>l.book===current.book).map(l=>l.markdown).join('\n\n---\n\n'),`${current.book}.md`);
$('#continue').onclick=()=>go(last||'P01');$('#search').oninput=e=>{filter.search=e.target.value;renderCatalogue()};$('#level').onchange=e=>{filter.level=e.target.value;go();renderCatalogue()};$('#progress-filter').onchange=e=>{filter.progress=e.target.value;go();renderCatalogue()};$('#reset').onclick=()=>{filter={book:'all',category:'all',level:'all',progress:'all',search:''};$('#search').value='';$('#level').value='all';$('#progress-filter').value='all';renderCatalogue()};
$('#rate').value=rate;$('#rate-label').textContent=rate.toFixed(2)+'×';$('#rate').oninput=e=>{rate=Number(e.target.value);$('#rate-label').textContent=rate.toFixed(2)+'×';persist()};$('#voice').onchange=e=>{stop();voiceURI=e.target.value;persist()};$('#stop').onclick=stop;$('#daily-play').dataset.speak='J’ai envie d’apprendre.';$('#daily-play').onclick=()=>speak('J’ai envie d’apprendre.',$('#daily-play'));
for(const [i,b]of books.entries()){const n=button('',()=>filterBook(b.id),'book-card');n.dataset.category=b.category;n.append(el('span',`0${i+1} / ${b.lessons.length} 课`,'tiny-label'),el('h3',b.book_title),el('p',b.book_fr),el('span',`${[...new Set(b.lessons.map(l=>l.level))].join(' – ')}  ↗`,'small'));$('#book-grid').append(n)}
document.addEventListener('keydown',e=>{if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();go();route();$('#search').focus()}});window.addEventListener('hashchange',route);window.addEventListener('pagehide',stop);if(window.speechSynthesis)window.speechSynthesis.addEventListener('voiceschanged',refreshVoices);refreshVoices();renderCatalogue();route();
})();
