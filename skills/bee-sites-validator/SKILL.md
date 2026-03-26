---
name: bee-sites-validator
description: |
  Bee.com Sites 深度验证技能。对 bee.com 收录的 sites 进行深度验证，
  使用 browser 真实渲染排除代理问题/临时故障，验证 sites 本身、跳转的三方网站、
  三方推特账号状态（封禁检查 + 最近更新），生成飞书云文档报告并列出确实有问题的 sites。

  **务必在以下场景使用此 Skill**：
  (1) 需要验证 bee.com sites 是否真实可访问
  (2) 需要排除代理问题/临时故障确认 sites 真实状态
  (3) 需要验证 sites 关联的三方网站和推特账号
  (4) 用户提到"sites 验证"、"sites 检查"、"bee sites 问题"、"sites 失效"
  即使用户没有明确说"验证"，只要涉及检查 bee.com sites 状态，都应使用此 Skill。
---

# Bee.com Sites 深度验证

## 概述

对 bee.com 收录的 sites 进行深度验证，覆盖：
1. 从 WordPress API 获取 sites 列表
2. HTTP 初步检测（快速筛选非 200）
3. Browser 深度验证（排除假阳性）
4. 三方网站验证
5. 推特账号验证（封禁检查 + 最近更新）
6. 生成飞书云文档报告

## 配置（首次使用必须确认）

**首次执行此 Skill 时，必须先向用户确认以下配置项。**

### 配置文件

路径：`<skill 目录>/config.json`

```json
{
  "report_folder_token": "",
  "webhook_url": "",
  "data_dir": "",
  "sites_api_url": "https://www.bee.com/wp-json/wp/v2/sites",
  "skip_domains": ["t.me"]
}
```

### 配置项说明

| 配置项 | 必填 | 说明 |
|--------|------|------|
| `report_folder_token` | ✅ | 飞书云盘文件夹 Token，报告将创建在此文件夹中 |
| `webhook_url` | ✅ | 飞书机器人 Webhook 地址，或 `"direct"` 表示当前对话回复 |
| `data_dir` | 可选 | 临时数据存放目录，默认 skill 目录下的 `data/` |
| `sites_api_url` | 可选 | WordPress sites API 地址 |
| `skip_domains` | 可选 | 跳过检测的域名列表 |

### 首次使用流程

1. 读取 `<skill 目录>/config.json`
2. 如果配置为空，向用户询问：
   > 🐝 首次使用 Sites 验证技能，需要确认配置：
   > 1. **报告存放文件夹**：请提供飞书云盘文件夹链接
   > 2. **通知方式**：飞书 Webhook 地址，或输入 `direct` 直接回复
3. 保存配置，后续自动读取

---

## 为什么这样设计

### 为什么需要两步验证（HTTP + Browser）？

- **HTTP 检测**：快速筛选，但可能误报（代理问题、DNS 污染、临时故障）
- **Browser 验证**：真实渲染，排除假阳性，确认页面实际可访问

### 为什么检查推特账号？

很多 sites 依赖社交媒体引流，推特账号封禁/停更意味着 sites 可能已废弃。

### 为什么只深度验证非 200 的 sites？

200 状态的 sites 大概率正常，聚焦资源在可疑项上提高效率。

---

## 依赖工具

| 工具 | 用途 | 必须 |
|------|------|------|
| `browser` | 页面真实渲染、snapshot、判断内容可访问性 | ✅ |
| `exec` | 执行 Python 脚本获取 sites 列表、清理文件 | ✅ |
| `feishu_create_doc` | 生成飞书云文档报告 | ✅ |
| `message` | 发送通知（webhook_url="direct"时） | ✅ |
| `read` / `write` | 读写配置文件、临时数据 | ✅ |

---

## 验证标准

### Sites 页面验证

#### ❌ FAIL（真有问题）判定标准

**1. 错误关键词（出现任意一个即 FAIL）：**
- HTTP 状态错误：`403`、`404`、`500`、`502`、`503`、`504`、`520`、`521`、`522`、`524`
- 错误文案：`Access Denied`、`Not Found`、`Forbidden`、`Internal Server Error`、`Bad Gateway`、`Service Unavailable`
- 站点状态：`Site suspended`、`Domain parked`、`Domain expired`、`Website is down`、`This site is not available`
- 安全拦截：`Cloudflare protection`、`DDoS protection`、`Security check`（但需区分假阳性）

