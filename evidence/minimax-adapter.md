> 后续真实验证已完成一轮：MiniMax-M3三场景仅无资料通过，另两项多工具拒绝。当前结果见minimax-live-2026-10-17.md；下方“未配置/未调用”为早期历史状态。

# MiniMax接入状态

2026-10-17。新增Chat Completions分支，原Responses分支保留；真实LangGraph循环不变。

新增5项适配行为测试先失败后通过，当前完整28项测试通过；包括三类场景的**协议fixture**和OpenAI SDK到本地HTTP替身的请求/工具结果续接。DNS被阻断，未调用真实MiniMax，不是供应商成功率或三场景验收。

缺少MINIMAX_API_KEY，.env模板已准备、真实.env默认空Key并加入Git忽略。填写后才执行README的三个真实命令并人工核对证据。记录不得包含Key或模型思考文本。

新实现改变后，旧independent-replay.json中的源码指纹不再代表当前版本，只记录拆课当时验证；当前独立目录结构未改变，完整测试仍包含隔离复制场景。MiniMax配置文档与预算已同步OUTLINE及README。

/arch批准后实施，/rev指出HTTP明文凭据风险，新增失败回归并修为仅HTTPS，复审通过；QA独立重跑28项通过、Retain。当前五个实现文件行覆盖93%（live_agent96%）。不改变无真实provider记录的状态。
