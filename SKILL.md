---
name: tapdb-ai-insight
description: >
  TapDB AI Insight服务。通过聊天对话的方式能调用Tapdb的后端AI引擎，用于查询和分析TapDB 中的游戏运营数据，
  包括活跃(DAU/WAU/MAU)、  留存(1日留存-180日留存)、付费(收入/ARPU/ARPPU)、来源(新增/转化)、用户价值(LTV)、版本分布、
  玩家行为、广告变现等指标。支持国内和海外两套数据源。
  当用户需要查询游戏数据、分析运营指标、对比项目表现、检测数据异常、生成数据报告时使用此技能。
  触发关键词：TapDB、DAU、MAU、留存、付费、收入、ARPU、LTV、活跃、新增、来源、玩家行为、
  版本分布、鲸鱼用户、广告变现、运营概览、游戏数据分析。
---

# TapDB AI Insight

通过 Python 脚本调用 TapDB AI Insight接口，获取游戏的活跃、留存、付费、来源等数据指标。
使用本skill时，本质上是将用户对话托管给TapDB AI Insight，将用户的问题提交给AI Insight接口，然后将
AI Insight接口返回的信息作为回复内容展示给用户。

## 环境要求

- 查询脚本: `<SKILL_DIR>/py-scripts/ask.py`（纯标准库，无外部依赖）
- Python 3（优先用 `python3`；如环境仅有 `python`，则用 `python`）
- git（用于 Skill 更新检查）
- 认证密钥 `TAPDB_MCP_KEY_CN` / `TAPDB_MCP_KEY_SG`

## 运行前检查（每次会话首次使用）

### 1. Skill 更新


`<SKILL_DIR>`自身是一个github仓库，通过git命令来检查是否有新的版本。如果github上有新的commit，自动更新到最新版本。

### 2. 环境变量

```bash
[ -z "$TAPDB_MCP_KEY_CN" ] && echo "❌ CN 未设置" || echo "✅ CN 已配置"
[ -z "$TAPDB_MCP_KEY_SG" ] && echo "❌ SG 未设置" || echo "✅ SG 已配置"
```

缺少则**停止操作**，引导配置：秘钥在 **TapDB 页面右上角 → 账号设置 → 秘钥管理**。国内 CN/海外 SG 各需独立秘钥。用户提供后按步骤 3 写入 shell 配置文件并验证。

### 3. 持久化检查

环境变量必须写入 shell 配置文件（根据 `$SHELL` 判断，zsh → `~/.zshrc`，bash → `~/.bashrc`），确保重启终端 / 新会话后仍可用。检查配置文件中是否已包含 `TAPDB_MCP_KEY_CN` / `TAPDB_MCP_KEY_SG` 的 export 语句，缺失的自动追加并 `source` 生效，然后运行 `list_projects` 验证。

## 工作流程

1. **Skill触发**: 当用户的输入文本明显是一个数据分析类的问题，或者需要一个分析类结果时，触发本skill
2. **执行脚本**: 脚本位置在`<SKILL_DIR>/py-scripts/ask.py`，将用户的输入文本作为参数传入
3. **结果返回**: 脚本执行结束时会在输出内容中出现`<ANSWER>...</ANSWER>`的前后缀内容，处在中间的文本即为执行结果，将其输出在cursor作为回复内容
4. **错误信息**: 当遇到错误或者异常时，错误信息会出现在`<ERROR>...</ERROR>`的前后缀中间。如果出现了错误信息，则跳过结果返回检查，只将错误信息作为回复内容。

### 通用参数

| 参数   | 说明            | 示例    |
|------|---------------|-------|
| `-q` | 问题内容（用户输入的文本） | `-q '@心动小镇 2025-12-18日的收入是多少？' ` |
