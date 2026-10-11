"""Materialize editorial records as canonical Markdown. Website builds read Markdown only."""
from pathlib import Path
import json,re,random
ROOT=Path(__file__).resolve().parents[1]
BOOKS=[
 ('grammar','G',42,'语法：从句子到论证','Grammaire en pratique','语法','从基础句型到时态、代词、从句与语气。'),
 ('expressions','E',28,'表达：日常搭配','Expressions du quotidien','表达','用完整词组处理交流、生活和服务场景。'),
 ('advanced-expressions','A',24,'表达：精确与深入','Expressions et nuances','表达','将语体、概念与抽象表达放进真实交流。'),
 ('pronunciation-basic','P',20,'发音：第一步','Les sons du français','发音','先建立声音区别，再理解拼读和基本连接。'),
 ('pronunciation-connected','M',15,'发音：连成句子','Du mot à la conversation','发音','音节、节奏、联诵与日常话轮。'),
 ('pronunciation-fluent','F',15,'发音：自然陈述','Parler avec clarté','发音','在会话、叙事和正式陈述中组织信息。'),
 ('idioms','I',24,'习语：理解与运用','Images et idiomes','习语','理解比喻、语体与具体使用边界。')]
SOURCE_COUNTS={'grammar':145,'phrasal-verbs':70,'phrasal-verbs-advanced':60,'pronunciation-elementary':50,'pronunciation-introduction':60,'pronunciation-advanced':60,'oxford-idioms':60}
SOURCE_MAP={}
def map_units(book,units,targets,reason):
 for n in units:
  if (book,n) in SOURCE_MAP:raise ValueError(f'duplicate source {book} {n}')
  SOURCE_MAP[book,n]={'source_book':book,'source_unit':n,'targets':targets.split(), 'adaptation':reason}
def span(a,b):return range(a,b+1)

