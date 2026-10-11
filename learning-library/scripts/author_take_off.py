"""Original Chinese companions, in the order of the scanned Oxford book.
Run from anywhere; preserves imported source text unchanged.
"""
from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parents[1]
COURSE=[]
def add(title,goal,explanation,analogy,examples,quiz,application):
 COURSE.append(dict(title=title,goal=goal,explanation=explanation,analogy=analogy,examples=examples.strip().split('\n'),quiz=quiz,application=application))

add('初次开口：问候、点单与价格','分清见面和道别，用礼貌语点一份餐饮，读出1–30并询价。',
'''原书1.1（印刷2–3页）从 Bonjour、Bonsoir、Salut 到 Au revoir、À demain、Bonne nuit 区分交际目的：bonne nuit 是就寝前的祝愿，不能当作一般晚间见面问候。Ça va? 语调上扬是询问，Ça va. 降调是回答。对陌生人可用 Monsieur、Madame；书中 Mademoiselle 是原有称谓，不必把婚姻状况当作称呼前提。

1.2（4–5页）点单可先说食物，再加 s’il vous plaît；merci 回应服务，d’accord 表同意，bon appétit 祝人用餐愉快。名词的语法性别决定 un/une、le/la；元音或哑音 h 前 le/la 变 l’，但 un/une 不照此缩写。学词时把冠词一起记。

1.3（6–7页）C’est combien? 问价格，ça fait 表合计。1–16先记，17–19由 dix 加个位组成，21是 vingt et un，22–29接 vingt-，30是 trente。1.4（8–9页）菜单用 nature 表原味、service compris 表已含服务；原菜单与对话出现欧元及法郎，按原书情境阅读，不能用它推断今日价格。

1.5（10–11页）咖啡馆故事把点单、电话 Allô?、插话 Excusez-moi、à tout à l’heure 与 à demain 放在一起；读文字稿时先标谁向谁说话，再判断下次见面时间。12–14页 Test/Summary 回收礼貌语、性别和数字；原录音未提供，读稿正确不等于完成听辨。''',
'把玩具咖啡馆分成“进门”“点单”“离开”三个站，娃娃到站时选一句话；红蓝篮子分别装 une salade 和 un café。篮子颜色只是记忆标签，食物本身没有男女之分，Salut 也不能只固定在一个站。',
'''Bonjour, Madame Chen. → 陈女士，您好。
Bonsoir, Monsieur Martin. → 马丁先生，晚上好。
Une soupe et un thé, s’il vous plaît. → 请给我一份汤和一杯茶。
Le gâteau, c’est combien ? → 这块蛋糕多少钱？
Deux jus, ça fait huit euros. → 两杯果汁合计八欧元。
Bonne nuit, Léa. À demain ! → 晚安，莱娅。明天见！''',
[('晚上刚进咖啡馆，应说哪一句？',['Bonne nuit.','Bonsoir.','À demain.'],1,'Bonsoir 用于晚间见面；bonne nuit 是就寝祝愿，à demain 是道别。'),('想要“一份沙拉”，选哪一项？',['un salade','le une salade','une salade'],2,'salade 为阴性单数，用 une；冠词不能叠加。'),('二十一应如何表达？',['vingt et un','vingt-onze','deux-un'],0,'21是 vingt et un；vingt-onze 和 deux-un 都不是21的表达。')],
'自画一张包含汤、茶、蛋糕的原创菜单；演进门问候、点两项、询价和道别四轮，合计用30以内数字。')

add('城里问路：位置、方向与门牌','询问城市设施，按地标给两步路线，读31–69门牌。',
'''2.1（16–17页）先列设施再定位置：il y a 可接单数或复数，表示“有”；où est/où sont 则问已知地点在哪。复数通常加-s，feu→feux 是例外；le/la/l’→les，un/une→des。les toilettes 在本课厕所义用复数。

2.2（18–19页）问路用 Pour aller à… ?，指路用 tournez、continuez、allez，配 à gauche/à droite/tout droit、après、jusqu’à。à+le→au、à+les→aux；de+le→du、de+les→des；à la/à l’及de la/de l’不融合。en face de 表对面，à côté de 表旁边。命令式通常省主语：对陌生人用 vous 形式 tournez；熟人用 tourne；包含自己用 allons。

2.3（20–21页）trente/quarante/cinquante/soixante 加个位组成31–69，逢一用 et un。être 的现在时是 suis、es、est、sommes、êtes、sont；c’est 常用于识别或定位，不代替所有主语的 être。

2.4（22–23页）地图阅读要先找起点、街名与参照物，再检验“对面”“旁边”，不能凭OCR乱序推断图示。2.5（24–25页）故事重复办公室地址与路线，适合练复述确认：先门牌、再车站转弯、最后桥与银行。26–28页测试/总结综合数字、缩合和路线。''',
'用积木摆车站、桥和银行，让玩具车按“到桥左转”走；把 à 与 le 两块扣成 au。真实地图方向取决于出发位置，积木合扣也只适用于列出的冠词组合。',
'''Il y a une pharmacie près de la gare. → 车站附近有一家药店。
Où sont les toilettes ? → 厕所在哪里？
Continuez tout droit jusqu’au pont. → 一直走到桥边。
Tournez à gauche après le musée. → 过了博物馆后左转。
La banque est en face du cinéma. → 银行在电影院对面。
C’est au numéro cinquante et un. → 就在五十一号。''',
[('Allez jusqu’___ feux.',['à les','aux','au'],1,'feux 为复数，à+les 缩合为 aux；au 只配阳性单数。'),('已知有一家银行，询问它的位置应选？',['Où est la banque ?','Il y a une banque.','Combien de banques ?'],0,'où est 定位已知银行；il y a 是陈述存在，combien 问数量。'),('“电影院旁边”正确表达？',['à côté de le cinéma','à côté la cinéma','à côté du cinéma'],2,'cinéma 是阳性，de+le 必须缩合 du。')],
'画三个地点，标51、43、62号；从家到车站写两条命令式，再用一句 il y a 介绍沿途设施。')

add('时间和日程：约在星期几几点','读时间和70–100，区分一次安排与每周习惯，提问并否定。',
'''3.1（30–31页）Il est… 报当前时间，à… 指事件发生时间；une heure、deux heures，midi/minuit 不加 heures。et quart 加十五分，moins le quart 距下一小时十五分；heure(s) et demie 与 midi/minuit et demi 性别不同。规则-er现在时词尾-e/-es/-e/-ons/-ez/-ent；on 指我们时仍用单数动词。

3.2（32–33页）lundi 是本次星期一，le lundi 常是每周一；du lundi au vendredi 表从周一到周五。70按60+10，71为soixante et onze，80为quatre-vingts，后接个位去-s：quatre-vingt-un，90按80+10。quel/quelle/quels/quelles 与其修饰名词的性数一致，问 quelle heure、quels jours。

3.3（34–35页）规则-ir以finir为型：finis、finis、finit、finissons、finissez、finissent，不能套给所有-ir动词。问题可用升调、est-ce que 或倒装；ne…pas 把变位动词夹住，元音前n’。口语省ne可识别，练书写保留。

3.4（36–37页）电视节目表先看频道、起止时间、类型，再给选择理由；跨午夜时不要把结束时间误当更早的同一天。3.5（38–39页）故事不断提议又因工作、课程或运动改期，用 ce n’est pas possible 加原因再给新日期。40–42页测试/总结同时检验动词、星期、数字和约会；按纸面材料练，不假装听过CD。''',
'把一周画成七格游戏棋盘，用小钟摆约会；贴着 le 的星期卡表示每周重复。棋盘只能帮助理解一次与习惯，真正时间也可能用24小时制，不能把晚上九点永远写成9点而不说明。',
'''Il est six heures et demie. → 现在六点半。
Le cours commence à neuf heures moins le quart. → 课程八点四十五开始。
Je travaille mercredi. → 我这周三工作。
Je ne travaille pas le mercredi. → 我每周三不工作。
Nous finissons à dix-huit heures. → 我们十八点结束。
Quel jour est libre ? → 哪一天有空？
C’est le numéro quatre-vingt-douze. → 这是九十二号。''',
[('每周一都工作应选？',['Je travaille le lundi.','Je travaille un lundi.','Je travaille lundi soir seulement.'],0,'le lundi 标记每周重复；un lundi 是某个星期一，seulement 限定一次。'),('7:45用口语时钟怎样说？',['sept heures et quart','huit heures moins le quart','huit heures et quart'],1,'离八点还差一刻是7:45；另两项是7:15与8:15。'),('Nous ___ à midi. (finir)',['finit','finissent','finissons'],2,'规则finir的nous形式是finissons；finit配单数第三人称，finissent配复数第三人称。')],
'写一个星期三的真实日程，用开始/结束时间、一个否定句与一个提议句约朋友。')

