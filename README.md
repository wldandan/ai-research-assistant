# 从零构建 AI 资料研究助理

一门**独立、免费、不出镜**的项目实战课。面向会基础 Python 的开发者，用真实大模型、工具调用和 LangGraph，做出能查资料、给出处、如实呈现失败的研究助理。约80分钟录播设计，另计安装与暂停练习；视频与真实模型场景验收仍在制作。

课程免费，真实模型API可能收费；当前不收款、不预售或接赞助。

## 与《AI Agent 关键技术与实践》的关系

这是两门课程，不是“大课的Mini目录”或必须连续购买的上下篇：

| | 本课 | AI Agent 关键技术与实践 |
|---|---|---|
| 目标 | 完成一个小型真实Agent项目 | 系统学习Agent关键技术与工程实践 |
| 范围 | 受控资料检索、模型选择工具、循环、引用与失败核对 | 工具、上下文、记忆、多Agent、MCP、安全、评测与恢复等 |
| 先修关系 | 不要求先学或安装另一门课 | 也不要求先学本课 |
| 代码与版本 | 本目录自带完整最小代码、语料、锁文件 | 独立维护自己的代码和交付 |

两者可以相互推荐学习，不存在运行依赖。原检索/校验/摘录函数经授权抽取改编，来源见 [SOURCE-PROVENANCE](docs/SOURCE-PROVENANCE.md)；后续各自维护，不自动同步，不要求原仓库存在。大课入口：[AI Agent关键技术与实践](https://github.com/wldandan/ai-agent-engineering-course)。本课尚未创建远端仓库。

## 课程与文件入口

- [详细大纲](OUTLINE.md)：唯一内容事实源，七节共80分钟。
- [课程简介](COURSE-BRIEF.md)、[学习成果](LEARNING-OUTCOMES.md)、[章节导航](SYLLABUS.md)、[验收要求](ASSESSMENT.md)。
- `demo.py`：命令行及可重复离线图；`live_agent.py`：真实模型自主工具循环。
- `research.py`、`data/notes.json`：本课自有检索、校验、摘录及两条受控教学笔记。
- `starter.py` / `reference.py`：路由练习与参考；[学习记录](submission-template.md)。

## 安装：只需要本课程目录

需要Python3.11+与uv；本轮验证macOS arm64、Python3.12.12。下载或复制整个本课目录后，进入含 `pyproject.toml` 的目录；无需完整Courses工作区或另一门课程。首次安装需联网下载依赖，运行时从本文件位置读取资料，不依赖终端当前目录。

```bash
# 进入下载后的 ai-research-assistant-course 目录
uv sync --frozen --extra live
```

### 真实模型主线

在本机安全配置 `OPENAI_API_KEY` 和 `RESEARCH_MODEL`；后者填账户实际可用、支持Responses function calling的模型名称。不要在代码、聊天或提交的学习记录中填写密钥。

```bash
uv run --frozen --extra live python demo.py --live --query '请根据课程资料解释 Agent loop'
```

缺配置退出1、状态configuration_required，不会静默回退离线模拟。模型自行产生工具调用与关键词；程序返回公开教学片段，模型再选择继续检索或回答。观察 `nodes/tools/evidence/answer/status`：tools含call_id、模型参数、function_call_output及实际返回资料。未检索、假引用或有证据无引用判failed；这是窄规则，不代表语义正确。

最多4轮模型、3次工具，每轮一个工具调用、最多输出600token、单请求30秒超时、零自动重试；预算耗尽明确结束，不伪造答案。未完成/截断的provider响应不判成功、不执行其中待处理工具。资源限制不是精确金额预算，请在供应商账户设置支出限制。只发公开教学问题与资料，不上传公司内部材料。关闭LangSmith跟踪，SDK请求store=False不等于供应商零保留承诺。

**当前真实接口已用SDK＋本地HTTP fixture验证，尚无供应商实际运行记录。** 要完成整课验收，仍需正常、无资料、换问题三个实际live场景及人工回查。无凭证可以先做离线练习，但不算完成真实Agent验收。

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
