# PDF → AI 可读 Markdown：调研与执行记录

研究日期：2026-10-11。源目录为 `trccanada`，不是环境上下文中的 `trccannada`。只处理用户提供的本地文件，不改写 PDF。

## 1. 这批文件的情况

| 本地书籍 | PDF 物理页数 | 检查结果 |
|---|---:|---|
| English Grammar in Use，Murphy，第五版 | 392 | 有可提取文本 |
| English Phrasal Verbs in Use | 210 | 有文本层，部分文字已有旧 OCR 错误 |
| English Phrasal Verbs in Use Advanced | 189 | 完全没有文本层，必须 OCR |
| English Pronunciation In Use — Introduction，Hancock | 19 | 部分有文本，部分为图像；是节选，不是全书 |
| English Pronunciation in Use — Elementary，Marks | 168 | 完全没有文本层，必须 OCR；音标须看页图确认 |
| English Pronunciation in Use Advanced，Hewings | 191 | 有文本层但存在音标编码问题 |
| Oxford Word Skills Advanced Idioms & Phrasal Verbs | 200 | 有文本层，存在旧 OCR 错误 |

合计 1,369 个 PDF 物理页；不根据封面或印刷末页推断 PDF 页数。

## 2. 工具比较与选择

| 方式 | 适合什么 | 本项目判断 |
|---|---|---|
| PyMuPDF `get_text()` / pdftotext | 快速提取文字、统计是否有文本层 | 用于检测和保存原始文本；不独立承担复杂教材排版还原 |
| PyMuPDF4LLM | Markdown、分页数据、布局分析、表格和标题提取 | 本次主转换工具；保留分页与布局坐标 |
| Tesseract OCR | 无文本层的扫描页 | 对低文本页单独识别英文，再转换为 Markdown |
| Docling | 统一结构化文档对象、阅读顺序和标题层级处理 | 作为后续疑难页复核的备选；本次未运行，未宣称其输出更准确 |
| 人工或视觉模型逐页重排 | 音标、图示、匹配题、复杂表格 | 高风险页必须复核；本轮自动转换不等于人工校订 |

PyMuPDF4LLM 文档提供 `page_chunks=True`，输出分页文字及页码等元数据，也支持 OCR。它解决的是抽取，不保证所有版面和音标准确。不能只看 `.md` 后缀就认为教材已经结构化完毕。[API 文档](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/api.html)。

Docling 的标题层级处理使用文档的版面和章节信息；适合作为结构化文档处理的另一条路线。[官方说明](https://docling-project.github.io/docling/usage/heading_levels/)。

## 3. Markdown 约定

正文尽量使用 CommonMark 的标题、段落、列表和图片链接。表格采用常见 Markdown 表格扩展；元数据使用 YAML front matter，这是项目约定，并非 CommonMark 标准的一部分。[CommonMark 规范](https://spec.commonmark.org/spec)。

采用两层存储：

1. **原书抽取层 `sources/`**：忠实保存原文和版面证据，不能混入原创法语内容。
2. **原创教材层 `french/`（拟建）**：按教学单元编辑，由人工可读 Markdown 作为源，再生成网页。

每本书输出：

- `book.md`：整本 Markdown，逐页排序。
- `pages/0001.md`：每个 PDF 物理页一个小文件，适合 AI 按页读取。OCR 页用代码块保留纯文本转录，避免自动表格造成粘词。
- `contents.md`：前部目录页的自动抽取，保留原书顺序。
- `chunks.jsonl`：一页一条记录，包含文本、原始提取文本、页码、提取方式、图片路径和检查标记；供检索和进一步语义切块。
- `raw/0001.txt`：原生提取或 OCR 的逐页纯文本，便于比对。
- `images/0001.jpg`：原页的视觉备份，包括插图、表格和音标。
- `ocr/0001.json`：需要 OCR 的页保留结果与平均词置信度。
- `manifest.json`：源文件 SHA-256、总页数、版本和每页索引。

物理页号和印刷页号不能混为一谈。因此 `pdf_page` 从 1 开始，`printed_page` 尚未逐页确认时留空。检索命中后，应能回到确切文件和页图。

## 4. 为什么现在按页分块

分页是可靠的来源定位边界，先保证不漏页、不失去出处。后续在编辑教材时按教学单元再切块：一课的讲解、练习和答案建立关联，不能把同一题的题干和选项切散。

整本 `.md` 便于浏览与全局搜索，逐页 `.md` 和 `.jsonl` 避免一次把整本书塞进 AI 上下文。页图不做 base64 内嵌，防止文本膨胀。原图链接方便视觉核对，但纯文本 AI 不会自动理解图中内容。

## 5. 已知质量边界

- OCR 置信度只是词级自动识别信号，不能证明语义、音标或题目对应关系正确。
- 旧 PDF 文本层自身可能已经有 OCR 错误；“native-layout”不等于人工验证。
- 英语音标可能使用自定义字体，抽成 ASCII 或特殊字符；必须看原页确认。
- 图示和录音不能靠文字抽取恢复。当前目录没有配套音频，不能声称已经恢复原书听力练习。
- 少字页包括封面、空白页、图片页；仍保留记录和原页图，不删除。
- 页级完整性校验通过后，仍需对目录、代表性讲解页、练习页和答案页做抽样核对。

## 6. 执行与复现

转换脚本：`../scripts/convert_books.py`。Python 3.13 环境在 `/tmp/trccanada-convert-venv`，不是长期依赖位置；重新建环境后可再运行。建议依赖与版本以 `sources/*/manifest.json` 为准。

```sh
uv venv .venv
uv pip install --python .venv/bin/python pymupdf4llm==1.28.2
.venv/bin/python learning-library/scripts/convert_books.py
```

建议使用 Python 3.13（本轮实际运行版本）；`finalize_sources.py` 会补存纯文本、修正 OCR 展示并检查完整性。

还需系统可执行文件 `tesseract` 和英文语言包 `eng`。脚本在每本书完成后写入清单，OCR 页有缓存；重跑会重提取原生文本，保留已生成的页图与 OCR 缓存。源 PDF 改动后应另建输出或清除旧缓存。

## 7. 调研渠道

先按 `agent-reach` 的 Exa 路线搜索。Claude Design 官方文档成功返回；其余查询出现免费配额限制，改用本会话网页检索工具核对官方来源。没有上传本地 PDF 到转换服务。