**2. 页面空白/空内容：**
- DOM 节点数 < 10（不含 html/head/body）
- body 内几乎无文本内容（< 50 字符）
- 只有加载动画但 30 秒后仍未渲染内容

**3. 导航问题：**
- browser navigate 超时（30 秒）
- browser navigate 报错（DNS 解析失败、连接拒绝等）
- 重定向次数过多（> 5 次）

#### ⚠️ WARN（可能有问题）判定标准

**1. 需登录/授权：**
- 页面提示"Please log in"、"需要登录"、"Sign in to continue"
- 重定向到登录页（/login/、/signin/、/auth/）

**2. 重定向：**
- 重定向到非预期域名（但目标页面正常）
- 301/302 重定向（最终加载成功）

**3. 加载慢：**
- 首次加载超过 20 秒但不超过 30 秒
- 部分资源加载失败但不影响主要内容

**4. 内容少：**
- 页面有内容但很少（可能是 placeholder 页、Coming Soon 页）
- 文本 < 200 字符但 > 50 字符

#### ✅ PASS（正常/假阳性）判定标准

**必须满足以下条件之一：**
1. HTTP 200 + Browser 渲染正常 + 有实质业务内容
2. HTTP 非 200（如 403）但 Browser 渲染正常 → **假阳性，排除**
3. 有实质业务内容 + 无错误关键词 + 30 秒内加载

**实质业务内容判断：**
- DOM 节点数 > 50
- 文本内容 > 200 字符
- 包含业务相关元素（导航、内容区、页脚等）

### 三方网站验证

#### ❌ FAIL：
- 无法访问（超时/404/500）
- 域名过期（显示"Domain expired"、"Domain parked"）
- 页面显示"Site suspended"、"Website is down"

#### ✅ PASS：
- 正常渲染，有实质内容

### 推特账号验证（详细标准）

#### ✅ PASS（正常）判定标准

**必须同时满足以下条件：**
1. 账号页面正常加载（HTTP 200 或 302）
2. 显示账号基本信息（账号名、@handle、简介）
3. 显示粉丝数、关注数、发帖数（至少能看到这几个数字）
4. 时间线显示推文（至少能看到几条推文）
5. 无 FAIL 类封禁关键词
6. 最近 2 个月（60 天）内有新推文

**数据提取要求（每条推特验证必须记录）：**
- 粉丝数（Followers）
- 关注数（Following）
- 发帖数（Posts/Tweets）
- 最近推文时间（用于判断是否停更）

**示例输出：**
```
@beenetworkintl → PASS - 831.1K followers, 4,688 posts, 最近推文：2 天前
```

---

#### ⚠️ WARN（可能已废弃）判定标准

**满足以下任一条件即标记为 WARN：**

**1. 停更判断：**
- 最近 2 个月（60 天）无新推文
- 上一条推文时间 > 60 天前
- 账号有内容但长期未更新

**2. 账号不活跃：**
- 发帖数 = 0（从未发过推文）
- 粉丝数 < 100（可能是新号或不活跃）
- 关注数 = 0（可能是假账号）

**3. 内容异常：**
- 账号存在但时间线为空（可能删光了推文）
- 只能看到基本信息，推文需要登录才能查看

**示例输出：**
```
@xxx_project → WARN - 粉丝 2.3K, 但已停更 8 个月（最后推文：2025-07-15）
@yyy_official → WARN - 账号存在，但 0 条推文（从未发布）
```

---

#### ❌ FAIL（封禁/不存在）判定标准

**满足以下任一条件即标记为 FAIL：**

**1. 封禁关键词（出现任意一个即 FAIL）：**
- `Account suspended`（账号被封禁）
- `doesn't exist` / `This account doesn't exist`（账号不存在）
- `Account does not exist`（账号不存在）
- `suspended`（在页面标题或显眼位置）
- `账号不存在`（中文版）
- `已被封禁`（中文版）
- `已被冻结`（中文版）
- `This account is no longer available`（账号不再可用）

**2. HTTP 错误：**
- HTTP 404（账号页面不存在）
- HTTP 403 且页面显示错误（区分 Cloudflare 防护）

