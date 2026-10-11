# 全站单词巧记审校记录

更新日期：2026-10-12。覆盖 9 册、230 课、814 条教学例句中的 1394 个不同词形，共 4485 次出现。

每个词形都明确存储 `hook`（中文声音钩子）、`line`（短口诀）、`cue`（具体小画面）。这次重新编写全部 1394 条，三段分别自审，再交换区段逐行复核；只解释意思、仅提示动作或只引用词族的旧条目不再计作声音巧记。修正建议与最终合并记录见 `word-sound-review.json`。

## 记忆线索

全部 1394 词形采用中文近音配场景。近音可以抓住关键声音，不把中文串当作完整法语音译；阴阳性、变位和语境仍由词义、原句与发音规则说明。

词卡点击后明确显示「谐音钩子 → 短口诀 → 小画面」，口形练法继续可以展开。规则、单词慢读、连读标记和 814 条整句记忆保留。

## 示例

|词|声音钩子|巧记|
|---|---|---|
|billet|毕业|毕业了，买票回家！|
|yeux|耶|眼睛喊耶，嘴巴亲亲。|
|bonjour|蹦猪|蹦猪见人，就说你好！|
|continuez|空踢＋耶|空踢也不停，继续踢到喊耶！|
|demain|等明|明天的事，等明天。|
|tête|忒|忒疼，摸摸头！|

截图中 `Continuez tout droit jusqu’au pont.` 的 `droit` 改为本句「直；笔直地（一直向前）」，修正之前显示「权利」的语境误配。

## 发音修正

修正在 `scripts/content/site-ipa-corrections.json` 中保存；重建数据时仍会应用。/ɥi/ 由前圆唇滑音接 /i/，不是两个独立元音。参见 [德州大学法语滑音课](https://www.laits.utexas.edu/fi/html/pho/07.html)。

|词形|宽式标注|
|---|---|
|as|/a/|
|bibliothèque|/biblijɔtɛk/|
|habitions|/abitjɔ̃/|
|jouent|/ʒu/|
|joues|/ʒu/|
|jeune|/ʒœn/|
|déjeune|/deʒœn/|
|d'agneau|/daɲo/|
|ressens|/ʁəsɑ̃/|
|roues|/ʁu/|
|suit|/sɥi/|
|suivi|/sɥivi/|
|nuancer|/nɥɑ̃se/|
|téléphonent|/telefɔn/|
|téléphoné|/telefɔne/|
|aujourd'hui|/oʒuʁdɥi/|
|biscuits|/biskɥi/|
|bruit|/bʁɥi/|
|conduire|/kɔ̃dɥiʁ/|
|cuillère|/kɥijɛʁ/|
|cuisinant|/kɥizinɑ̃/|
|cuisine|/kɥizin/|
|cuisiner|/kɥizine/|
|cuisinière|/kɥizinjɛʁ/|
|depuis|/dəpɥi/|
|dix-huit|/dizɥit/|
|fruits|/fʁɥi/|
|l'huile|/lɥil/|
|nuit|/nɥi/|
|nuits|/nɥi/|
|parapluie|/paʁaplɥi/|
|pluie|/plɥi/|
|puis|/pɥi/|
|puis-je|/pɥiʒ/|
|s'appuie|/sapɥi/|
|traduit|/tʁadɥi/|

词典复核入口：[as（动词与名词区别）](https://fr.wiktionary.org/wiki/as)、[bibliothèque](https://fr.wiktionary.org/wiki/biblioth%C3%A8que)、[habitions](https://en.wiktionary.org/wiki/habitions)、[joues](https://fr.wiktionary.org/wiki/joues)、[jeune](https://fr.wiktionary.org/wiki/jeune)、[déjeune](https://fr.wiktionary.org/wiki/d%C3%A9jeune)、[agneau](https://fr.wiktionary.org/wiki/agneau)、[ressens](https://fr.wiktionary.org/wiki/ressens)、[roues](https://fr.wiktionary.org/wiki/roues)、[suivi](https://fr.wiktionary.org/wiki/suivi)、[nuancer](https://fr.wiktionary.org/wiki/nuancer)、[téléphoner](https://fr.wiktionary.org/wiki/t%C3%A9l%C3%A9phoner)。变位结尾按上述词根和词条分析。

## 边界

巧记不是中文音译表。近音只提示部分关键声音，记忆效果因人而异。IPA 是宽式学习参考，除明确修正项外，扩展词音仍主要来自 eSpeak NG，未对全站逐词进行真人听校。名字、借词、弱 e 和地区口音保留差异；例如 [Montréal](https://en.wiktionary.org/wiki/Montr%C3%A9al) 的不发 /t/ 形式有词典依据，未强行改为带 /t/。

播放继续使用设备法语语音，不是新录制的真人音频；单独点击同形词时，合成器可能采用另一种词义读法，需结合整句核对。

## 验证结果

本轮构建通过；4485 次单词点击逐一核对声音钩子、口诀和小画面，230 课五种手机视图通过。单词／句子／课程单元测试共 22 项通过，原发音功能 72 项及主站 24 项浏览器检查通过。结果见 `word-memory-release-verification.json`。结构检查保证覆盖和字段完整；逐行人工交叉复核用于发现声音牵强、陌生钩子和场景关联问题，两者不能互相替代。

原 Downloads EPUB/PDF 已不在原路径，相关两项原书档案测试本次未重跑；没有改动测试制造通过。课程和网页验证不依赖这两个原文件。
