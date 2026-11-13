# AI Research Assistant：Agent工程免费入门项目

一个**独立、免费、不出镜**的Agent工程入门项目。面向会基础Python的开发者，通过约80分钟引导内容，用真实大模型、工具调用和LangGraph做出能查资料、给出处、如实呈现失败的研究助理。它采用短课式教学设计，但在产品体系中定位为Starter Project，不是Build、Run、Assure、Optimize之外的第五门核心Course。另计安装与暂停练习；三个真实模型场景已验收，视频仍在制作。

课程免费，真实模型API可能收费；当前不收款、不预售或接赞助。

## 与《AI Agent 关键技术与实践》的关系

这是两个可以独立进入的学习产品，不是“大课的 Mini 目录”或必须连续购买的上下篇：

| | 本项目 | AI Agent 关键技术与实践 |
|---|---|---|
| 目标 | 完成一个小型真实Agent项目 | 系统学习Agent关键技术与工程实践 |
| 范围 | 受控资料检索、模型选择工具、循环、引用与失败核对 | 工具、上下文、记忆、多Agent、MCP、安全、评测与恢复等 |
| 先修关系 | 不要求先学或安装另一门课 | 也不要求先学本课 |
| 代码与版本 | 本目录自带完整最小代码、语料、锁文件 | 独立维护自己的代码和交付 |

