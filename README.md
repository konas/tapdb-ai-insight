# tapdb-ai-insight
访问TapDB「AI洞察」服务的AI Skills以及python客户端实现

## 使用指南

### 1. 配置MCP KEY
mcp key是用来访问tapdb服务的密钥，具体可以在 `TapDB 页面右上角 → 账号设置 → 秘钥管理 `找到代表您身份的密钥值。

- 如果你需要访问国内的AI Inight，拷贝[国内Tapdb](https://www.tapdb.com)的密钥值写入到`TAPDB_MCP_KEY_CN`环境变量
- 如果你需要访问海外的AI Inight，拷贝[海外Tapdb](https://console.ap-sg.tapdb.developer.taptap.com)的密钥值写入到`TAPDB_MCP_KEY_SG`环境变量
- python代码会优先读取`TAPDB_MCP_KEY_CN`，所以如果你需要访问海外AI Insight，请先将执行`unset TAPDB_MCP_KEY_CN`


### 2. 示例：在cursor中使用本skill（mac os）

```shell
# 安装python和git，如果你的系统中已经安装好，可以跳过
brew install git
brew install python@3.11
# 安装skill
mkdir -p  ~/.cursor/skills
cd ~/.cursor/skills
git clone git@github.com:konas/tapdb-ai-insight.git
```

### 3. 注意事项
- 重启cursor或者执行cursor的`reload window`指令后新开一页，即可开始使用本skill。
- 建议关闭其他跟本skill存在业务重叠的skill/mcp tool,不让AI做选择题。

