"""Build editable offline tutoring annotations; original 50-lesson annotations win.
Generated IPA is explicitly tagged as synthesis reference, not human-audited IPA.
"""
from pathlib import Path
import concurrent.futures, json, re, subprocess, sys
from build_site import load_library, ROOT
from pronunciation import words, norm
CONTENT = ROOT / 'scripts/content'

def read_glosses():
    result = {}
    for line in (CONTENT/'site-word-meanings.txt').read_text().splitlines():
        if not line or line.startswith('#'): continue
        keys, meaning = line.split('=', 1)
        for key in keys.split(','): result[key.strip()] = meaning
    return result

def reason(word, ipa):
    out = []
    if "'" in word:
        out.append('撇号表示前面的小词发生省音，省去的元音不再单独读；撇号前后的部分合成这一张词卡。')
    for letters, sound, text in [('eau','o','eau 在这个词里合成一个 /o/。'),('ou','u','ou 在这个词里读 /u/，是后圆唇音。'),('oi','wa','oi 在这个词里滑成 /wa/，不逐字读 o、i。'),('qu','k','qu 在这个词里读 /k/，u 不另发元音。'),('ch','ʃ','ch 在这个词里读 /ʃ/，持续送气。'),('gn','ɲ','gn 在这个词里读 /ɲ/，不拆成 g 和 n。'),('tion','sjɔ̃','tion 在这个词里接成 /sjɔ̃/，最后是鼻元音。'),('ç','s','ç 在这里读 /s/。'),('é','e','é 对应较闭的前元音 /e/。'),('è','ɛ','è 对应较开的前元音 /ɛ/。')]:
        if letters in word and sound in ipa: out.append(text)
    for sound in ['ɛ̃','ɑ̃','ɔ̃','œ̃']:
        if sound in ipa: out.append(f'/{sound}/ 是鼻元音：元音带鼻化，不在后面再拼一个清晰的 n 或 m。')
    if word.endswith('er') and ipa.endswith('e'): out.append('词尾 er 这里读 /e/，r 不另外发声。')
    if word.endswith('ez') and ipa.endswith('e'): out.append('词尾 ez 这里读 /e/，不是读字母 e、z。')
    if word.endswith('ent') and word in {'augmentent','arrivent','parlent','diminuent','découvrent','préparent','imaginent','s’ouvrent','s\'ouvrent','devinent','prêtent','reprennent','donnent','jouent','retrouvent','lisent','téléphonent'}:
        out.append('这里是动词第三人称复数，词尾 ent 不另发音，不读成鼻音 /ɑ̃/。')
    elif word.endswith('e') and not ipa.endswith('ə') and len(word)>2:
        out.append('词尾书写 e 在这份独读标注中不单独成一个音节；自然语流和地区口音可能保留弱 e。')
    if word.endswith(('s','x','t','d')) and not ipa.endswith(('s','z','t','d')):
        out.append('这个词的最后一个书写辅音在此独读形式里不响；句中是否联诵要另外看连接标记，不能逢元音就补音。')
    if '人名' in GLOSSES.get(word,'') or '角色名' in GLOSSES.get(word,''):
        out.append('这是专名，实际读法以本人／角色录音为准；这里显示法语合成参考读法。')
    if not out: out.append(f'先按 /{ipa}/ 对照声音；书写字母数量不等于音节数量，口形提示见下方，点击单词慢读后再听句中读法。')
    return ' '.join(out[:4])

PICTURE_RULES=[
 ('钱|欧元|预算|价格|账户|零钱|储蓄|费用','money'),('火车|地铁','train'),('车|驾驶','car'),('飞机|飞船','boat'),('水|雨|汤','water'),('咖啡|茶|杯|果汁','cup'),('面包|馅饼|蛋糕|饼干','bread'),('奶|奶酪','milk'),('鱼','fish'),('蛋','egg'),('猫','cat'),('人名|角色名|先生|女士|他|她|护士|教师|学生|同事|邻居|家庭|兄弟|姐妹|父亲','person'),('书|词典|小说|报纸|文章|页|课|词汇表','book'),('说|话|表达|意见|问|答|消息|评论','voice'),('时间|时刻|小时|分钟|晚|早|迟','clock'),('年|月|星期|日历|天|周','calendar'),('房|办公室|客厅|楼|城堡','house'),('路|街|途径|方向','road'),('工作|职业|工场','work'),('吃|菜|食物|沙拉|水果|饭|点心','food'),('写|笔|画|字母','write'),('爱|喜欢|高兴|幸福|喜悦','thanks'),('听|耳','ear'),('眼|看|照片|图片','eye'),('手|给|帮助','give'),('去|走|来|回|出发','go'),('电脑|程序|软件|录音|电话','phone'),('睡|休息','sleep'),('害怕|担心','fear'),('决定|选择|或','choice'),('否定|没有|不','no'),('大|高|长','big'),('小|少','small'),('颜色|白色|蓝色|棕色','color'),('植物|树|森林|花','tree'),('关|打开','close'),('窗','window'),('正确|明白|成功|完成','check'),('重要|要点|目标','star'),('玩|比赛|游戏','play'),('尝试|做|动作|进行','action')]