add('复习一：把咖啡馆、地图和日程串起来','综合原书1–3单元完成点单、指路和改约，判断错误属于词汇还是结构。',
'''Review 1（43页）词汇先按称呼、问候、食物饮料、建筑分类，再读日程表；看到星期和时间时分清活动与人物，不能只认出单词就判断整句。

44页 Grammar and usage 把 à/de 缩合与路线连起来：jusqu’aux feux、à la gare、à côté du café；每次先确定后面名词是le、la、l’还是les。动词填空要先圈主语：tu…-es、nous…-ons、vous…-ez；finir的nous为-finissons。数字运算需先算数值再写词，区分soixante、quatre-vingts及后续个位。

45页 Listening 用“旧友约见”和“新工作日程”同时检验事实、地点和时间；缺原音频时可以整理待确认栏、阅读现有不完整题干，不能从提示强行填完空。Speaking 的朗读可自录练节奏，但不声称已与原录音比较。

46页口语任务从问候、拒绝、换日期，到问餐馆位置、约时间，最后读取餐馆广告中的地址、电话、开放日与午晚营业时段。完成一次真实对话时，至少确认地点及日期、时间两项；如果卡住，回到T01礼貌语、T02路线、T03日程再练。''',
'安排一次玩偶聚餐：先用菜单卡选餐，再走积木路线，最后在星期棋盘放小钟。三种卡要一起看；游戏成功只说明能读和说这些句子，不证明听懂了没有播放的录音。',
'''Salut, Zoé ! Tu vas bien ? → 嗨，佐伊！你好吗？
On déjeune ensemble samedi ? → 周六一起吃午饭吗？
Samedi, je travaille jusqu’à midi. → 周六我工作到中午。
Alors, à midi et demi ? → 那么十二点半怎么样？
Le restaurant est à côté de l’église. → 餐馆在教堂旁边。
Tournez à droite aux feux. → 在红绿灯处右转。''',
[('好友提议周六上午见面，你工作到中午，合理回应？',['D’accord, à dix heures.','Je travaille jusqu’à midi. À midi et demi ?','Bonne nuit, musée.'],1,'先说明冲突再提中午后的时间；十点仍冲突，末项不是有效回应。'),('à côté ___ jardins',['des','aux','le'],0,'à côté de 后de+les缩合des，aux属于à+les。'),('缺CD，原听力填空怎样处理？',['凭故事角色编答案','全部填最常见词','记为待听，先核可见文字'],2,'不可把推测冒充听力证据；可见文字练习与待听题应分别记录。')],
'给朋友设计聚餐方案：一句邀请、一句说明空闲时间、两步指路、一句确认；隔一天不看稿复述。')

add('住宿：预订、登记与介绍房间','拼名字、预订酒店或营位，理解设施、月份、楼层和较大数字。',
'''4.1（48–49页）登记先说 j’ai une réservation，再用 je m’appelle 与 ça s’écrit 拼姓名；complet 表住满。avoir现在时ai/as/a/avons/avez/ont；s’appeler有me/te/se/nous/vous/se，appelle与appelons/appelez的单双l不同。百位cent在整倍数末尾加-s，后有数字去-s；mille不加-s。

4.2（50–51页）营地询价区分par jour、par personne、车辆和营位，gratuit为免费。月份janvier至décembre小写，en juillet 表在七月。规则-re以vendre为型：vends/vends/vend/vendons/vendez/vendent；prendre不同：prends/prends/prend/prenons/prenez/prennent，不能把d机械保留。

4.3（52–53页）看度假屋时分séjour、cuisine、chambre、salle de bains，说明设备和左右位置。形容词通常后置，但grand/petit/beau/bon/vieux常前置，并与名词性数配合；beau/belle/beaux/belles及vieux/vieille等需单记，复数前置形容词前des通常变de。

4.4（54–55页）房屋广告先分à louer出租、à vendre出售，再核城市、面积、房间、楼层和ascenseur，不把“有电梯”直接推断所有无障碍条件。4.5（56–57页）故事综合拼名、每晚价格、早餐另计、房号与楼层；58–60页Test/Summary用这些信息介绍自己的家。原价格为书中历史情境。''',
'搭一个积木酒店，把“房费”“早餐”“营位”分成三张价签，再让娃娃拼名字领钥匙。价签组合帮助算钱，但不能把原书价格当成今天酒店报价，楼层制度也要看实际标识。',
'''J’ai une réservation pour deux nuits. → 我预订了两晚。
Je m’appelle Lin. Ça s’écrit L-I-N. → 我叫林，拼作L-I-N。
Avez-vous un emplacement en août ? → 八月有营位吗？
Le petit déjeuner est compris ? → 包含早餐吗？
Nous avons deux belles chambres. → 我们有两个漂亮的卧室。
La chambre coûte deux cents euros. → 房间两百欧元。
Je prends l’escalier jusqu’au premier étage. → 我走楼梯到二楼（法国楼层的premier étage）。''',
[('“我们有”选择？',['nous avons','nous ont','nous sommes avoir'],0,'avoir配nous用avons；ont配ils/elles，不能加sommes拼成现在时。'),('“一间漂亮的厨房”正确？',['un beau cuisine','une belle cuisine','une cuisine belles'],1,'cuisine阴性单数，冠词une、形容词belle并通常前置。'),('两百一十如何写？',['deux cents dix','deux mille dix','deux cent dix'],2,'cent后另有数字不加-s；deux mille dix是2010。')],
'设计两晚住宿需求，写人数、月份、淋浴/早餐要求并问总价；用三句话介绍房间设备。')

add('个人资料：年龄、家人、职业与一天','用年龄与国籍介绍自己，说明家庭关系、职业和每日活动。',
'''5.1（62–63页）年龄用avoir…ans，不能照中文用être。国籍形容词与人性数配合：chinois/chinoise、canadien/canadienne，belge/suisse等阴阳同形；一般后置，形容词小写。用habiter、parler、apprendre分别说明居住、已会语言和正在学的语言。

5.2（64–65页）家庭关系用de串联：la sœur de Paul；de+le→du、de+les→des。mon/ma/mes、ton/ta/tes、son/sa/ses按被拥有名词选，不按拥有者性别选；notre/nos、votre/vos、leur/leurs区别一件与多件。元音前阴性单数用mon/ton/son，如mon amie。

5.3（66–67页）职业接être通常不加冠词：elle est technicienne；加修饰成分时结构会变化。工作地点用dans un magasin/un hôpital。每日活动的代词式动词如se réveiller、se lever、s’habiller、se coucher需保留me/te/se等；je me lève、nous nous levons词干重音不同，原书说明句把重音写成é，但变位示例lève正确；本课采用规范的è。

5.4（68–69页）法语世界地图与各地用词展示地域差异，如加拿大fin de semaine；数字与地图是原书年代资料，不用于推断今天人口。5.5（70–71页）早餐故事介绍职业、父母来源与现居地；国籍、血缘和居住城市不是同一概念。72–74页Test/Summary把家庭所有格、日常动词和职业连成介绍。''',
'用娃娃家谱和小床演一天：“我的姐姐”放ma sœur那一格，几个孩子放mes enfants。标签跟物品换衣服，不能看拿书娃娃的性别来选son或sa；有些代词式动词也不是字面“自己给自己做”。',
'''J’ai vingt-sept ans. → 我二十七岁。
Elle est canadienne et habite à Québec. → 她是加拿大人，住在魁北克市。
Le frère de Nora est infirmier. → 诺拉的哥哥是护士。
Sa mère travaille dans une école. → 他/她的母亲在学校工作。
Nous nous levons à sept heures. → 我们七点起床。
Je m’habille avant le petit déjeuner. → 我在早餐前穿好衣服。
Mon amie parle trois langues. → 我的女性朋友说三种语言。''',
[('Paul的母亲：___ mère',['son','ses','sa'],2,'mère为阴性单数，所以sa；拥有者Paul为男性不改变选择。'),('Elle ___ trente ans.',['est','a','fait'],1,'年龄用avoir，第三人称单数a；être与faire不用于本句年龄。'),('“我们起床”应选？',['Nous nous levons.','Nous se levons.','Nous levons nous.'],0,'代词式动词主语nous配nous，代词在变位动词前。')],
'做四格人物卡，分别写年龄、国籍/住址、家人职业、起床时间；至少用两种所有格及一个代词式动词。')

add('购物：指物、数量与试穿','挑选礼物，购买定量食品，说明衣服颜色尺寸并试穿。',
'''6.1（76–77页）指物时ce配阳性单数辅音开头，cet配阳性单数元音或哑h开头，cette配阴性，ces配复数。代替名词用celui/celle/ceux/celles加-ci/-là；保留名词用ce vase-ci。颜色通常配合，orange、marron作颜色不变。vouloir现在时veux/veux/veut/voulons/voulez/veulent；je voudrais更委婉。

6.2（78–79页）不定量食品用du/de la/de l’/des；数量词后用de/d’：un kilo de、un litre d’、une douzaine de。普通否定将不定/部分冠词改de/d’，如pas de tomates；不是所有冠词都取消。en代替de引出的数量对象，数量仍保留：j’en prends deux。法国市集中的une livre按500g理解，别混成英制磅。

6.3（80–81页）问尺码用Vous faites quelle taille?；faire现在时fais/fais/fait/faisons/faites/font。le/la/l’/les是直接宾语代词，放所依附动词前：je le prends；je peux les essayer。le pantalon、le jean用单数指一条；鞋袜常用复数。

6.4（82–83页）尺码表和邮购目录要同时核商品、材质、颜色、尺码、编号与价格；原换算仅供读表，不保证品牌合身。6.5（84–85页）礼物故事加入hésiter、assorti、paquet-cadeau，并由vous转tu；86–88页测试/总结检验代词、数量和描述。''',
'开玩具商店：指着杯子用ce bol，把“杯子”卡拿走才换celui-ci；水果数好放en篮子，篮外保留deux。代词不能在脱离前文时凭空告诉别人具体是哪种水果，衣服尺码也不是儿童积木尺寸。',
'''Je préfère cette tasse bleue. → 我更喜欢这个蓝色杯子。
Cet objet coûte douze euros. → 这件物品十二欧元。
Ces robes sont belles ; je prends celle-là. → 这些连衣裙很漂亮；我选那件。
Je voudrais un kilo de pommes. → 我要一公斤苹果。
Vous avez des poires ? J’en prends trois. → 你们有梨吗？我买三个。
Je n’ai pas de monnaie. → 我没有零钱。
Je peux les essayer ? → 我可以试穿它们吗？
Vous faites quelle pointure ? → 您穿多大鞋码？''',
[('阳性objet前“这件”用？',['cet','cette','ces'],0,'objet为阳性单数元音开头，用cet；cette是阴性，ces是复数。'),('一公斤苹果：un kilo ___ pommes',['des','du','de'],2,'明确数量后用de，不按pommes复数改des。'),('已谈到两双鞋，“我能试穿它们吗”选？',['Je peux essayer les ?','Je peux les essayer ?','Je les peux essayer ?'],1,'les依附动作essayer，放不定式前；不能放到peux前或句末。')],
'挑一份礼物、一件衣服和两种食品，各写询问与回应；食品用定量和en，衣服用直接宾语代词。')

