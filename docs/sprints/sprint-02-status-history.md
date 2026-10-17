> 历史状态：迁移前Mini版本，不作当前独立课状态。

# AI Agent 关键技术与实践 · Mini：进度

日期：2026-10-17

- [x] 需求与 AC，架构审查通过
- [x] 先失败测试，再实现最小图
- [x] 复用 search_notes/build_report，路由接入真实运行
- [x] 学员 README、练习与参考解答
- [x] 独立环境、运行证据和代码/教学审查（/rev 通过；QA 最小 Demo Retain）
- [ ] 真实学员试学（本轮范围外）
- [x] 真实Agent入口：模型自主工具调用、结果回传与有界LangGraph循环（fixture协议验证）
- [ ] 真实供应商三场景实测、人工核对与视频（整课发布前必需）

详细任务：docs/sprints/sprint-01.md。当前未完成项不得标为整课交付。

验证：新增 9 项通过，复用模块 6 项通过；新增实现行覆盖 85%；5 次 CLI 运行记录在 evidence/replay.json。最小 Demo 可用，尚非完整七节课程。

Sprint 02：目录迁移为mini，名称与课程仓库OUTLINE统一；早期free-course历史证据不改写为live证据。真实模型主线已实现接口，尚无供应商调用记录。

Sprint02验证：19项测试通过；含真实SDK对本地HTTP替身的两轮协议验证、incomplete响应拒绝回归。live_agent行覆盖97%，新增四个实现文件合计81%（不计CLI子进程覆盖）。/rev修复后复审通过，QA指出工具轨迹缺少call_id可见性，已先失败测试再补齐，QA复核Retain（代码及协议层）；无供应商实际调用。