def picture(meaning):
    for pattern, group in PICTURE_RULES:
        if re.search(pattern,meaning): return group
    return 'concept'

# These are playful Chinese sound hooks, not transcriptions. They intentionally
# cannot represent French nasal vowels, consonant clusters or Mandarin tones.
HOOKS={'je':'热','j’ai':'杰','j\'ai':'杰','tu':'玉兔','vous':'武','nous':'努','il':'伊勒','ils':'伊勒','elle':'艾勒','elles':'艾勒','le':'勒','la':'拉','les':'雷','de':'德','des':'德','un':'昂','une':'玉讷','est':'诶','et':'诶','pas':'帕','ne':'呢','ce':'瑟','cette':'塞特','ces':'塞','ça':'萨','on':'翁','en':'昂','dans':'当','pour':'普尔','avec':'阿韦克','qui':'基','que':'克','quoi':'夸','oui':'喂','non':'农','bien':'别昂','très':'特蕾','plus':'普吕','petit':'珀蒂','petite':'珀蒂特','café':'咖啡','quinze':'干兹','seize':'塞兹','euros':'油螺','vingt':'万','yeux':'约','tête':'泰特','billet':'比耶','argent':'阿让','coûte':'库特','jette':'热特','fenêtres':'弗奈特','côté':'科泰'}
CV={
'p':['帕','皮','普','皮玉','佩','派','波','坡','珀','珀','珀','庞','潘','蓬'],
'b':['巴','比','布','比玉','贝','拜','波','博','伯','伯','伯','邦','班','蹦'],
't':['塔','提','兔','玉特','泰','泰','托','托','特','特','特','唐','坦','通'],
'd':['达','迪','杜','迪玉','戴','戴','多','朵','德','德','德','当','丹','东'],
'k':['卡','基','库','库玉','凯','凯','科','科','克','克','克','康','干','孔'],
'ɡ':['嘎','吉','古','谷玉','盖','盖','戈','果','格','格','格','冈','甘','公'],
'f':['法','菲','夫','弗玉','费','菲','佛','佛','弗','弗','弗','芳','梵','丰'],
'v':['瓦','维','武','武玉','韦','韦','沃','沃','弗','弗','弗','旺','万','翁'],
's':['萨','西','苏','叙','塞','塞','索','索','瑟','瑟','瑟','桑','珊','松'],
'z':['扎','兹','祖','许兹','泽','泽','佐','佐','泽','泽','泽','藏','赞','宗'],
'ʃ':['沙','希','舒','叙','谢','谢','绍','硕','舍','舍','舍','商','山','雄'],
'ʒ':['扎','吉','茹','玉茹','热','热','若','若','热','热','热','让','然','荣'],
'l':['拉','莉','卢','吕','雷','莱','洛','洛','勒','勒','勒','朗','兰','隆'],
'ʁ':['哈','里','胡','吕尔','黑','黑','霍','霍','赫','赫','赫','杭','然','洪'],
'm':['马','米','姆','缪','梅','梅','莫','莫','么','么','么','芒','曼','蒙'],
'n':['纳','尼','努','女','内','奈','诺','诺','讷','讷','讷','囊','南','农'],
'j':['雅','伊','优','玉','耶','耶','哟','哟','耶','耶','耶','央','扬','雍'],
'w':['瓦','威','乌','玉','韦','韦','沃','沃','沃','沃','沃','汪','万','翁'],
'ɥ':['玉阿','玉伊','玉乌','玉','玉耶','玉耶','玉哦','玉哦','玉厄','玉厄','玉厄','玉昂','玉安','玉翁']}
VOWELS=['a','i','u','y','e','ɛ','o','ɔ','ə','ø','œ','ɑ̃','ɛ̃','ɔ̃']
VHOOK=['阿','伊','乌','玉','诶','诶','欧','哦','呃','厄','厄','昂','安','翁']
C=[('ʃ','什'),('ʒ','日'),('ʁ','尔'),('l','勒'),('s','斯'),('z','兹'),('t','特'),('d','德'),('k','克'),('ɡ','格'),('f','夫'),('v','夫'),('p','普'),('b','布'),('m','姆'),('n','恩'),('ɲ','涅'),('ŋ','嗯'),('j','伊'),('w','乌'),('ɥ','玉')]
CMAP=dict(C)
def hook(word,ipa):
    if word in HOOKS:return HOOKS[word]
    ipa=ipa.replace('œ̃','ɛ̃').replace('ɑ','a') if 'ɑ̃' not in ipa else ipa.replace('œ̃','ɛ̃')
    tokens=re.findall(r'[ɑɛɔœ]̃|.',ipa)
    pending=[];out=[]
    for sound in tokens:
        if sound in VOWELS:
            v=VOWELS.index(sound)
            if pending:
                out.extend(CMAP.get(c,'') for c in pending[:-1]);out.append(CV.get(pending[-1],VHOOK)[v]);pending=[]
            else:out.append(VHOOK[v])
        elif sound in CMAP:pending.append(sound)
    out.extend(CMAP.get(c,'') for c in pending)
    return ''.join(out) or word