add('餐馆：点菜、追加与结账','询问菜品、表达喜好、请求补充餐具或食物，并礼貌结账。',
'''7.1（90–91页）先分menu套餐与carte菜单，再问Le plat du jour, qu’est-ce que c’est?；cuisson表示熟度，bien cuit 表熟透。重读代词moi/toi/lui/elle/nous/vous/eux/elles可用于pour moi、avec eux或强调。aller现在时vais/vas/va/allons/allez/vont，后接不定式表示打算：je vais prendre。

7.2（92–93页）间接宾语me/te/lui/nous/vous/leur代替apporter/donner/téléphoner等动词的à+人，lui不分男女，leur不加-s；放相应动词前。pouvoir为peux/peux/peut/pouvons/pouvez/peuvent，接不定式：vous pouvez m’apporter…。ne…plus是“不再/没有剩余”，后不定量冠词通常变de：plus de pain。

7.3（94–95页）甜点口味用à加冠词：au chocolat、à la vanille、à l’orange、aux fraises。qu’est-ce que…comme…询问种类。结账可说l’addition, s’il vous plaît；en même temps要求一起送来，pressé表示赶时间。

7.4（96–97页）按前菜、主菜、甜点读菜单，借食材描述表达饮食要求；不能仅凭菜名推断全部配料。7.5（98–99页）故事中人物改选菜品、邀请他人入席并提前结账，追踪“最后选什么”与“谁离开”要看后续修改。100–102页Test/Summary重练代词、口味和服务请求。''',
'把玩具餐盘分前菜、主菜、甜点三圈，给服务员娃娃一张moi卡表示“给我”。盘子帮助顺序，但lui不是只能男性娃娃，菜单名称也不是完整过敏原清单。',
'''Pour moi, une soupe aux légumes. → 我要一份蔬菜汤。
Je vais prendre le poisson. → 我打算点鱼。
Qu’est-ce que vous avez comme dessert ? → 你们有什么甜点？
Pouvez-vous nous apporter deux verres ? → 您可以给我们拿两个杯子吗？
Nous n’avons plus de pain. → 我们没有面包了。
Cette glace à la vanille est délicieuse. → 这份香草冰淇淋很好吃。
L’addition, s’il vous plaît. → 请结账。''',
[('给两位顾客带菜单：Je ___ apporte le menu.',['lui','leur','leurs'],1,'两位顾客是à+复数人，间接宾语用leur，不加-s；lui是单数。'),('“我们没有水了”选？',['Nous n’avons plus d’eau.','Nous ne sommes pas eau.','Nous n’avons encore l’eau.'],0,'ne…plus表示不再有，量词冠词改d’；être不能表示拥有。'),('草莓馅的馅饼：tarte ___ fraises',['au','de le','aux'],2,'口味结构à+les fraises缩合aux；au配阳性单数，de le不合法。')],
'编一顿原创三道菜，用pour moi点单，问一次配料，追加一件餐具，再请求账单。')

add('复习二：住宿、家庭、购物与用餐','在同一次旅程中完成订房、介绍同行者、购物试穿和点餐，检查冠词及代词。',
'''Review 2（103页）词汇把颜色、果蔬、肉类、衣物和餐具分组；职业词根及-eur/-euse、-ien/-ienne等帮助识别，但职业阴性不能全靠同一词尾推算。人物描述需合并年龄、国籍、工作与家庭线索。

104–105页语法把vouloir/pouvoir/faire/avoir/aller用于试穿对话：je fais du…表示尺码，je peux l’essayer是请求，je vais prendre是决定。食品du/de la/des表示量，au/à la/aux表示口味；看到“部分冠词”与“à缩合冠词”都像du/au时要追问功能。代词式活动先配主语与me/te/se/nous/vous/se，再配动词，nous nous réveillons 两个nous功能不同。

105页餐馆老板采访是缺音频的听辨任务，可先从职业、厨房、食物词预测主题，不把预测当确认。106页朗读及订房口语综合人数、晚数、设施、价格；完成订房应复述条件，再提出个人需求。T05–T08各提供一个可返回练的场景，本课独立题目不复制原书答案。''',
'给玩偶旅行箱放房卡、家谱卡、商店卡、餐盘卡；每翻一张就要用上一张里的人物信息。四张卡仍不是四种万能句型，食品“有多少”与“什么口味”必须分开。',
'''Nous voudrions une chambre pour trois personnes. → 我们想要一间三人房。
Ma sœur est architecte. → 我姐姐是建筑师。
Elle se réveille tôt. → 她醒得早。
Je peux essayer cette veste ? → 我可以试穿这件外套吗？
J’en voudrais deux kilos. → 我想要两公斤（前文所说的东西）。
Je vais prendre une tarte au citron. → 我打算点一份柠檬馅饼。
Vous pouvez lui apporter une cuillère ? → 您能给他/她拿一个勺子吗？''',
[('“柠檬口味”与“一公斤柠檬”应分别用？',['au citron / de citrons','du citron / aux citrons','à citron / des citrons'],0,'口味à+le缩合au；明确一公斤后用de。'),('Nous ___ réveillons tôt.',['se','nous','vous'],1,'nous主语对应反身代词nous；se配第三人称，vous配第二人称。'),('她是建筑师的基本表达？',['Elle est une l’architecte.','Elle a architecte.','Elle est architecte.'],2,'基本职业介绍être后直接接职业；不能叠加冠词或用avoir。')],
'用七句介绍一次旅行：订房两句、家人两句、购物一句、点餐及请求服务各一句；圈出所有冠词解释功能。')

add('出行：交通、车票与汽车故障','比较交通方式，读24小时列车时刻，并完整报告车辆故障。',
'''8.1（108–109页）乘交通工具用en train/en avion/en voiture/en bus；步行à pied、自行车à vélo，书中也列à moto/à cheval。不要按中文“坐/骑”逐字选介词。y代替地点短语并放相应动词前：j’y vais；它不代替所有à+人的成分。

8.2（110–111页）买票先说目的地、aller simple或aller retour、première/seconde classe，再确认départ与arrivée。devoir现在时dois/dois/doit/devons/devez/doivent，后接不定式。qui引导关系从句并充当从句主语，人和物都能指：le train qui part。官方时刻用24小时：16h15读seize heures quinze，不说seize heures et quart。

8.3（112–113页）求助先报位置、车型颜色、车牌、故障及姓名；en panne d’essence、un pneu crevé、la batterie à plat、les freins ne marchent plus各指不同问题。方式副词通常由阴性形容词加-ment：lentement、normalement；gentiment、vraiment、poliment另记。

8.4（114–115页）原SNCF旅客指南介绍售票窗口、自动机、预购等，阅读时先定位标题与适用对象；有效期、票制是原书历史资料，不当当前出行规则。8.5（116–117页）故事强调目的地、会议时间与故障求助，je dois y être把义务和地点代词连起来。118–120页Test/Summary检查时刻、交通介词、qui与故障描述。''',
'玩具火车带“去哪里”的站牌，站牌重复时用一枚y代替；轮胎、电池和油箱各贴故障图卡。y只记住前文那个地点，不能随意代替姓名；玩具维修不代表现实维修操作。',
'''Je vais à Lyon en train. → 我乘火车去里昂。
Nous y allons à vélo. → 我们骑自行车去那里。
Je voudrais un aller retour pour Lille. → 我想买一张去里尔的往返票。
Le train qui part à seize heures est direct. → 十六点出发的那班火车是直达车。
Je dois arriver avant dix-huit heures. → 我必须十八点前到。
Ma voiture est en panne près du pont. → 我的车在桥附近坏了。
La batterie est à plat. → 电池没电了。
Pouvez-vous venir rapidement ? → 您能尽快过来吗？''',
[('16h45时刻表规范读法？',['seize heures moins le quart','seize heures quarante-cinq','quatre heures et quart'],1,'24小时制直接读分钟45；第一项表达15:45的倒数式，第三项是4:15。'),('le train ___ arrive à midi',['que','où','qui'],2,'缺的是arrive的主语，qui指先行词train；que作宾语，不适用。'),('Nous allons à Rennes. Nous ___ allons en bus.',['y','en','lui'],0,'y代替地点à Rennes；en常代替de引出的成分，lui常指间接宾语人。')],
'自拟一张有起终点、出发到达时刻和票种的车票；另用四句给修车厂报位置、车况、车型及请求。')

