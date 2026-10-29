# 发音五步学习视图

## 每句的谐音梗与脑内小电影（2026-10-12）

9 册、230 课的全部 814 条教学例句都有两段独立内容：先看谐音梗抓声音，再想象脑内小电影串起人物、动作与句意。在前四个学习视图中显示，自主回忆时隐藏；下方保留分组跟读与整句播放。

`scripts/content/sentence-memories.json` 是句级内容的唯一编辑入口，按「课号:例句序号」保存原法语、原中文、声音梗和电影。保留并修整 153 条既有逐句故事，另写 661 条，替换通用演员、招牌与字幕模板。长句以熟悉的关键近音钩子连接法语节奏组，不强求每个音都配成汉字。

`scripts/sentence_memory.py` 在构建前核对每条的法语和中文，拒绝漏句、重复键、空故事与旧通用模板；改课文后必须同步审查对应故事。`prepare_site_tutor.py` 再生成注释时也读取这份逐句内容，不再自动拼接泛化场景。

谐音是声音联想，电影是脑中想象的短故事；本次没有生成或嵌入视频文件。电影里的夸张物件帮助记忆，不代替原句翻译。单词巧记、发音规则、连读标记与设备法语语音保留。

## 单词发音巧记

2026-10-12：全站 1394 个词形改用逐词编写的短口诀和具体场景，覆盖 9 册、230 课、814 条教学例句。同音词或变位可以共享声音线索，场景结合词义；每词明确给出熟悉的中文近音钩子，把关键声音与词义串进小画面；不再把只有意思的动作提示算作声音巧记。原有口形练法保留。

点击词卡，词义下面显示「谐音钩子 → 短口诀 → 小画面 → 法语慢读」。口形、声音路线和分步练法收在可展开区，在「为什么这样读」视图自动展开。原来的发音规则、整句记忆与连读标记保留；自主回忆视图隐藏提示，无声音时也能阅读。

`scripts/content/word-memories.json` 是全站巧记的编辑入口；`scripts/word_memory.py` 在构建时拒绝漏词、重复键、缺少中文声音钩子、空场景和过期条目，不自动补泛化口诀。音标拆解仍由 `web/word-memory.js` 生成，只用于展开后的口形练习。旧的机器生成汉字声音钩子不再出现在词卡详情。

中文近音帮助回忆，不能准确转写法语，也不按汉字声调念。口诀经过逐条编写及交叉审校，不等于所有词音已逐词真人听校，也不保证看一眼即可记住。[全站审校记录](word-memory-audit.md)列出范围和来源。

`tests/word_memory_check.py` 检查全部词形及音符覆盖、缺失条目拒绝、I07 切词更新、法语播放、手机显示和回忆隐藏；`tests/site_tutor_check.py` 在 230 课中逐个点击全部 4485 个词卡，核对显示的是该词的巧记。

## 全站扩展（2026-10-11）

同一套五步视图覆盖 9 册、230 课的 814 条教学例句，包含 1394 个词形。原 50 课的词音、分组、连接说明和规则口诀保留；谐音梗与脑内电影另列，在回忆视图隐藏。

新增词音由本机 eSpeak NG 生成并明确标记为合成参考，尚未逐词真人听校；dos、Agathe、字母拼写等采用显式修正。专名、同形词、地区差异和独读／句中读法应结合实际试听。新增节奏组中的“逐词提示”帮助对应词卡，不能当短语翻译；完整意思以原有整句中文和课文讲解为准。I07 三句另有定制短语释义、规则和搞笑画面，包括 les yeux 的 /z/ 与 vingt euros 的 /t/。

中文谐音是联想钩子，不是音标；无法精确表示鼻化、圆唇、辅音群，也不按普通话声调念。目前所有 814 条教学例句均采用逐句编写的故事；学习效果因人而异，不承诺听一遍即记住。

扩展数据入口位于 `scripts/content/`：

- `pronunciation-rule-memory.txt`：原 50 课规则口诀。
- `pronunciation-memory.txt`：50 课谐音梗和脑内电影。
- `site-word-meanings.txt`、`site-words.json`：新增词义、词音、拼写提示、图形类别、声音钩子和来源。
- `site-tutor.json`：180 课逐句记忆提示，保存原法语供构建时核对。
- `site-tutor-overrides.json`：定制内容优先入口，I07 的分组与故事在此。

