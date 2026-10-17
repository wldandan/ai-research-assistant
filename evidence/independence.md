# 独立课程隔离验证

2026-10-17。验证对象：《从零构建 AI 资料研究助理》。架构审查及代码审查已通过。

## 验证方法

只将本课Git暂存的课程文件复制到临时目录，不复制`.venv`、`.git`、缓存或任何大课文件。清空PYTHONPATH、去掉VIRTUAL_ENV及项目环境覆盖项，以新建venv执行冻结安装；所有进程工作目录为`/tmp`。临时副本在验证结束后清理，运行命令及结果保存在[independent-replay.json](independent-replay.json)。

## 实际结果

- `uv sync --frozen --extra live --project <独立临时副本>` 成功，新环境安装依赖。
- 新环境执行完整unittest：21项通过，包括再次复制课程后的独立运行检查、实际SDK经本地HTTP替身的协议验证、错误及预算边界。
- 三个参考离线查询 `agent loop` / `不存在的天文星系XYZ` / `memory`：均退出0，分别走report/insufficient/report，并保留本次来源。
- 清空真实模型配置后，live CLI退出1并报告configuration_required；没有模拟回退或实际模型请求。
- 回放包含demo/live_agent/research/starter/reference/语料/依赖声明/锁文件八项源码SHA256，可与当前版本核对。证明仅针对当前这些文件，不代表视频或provider能力已完成。
- 额外开发覆盖检查：五个本课实现文件合计82%行覆盖，research92%、live_agent97%；CLI子进程不计入该进程覆盖，不是整个课程覆盖率。

## 独立性的含义

源码只导入本课模块和冻结第三方包，资料按research.py自身位置读取。不导入agent_workshop、不读取大课、不添加另一门课的sys.path；两条笔记随课交付。没有跨课软链接、本地路径包或共享工作区配置。

安装首次需要下载包，但不需要访问原课程；运行离线示例不需要模型凭证。开发者额外使用的覆盖率工具不属于学员运行依赖，独立副本的测试与三场景已在其全新环境通过。

## 边界

21项通过证明代码与本地协议契约；真实provider三个场景、人工语义核对、视频与陌生学员试学未完成。旧Mini/free-course回放移至history，只能作为历史记录。独立QA结论见review-independence.md。