add('健康表达：症状、过去发生的事与指令','说明哪里不舒服、何时发生，读懂指令结构而不把语言材料当处方。',
'''9.1（122–123页）身体部位多用定冠词：avoir mal à la tête/à l’oreille/au dos/aux dents。mal au cœur在本课是恶心，不应机械译成心脏痛。avoir还构成faim/soif/chaud/froid/peur/besoin de/envie de；être malade表示生病，不能把这些都统一成être。

9.2（124–125页）叙述已发生的事用avoir现在时加过去分词：j’ai mangé。规则-er→-é，许多-ir→-i、-re→-u，但ouvrir→ouvert、souffrir→souffert等须查。否定夹助动词：je n’ai pas dormi，不能把pas放在分词后。

9.3（126–127页）il faut+不定式表达必须；对具体听者也可用命令式。否定命令式ne…pas夹动词，代词在前：ne vous inquiétez pas。eu、bu、été、mis、pu、pris、vu分别来自avoir、boire、être、mettre、pouvoir、prendre、voir。用这些形式报告自己做过什么，不照原故事给人开药。

9.4（128–129页）原顺势疗法表按鼻、喉、头、眼和口渴症状组织，本课只学习读取症状表及对应栏位，不把该表当作有效性证据或用药推荐。9.5（130–131页）故事中的来电把过去整夜的状态与现在症状区分开，读稿找J’ai été/Je n’ai pas dormi与现在时；132–134页Test/Summary复习症状、过去分词和指令。''',
'给布娃娃身体贴头、牙、脚卡片，用昨日/现在两只盒子放症状句。盒子帮助时间表达，不负责判断病因；法语“恶心”也不能靠把卡片贴在心脏位置就解释成心脏病。',
'''J’ai mal au dos depuis ce matin. → 我从今天早上起背疼。
Elle a mal aux dents. → 她牙疼。
J’ai froid et j’ai soif. → 我冷而且口渴。
J’ai mal dormi cette nuit. → 我昨晚没睡好。
Nous avons appelé le médecin. → 我们给医生打过电话了。
Je n’ai pas pris ce médicament. → 我没吃过这种药。
Il faut demander conseil au pharmacien. → 需要向药剂师咨询。
Ne prenez pas mon verre. → 不要拿我的杯子。''',
[('“我牙疼”正确？',['Je suis mal dents.','J’ai mal à les dents.','J’ai mal aux dents.'],2,'avoir mal à+les dents缩合aux；不能用être或保留à les。'),('完成过去“我没睡”：Je ___ dormi.',['n’ai pas','ne suis pas','n’ai dormi pas'],0,'dormir复合过去用avoir，ne…pas包助动词；B助动词错误，C重复并错置。'),('il faut后接哪个形式？',['demandez','demander','demandons'],1,'il faut后这里接不定式demander；其他为变位形式。')],
'写一张原创就诊语言卡：现在症状两句、开始时间一句、已做/未做的事各一句；只报告事实，不自行补治疗方案。')

add('闲暇：经历、习惯与过去背景','谈兴趣与频率，用être构成复合过去，并用未完成过去描述过去习惯。',
'''10.1（136–137页）aller、arriver、venir、partir、rester、tomber、naître、mourir等在本课不及物用法中以être构成复合过去，分词常随主语性数配合：elles sont parties。代词式动词也用être，但不是永远跟主语配合：elle s’est cassé le bras 中le bras为后置直接宾语，cassé不加-e；部分移动动词带直接宾语时可改用avoir。

10.2（138–139页）从过去持续至现在的活动用现在时+depuis：je lis…depuis deux ans。运动或游戏用jouer à，乐器用jouer de，并按冠词缩合。频率用souvent、toujours、quelquefois、de temps en temps、une fois par semaine；ne…jamais表示从不，复合时放助动词两侧。

10.3（140–141页）未完成过去描述习惯与背景：nous现在时去-ons，加-ais/-ais/-ait/-ions/-iez/-aient；être用ét-。复合过去推进事件，未完成过去铺场景，如je dormais quand il est arrivé；不能单靠中文“了”判断。

10.4（142–143页）休闲文章读ne…jamais与百分比：分母是原文指定人群，统计只代表原资料年代。10.5（144–145页）病后道别和家人往事把一次经历、持续状态和童年背景交织；146–148页Test/Summary需同时说明喜欢什么、做多久、多久一次和过去做什么。''',
'把照片贴在玩具时间长绳上：单张“跌倒”照片是事件，整段涂色“小时候经常读书”是背景，绳子延伸到现在是depuis。图形只是判断线索，同一动作也能按说话视角成为背景或事件。',
'''Ma sœur est arrivée hier. → 我姐姐昨天到了。
Elles sont restées trois jours. → 她们待了三天。
Elle s’est lavé les mains. → 她洗了手。
Je joue du violon depuis un an. → 我拉小提琴已有一年了。
Nous jouons aux cartes deux fois par mois. → 我们每月玩两次牌。
Je ne vais jamais au stade. → 我从不去体育场。
Quand j’étais enfant, je lisais le soir. → 我小时候晚上常读书。
Je lisais quand il a téléphoné. → 他打电话来时我正在读书。''',
[('“她们出发了”选？',['Elles ont parties.','Elles sont parties.','Elles sont parti.'],1,'partir本句用être，elles使分词加-es；A助动词错，C漏配合。'),('一直学到现在已有两年应选？',['J’apprends le français depuis deux ans.','J’ai appris le français il y a deux ans seulement.','Je vais apprendre dans deux ans.'],0,'depuis+现在时表达仍持续；B是两年前的已发生事件，C是两年后的将来。'),('玩钢琴应选？',['jouer au piano','jouer le du piano','jouer du piano'],2,'乐器用jouer de，de+le缩合du；不能套运动的à。')],
'写一项兴趣的持续时间和频率，再加两句童年习惯与一次上周事件，检查être分词配合。')

add('复习三：出行、健康与过去叙事','串联旅程、症状、兴趣和历史叙述，区别持续至今、过去背景与已完成事件。',
'''Review 3（149页）词汇按交通与身体分类，pied既可出现在à pied也可在mal au pied。问答需先识别问出生地、交通、习惯还是症状，不能只按关键词联想。

150页语法中的戒烟经历用未完成过去说以前的频繁行为，用复合过去说停止这一事件，用现在时+depuis说持续至今的锻炼。兴趣采访再核jouer à/de、频率和jamais；这三种时间视角可以出现在同一段中。

150–151页Hastings阅读/听力任务含人物关系、先后事件和具体日期；先建立“谁—做什么—什么时候”表，再判断过去时。原听力未提供，不把历史常识或猜词当成实际听见的词。152页医生口语用depuis说明持续症状，用hier+复合过去报告昨日动作，再说明现在是否还疼；另有“不健康生活方式”虚构竞赛任务，用于语言练习而非生活建议。

本复习返回T10交通介词与时刻、T11症状及avoir过去式、T12être过去式/未完成过去/兴趣。自测时标明错误来源：缺词、助动词、分词配合或时间视角，修正后换人物和日期再说一次。''',
'让三只玩具恐龙排“以前—昨天—现在”，每只拿一张句子卡；把从以前连到现在的橡皮筋标depuis。恐龙的位置不自动决定时态，过去的某一天也能同时有背景和事件。',
'''Avant, je prenais toujours le bus. → 以前我总乘公交车。
Hier, je suis rentré à pied. → 昨天我步行回家了（说话者为男性）。
Je marche tous les jours depuis un mois. → 我每天步行已有一个月。
J’ai eu mal à la tête hier. → 我昨天头疼。
Aujourd’hui, je n’ai plus mal. → 今天我不再疼了。
Je jouais aux cartes quand elle est arrivée. → 她到来时我正在打牌。
Nous y sommes allés en train. → 我们乘火车去了那里。''',
[('以前经常的背景行为，应选？',['Avant, je fumais.','Avant, je fumerai demain.','Avant, je suis fumer.'],0,'fumais是未完成过去，适合以前习惯；其余时间冲突或结构不成立。'),('“昨天头疼，现在不疼了”应说？',['J’ai mal demain.','J’ai eu mal hier ; maintenant, je n’ai plus mal.','Je n’ai jamais eu mal hier et toujours.'],1,'先用eu报告昨日状态，再用ne…plus表达现在停止；其余不符合时间或语义。'),('过去正在读书时她到了：Je ___ quand elle est arrivée.',['lirai','suis lire','lisais'],2,'lisais铺背景，与一次到达事件配合；lirai为将来，suis lire不成立。')],
'编四句出行中的小故事：过去习惯、昨日事件、当时背景、现在持续活动各一句，并给每句标时间依据。')

