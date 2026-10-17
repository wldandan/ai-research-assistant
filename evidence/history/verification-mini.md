# Mini迁移及真实模型接口验证

2026-10-17。macOS arm64、Python3.12.12、LangGraph1.2.11、OpenAI SDK3.14.0。

- 新目录mini的独立环境 uv sync --frozen --extra live 成功。
- uv run --frozen --extra live python -m unittest discover -s tests -v：19项通过。
- 7个初始live行为测试先失败后实现；缺失--live配置检查先失败后修复；incomplete响应误判回归先失败后修复。
- 实际SDK构造两轮请求，经本地HTTP替身返回工具调用和最终文本；禁止DNS，按call_id回传，真实SDK序列化成功。此为协议fixture，不是provider实测。
- 原始离线三场景仍通过；未配置live明确退出1，不假装完成。
- coverage：live_agent97%，demo/live_agent/reference/starter合计81%；CLI子进程未并入进程覆盖。不是全课程覆盖率。
- /arch审批后实施；/rev指出incomplete风险，修复并复审通过后进入QA。

真实供应商状态：没有完整OPENAI_API_KEY＋MINI_MODEL配置，未发送真实请求；未获得真实模型三场景记录、人工支持关系核对或真实费用。课程仍在制作，不具备整课完成声明。

历史 replay.json 保留free-course旧路径和旧代码指纹；那是迁移前实际离线运行，不适合作为当前live或修改后源码一致性证据。更新后的fixture测试和代码分别保存在tests及live_agent.py，不将它们伪标真实响应。

QA复核：Retain。工具轨迹补齐call_id、function_call_output类型、实际返回资料和模型参数；19项测试重新通过。未补供应商实测，发布门槛不变。