**3. 页面特征：**
- 页面只显示错误图标 + 错误文案
- 页面完全空白（无任何内容）
- 重定向到 Twitter 首页且无账号信息

**示例输出：**
```
@zzz_scam → FAIL - Account suspended（账号被封禁）
@fake_bee → FAIL - This account doesn't exist（账号不存在）
```

---

#### 📋 验证步骤（每个推特账号必须完整执行）

**方法 A：使用脚本自动化（推荐）**

1. **准备输入文件** `twitter_accounts.json`：
   ```json
   {
     "accounts": [
       {
         "id": 123,
         "site_name": "Bee Network",
         "twitter_url": "https://twitter.com/beenetworkintl",
         "snapshot": "<browser snapshot 内容>"
       },
       ...
     ]
   }
   ```

2. **执行验证脚本**：
   ```bash
   python scripts/validate_twitter.py twitter_accounts.json twitter_results.json
   ```

3. **脚本输出包含**：
   - 封禁检测结果（FAIL/WARN/PASS）
   - 粉丝数、关注数、发帖数
   - 最近推文时间
   - 统计摘要（总数/PASS/WARN/FAIL/封禁数）

**方法 B：手动验证（逐个）**

对每个推特链接：

1. **打开页面**
   ```
   browser navigate url=<twitter_url>
   ```
   - 等待加载最多 15 秒
   - 如果超时 → 标记为 FAIL（超时）

2. **获取渲染内容**
   ```
   browser snapshot → 获取完整 DOM 内容
   ```

3. **提取关键数据**
   - 账号名、@handle
   - 粉丝数（Followers）
   - 关注数（Following）
   - 发帖数（Posts/Tweets）
   - 最近推文时间（从时间线提取第一条推文时间）

4. **检查封禁关键词**
   - 扫描 snapshot 内容，检查是否包含 FAIL 类关键词
   - 特别注意页面标题、错误提示区域

5. **判断状态**
   - 有封禁关键词 → FAIL
   - 无封禁关键词但停更>60 天 → WARN
   - 无封禁关键词且近期有更新 → PASS

6. **记录结果**
   ```json
   {
     "site_id": 123,
     "twitter_url": "https://twitter.com/beenetworkintl",
     "status": "PASS",
     "followers": "831.1K",
     "following": "125",
     "posts": "4,688",
     "last_tweet": "2026-03-24",
     "reason": "账号正常，近期有更新"
   }
   ```

---

#### 🚨 特殊情况处理

| 场景 | 判定 | 说明 |
|------|------|------|
| Cloudflare 防护 | 继续验证 | HTTP 403 但能正常渲染 → 假阳性，按正常流程验证 |
| 需要登录 | 视情况而定 | 能看到基本信息（粉丝数等）→ PASS/WARN；完全看不到 → FAIL |
| 账号名变更 | PASS | @handle 变了但账号还在 → PASS，记录新@handle |
| 推文被删光 | WARN | 账号存在但 0 条推文 → WARN（可能已废弃） |
| 新注册账号 | WARN | 粉丝<100 且发帖<10 → WARN（可能是假账号） |

---

#### 📊 报告中的推特验证结果格式

**每个问题分类下都要有推特验证结果表格：**

```markdown
### 推特账号封禁（2 个）

**ID 列表：**
```
[123, 456]
```

| ID | Sites 名称 | 推特账号 | 状态 | 详情 |
|----|-----------|---------|------|------|
| 123 | XXX Project | @xxx_project | FAIL | Account suspended |
| 456 | YYY Token | @yyy_token | FAIL | This account doesn't exist |

### 推特账号停更（5 个）

**ID 列表：**
```
[789, 1011, 1213, 1415, 1617]
```

| ID | Sites 名称 | 推特账号 | 状态 | 最后推文时间 | 停更天数 |
|----|-----------|---------|------|-------------|---------|
| 789 | ZZZ Game | @zzz_game | WARN | 2025-07-15 | 254 天 |
| 1011 | AAA App | @aaa_app | WARN | 2025-09-01 | 206 天 |
```

**统计摘要（放在报告概览部分）：**
```
推特账号验证：
- 总数：X 个
- ✅ PASS: X 个（正常）
- ⚠️ WARN: X 个（停更/不活跃）
- ❌ FAIL: X 个（封禁/不存在）
- 封禁率：X%
- 停更率：X%
```

---