add('在家待客：欢迎、比较与致谢','欢迎客人并提供茶点，比较房屋及物品，写合适语气的感谢便条。',
'''11.1（154–155页）Entrez、Asseyez-vous欢迎入内和就座；vous avez fait bon voyage?问旅途。chez接人名/人称重读代词表示某人的家或营业处：chez moi、chez eux、chez le médecin；不能写chez je。

11.2（156–157页）比较plus/moins/aussi+形容词+que，形容词仍与被描述名词配合；比较对象是人称代词时用moi/toi/eux等。最高级le/la/les plus/moins，与形容词位置一起处理：la plus grande pièce、la pièce la plus calme；比较范围常用de。

11.3（158–159页）bon的比较级meilleur仍是形容词，要配合；bien作副词的比较级mieux修饰动作。mal可用plus mal/pire，须看结构。物主代词le mien/la mienne/les miens/les miennes按所替代物性数选；nôtre/vôtre有重音，与notre/votre物主限定词区分。

11.4（160–161页）两封感谢便条语气不同，从称呼、tu/vous、结束语识别亲疏，再写自己的具体感谢。手写OCR尤其需对原图核字。11.5（162–163页）拜访故事用推荐茶饮、询问喜好与比较人物性格；164–166页Test/Summary检验欢迎、续份、礼貌拒绝、比较和物主代词，不要求照搬故事角色评价。''',
'给两个积木房子量大小，拿掉“我的房子”卡换la mienne；给客人娃娃续一块玩具蛋糕。房子比高只是plus grand的一个情境，meilleur是质量较好而mieux是做得较好，不能只用尺子区分。',
'''Entrez et asseyez-vous, s’il vous plaît. → 请进，请坐。
Vous prendrez du thé ? → 您喝点茶吗？
Non merci, j’en ai assez. → 不，谢谢，我已经够了。
Votre cuisine est plus claire que la mienne. → 您的厨房比我的明亮。
Cette pièce est la plus calme de la maison. → 这个房间是家里最安静的。
Ce gâteau est meilleur que le mien. → 这个蛋糕比我的好吃。
Elle chante mieux que moi. → 她唱得比我好。
Merci pour cette agréable soirée. → 谢谢这段愉快的晚间时光。''',
[('“去她家”应选？',['chez elle','chez la','chez je'],0,'chez是介词，后用重读代词elle；la为直接宾语，je为主语。'),('“她唱得更好”用？',['Elle chante meilleure.','Elle chante mieux.','Elle chante bon.'],1,'修饰chante动作的副词bien比较级是mieux；meilleure和bon是形容词。'),('代替阴性单数ma cuisine应选？',['le mien','les miennes','la mienne'],2,'cuisine阴性单数，所以la mienne；不能按拥有者性别决定。')],
'写一次来访欢迎三句和离开后感谢两句；另比较两件家中物品，分别用plus…que和物主代词。')

add('做计划：天气、邀请和关系从句','谈天气与季节，礼貌提出或拒绝计划，用qui/que说明喜欢的地点或作品。',
'''12.1（168–169页）天气的il通常无具体人称：il fait chaud/froid/beau/mauvais，il pleut/neige，il y a du vent/du soleil/des nuages。预测可用aller+不定式：il va pleuvoir、il va y avoir…；倒装va-t-il中的-t-是连音形式。季节名阳性，常用au printemps、en été/en automne/en hiver。

12.2（170–171页）邀请用vouloir/pouvoir，拒绝给devoir+不定式的原因。条件式je voudrais/j’aimerais/je préférerais缓和愿望，on pourrait建议，vous devriez建议应做的事。规则词用将来词干加未完成过去词尾；不规则pourr-/voudr-/devr-另记，-re去末尾e。

12.3（172–173页）qui作关系从句主语，que/qu’作直接宾语：une artiste qui peint；le tableau que j’admire。que不可像英语有时省略，元音前qu’；不能只用“人选qui，物选que”的口诀，因为人和物两者都能用。

12.4（174–175页）天气图与地区文字需合看地域、早晚、温度、云雨风，预测中的将来时先识义，T17再系统学形式。12.5（176–177页）获奖消息把天气心情、领奖日期和同行邀请连接起来，比较未确定建议pourrait与实际安排。178–180页Test/Summary集中天气、情态动词、条件式和关系从句。''',
'给周末游玩棋盘贴太阳、雨和云，拿“想去”卡用voudrais，拿“可以提议”卡用pourrait；谁在画画的小人是qui，别人画的画是que。卡片帮助分角色，qui/que的选择依据语法位置，不是画的是人还是物。',
'''Il y a du brouillard ce matin. → 今天早上有雾。
Il va pleuvoir cet après-midi. → 今天下午要下雨。
Au printemps, je marche dans le parc. → 春天我在公园散步。
J’aimerais visiter ce château. → 我想参观这座城堡。
On pourrait se retrouver devant la gare. → 我们可以在车站前碰面。
Je ne peux pas venir ; je dois travailler. → 我不能来，我得工作。
Voici l’artiste qui expose ici. → 这是在这里办展的艺术家。
C’est le tableau que je préfère. → 这是我最喜欢的那幅画。''',
[('“正在唱歌的女孩”：la fille ___ chante',['que','qui','qu’'],1,'关系词担任chante的主语，用qui；que是宾语。'),('礼貌说“我想参观”应选？',['Je voudrais visiter.','Je voudrai visiter hier.','Je veux visitez.'],0,'voudrais为条件式，后接不定式visiter；voudrai是将来，visitez为变位。'),('“天空在下雨”法语基本表达？',['Il fait pleut.','Elle est pluie.','Il pleut.'],2,'pleuvoir本身是天气动词，用无人称il；不再加faire或être。')],
'写周末邀请：天气一句、愿望一句、提议一句、时间地点一句；用关系从句补充想去的地点。')

add('回顾过去：海外经历、假期和心情','谈国家与假期经历，用il y a定位多久以前发生的事，正确放置宾语代词。',
'''13.1（182–183页）去/在国家通常阴性用en、阳性辅音开头用au、复数用aux：en Chine、au Canada、aux Pays-Bas；阳性元音开头也常用en，如en Iran，不能只看性别套au。区分国家名与国籍形容词。

13.2（184–185页）连续两动词时本课第二个用不定式：j’adore faire du ski、je voudrais téléphoner；有些动词需要à/de后接不定式，不能一概省介词。il y a+时长表示“多久以前”，如il y a trois jours，是事件距今距离；depuis则可说持续至今。

13.3（186–187页）心情表达区分être de bonne/mauvaise humeur、ne pas avoir le moral、s’ennuyer。宾语代词在单动词前，在复合时态助动词前，在情态/近将来结构所依附不定式前；肯定命令式通常放后并连字符：appelle-le、téléphone-moi。否定命令式回到前：ne lui téléphone pas。

13.4（188–189页）旅游文章的67 millions、36,2 millions等对应1997年资料；读比较对象时要分游客人数、长住次数、收入三种指标，不能把一个排名当所有排名。13.5（190–191页）领奖致辞用未完成过去说童年习惯，用复合过去回顾帮助和经历，再用les remercier指代感谢对象。192–194页Test/Summary综合国家、情绪、过去时和il y a。''',
'把玩具旅行地图上的国家分三个盒子en/au/aux，事件照片旁贴“距今三天”箭头；代词小车停在它服务的动作前。国家分盒有元音例外，肯定命令式的小车也会挪到后面，所以不能把位置永远固定。',
'''Nous avons passé une semaine au Canada. → 我们在加拿大待了一周。
Elle est née aux États-Unis. → 她出生在美国。
Je suis rentré il y a quatre jours. → 我四天前回来了（说话者为男性）。
J’habite ici depuis quatre jours. → 我住在这里已有四天了。
Je n’ai pas le moral aujourd’hui. → 我今天心情低落。
Je lui ai téléphoné hier. → 我昨天给他/她打电话了。
Je vais les remercier. → 我打算感谢他们/她们。
Donne-moi ton adresse. → 把你的地址给我。''',
[('“三天前到了”：Je suis arrivé ___ trois jours.',['depuis','il y a','pendant depuis'],1,'一次到达距今三天用il y a；depuis强调持续，不能直接用于本题一次到达。'),('近将来“我打算给她打电话”选？',['Je lui vais téléphoner.','Je vais téléphoner lui.','Je vais lui téléphoner.'],2,'lui依附不定式téléphoner，放其前；不是依附aller。'),('去复数国家Pays-Bas用？',['aux Pays-Bas','au Pays-Bas','en les Pays-Bas'],0,'les Pays-Bas为复数国家名，去/在用aux。')],
'写一次虚构假期：国家、出发多久以前、当时背景、一次事件、现在心情各一句；加一句代词式感谢或致电。')

