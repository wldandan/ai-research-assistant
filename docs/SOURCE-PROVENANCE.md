# 独立课程代码来源

2026-10-17。用户授权从同一作者原课程复用与拆分，未引入第三方商业课程材料。

- 原位置：ai-agent-engineering-course/mini，拆分前大课提交1d13c68。
- 本课research.py中的validate_search_args/search_notes/build_report由原workshops/3-day/src/agent_workshop/research.py抽取改编，语料读取改为本课data/notes.json。
- 只携带N01/N02两条受控笔记，不携带其他案例和完整原运行器。
- demo/live_agent、starter/reference、测试与原始文档从mini迁入后由本独立课程维护。
- 此后两门课独立版本，不自动同步；需要借鉴修复时人工审查变更。无共享目录、软链接、file路径依赖、父仓安装或跨课sys.path。
- 以下指纹仅记录迁移来源，不是运行时查找位置；本课运行不读取原课程。

原research.py SHA256：28fec656e5ed2e5febac910c927162b1538e69f8626c98399ae6e95d2d7118f2
原notes.json SHA256：03aa149c2174ea98bef83a27f67f5e7d628d3bcfcd89be9981ac41cbf67ac070

原仓库参考：https://github.com/wldandan/ai-agent-engineering-course 。本地重排可能尚未推送，指纹对应本次实际本地来源。

版权归属与对外发布许可另行确认，本次迁移不自动授予新许可证。旧evidence内记录保留为历史，其旧路径不能当作本课依赖。
