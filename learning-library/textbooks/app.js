'use strict';
(() => {
const data=JSON.parse(document.getElementById('textbook-data').textContent);
const lessons=data.lessons,byId=new Map(lessons.map(l=>[l.id,l])),books=data.books;
const $=s=>document.querySelector(s),node=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
const normalize=s=>String(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[’‘]/g,"'").toLowerCase();
const KEY='francais.textbooks.v1',DAY=86400000;let saved={};
function storageWarning(){ $('#storage-status').hidden=false;$('#storage-status').textContent='浏览器未能保存进度；本次阅读、练习和主题切换仍可使用。'; }
try{saved=JSON.parse(localStorage.getItem(KEY)||'{}');if(!saved||typeof saved!=='object'||Array.isArray(saved))saved={};}catch(e){storageWarning();}
let done=new Set((Array.isArray(saved.done)?saved.done:[]).filter(id=>byId.has(id)));
let last=byId.has(saved.last)?saved.last:null;
let reviews=saved.reviews&&typeof saved.reviews==='object'&&!Array.isArray(saved.reviews)?saved.reviews:{};
let rate=typeof saved.rate==='number'&&saved.rate>=.65&&saved.rate<=1.1?saved.rate:.85;
let voiceURI=typeof saved.voice==='string'?saved.voice:'',voices=[],current=null,recalling=false;
let timer=null,generation=0,filterBook='all',filterStatus='all',search='';
function persist(){try{localStorage.setItem(KEY,JSON.stringify({done:[...done],last,reviews,rate,voice:voiceURI}));}catch(e){storageWarning();}}
function announce(text){$('#live').textContent=text;}
function theme(){const dark=document.documentElement.dataset.theme==='dark';$('#theme-toggle').textContent=dark?'☀ 明色':'☾ 暗色';$('#theme-toggle').setAttribute('aria-pressed',String(dark));document.querySelector('meta[name="theme-color"]').content=dark?'#171f1c':'#f7f5ef';}
theme();$('#theme-toggle').onclick=()=>{document.documentElement.dataset.theme=document.documentElement.dataset.theme==='dark'?'light':'dark';theme();try{localStorage.setItem('francais.theme.v1',document.documentElement.dataset.theme);}catch(e){storageWarning();}};
const isDue=id=>{const r=reviews[id];return r&&typeof r.due==='number'&&r.due<=Date.now();};
function updateProgress(){const due=lessons.filter(l=>isDue(l.id)).length;$('#progress-summary').textContent=`已标记学过 ${done.size} / ${lessons.length} 课 · ${due} 课到期回忆`;$('#continue').textContent=last?`继续 ${last} · ${byId.get(last).title}`:'从零开始 · 语音第1课';$('#due-filter').textContent=`今天的回忆练习${due?' · '+due:''}`;}
function catalogue(){
const query=normalize(search.trim()),exact=byId.has(search.trim().toUpperCase())?search.trim().toUpperCase():null;
const searchable=l=>[l.id,l.title,l.book_title,l.source_title,l.goal,l.explanation,l.analogy,l.application,l.teacher_notes||'',l.prerequisite_note||'',...l.teaching_points,...l.self_check,l.anchor.fr,l.anchor.zh,l.anchor.sound,l.anchor.movie,l.anchor.pronunciation,...l.quiz.flatMap(q=>[q.prompt,...q.choices,q.reason])].join(' ');
const found=lessons.filter(l=>(filterBook==='all'||l.book===filterBook)&&(filterStatus==='all'||filterStatus==='done'&&done.has(l.id)||filterStatus==='new'&&!done.has(l.id)||filterStatus==='due'&&isDue(l.id))&&(exact?l.id===exact:!query||normalize(searchable(l)).includes(query)));
$('#catalogue').replaceChildren();$('#result-count').textContent=`${found.length} / ${lessons.length} 课`;$('#empty').hidden=found.length>0;
for(const l of found){const b=node('button',undefined,'lesson-card');b.type='button';b.dataset.lesson=l.id;const meta=node('span',undefined,'card-meta');meta.append(node('span',l.id+' · '+l.level),node('span',done.has(l.id)?'已学 ✓':isDue(l.id)?'到期回忆':l.minutes+'分钟'));b.append(meta,node('h3',l.title),node('p',l.goal));b.onclick=()=>go(l.id);$('#catalogue').append(b);}
updateProgress();
}
function go(id=''){if(location.hash.slice(1)===id)route();else location.hash=id;}
function paragraphs(target,text){target.replaceChildren();for(const part of String(text).split(/\n\s*\n/)){const p=node('p',part);target.append(p);}}
function list(target,items){target.replaceChildren(...items.map(t=>node('li',t)));}
function stop(){generation++;clearTimeout(timer);timer=null;try{window.speechSynthesis?.cancel();}catch(e){}}
function refreshVoices(){
try{voices=(window.speechSynthesis?.getVoices()||[]).filter(v=>/^fr(?:[-_]|$)/i.test(v.lang));}catch(e){voices=[];}
if(voices.length&&!voices.some(v=>v.voiceURI===voiceURI))voiceURI=(voices.find(v=>/^fr[-_]fr$/i.test(v.lang))||voices[0]).voiceURI;
$('#voice').replaceChildren();
if(!voices.length){const o=node('option','设备暂未提供法语声音');o.value='';$('#voice').append(o);}
for(const v of voices){const o=node('option',v.name+' · '+v.lang);o.value=v.voiceURI;$('#voice').append(o);}
$('#voice').value=voiceURI;$('#voice').disabled=!voices.length;
$('#voice-status').textContent=voices.length?'点击整句或单词听法语；之后请自己说一次。':'设备没有法语声音，请在系统语音设置中添加。';
for(const n of document.querySelectorAll('#listen,#slow,#chunks,.word'))n.disabled=!voices.length;
}
function speak(text,speed=rate){
stop();const v=voices.find(v=>v.voiceURI===voiceURI);if(!v||!window.SpeechSynthesisUtterance)return;
try{const u=new SpeechSynthesisUtterance(text);u.voice=v;u.lang=v.lang.replace('_','-');u.rate=speed;u.onerror=()=>{$('#voice-status').textContent='朗读未完成，请再试一次或更换法语声音。';};window.speechSynthesis.speak(u);}catch(e){$('#voice-status').textContent='设备未能播放，请更换法语声音后再试。';}
}
function echo(){
stop();if(!current)return;const v=voices.find(v=>v.voiceURI===voiceURI);if(!v||!window.SpeechSynthesisUtterance)return;
const steps=current.anchor.fr.split(/(?<=[,;:!?。.，])\s*/).filter(Boolean);steps.push(current.anchor.fr);let i=0;const token=generation;
function next(){if(token!==generation||i>=steps.length)return;const text=steps[i++],u=new SpeechSynthesisUtterance(text);u.voice=v;u.lang=v.lang.replace('_','-');u.rate=Math.min(rate,.8);u.onend=()=>{if(token!==generation)return;$('#voice-status').textContent=i<steps.length?'轮到你跟读，稍后回到完整句。':'跟读结束。现在隐藏文字，看图自己说一次。';timer=setTimeout(next,Math.max(1600,text.length*65));};u.onerror=()=>{$('#voice-status').textContent='跟读播放中断，请重试或更换声音。';};try{window.speechSynthesis.speak(u);}catch(e){$('#voice-status').textContent='设备无法播放。';}}
next();
}
function recall(active){
stop();recalling=active;$('#answer-content').hidden=active;$('#recall-instruction').hidden=!active;$('#recall').hidden=active;$('#reveal').hidden=!active;
$('#anchor-image').alt=active?'记忆场景：请尝试看图用法语表达。':current.anchor.illustration?.alt||'记忆场景';
for(const n of document.querySelectorAll('.study-support'))n.hidden=active;
$('#retry').hidden=true;$('#remembered').hidden=true;
if(active){$('#review-status').textContent='不看文字，先说出来；需要时再揭晓。';$('#anchor-title').scrollIntoView({block:'start'});}
else{$('#retry').hidden=false;$('#remembered').hidden=false;$('#review-status').textContent='回听核对后，按自己的真实表现记录。';}
}
function review(success){if(!current)return;const prev=reviews[current.id],oldStep=Number.isInteger(prev?.step)&&prev.step>=0&&prev.step<=3?prev.step:0;const step=success?Math.min(3,oldStep+1):0;const days=success?[1,1,3,7][step]:0;
reviews[current.id]={step,due:success?Date.now()+days*DAY:Date.now(),last:Date.now()};persist();updateProgress();$('#review-status').textContent=success?`已安排${days}天后再次回忆。换个情境也试一试。`:'已放回待练清单。先听法语，再借图自己说。';$('#remembered').hidden=true;$('#retry').hidden=true;}
function renderQuiz(){const target=$('#quizzes');target.replaceChildren();$('#quiz-score').textContent='';for(const [i,q]of current.quiz.entries()){const f=node('fieldset');f.append(node('legend',`${i+1}. ${q.prompt}`));for(const [j,c]of q.choices.entries()){const label=node('label'),input=node('input');input.type='radio';input.name='q'+i;input.value=j;input.onchange=()=>{target.querySelectorAll('.quiz-feedback').forEach(n=>n.remove());$('#quiz-score').textContent='选择已更新，请重新检查答案。';};label.append(input,node('span',c));f.append(label);}target.append(f);}}
function checkQuiz(){if(!current)return;$('#quizzes').querySelectorAll('.quiz-feedback').forEach(n=>n.remove());let right=0;current.quiz.forEach((q,i)=>{const selected=$(`#quizzes input[name="q${i}"]:checked`),ok=selected&&Number(selected.value)===q.answer;if(ok)right++;const p=node('p',(selected?(ok?'答对了。':'再想一想。'):'还没有选择。')+q.reason,'quiz-feedback'+(ok?'':' wrong'));$('#quizzes').children[i].append(p);});$('#quiz-score').textContent=`${right} / ${current.quiz.length}题正确。说出理由，再做情景输出；选择题得分不代表语言等级。`;}
function renderLesson(){
const l=current,a=l.anchor;recalling=false;$('#breadcrumb').textContent=l.book_title+' / '+l.id;$('#lesson-meta').textContent=l.id+' · '+l.level+' · 约'+l.minutes+'分钟 · '+l.source_title;$('#lesson-title').textContent=l.title;$('#goal').textContent=l.goal;
$('#readiness').textContent=l.prerequisite_note||'';
for(const n of document.querySelectorAll('.study-support'))n.hidden=false;
paragraphs($('#explanation'),l.explanation);list($('#teaching-points'),l.teaching_points);$('#analogy').textContent=l.analogy;
const img=$('#anchor-image');$('#image-status').hidden=true;img.onerror=()=>{$('#image-status').hidden=false;};img.onload=()=>{$('#image-status').hidden=true;};
if(a.illustration){img.hidden=false;img.src=a.illustration.src;img.alt=a.illustration.alt;img.width=a.illustration.width;img.height=a.illustration.height;}else{img.removeAttribute('src');img.hidden=true;$('#image-status').hidden=false;}
$('#anchor-fr').textContent=a.fr;$('#anchor-zh').textContent=a.zh;$('#sound').textContent=a.sound;$('#movie').textContent=a.movie;$('#pronunciation').textContent=a.pronunciation;
$('#words').replaceChildren();for(const word of a.fr.match(/[A-Za-zÀ-ÖØ-öø-ÿŒœÆæ]+(?:[’'’-][A-Za-zÀ-ÖØ-öø-ÿŒœÆæ]+)*/g)||[]){const b=node('button',word,'word');b.type='button';b.lang='fr';b.setAttribute('aria-label','听词 '+word);b.onclick=()=>speak(word,.75);$('#words').append(b);}
$('#answer-content').hidden=false;$('#recall-instruction').hidden=true;$('#recall').hidden=false;$('#reveal').hidden=true;$('#retry').hidden=true;$('#remembered').hidden=true;$('#review-status').textContent='';
renderQuiz();$('#application').textContent=l.application;list($('#self-check'),l.self_check);$('#sources').replaceChildren();
for(const s of l.sources){const label=data.source_names[s.book]||s.book;$('#sources').append(node('li',label+'：'+s.label+'。本机定位 '+s.book+'/'+s.location+'；'+(/ocr/i.test(s.review_status||'')?'OCR来源，精确内容需回看页图。':'按原书章节读取，音标与图表仍需核对。')));}
$('#teacher-notes').replaceChildren();if(l.teacher_notes)$('#teacher-notes').append(node('h3','配套教师资料辅助'),node('p',l.teacher_notes));
$('#mark').textContent=done.has(l.id)?'已学 · 点击取消':'标记学过';const siblings=lessons.filter(x=>x.book===l.book),i=siblings.findIndex(x=>x.id===l.id);$('#position').textContent=`本册 ${i+1} / ${siblings.length} 课`;
$('#previous').disabled=i===0;$('#next').disabled=i===siblings.length-1;$('#previous').onclick=()=>go(siblings[i-1].id);$('#next').onclick=()=>go(siblings[i+1].id);refreshVoices();
}
function route(){stop();let id='';try{id=decodeURIComponent(location.hash.slice(1));}catch(e){}current=byId.get(id)||null;$('#dashboard').hidden=!!current;$('#lesson').hidden=!current;if(current){last=current.id;persist();renderLesson();$('#lesson-title').focus();}else catalogue();updateProgress();window.scrollTo(0,0);}
for(const [i,b]of books.entries()){
const children=lessons.filter(l=>l.book===b.id),card=node('button',undefined,'book-card');card.type='button';card.append(node('span',String(i+1).padStart(2,'0'),'book-number'),node('h3',b.title),node('p',b.subtitle),node('span',`${b.level} · ${children.length}课 ↗`,'small'));card.onclick=()=>{filterBook=b.id;$('#book-filter').value=b.id;catalogue();$('#search').scrollIntoView({block:'center'});};$('#book-grid').append(card);
const o=node('option',b.title);o.value=b.id;$('#book-filter').append(o);
}
$('#back').onclick=()=>go();$('#continue').onclick=()=>go(last||lessons[0].id);
$('#search').oninput=e=>{search=e.target.value;catalogue();};$('#book-filter').onchange=e=>{filterBook=e.target.value;catalogue();};$('#status-filter').onchange=e=>{filterStatus=e.target.value;catalogue();};
$('#due-filter').onclick=()=>{filterStatus='due';filterBook='all';search='';$('#search').value='';$('#status-filter').value='due';$('#book-filter').value='all';catalogue();$('#search').scrollIntoView({block:'center'});};
$('#reset').onclick=()=>{filterBook='all';filterStatus='all';search='';$('#book-filter').value='all';$('#status-filter').value='all';$('#search').value='';catalogue();};
$('#listen').onclick=()=>speak(current.anchor.fr);$('#slow').onclick=()=>speak(current.anchor.fr,.65);$('#chunks').onclick=echo;$('#stop').onclick=stop;
$('#recall').onclick=()=>recall(true);$('#reveal').onclick=()=>recall(false);$('#retry').onclick=()=>review(false);$('#remembered').onclick=()=>review(true);$('#check-answers').onclick=checkQuiz;
$('#mark').onclick=()=>{if(done.has(current.id))done.delete(current.id);else done.add(current.id);persist();$('#mark').textContent=done.has(current.id)?'已学 · 点击取消':'标记学过';updateProgress();announce('学习标记已更新。');};
$('#rate').value=rate;$('#rate-value').textContent=rate.toFixed(2)+'×';$('#rate').oninput=e=>{rate=Number(e.target.value);$('#rate-value').textContent=rate.toFixed(2)+'×';persist();};$('#voice').onchange=e=>{stop();voiceURI=e.target.value;persist();};
$('#download').onclick=()=>{const url=URL.createObjectURL(new Blob([current.markdown],{type:'text/markdown;charset=utf-8'})),a=node('a');a.href=url;a.download=current.id+'.md';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);};
window.addEventListener('hashchange',route);window.addEventListener('pagehide',stop);try{window.speechSynthesis?.addEventListener('voiceschanged',refreshVoices);}catch(e){}refreshVoices();route();
})();