两者可以相互推荐学习，不存在运行依赖。原检索/校验/摘录函数经授权抽取改编，来源见 [SOURCE-PROVENANCE](docs/SOURCE-PROVENANCE.md)；后续各自维护，不自动同步。项目仓库：[AI Research Assistant](https://github.com/wldandan/ai-research-assistant)；大课入口：[AI Agent关键技术与实践](https://github.com/wldandan/ai-agent-engineering-course)。

## 课程与文件入口

- [详细大纲](OUTLINE.md)：唯一内容事实源，七节共80分钟规划。
- [第一节18分钟试讲稿](lessons/01-evidence-first/SCRIPT.md)、[不出镜录屏清单](lessons/01-evidence-first/RECORDING-CHECKLIST.md)与[课件/录屏素材入口](lessons/01-evidence-first/materials/README.md)：已提供10页PPTX/PDF、离线真实回放、四段无声演示与18分钟画面底片；待配音、字幕和试学。
- [课程简介](COURSE-BRIEF.md)、[学习成果](LEARNING-OUTCOMES.md)、[章节导航](SYLLABUS.md)、[验收要求](ASSESSMENT.md)。
- `demo.py`：命令行及可重复离线图；`live_agent.py`：真实模型自主工具循环。
- `research.py`、`data/notes.json`：本课自有检索、校验、摘录及两条受控教学笔记。
- `starter.py` / `reference.py`：路由练习与参考；[学习记录](submission-template.md)。

## 安装：只需要本课程目录

需要Python3.11+与uv；本轮验证macOS arm64、Python3.12.12。下载或复制整个本课目录后，进入含 `pyproject.toml` 的目录；无需完整Courses工作区或另一门课程。首次安装需联网下载依赖，运行时从本文件位置读取资料，不依赖终端当前目录。

```bash
# 进入下载后的 ai-research-assistant 目录
uv sync --frozen --extra live
```

### 真实模型主线：先用 MiniMax

已接入MiniMax的OpenAI兼容 **Chat Completions**，它与原先OpenAI Responses是两种协议，不是只换地址。使用独立的MINIMAX_API_KEY，绝不会拿OPENAI_API_KEY作为后备发给MiniMax。其他供应商不在本轮适配范围。

复制配置示例（本机已有.env时不要覆盖），只在本地填写Key：

```bash
cp .env.example .env
```

`.env` 已被Git忽略，示例不含真实密钥；程序不自行读取.env，运行时由uv的`--env-file`显式加载。

```dotenv
MINIMAX_API_KEY=在本机填写你的MiniMax密钥
MINIMAX_BASE_URL=https://api.minimax.io/v1
RESEARCH_MODEL=MiniMax-M2.5
```

示例使用官方国际站地址和文档列出的M2.5，实际权限以你的账户为准。如果使用其他区域控制台，请填写对应的兼容地址和Key；不要混用区域。兼容地址只接受HTTPS，不接受带用户名密码、查询参数或fragment的URL。不要把密钥发到聊天或提交进Git。

```bash
uv run --frozen --extra live --env-file .env python demo.py --live --provider minimax --query '请根据课程资料解释 Agent loop'
uv run --frozen --extra live --env-file .env python demo.py --live --provider minimax --query '资料中如何解释不存在的天文星系 XYZ？'
uv run --frozen --extra live --env-file .env python demo.py --live --provider minimax --query '请根据课程资料解释会话记忆 memory'
```

依次核对实际工具调用、正常查询的N01、没有资料时的不足结论、换问题的N02。真实模型可能选错关键词或违反任务要求，不能把上述预期当作已成功；应保存失败并解释。

观察nodes/tools/evidence/answer/status：tools含call_id、模型参数、role=tool的实际公开资料返回。完整assistant工具调用与思考上下文仅在内部续接，公开answer移除think段，不把推理文本写入回放。未检索、假引用或有证据无引用判failed；编号正确不代表语义支持。

默认最多4轮模型、3次工具调用（按调用数而非批次数计数），支持同轮多个工具请求，逐项执行并完整回填结果。执行前校验整批参数及唯一call_id，非法或超剩余预算则整批拒绝。可通过`--max-model-turns`与`--max-tool-calls`显式配置；模型由RESEARCH_MODEL选择，无型号特例。MiniMax每次max_tokens=4096（含思考额度），单请求60秒，零自动重试。最多4×4096生成token的预算不是精确金额上限，输入token也可能重复计费；请在供应商账户设置支出限制。长度截断、不支持的finish_reason、非法/超预算工具批次或耗尽轮数均明确失败，不伪造答案。

原OpenAI Responses路径保留：使用OPENAI_API_KEY/RESEARCH_MODEL和`--provider openai`（默认），原限制每轮600输出token、30秒。两种协议的工具结果字段不同，不混用配置。

**2026-10-17在相同MiniMax-M3、相同三个问题及4轮/3工具预算下，三场景均通过；换问题场景同轮两个工具调用成功续接。** [最新真实记录与人工核对](evidence/minimax-live-2026-10-17-batch.md)。历史失败保留，代码不绑定该型号。OpenAI仍仅有本地fixture验证。 未配置Key会明确退出，不回退模拟。只发送公开教学问题和笔记，不传入公司内部材料。关闭LangSmith跟踪，不承诺供应商零保留。

官方接口依据：[MiniMax OpenAI SDK兼容文档](https://platform.minimax.io/docs/api-reference/text-openai-api)。本轮验证记录见[evidence/minimax-adapter.md](evidence/minimax-adapter.md)。

### 离线对照和路由练习（约15–20分钟）

默认执行真实LangGraph＋确定性程序，没有真实LLM，回答是原文摘录，不是模型摘要。只做离线时可以 `uv sync --frozen`，无需live extra。安装后离线运行不需要网络、API Key或其他课程。

大纲第2–6节的一个基础练习：**无资料时，下一步应该去哪里？** 固定问题、语料、检索函数，只改变路由。运行前先写预测：空evidence后走report还是insufficient，为什么？

```bash
uv run --frozen python demo.py --solution starter --query '不存在的天文星系XYZ'
```

原始starter故意出错：退出1，nodes为 `[search, report]`，checks_passed=false。即便answer文字是“资料不足”，也不能证明路径正确——复用的摘录函数对空列表本来就返回这句话。

只修改 `starter.py::route_after_search`，不改输入、语料、检查器或参考答案：

| 条件（按顺序） | 返回 |
|---|---|
| error非空，即便也有evidence | `error` |
| 没有error、evidence非空 | `report` |
| 没有error、evidence为空 | `insufficient` |

函数不修改输入、不调用工具。保存后重跑**同一starter命令**：应退出0、nodes变为 `[search, insufficient]`。这次图加载了你的实际函数，不是孤立测试。再用agent loop和memory确认正常路径不被改坏。切换reference不算你完成练习。

```bash
uv run --frozen python demo.py --solution reference --query 'agent loop'
uv run --frozen python demo.py --solution reference --query '不存在的天文星系XYZ'
uv run --frozen python demo.py --solution reference --query 'memory'
uv run --frozen python demo.py --solution reference --query ''
```

前三条参考运行应退出0，空字符串应退出1并进入error；空白查询无效与合法查询无结果不是一回事。查看本次evidence编号和原文，不沿用上次回答。

## 判断与提交

本地填写 [学习记录](submission-template.md)：三案例的预测、实际节点、来源、回答、退出码、修改前后对照。无需公开PR或留下邮箱。来源编号检查只判“属于本次evidence”，不判断语义支持；`[N01] Agent从不需要工具` 即便通过编号检查，仍应被人工判为不受原文支持。

没有自主模型的离线结果不能冒充live；fixture只能标协议测试；实际模型跳过工具或给错结论需如实记录。

## 测试、证据与排错

```bash
uv run --frozen --extra live python -m unittest discover -s tests -v
```

测试包含原始starter故意失败的行为契约；你修正starter后，这条回归不再适用，按三案例命令验收自己的解答，不删除测试来伪造通过。

- 找不到langgraph/openai：先在本课程目录按需sync，再用uv run；不要安装另一门课修复。
- 有中文问法却无结果：这是主题子串检索、空格分词、任一词匹配、资料顺序截断，不是语义检索或完整向量RAG。
- starter退出1：先读nodes/status/error，再判断是否是预期练习失败。
- provider失败/无凭证：如实保留状态，不替换成模拟回答。

[独立运行验证](evidence/independence.md) 记录当前课程隔离安装和运行；旧mini/free-course回放仅作[历史记录](evidence/history/)，其中旧绝对路径和源码指纹不代表当前成功，也不参与运行。课堂故障可对照当前独立离线回放，但不能说成学员本机或真实模型刚成功。

本课不包含网络搜索、真实发送、生产鉴权、MCP、多Agent或长期记忆。实验解决“模型动作、程序执行、证据之间是否一致”，后续才逐步讨论更复杂工程能力。官方依据：[LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)、[Responses function calling](https://developers.openai.com/api/docs/guides/function-calling)。
