# 发布验证（2026-10-11）

目标分支：`publish/website`（GitHub Pages实际发布来源）。根页保留 `#draft-6` 及原研究稿锚点。

- `python3 -m unittest discover -s learning-library/tests -v`：7项课程检查通过；5项需本机完整源文件的测试在公开版明确跳过（本机版先前12项全部通过）。
- `python3 learning-library/tests/browser_check.py`：24项通过。
- `python3 learning-library/tests/theme_check.py`：9项通过。
- `python3 tests/check_published_site.py`：真实HTTP目录验证根页373页、4250原文段落、537组补充、逐例定位、跨行搜索、法语声音路由、明暗记忆、手机宽度；学习库9册230课、8个新课路由与练习、来源缺失说明和返回入口均通过。根页本地文件及锚点链接均有效，无重复ID和JS错误。

浏览器朗读检查使用模拟法语声音验证调用；真实发声仍依赖设备安装的法语声音。OCR不是逐字校勘定本。

两本新增书籍的源全文不部署；逐例对比研究的OCR嵌入根页，Markdown在docs/source下。PDF、第三方论文缓存不部署，页面对应链接改为本机档案说明。

上线后可运行 `python3 tests/check_published_site.py --url https://ziyetsui.github.io/trccannada/` 复验实际站点。
