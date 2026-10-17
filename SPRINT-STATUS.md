# 用 Python 和 LangGraph 做一个有据可查的资料研究助理：进度

2026-10-17。独立免费项目课，真实模型自主工具循环为主线。

- [x] 独立目录与课程名称、大纲、README统一
- [x] 架构审批；独立性测试先失败再迁移实现
- [x] 随课research.py和N01/N02语料，移除跨课导入
- [x] 冻结依赖全新隔离安装、运行与测试留证（21项测试通过）
- [x] 代码审查及QA Retain；独立课程本地版本化
- [ ] 供应商真实模型三个场景与人工支持关系核对
- [ ] 课件/视频制作与陌生学员试学

当前Sprint：docs/sprints/sprint-03.md。早期Mini状态与证据仅作历史记录，不能当作独立运行或provider成功。

当前代码五个实现文件行覆盖82%。独立验收不代表provider实测或整课制作完成。证据：evidence/independence.md、independent-replay.json、review-independence.md。

名称修订：按用户要求恢复为《用 Python 和 LangGraph 做一个有据可查的资料研究助理》。独立目录、运行方式和两课关系不变；历史Sprint及验证记录保留当时名称。

MiniMax接入：新增Chat Completions协议与独立MINIMAX_API_KEY配置，本地.env默认空Key且忽略Git。两种协议测试中，真实MiniMax三场景仍未执行。当前任务见docs/sprints/sprint-04.md。

Sprint04完成接入与配置准备：28项测试通过，五个实现文件行覆盖93%，/rev与QA Retain。真实MiniMax Key待用户本地填写，三个provider场景未执行。

2026-10-17真实验证：MiniMax-M3已连通，首次三场景均因多工具拒绝；补单工具请求参数后无资料场景通过（3工具/4轮），正常和换问题检索N01/N02后仍多工具拒绝。保留全部真实失败证据，未标记三场景全部成功。28项本地回归通过。

QA真实验收结论：1场景通过、2场景失败，发布Revise；不能把此前代码/fixture的Retain当作真实供应商通过。当前待办见docs/sprints/sprint-05.md。

2026-10-17 Sprint06：通用多工具批次兼容完成，双协议整批预校验/逐项回填、独立调用计数、默认4轮/3工具预算及CLI配置，无模型名分支。38项测试通过。第一次批次实测2通过/1失败（空资料假引用），保留记录；收紧通用证据提示后，同模型同问题同预算三场景均通过，人工回查N01/N02。最新证据见evidence/minimax-live-2026-10-17-batch.md。整课仍待短课素材及陌生学员试学。