def make_mapping():
 b='grammar'
 groups=[(1,1,'G08'),(2,2,'G03 G08'),(3,4,'G08'),(5,5,'G09'),(6,6,'G11 G12'),(7,10,'G09 G14'),(11,12,'G14'),(13,14,'G12'),(15,16,'G13'),(17,17,'G02 E08'),(18,18,'G11'),(19,20,'G15'),(21,24,'G16'),(25,25,'G16 G19'),(26,26,'G17'),(27,27,'G18'),(28,28,'G17 A08'),(29,30,'G17 A08'),(31,32,'G17 G06'),(33,37,'G18 E23'),(38,41,'G19 G20'),(42,46,'G21'),(47,48,'G22'),(49,50,'G07 G22'),(51,52,'G07 G17 M12'),(53,68,'G23 G42'),(69,70,'G26 G27'),(71,75,'G25 G26'),(76,78,'G40 G25'),(79,80,'G27 E04'),(81,81,'G28'),(82,84,'G32 G01 G28'),(85,91,'G32 G37 G26'),(92,93,'G33'),(94,96,'G34'),(97,99,'G35 G23'),(100,101,'G35 G37'),(102,104,'G36 G37'),(105,108,'G36'),(109,110,'G29 G30 G31 G37'),(111,112,'G37'),(113,113,'G39'),(114,115,'G19 G20'),(116,116,'G38 G41'),(117,118,'G35 G19 I24'),(119,120,'G14 G41'),(121,122,'G41 E09'),(123,126,'G40 E14'),(127,128,'G40 G42'),(129,131,'G35 G42 E04'),(132,136,'G42 E12 E13'),(137,138,'E14 E15'),(139,139,'E16'),(140,140,'E14'),(141,142,'E19 E20'),(143,144,'E15 E25'),(145,145,'G42 E01')]
 for a,z,t in groups:
  reason='保留语法学习功能，以目标单元中的法语结构重写例句与练习；重叠讲解合并。'
  if a in [7,13,15,19,21,25,33,38,53,117]:reason='语言体系适配：英语时态、情态或非限定结构不作逐字等同，使用法语时态、语气、不定式和条件结构解释相同表达功能。'
  if a>=137:reason='替换英语短语动词粒子规则：学习法语方向、阶段、结果与固定动词搭配；不宣称法语拥有同一粒子系统。'
  if a==46 or (a<=46<=z):reason+=' 使役主题补充法语 faire + 不定式，区别于被动。'
  map_units(b,span(a,z),t,reason)
 b='phrasal-verbs'
 targets=['E01','E03','E12 E13','E04','E02 E03','E10','E08 E09 A06','E10 E14','E21 E22','E05','E07','E06','E16 E19','E14 E15','E15','E12 E13','E16','E14','E12 E13','E14 E19','E14','E17','E17 A07','G40 E14','E18','E16 A09','E20','E19','E14 A23','A16 E15','E21','E22','I13','E22','E23','E25','E25 A13','E24','E24','I19 E24','A16','E26','E26','A18','E26 A17','I11 A17','A19 E26','A19 E26','I12 A17','E21 E23','I05 E27','I04 E27','I04 A21','I17 E21','E27 G11','E28 A22','I13 E05','E27 A20','I13 E27','E28 I10','A24','E28','I09 E28','A04','A04','I14 A18','I23 A16','I15 A11','F14 E02','A04']
 for n,t in enumerate(targets,1):map_units(b,[n],t,'沿用核心动词、概念、功能或生活主题；英语粒子与地区变体改编为法语真实搭配和法语语体/地区差异。')
 b='phrasal-verbs-advanced'
 targets=['A01 E01','A01 G42','A02 E04','A02 G35','A01','E02 A01','A03','A03 I01','A04','A05','A05 E16','A05 E12','A05 E15','A05 E12','A05 E14','A05 E16','A07','A08','A09','A10','A09','A16','A23','A11','A12','A13','A14','A15','A15','A13','A16','A17','A18','A18','A17 I12','A19','A20','A20','A21 I04','A21 I02','A21 I05','A21 I13','A22','A22 I06','A23','A23 E14','A24','A24','G40 E28','E28 I09','A18 I14','I17','I23','A04','E28 I10','A06 E10','A06 E08','A06 E10','A06 E11','A06 E06']
 for n,t in enumerate(targets,1):map_units(b,[n],t,'保留高级搭配、隐喻、语体和主题功能；以法语对应表达重新编写，重复主题与基础册及习语册联读。')
 b='pronunciation-elementary'
 targets=['P01','P02','P03','P05','P06','P02','P04','P02 P04','P14','P06 P14','P09','P09','P09','P10','P10 P11','P10','P11','P11','P13','P12 P15','P12','P12','P14','M08','M08','M08 P15','M02 M08','P17','P04 M05','M03','M03','M03 E01','M09','P19 M02','P19 M02','P17 M03','M04','M04','M04 G01','M07 G09','M05 F03','M07 P15','M07 G09','F06 M11','F09','F08','M11 F06','M11 F06','P20 M12','P20 M12']
 for n,t in enumerate(targets,1):map_units(b,[n],t,'发音教学方法保留；英语音值、词重音、词尾和弱读规则替换为法语声音、节奏组、静音词尾与语流。')
 b='pronunciation-introduction'
 targets=['P01','P02','P09','P10','P09','P02','P04 M05','P10','P09','P14 P15','P02 P14','P11','P12','P05 P04','P13','P06','P10 P11','P03','P04','P14','P17','M03','M03 M04','M08','M08 P15','M07 P15','M07 G09','M03','M03 E01','M03','M03','M11','M04','F03 M05','M07 G01','M07 G17','M04','P19 M02','P19 M02','M08 F04','M10','M09','F05 P17','M10','F09','F08','M10 E23','F12','M11','M11 F06','M11 F06','M13','M11','M12 P20','M12','M12','F06','F13','F07','F07']
 for n,t in enumerate(targets,1):map_units(b,[n],t,('节选正文与目录提供组织参考；' if n<=10 else '仅目录可见，缺失正文不假装已恢复；')+'法语内容为原创补充，替换英语专属声音和重音规律。')
 b='pronunciation-advanced'
 targets=['F01 F14','F01','M01','M01','F02','F02','M08','M08 P15','M08 M02','M03','M03 M07','M03 M07','M03 M07','M03 M07','M03 M07','M03 E01','M03 E01','M03 E01','M03 E01','M03 E01','M04 M05','M11','P04 M05','P13 P17','M01 F14','M02 P19','F03 M05','F03','F04 P15','F04 P15','M05 P17','F05','F06','F06','M03 E01','F06','F06','M11 G32','P20 M12','F06 M09','M12','F06','M12','M12 F07','M14 M12','M13 G39','M11','F10','F07','F07','F07','F08','F08','F11 F05','F11 F05','F12','F06 F11','F13','M13','F12 F13']
 for n,t in enumerate(targets,1):map_units(b,[n],t,'保留词组、会话、信息组织与正式场景的训练层次；英语固定词重音、弱式与成音节辅音改为法语节奏组、语流和对应发音知识。')
 b='oxford-idioms'
 targets=['I01','A03 I01','E01 G42','A02 E04','I02','I03','I04','I04','I05','I06','I07','I07 A19','I08 A22','I09','I10','I11','I11 A17','I12','I12','I10 I13','I13','I04 I13','I04 I13','I04 I13','I13','F11 I16','I14','I23 A16','I15','I15','I15 A16','I14','A24 I15','I16 F08','I16 E24','F11 I16','A17 F08','I16','I16 M11','I17','I18','I19','I19','I20','I20 A15','I03 A21','I21','I21','I22','I22','I23','I23','G42 A01','A18 I23','A03','A02 I02','A05','I24','I24','I24']
 for n,t in enumerate(targets,1):map_units(b,[n],t,'保留 I can…目标、人物/生活/事件/新闻/沟通/行为/语体/习语类型分区；相邻主题合并，以法语习语与实际使用边界重写。')
 assert len(SOURCE_MAP)==505

