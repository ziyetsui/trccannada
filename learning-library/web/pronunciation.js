/* Offline pronunciation tutor. Each example is backed by explicit lesson data. */
'use strict';
window.createPronunciationExample = function(example, index, api) {
 const {el,button,stop,speak,sequence,available}=api, p=example.pronunciation;
 const card=el('section',undefined,'pronunciation-card');
 card.setAttribute('aria-label',`例句 ${index} 分步学习`);
 let stage=0, selected=0, repeats=3, reveal=false;
 const stages=['意思与图解','为什么这样读','逐词慢读','一点点连起来','自己说一次'];
 const head=el('div',undefined,'pronunciation-head');
 const intro=el('div');intro.append(el('span',`例句 ${index} · 五步学会一句`,'tiny-label'));
 const french=el('p',example.fr,'example-fr');french.lang='fr';intro.append(french,el('p',example.zh,'example-zh'));
 const audio=(label,text,rate,node)=>{const b=button(label,()=>speak(text,node||b,rate),'quiet');b.dataset.speak=text;b.disabled=!available();return b;};
 const linkLegend=el('p','‿ 联诵（补出辅音） · ⌒ 连读（原有辅音） · ⋯ 可选联诵 · × 不联诵；点击标记看原因并听两词。','connection-legend');
 const linkDetail=el('div',undefined,'inline-connection-detail');linkDetail.hidden=true;linkDetail.setAttribute('aria-live','polite');
 let offset=0,marked=0;french.replaceChildren();
 for(const note of p.links){
  const blocked=/不联诵|无联诵|无 \/z\/ 联诵|禁止联诵|阻止联诵|保持词尾无声|词尾不读/.test(note.label);
  const optional=/可选联诵|常见.*联诵/.test(note.label);
  const kind=blocked?'blocked':optional?'optional':/^连读/.test(note.label)?'flow':/^联诵|数字的连接形式/.test(note.label)?'liaison':null;
  if(!kind||!Number.isInteger(note.after))continue;
  const symbol={blocked:'×',optional:'⋯',flow:'⌒',liaison:'‿'}[kind],sound=note.label.match(/\/([^/]+)\//)?.[1];
  french.append(document.createTextNode(example.fr.slice(offset,note.after)));
  const mark=button('',()=>{stop();linkDetail.replaceChildren(el('strong',`${note.fr} · ${note.label}`),el('p',note.reason));linkDetail.hidden=false;if(available())speak(note.fr.replace(' → ',' '),mark,.7);},`connection-mark connection-${kind}`);
  mark.title=`${note.fr}：${note.label}`;mark.setAttribute('aria-label',`${note.fr}：${note.label}，查看原因并慢读`);
  mark.append(el('span',symbol),el('small',blocked?'不连':sound|| (optional?'可选':'连接')));
  french.append(mark);offset=note.after;marked++;
 }
 french.append(document.createTextNode(example.fr.slice(offset)));
 linkLegend.prepend(el('strong','连读标记：'));
 if(!marked)linkLegend.append(el('span','本句未标出特殊联诵或辅音连读，按意义组平顺读即可。','connection-empty'));
 intro.append(linkLegend,linkDetail);
 head.append(intro,audio('▶ 听完整句',example.fr));card.append(head);
 const nav=el('div',undefined,'pronunciation-tabs');nav.setAttribute('aria-label',`例句 ${index} 的学习步骤`);
 const body=el('div',undefined,'pronunciation-body');
 const tabs=stages.map((label,i)=>{const b=button(`${i+1} ${label}`,()=>{stop();stage=i;render();},'pronunciation-tab');nav.append(b);return b;});
 card.append(nav,body);
 function portrait(group,word){
  const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox','0 0 120 84');svg.setAttribute('role','img');
  const title=document.createElementNS(ns,'title');title.textContent=`${word.fr}：${word.zh} 的记忆图`;svg.append(title);
  const add=(tag,attrs)=>{const n=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);svg.append(n);return n;};
  const path=d=>add('path',{d,fill:'none',stroke:'currentColor','stroke-width':2.4,'stroke-linecap':'round','stroke-linejoin':'round'});
  const circle=(x,y,r)=>add('circle',{cx:x,cy:y,r,fill:'none',stroke:'currentColor','stroke-width':2.4});
  const text=(s,x=60,y=50,size=18)=>{const n=add('text',{x,y,'text-anchor':'middle',fill:'currentColor','font-size':size,'font-family':'sans-serif'});n.textContent=s;};
  const human=(x=48)=>{circle(x,24,9);path(`M${x} 34v26m-15-12 15-10 15 10m-15 12-10 14m10-14 10 14`);};
  const arrow=(x=15,y=44)=>path(`M${x} ${y}h32m-9-8 9 8-9 8`);
  const house=()=>path('M22 40 60 12l38 28M30 36v38h60V36M53 74V50h15v24');
  const clock=()=>{circle(60,42,28);path('M60 23v20l17 10');};
  const book=()=>path('M60 25Q40 12 20 20v48q20-8 40 5 20-13 40-5V20Q80 12 60 25v48');
  const balloon=()=>path('M18 16h84v43H62L43 74V59H18z');
  const forms={
   person:()=>human(60),people:()=>{human(40);human(83);},self:()=>{human(75);arrow(12,34);},wave:()=>{human(40);path('M55 47l20-26m8-8q17 8 0 17');},
   point:()=>{circle(83,42,18);arrow(16);},own:()=>{human(32);path('M67 44h34v28H67zM32 42h28m-6-6 6 6-6 6');},
   have:()=>{human(32);path('M62 40h39v30H62zM22 49q38 24 70 0');},give:()=>{human(24);human(96);arrow(44);},
   together:()=>{human(32);human(88);path('M46 47h28');},at:()=>{house();circle(60,43,8);path('M60 51v12');},
   inside:()=>{path('M24 16h72v60H24z');circle(60,46,12);},on:()=>{path('M20 59h80');circle(60,44,14);},
   of:()=>{book();arrow(62,42);},for:()=>{human(90);arrow(15);},link:()=>{circle(40,42,19);circle(76,42,19);},
   equal:()=>path('M30 32h60M30 51h60'),contrast:()=>{path('M60 13v62M25 36l10-15 10 15z');circle(85,48,16);},
   go:()=>{human(34);arrow(62,44);},home:()=>{house();arrow(2,50);},road:()=>path('M35 74 49 14M85 74 71 14M60 20v10m0 9v10m0 9v10'),
   calendar:()=>{path('M25 18h70v58H25zM25 33h70M42 10v17m36-17v17');text('15',60,62,22);},clock,repeat:()=>{path('M31 26a28 28 0 1 1-2 32M31 12v16H15');},
   next:()=>{arrow(18);arrow(64);},start:()=>{path('M30 72V14l49 16-49 17');},finish:()=>{path('M24 70V14h66v28H24M35 14v28m12-28v28m12-28v28m12-28v28M24 28h66');},
   number:()=>{circle(60,42,30);text(word.fr==='quinze'?'15':word.fr==='seize'?'16':word.fr==='deux'?'2':word.fr==='trois'?'3':word.fr==='huit'?'8':word.fr==='six'?'6':word.fr==='douze'?'12':word.fr==='quatorze'?'14':'123',60,51,23);},
   one:()=>{circle(60,42,25);text('1',60,51,25);},quantity:()=>{circle(34,30,10);circle(64,30,10);circle(94,30,10);circle(49,60,10);circle(79,60,10);},
   all:()=>{path('M15 14h90v62H15z');circle(38,40,9);circle(62,40,9);circle(86,40,9);},more:()=>{path('M25 60h70M60 70V15m-9 10 9-10 9 10');},part:()=>{path('M24 18h72v52H24zM48 18v52m24-52v52');},
   water:()=>{path('M60 10Q18 57 46 72q14 10 28 0Q102 57 60 10z');},cup:()=>{path('M30 30h48v33q-24 22-48 0zM78 35h15q15 22-15 23M24 76h68M42 10q-8 8 0 15m19-15q-8 8 0 15');},
   bread:()=>{path('M20 45q0-28 40-28t40 28v24H20zM36 30l8 12m13-15 8 12m13-9 8 12');},milk:()=>{path('M43 12h34v12l10 12v38H33V36l10-12zM33 36h54');text('LAIT',60,60,12);},
   wine:()=>{path('M39 13h42v25q-21 25-42 0zM60 53v21M43 74h34M40 31h40');},bowl:()=>{path('M20 35h80q-5 40-40 40T20 35zM16 35h88');},food:()=>{circle(60,43,29);circle(60,43,20);path('M15 17v53M8 17v16h14V17m85 0v53');},
   egg:()=>path('M60 12C42 12 25 53 37 68q23 18 46 0C95 53 78 12 60 12z'),fish:()=>{path('M20 42q35-40 68 0-33 40-68 0zM88 42l23-19v38z');circle(38,38,2);},
   cat:()=>{path('M36 29V10l18 16h14l18-16v19q16 37-26 40Q18 66 36 29zM54 48h12l-6 6zM21 41l25 4m-25 9 25-3m29-6 25-4m-25 10 25 3');},
   paw:()=>{circle(38,25,9);circle(60,19,9);circle(82,25,9);path('M60 39q-33 5-23 28 12 13 23 2 11 11 23-2 10-23-23-28z');},giraffe:()=>{path('M46 74V28l-9-8 5-10 15 9h22l9 13-24 9v33M51 19V8m18 12V8');circle(72,29,2);path('M49 44h13m-13 15h13');},
   house,tree:()=>{path('M60 75V46M35 50q-23-19 1-30 0-22 25-10 25-12 24 10 25 12 0 30z');},mountain:()=>path('M12 73 46 14l24 40 14-24 24 43zM34 35l12 5 10-8'),
   book,letter:()=>{path('M18 19h84v53H18zM18 19l42 29 42-29');},write:()=>{path('M25 63l5-18 45-35 13 14-45 36zM30 45l13 15M23 75h74');},
   phone:()=>{path('M45 12h35v62H45zM54 19h17M54 64h17M34 23q-17 20 0 39m57-39q17 20 0 39');},record:()=>{path('M48 15q12-12 24 0v32q-12 15-24 0zM36 37q0 29 24 29t24-29M60 66v12');},
   voice:()=>{human(30);path('M57 22q18 10 0 20m12-28q32 18 0 36m13-44q46 26 0 52');},ear:()=>{path('M36 38q-7-34 26-28 29 7 10 33-12 9-12 24-12 18-21-3M47 30q13-22 22-3L54 48');},
   eye:()=>{path('M14 43q46-50 92 0-46 50-92 0z');circle(60,43,16);},question:()=>{balloon();text('?',60,49,32);},name:()=>{human(28);path('M57 22h49v35H57z');text(word.fr.includes('appelle')?'Lina':'nom',81,44,13);},
   mind:()=>{path('M42 70V55q-20-40 17-44 32-1 25 31l11 12H80v16M50 30q9-18 20 0-6 17-15 0');},light:()=>{circle(60,32,21);path('M48 51v15h24V51M49 73h22M25 30H13m94 0H95M36 9l-8-8m56 8 8-8');},
   star:()=>path('M60 10 70 31l24 3-18 17 5 24-21-12-21 12 5-24-18-17 24-3z'),spark:()=>path('M60 9v66M27 42h66M37 19l46 46M37 65l46-46'),
   check:()=>{circle(60,42,30);path('M41 41l13 14 26-28');},good:()=>{circle(60,42,29);circle(50,34,2);circle(70,34,2);path('M43 48q17 22 34 0');},
   no:()=>{circle(60,42,29);path('M39 21l42 42');},choice:()=>{path('M60 75V43L33 17m27 26 27-26M22 17h16v16m44 0V17h16');},compare:()=>{path('M60 15v60M27 28h66M37 28 21 56h32zM85 28 69 56h32z');},
   bag:()=>{path('M28 31h64v43H28zM44 31V16q16-15 32 0v15');},coat:()=>path('M42 12 24 23 10 45l15 10 14-18v38h42V37l14 18 15-10-14-22-18-11-18 17z'),
   foot:()=>path('M57 12h25v34q5 13 18 16 18 16-10 16H29q-9-12 12-20l16-7z'),window:()=>{path('M25 12h70v62H25zM60 12v62M25 42h70');},
   close:()=>{path('M40 12h40v62H40z');circle(69,45,2);arrow(5);},train:()=>{path('M35 10h50v52H35zM42 20h36v21H42zM43 62l-14 16m48-16 14 16M35 72h50');circle(46,51,3);circle(74,51,3);},
   car:()=>{path('M20 48l12-25h55l13 25v18H20zM33 46h53');circle(36,66,8);circle(85,66,8);},boat:()=>path('M18 51h86L86 72H35zM59 51V10L29 43h30m6-33 30 33H65'),
   table:()=>path('M17 30h86v12H17zM28 42v32m64-32v32'),broken:()=>{path('M22 25h76v43H22zM58 25l-10 19 17-5-9 29M13 11l10 9m84-9-10 9');},
   moon:()=>path('M76 12a31 31 0 1 0 8 54 31 31 0 0 1-8-54z'),sun:()=>{circle(60,41,20);path('M60 7v9m0 50v10M25 41H15m80 0h10M35 16l7 8m36 35 7 8m0-51-7 8M42 59l-7 8');},
   wind:()=>path('M15 26h64q25 0 12-17M9 43h90q20 0 8 16M20 60h45q20 0 10 16'),cold:()=>{path('M60 10v64M31 24l58 36M31 60l58-36M50 14l10 9 10-9M50 70l10-9 10 9');},
   party:()=>{path('M25 70 40 29l45 29zM64 12l-5 14m21-9-5 12m21 5-14 6M34 10l6 8');circle(94,13,3);},money:()=>{circle(60,42,30);text('€',60,52,31);},
   big:()=>{path('M29 70V14h51v56M15 14v56m-5-6 5 6 5-6m-10-44 5-6 5 6');},small:()=>{path('M43 47h30v23H43M32 47v23m-4-5 4 5 4-5');},long:()=>{path('M17 42h86M17 30v24m86-24v24M25 37l-8 5 8 5m70-10 8 5-8 5');},
   color:()=>{circle(60,42,28);path('M33 38h54M37 54h46M44 24h32');text(word.fr==='blanc'?'白':'棕',60,48,13);},slow:()=>{path('M20 60h79M33 55q-7-36 23-33 25 3 19 33M75 52l12-12 12 13');circle(55,42,12);},
   near:()=>{house();human(13);},meet:()=>{human(30);human(88);path('M46 44h27m-6-6 6 6-6 6');},reply:()=>{balloon();path('M85 35H37l11-10m-11 10 11 10');},
   organize:()=>{path('M60 11v23M25 53V34h70v19M15 53h20v21H15m35-21h20v21H50m35-21h20v21H85');},chart:()=>{path('M22 12v61h79M37 64V45h12v19m10 0V30h12v34m10 0V17h12v47');},
   plan:()=>{path('M26 12h68v62H26M36 29h12m9 0h26M36 45h12m9 0h26M36 61h12m9 0h26');},change:()=>{arrow(17,28);path('M100 57H65l9-8m-9 8 9 8');},stay:()=>{human(60);path('M27 78h66');},
   full:()=>{path('M25 17h70v58H25zM25 31h70M35 41h50m-50 12h50m-50 12h50');},sleep:()=>{human(35);text('z',75,30);text('Z',93,17);},
   fear:()=>{circle(60,42,28);circle(49,34,3);circle(72,34,3);circle(60,55,7);},hurt:()=>{human(40);path('M82 23v32m-16-16h32');},
   hero:()=>{human(60);path('M46 36 25 65l35-6 35 6-21-29');},care:()=>{path('M60 12 96 72H24z');text('!',60,62,28);},
   calm:()=>{path('M18 32q15-10 30 0t30 0 30 0M18 52q15-10 30 0t30 0 30 0');},
   help:()=>{human(30);human(90);path('M44 47h32m-16-16v32');},please:()=>{human(40);path('M53 44l17-16 17 16m-17-16v32');},thanks:()=>{path('M60 72 23 38q-10-33 20-26 12 2 17 16 5-14 17-16 30-7 20 26z');},
   can:()=>{circle(60,42,28);path('M43 43l12 12 23-26');},need:()=>{human(30);circle(88,42,20);text('!',88,49,24);},want:()=>{human(30);arrow(52);circle(98,42,10);},take:()=>{path('M20 60h60l20-20M45 59V28h30v31M28 60l-9-27 9-3 12 25');},
   play:()=>{circle(60,42,28);path('M52 25v34l25-17z');},action:()=>{human(40);arrow(65);},show:()=>{human(25);path('M57 17h48v48H57M81 65v13');},work:()=>{path('M25 32h70v41H25zM46 32V15h28v17M25 47h70');}
  };
  if(!forms[group])throw new Error(`Missing illustration: ${group}`);
  forms[group]();return svg;
 }
 function wordCard(w,i,showImage=true){
  const item=el('div',undefined,'word-card'+(selected===i?' selected':''));
  const choose=button('',()=>{selected=i;showWord();body.querySelectorAll('.word-card').forEach((n,j)=>n.classList.toggle('selected',j===i));if(available())speak(w.fr,choose,.65);},'word-select');
  choose.setAttribute('aria-label',`${w.fr}：${w.zh}，查看解释并慢读`);
  if(showImage)choose.append(portrait(w.picture,w));
  const label=el('strong',w.fr);label.lang='fr';choose.append(label,el('span',w.zh,'word-meaning'),el('span',`/${w.ipa}/`,'word-ipa'));
  item.append(choose,audio('▶ 单词慢读',w.fr,.65));return item;
 }
 let wordInfo;
 function showWord(){
  if(!wordInfo)return;const w=p.words[selected];wordInfo.replaceChildren();
  wordInfo.append(el('h3',`${w.fr} · /${w.ipa}/`),el('p',`这句话里的意思：${w.zh}`),el('p',w.reason));
  const mouth=el('div',undefined,'mouth-tips');
  const tips=[['y','/y/：舌头靠前，先摆 /i/ 的舌位再圆唇；不要变成 /u/。'],['u','/u/：嘴唇圆，舌头靠后；与 tu 的 /y/ 区别开。'],['ɛ̃','/ɛ̃/：元音带鼻化，气流可经鼻腔；末尾不另加响亮的 n。'],['ɑ̃','/ɑ̃/：保持开放元音的鼻化；别在尾巴上再拼一个 n。'],['ɔ̃','/ɔ̃/：圆唇并带鼻化；不要先发 /o/ 再补一个 n。'],['œ̃','/œ̃/：圆唇、较开放且鼻化；部分口音与 /ɛ̃/ 合并。'],['œ','/œ/：圆唇、开口比 /ø/ 大一些，像 peur 的元音。'],['ø','/ø/：圆唇、开口较小，像 peu 的元音。'],['ʁ','/ʁ/：轻轻使用口腔后部气流，不用力刮嗓子。'],['ʒ','/ʒ/：让气流持续摩擦，声带振动；别加英语 j 开头的闭塞。'],['ʃ','/ʃ/：持续送出“嘘”似的气流，喉部不必振动。'],['ɲ','/ɲ/：舌面贴近硬腭，气流从鼻腔通过；gn 不拆成两个辅音。'],['ɥ','/ɥ/：从前圆唇口形快速滑向后面的元音，不额外增加音节。'],['wa','/wa/：快速从圆唇口形滑到 /a/，oi 不拆成 o、i 两个音。'],['ə','/ə/：轻轻发弱 e；先保留练清楚，再观察自然语流中是否省去。'],['ɛ','/ɛ/：舌头靠前，开口比 /e/ 更大，元音保持稳定。'],['e','/e/：舌头靠前，开口较小；别拖成英语式双元音。'],['i','/i/：舌位靠前且高，嘴唇不必圆起。']];
  let count=0;for(const [symbol,tip]of tips){const relevant=['ɛ','œ','e','i','u','y','ø'].includes(symbol)?w.ipa.replace(/[ɛœɔɑae]̃/g,'').includes(symbol):w.ipa.includes(symbol);if(relevant&&count<3){mouth.append(el('p',tip));count++;}}
  if(count)wordInfo.append(el('h4','嘴巴怎么做'),mouth);
  if(['plus','six','est','un'].includes(w.fr.toLowerCase()))wordInfo.append(el('p','单词独读和句中词尾可能不同。先看这里的标注，再点短语核对；设备合成声音可能采用另一种读法。','small muted'));
 }
 function playSteps(steps,control){sequence(steps.flatMap(s=>Array.from({length:repeats},()=>({...s}))),control);}
 function controls(){
  const row=el('div',undefined,'tutor-controls'),label=el('label','每项重复 '),select=el('select');select.setAttribute('aria-label',`例句 ${index} 每项重复次数`);
  for(const n of [1,2,3,5]){const o=el('option',`${n} 遍`);o.value=n;o.selected=n===repeats;select.append(o);}select.onchange=()=>{stop();repeats=Number(select.value);};label.append(select);row.append(label,button('■ 停止',stop,'quiet'));return row;
 }
 function render(){
  wordInfo=null;body.replaceChildren();tabs.forEach((t,i)=>t.setAttribute('aria-pressed',String(i===stage)));
  linkLegend.hidden=stage===4;linkDetail.hidden=true;
  if(stage===0||stage===1||stage===2){
   body.append(el('h3',stage===0?'先看懂，再听懂':stage===1?'把拼写、声音和口形对应起来':'一个词一个词，留出跟读的空隙'));
   body.append(el('p',stage===0?'点每张词卡：看它在这句话里的意思，有声音时也会慢读。图画是记忆提示，短语意思请看下面。':stage===1?'点一个词看具体原因。/ / 里面是声音符号，不用先背整张音标表，也不要照汉字谐音读。':'每个单词都可单独点击；连续练习会逐词慢读，每遍之后留 1.4 秒给你跟读。','small muted'));
   if(stage===2){body.append(controls());const run=button('▶ 逐词跟读',()=>playSteps(p.words.map((w,i)=>({text:w.fr,rate:.65,gap:1400,node:body.querySelectorAll('.word-select')[i]})),run),'primary');run.dataset.speak='words';run.disabled=!available();body.append(run);}
   const grid=el('div',undefined,'word-grid');p.words.forEach((w,i)=>grid.append(wordCard(w,i,stage===0)));body.append(grid);
   wordInfo=el('div',undefined,'word-detail');wordInfo.setAttribute('aria-live','polite');body.append(wordInfo);showWord();
   if(stage===0){const meanings=el('div',undefined,'phrase-meanings');meanings.append(el('h3','合起来是什么意思'));for(const c of p.chunks){const row=el('p');row.append(el('strong',c.fr+' '),document.createTextNode(c.zh));meanings.append(row);}meanings.append(el('p','整句：'+example.zh,'sentence-translation'));body.append(meanings);}
  }else if(stage===3){
   body.append(el('h3','从小组到整句，慢慢搭起来'),el('p','① 单独听小组 → ② 逐渐扩展 → ③ 听完整句。分段用于练习，最后要回到整句的自然节奏。下划线 ‿ 表示声音连接，不是额外的一个词。','small muted'),controls());
   const rows=el('div',undefined,'chunk-list');for(const [i,c]of p.chunks.entries()){const row=el('div',undefined,'chunk-row'),copy=el('div');copy.append(el('strong',`${i+1}. ${c.fr}`),el('p',c.zh,'small'));row.append(copy,audio('▶ 听这组',c.fr,.7));rows.append(row);}body.append(rows);
   const joined=el('div',undefined,'join-ladder');joined.append(el('h4','逐渐扩展'));for(let i=0;i<p.chunks.length;i++){const fr=p.chunks.slice(0,i+1).map(c=>c.fr).join(' '),row=el('div',undefined,'chunk-row');row.append(el('span',fr),audio('▶ 连起来',fr,.75));joined.append(row);}body.append(joined);
   const run=button('▶ 自动分组 → 扩展 → 整句',()=>{const steps=p.chunks.map(c=>({text:c.fr,rate:.7,gap:1500}));for(let i=1;i<p.chunks.length;i++)steps.push({text:p.chunks.slice(0,i+1).map(c=>c.fr).join(' '),rate:.75,gap:2000});steps.push({text:example.fr,rate:1,gap:2500});playSteps(steps,run);},'primary');run.dataset.speak='chunks';run.disabled=!available();body.append(run);
   const notes=el('div',undefined,'connection-notes');notes.append(el('h3','这里的声音怎样接起来'));
   if(!p.links.length)notes.append(el('p','这句没有另外标注要添加的联诵辅音。按上面的词音和意义小组平顺读出；不要看到相邻词就主动加 /z/ 或 /t/。'));
   for(const note of p.links){notes.append(el('h4',`${note.fr} · ${note.label}`),el('p',note.reason),audio('▶ 只听这个连接',note.fr.replace(' → ',' '),.7));}
   if(/[,;:«»?!]/.test(example.fr))notes.append(el('p','逗号、列举或引用处可以留小边界。练习分段不等于正常说话要在每个词后停下；有真正停顿时不跨停顿联诵。'));
   body.append(notes,audio('▶ 正常速度核对整句',example.fr,1));
  }else{
   body.append(el('h3','现在，轮到你说'),el('p','先听一遍 → 隐藏法语 → 根据中文或图画自己说 → 显示原句并核对。播放完成不代表已经学会，能独立说出来后再标记本课已学。'));
   body.append(audio('▶ 先听一次',example.fr,.85));
   const prompt=el('div',undefined,'recall-prompt');prompt.append(portrait(p.words.find(w=>!['point','of','at'].includes(w.picture))?.picture||p.words[0].picture,p.words.find(w=>!['point','of','at'].includes(w.picture))||p.words[0]),el('p',example.zh));
   body.append(prompt);french.hidden=!reveal;head.querySelector('.example-zh').hidden=false;
   const answer=el('div',undefined,'recall-answer');answer.hidden=!reveal;answer.append(el('p',example.fr,'example-fr'),el('p',p.chunks.map(c=>c.fr).join(' / '),'small'));
   const toggle=button(reveal?'隐藏法语，自己说':'显示法语，核对一下',()=>{stop();reveal=!reveal;answer.hidden=!reveal;french.hidden=!reveal;toggle.textContent=reveal?'隐藏法语，自己说':'显示法语，核对一下';},'primary');body.append(toggle,answer,audio('▶ 再听整句核对',example.fr,1));
   const checklist=el('div',undefined,'recall-checks');for(const text of ['我知道每个小组在说什么','我能说清这课的关键声音','我能把小组连成整句']){const label=el('label'),input=el('input');input.type='checkbox';label.append(input,document.createTextNode(text));checklist.append(label);}body.append(checklist,el('p','今天练会后，明天先不看法语再说一次；卡住就只回听卡住的那个词。','small muted'));
  }
  if(stage!==4)french.hidden=false;
  const foot=el('div',undefined,'tutor-footer');
  if(stage<4)foot.append(button(`下一步：${stages[stage+1]} →`,()=>{stop();stage++;render();},'text-button'));
  if(stage>0)foot.prepend(button('← 上一步',()=>{stop();stage--;render();},'text-button'));
  body.append(foot);
 }
 render();return card;
};