add('工作联系：电话留言、约见与将来','打商务电话留消息，读简历和求职信，区分将来、刚刚发生与礼貌建议。',
'''14.1（196–197页）先问Je voudrais parler à…，人不在可问Je peux laisser un message?。未来可用现在时+明确日期、aller+不定式或简单将来；简单将来常用于陈述未来事实与预测。规则-er/-ir在不定式后加-ai/-as/-a/-ons/-ez/-ont；être用ser-。

14.2（198–199页）venir de+不定式表示刚刚：elle vient de sortir。电话用C’est de la part de qui?问来电者，Ne quittez pas请等待，Je vous le/la passe转接，C’est noté确认记下，son poste est occupé表示分机忙。姓名、公司、回拨号码和事由应完整复述。

14.3（200–201页）约见用Quel jour vous conviendrait?；将来-re去末e，如répondrai。常见不规则词干：ir-/aur-/fer-/viendr-/verr-/pleuvr-/pourr-/voudr-/saur-/recevr-/devr-，再加同套将来词尾；条件式共享这些词干，却用-ais等词尾，所以je pourrai与je pourrais不是同一形式。

14.4（202–203页）CV的formation、expérience professionnelle、langues、sports分栏检索；求职信先说明来意，再附件ci-joint、补充资料和礼貌结尾。书中日期、年龄及格式用于读原文本，不强称是现代通用模板。14.5（204–205页）实习生故事整合介绍他人、工作日程、转接与约见；206–208页Test/Summary总检未来、电话词和留言准确性。''',
'两只玩具电话之间放留言板，用“刚刚”印章贴vient de，用明天日历贴rappellerai。印章只是时间意义提示，不可把venir de当将来；礼貌条件式与未来承诺也要用不同卡。',
'''Je voudrais parler à Madame Roy. → 我想找鲁瓦女士讲话。
Puis-je laisser un message ? → 我能留个口信吗？
C’est de la part de Mei Lin, de la société Atlas. → 来电的是阿特拉斯公司的梅林。
Elle vient de partir en réunion. → 她刚去开会了。
Je rappellerai demain matin. → 我明天上午会再打来。
Nous serons disponibles jeudi. → 我们周四有空。
Quel jour vous conviendrait ? → 哪一天对您合适？
Vous trouverez mon CV ci-joint. → 附件中有我的简历。''',
[('“我会回拨”未来承诺用？',['Je rappellerais.','Je rappeler.','Je rappellerai.'],2,'rappellerai是简单将来；rappellerais为条件式，rappeler为不定式。'),('“她刚刚离开”用？',['Elle vient de partir.','Elle va venir hier.','Elle vient partirais.'],0,'venir de+不定式构成最近过去；其他结构与时间不合。'),('Je vous le passe. 在电话中意思是？',['我把您写在简历里','我给您转接他','我会挂断电话'],1,'本情境passer quelqu’un au téléphone是转接；le指要找的人。')],
'自录一段45秒电话：说明身份和公司、找人、听说不在、留事由和回拨时间，最后复述号码。')

add('复习四：从来访到工作电话的综合表达','综合待客、天气计划、过去经历与职场电话，核对时态与代词。',
'''Review 4（209页）词汇把季节、天气、国家、外貌情绪和动作分组，并找反义关系。九组问答分别指向电话、天气、经历、结婚时间、续份及邀请：先找问句交际目的，再选择回应，不能仅看有相同词。

210页祖母回忆用être复合过去说出生和抵达，用avoir复合过去说打电话和搭车，用未完成过去描述天气、心情和宝宝当时的状态。天气预报则练简单将来和不规则词干：fera、aura、pleuvra、sera、pourrez；不是把所有将来都换成aller。

210–211页Van Gogh任务把出生地、住处、作品和时间顺序结合，先分阅读可知、个人背景知识和必须听CD的信息；缺音频时不能把答案表文字当听力完成记录。212页朗读回收国家介词、过去形态和间接宾语；电话角色练习需核对来电身份与返回日期。

212页澳大利亚明信片把旅途背景、当前假期、已遇见的人、持续三周与下周返程放在一起；同一封信可以有多个时态。把T14–T17的结构用在自己的原创情境，再返回原题核格式，是本轮复习的完成标准。''',
'给四只娃娃分别戴“回忆”“现在”“预测”“礼貌请求”帽子，围着同一张旅行明信片说话。帽子提醒视角，同一说话者可以换帽；看见demain也要先判断是否愿望或承诺。',
'''Tu veux dîner chez nous vendredi ? → 周五你想来我们家吃晚饭吗？
J’aimerais bien, mais je dois travailler. → 我很想去，但我得工作。
Il faisait froid quand nous sommes arrivés. → 我们到达时天气很冷。
Demain, il fera plus chaud. → 明天天气会更暖。
Je suis ici depuis trois semaines. → 我在这里已有三周了。
Je lui ai écrit la semaine dernière. → 我上周给他/她写过信了。
Pouvez-vous lui dire que j’ai appelé ? → 您能告诉他/她我打过电话吗？
Je rentrerai mardi prochain. → 我下周二回来。''',
[('抵达时天气冷应选？',['Il faisait froid quand nous sommes arrivés.','Il fera froid hier nous arriver.','Il fait sommes froid.'],0,'背景用未完成过去faisait，一次到达用复合过去sommes arrivés。'),('“我上周给她写信”：Je ___ écrit la semaine dernière.',['l’ai','lui ai','ai lui'],1,'écrire à quelqu’un用lui，复合时态代词在助动词ai前。'),('“将来我能来”应选？',['Je pouvais venir.','Je peux venu.','Je pourrai venir.'],2,'pourrai为pouvoir简单将来，后接不定式venir；pouvais是过去，venu是分词。')],
'写五句明信片再附两句电话留言，含过去背景、完成事件、depuis、未来和礼貌请求。')

add('答案附录：定位、核对和改错','按单元与题号找到原答案，区分唯一答案、开放示例与待听信息，把错题变成可复述规则。',
'''Answers（印刷213–223页）沿主单元、Test、Summary与Review的原顺序编排。213页从Unit 1开始，214–215页含Unit 2/3与Review 1；215–218页接Unit 4–7与Review 2；218–220页接Unit 8–10、Review 3和Unit 11；220–223页接Unit 12–14与Review 4。跨页时必须同时核单元标题和题号，不能以PDF物理页当题页；这里每个PDF页是一张双页扫描。

先记录自己所做的题是Activity、Test还是Summary，再找到对应小标题和题号。a2/b9这类紧凑字母数字表示配对关系；V/F及括号补充表示真假判断和修正，不是必须照抄的长答案。Example标示开放题示例，可以存在别的正确表达；语法、信息条件和语气都满足时，不因用词不同就判错。

核对法语时先看意思是否满足题干，再看冠词性数、主语与动词、助动词与分词、宾语代词位置，最后核拼写重音。Tu as…与Vous avez…意思接近但听者关系不同；一处冠词错不能通过背全句解决，要换另一个名词验证规则。

答案中的完整听力文本可以帮助阅读和理解，但原CD缺失，不能据此记成“听对了”；TTS也不是原录音。扫描OCR可能把l’识成I’、è识成é或把两列黏连，疑点回到原图，保留待核标记。本课例句与选择题是新增改错示范，既非原练习答案也非原文翻译。''',
'把错题当积木模型：先对照图纸找缺的那一块，再自己重新搭一个不同颜色的模型。图纸里的“示例模型”不是唯一搭法；只偷看成品也不能证明刚才听懂了玩具电话。',
'''J’ai choisi la réponse B. → 我选了B答案。
Je vérifie le numéro de l’activité. → 我核对活动题号。
Cette phrase respecte la consigne. → 这个句子符合题目要求。
Voici une autre réponse possible. → 这是另一个可能的答案。
Il manque un article dans ma phrase. → 我的句子少了一个冠词。
Je dois vérifier ce mot sur l’image. → 我需要在原图上核查这个词。
Je n’ai pas écouté l’enregistrement original. → 我没有听原录音。''',
[('开放题答案以Example开头，你写了意思相同且语法正确的另一句，应如何核对？',['必须全部改成示例原句','检查是否满足情境和语气，再认可合理变体','直接判零分'],1,'Example通常提供示例而非唯一字串，仍须核任务条件、语法和称呼。'),('原CD缺失，读了附录的听力文本后可记录什么？',['已读文本并理解，听辨仍待完成','原音频全部听懂','原说话者语调全部正确'],0,'阅读证据只支持文本理解，无法证明听辨和原音语调。'),('扫描答案的题号与自己练习不匹配，第一步？',['照最像的句子抄','按答案页物理编号猜','核单元及Activity/Test/Summary标题'],2,'同一答案页有多个单元或不同题型，先确认位置，才能正确配题。')],
'任选一题已做的原文字练习，写下单元/题型/题号、自己的回答、核对依据及一条修正规则，再造一个新例句。')