EXTRAS={
'G01':('区分存在与识别：il y a 表“有”，c’est 表“这是”；ce sont 常用于复数识别。',[('Il y a une pharmacie ici.','这里有一家药店。'),('C’est une pharmacie.','这是一家药店。')]),
'G19':('au cas où 通常接条件式，如 Au cas où il pleuvrait；comme si 常配 imparfait 或 plus-que-parfait 表仿佛情境。',[('Il parle comme s’il savait tout.','他说得好像自己什么都知道。')]),
'G20':('à moins que（除非）、pourvu que（只要/但愿）常接虚拟式。',[('Je viendrai à moins qu’il pleuve.','除非下雨，否则我会来。')]),
'G21':('使役 faire + 不定式表示让某动作发生，与被动不同：Je fais réparer ma voiture。',[('Je fais réparer ma voiture.','我让人修我的车。')]),
'G23':('其他常用结构：être habitué à faire 表习惯于；Il est inutile de faire 表做某事无益；voir/entendre + 宾语 + 不定式可描述感知到的动作。',[('Je suis habitué à travailler tôt.','我习惯早早工作。'),('Il est inutile de répéter.','重复没有用。'),('Je vois les enfants jouer.','我看见孩子们玩耍。')]),
'G27':('复合名词不照搬英语 noun+noun；法语常用 de 或 à 连接，如 une salle de réunion。复数需按词组核对。',[('C’est une salle de réunion.','这是一间会议室。')]),
'G28':('所属关系也可用 de：le livre de Léa；un ami à moi 表“我的一个朋友”，重读代词形式见 G32。',[('Le livre de Léa est ici.','莉娅的书在这里。'),('C’est un ami à moi.','这是我的一个朋友。')]),
'G32':('不定量与全称还包括 quelques（几个）、chacun（每个，单数变位）、les deux（两者）、ni…ni（既不…也不）。',[('Chacun a une clé.','每个人有一把钥匙。'),('Je ne prends ni thé ni café.','我既不喝茶也不喝咖啡。')]),
'G34':('补充性关系从句可用逗号隔开，仍使用相应关系词；它补充而非限制先行词范围。',[('Ma sœur, qui vit à Lyon, arrive demain.','我的姐妹住在里昂，她明天到。')]),
'G35':('fatigant 描述令人疲倦，fatigué 描述感到疲倦；形容词也有接口，如 content de、prêt à。comme 可用于比拟。',[('Ce travail est fatigant ; je suis fatigué.','这工作累人；我累了（男性说话者）。')]),
'G36':('assez 表足够，trop 表过量：assez grand pour entrer、trop lourd pour être porté。它们不是普通比较级，需要结合目的结构。',[('Ce sac est trop lourd pour moi.','这个包对我来说太重了。')]),
'G37':('程度与时间副词还包括 très、si、tellement、assez、plutôt、déjà、encore、pas encore；même 可表示“甚至”或“连…也”，位置取决于突出对象。',[('Je n’ai pas encore fini.','我还没做完。'),('Même Léa est venue.','连莉娅都来了。')]),
'G38':('comme 可在从句前引出背景原因，如 Comme il pleut, je reste；不可把它与所有英语 as 用法等同。',[('Comme il pleut, je reste ici.','因为下雨，我留在这里。')]),
'G40':('交通方式常用 en bus/en train/à pied；乘坐具体交通工具可用 prendre le bus/le train。',[('Je vais au travail à pied.','我步行去上班。')]),
'G41':('pendant 接名词，pendant que 接完整从句；à la fin de 指某过程末尾，finalement 常表示最终结果。',[('Je lis pendant qu’elle cuisine.','她做饭时我读书。'),('À la fin du cours, nous révisons.','课末我们复习。')]),
'G42':('再记几组：demander quelque chose à quelqu’un，protéger quelqu’un de quelque chose，parler de/à，compter sur。介词选择看词组与实际意思。',[('Je compte sur toi.','我依靠你。')]),
'E27':('人生阶段常用 grandir、se marier、prendre sa retraite；阶段本身和叙述时态分开学习。',[('Mon père a pris sa retraite.','我父亲退休了。')]),
'I13':('体育中另有 marquer un but（进球）、faire match nul（打平）、remporter la victoire（获胜）；这些是常用搭配，不全是比喻。',[('Les équipes ont fait match nul.','两队打平了。')]),
'I15':('descendre dans la rue 可指走上街头示威，需按语境区分普通移动与公共行动。',[('Les manifestants sont descendus dans la rue.','示威者走上街头。')]),
'I23':('新闻和正式文本中可见 ouvrir une enquête（展开调查）、commettre une infraction（违法违规）、porter plainte（提出控诉/报案）。这里只解释词组，不判断具体案件。',[('La police a ouvert une enquête.','警方展开了调查。')])}
REFS={
 'grammar':[('Tex’s French Grammar — 大学语法索引','https://www.laits.utexas.edu/tex/pr/'),('OQLF — 法语语法与语言资料','https://vitrinelinguistique.oqlf.gouv.qc.ca/')],
 'expressions':[('CNRTL — 核对词义与搭配','https://www.cnrtl.fr/definition/'),('FRANCOMANE — 第二语言法语资源','https://francomane.ccdmd.qc.ca/')],
 'advanced-expressions':[('CNRTL — 核对词义与搭配','https://www.cnrtl.fr/definition/'),('OQLF — 语体与表达资料','https://vitrinelinguistique.oqlf.gouv.qc.ca/')],
 'idioms':[('Dictionnaire de l’Académie française — 词义与表达查询','https://www.dictionnaire-academie.fr/'),('CNRTL — 表达用例查询','https://www.cnrtl.fr/definition/')],
 'pronunciation':[('OQLF — 元音与 IPA 约定','https://vitrinelinguistique.oqlf.gouv.qc.ca/22205/la-prononciation/notions-de-base-en-phonetique/les-voyelles-phonetiques'),('OQLF — 禁止联诵的环境','https://vitrinelinguistique.oqlf.gouv.qc.ca/23552/la-prononciation/liaisons/contextes-de-liaisons-interdites'),('Français interactif — 语音符号与真实音频资源','https://www.laits.utexas.edu/fi/html/pho/02.html')]}

