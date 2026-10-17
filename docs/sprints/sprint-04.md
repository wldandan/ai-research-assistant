# Sprint04：MiniMax OpenAI兼容接入

2026-10-17；用户选择先用MiniMax。/arch批准兼容层：不替换已有Responses，通过protocol分流Chat Completions，LangGraph主循环复用。

## AC

- --provider minimax只读取MINIMAX_API_KEY、MINIMAX_BASE_URL和RESEARCH_MODEL；不回退到OpenAI key。
- Chat工具定义、完整assistant/tool_calls/reasoning上下文、role=tool/tool_call_id回填与官方兼容文档一致。
- 最多4模型轮/3工具，一轮多工具整体拒绝，length等未完成响应明确失败。
- MiniMax max_tokens4096（含思考）、单请求60秒、零自动重试；OpenAI原预算保持。
- 私有思考不进入公开answer/证据；base URL校验，不输出Key或敏感异常文本。
- .env.example可公开，实际.env忽略Git；uv --env-file显式加载。
- 三真实场景待Key配置，未执行前只标协议验证。

## TDD

新增5个MiniMax行为测试先失败（缺protocol/CLI provider），再补接入层通过。涵盖正常/无资料/变化输入、完整消息续接、截断/并行拒绝、预算停止、凭据不混用、真实SDK经HTTP替身的Chat序列化。原21项测试继续保持。

## 来源与范围

官方：https://platform.minimax.io/docs/api-reference/text-openai-api 。使用官方全球兼容地址为默认配置；模型M2.5是可修改示例。未读取其他应用保存的密钥，未发送真实请求。
