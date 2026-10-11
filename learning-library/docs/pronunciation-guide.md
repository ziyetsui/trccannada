# 发音五步学习视图

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
