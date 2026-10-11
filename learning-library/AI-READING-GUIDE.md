# 给 AI 的读取与改编说明

## 先判断资料状态

此资料库含原七份英文PDF及新增Oxford法语PDF/40篇故事EPUB的本地转换，并非校订版。不要把 OCR 或字体编码错误当成原书规则，不要声称“所有内容准确”。所有 `pdf_page` 都是 PDF 物理页码，不是印刷页码。

## 推荐读取流程

1. 读 `sources/inventory.json` 确认书目与页数。
2. 读目标册的 `contents.md`，定位知识板块。
3. 读 `pages/NNNN.md` 或筛选 `chunks.jsonl`，一次只读相关页。
4. 碰到音标、图示、表格、题干与选项配对时，核对 `images/NNNN.jpg`；不能仅凭 OCR 重建练习。
5. 需要更大或更清晰的图时，从项目根目录的源 PDF 按物理页重新渲染。
6. 输出论据标注书目 ID 和 PDF 物理页码；不能把尚未确认的印刷页码编造出来。

## 数据字段

- `book_id`：稳定的书目 ID。
- `pdf_page`：从 1 开始的物理页。
- `printed_page`：未确认时为 null。
- `extraction`：`native-layout` 或 `ocr`；前者也可能包含 PDF 自身的旧 OCR 错误。
- `text`：建议用于阅读的 Markdown。OCR 页为带代码块的纯文本转录。
- `source_text`：原生提取或 OCR 的纯文本。
- `layout_markdown`：布局工具的原始排版结果，可能有粘词、错表格和错误阅读顺序。
- `layout_boxes`：原生文本页的版面位置，供辅助定位；OCR 页没有同样的坐标数据。
- `word_confidence`：OCR 平均词置信度，不是准确率，也不是音标识别评分。
- `review_flags`：自动抽取、OCR、表格与音标需要核验的标志。
- `markdown_file` / `raw_file` / `image_file`：相对于该册目录的文件路径。

## 改编法语时的约束

- 原文抽取与原创教材分开保存。不能把生成内容插回来源文件伪装成书中内容。
- “参考框架”指学习组织方法和明确可追踪的覆盖关系，不等于逐句翻译英文书。
- 英语时态、重音、粒子与短语动词不能机械套入法语。
- 法语性数配合、冠词、代词顺序、虚拟式、联诵等必须按法语规则独立解释。
- 每个例句、题目、答案和比喻需要语义一致；比喻后写清使用边界。
- 新编教材的等级属于教学建议，不能说成考试机构认证。
- 未提供原书音频，禁止声称恢复了原音频或原听辨练习。
- 浏览器法语 TTS 可播放文字，但不能保证完美语调、口音或学习者发音评分。
- Introduction 只有节选；可借其目录编写原创补充，但须在来源关系中标明。

## 优先查看的质量信息

`sources/verification.md` 记录文件完整性与抽样发现。重点包括：音标乱码、表格列对齐丢失、OCR 把字母看成数字、图示中的文字顺序错乱。遇到这些情况先回原页核对，不自动推断答案。

## 原创法语教材的读取

从 `french/README.md` 选择分册，按固定课号读取 Markdown。JSON front matter 中的 source_units 是主题改编索引，不表示例句取自原书；具体对应见 coverage.json。status 为 original-edited-draft，不能据此声称已经真人审校。每课固定包含目标、讲解、幼儿比喻、例句、练习、答案原因、应用、相关学习与参考资料。

`index.html` 从这些 Markdown 构建，内嵌数据与脚本，可离线阅读；法语语音是否能离线播放取决于设备声音。修改课程后运行 scripts/build_site.py 同步网页。

## 新增的两份法语资料

`french/stories/S01–S40.md`按三卷10+10+20篇原序编写中文阅读辅助；`french/take-off/T01–T22.md`按Oxford14单元、4复习、答案与附录入口组织。它们本身已有法语内容，不需要机械再译成法语。

- `sources/french-stories/book.md`：完整313个spine文档；`raw/`保留EPUB原成员，`chunks.jsonl`每个spine一条。`reader.json`每故事含原文、词表、法英摘要、原题和原答案，全部原段稳定编号；`issues`保留已识别的底本错误。
- `sources/oxford-take-off/book.md`：全部131个PDF物理页的整页OCR；`halves/`按左右半页识别，`units/`按原目录定位，`reader.json`建立22个阅读入口。物理PDF6右页为印刷1页，不能把131称为印刷页数。
- 课的`source_reader`指定来源书与阅读入口。`source_units`表示原目录对应，不表示新题出自原书。`lang=fr`的来源段落可直接用法语声音播放；混排段落由用户选中法语后播放。
- 原书错误原样保留，学习时先读对应核对说明，勿把故事人物观点、缺失音频题答案或未经核对的OCR音标当成可靠规则。