`scripts/prepare_site_tutor.py` 使用本机 espeak-ng 生成扩展数据；常规网页构建不需要语音引擎或联网。`scripts/site_tutor.py` 验证覆盖、分组、连接和过期注释。`tests/site_tutor_check.py` 检查 814 条例句渲染、230 课手机五视图、I07 特定连接、规则保留、法语播放和注释错配拒绝。

参考：[eSpeak IPA 输出](https://espeak.sourceforge.net/commands.html)、[OQLF：euro 前的联诵](https://vitrinelinguistique.oqlf.gouv.qc.ca/23630/la-prononciation/prononciation-de-mots-particuliers/prononciation-de-euro)。

2026-10-11：初级 P01–P20、中级 M01–M15、高级 F01–F15 共 50 课、150 条例句均加入五步学习视图。

1. 意思与图解：305 个词形的宽式 IPA、中文释义、词卡与小图；按句子区分 son 等同形词，短语释义解释固定搭配与助动词。
2. 为什么这样读：按词说明字母组合、哑音、变位结尾和省音，提供与词中声音对应的中文口形提示。
3. 逐词慢读：0.65 速率，支持每项重复 1、2、3、5 遍，每遍之间留 1.4 秒跟读；点击词卡可直接听单词。
4. 一点点连起来：逐小组听读、由短到长扩展、局部连接试听、正常速度整句核对。区分联诵、原有辅音连读、省音、禁止联诵及可选变体。
5. 自己说一次：隐藏法语，根据中文和图示回忆，显示原句并自查；不会因为播放过就自动标记已学。

## 内容和声音的边界

词音采用宽式学习标注，保留弱 e 的形式与常见省去形式并存；鼻元音、/a/ 与 /ɑ/、/œ̃/ 与 /ɛ̃/ 等地区差异在词卡及对应课中提示。图画是语义记忆线索，不能单独表达冠词、时态和每种词义；实际释义与句子搭配共同解释。

声音仍由设备法语 TTS 提供。速率参数不是精确的物理倍速；单词独读与句中音值可能不同。TTS 不保证实现指定联诵、随意口语同化、语调与所有地区变体。页面不宣称提供真人原录音或自动发音评分。

## 编辑与构建

- `scripts/content/pronunciation-words.txt`：逐词 IPA、意思、图形类别、拼写原因。
- `scripts/content/pronunciation-chunks.txt`：每句意义分组与中文；构建时逐词核对是否还原原句。
- `scripts/content/pronunciation-links.json`：明确编写的相邻词连接说明；不自动猜测联诵。跨标点不套用连接。
- `scripts/pronunciation.py`：将注释合并到网页数据，并拒绝漏词、漏课、重复条目或错配分组。
- `web/pronunciation.js`：五视图和本地 SVG 记忆图。

构建 `python3 scripts/build_site.py` 后，直接打开 `index.html#F02`。所有新增资源嵌入单文件网页，不需要服务器或在线接口。

## 规则参考

以下资源用于核对分类与发音原则，解释与插画为本项目原创教学内容：

- [OQLF：元音音标与地区转写约定](https://vitrinelinguistique.oqlf.gouv.qc.ca/22205/la-prononciation/notions-de-base-en-phonetique/les-voyelles-phonetiques)
- [OQLF：必需联诵](https://vitrinelinguistique.oqlf.gouv.qc.ca/23549/la-prononciation/liaisons/contextes-de-liaisons-obligatoires)
- [OQLF：禁止联诵](https://vitrinelinguistique.oqlf.gouv.qc.ca/23552/la-prononciation/liaisons/contextes-de-liaisons-interdites)
- [University of Texas：法语音标与语音示例](https://www.laits.utexas.edu/fi/html/pho/02.html)

`tests/pronunciation_check.py` 覆盖 50 课渲染、全部图卡、手机五视图排版、无语音时阅读、法语声线、单词速率、重复间隔、停止取消、整句速率、隐藏／显示及播放不自动完成课程。语音调度使用测试替身；这验证播放请求，不等于听觉审校每一种真实设备声音。

## 逐句发音记忆口诀

50 课、150 条例句各有一句中文发音口诀，保存在 `scripts/content/pronunciation-memory.txt`。口诀提示口形、鼻化、词尾和连接，不能替代法语声音，也不保证听一遍即记住。每句附意义组节奏按钮和“分组记 → 整句说”，播放原法语，组间留出跟读空隙；回忆视图隐藏口诀。