add('语法总表：按问题检索规则和变位','用附录定位冠词、形容词、代词、介词和时态，核变位表并理解规则范围。',
'''Grammar Summary（224–236页）是检索工具。224页名词性别、复数和冠词：常规-s，-eau多加-x，œil→yeux、journal→journaux需记；le/la/l’/les与un/une/des区分确定性，à/de遇le/les缩合。225–226页形容词配合、位置、物主/指示/疑问限定词；mon/sa等按所修饰名词选，cet用于阳性元音前，quel按名词性数变。

226–228页主语代词与重读代词不能互换；直接宾语le/la/les和间接宾语lui/leur取决于动词结构。代词在相应动词前，复合时态在助动词前，肯定命令式常放后；y代地点、en代de成分并保留数量。物主代词le mien等替代名词，指示代词celui-ci等指具体对象；c’est/ça配不同表达，但不能把书中“ça用于其他所有动词”当无例外规则。关系代词qui担任主语、que担任宾语。

228–230页介词核国家en/au/aux、交通en/à、所属de。副词常以阴性形容词加-ment，gentiment等例外；比较/最高级plus/moins/aussi…que、le plus，bon→meilleur与bien→mieux分别管性质与动作。问句有升调、est-ce que、倒装；否定ne…pas/plus/jamais夹变位动词，不定量冠词常变de，但être后的表语等不能机械照搬。

230–232页动词系统先找不定式、词干和人称，再选现在、命令、未完成过去、复合过去、将来或条件式。代词式动词保留额外代词。命令式tu并非所有动词都去-s：parle但finis、prends；nous/vous也有不规则形式。未完成过去用nous现在词干，être用ét-；复合过去选avoir/être及分词配合；将来词干加-ai等，条件式同词干加-ais等。

232–236页表格覆盖规则-er、finir型-ir、vendre型-re及prendre家族；avoir/être兼作助动词；另列aller、dormir、ouvrir、partir、sortir、venir、connaître、croire、dire、écrire、faire、lire、mettre、falloir、pleuvoir、savoir、voir、devoir、pouvoir、vouloir。查表读“动词—时态列—人称行”，缺行不代表该人称不存在。原图已核：233页印作je prend、234页印作ils partirent与ils croirons，均为原书误植；规范形式是je prends、ils partiront、ils croiront。保留源文，但不要把印刷错误学成特殊规则。

这份总表以本课程为范围，原规则有简化；本课用具体反例提示边界，不把附录当全部法语语法。遇新语境先定位原说明，再查参考资料。''',
'像给积木分类柜贴抽屉名：名词、冠词、代词、动词。拿动词积木先选时态托盘，再选人称格；但不规则积木要看自己的形状，不能硬塞进规则盒，也不能把只有部分行的表当成缺零件。',
'''Les nouveaux bureaux sont calmes. → 新办公室很安静。
C’est mon sac ; le tien est là-bas. → 这是我的包；你的在那边。
Je leur ai donné deux billets. → 我给了他们/她们两张票。
Je vais lui répondre. → 我打算回复他/她。
Finis ton exercice, puis parle doucement. → 做完练习，然后轻声说话。
Nous vendions des livres. → 我们以前卖书。
Elles partiront demain. → 她们明天出发。
Je pourrais venir vendredi. → 我周五可以来。''',
[('查“她们将出发”，应选partir表哪一项？',['ils/elles + futur : partiront','nous + présent : partons','ils/elles + imparfait : partaient'],0,'主语第三人称复数、时间为将来，需要partiront；不是现在或过去。'),('tu命令式全部去-s，对吗？',['对，finir变fini','不对，parle但finis、prends','对，prendre变prend'],1,'去-s主要适用于-er型等情况；finis/prends保留-s，原总表简化不能全套。'),('代词指“给他们”，应选？',['les','leurs','leur'],2,'间接宾语à+复数人用leur且不加-s；les是直接宾语，leurs是物主限定词。')],
'选三个真实疑问，分别查一项名词规则、一项代词位置和一项动词变位；记印刷页并各写原创示例。')

add('词汇附录：把字母索引变成主题词卡','按法语词头查词，结合词性、搭配和语境建立覆盖全书情景的个人词库。',
'''Vocabulary glossary（237–244页）实际上按法语字母顺序排列，并非中文主题词表：237页A起，238页B/C，239页C/D/E，240页F/G/H，241页J/L/M，242页N/O/P，243页P/R/S，244页S/T/U/V/W/Y/Z及结尾。按词头查找，冠词le/la/l’不是排序重点；代词式动词看se/s’与动词，不把所有词塞进S栏。OCR双栏错序时回看原图。

名词连冠词和性别记，如l’aéroport(m)；复数词要保留les；形容词的(e)提示阴性，blanc/blanche、curieux/curieuse等完整变化另记。动词词头是不定式，ai、pris、étais等要先还原avoir、prendre、être再查变位表。faire可指做，也可在时间、价格、尺码表达中形成不同中文意思；la recette可指食谱，也可在旅游文章中指收入，不能只背第一个释义。

把字母词汇转为全书主题时，依次建：问候/礼貌、咖啡馆/价格数字、城镇建筑/路线、星期/时间/日程、住宿房间/设备/月份、个人国籍语言/家庭/职业/日常、礼物颜色形状材料/果蔬数量/衣物尺码、餐馆食材口味/餐具结账、交通车票/车辆故障、身体症状/就医、休闲运动乐器/频率、待客饮品/比较、天气季节/邀请、国家旅行/心情往事、工作电话/求职通信。每组从附录检索词头，再返回对应单元原句理解用法，不把单个词头当完整会话。

记录搭配比记录孤词更有效：un billet aller retour、avoir mal à、faire la vaisselle、laisser un message、se réveiller。把词卡分为“能认出”“能说出”“能造新句”三栏，按自己错误调整；英语释义供理解，多义词要先查本章语境。本课仅提供原创练法，原词汇全文仍从原书阅读入口查。''',
'把散在字母抽屉里的玩具食物、车辆和小电话，取出来装进不同场景盒；每盒贴一个可说的短句。分类是自己的学习办法，原书仍按字母；同一玩具也能进两盒，像temps既指时间也指天气。',
'''Je cherche le mot « billet » dans le glossaire. → 我在词汇附录里查billet这个词。
Il me faut un billet aller retour. → 我需要一张往返票。
Ce mot a deux sens dans ce livre. → 这个词在本书有两个意思。
J’apprends « une cuillère » avec son article. → 我把une cuillère连同冠词一起学。
Je classe « se lever » avec les activités quotidiennes. → 我把se lever归在日常活动组。
Je voudrais laisser un message. → 我想留个口信。
Quel temps fera-t-il samedi ? → 周六天气会怎样？
Je vérifie le sens dans la phrase. → 我在句中核对词义。''',
[('遇到ai，应先查哪个词头？',['aimer','avoir','aller'],1,'ai是avoir的je现在时，不能按开头相同误查aimer或aller。'),('词卡要记“勺子”，最好写哪一项？',['cuillère，无其他信息','勺子=不变化','une cuillère + 一个搭配'],2,'连冠词保存性别，再用搭配巩固用法；孤词不足以选冠词，名词也可变复数。'),('旅游文章的recettes touristiques应先如何理解？',['按文章语境理解为旅游收入','只因常见意思就译旅游食谱','当成所有国家人口'],0,'原旅游段讨论收益指标，recette在此是收入；应由上下文确定词义。')],
'从三个不同主题各选两词，记录词头、冠词/词性、章号和一个原创搭配；隔天不看中文造句。')

add('术语表与索引：看懂语法说明的路标','理解原书英文语法术语，并通过索引页码返回对应讲解，避免按术语名称猜规则。',
'''Glossary of grammatical terms（245–247页）先按功能理解：noun名词命名人事物/概念，verb动词表动作或状态，adjective形容词修饰名词，adverb副词修饰动词/形容词/副词，article冠词有definite与indefinite之分。pronoun代词代替名词性成分，preposition介词连接关系。Subject主语、object宾语是句中职位，不是固定词类；direct object无中介直接受动词支配，indirect object需看动词结构。

agreement配合涉及gender（masculine/feminine）、number（singular/plural）和person（一/二/三人称）；person不是问现实中有几个人。infinitive不定式是字典形，stem词干加ending词尾形成变位，regular/irregular区分是否遵循共同模式。auxiliary是avoir/être在复合时态中的助动词角色，past participle是过去分词，不等于一个完整时态。

present、passé composé、imperfect、future是本书的主要时态术语；conditional用于愿望/礼貌等，imperative用于指令。reflexive verb标有额外代词，但实际代词式结构还需看具体用法。disjunctive pronoun是介词后或强调用的重读形式，possessive forms包括物主限定词和物主代词。comparative与superlative分别比较与最高级；intonation语调、syllable音节是声音概念；word order词序是句中位置，不等于逐词中文排序。

Grammar index（248页）列adjectives、adverbs、articles、comparatives、colours、days、depuis、gender、il y a、imperative、months、negatives、numbers、plurals、prepositions、各类pronouns、questions、superlatives、time、titles、tu/vous和verbs等。用“问题→术语→印刷页→上下文”检索；例如pronouns/position of→187，depuis→139，future→197/201，que/qui→173。页码为原书印刷页，不是扫描PDF第几页。

索引是路标而非定义：同一il y a有“有”（17页）与“多久以前”（185页）两义；en数量代词重点79页，y地点代词109页；248页原图确把en也列109，属于索引交叉引用疑点，以原讲解为准。reader本节教学范围为245–248；249页出版物广告与后续封底只作版本背景，另在来源资料保留。''',
'做一张玩具图书馆地图：术语卡是书架名，页码是书架地址；“名词”积木可以坐主语椅也可以坐宾语椅。卡片名称不是完整规则，看到participe不能只拿一块分词就说自己搭好整个过去时句子。',
'''Dans cette phrase, « Léa » est le sujet. → 在这个句子里，Léa是主语。
Le mot « calme » est un adjectif ici. → calme这个词在这里是形容词。
« Venir » est un infinitif. → venir是不定式。
Dans « elle a fini », « a » est un auxiliaire. → 在elle a fini中，a是助动词。
« Fini » est un participe passé. → fini是过去分词。
Je cherche la position des pronoms dans l’index. → 我在索引里查代词的位置。
La page indiquée est une page du livre. → 标出的页码是书的印刷页。
Je vérifie la règle avec un exemple. → 我用例句核对规则。''',
[('Dans « Lina lit un roman », un roman是什么职位？',['主语','直接宾语','助动词'],1,'读什么？读一本小说，un roman是lit的直接宾语；Lina才是主语。'),('在elle a parlé中，parlé是什么？',['不定式','完整将来时','过去分词'],2,'parlé是parler的过去分词，须与a合成复合过去；不定式是parler。'),('索引标position of pronouns 187，应怎样使用？',['去印刷187页读上下文，再核自己句型','直接打开PDF187页','只背数字不用看讲解'],0,'本扫描双页合一，索引是印刷页；规则要结合上下文核对。')],
'给一个原创法语句子标主语、动词、宾语与形容词；再挑两个问题，沿248页索引找到原讲解并记页码。')