## 执行流程

### 第零步：加载配置
读取 `config.json`，配置为空则询问用户。

### 第一步：获取 Sites 列表
执行 `scripts/validate_sites.py` 获取 sites：
1. 分页请求 WordPress API
2. 过滤 `status=publish` 的 sites
3. 提取每个 site 的：ID、link（WP 详情页）、site-go-url（主跳转）、twitter 链接

### 第二步：HTTP 初步检测
Python 脚本已完成：
- 访问 WP 详情页
- 提取主跳转链接
- HTTP 请求主跳转链接
- **标记非 200 的 sites**

### 第三步：Browser 深度验证（非 200 sites）

🚨 **详细操作步骤（每个 site 必须完整执行）：**

1. **打开页面**
   ```
   browser navigate url=<WP 详情页 URL>
   ```
   - 等待加载最多 30 秒
   - 如果超时 → 标记为 FAIL（超时）

2. **获取渲染内容**
   ```
   browser snapshot → 获取完整 DOM 内容
   ```

3. **判断真实状态**
   - 检查错误关键词：`403`、`404`、`500`、`Access Denied`、`Not Found`、`Service Unavailable`、`Site suspended`、`Domain parked`
   - 检查页面是否为空（DOM 节点数 < 10）
   - 检查是否有实质业务内容

4. **排除假阳性**
   - HTTP 403 但 Browser 渲染正常 → **假阳性（Cloudflare 防护）**
   - HTTP 502 但 Browser 渲染正常 → **假阳性（临时故障已恢复）**
   - 标记为 `403_false_positive` 或 `502_false_positive`

5. **提取三方链接**
   - 从页面中提取官网链接（site_go_url）
   - 从页面中提取推特链接（如果有）

6. **记录结果**
   ```json
   {
     "id": 123,
     "wp_url": "https://www.bee.com/sites/123.html",
     "http_status": 403,
     "browser_status": "PASS",
     "is_false_positive": true,
     "reason": "Cloudflare bot protection"
   }
   ```

### 第四步：三方网站验证
对每个 site 的三方链接：
1. `browser navigate` 打开
2. `snapshot` 验证可访问性
3. 按「三方网站验证」标准判断

### 第五步：推特账号验证

#### 方法 A：使用脚本自动化（推荐）

1. 准备输入文件 `twitter_accounts.json`：
   ```json
   {
     "accounts": [
       {"id": 123, "twitter_url": "https://twitter.com/xxx", "snapshot": "<browser snapshot 内容>"},
       ...
     ]
   }
   ```

2. 执行验证脚本：
   ```bash
   python scripts/validate_twitter.py twitter_accounts.json twitter_results.json
   ```

3. 脚本输出：
   - 封禁检测结果（FAIL/WARN/PASS）
   - 最近推文时间
   - 统计摘要

#### 方法 B：手动验证（逐个）

对每个推特链接：
1. `browser navigate` 打开账号页
2. `snapshot` 检查封禁关键词
3. 提取最近推文时间
4. 判断是否 2 个月内更新

**封禁关键词检测清单：**
- `Account suspended`
- `doesn't exist`
- `账号不存在`
- `已被封禁`
- `已被冻结`
- `This account doesn't exist`
- `Account does not exist`

**更新时间判断：**
- 提取最近推文时间（格式：2026-03-20 或 Mar 20, 2026 或 2h ago）
- 超过 60 天无更新 → 标记为 WARN
- 封禁 → 标记为 FAIL

### 第六步：生成报告
使用 `feishu_create_doc` 创建报告：
- **文件夹**：从 `config.json` 读取
- **标题**：`🐝 Bee.com Sites 验证报告 - YYYY-MM-DD`

**报告结构（必须包含以下内容）：**

1. **概览表格**
   - 总 sites 数量
   - 有 site_go_url 数量
   - 有推特链接数量
   - HTTP 非 200 数量

2. **状态码分布表格**
   - 状态码 | 数量 | 说明

3. **ID 列表（便于批量处理）** - 放在每个分类表格上方，用代码块格式
   - 每个问题分类下都要有对应的 ID 列表
   - 403 假阳性分类也要有 ID 列表
   
   格式示例（放在每个分类标题下方、表格上方）：
   ```markdown
   ### 404 不存在（15 个）
   
   **ID 列表：**
   ```
   [5882, 5091, 4862, ...]
   ```
   
   | ID | 链接 | ... |
   ```

