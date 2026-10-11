# -*- coding: utf-8 -*-
"""Update delivery counts from the validated source curriculum."""
from build_site import ROOT,load_library
import json,re

def update():
 lessons=load_library(ROOT/'french');n=len(lessons);examples=sum(len(l['examples']) for l in lessons);quizzes=sum(len(l['quiz']) for l in lessons)
 readme=ROOT/'README.md';s=readme.read_text();s=s.replace('已完成七份 PDF 共 1,369 页的本地 Markdown 转换，以及参考其框架编写的七册原创法语教材：168 课、531 条例句、336 道课内练习，另含定位自测、综合复习与参考表。',f'已完成八份 PDF 共 1,500 个物理页及一份 EPUB（313 个正文文档）的本地 Markdown 转换。学习库共九册、{n} 课、{examples} 条新编法语例句、{quizzes} 道课内练习，另含定位自测、综合复习与参考表。')
 s=s.replace('网页没有外部依赖。', '新增 **[故事阅读：40篇](french/stories/README.md)** 与 **[生活法语：Oxford起飞](french/take-off/README.md)**。每课“原书全文”保留对应原文、词表与原题答案，附新编中文辅助；故事法语可逐段播放，Oxford混排页可选中法语播放。[新增转换与验证](docs/additional-verification.md)。\n\n网页没有外部依赖。')
 s=s.replace('课程 ZIP 包含独立网页、全部法语 Markdown、编辑与构建脚本、调研和验证文档，以及用于追踪框架的原书目录及目录页图。完整原书逐页转换仍在本地 sources/ 中，没有打进分享包，也没有发布到公网。','课程 ZIP 包含九册新编教学、独立网页和编辑文件，保留原七书目录供查框架。完整来源文本（含新两书的网页内嵌原文）仅在本机完整版，分享包移除这部分；包内原文标签会明确提示。没有发布到公网。')
 s=s.replace('| Oxford Word Skills Advanced Idioms & Phrasal Verbs | 200 | [阅读全文](sources/oxford-idioms/book.md) | [目录](sources/oxford-idioms/contents.md) |','| Oxford Word Skills Advanced Idioms & Phrasal Verbs | 200 | [阅读全文](sources/oxford-idioms/book.md) | [目录](sources/oxford-idioms/contents.md) |\n| Oxford Take Off in French | 131（双页扫描） | [阅读全文](sources/oxford-take-off/book.md) | [目录](sources/oxford-take-off/contents.md) |\n| Learn French for Beginners — 3 in 1 Bundle | EPUB，313正文文档 | [阅读全文](sources/french-stories/book.md) | [40篇目录](sources/french-stories/contents.md) |')
 s=s.replace('合计 **1,369 页**。其中原生文本页 998 页、OCR 页 371 页。','八份PDF合计 **1,500 个物理页**。其中原生文本页 998 页、OCR 页 502 页；EPUB另按313个spine文档读取，不编造页数。原七PDF转换检查保留在原报告；新增两书另有完整性检查。')
 s+='''\n## 重建新增资料\n\n```sh\npython3 scripts/finalize_additions.py\npython3 scripts/build_site.py\npython3 -m unittest discover -s tests -v\npython3 tests/additional_books_browser.py\n```\n\n日常改课只运行build_site；import_stories.py与author_take_off.py会重新生成对应课，勿覆盖手工修改。Oxford转换需PyMuPDF、Tesseract和fra+eng模型，先运行import_oxford.py，再运行segment_oxford.py；模型路径在脚本中设为/tmp/trcc-tessdata。来源文件变更时不复用旧PDF OCR缓存。\n''';readme.write_text(s)
 p=ROOT/'french/README.md';s=p.read_text().replace('| 习语与形象表达 | 24 | [Images et expressions](idioms/README.md) |','| 习语与形象表达 | 24 | [Images et expressions](idioms/README.md) |\n| 故事阅读：40个小世界 | 40 | [40 histoires à lire](stories/README.md) |\n| 生活法语：Oxford起飞 | 22 | [Le français au quotidien](take-off/README.md) |').replace('合计 168 课、531 条例句、336 道课内选择题',f'合计 {n} 课、{examples} 条例句、{quizzes} 道课内选择题')
 s+='\n新增两书本身已有法语：S01–S40按3卷40篇原序带读，建议B1；T01–T22按14主单元、4复习、答案与附录排列，建议A1–A2。来源版保留原文词表原题答案；新课为中文辅助与独立练习。已发现底本错误逐课提示，机器OCR未全面校勘。新增62条框架对应后，共567条。\n';p.write_text(s)
 p=ROOT/'START-HERE.md';s=p.read_text().replace('7 册、168 课、531 条法语例句、336 道课内练习',f'9 册、{n} 课、{examples} 条法语例句、{quizzes} 道课内练习').replace('完整的 1,369 页原书转换在原工作目录的 learning-library/sources/，未打入此包。','完整的1,500个PDF物理页与313个EPUB文档在原工作目录的learning-library/sources/。两份新增资料全文也只在本机完整版；包内原文标签会提示使用本机完整版。').replace('教材为原创法语初稿，参考七本英文教材的教学框架进行适配与合并', '原七册为参考英文框架适配的原创法语初稿，新增两册为40篇法语故事与Oxford全书的中文辅助和独立练习')
 s=s.replace('505 条源单元编号对应','567 条框架条目对应');p.write_text(s)
 p=ROOT/'sources/README.md';s=p.read_text();s+='\n## 新增法语资料\n\n- [40篇故事EPUB](french-stories/book.md)：313个spine文档，40篇按3卷10/10/20排列，raw保存全部EPUB成员。\n- [Oxford Take Off in French](oxford-take-off/book.md)：131个双页扫描页，另按262个半页OCR定位原单元。\n- [新增完整性检查](../docs/additional-verification.md)；原七份PDF报告范围不自动扩展到新增资料。\n';p.write_text(s)
 p=ROOT/'AI-READING-GUIDE.md';s=p.read_text().replace('此资料库是用户提供的七份英文 PDF 的本地自动抽取','此资料库含原七份英文PDF及新增Oxford法语PDF/40篇故事EPUB的本地转换');p.write_text(s)
 print(json.dumps({'lessons':n,'examples':examples,'exercises':quizzes},ensure_ascii=False))
if __name__=='__main__':update()
