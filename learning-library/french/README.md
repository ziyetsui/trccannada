# 法语，一点点 · Français en pratique

[打开学习网页](../index.html) · [学习路线与自测](study-guide.md) · [综合复习](review.md) · [随手查](reference.md) · [原书框架对应](coverage.md)

中文讲解、法语例句，按“讲解 → 小朋友比喻 → 例句 → 练习 → 原因 → 自己应用”学习。每课约八分钟只是阅读建议；形成熟练表达需要重复练习。

| 分册 | 课数 | 目录 |
|---|---:|---|
| 语法：从句子到论证 | 42 | [Grammaire en pratique](grammar/README.md) |
| 日常表达 | 28 | [Expressions au quotidien](expressions/README.md) |
| 进阶表达 | 24 | [Expressions pour aller plus loin](advanced-expressions/README.md) |
| 发音：第一步 | 20 | [Premiers sons](pronunciation-basic/README.md) |
| 发音：连成一句 | 15 | [Parler en phrases](pronunciation-connected/README.md) |
| 发音：说得自然 | 15 | [Parler avec aisance](pronunciation-fluent/README.md) |
| 习语与形象表达 | 24 | [Images et expressions](idioms/README.md) |
| 故事阅读：40个小世界 | 40 | [40 histoires à lire](stories/README.md) |
| 生活法语：Oxford起飞 | 22 | [Le français au quotidien](take-off/README.md) |

合计 230 课、814 条例句、482 道课内选择题，另有 20 道定位自测、35 道混合复习题。每课含解释答案与应用任务。建议等级为 A1–B2，不代表官方认证或完整考试大纲。

这是参考七份英文书教学框架编写的原创法语初稿，重叠主题合并，英语特有项目按法语需要改编。505 条编号对应可在 coverage.md / coverage.json 查询；不表示复刻原书每一句、每一道练习或音频。Introduction 的源 PDF 只有节选，其余单元按目录作原创补充。

网页可直接双击打开，无需服务器。声音由浏览器和设备提供；可选择法国或加拿大法语声音、调整速度、停止播放。没有法语声音时请在系统语音设置中添加。语音合成不等于真人示范或发音评分。课程完成状态由你手动标记，保存在当前浏览器；换浏览器、移动文件或清除浏览数据可能失去进度。

教材未经过法语教师逐课审校。尤其是口音、音标与使用语境，可对照所列法语权威资源继续核验。

## 编辑与重建

“相关学习”与 prerequisites 提供建议阅读顺序，包含前一课；不是必须先完成的门槛。你可以直接进入任何一课。

课程文件使用 UTF-8 Markdown，开头 JSON 为有效的 YAML 元数据子集；固定二级标题供脚本解析。直接修改课程 Markdown 后，从资料库目录运行：

```sh
python3 scripts/build_site.py
```

需要 Python 3.10 及以上，不需要第三方依赖。网页里的“下载本课／本册 Markdown”可导出当前嵌入内容。`scripts/content/*.txt` 是本次批量编写记录，`author_curriculum.py` 会重新生成全部课文；手工改课后只运行 build_site，避免覆盖自己的修改。

页面顶部提供明／暗模式切换。首次打开跟随系统外观；手动选择后保存在当前浏览器，下次打开继续使用。

新增两书本身已有法语：S01–S40按3卷40篇原序带读，建议B1；T01–T22按14主单元、4复习、答案与附录排列，建议A1–A2。来源版保留原文词表原题答案；新课为中文辅助与独立练习。已发现底本错误逐课提示，机器OCR未全面校勘。新增62条框架对应后，共567条。
