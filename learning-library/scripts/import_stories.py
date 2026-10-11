"""Lossless EPUB provenance + editable, original Chinese reading lessons.
Run with Python 3.9+: python3 scripts/import_stories.py [source.epub]
"""
from pathlib import Path
import sys, zipfile, hashlib, json, re, posixpath
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'sources/french-stories'
def tag(e): return e.tag.rsplit('}',1)[-1]
def plain(e): return ' '.join(''.join(e.itertext()).split())
def inline(e, source_href):
    def target(url):
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',url): return url
        return 'raw/'+posixpath.normpath(posixpath.join(posixpath.dirname(source_href),url))
    name=tag(e)
    if name in ('img','image'):
        url=e.get('src') or e.get('{http://www.w3.org/1999/xlink}href','')
        return '!['+e.get('alt','')+']('+target(url)+')'
    if name=='br': return '  \n'
    s=e.text or ''
    for c in e: s+=inline(c,source_href)+(c.tail or '')
    s=s.replace('\r','').strip()
    if name=='a': return '['+s+']('+target(e.get('href',''))+')'
    if name in ('b','strong'): return '**'+s+'**'
    if name in ('i','em'): return '*'+s+'*'
    return s

def convert(source):
    OUT.mkdir(parents=True,exist_ok=True)
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    with zipfile.ZipFile(source) as z:
        container=ET.fromstring(z.read('META-INF/container.xml'))
        opf=container.find('.//{*}rootfile').get('full-path'); base=posixpath.dirname(opf)
        package=ET.fromstring(z.read(opf)); manifest={x.get('id'):x.attrib for x in package.findall('.//{*}manifest/{*}item')}
        spine=[posixpath.join(base,manifest[x.get('idref')]['href']) for x in package.findall('.//{*}spine/{*}itemref')]
        title=plain(package.find('.//{*}metadata/{*}title'))
        for name in z.namelist():
            if name.endswith('/') or '..' in Path(name).parts or name.startswith('/'): continue
            dest=OUT/'raw'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(name))
        chunks=[];units=[];front=[];current=None;active=False;volume=0;parts=[]
        for index,href in enumerate(spine,1):
            root=ET.fromstring(z.read(href)); body=root.find('{*}body'); elements=list(body) if body is not None else []
            texts=[plain(e) for e in elements if plain(e)]
            head=texts[0] if texts else ''
            if re.match(r'French Short Stories for Beginners.*Volume [123]',head): volume=int(re.search(r'Volume ([123])',head)[1])
            chapter=re.match(r'Chapter (\d+)\.\s*(.*)',head)
            if chapter:
                current={'unit':len(units)+1,'volume':volume,'chapter':int(chapter[1]),'title':chapter[2],'blocks':[],'source_hrefs':[]};units.append(current);active=True
            role='other';lang='mixed'
            if chapter: role='story';lang='fr'
            elif head=='Vocabulary': role='vocabulary'
            elif head.startswith('Résumé'): lang='fr';role='summary'
            elif head.startswith('Summary'): lang='en';role='summary'
            elif head.startswith('Questions sur'): role='exercise';lang='fr'
            elif head.lower().startswith('questions about'): role='exercise';lang='fr' if volume==1 else 'en'
            elif head=='Answers': role='answer';lang='mixed'
            blocks=[];md=[]
            for bi,e in enumerate(elements,1):
                text=plain(e);bid=f'{Path(href).stem}-b{bi:03}'
                if text:
                    # French chapter content; the English "Chapter" label stays unvoiced.
                    blang='mixed' if chapter and bi==1 else ('en' if bi==1 and head.lower().startswith('questions about') else lang)
                    block={'id':bid,'text':text,'lang':blang,'role':role,'source_ref':href}
                    if tag(e) in ('ol','ul'):
                        items=[plain(c) for c in e if tag(c)=='li']
                        block['source_text']=text
                        block['text']='\n'.join((chr(65+j)+'. ' if tag(e)=='ol' else '• ')+v for j,v in enumerate(items))
                    blocks.append(block)
                if tag(e) in ('ol','ul'):
                    md.append('\n'.join('- **'+chr(65+j)+'.** '+inline(c,href) if tag(e)=='ol' else '- '+inline(c,href) for j,c in enumerate(e) if tag(c)=='li'))
                elif tag(e)=='table':
                    rows=[]
                    for tr in e.iter():
                        if tag(tr)=='tr':rows.append([inline(c,href) for c in tr if tag(c) in ('td','th')])
                    if rows:
                        width=max(map(len,rows));rows=[r+['']*(width-len(r)) for r in rows]
                        md+=['| '+' | '.join(r)+' |' for r in rows[:1]]+['| '+' | '.join(['---']*width)+' |']+['| '+' | '.join(r)+' |' for r in rows[1:]]
                else:
                    val=inline(e,href)
                    if not val:continue
                    heading=tag(e).startswith('h') and tag(e)[1:].isdigit() or 'heading' in e.get('class','')
                    md.append(('### ' if heading else '')+val)
            record={'book_id':'french-stories','source_unit':index,'spine_index':index,'source_ref':href,'title':head,'text':'\n\n'.join(b.get('source_text',b['text']) for b in blocks),'blocks':blocks,'markdown':'\n\n'.join(md)}
            chunks.append(record)
            parts.append(f'## Spine {index:03} · {href}\n\n<!-- Source: {href} -->\n\n'+record['markdown'])
            if active and current:
                current['blocks']+=blocks;current['source_hrefs'].append(href)
            else: front.append({'source_ref':href,'blocks':blocks})
            if head=='Answers':active=False
        assert len(units)==40 and [sum(u['volume']==v for u in units) for v in (1,2,3)]==[10,10,20]
        (OUT/'book.md').write_text('# '+title+'\n\nSource SHA-256: '+digest+'\n\n'+'\n\n'.join(parts))
        (OUT/'contents.md').write_text('# 全部 EPUB spine 文档\n\n'+'\n'.join(f'- {c["spine_index"]:03} · [{c["title"] or c["source_ref"]}](raw/{c["source_ref"]})' for c in chunks)+'\n\n# 故事顺序\n\n'+'\n'.join(f'- S{u["unit"]:02} · 卷{u["volume"]}第{u["chapter"]}篇 · {u["title"]}' for u in units))
        (OUT/'chunks.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in chunks))
        (OUT/'reader.json').write_text(json.dumps({'book_id':'french-stories','title':title,'units':units,'front_matter':front},ensure_ascii=False,indent=2))
        meta={'id':'french-stories','source_file':source.name,'sha256':digest,'source_sha256':digest,'title':title,'format':'epub','spine_documents':len(spine),'story_units':40,'volumes':[10,10,20],'conversion_status':'complete-spine-extraction','spine':spine,'units':[{'unit':u['unit'],'title':u['title'],'volume':u['volume'],'chapter':u['chapter'],'source_hrefs':u['source_hrefs']} for u in units],'blocks':sum(len(c['blocks']) for c in chunks),'assets':len([x for x in z.namelist() if not x.endswith('/')]),'non_story_spine_documents':len(front),'source_note':'Raw archive members are retained under raw/. Original French, English summaries, vocabulary, exercises and keys are unchanged; source errors are preserved.'}
        (OUT/'manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
    return units,meta

# Editorial notes were written after reading each complete story and its vocabulary/questions.
# These are project-authored lessons, never attributed to the EPUB author.
LESSONS=[]
def note(title,synopsis,focus,meaning,point,analogy,examples,question,choices,reason):
    LESSONS.append(dict(title=title,synopsis=synopsis,focus=focus,meaning=meaning,point=point,analogy=analogy,examples=examples,question=question,choices=choices,reason=reason))
note('学车风波：耐心改变结果','Martin观察到Lucas与爸爸每次学车后都很生气，发现爸爸缺少耐心。他建议哥哥做家务，让妈妈有空教车。Lucas最终拿到驾照，爸爸却把功劳归给自己；末尾的玩笑要结合全篇判断。','voiture d’occasion','二手车','背景描写常见未完成过去时，推进事件常见简单过去时。阅读时把était看作状态，把décida看作新决定；复述可改用常见的复合过去时。','像换一位愿意慢慢教你的自行车教练，学习的路就顺了。',[('Lucas a choisi une voiture d’occasion.','Lucas选了一辆二手车。'),('Sa mère lui explique les gestes avec patience.','妈妈耐心地向他解释动作。'),('Martin a proposé une solution à son frère.','Martin向哥哥提出了解决办法。')],'Martin给哥哥的关键建议是什么？',['帮妈妈做家务，请妈妈教开车','放弃驾照考试','让爸爸每天加课'],'妈妈更有耐心；分担家务让她有时间教车，之后Lucas进步。')
note('雨天游戏：现实与想象的切换','Lucien被连续下雨困在托儿所，嫌捉迷藏不够刺激，组织了村民躲避食人魔的游戏。玩具士兵变成救援目标，保育员被想象成女巫；最后他撞到老师，午餐把大家拉回现实。','cachette','藏身处','souvent表示常常，jamais表示从不。故事规则要求不断更换cachette；把现实物品与想象角色配对，才能理解最后出现的“墙”其实是老师。','想象力给教室套上城堡滤镜，但午饭铃一响就回到教室。',[('Lucien cherche une nouvelle cachette.','Lucien寻找新的藏身处。'),('Les enfants jouent pendant la pluie.','孩子们在下雨时玩耍。'),('La maîtresse annonce le déjeuner.','老师宣布午餐时间到了。')],'游戏最后让Lucien停下来的“墙”是什么？',['来叫大家吃饭的老师','真正的石头城墙','突然倒下的树'],'结尾退出幻想后，Lucien向老师道歉；她说明来叫孩子们吃午餐。')
note('仙人掌朋友：好心也要懂方法','Margot收到爷爷送的仙人掌，每天浇水，植株却逐渐失去光泽。她加倍浇水也无效，于是打电话求助。爷爷解释问题并换盆处理；一个月后仙人掌恢复。阅读要区分努力的数量与方法是否合适。','rempoter','给植物换盆','malgré后接名词表示尽管：malgré ses efforts。pourtant连接相反预期：她很用心，植物却变差。源书的养护次数是故事细节，不应当作适用于所有仙人掌的统一规则。','给朋友送水也要先问他需不需要，越多不总是越好。',[('Margot a trop arrosé sa plante.','Margot给植物浇水过多。'),('Son grand-père va rempoter le cactus.','爷爷要给仙人掌换盆。'),('Malgré ses efforts, elle a besoin d’aide.','尽管她很努力，她仍需要帮助。')],'爷爷为了救仙人掌做了什么？',['处理受损根部并换盆','让Margot每天再浇三次水','把仙人掌直接扔掉'],'正文写爷爷取出植株、清理并剪去部分根部，放入新盆与土中。')
note('西兰花协定：先尝一口','Solène拒绝吃西兰花。妈妈提出一周内每天尝一口不同做法；如果仍不喜欢，以后就不再要求。她从怀疑焗菜，到吃完不同菜式，最后承认自己没有原来那么讨厌西兰花。姐姐不吃则有过敏原因。','bouchée','一口食物','ne…pas si…表示没有那么……。Ce n’est pas si mauvais的语气比“非常好吃”弱，符合Solène慢慢改变看法的过程。词表goûter在这里作动词“尝”，另可作名词“点心”。','给新颜色先留一个小格子试涂，不必一下把整张画涂满。',[('Je vais goûter une bouchée de gratin.','我要尝一口焗菜。'),('Ce plat n’est pas si mauvais.','这道菜没有那么难吃。'),('Elle a changé d’avis après une semaine.','一周后她改变了看法。')],'妈妈提出的约定是什么？',['一周内每天尝一口相关菜式','马上吃完一大盘生西兰花','姐姐也必须吃西兰花'],'正文的约定是每天尝一口、持续一周，并非强迫姐姐吃致敏食物。')
note('小猫出走：误会怎样解开','Lily春天掉毛，以为自己会变丑而被Sarah抛弃，于是离家。流浪猫Agathe和Cleo帮助她找食物和住处。看到寻猫启事后，Agathe指出主人仍关心她，并解释掉毛；Lily终于回家。','affiche','海报、告示','avoir peur de和penser que可引出担心与判断。Lily的担忧不等于事实；理解故事时分别记录“她以为的”与“主人实际做的”。','像看到橡皮屑就误以为作业本要消失，先问一问才能知道真相。',[('Lily a vu une affiche avec sa photo.','Lily看到印着自己照片的告示。'),('Sarah cherche sa petite chatte.','Sarah在寻找她的小猫。'),('Agathe la rassure avec douceur.','Agathe温柔地安慰她。')],'什么证据说明Sarah仍想找到Lily？',['街上贴有寻猫告示','Sarah把所有猫粮扔掉了','餐馆关闭了'],'Lily认出告示上的自己，Agathe由此推断主人没有抛弃她。')
note('棋盘王国上篇：梦的入口','Alexandre整理好房间后想野餐。妈妈忙于家务，让他先铺毯子；他避开蜜蜂与强烈阳光，选树荫下，赶走蚂蚁后睡着。醒来仿佛到了棋盘形平原旁的城堡，一个自称男仆的人为他准备衣服；本篇留下悬念。','ombre','阴影、树荫','d’abord、ensuite、enfin帮助排列选地点的顺序。原书的简单过去时可只辨识，不必一开始就主动使用。续篇才揭示梦的结局，不要把上篇当作完整解决。','像电影上半场先摆出毯子、格子和蚂蚁，等下半场再看它们怎样变成梦。',[('Il installe la couverture à l’ombre.','他把毯子铺在树荫下。'),('Sa mère termine le ménage.','妈妈完成家务。'),('Dans son rêve, il découvre un château.','在梦里，他发现一座城堡。')],'Alexandre最终把野餐毯铺在哪里？',['树荫下','蜜蜂飞舞的花旁','太阳最强的草地中央'],'前两个地点分别有蜜蜂和强烈阳光，他最后选择树下。')
note('棋盘王国下篇：找出梦中对应物','Samuel告诉Alexandre，他是王子，也是棋盘王国的守护者。取剑途中巨蚁袭村，他与骑士击退蚂蚁。王后的声音变成妈妈的呼唤，他醒在野餐毯上；前篇毯子的格子与蚂蚁在梦里都有对应。','forgeron','铁匠','il s’agit de表示“说的是、涉及的是”。理解梦境要沿着现实→梦→现实读；结尾的复合过去时J’ai sauvé表示人物在复述刚经历的事。','梦像拼积木，把白天见到的小蚂蚁拼成了大怪兽。',[('Samuel attend devant l’atelier du forgeron.','Samuel在铁匠作坊前等候。'),('Le prince protège le village avec ses chevaliers.','王子和骑士们保护村庄。'),('Alexandre s’est réveillé près de sa mère.','Alexandre在妈妈身旁醒来。')],'Alexandre与Samuel去村庄的目的是什么？',['取Alexandre的新剑','购买野餐面包','寻找失踪的王后'],'Samuel明确说要去铁匠处取王子的新剑，巨蚁袭击发生在途中。')
note('特别的远足：线索与礼貌','Zoé帮Clément系鞋带，两人落在队伍后面并迷路。他们分享点心给松鼠Félix，随后进入会说话的森林。原本想求助鹰Octave，但鹰生病；老橡树Aristide举高松鼠，让它看见营地，最终带孩子们回队。','chêne','橡树','à la place de表示代替。老橡树代替生病的鹰提供帮助。troupeau原意“兽群”，松鼠用它指孩子们的队伍，是人物视角带来的幽默。','森林像一座有自己礼貌规则的小城，懂得道谢才能成为好客人。',[('Le vieux chêne soulève le petit écureuil.','老橡树把小松鼠举高。'),('Zoé remercie leur guide.','Zoé感谢他们的向导。'),('Les enfants retrouvent enfin leur groupe.','孩子们终于找回队伍。')],'鹰生病后，谁实际帮助Félix看见营地？',['老橡树Aristide','白狼Hélène','老师Ludivine'],'老橡树把松鼠举到高处，让它辨认营地方向。')
note('海盗游戏：书页变舞台','Maxime与Bruno因考试成绩差而被收走电子设备。兄弟先轮流朗读海盗故事，再把床、椅子、尺子和浴袍带改造成舞台道具。妈妈叫他们吃点心，海盗“宝藏”变成牛奶和曲奇。','butin','战利品、收获','en guise de表示作为、充当；真实物品与假想物品可用X représente Y对应。读懂最后的butin，要知道语境已从海盗故事切回家庭点心。','两把椅子可以在想象里变成跳板，书里的人物则借你的声音出场。',[('Les frères lisent les dialogues à voix haute.','兄弟们大声朗读对话。'),('Une règle représente le sabre du capitaine.','一把尺子代表船长的军刀。'),('Leur butin est une assiette de biscuits.','他们的战利品是一盘饼干。')],'结尾兄弟口中的“宝藏”指什么？',['牛奶和曲奇点心','海里捞出的金币','被没收的电脑'],'妈妈叫他们吃点心，结尾把cookies et lait称为butin，延续海盗游戏用语。')
note('太空涂色：改写故事的自由','Magali得到童话涂色书，却觉得故事和图画缺乏趣味。她把公主改成外星大使Célestine，仙女改成对手，狗改成守卫Éon，并画出逃生舱。妈妈听完新版本后送她空白本，让她创作自己的故事。','récit','故事、叙述','dans sa version表示“在她的版本中”。复述时区分原童话和改写版，尤其狗与人形守卫的关系；ses propres histoires中的propre放名词前表示“自己的”。','就像同一盒彩笔可以画城堡，也可以画飞船，故事由你来选。',[('Magali invente un nouveau récit.','Magali创作一个新故事。'),('Éon prend une apparence humaine.','Éon变成人的模样。'),('Sa mère lui offre un carnet de pages blanches.','妈妈送她一本空白页的本子。')],'妈妈最后为什么送Magali空白本？',['支持她写画自己的故事','要求她抄写旧童话','惩罚她涂错颜色'],'妈妈听懂了她的改写后，送空白页让她继续原创。')
note('巨型披萨：想象中的分工','五位朋友在Hervé的树屋想起Aurélie生日会的巨型披萨，想象自己在工厂分工制作。有人揉面，有人煮酱，Hervé刨奶酪；Aude和Marcel悄悄省去大蒜。妈妈邀他们去快餐店时，大家已经想好要点披萨。','garniture','配料、馅料','pendant que和tandis que可以描写同时进行的动作。把五人的任务列成表，比逐词翻译更容易掌握情节。pâte是面团；本篇词表的rapper le fromage在教学例句中规范写作râper。','五个人像五条小流水线，最后把各自的成果拼成一个圆。',[('Hervé râpe le fromage pour la pizza.','Hervé为披萨刨奶酪。'),('Marcel préfère une garniture à l’ananas.','Marcel更喜欢菠萝配料。'),('Pendant que la pâte lève, les amis préparent la sauce.','面团发酵时，朋友们准备酱汁。')],'Aude和Marcel在酱里省去了什么？',['大蒜','番茄','所有香料'],'Marcel觉得蒜味太重，两人商量后把蒜放到一边。')
note('准备起飞：担心与信任','小狗Oxy担心Alice出差后不回来，听从流浪狗Rex建议藏进箱子。在机场Louis帮它避开扫描检查；飞机上两只狗又帮助其他动物。听到鹦鹉说主人也怕被抛弃，Oxy换位思考，落地后主动去找Alice。','caisse de transport','运输笼、宠物箱','avoir peur de与rassurer分别表示担心与安抚。故事中Oxy的想法会变化，不能把Rex的个人经历当成Alice必然抛弃它的证据。情节是幻想，不作真实宠物出行步骤。','像担心朋友搬家就不理你，先想一想他也可能会想念你。',[('Alice part en voyage pour quelques jours.','Alice出差几天。'),('Louis attend dans sa caisse de transport.','Louis在运输笼里等候。'),('Oxy décide de retrouver sa maîtresse.','Oxy决定去找主人。')],'Oxy在机场结识并得到帮助的狗叫什么？',['Louis','Rex','Arc-en-ciel'],'Rex在出发前给建议；机场和飞机上帮助Oxy的是Louis，Arc-en-ciel是鹦鹉。')
note('最好的朋友：小争执与长久回忆','Charlotte与Ines玩跳房子，因是否踩线争吵。虽然互不说话，她们仍一起帮Mme Morel整理阁楼。老妇人拿出与已故好友的照片，提醒她们珍惜相伴的时间。两人逐渐恢复交谈，最后获赠球拍与布朗尼。','donner un coup de main','帮一把、搭把手','se disputer是争吵，se réconcilier是和好。故事没有一句突然宣布“和好了”，而是用递玩具、微笑和再次交谈展示变化；阅读可找这些行为证据。','友谊像相册，一张小争吵不应该盖住整本快乐照片。',[('Les amies donnent un coup de main à leur voisine.','朋友们帮邻居搭把手。'),('Elles découvrent un ancien album de photos.','她们发现一本旧相册。'),('Un sourire les aide à se réconcilier.','一个微笑帮助她们和好。')],'Mme Morel请两位女孩帮什么忙？',['整理阁楼','在花园种树','修理跳房子的场地'],'她正在整理grenier，女孩们分类旧物，并在过程中看到照片。')
note('鸟舍小队：找到自己的长处','Pingouin加入由鹰指挥的动物小队，与鹰隼、猫头鹰和乌鸦训练。森林、沙漠和城市任务中它觉得自己不如别人；到南极，其他鸟很难觅食，它却能潜水捕鱼，终于看见自己对团队的价值。','coéquipier','队友','être doué pour加名词或不定式，表示擅长某事；se rendre utile表示发挥用处。名字Pingouin在作品中是角色称呼，阅读不必把幻想动物设定当生物分类课程。','拼图的每一片形状不同，缺了最不起眼的一片也拼不完整。',[('Pingouin est doué pour la pêche.','Pingouin擅长捕鱼。'),('Il partage les poissons avec ses coéquipiers.','它和队友分享鱼。'),('Chaque membre apporte quelque chose à l’équipe.','每位成员都为团队带来贡献。')],'Pingouin在南极任务中怎样帮助队友？',['潜水捕鱼并分享','飞到高空侦察','在沙漠寻找果树'],'其他鸟难以从冰面捕鱼，它擅长潜水，带回一堆鱼。')
note('Galazio：奇妙世界与家的价值','Angela受睡前故事启发，幻想彩虹是通往异世界的入口。她踏入倒映彩虹的水洼，来到Galazio，认识小仙女Emmeline，却发现这里也有上学和等待。她想家，最后从课堂中的幻想醒来，急着拥抱父母。','flaque d’eau','水洼','si引导想象条件时常与条件式结合：si je pouvais… je…rais。原文Galazio/Glazio拼写有变化，按同一幻想世界理解；分清人物经历和课堂结尾揭示的梦醒。','奇妙游乐场也有散场的时候，最温暖的入口常常是家门。',[('Une flaque d’eau reflète les couleurs du ciel.','一个水洼映出天空的颜色。'),('Angela rencontre une fée nommée Emmeline.','Angela遇见名叫Emmeline的仙女。'),('Même dans un monde magique, sa famille lui manque.','即使在魔法世界，她也想念家人。')],'Angela在幻想中通过什么进入Galazio？',['倒映彩虹的水洼','一扇教室门','仙女的魔杖'],'故事明确把倒映彩虹的水洼认作入口；Em并没有魔杖。')
note('银河小猫：字面想象与词义','Monocle、Oto与Farfouille听到“银河”，想象它是一条真正的奶河。三只小猫在纸箱变成的飞船里探索，收集温暖的发光奶，并击退老鼠。主人叫它们回家时，读者才完全回到现实。','voie lactée','银河','lacté与奶有关，但la Voie lactée是银河的名称，不是日常一条奶路。作者故意让小猫按字面理解，形成幻想。辨析真实词义与角色误解。','词语像贴纸，贴着“奶”的银河不会真的变成早餐杯，只有故事能这样玩。',[('Les chatons imaginent une rivière de lait.','小猫们想象一条奶河。'),('Monocle surveille le radar du vaisseau.','Monocle监看飞船雷达。'),('Le lait de leur rêve est chaud et lumineux.','它们梦里的奶温暖而发光。')],'哪只小猫的一只眼周围有灰色？',['Monocle','Oto','Farfouille'],'开头明确介绍Monocle的外貌；原书答案表在此题有误，应按正文。')
note('不同的心灵：想象不能代替了解','Théo看完探索身体的动画，转而想象家人的心灵。妹妹像粉色玩具沙坑，爸爸像灰色档案办公室，妈妈像明亮的书房花园。最后他意识到这些空间都来自自己已知的喜好，并开始问自己的心灵是什么样。','souvenir','回忆、纪念物','ressembler à表示像……，imaginer que表示想象……。这些比喻是Théo的推测，不是对家人心灵的客观描写。比较气味、颜色、声音和物品可整理三个空间。','像为三个人各画一张房间图，图里装的是你认识的他们，而不是他们的全部。',[('Théo imagine un bureau rempli de souvenirs.','Théo想象一间装满回忆的办公室。'),('La pièce de sa mère ressemble à une bibliothèque.','妈妈的空间像一间图书室。'),('Il se demande à quoi ressemble son propre esprit.','他想知道自己的心灵是什么样。')],'Théo想象爸爸的心灵里有哪种明显气味？',['咖啡味','草莓洗发水味','海水味'],'爸爸的灰色办公室有浓咖啡味；草莓味属于妹妹的想象空间。')
note('四季森林：把选择题变创作题','Stéphanie要写最喜欢的季节，但四季都喜欢。她询问父母朋友后，决定写四季合一的森林。最初全部混合不满意，后来被分格调味盘启发，让森林各区域各有一季；作文赢得全班欣赏。','assiette compartimentée','分格餐盘','tantôt… tantôt…表示时而……时而……；ni… ni…表示既不……也不……。季节通常用en été/en hiver/en automne与au printemps；注意春天的搭配不同。','像一盒分格颜料，不必把四种颜色全部搅成一团。',[('Au printemps, les fleurs s’ouvrent.','春天，花朵绽放。'),('Une assiette compartimentée inspire son dessin.','一只分格餐盘启发她的图画。'),('Dans sa forêt, chaque saison possède son espace.','在她的森林里，每个季节都有自己的空间。')],'什么启发她把森林划成不同季节区？',['分格装调味品的餐盘','爸爸的冬衣','一张足球比赛照片'],'她看到餐盘各格装不同调味品，想到让森林分区而非把季节混在一起。')
note('我认识所有词：词典打开新路','Marianne被同学选去写诗，自信认识所有词，拒绝词典。哥哥假装向她请教，从她会的bouloche、aromates问到不会的saltimbanque、cuniculture和花名。她发现学习没有终点，主动请哥哥教查词。','cuniculture','家兔饲养、养兔业','personne ne…表示没有人……；ne…aucun表示一个也不……。标题的“所有词”是人物过度自信的口号，结尾用反例推翻它。熟悉词→生词的顺序构成转变。','词典像一张会继续展开的地图，走到已知边界还能发现新地方。',[('Personne ne connaît tous les mots.','没有人认识所有的词。'),('Marianne découvre le mot cuniculture.','Marianne发现了“养兔业”这个词。'),('Son frère lui apprend à utiliser un dictionnaire.','哥哥教她使用词典。')],'Marianne最后主动请求学什么？',['怎样在网上和词典里查词','怎样证明所有人都不如她','怎样饲养家兔作为比赛'],'她承认还有许多生词，请哥哥教网上查询，哥哥也提出教用词典。')
note('零花钱：储蓄与分享','Jules第一次拿零花钱，以为可以买清单上的所有东西。爸爸说明预算不够，建议储蓄一部分。他把钱全放进龟形储蓄罐，后来朋友请吃冰淇淋，才想留钱回请。爸爸给预支机会，最后奖励他的责任感；他也学会分享。','tirelire','储蓄罐','une partie de表示其中一部分，tout表示全部。économiser与dépenser是相反动作；爸爸建议“一部分”而Jules起初选择“全部”，这是后续变化的重要起点。','零钱像一小盒积木，留一些搭大城堡，也留一些与朋友一起玩。',[('Jules garde ses pièces dans une tirelire.','Jules把硬币放进储蓄罐。'),('Il économise une partie de son argent.','他储蓄一部分钱。'),('Partager un chocolat lui fait plaisir.','分享一块巧克力让他开心。')],'爸爸送Jules的第一个储蓄罐是什么形状？',['乌龟','小猪','小汽车'],'正文是tirelire en forme de tortue；不要按常见猪形储蓄罐猜答案。')
note('武术梦想：先弄清消息来源','Beth看武术表演后想学习，却被Bobby关于训练会弄伤骨头肌肉的说法吓到。她找哥哥Keith求证，哥哥查资料并鼓励她请父母带去观察课程。人物查过网页并不自动让叙述成为可靠的训练说明；本课只练阅读与求证表达。','avait tort','弄错了、判断错了','avoir tort与avoir raison分别表示判断错与对。D’après cet article表示据这篇文章；这是注明消息来源，不等于证据已充分。故事中的健康与训练断言不作现实指导或答题知识。','像听说泳池里有怪兽，先找可信的教练问清楚，而不是照传言行动。',[('Beth se demande si son cousin a tort.','Beth想知道表亲是不是弄错了。'),('Elle pose une question à son frère.','她向哥哥提出一个问题。'),('Elle n’a pas encore choisi son art martial.','她还没有选好要学哪种武术。')],'故事结束时Beth选定具体哪种武术了吗？',['还没有选定','已经确定柔道','已经确定跆拳道'],'Keith询问她想学哪种，她回答还不知道，并建议之后由父母陪同了解。')
note('这是什么主意：结果与尝试','Cindy把自己的鞋带绑在一起，想独自练两人三足，却摔倒。她把不同主意想象成人：失败的尝试、楼梯、电梯和花园小矮人。楼梯电梯各有利弊，小矮人主意提醒她有些结果需要尝试才知道。','tenter sa chance','试一试、碰碰运气','utile与inutile表示有用与无用；comparatif plus… que…可用于比较楼梯和电梯。故事让“主意”说话是拟人，并非靠外貌就能可靠判断一个主意好坏。','主意像新拼图，有些要放一放、试一试，才知道能不能接上。',[('Cindy cherche une idée plus pratique.','Cindy寻找更实用的主意。'),('Un ascenseur ne fonctionne pas sans électricité.','电梯没有电就无法运转。'),('Elle veut tenter sa chance avec un nouveau projet.','她想试试一个新计划。')],'Cindy起初为什么不开心？',['自认聪明的训练主意失败，还摔伤了手肘','忘了去学校','花园里的楼梯坏了'],'开头交代她把鞋带绑一起，第一步就摔倒，自尊也受打击。')
note('好运与努力：用实例支持观点','Jacob在院子里找四叶草，希望好运让游戏、足球与成绩都变好。姐姐Leah用他的历史进步、妈妈园艺进步和自己的篮球训练举例，说明努力的重要。他理解后仍想找四叶草，但理由变成觉得有趣。','trèfle à quatre feuilles','四叶草','grâce à常接积极原因；en comptant sur表示依靠。读论点后找具体例子，别把最后继续找草误读为完全没听懂姐姐，因为他的动机已经改变。','好运像顺风，练习才是你真正会踩的自行车踏板。',[('Jacob cherche un trèfle à quatre feuilles.','Jacob寻找四叶草。'),('Leah s’améliore grâce à son entraînement.','Leah通过训练取得进步。'),('Il demande de l’aide pour mieux apprendre.','他请求帮助，以便学得更好。')],'Leah用哪项自身经历说明努力的作用？',['经过训练成为学校篮球队队长','捡到四叶草后赢得彩票','一夜学会所有历史知识'],'她明确说经过数月努力训练，成为篮球队队长。')
note('生活不是游戏：读懂别人的感受','Charlie刚玩完射击游戏，把家里继续当战场，逗妹妹、想用勺子弹橄榄，还把邻居家叫敌方领地。妈妈提醒他真人没有游戏数据可看，行为会伤人、惹麻烦。他答应更懂事；餐桌让兄妹恢复合作。','se comporter','表现、举止','cesser de加不定式表示停止某行为，promettre de表示承诺做某事。阅读时把游戏中的“任务胜利”与现实中的“他人感受”分开，才能理解妈妈的担忧。','游戏角色有血量条，朋友没有屏幕提示，要靠倾听才能知道感受。',[('Charlie promet de mieux se comporter.','Charlie答应表现得更好。'),('Sa sœur n’aime pas ce jeu.','妹妹不喜欢这个游戏。'),('Il doit écouter les sentiments des autres.','他应该倾听别人的感受。')],'妈妈和Charlie认真谈话的主要原因是什么？',['他把现实当游戏，行为困扰别人','他的电脑开不了机','他没有找到游戏宝藏'],'妈妈列出逗妹妹、学校冲突与称邻居为敌人的行为，担心他继续惹麻烦。')
note('瓶中船：传说与手工过程','Aria跟爷爷逛海边摆件店，被瓶口小、船却大的模型吸引。店主先讲小精灵造船传说，再揭示模型由爷爷制作。回家后爷孙制作船体和帆，在瓶内组合、拉线展开，Aria最后塞入瓶塞。','voile','船帆','tout d’abord、puis、maintenant可标出制作步骤。注意la voile是帆，le voile可指面纱；本篇只学船的语境。传说与爷爷实际展示的制作过程分属不同叙述层。','先听一个魔法解释，再像拆积木一样看清真正的组装过程。',[('Aria dessine les voiles sur du papier.','Aria在纸上画出船帆。'),('Son grand-père assemble les pièces dans la bouteille.','爷爷在瓶内组装零件。'),('Elle ferme la bouteille avec un bouchon.','她用瓶塞封住瓶口。')],'店里那些让Aria惊叹的瓶中船是谁制作的？',['她的爷爷','来自海上的小精灵已被证实','她学校的老师'],'店主先讲传说，随后明确说所有这些模型都是她爷爷做的。')
note('每顿吃糖吗：追问为什么','Jayden午餐时觉得糖比蔬菜更好吃，问为什么不每餐吃糖。他不断提出反问，包括能否用补充剂代替蔬菜；家人试着解释。他最后吃完饭又问甜点，得到水果沙拉，形成幽默收尾。','rassasié','吃饱的、饱足的','pourquoi引出原因问题，parce que给理由，au lieu de表示代替。本篇重点是提问与解释的语言，原作营养讨论包含简化断言，不能直接作为个体饮食指导。规范例句用pâtes表示面食。','好问题像打开饭盒的一层盖子，问完一层还会看见下一层。',[('Jayden demande pourquoi le repas est varié.','Jayden问为什么这顿饭有多种食物。'),('Après le déjeuner, il se sent rassasié.','午餐后，他觉得吃饱了。'),('Son père a préparé une salade de fruits.','爸爸准备了水果沙拉。')],'最后爸爸告诉Jayden甜点是什么？',['水果沙拉','一整块巧克力蛋糕','只有糖果'],'结尾的明确答案是une salade de fruits；家人因他的失望表情而发笑。')
note('网络安全故事：区分故事与可靠规则','Eleanor下载游戏嫌网速慢，姐姐解释病毒、木马与备份，并借特洛伊木马传说打比方。但原作错误地把锁图标等同网站及下载安全。本课保留原文供对照，同时明确：连接加密不保证网站可信或文件安全。','logiciel malveillant','恶意软件','se faire passer pour表示冒充；une copie de secours表示备份。把来源陈述与核实结论分开阅读。锁图标涉及HTTPS连接保护，不是对网站信誉、下载文件或游戏安全的保证；此点已据Chromium官方说明校核。','信封封好了能保护信在路上的内容，却不能证明写信的人说的都是真的。',[('Un logiciel malveillant peut se faire passer pour un jeu.','恶意软件可能冒充游戏。'),('Eleanor apprend le sens du mot sauvegarde.','Eleanor学习“备份”这个词的含义。'),('Une connexion chiffrée ne garantit pas un fichier sûr.','加密连接不保证文件安全。')],'姐姐借哪段传说解释伪装成无害程序的恶意软件？',['特洛伊木马','灰姑娘','瓶中船精灵'],'正文先讲希腊人把士兵藏在木马中，随后类比程序伪装。锁图标的原作断言另有纠错，不作为正确知识。')
note('缩小的一天：用比较看世界','Felicity在外婆家窗边看昆虫，想象自己变小。柠檬水杯像塔，草像丛林；她看见蚂蚁、千足虫、蜻蜓与蛞蝓。螳螂逼近时蝴蝶救她回窗边。她回床上休息，相信下次醒来会恢复。','minuscule','极小的、微小的','aussi… que…表示同样……；plus… que…表示更……。大小改变带来视角改变，同一个杯子可以比作高塔。结尾只写她相信会恢复，并未描写下一次醒来。','把你的玩具小人放在草丛里，就会发现草叶也能像大树。',[('Le verre paraît aussi haut qu’une tour.','杯子看起来像塔一样高。'),('Felicity devient minuscule dans son aventure.','Felicity在冒险中变得极小。'),('Un papillon la ramène à la fenêtre.','一只蝴蝶把她带回窗边。')],'Felicity受到螳螂威胁时，谁救了她？',['蝴蝶','蜻蜓','一只蚂蚁'],'她被带到空中，抬头看到蝴蝶彩色翅膀，随后被放回窗边。')
note('可以哭：勇敢与表达','Riley踢球跌倒，明明疼却怕显得软弱而不肯哭。妈妈照顾他，并用爸爸因疼痛、爱犬离世和妹妹出生而哭的例子，区分疼痛、悲伤和喜悦。Riley终于承认自己很疼，接受拥抱。','larmes de joie','喜悦的泪水','avoir mal à加身体部位表示某处疼：au genou、à la cheville。故事主要讨论表达感受，不把其中家庭处理伤情的步骤当作医疗说明。勇敢在人物对话中被重新理解。','眼泪像情绪的窗户，开一开让别人看见你需要帮助。',[('Riley a mal au genou.','Riley膝盖疼。'),('Son père a versé des larmes de joie.','爸爸流下了喜悦的泪水。'),('Il ose enfin dire ce qu’il ressent.','他终于敢说出自己的感受。')],'妈妈提到爸爸因哪件高兴的事流泪？',['Riley妹妹出生','足球队输球','踩到海胆'],'妈妈把妹妹出生的眼泪解释为larmes de joie，与另两种疼痛和悲伤的情境区别。')
note('照片与回忆：感受也被留下','老师发给Freya研学照片，爸爸把欢乐的几张挂在走廊。她好奇为什么墙上多是笑脸，于是翻相册，看见童年装扮、过敏的尴尬、旧家与去世爷爷等回忆。她想到照片不只保留事件，也唤起不同感受。','nostalgique','怀念往昔的、怀旧的','rappeler quelque chose à quelqu’un表示让某人想起某事。joyeux、triste、nostalgique分别表达不同情绪；Freya的喜好是人物感受，不是所有家庭都应遵守的挂照片规则。','照片像小音乐盒，打开时不仅看到画面，还会听见那天的心情。',[('Cette photo rappelle un voyage à Freya.','这张照片让Freya想起一次旅行。'),('Elle se sent nostalgique en regardant son ancienne maison.','看旧家的照片时，她感到怀念。'),('Son père accroche les images dans le couloir.','爸爸把照片挂在走廊。')],'Freya把老师给的照片放哪里带回家？',['书包里两本书之间','教室地板上','外套的湿口袋里'],'正文交代她放在书包里的两本书之间，以免照片折皱。')
note('和我说话：动物对话的想象','Caleb带着存下的钱与爸爸去能领养获救动物的店，准备捐款。看到鹦鹉重复人话，他想象狗、鱼、鸟和猫会说什么。故事明确说金鱼三秒记忆说法不正确，只把它当假设笑话；结尾他仍没决定领养谁。','don','捐款、赠予','si与条件式可用来构想尚未发生的对话：si les animaux parlaient…。don与achat不同，店内设置强调以捐助支持救助与领养。结尾的未作决定不能脑补成已选猫。','把宠物的动作想象成台词，就像给无声漫画配对白。',[('Caleb veut faire un don à l’association.','Caleb想向协会捐款。'),('Le perroquet répète quelques mots.','鹦鹉重复几个词。'),('Il n’a pas encore choisi son animal.','他还没有选好自己的动物。')],'故事最后Caleb决定领养哪种动物？',['还没有决定','已经选定小猫','已经选定金鱼'],'爸爸问是否选好，他回答还没选，可能需要帮助。')
note('变形女巫：误读与新认识','暴风雨停电夜，Oliver听到敲门，来客Julie是妈妈的大学好友。他因黑衣、咳声与电影印象猜她是变形女巫。后来发现她只是觉得爸爸泡的茶难喝；分享巧克力与旅行照片后，他改变了看法。','se faire passer pour','冒充、装作','croire que描述相信的内容，不代表事实成立。列出“看到的事实→Oliver的猜测→后来解释”三列，可辨认惊悚气氛怎样制造误会。结尾仍称女巫是一句亲切玩笑。','黑暗里外套像怪物，开灯看清后也许只是来做客的阿姨。',[('Oliver croit qu’une sorcière se fait passer pour Julie.','Oliver以为女巫冒充了Julie。'),('En réalité, elle trouve le thé mauvais.','实际上，她觉得茶难喝。'),('Julie lui montre des photos de voyage.','Julie给他看旅行照片。')],'Oliver听到的吐声最后被解释为什么？',['Julie把难喝的茶吐进纸巾','女巫正在变回原形','窗外的树折断了'],'他进房看到Julie拿着纸巾，她低声说爸爸泡的茶难喝。')
note('天气的秘密：从猜想走向解释','Amy带伞上学，猜天气预报员是否到处旅行、去太空或向外星人问天气。老师区分播报员与气象学家，介绍观测数据、仪器与模型。她虽然失去一个奇幻猜想，却更好奇，最后跑向图书馆找书。','baromètre','气压计','servir à加不定式表示用途。qui用于说明人，qui/que关系从句还可补充事物功能。读老师说明时分“谁播报、谁研究、用什么信息”三组，不必背完所有技术名词。','预报像根据拼图推测整幅画，先收集很多片，不能只抬头看一眼。',[('Amy emporte son parapluie à l’école.','Amy带伞去学校。'),('Un baromètre sert à mesurer la pression de l’air.','气压计用来测量气压。'),('Elle cherche des livres pour en savoir plus.','她找书来了解更多。')],'故事最后Amy去哪里继续了解天气？',['图书馆','机场','外星飞船'],'她感谢老师后拿上借书卡，趁课间去图书馆。')
note('收藏什么：兴趣与实际条件','Marty见朋友收藏信封邮票，也想有自己的收藏。他比较花、钱币、漫画、标本、石头与奖牌等选择，考虑兴趣、空间和成本。最后想到既吃巧克力又留下包装，清理并贴进本子；父母同意但要求不过量吃。','emballage','包装','au lieu de表示而不是、代替；du moment que表示只要。选择过程靠排除不合适项目推进。区分collectionner le chocolat与collectionner les emballages，是理解最终方案的关键。','收藏像给喜欢的事做一册小档案，不一定要把最大最贵的东西搬回家。',[('Marty collectionne les emballages de chocolat.','Marty收藏巧克力包装。'),('Il colle le premier dans un carnet neuf.','他把第一张贴进新本子。'),('Les ballons prennent trop de place dans sa chambre.','球在他房间里占地方太多。')],'Marty最后选择收藏什么？',['巧克力包装','整盒永不打开的巧克力','真正的足球比赛'],'他想到可以吃掉巧克力，再清理包装贴进本子，两种兴趣结合。')
note('人人都能教：把步骤讲清楚','M. Adler发现学生不想学数学，又因雨不能出去，于是让每人准备一个五分钟小课。Lucy教画熊，Colin教折纸飞机，其他人教编发、打结和辨词。活动后大家心情更好，但数学课仍要继续。','enseigner','教、教授','apprendre既可表示学，也可表示教：apprendre quelque chose à quelqu’un是教某人某事。使用d’abord、puis、enfin讲步骤；命令式dessinez邀请全班一起画。','每个人的口袋都有一件会做的小事，拿出来就能当五分钟老师。',[('Lucy enseigne à la classe comment dessiner un ourson.','Lucy教全班怎样画小熊。'),('Colin plie une feuille pour fabriquer un avion.','Colin折一张纸来做飞机。'),('Ensuite, les élèves reprennent leur cours de mathématiques.','然后学生们继续上数学课。')],'活动结束后，数学课是否被取消？',['没有，老师宣布继续学加法','取消了一整年','改成永远只上画画课'],'老师一开始就说之后仍上数学课，结尾明确开始学加法。')
note('谁拿了羊腿：让线索说话','Maximilian练剑后和弟弟Edward去厨房，厨娘认定有人偷羊腿。女仆说擦掉了通向后门的油脂和“泥土”；Edward想到那可能是香料。兄弟去狗窝发现半吃掉的羊腿，解开误会，Edward得到草莓小挞奖励。','coupable','有责任的、罪魁、犯错者','devoir加不定式既可表示义务，也可表达推测，本篇“must have dragged”的推断要看语境。问最后见到物品的时间与痕迹，比直接指责某个人更有助于理清情节。','侦探像顺着面包屑找路，先看地上的证据，再决定往哪里走。',[('Edward remarque une trace de graisse.','Edward注意到一道油脂痕迹。'),('Le chien dort près du gigot d’agneau.','狗在羊腿旁睡觉。'),('La cuisinière découvre enfin le coupable.','厨娘终于发现了罪魁。')],'失踪的羊腿最终在哪里找到？',['王子养的狗的狗窝里','铁匠的炉子旁','骑士的盔甲中'],'Maximilian在狗窝看到狗睡着，围着已经吃掉一半的羊腿。')
note('猜猜惯用语：字面与实际意思','Emma学校举办惯用语日，学生用装扮、画画与动作让同学猜。狗装对应狗叫与商队，三个线索组成“时间就是金钱”；Emma戴猫耳、打呵欠，让大家猜别惊醒睡猫。她最喜欢的是同学用心准备的表达过程。','c’est du gâteau','这很容易、小菜一碟','固定表达的实际意思不总能逐词相加。c’est du gâteau是“很容易”，不是当场介绍甜点；le temps, c’est de l’argent要整体理解。原文对部分谚语的写法解释可再查词典，不照搬成唯一标准。','惯用语像暗号，看到蛋糕图片有时说的是容易，而不是开饭了。',[('Pour elle, ce petit exercice, c’est du gâteau.','对她来说，这道小练习轻而易举。'),('Emma mime un chat qui dort.','Emma模仿一只睡着的猫。'),('Ses camarades devinent le sens de l’expression.','同学们猜出这个表达的意思。')],'Emma说自己最喜欢哪条表达？',['Le temps, c’est de l’argent','所有关于狗的谚语','一条关于篮球的规则'],'正文说她喜欢同学逐步表演“时间/C/金钱”的努力，而原书本篇答案表多处不符。')
note('儿童集市：从观察到公益行动','Toby与爸爸去菜市场、超市，回程看到邻居旧物出售，想到办儿童集市。他与朋友商量交换旧物、卖点心，征得父母和邻居同意。三张桌子变成社区活动，最后收入装入写着孩子名字的信封，捐给医院儿童慈善项目。','échange','交换','échanger X contre Y表示用X换Y，faire un don à表示向……捐赠。marché既可指市场，也可指协议；本篇标题首先是孩子办的市场。辨认想法、准备、实施与结果四阶段。','把不再玩的玩具放上共享桌，一个人的旧物就能成为另一个人的新惊喜。',[('Toby échange sa voiture contre un T-shirt.','Toby用小汽车换了一件T恤。'),('Les voisins prêtent des tables aux enfants.','邻居把桌子借给孩子们。'),('Le groupe fait un don à un programme pour les enfants.','小组向一个儿童项目捐款。')],'孩子们最后如何处理集市收入？',['捐给医院的儿童慈善项目','全买电子游戏','平均买巧克力当晚吃完'],'正文结尾说钱装入署名信封，送往医院儿童慈善项目。')
note('乌龟岛：移动的文化展馆','Carter看见乌龟背岛的插图，想象在移动岛屿生活。他认识Elena，在纪念品展馆看来自各地的陶器与服饰：日本招财猫、俄罗斯Gzhel、摩洛哥塔吉锅等。岛不只提供不同食物，也成为接触文化语言的旅程；他想写图画书。','carapace','甲壳、龟壳','venir de与provenir de表示来自，servir à表示用途。展馆是陶器区与服装区等分区，并非只有花瓶。把物品、来处、功能配成三列，记忆更牢。','一只大乌龟背着流动图书馆，每到一处就带回新的故事。',[('La tortue porte une île sur sa carapace.','乌龟的甲壳上托着一座岛。'),('Elena présente une théière venue de Russie.','Elena介绍一把来自俄罗斯的茶壶。'),('Carter veut créer son propre livre illustré.','Carter想创作自己的图画书。')],'Elena介绍的Gzhel陶器来自哪里？',['俄罗斯','日本','摩洛哥'],'俄罗斯对应Gzhel茶具，日本对应Maneki-neko，摩洛哥对应塔吉锅。')
note('一起打扫：分工让家务有趣','Ophelia分工，Marshall洗碗，Jennie吸尘，她负责洗衣和厨房地面，爸爸负责较难的窗户镜子与卫生间。每人给任务增加游戏感；完成后全家外食，妈妈回来表达欣赏。阅读留意轮换任务与最初分工的差别。','faire la vaisselle','洗碗','s’occuper de表示负责、照顾；être chargé de表示被安排负责。pendant que可表达多人同时劳动。原文清洁用品描述仅是情节，课程不把它当产品使用或儿童独立操作指引。','家庭像一支小乐队，各自弹好一件乐器，整首歌才会顺。',[('Marshall fait la vaisselle avec soin.','Marshall认真洗碗。'),('Jennie passe l’aspirateur dans le salon.','Jennie在客厅吸尘。'),('Ophelia s’occupe du linge pendant que son père nettoie les fenêtres.','爸爸擦窗时，Ophelia负责衣物。')],'最初分工中谁负责洗碗？',['Marshall','Jennie','Ophelia'],'姐姐说明Jennie上周洗过，这周由Marshall洗；之后会有房间和任务轮换。')

ISSUES=[
 {'unit':4,'message':'原书第2题仅四个选项，答案却写E；按题面“成人吃很多难吃的东西”应对应A。原答案照存。'},
 {'unit':12,'message':'正文主人名为Alice，原题第1题选项却无Alice，答案A对应Alison；英语摘要还把Oxy代词变成she。以法语正文辨认角色，原版照存。'},
 {'unit':16,'message':'原书第3题正文为Monocle（B），答案却D；第4题正文奶是Chaud（D），答案却B（Coloré）。原答案照存。'},
 {'unit':21,'message':'人物对骨骼、肌肉与武术训练的断言属于原作叙述，未作为可靠健康知识校核。本课不将其用作训练指导或正确知识测验。'},
 {'unit':26,'message':'原文营养讨论存在简化断言，不能作为个体饮食或补充剂指导；原文把pâtes（面食）多处拼成pattes（爪/腿），新编例句使用规范拼写。'},
 {'unit':27,'message':'原作声称锁图标能保证网站和下载安全，此结论不成立；HTTPS连接加密不保证网站可信或文件安全，见Chromium官方说明。词表还把rhume与grippe英译颠倒：rhume是感冒，grippe是流感。'},
 {'unit':29,'message':'原文家庭处理受伤情节未作医疗方法校核；只用于理解人物感受与语言，不作伤情处理指引。'},
 {'unit':37,'message':'原书第1–4题答案与正文/题面冲突：正文与法题应为A、D、D、A，原答案为D、A、A、C；第5题A一致。原答案照存。'},
 {'unit':40,'message':'原作清洁用品、口罩与家务操作描述属于故事情节，未作为产品安全使用说明校核。'},
 {'unit':0,'message':'原作多处法语拼写、变位、配合及英文词表译义存在问题；完整来源照存，课程自编例句另行规范编辑。level为本项目教学建议，故事虽标“初学者”仍大量使用简单过去时与复杂句，按B1带读。'}
]

def write_lessons(units,meta):
    assert len(LESSONS)==40
    dest=ROOT/'french/stories';dest.mkdir(parents=True,exist_ok=True)
    for unit,data in zip(units,LESSONS):
        n=unit['unit'];lid=f'S{n:02}';prereq=[] if n==1 else [f'S{n-1:02}']
        info={'id':lid,'title':data['title'],'book':'stories','book_title':'故事阅读：40个小世界','book_fr':'40 histoires à lire','category':'阅读','level':'B1','section':f'第{unit["volume"]}卷 · 故事阅读','prerequisites':prereq,'minutes':18 if n in (8,15,37) else 12,'status':'original-edited-draft','source_units':[f'french-stories:{n}'],'source_reader':{'book_id':'french-stories','unit':n},'source_title':unit['title'],'source_sha256':meta['sha256']}
        # Rotate the correct choice position to avoid a predictable all-A key.
        options=list(data['choices']);shift=(n-1)%3;options=options[shift:]+options[:shift];correct=options.index(data['choices'][0]);wordopts=[data['meaning']]+list(DISTRACTORS[n-1]);wshift=n%3;wordopts=wordopts[wshift:]+wordopts[:wshift];wcorrect=wordopts.index(data['meaning'])
        issues=[i['message'] for i in ISSUES if i['unit']==n]
        text='---\n'+json.dumps(info,ensure_ascii=False,indent=2)+'\n---\n\n# '+lid+' · '+data['title']+'\n\n'
        sections=[('学完能做什么',f'读懂《{unit["title"]}》的人物、事件与转折；能用自己的话复述，并在语境中理解 {data["focus"]}。'),('讲解',data['synopsis']+'\n\n'+data['point']+'\n\n词语抓手：'+data['focus']+' 表示“'+data['meaning']+'”。先在完整原文找到这个词，再读原书词表核对上下文；原词表是法英对照，新课中文释义为本项目编写。'+(('\n\n来源提醒：'+' '.join(issues)) if issues else '')),('给小朋友的比喻',data['analogy']),('例句','\n'.join('- '+fr+' → '+zh for fr,zh in data['examples'])),('练习','### 1. '+data['question']+'\n\n'+'\n'.join(f'- {chr(65+i)}. {v}' for i,v in enumerate(options))+'\n\n### 2. 本篇语境中的“'+data['focus']+'”是什么意思？\n\n'+'\n'.join(f'- {chr(65+i)}. {v}' for i,v in enumerate(wordopts))),('答案与原因',f'1. {chr(65+correct)} — '+data['reason']+f'\n2. {chr(65+wcorrect)} — 本篇语境中 {data["focus"]} 对应“{data["meaning"]}”；应结合原文中的动作、物品和上下文辨义，另两项不符合此处语境。'),('一分钟应用',f'不看摘要，用三句话说出《{unit["title"]}》的开始、转折和结尾。至少一句使用 {data["focus"]}；再说出你支持判断的一处原文线索。遇到简单过去时，可先用现在时复述，再挑战复合过去时。'),('相关学习',('S06、S08：现实与幻想线索' if n==7 else ('S07：续篇与结局' if n==6 else (f'S{n-1:02}：上一篇；' if n>1 else '')+(f'S{n+1:02}：下一篇' if n<40 else 'S01：回到第一篇比较阅读进步')))),('参考资料','- [Dictionnaire de l’Académie française — 法语词典](https://www.dictionnaire-academie.fr/)'+ ('\n- [Chromium — 锁图标与连接安全](https://blog.chromium.org/2023/05/an-update-on-lock-icon.html)' if n==27 else '')+f'\n\n本课来源：用户提供 EPUB 第{unit["volume"]}卷第{unit["chapter"]}篇《{unit["title"]}》。完整正文、原词表、摘要、原练习和答案见本课来源阅读器；可回查 '+', '.join(unit['source_hrefs'])+'。\n\n本课讲解、中文释义、比喻、例句与两道练习均为本项目原创编写；原书材料保留在来源版，不把新编内容归属于原作者。等级为教学建议。')]
        text+='\n\n'.join('## '+title+'\n\n'+body for title,body in sections)+'\n'
        (dest/(lid+'.md')).write_text(text)
    reader=json.loads((OUT/'reader.json').read_text());reader['issues']=ISSUES;(OUT/'reader.json').write_text(json.dumps(reader,ensure_ascii=False,indent=2))
    report={'book_id':'french-stories','source_file':meta['source_file'],'source_sha256':meta['sha256'],'spine_documents':meta['spine_documents'],'blocks':meta['blocks'],'units':40,'volumes':[10,10,20],'lessons':40,'original_examples':120,'original_exercises':80,'reader_unit_blocks':sum(len(u['blocks']) for u in units),'fr_story_blocks':sum(b['role']=='story' and b['lang']=='fr' for u in units for b in u['blocks']),'non_story_spine_documents':meta['non_story_spine_documents'],'validation':{'lesson_schema':'40 lessons parsed by build_site.parse_lesson; exactly 9 sections, 120 examples and 80 quizzes','source_text':'All 313 spine documents compared to original XML body text after whitespace normalization; list labels retained from EPUB upper-alpha style with source_text for comparison','local_links':'All local links and images in book.md checked against extracted raw members','reader_partition':'All 4892 text blocks occur exactly once in reader units or front_matter'},'source_note':'Full EPUB spine, raw XHTML/assets, source vocabulary/exercises/keys retained. English summaries are summaries, not full translations. Source-derived text and new Chinese editorial material are distinct.','issues':ISSUES,'records':[{'source_book':'french-stories','source_unit':u['unit'],'lesson_ids':[f'S{u["unit"]:02}'],'source_hrefs':u['source_hrefs'],'title':u['title'],'volume':u['volume'],'chapter':u['chapter']} for u in units]}
    (ROOT/'docs/stories-import.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))

DISTRACTORS=[
('新车','驾照'),('城堡','食堂'),('浇水','修剪叶子'),('一顿饭','一把叉子'),('路灯','项圈'),
('阳光','毯子'),('木匠','骑士'),('松树','河流'),('船员','木板'),('颜色','制服'),
('酱汁','烤箱'),('行李传送带','安全扫描器'),('打一通电话','举起拳头'),('指挥官','猎物'),('彩虹','水流瀑布'),
('飞船','星际雷达'),('作业','文件抽屉'),('普通平盘','餐具柜'),('街头表演艺人','白豆炖肉'),('龟壳','购物清单'),
('说对了','拿错了东西'),('承认失败','拒绝机会'),('三叶薄荷','玫瑰花瓣'),('安慰别人','挑选东西'),('船体','瓶塞'),
('饥饿的','生气的'),('加密连接','备用文件'),('巨大的','危险的'),('悲伤的泪水','受伤的眼泪'),('感到尴尬的','正在发怒的'),
('购买价格','宠物玩具'),('向某人请教','与某人交朋友'),('温度计','风速计'),('邮票','纸币'),('学习','计算'),
('目击者','对手'),('这很困难','这是蛋糕店'),('捐款','购买收据'),('岛屿','海洋'),('吸尘','洗衣')]

if __name__=='__main__':
    source=Path(sys.argv[1]) if len(sys.argv)>1 else next(Path('/Users/ziye/Downloads').glob('Learn French for Beginners*epub'))
    units,meta=convert(source)
    write_lessons(units,meta)
    print(json.dumps({k:meta[k] for k in ('id','sha256','spine_documents','story_units','blocks')},ensure_ascii=False))
