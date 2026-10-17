# 最小 Demo 验证记录

2026-10-17；macOS arm64、CPython 3.12.12、LangGraph 1.2.11。

- TDD：实现前 7 项行为测试因缺失 Demo 的断言失败；实现后通过。新增过滤边界和追踪隔离检查后，当前共 9 项通过。
- 安装：独立目录 `uv lock`、`uv sync --frozen` 成功，仅声明 LangGraph，不安装三天课 SDK/MCP extra；锁文件保留全部间接依赖。
- 独立环境：`uv run --frozen python -m unittest discover -s tests -v`，9 项通过。
- 复用模块：原 workshop 的 `test_research.py` 六项通过；未改原模块。
- 覆盖：原 workshop 已有 coverage 工具测新增 demo/reference/starter，72 statements、11 missing、85% 行覆盖；CLI 子进程行为另有测试，但不计入这次进程覆盖。不是整个课程覆盖率。
- 端到端：从 /tmp 用绝对路径执行 5 次 CLI，原始 starter 无资料退出 1，参考正常/无资料/换问题退出 0，空白无效输入退出 1。原始 JSON、命令、日期、环境、相关源文件 SHA256 见 replay.json。
- 离线：默认执行无需密钥；DNS 阻断下正常案例通过。独立 /rev 审查设置 tracing 环境为 true 的新进程，节点内追踪 false，网络尝试为 0。
- 已知边界：规则判断引用编号与本次 evidence，不判语义支持；没有实际模型能力或性能声明；没有实际陌生学员试学。

## 审查顺序

/arch 批准小图适配架构；/rev 代码与安全审查通过后进入 QA。教学/QA 最终结论记录于 Sprint 状态与 review.md。

## 重放与限制

replay.json 是同一程序历史运行证据，不代表当前学员环境成功。现有课程仓库正在重排，相关 workshop 文件尚未纳入原仓库提交；本 Demo 依赖当前完整工作目录，不能单独分发本次提交就宣称已经可独立安装。公开交付前需把依赖来源纳入一致版本，或打包合适的共享模块；本轮不擅自提交课程其他未完成改动。
