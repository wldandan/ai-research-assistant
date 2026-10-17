# Sprint03：拆为独立免费课程

2026-10-17；用户明确要求两门独立课程。标题《从零构建 AI 资料研究助理》，目录Courses/ai-research-assistant-course，大课仍为《AI Agent关键技术与实践》。

## AC

- 免费课单目录自包含，无大课sys.path、import、软链接或本地包依赖。
- 复用函数抽取改编为research.py，只携带data/notes.json的N01/N02。按__file__读资源，不依赖工作目录。
- 已有离线与真实Agent行为保持；真实provider未配置状态不改变、不伪造成功。
- 仅本课程版本文件复制到临时目录，独立venv冻结安装，从其他工作目录运行三个离线案例、live缺配置和完整测试。
- 大课入口移除mini子课定位，只留可选课程关系说明；本课名称、四件套、大纲、README和spike一致。

## 架构审批

/arch批准。抽取三个小函数是去除运行耦合的必要范围；原始来源指纹记录，不要求运行时读取。父目录非Git仓，本课可独立本地Git版本化，不创建远端，不产生未声明子模块。两边后续独立维护，不引入公共平台或共享包。

## TDD

新增两个独立性行为测试：仅复制课程到临时目录、清空PYTHONPATH运行；自有模块与两条语料存在。迁移前均明确失败：缺research.py、ModuleNotFoundError agent_workshop。抽取本课模块并改本地导入后重新验收，实际结果见evidence/independence.md。

## 不变范围

不制作视频、不发送实际模型请求；不改大课重排中的其他文件。旧证据归evidence/history，并明确历史路径不等于当前依赖。新课是独立产品，不要求用户先学大课。
