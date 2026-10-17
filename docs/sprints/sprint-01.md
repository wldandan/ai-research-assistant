> 迁移前历史记录：旧free-course/Mini位置与名称已被独立课程替代；不作为当前运行说明。

# Sprint 01：首课最小流程

2026-10-17；用户授权实现最小 Demo；架构审查 /arch：Architecture approved，无阻塞。完整团队流程文档 `~/.Codex/TEAM_WORKFLOW.md` 本机不存在，按已提供的全局规则执行需求、架构、TDD、审查与验证。

## 范围和验收

1. 复用既有检索、摘录，新增真实 LangGraph 小图。AC：agent loop=N01、memory=N02；默认不联网，仅 N01/N02 可进入结果。
2. starter 真实控制图。AC：无资料时原始 starter 走 report 且检查失败，参考路由走 insufficient 且通过；错误状态优先且不修改输入。
3. 保留可查证结果。AC：输出含 evidence、nodes、status、error；空白/超长输入区分于无结果；引用检查拒绝假来源和非本次来源，不声称语义正确。
4. 可复现学习入口。AC：独立最小依赖锁文件，README 说明预测、修改、观察、提交和历史回放，不需要完整三日课安装。

## 架构

free-course 仅依赖 LangGraph 及相邻 workshop 的 research 模块，不修改旧运行器。图的 search 节点复用函数并过滤允许的编号；三个有界终点；starter/reference 通过函数注入。工作目录以 __file__ 定位。没有网络模型或付费入口。

架构审查要求：过滤攻击样本；报告节点与文字分开观察；引用只判归属；无效输入与空资料分开；异工作目录验证。均纳入交付。

## TDD 记录

先创建七项行为测试并运行，7 项均因“最小 Demo 尚未实现”的明确断言失败；再实现，7 项通过。测试涵盖三案例、实际路由注入、错误/空结果、引用局限与 CLI 退出码；后续边界回归见证据报告。

## 边界

默认 deterministic simulation＋真实框架调度；不包含真实 LLM、语义评分或生产能力。实现仅放新目录；原课程重排中的未提交修改不纳入本任务提交。
