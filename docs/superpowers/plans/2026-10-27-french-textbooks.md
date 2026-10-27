# 六本法语教材课程 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 六本教材先转 Markdown，按原课组织完整中文辅助微课及 Oxford 风格图句练习，并发布。
**Architecture:** 独立课程 JSON、逐课 MD、静态 HTML 构建器；私有来源外置；旧230课保持。
**Tech Stack:** Python, HTML/CSS/JavaScript, Playwright, Tesseract, EPUB XML, image_gen.
**Spec:** ../specs/2026-10-27-french-textbooks-design.md

## Global Constraints

- 原书全文、扫描图片、密钥和私人学习计划不提交。
- 图句四字段一致才可复用；每课一个精选图句和至少两项有解释练习。
- 原书定位可回查；OCR未校订页明确标注；缺A2、缺音频不补造。
- 保留原230课及163图、TCF入口；GitHub Pages子路径可用。

## Review Focus

- 长B1句在手机宽度不溢出，回忆不泄露文字。
- 非法hash、无语音、存储异常仍可使用。
- 教师书与学生书只在确认的课号对应，不推测听力答案。
- 新图像数量、否定、关系和句意核对。
- Markdown与网页例句/答案/来源一致，源全文不进入公开页面。

### Task 1: 来源完整性

- [x] 验证2 EPUB阅读顺序、资源和输出哈希，4 PDF共703物理页覆盖、源哈希与chunk/页一致。
- [x] 按真实目录建立全课来源映射，待核标签保留。

### Task 2: 教材内容

- [x] 编写简明上/下、你好A1、你好B1(教师配套)、你好4各课与复习课JSON；字段遵循content-schema.json，原文不复制。
- [x] 对照来源抽检法语、规则、答案与图句，生成逐课MD与覆盖清单。

### Task 3: 渲染与交互

- [x] 编写浏览器行为测试，验证缺路由会失败。
- [x] 构建器检查ID、来源、图句和图片哈希，生成离线可用入口。
- [x] 测试隐藏/揭晓、语音/无语音、移动端/主题/存储失败/进度、搜索和练习反馈。

### Task 4: 插图

- [x] 精确复用适合教学点的旧图句；其他逐图调用image_gen，保存prompt、模型、SHA256。
- [x] 样图审查、逐册总览、大图复核数量/否定、必要修订；无缺图后发布。

### Task 5: 验收上线

- [x] 运行新课完整性/浏览器测试，旧站check_published_site和TCF测试。
- [ ] 检查公开目录无私有原文，创建PR至publish/website，合并发布并核验真实网址。
