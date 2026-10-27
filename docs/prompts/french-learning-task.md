# 法语资料与课程开发提示词

基准：[Oxford 起飞最佳实践](../french-learning-best-practices.md)。把花括号内容替换成真实任务后使用。

## 继续开发一个内容模块

> 继续开发 TRC Canada，新增「{主题、适用人群、希望完成的交际任务}」。
>
> 先读 docs/french-learning-best-practices.md、既有 Oxford 起飞课程、视觉记忆设计和最终图片 manifest。以最后一版 Oxford 起飞的功能与图片为体验基准：成年人零基础，按三岁也能懂的直观程度设计。
>
> 检查本地仓库、未提交/未上传改动和上次功能去向，确认当前实际开发基线。从保留的主仓库创建独立分支和 worktree；本地确实没有仓库时，再 clone。
>
> 先核验 {资料路径或原始网址；没有则搜集对应主题的权威公开资料}，记录出处与核验日期。区分原始内容、本站原创解释与尚未核验的信息。
>
> 每个学习单元给出明确任务、中文解释、直观比喻、法语例句、发音拆解、声音钩子、脑内电影、主动练习和解释答案。配图优先保住句意，用一个场景把声音钩子与动作连接。
>
> 延续先听法语、看图理解、分组跟读、隐藏答案自己说、揭晓回听的流程。保留现有导航、搜索、语音、学习标记与主题，不把点击过当作掌握。
>
> {图片范围：复用指定 ID，或为明确数量的新增例句配图；新图先审代表样本。} 如复用图片，保持原图与原句、翻译、钩子绑定，改句后不能沿用已经不匹配的图。
>
> 更新源模板和可重建内容，验证手机、深色模式、无语音/存储受限、图句一致与既有功能。完成后 commit、push、创建以正确分支为目标的 PR，给出本地预览方式、实际验证结果和未完成项。保留主仓库。

## 单幅插图的输入模板

以下是本项目图片内容模板，按当次图片工具的参数格式提交；历史模型名不是强制要求。

```text
Use case: French sentence memory illustration for an adult absolute beginner.
Stable sentence ID: {ID}
French target, for context only: {exact French sentence}
Actual intended meaning: {Chinese meaning}
Approximate sound hook, never print: {sound association}
Mnemonic action: {one coherent interaction linking the sound hook and meaning}
Hard semantic constraints: {exact participants, quantities, negation, intention, temporal relationship}

Warm ivory background, bold charcoal outlines, flat hand-painted gouache,
restrained teal and tangerine accents, expressive adult characters, landscape 3:2.
One uncluttered scene, a large focal action and clear gestures.
The actual sentence meaning must be recoverable from the scene.
Sound-hook props must physically interact with the target action.
No comic panels or collage. Do not line up unrelated props.
Do not print the sentence, Chinese phonetics, IPA, captions, logos or watermarks.
Necessary learning-object props: {none, or the exact number/clock/letter sequence to verify}
Revision focus: {specific observed error; leave empty for first version}
```

## 每次交付必须回答

- 新增内容对应什么学习任务，来源与原创部分如何区分？
- 图、句、翻译和提示是否对上，数量/时间等硬约束是否人工看过？
- 学习者能否隐藏答案后主动表达，再听法语校准？
- 哪些验证真实跑过；哪些资料读不到、设备功能不可用或尚未完成？
- PR、开发 worktree、本地预览与最佳实践文档分别在哪里？