SOURCE_NOTES={
 1:['问候与语调','冠词性别','1–30及价格','菜单','电话点单故事','Test/Summary'],
 2:['复数/il y a','路线/缩合/命令式','31–69/être','地图','办公室路线故事','Test/Summary'],
 3:['时间/-er','星期/70–100/quel','-ir/疑问/否定','节目表','改约故事','Test/Summary'],
 4:['词汇/日程','缩合/动词/数字运算','旧友与新工作听力题干','餐馆广告/角色口语'],
 5:['入住/avoir/s’appeler/百千数','营地/月/-re','gîte/形容词','房产广告','酒店故事','Test/Summary'],
 6:['年龄/国籍','家人/de/物主限定词','工作/代词式动词','法语世界','职业介绍故事','Test/Summary'],
 7:['指示词/颜色/vouloir','数量/de/en','试穿/直接宾语/faire','尺码与目录','礼物故事','Test/Summary'],
 8:['点菜/重读代词/aller','间接宾语/ne plus/pouvoir','口味/种类/结账','菜单阅读','晚餐故事','Test/Summary'],
 9:['词汇与职业','试穿/口味/代词式活动','采访听力题干','订房口语'],
 10:['交通/y','车票/devoir/qui/24小时','故障/-ment','原SNCF指南','缺油故事','Test/Summary'],
 11:['身体症状/avoir','avoir复合过去/分词','il faut/否定命令','原顺势疗法症状表','生病故事','Test/Summary'],
 12:['être复合过去/配合','depuis/兴趣/频率','未完成过去','休闲统计','病后/家世故事','Test/Summary'],
 13:['兴趣/交通/身体词','戒烟时态/兴趣采访','Hastings题干与补文','医生/生活方式角色口语'],
 14:['待客/chez','比较/最高级','不规则比较/物主代词','两封手写感谢便条','拜访茶饮故事','Test/Summary'],
 15:['天气/季节','邀请/条件式','qui/que','地区天气图文','获奖邀请故事','Test/Summary'],
 16:['海外/国家介词','假期/不定式/il y a','心情/代词位置','1997旅游统计','领奖致辞','Test/Summary'],
 17:['电话留言/将来','最近过去/电话用语','约见/-re及不规则将来','CV/求职信','实习生转接故事','Test/Summary'],
 18:['词汇/反义/交际目的','祖母回忆/将来天气','Van Gogh题干与补文','电话/明信片口语'],
 19:['14单元与4Review答案','Test/Summary','开放题Example','缺音频任务核对边界'],
 20:['名词冠词','形容词','代词全类','介词','副词比较','疑问否定','时态/命令/条件','规则与不规则变位表'],
 21:['A–Z法英字母词汇','冠词与性别标记','不定式词头','多义及搭配','全书情景主题检索'],
 22:['245–247术语定义','248语法索引','广告封底属版本背景']}

def main():
 reader=json.loads((ROOT/'sources/oxford-take-off/reader.json').read_text())
 assert len(COURSE)==len(reader['units'])==22
 dest=ROOT/'french/take-off';dest.mkdir(parents=True,exist_ok=True)
 review=[]
 for n,(c,u) in enumerate(zip(COURSE,reader['units']),1):
  ident=f'T{n:02}';level='A1' if n<=10 else 'A2'
  if n in [19,21,22]:level='A1/A2'
  meta={'id':ident,'title':c['title'],'book':'take-off','book_title':'生活法语：Oxford起飞','book_fr':'Le français au quotidien','category':'情景','level':level,'section':u['title'],'prerequisites':[f'T{n-1:02}'] if n>1 else [],'minutes':18 if n not in [4,9,13,18,19,20,21,22] else 15,'status':'original-edited-draft','source_units':[f'oxford-take-off:{n}'],'source_reader':{'book_id':'oxford-take-off','unit':n}}
  notice=f'本课为依据 Oxford Take Off in French 的「{u["title"]}」（印刷{u["printed_start"]}–{u["printed_end"]}页）新增的原创中文辅助讲解；例句、比喻与练习独立编写，不是原文逐字翻译。原文、原题及原答案请展开原书阅读入口核查。原CD未提供，合成朗读不等于原录音；等级仅为教学建议。'
  examples='\n'.join('- '+line for line in c['examples'])
  quiz=[];answers=[]
  for j,(prompt,choices,correct,reason) in enumerate(c['quiz'],1):
   assert 0<=correct<len(choices)
   quiz.append(f'### {j}. {prompt}\n\n'+'\n'.join(f'- {chr(65+k)}. {choice}' for k,choice in enumerate(choices)))
   answers.append(f'{j}. {chr(65+correct)} — {reason}')
  related='、'.join(f'T{k:02}' for k in range(max(1,n-3),n)) or 'T02（城里问路）'
  body='---\n'+json.dumps(meta,ensure_ascii=False,indent=2)+'\n---\n\n# '+ident+' · '+c['title']+'\n\n## 学完能做什么\n\n'+c['goal']+'\n\n'+notice+'\n\n## 讲解\n\n'+c['explanation']+'\n\n## 给小朋友的比喻\n\n'+c['analogy']+'\n\n## 例句\n\n'+examples+'\n\n## 练习\n\n'+'\n\n'.join(quiz)+'\n\n## 答案与原因\n\n'+'\n'.join(answers)+'\n\n## 一分钟应用\n\n'+c['application']+'\n\n## 相关学习\n\n'+related+'\n\n## 参考资料\n\n- [Tex’s French Grammar — 大学语法索引](https://www.laits.utexas.edu/tex/pr/)\n- [OQLF — 法语语法与语言资料](https://vitrinelinguistique.oqlf.gouv.qc.ca/)\n\n> 语法链接供核对与继续学习；来源定位以本课标出的原书印刷页及原图为准。\n'
  (dest/f'{ident}.md').write_text(body)
  source=ROOT/f'sources/oxford-take-off/units/{n:02}.md'
  pages=sorted({b['printed_page'] for b in u['blocks'] if b.get('printed_page') is not None})
  review.append({'lesson':ident,'reader_unit':n,'source_title':u['title'],'printed_pages':pages,'pdf_pages':sorted({b['pdf_page'] for b in u['blocks']}),'reviewed_content':SOURCE_NOTES[n],'review_method':'Read ordered OCR by printed page: lesson/objective pages, dialogue and story text, Language Building explanations, cultural/document reading, Test/Summary and Review tasks; long vocabulary and answer lists checked by structure, sample entries and page headings. OCR is not a visual proofread of every glyph.','unit_text_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'examples':len(c['examples']),'independent_mcq':len(c['quiz'])})
 pdf_source=Path('/Users/ziye/Downloads/Oxford take off in French (Marie-Thérèse Bougard) (z-library.sk, 1lib.sk, z-lib.sk).pdf')
 report={'source_sha256':hashlib.sha256(pdf_source.read_bytes()).hexdigest(),'source_file':str(pdf_source),'book_id':'oxford-take-off','lesson_count':22,'order':'14 main units interleaved with 4 reviews, then Answers, Grammar Summary, Vocabulary, Glossary/Grammar index','authorship':'Original Chinese teaching, analogies, examples and independent MCQs; imported source text retained separately.','audio_status':'Original CD not supplied; no claim of original listening completion.','review':review,'editorial_cautions':[{'pages':[6,8,48,56,80],'note':'Franc/euro prices retained as historical source context; no current price inference.'},{'pages':[68,69,96,128,129,142,188,202],'note':'Demographic/statistical/travel/employment context is historical; homeopathy page is read as language data, not treatment recommendation.'},{'pages':[67,160,233,234,248],'note':'Images checked: printed é in rule explanation but lève in examples; printed je prend/partirent/croirons are source errors, not OCR errors. Printed en index repeats109. Handwritten notes read visually. Companion uses standard forms; source unmodified.'},{'pages':[137,228,230],'note':'Rules have scope limits: reflexive agreement; demonstrative ça; imperative tu final -s; infinitive groups do not determine every irregular form.'}],'visual_checks':[{'pdf_page':39,'printed_pages':[66,67],'finding':'Printed explanation says é but conjugation examples correctly show lève; companion explains è.'},{'pdf_page':86,'printed_pages':[160,161],'finding':'Read both handwritten thank-you notes; Sophie/Pierre use tu and grosses bises, Brigitte/Philippe use vous and amicalement.'},{'pdf_page':122,'printed_pages':[232,233],'finding':'Printed je prend is a source typo, standard je prends.'},{'pdf_page':123,'printed_pages':[234,235],'finding':'Printed ils partirent/ils croirons in future column are source typos, standard partiront/croiront.'},{'pdf_page':130,'printed_pages':[248,249],'finding':'Original index has en 79,109 and y 109; printed249 is publication advert.'}],'limits':'This is content review for original companions, not certification of complete glyph-level OCR correction or original-audio answers.'}
 (ROOT/'docs').mkdir(exist_ok=True)
 (ROOT/'docs/oxford-course-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'lessons':len(COURSE),'examples':sum(len(c['examples']) for c in COURSE),'quizzes':sum(len(c['quiz']) for c in COURSE)},ensure_ascii=False))
if __name__=='__main__':main()
