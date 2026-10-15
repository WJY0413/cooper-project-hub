# LinkedIn People-Search Mining｜历史说明

公开同步快照：2026-10-15。保留原文工作方法；附件与企业依赖的调整见文末。

[返回项目目录](../README.md)

本说明对应附件 LinkedIn_People_Search_Mining_Skill_For_Codex_20260805.zip。它用于在已登录的 LinkedIn People Search 结果页中采集可见卡片，并在采集完成后把原始记录写入包内的 linkedin_raw_library.sqlite。

仅处理已提供的 People Search 结果页。不要打开个人主页，不要发送连接或消息，不要做评分、公司研究或触达。

## 开始前

- 解压 ZIP，并在解压后的包根目录运行命令。
- 先阅读 linkedin-mining-v2/SKILL.md；该文件定义浏览器操作、逐页采集和终态判断。
- 任务目录、页面原文和 contacts_master.jsonl 都是原始采集记录；不要手工覆盖。

## 采集与入库流程

1. 用 init_linkedin_capture_task.py 为一个 People Search URL 创建任务目录。
2. 在结果页逐页采集。每看到一页后，立刻用 append_linkedin_raw_capture_page.py 写入该页；页面文本保存到 raw_pages/。
3. 终态必须连续两次确认没有下一页，中间保留短暂间隔；不要以一次无响应或单次页面加载失败作为完成。
4. 确认 workflow_state.status 为 complete 后，在包根目录运行 tools/ingest_completed_capture.py，参数为任务目录。

该脚本会调用 linkedin-raw-library-ingest，写入同一包内的 linkedin_raw_library.sqlite，并立即运行完整性校验。成功时会输出 ingested 状态、页面数和原始卡片数。

## 如何确认已成功

| 检查项 | 预期结果 |
|---|---|
| 任务状态 | workflow_state.status 为 complete |
| 入库回执 | ingest_status 为 ingested |
| 数据库校验 | integrity 为 ok，foreign_key_violations 为 0 |
| 可追溯性 | 每个来源页、原文、任务元数据和 contacts_master.jsonl 均保留 |

## 包内结构

- linkedin-mining-v2/：浏览器采集技能与逐页写入脚本。
- linkedin-raw-library-ingest/：完成采集后的原始库写入与验证技能。
- tools/ingest_completed_capture.py：推荐的单命令入库入口。
- linkedin_raw_library.sqlite：可直接使用的原始库，初始不含真实联系人数据。
- examples/fictional_two_page_capture/：虚构两页示例，仅用于理解与测试。

## 异常处理

如果页面加载、按钮状态或滚动位置异常，先停留在同一结果页恢复，而不是跳转到个人主页。若入库校验失败，不要删除原始任务目录；保留现有文件并根据错误信息排查后重试。原始采集入库不等于后续研究、评分或外联。

操作入口：README.md 是总览；SCRIPT_INDEX.md 说明每个脚本；两个 SKILL.md 是给 Codex 执行时读取的完整规则。

## 原附件状态与替代入口

原页面提到了 `LinkedIn_People_Search_Mining_Skill_For_Codex_20260805.zip`，但本次读取未发现附件块，本地定向查找也未找到同名包。因此没有伪造或用新版冒充该旧包。

可使用 [新版 LinkedIn 分享流程](linkedin.md) 和其 [下载包](../downloads/05-linkedin.zip)。新版提供采集和话术草稿，不包含本旧版描述的原始库入库功能。
