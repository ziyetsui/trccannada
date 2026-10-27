# TCF Canada 备考页验收记录

2026-10-27。基线：`origin/publish/website`，c02edebe01b2086f40313bb7f7caff13bf7a1a6f。

## 本轮交付

- 独立备考页：`learning-library/tcf-canada/index.html`，学习库源模板与生成页面均有入口。
- 七个资料入口及逐项核验范围，听说读写原创练习建议和第一周起步安排。
- 三组原版 Oxford 图句热身：T05:2、T09:1、T21:6。保留原法语、翻译、钩子、脑内电影和原图；没有新购或替换图片。
- [Oxford 最佳实践](french-learning-best-practices.md)、[任务与插图 prompt](prompts/french-learning-task.md)、[来源核验](research/2026-10-27-tcf-resources.md)。

## 实际验证

- 基线执行 `python3 tests/check_published_site.py`：通过。
- 新路由的测试首次执行返回 404，确认能捕获尚未实现的页面；实现后通过。
- `python3 tests/test_tcf_prep.py -v`：8 项通过。包含 GitHub Pages 子路径与往返导航、重建后的入口、原图原句对应及图片解码、隐藏/揭晓答案、无法语语音、法语声音与准确原句、主题/手机/存储受限、无 JavaScript 阅读。
- 首轮新测试中两处回库链接定位同时命中页首与页尾；收窄到 header 后，8 项重新通过。未删减任何导航或降级用例。
- `python3 -m unittest discover -s learning-library/tests -v`：41 项，36 通过，5 项按现有规则跳过（公开站点不含私有原始教材）。
- 修改后再次执行 `python3 tests/check_published_site.py`：通过。覆盖原站 373 页、4250 段、537 组，学习库 9 册/230 课、法语朗读、手机布局和原有练习。
- `python3 learning-library/scripts/build_site.py`：成功；仍为 230 课、814 例句、1394 词形、482 练习、163 原版插图。
- 实看桌面、图句练习和手机深色截图；新页面在 360/390/768px 无横向溢出。
- 独立审查未发现阻塞问题；审查者独立重跑 8 项新浏览器测试，通过。
- `git diff --check`：通过。主仓库保持原分支、原提交且无文件改动。

## 使用与边界

在开发 worktree 中运行 `python3 -m http.server 8768 --bind 127.0.0.1`，打开 http://127.0.0.1:8768/learning-library/tcf-canada/ 预览。

设备语音用于合成慢读，不是考试音频；本站热身不是官方题目或分数预测。新页面的第三方资料需要联网。RFI 本轮仅确认 FEI 推荐入口，未独立读取正文。具体资料访问可能受地区、脚本和站点防护影响。

现有学习库 ZIP 的打包内容保留；新备考页作为独立网站入口交付，不声称已有 ZIP 包含它。

## GitHub 交付

已推送分支 `feat/tcf-canada-prep`，创建 [PR #4](https://github.com/ziyetsui/trccannada/pull/4)，目标分支 `publish/website`。PR 已附加到当前聊天；开发 worktree 保留用于预览与后续修改。