def section(book,n):
 ranges={
 'grammar':[(8,'基础句子'),(14,'过去与持续'),(20,'将来、条件与语气'),(24,'动作与复杂句'),(28,'名词与限定词'),(34,'代词与关系从句'),(39,'描述与连接'),(42,'时间、地点与搭配')],
 'expressions':[(4,'学习表达'),(11,'核心动词'),(16,'介词与方向'),(20,'概念'),(25,'交流功能'),(28,'生活场景')],
 'advanced-expressions':[(6,'搭配、语体与隐喻'),(10,'抽象概念'),(16,'交流与决策'),(24,'工作、生活与世界')],
 'pronunciation-basic':[(16,'声音与拼写'),(20,'音节、连接与语调')],
 'pronunciation-connected':[(8,'音节、词组与语流'),(15,'会话与训练')],
 'pronunciation-fluent':[(4,'口音与自然语流'),(10,'会话中的信息组织'),(15,'正式陈述与整合')],
 'idioms':[(1,'学习习语'),(6,'人物与行为'),(12,'日常生活'),(13,'事件'),(15,'新闻与社会'),(16,'沟通'),(21,'态度与选择'),(23,'语体'),(24,'习语类型')]}
 return next(label for end,label in ranges[book] if n<=end)

def write_curriculum():
 make_mapping()
 records=sorted(SOURCE_MAP.values(),key=lambda r:(list(SOURCE_COUNTS).index(r['source_book']),r['source_unit']))
 for rec in records:
  b,n=rec['source_book'],rec['source_unit']
  rec['source_contents']=f'../sources/{b}/contents.md'
  rec['status']='framework-adapted-original-content'
  rec['source_body_available']=not(b=='pronunciation-introduction' and n>10)
  rec['pdf_page']={'grammar':14,'phrasal-verbs':9,'phrasal-verbs-advanced':9,'pronunciation-elementary':11,'pronunciation-advanced':7}.get(b)
  if rec['pdf_page']:rec['pdf_page']+=2*(n-1)
  if b=='pronunciation-introduction':rec['pdf_page']=9+n if n<=10 else None
 curriculum=[]
 for slug,prefix,count,zh,fr,category,description in BOOKS:
  folder=ROOT/'french'/slug;folder.mkdir(parents=True,exist_ok=True)
  lines=(ROOT/'scripts/content'/f'{slug}.txt').read_text().splitlines()
  assert len(lines)==count,(slug,len(lines),count)
  for n,line in enumerate(lines,1):
   fields=line.split('§');assert len(fields)==9,(slug,n,len(fields))
   lid,level,title,goal,rule,analogy,exblob,qblob,task=fields
   assert lid==f'{prefix}{n:02}'
   examples=[tuple(v.split('→',1)) for v in exblob.split(';;')]
   if lid in EXTRAS:
    extra,more=EXTRAS[lid];rule+='\n\n'+extra;examples+=more
   quizzes=[]
   for qn,q in enumerate(qblob.split(';;'),1):
    prompt,correct,w1,w2,reason=q.split('¦')
    choices=[correct,w1,w2];random.Random(lid+str(qn)).shuffle(choices)
    quizzes.append({'prompt':prompt,'choices':choices,'answer':choices.index(correct),'reason':reason})
   prereq=[f'{prefix}{n-1:02}'] if n>1 else {'G':['P01'],'E':['G01'],'A':['E01','G23'],'P':[],'M':['P17','P18','P19'],'F':['M03','M06'],'I':['E01','E02']}.get(prefix,[])
   meta={'id':lid,'title':title,'book':slug,'book_title':zh,'book_fr':fr,'category':category,'level':level,'section':section(slug,n),'prerequisites':prereq,'minutes':8,'status':'original-edited-draft','source_units':[f'{r["source_book"]}:{r["source_unit"]}' for r in records if lid in r['targets']]}
   refs=REFS['pronunciation' if prefix in 'PMF' else slug]
   if lid in ['G20','G39']:refs=refs+[('OQLF — 连词与语式','https://vitrinelinguistique.oqlf.gouv.qc.ca/24238/la-grammaire/le-verbe/modes/subjonctif/subjonctif-ou-indicatif-apres-les-subordonnants-composes'),('加拿大语言门户 — après que 的规范差异','https://nos-langues.canada.ca/fr/cles-de-la-redaction/apres-que-indicatif-ou-subjonctif')]
   if lid in ['P09','F14']:refs=refs+[('OQLF — 塞擦化','https://vitrinelinguistique.oqlf.gouv.qc.ca/24467/la-prononciation/phenomenes-phonetiques/laffrication')]
   md='---\n'+json.dumps(meta,ensure_ascii=False,indent=2)+'\n---\n\n'+f'# {lid} · {title}\n\n## 学完能做什么\n\n{goal}\n\n## 讲解\n\n{rule}\n\n## 给小朋友的比喻\n\n{analogy}\n\n## 例句\n\n'
   md+='\n'.join(f'- {a} → {b}' for a,b in examples)+'\n\n## 练习\n\n'
   for qn,q in enumerate(quizzes,1):
    md+=f'### {qn}. {q["prompt"]}\n\n'+'\n'.join(f'- {chr(65+i)}. {c}' for i,c in enumerate(q['choices']))+'\n\n'
   md+='## 答案与原因\n\n'+'\n'.join(f'{i}. {chr(65+q["answer"])} — {q["reason"]}' for i,q in enumerate(quizzes,1))
   md+=f'\n\n## 一分钟应用\n\n{task}\n\n## 相关学习\n\n'+ ('、'.join(prereq) or '从本课开始')+'\n\n## 参考资料\n\n'
   md+='\n'.join(f'- [{label}]({url})' for label,url in refs)+'\n\n> 例句、练习与比喻均为本项目原创编写；参考链接用于核对规则或进一步查询，不表示逐句摘自链接。等级为教学建议。\n'
   (folder/f'{lid}.md').write_text(md)
   curriculum.append(meta)
  toc=[f'# {zh}\n\n*{fr}*\n\n{description}\n\n> 原创编辑初稿；原书知识点已合并改编，不是原书逐句翻译。\n']
  for m in curriculum:
   if m['book']==slug:toc.append(f'- [{m["id"]} · {m["title"]}]({m["id"]}.md) · {m["level"]} · {m["section"]}')
  (folder/'README.md').write_text('\n'.join(toc)+'\n')
 coverage={'description':'编号级框架对应，不是逐句、逐题或原书音频覆盖声明。法语主题合并与原创补充均见 adaptation。','source_counts':SOURCE_COUNTS,'records':records}
 (ROOT/'french/coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2))
 (ROOT/'french/catalogue.json').write_text(json.dumps(curriculum,ensure_ascii=False,indent=2))
 md=['# 原书单元 → 法语教材：框架对应表','','七份来源目录共有 505 个编号单元，对应到 168 个原创法语单元。这里证明编号与板块均有去向，不意味着每一条英文词汇、原题或录音都被复刻。英语专属结构被法语表达功能替代；重复主题合并。Introduction 的 11–60 单元仅目录可见，其法语内容标为原创补充。','','| 来源 | 单元 | 法语目标 | 改编说明 |','|---|---:|---|---|']
 index={m['id']:m for m in curriculum}
 for r in records:
  links='、'.join(f'[{lid}]({index[lid]["book"]}/{lid}.md)' for lid in r['targets'])
  md.append(f'| [{r["source_book"]}](../sources/{r["source_book"]}/contents.md) | {r["source_unit"]} | {links} | {r["adaptation"]} |')
 (ROOT/'french/coverage.md').write_text('\n'.join(md)+'\n')
 print(f'Authored {len(curriculum)} Markdown lessons; {len(records)} source unit mappings.')

if __name__=='__main__':write_curriculum()
