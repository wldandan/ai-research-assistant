# 第一节课件制作大纲

中文 / blueprint / Python初学者 / 10页 / 18分钟讲师主导。用户已确认直接生成，阶段检查由代理完成。讲稿是内容权威，实际演示使用独立回放页，图稿不冒充原始日志。

<STYLE_INSTRUCTIONS>
Design Aesthetic: Precise technical blueprint educational presentation. Warm off-white #FAF8F5 background, very faint engineering grid #E5E5E5. Deep slate #334155 text, engineering blue #2563EB and navy #1E3A5F, light blue #BFDBFE; amber #F59E0B only for cautions. Bold, clean, highly legible simplified Chinese sans-serif titles and body. Generous margins and whitespace. Thin precise straight or right-angle connections; no photographs, no gradients, no organic drawing. One central visual idea per slide. No slide numbers, footer, logos, fake screenshots or extra text. Exact Chinese words below only, no invented text. 16:9 landscape, preferably 1920x1080 or larger equivalent. Technical editorial quality, speaker-led classroom slides. All content at large readable scale.
</STYLE_INSTRUCTIONS>

## 01 怎样判断 Agent 的回答有依据？

时间锚点：00:00–01:20。用 Python 和 LangGraph 做一个有据可查的资料研究助理

- 第一节 · 18分钟

视觉：A striking cover with one large blue outlined evidence document icon on the right connected by a thin line to a smaller speech bubble with a bracket-source icon. Main title left across two lines, subtitle smaller beneath. Tiny label only: 第一节 · 18分钟. No people, no robot mascots.

## 02 资料库只有两条笔记

时间锚点：01:20–03:10。编号用来定位，正文才是依据

- N01 · Agent loop
- 模型决定动作 → 执行工具 → 观察回传 → 继续或停止
- 最大轮次限制防止无界循环
- N02 · 会话记忆
- 保存此前对话；保留系统目标及近期有效资料
- 不同会话应隔离

视觉：Two equal spacious note sheets side by side, headed N01 and N02. Left sheet has blue circular-loop schematic and exact content shown below; right sheet stacked message shapes and its exact content. Do not draw bidirectional arrows between the two notes.

## 03 先看真实记录，再讨论实现

时间锚点：03:10–04:20。2026-10-17 · 真实API历史记录回放

- 最多 4 轮模型
- 最多 3 次工具调用
- 本次模型：MiniMax-M3
- 模型由配置选择
- 调用上限不是精确费用上限

视觉：Three horizontally aligned columns like a restrained technical fact sheet. Main emphasis: 4 and 3 large numeral limits, and model configuration. MiniMax-M3 appears only in the third column as recorded condition, not in title. Clear thin dividers. Bottom one caution phrase.

## 04 谁决定去查资料？

时间锚点：04:20–08:00。模型选择动作，程序执行受限工具

- model
- 选择检索词
- 工具参数
- tools
- Python检索
- 实际结果
- model
- 读取结果再回答
- N01

视觉：Clean left to right three-node technical flow: first box model with caption 选择检索词, second box tools with caption Python检索, third box model with caption 读取结果再回答. Arrow first to second labeled 工具参数; arrow second to third labeled 实际结果. Under it a compact source document N01 connected to tools only, not directly to answer. Make all arrows unambiguous.

## 05 正常查询：回查 N01 原文

时间锚点：04:20–08:00。请根据课程资料解释 Agent loop

- 实际检索：Agent loop → N01
- 原文：模型决定动作，执行工具，把观察结果交回模型，再决定继续或停止。最大轮次限制防止无界循环。
- 核对：循环步骤与轮次限制均有依据
- 2轮模型 · 1次工具 · report

视觉：Two vertically aligned reading panels. Left labelled 实际检索: exact keyword and source text. Right labelled 人工核对: exact supported ideas, no extra claims. Small metadata at bottom of the body in one line. Use blue ruled line to visually connect source and supported summary.

## 06 没有资料：承认不足也是合格结果

时间锚点：08:00–10:30。XYZ星系的问题，没有对应的课程笔记

- 检索：XYZ galaxy astronomy
- 工具返回：[]
- 资料不足：当前课程资料没有匹配内容。
- 2轮模型 · 1次工具 · insufficient
- 当前资料无匹配 ≠ 世界上没有答案

视觉：Simple technical path left to right: search query → empty list [] → a restrained amber result card. Emphasize exact short insufficient answer as central. Keep caution about no matches vs universal truth on bottom body line, no invented astronomy picture.

## 07 同一轮，两个工具请求

时间锚点：10:30–13:20。模型提出一批请求，程序逐项执行并完整回填

- 会话记忆 memory → N02
- memory agent loop → N01 / N02
- 逐项执行
- 最终引用 N02
- 2轮模型 · 2次工具 · report
- 检索词、次数以实际记录为准

视觉：Precise sequence schematic: model single box at top left sends two numbered tool-request strips inside one large tools group, strip1 会话记忆 memory → N02, strip2 memory agent loop → N01 / N02. Both results converge to model answer box labelled 最终引用 N02. Do not draw parallel lanes, processor concurrency symbols, or arrows implying parallel execution. Explicit caption 逐项执行. Include budget count bottom.

## 08 真编号，也可能配上错误结论

时间锚点：13:20–15:20。手工构造的教学反例 · 不是模型真实输出

- 原文 N01：最大轮次限制防止无界循环。
- 反例：[N01] Agent 能自动完成所有任务。
- 原文没有保证所有任务均能完成
- 编号检查还需要人工语义核对

视觉：Split composition. Left blue source note with exact source text. Right amber outlined quote bubble with false sentence and large amber question mark. Underline unsupported words 所有任务 in amber. A bottom verdict explains the gap, clearly showing it is not supported. No celebratory check mark on the false sentence.

## 09 真实失败必须保留

时间锚点：13:20–15:20。首次批次验证：空结果后仍出现假引用

- 实际证据为空：[]
- 回答却引用：[N01]
- failed
- 本次失败已保留；最终记录另存
- 单次通过不代表次次可靠

视觉：Restrained evidence audit diagram: left card actual [] with label 实际证据为空, right card quoted small [N01] with label 回答却引用N01, clear amber cross and failed status beneath. No fake log screenshot, no made-up full answer. Bottom text: 本次失败已保留；最终记录另存. Do not imply reliability rate.

## 10 用三行答案，检查一次回答

时间锚点：15:20–18:00。先自己判断，再回到记录核对

- ① 模型选择了哪些检索词？
- ② N02在哪里实际返回过？
- ③ 哪句原文支持“不同会话应隔离”？
- 下一节：search_notes 接收什么，返回什么？

视觉：Large clean educational checklist with three numbered questions in center-left, ample space and thin rule separators, a simple small source note icon on right. Bottom thin blue rule with next-lesson cue, no thanks or marketing.