GLOSSES=read_glosses()

def phonemize(word):
    ipa=subprocess.run(['espeak-ng','-q','-v','fr-fr','--ipa',word],text=True,capture_output=True,check=True).stdout.strip()
    ipa=re.sub(r'\([a-z-]+\)','',ipa).replace('ɜ','œ').replace('ɐ','a').replace('ɹ','ʁ').replace('g','ɡ')
    ipa=re.sub(r'[\sˈˌːˑ\-_]','',ipa)
    return word, ipa

OVERRIDES={'t-shirt':'tiʃœʁt','l-i-n':'ɛliɛn','eu':'y','cv':'seve','j\'y':'ʒi','août':'u','vingt':'vɛ̃','clef':'kle','dos':'do','agathe':'aɡat'}

def main():
    lessons=load_library(ROOT/'french')
    old={}
    for row in (CONTENT/'pronunciation-words.txt').read_text().splitlines():
        if row and not row.startswith('#'):
            word,ipa,zh,pic,why=row.split('|');old[word]=dict(ipa=ipa,zh=zh,picture=pic,reason=why,ipa_source='authored')
    vocabulary={norm(w) for l in lessons for e in l['examples'] for w in words(e['fr'])}
    missing=vocabulary-set(old)-set(GLOSSES)
    if missing:raise ValueError(f'missing meanings: {sorted(missing)}')
    cache_path=CONTENT/'site-ipa-cache.json'
    cache=json.loads(cache_path.read_text()) if cache_path.exists() else {}
    todo=sorted(vocabulary-set(old)-set(cache))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        cache.update(pool.map(phonemize,todo))
    cache.update(OVERRIDES)
    cache_path.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+'\n')
    lex=dict(old)
    for word in sorted(vocabulary-set(old)):
        ipa=cache[word]
        if not ipa:raise ValueError(f'empty IPA {word}')
        zh=GLOSSES[word]
        lex[word]=dict(ipa=ipa,zh=zh,picture=picture(zh),reason=reason(word,ipa),ipa_source='eSpeak NG synthesis reference')
    # High-frequency context-sensitive words keep meanings broad outside the original lessons.
    lex['a']['zh']='有；过去时助动词（avoir 的变位）'
    lex['son']['zh']='他／她的；声音（依句子而定）'
    lex['sommes']['zh']='我们是／在；过去时助动词'
    lex['en']['zh']='在……中；其中／一些（代词）'
    lex['le']['zh']='阳性单数冠词；它／他（宾语代词）'
    lex['la']['zh']='阴性单数冠词；它／她（宾语代词）'
    corrections=json.loads((CONTENT/'site-ipa-corrections.json').read_text())
    for word,values in corrections.items():lex[word].update(values)
    for word,data in lex.items():data['hook']=hook(word,data['ipa'])
    (CONTENT/'site-words.json').write_text(json.dumps(lex,ensure_ascii=False,indent=2)+'\n')
    annotations={}
    memories=json.loads((CONTENT/'sentence-memories.json').read_text())
    original={'P'+str(n).zfill(2) for n in range(1,21)}|{'M'+str(n).zfill(2) for n in range(1,16)}|{'F'+str(n).zfill(2) for n in range(1,16)}
    for lesson in lessons:
        if lesson['id'] in original:continue
        examples=[]
        for i,e in enumerate(lesson['examples']):
            ts=words(e['fr']);keys=list(map(norm,ts))
            entry=memories[f'{lesson["id"]}:{i+1}']
            if entry['fr']!=e['fr'] or entry['zh']!=e['zh']:
                raise ValueError('Review the sentence memory before regenerating: '+lesson['id'])
            mnemonic=f'声音梗：{entry["sound"]} 脑内电影：{entry["movie"]}'
            # Rule cues use explicit word annotations, separately from the joke.
            focus=[]
            for key in dict.fromkeys(keys):
                data=lex[key]
                if len(key)>2 and ('鼻元音' in data['reason'] or re.search(r'qu|ch|gn|ou|oi|é|è|tion',key)):
                    focus.append(f'{ts[keys.index(key)]} /{data["ipa"]}/：'+data['reason'].split('。')[0]+'。')
                if len(focus)==3:break
            rule=' '.join(focus) or '先把每个词点开慢读，再按节奏组合；词尾是否连接看原句标记，不照汉字声调或额外添加音节。'
            examples.append(dict(fr=e['fr'],mnemonic=mnemonic,rule_memory=rule))
        annotations[lesson['id']]=examples
    (CONTENT/'site-tutor.json').write_text(json.dumps(annotations,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'words':len(lex),'new_lesson_annotations':len(annotations),'examples':sum(map(len,annotations.values()))}))
if __name__=='__main__':main()
