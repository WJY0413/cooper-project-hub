# 飞书登录误判排障与 lark-shared Skill

公开同步快照：2026-10-15。保留原文工作方法；附件与企业依赖的调整见文末。

[返回项目目录](../README.md)

当 Codex 提示飞书“未登录”“缺少 token”或“需要重新授权”时，并不一定代表实际登录已经失效。本说明用于帮助同事识别 Windows Keychain 可见性导致的误判，并使用随文档附带的 `lark-shared` skill 进行安全排障。

## 常见现象

已完成飞书授权，或此前已经成功访问飞书资源，但在 Codex 的受限执行环境中突然看到 `no_token`、`no token in keychain`、`need_user_authorization`、`token_missing` 或用户身份缺失等提示。

## 根因

Codex 的受限沙箱有时无法读取当前 Windows 用户的 Keychain（凭据存储）。此时，沙箱把仍然有效的用户 token 误判为不存在。问题在于凭据可见性，而不一定是飞书授权过期。

## 正确排查顺序

1. 保留原始 profile。若失败命令带有 `--profile`，后续检查必须使用同一个 profile。
2. 不要因为一次沙箱报错立刻重新登录、退出登录或生成新的授权链接。
3. 在能够访问当前 Windows 用户 Keychain 的上下文中，执行只读验证：

```powershell
lark-cli.cmd auth status --json --verify
```

若使用了 profile：

```powershell
lark-cli.cmd --profile <profile-name> auth status --json --verify
```

1. 若结果显示 `verified: true`、`status: ready` 或 `tokenStatus: valid`，则登录仍有效。应在 Keychain 可见的上下文中继续原操作，不要重新授权。
2. 仅当受限沙箱和 Keychain 可见环境都确认凭据无效或缺失时，才按实际所需 scope 或业务域重新授权。

## 身份分流

| 身份 | 适用范围 | 正确处理方式 |
|---|---|---|
| `user` | 用户自己的邮箱、日历、云盘和文档等资源 | 凭据真实无效时才进行最小范围的 `auth login`。 |
| `bot` | 应用自身资源和应用级操作 | 缺少权限、app secret 或应用配置时，应检查开发者后台；用户 `auth login` 不能修复 Bot 配置。 |

## 安全原则

- 不要输出或转发 app secret、access token、refresh token、device code 或 Keychain 原始内容。
- 认证状态检查是只读操作；发送消息、发送邮件、修改文档和权限变更仍需按正常授权流程执行。
- 优先按缺失 scope 增量授权，避免为了排障而无差别申请全权限。
- 在 Windows PowerShell 中，如脚本入口被执行策略阻止，优先使用 `lark-cli.cmd`。

## 随文档附件

本文档末尾附带 `lark-shared` skill 的脱敏完整包。解压后可将该 skill 放入本地 Codex skills 目录，并按其中的鉴权与 Keychain 误判规则执行。

> 原图或附件卡片未直接复制；公开下载及替代说明见文末。

## 公开下载

[下载配套 ZIP](../downloads/lark-shared-public.zip)。这是经公开检查的分享副本，不含生产客户库或凭证。
