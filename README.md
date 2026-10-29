# 英法汉对比研究与法语学习库

网站：https://ziyetsui.github.io/trccannada/

- 根页面保留原有章节锚点（包括 `#draft-6`），新增373页OCR、4250个段落锚点及537组逐例法语补充，提供中文解释、幼儿类比、法语朗读和明暗模式。OCR仍需对照原书校订。
- `learning-library/`：9册230课、814条新编例句、482道练习；全部例句配整句谐音梗与脑内小电影，1394个不同词形均配可点击的声音钩子、短口诀与小画面，保留慢读、发音规则及连读标记；新增40篇故事的辅助课及Oxford的22个原框架入口。完整新增书籍来源只在本机版，公开课程包不含这些全文。
- 原书PDF、第三方论文全文及研究下载缓存保留在本机。根页面的OCR与逐例补充包含在本次更新内。
- `scripts/prepare_site.py` 从已验证的本机成果生成公开目录，并移除指向未发布PDF与缓存的链接。

GitHub Pages从 `publish/website` 分支根目录发布；更新PR应以此分支为目标。

## TCF Canada 备考

[独立备考页](learning-library/tcf-canada/) 提供官方考试与样题入口、听说读写训练方法、Oxford 图句基础热身和第一周起步安排。资料核验范围与日期在页面逐项标明。

后续开发先读 [Oxford 起飞最佳实践](docs/french-learning-best-practices.md) 与 [可复用任务和插图提示词](docs/prompts/french-learning-task.md)。

## 教材学习室

[九份教材、八条学习线](learning-library/textbooks/)共289节原创辅助微课、648道练习。新增A2衔接与发音入门／纠音，每课提供来源定位、Markdown、图句回忆和可保存任务勾选。原书全文仅保留本机。
