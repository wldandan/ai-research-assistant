> 迁移前历史记录：旧free-course/Mini位置与名称已被独立课程替代；不作为当前运行说明。

# Sprint 02：Mini定位与真实模型主线

2026-10-17。用户要求统一名称/大纲/README、目录改为Mini、真实模型参与决策。

## AC 与架构

- 目录free-course迁移mini；不保留双份实现；主课名称不变，Mini独立免费入门。
- 真实模型经Responses自主function_call，程序执行本地受限检索，按call_id回传，再由模型继续或回答。保留完整output，包括reasoning与工具消息。
- 模型最多4轮、工具最多3次，每轮仅一个工具调用、最多输出600token、30秒超时、无自动重试。此为资源预算非精确费用上限。末轮继续请求工具明确budget_exhausted。
- N01/N02白名单；原有校验不接受布尔limit、未知字段；未知工具拒绝。未检索/假引用/有证据无引用failed；来源正确不等于语义正确。
- 真实凭证显式配置OPENAI_API_KEY/MINI_MODEL，缺失退出，不静默模拟。离线路径默认不联网，仍可单独练习。

/arch有条件批准，以上限制已纳入实现。真实请求经官方SDK，显式store=False，关闭LangSmith；只传公开教学资料。

## TDD与验证

先新增7项接口行为测试，均因live_agent缺失失败，再实现通过。新增live CLI配置测试，先因缺失--live退出2失败，补接口后通过。当前测试数及审查结果见Sprint状态。测试使用协议fixture，不能标成实际provider成功。

## 课程设计

mini/OUTLINE.md是当前唯一内容大纲；spike旧大纲归history。真实LLM闭环从第3节进入，不再末节选做。课程发布前必须完成实际供应商三场景及人工证据支持检查，现阶段未完成。