4. **问题 Sites 详细表格** - 每个分类一个表格
   - 404 不存在
   - 服务器错误（500/502/520/521/530）
   - 需要付费（402/415）
   - 其他错误（202/410/530 等）
   
   **每个分类的结构（必须）：**
   ```markdown
   ### 分类名称（数量）
   
   **ID 列表：**
   ```
   [id1, id2, id3, ...]
   ```
   
   | ID | 访问链接 | WP 详情页 | 状态码 |
   |----|---------|----------|--------|
   | 5882 | https://... | https://www.bee.com/sites/5882.html | 404 |
   ```
   
   要求：
   - **ID 列表**：放在分类标题下方、表格上方，用代码块包裹
   - **访问链接**：site_go_url，完整 URL 可点击直接访问
   - **WP 详情页**：bee.com 上的 sites 详情页面链接，方便对照检查
   - 按状态码分组展示
   - 每组要有小标题和数量说明

5. **假阳性说明**
   - 403 假阳性分类说明（Cloudflare 防护等）
   - 主要类别表格

6. **对比昨日（如有历史数据）**

7. **详细数据文件路径**

### 第七步：发送通知
根据 `webhook_url` 配置：
- Webhook 地址：`curl POST` 发送
- `"direct"`：当前对话回复

**通知内容：**
- 概览数据
- **真有问题 Sites ID 列表**
- **问题链接集合（可点击）**
- 报告链接

---

## 输出格式

### 飞书报告 Markdown 格式

**ID 列表格式（代码块）：**
```markdown
### 404 ID 列表
```
[5882, 5091, 4862, 4682, 4509, 4476, 4440, 4418, 4377, 4254, 4179, 4122, 4002]
```
```

**问题 Sites 表格格式：**
```markdown
### 404 不存在（15 个）

| ID | 链接 | WP 详情页 | 状态码 |
|----|------|----------|--------|
| 5882 | https://evm.ink/collections | https://www.bee.com/sites/5882.html | 404 |
| 5091 | https://app.atlasdex.finance/swap | https://www.bee.com/sites/5091.html | 404 |
```

**要求：**
- **链接**：必须是完整 URL（带 https://），可点击直接访问
- **WP 详情页**：bee.com 上的 sites 详情页面链接，方便对照
- 表格按状态码分组
- 每组标题注明数量
- ID 列表用代码块包裹，方便复制批量处理

### JSON 数据格式（用于程序处理）

```json
{
  "validation_date": "2026-03-20T09:13:16",
  "total_sites": 1912,
  "with_site_go_url": 1844,
  "with_twitter_links": 297,
  "http_non_200_count": 177,
  "status_distribution": {
    "403": 125,
    "404": 15,
    "429": 17,
    "402": 6,
    "500": 2,
    "502": 2,
    "520": 1,
    "521": 1,
    "530": 1
  },
  "problem_sites": {
    "404": [
      {"id": 5882, "url": "https://evm.ink/collections", "status": 404},
      {"id": 5091, "url": "https://app.atlasdex.finance/swap", "status": 404}
    ],
    "server_error": [
      {"id": 4325, "url": "https://dappboard.com/", "status": 500},
      {"id": 4323, "url": "https://bitgur.com/", "status": 502}
    ],
    "paid": [
      {"id": 5957, "url": "https://www.xpet.tech/", "status": 402}
    ]
  },
  "id_lists": {
    "404": [5882, 5091, 4862, ...],
    "server_error": [4325, 4323, 4373, ...],
    "paid": [5957, 5155, 51537, ...],
    "other": [4374, 4189, 3915, ...],
    "403_false_positive": [67247, 66744, ...]
  }
}
```

---

## 执行约束

- **超时**：整体不超过 60 分钟
- **单页超时**：browser 加载等待最多 30 秒
- **验证方式**：HTTP 初筛 + Browser 深度验证
- **标签页管理**：每次验证完关闭新标签页
- **准确性优先**：宁可慢也要确保结果真实可靠

## 状态标记

- ✅ PASS — 正常可访问
- ❌ FAIL — 真有问题（封禁/404/500/空白）
- ⚠️ WARN — 有异常（需登录/重定向/加载慢/停更）
