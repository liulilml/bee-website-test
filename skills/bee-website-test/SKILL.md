---
name: bee-website-test
description: |
  Bee.com 网站全面自动化测试技能。对 www.bee.com 进行深度测试：动态抓取首页所有分类及站点链接，
  使用浏览器真实渲染验证每个 URL 的可达性和内容正确性，深度测试 Games/DApp Store/Bee Hive/AD 页面的
  交互功能（点击跳转、表单提交、轮播切换、下载验证），生成飞书云文档报告并与前一天结果对比。

  **务必在以下场景使用此 Skill**：
  (1) 需要对 bee.com 执行定时自动化测试
  (2) 用户要求测试 bee.com 网站链接可达性、页面渲染、交互功能
  (3) 需要生成 bee.com 测试报告
  (4) 用户提到"bee 测试"、"bee.com 测试"、"网站测试"、"bee 网站检查"
  (5) 需要验证 bee.com 的 DApp、游戏、新闻等内容是否正常加载
  即使用户没有明确说"测试"，只要涉及检查 bee.com 页面是否正常，都应使用此 Skill。
---

# Bee.com 网站自动化测试

## 概述

对 www.bee.com 进行全面的自动化测试，覆盖页面可达性、内容渲染、导航链接、分类站点、
深度交互（点击跳转、表单、轮播、下载）等，生成结构化的飞书云文档报告，并与前一天结果对比。

---

## 🚨🚨🚨 执行纪律 —— 必读（违反任何一条即为不合格测试）

### ❌ 绝对禁止的行为

1. **禁止跳过任何测试步骤**：每一步（第一步到第十六步）都必须执行，不允许"为了节省时间"跳过
2. **禁止抽样代替全量**：标注"全量"的步骤必须逐个验证，不能"选几个代表性的"
3. **禁止页面级代替点击级**：要求"逐个点击验证"的步骤，必须真的点击每一个，不能只看页面快照
4. **禁止伪造数据**：所有数据必须来自实际浏览器操作，不能根据经验/历史猜测结果
5. **禁止合并简化**：每个测试项独立记录，不能用"其余均正常"概括

### ✅ 必须遵守的规则

1. **计数器机制**：全量测试必须维护计数器，格式：`[X/N]`（X=当前序号，N=总数）
2. **进度汇报**：每完成 20 个项目，在工具调用间打印进度日志
3. **证据链**：每个测试结果必须有 snapshot 或 screenshot 作为证据
4. **完成度校验**：每个大步骤结束时，对比计划数量和实际数量，不匹配则补测

### 📊 完成度检查清单（报告生成前必须逐项确认）

生成报告前，必须逐项核对以下清单。任何一项未完成，**必须回去补测**，不能直接生成报告：

- [ ] 基础页面：9 个 URL 全部验证 ✓
- [ ] 分类站点：从首页提取的所有 `/sites/XXXX.html` 链接全部验证 ✓
- [ ] 新闻/文章：首页提取的所有文章链接全部验证 ✓
- [ ] Games：所有游戏卡片逐个点击验证 ✓（记录：X/N）
- [ ] DApp Store：所有 DApp 卡片逐个点击验证 ✓（记录：X/N）
- [ ] DApp 搜索：3 个存在 + 2 个不存在搜索测试 ✓
- [ ] Bee Hive 轮播：Next/Prev 切换 3+ 次并截图 ✓
- [ ] Bee Hive 新闻：前 10 条新闻链接点击验证 ✓
- [ ] AD 表单：表单填写 + 提交 + Media Kit 链接验证 ✓
- [ ] 下载功能：APK/App Store/Google Play 验证 ✓
- [ ] 外部链接：充值页面验证 ✓
- [ ] 社交媒体：**所有** 8 个社媒链接全部验证 ✓（不是 2 个！）
- [ ] 登录按钮：验证存在且可点击 ✓
- [ ] 悬浮按钮：置顶/推特/任务版 ✓
- [ ] 前一天对比：读取并对比 previous.json ✓

---

## ⚙️ 配置（首次使用必须确认）

**首次执行此 Skill 时，必须先向用户确认以下配置项。** 确认后保存到配置文件中，后续执行自动读取。

### 配置文件

路径：`<skill 目录>/config.json`（与 SKILL.md 同级）

```json
{
  "report_folder_token": "",
  "webhook_url": "",
  "data_dir": "",
  "quick_mode": false,
  "sample_rate": 0.2
}
```

### 配置项说明

| 配置项 | 必填 | 说明 |
|--------|------|------|
| `report_folder_token` | ✅ | 飞书云盘文件夹 Token，测试报告将创建在此文件夹中。用户需要提供一个飞书云盘文件夹链接或 Token。 |
| `webhook_url` | ✅ | 飞书机器人 Webhook 地址，用于发送测试结果通知。格式：`https://open.feishu.cn/open-apis/bot/v2/hook/xxx`。如果用户在当前对话中直接使用（非 cron 定时），可以填 `"direct"` 表示直接在当前对话回复结果。 |
| `data_dir` | 可选 | 对比数据文件 `bee-test-previous.json` 的存放目录。默认为 skill 目录下的 `data/`。 |
| `quick_mode` | 可选 | 是否启用快速模式（抽样测试）。默认 `false`（全量测试）。设置为 `true` 时抽样 20% 站点/Games/DApp。 |
| `sample_rate` | 可选 | 快速模式抽样比例，默认 `0.2`（20%）。 |

### 首次使用流程

1. 读取 `<skill 目录>/config.json`
2. 如果文件不存在或配置项为空，**必须暂停测试，先向用户询问**：

   > 🐝 首次使用 Bee.com 测试技能，需要确认两个配置：
   >
   > 1. **报告存放文件夹**：请提供一个飞书云盘文件夹链接，测试报告会创建在里面
   > 2. **通知方式**：请提供飞书机器人 Webhook 地址（用于接收测试结果通知），或输入 `direct` 在当前对话中直接回复

3. 用户提供后，保存到 `config.json`
4. 后续执行自动读取配置，无需再次询问

### 配置变更

用户随时可以说"修改报告地址"或"修改通知方式"来更新配置。

---

## 为什么这样设计

### 为什么用 browser 而不是 web_fetch？

bee.com 大量使用 SPA（单页应用）+ iframe 架构。`web_fetch` 只能拿到服务端返回的原始 HTML，
无法执行 JavaScript，这意味着：
- iframe 内的内容（DApp Store、Bee Hive、AD 页面的主体）完全看不到
- JS 动态渲染的游戏列表、DApp 卡片等不会出现
- 服务器可能返回 HTTP 200 但页面实际显示 403/错误——`web_fetch` 无法识别

使用 `browser` 可以真实渲染页面，通过 `snapshot` 获取 JS 执行后的完整 DOM，准确判断内容是否正常。

### 为什么需要直接访问 iframe 源地址？

bee.com 的 DApp Store、Bee Hive、AD 页面都是外层壳子 + iframe 嵌入的结构。
在外层页面操作 iframe 内的元素不可靠（点击可能跳出 iframe、snapshot 可能只拿到壳子）。
直接访问 iframe 源地址（`wp.bee.com/en/xxx`）可以稳定地操作和验证内容。

### 为什么 DApp Store 和 Games 要全量测试？

这些是 bee.com 的核心功能页面，每个卡片都需要验证点击后能正确打开、内容正常渲染。
跳过任何一个都可能漏掉线上问题。

---

## 依赖工具

| 工具 | 用途 | 必须 |
|------|------|------|
| `browser` | 页面渲染、snapshot、点击交互、表单填写、标签页管理 | ✅ |
| `exec` | 执行 curl 验证下载链接、检查/清理下载文件 | ✅ |
| `feishu_create_doc` | 生成飞书云文档测试报告 | ✅ |
| `message` | 发送测试结果通知（当 webhook_url 为 "direct" 时直接回复） | ✅ |
| `read` / `write` | 读写配置文件和对比数据文件 | ✅ |

---

## 重要技术背景

### iframe 结构

以下页面的主体内容加载在 `#iframe_layout` 中，测试时必须直接访问 iframe 源地址：

| 页面 | 外层 URL | iframe 源地址 |
|------|----------|---------------|
| DApp Store | `https://www.bee.com/dappStore/` | `https://wp.bee.com/en/dappStore` |
| Bee Hive | `https://www.bee.com/beeHive/` | `https://wp.bee.com/en/beeHive` |
| AD (Advertise) | `https://www.bee.com/advertise/` | `https://wp.bee.com/en/advertise` |

**Games 页面（gamecenter）没有 iframe**，可以直接在 `https://www.bee.com/gamecenter/` 操作。

### 新标签页行为

DApp Store、Bee Hive 中点击卡片/链接通常会**新开标签页**（`target="_blank"`）。测试流程：
1. 在列表页点击卡片/链接
2. 用 `browser tabs` 检查是否新增了标签页
3. 切换到新标签页（`browser snapshot targetId=<新标签 ID>`）验证内容
4. 验证完成后关闭标签页（`browser act kind=close targetId=<新标签 ID>`）
5. **每次验证完必须关闭标签页**，防止堆积导致浏览器性能下降

---

## URL 验证标准（全局适用）

```
browser navigate url=<URL> → 等待加载 (最多 15 秒) → browser snapshot → 判断规则
```

### ❌ FAIL（失败）判定标准

**1. 错误关键词（出现任意一个即 FAIL）：**
- HTTP 状态错误：`403`、`404`、`500`、`502`、`503`、`504`、`520`、`521`、`522`、`524`
- 错误文案：`Access Denied`、`Not Found`、`Forbidden`、`Internal Server Error`、`Bad Gateway`、`Service Unavailable`、`Request Timeout`
- 站点状态：`Site suspended`、`Domain parked`、`Domain expired`、`Website is down`、`Maintenance mode`
- 安全拦截：`Cloudflare protection`、`DDoS protection`、`Security check`、`Verify you are human`

**2. 页面空白/空内容：**
- DOM 节点数 < 10（不含 html/head/body）
- body 内几乎无文本内容（< 50 字符）
- 只有加载动画但 15 秒后仍未渲染内容

**3. 导航问题：**
- browser navigate 超时（15 秒）
- browser navigate 报错（DNS 解析失败、连接拒绝等）
- 重定向次数过多（> 5 次）

**4. 特殊情况：**
- 下载链接（.apk/.exe 等）返回非 200 状态码
- 视频/音频资源无法加载

### ⚠️ WARN（警告）判定标准

**1. 需登录/授权：**
- 页面提示"Please log in"、"需要登录"、"Sign in to continue"
- 重定向到登录页（/login/、/signin/、/auth/）
- 预期行为：某些页面本身就需要登录（如 growing.bee.com）

**2. 重定向：**
- 重定向到非预期域名（但目标页面正常）
- 301/302 重定向（最终加载成功）

**3. 加载慢：**
- 首次加载超过 10 秒但不超过 15 秒
- 部分资源加载失败但不影响主要内容

**4. Bot 防护：**
- Cloudflare bot protection 页面（人类用户可正常访问）
- 验证码页面（不影响功能但影响自动化测试）

### ✅ PASS（通过）判定标准

**必须同时满足以下条件：**
1. 10 秒内完成加载
2. DOM 包含实质业务内容（节点数 > 50，文本 > 200 字符）
3. 无 FAIL 类错误关键词
4. 页面标题非空且与预期相符
5. 主要内容区域渲染正常（非空白/非加载动画）

### 📊 特殊情况处理

| 场景 | 判定 | 说明 |
|------|------|------|
| iframe 页面 | 验证 iframe 源地址 | 直接访问 wp.bee.com/en/xxx 而非外层壳子 |
| 下载链接 | curl 检查 HTTP 头 | 不实际下载，用 `curl -sI` 检查状态码 |
| 社交媒体 | 检查账号存在性 | 不要求登录，只验证账号未被封禁 |
| 外部合作伙伴 | 允许 403/404 | 第三方页面可能变更，记录但不视为回归 |

---

## 测试执行流程

### 第零步：加载配置

1. 读取 `<skill 目录>/config.json`
2. 如果不存在或关键配置为空 → 暂停，向用户询问（见「配置」章节）
3. 配置就绪后继续

### 第一步：动态抓取首页结构

使用 `browser` 访问 https://www.bee.com，通过 `snapshot` 提取：
导航链接、侧边栏分类、站点卡片（`/sites/XXXX.html`）、新闻/文章链接、页脚链接（含所有社媒）、悬浮按钮。

**⚠️ 首页内容很长，必须多次滚动 + snapshot 确保提取完整：**
1. 首次 snapshot（顶部内容）
2. 滚动到中部 → snapshot（分类站点、新闻）
3. 滚动到底部 → snapshot（页脚、社媒链接）
4. 汇总所有提取的链接，记录总数

**必须提取并记录的链接类型：**
- 导航栏链接（Web3 Universe / Games / DApp / Bee Hive / Growing Platform / AD）
- 侧边栏分类链接（Meme Launchpad / AI Agents / DeSci / 100x Coins 等全部分类）
- 站点卡片链接（所有 `/sites/XXXX.html`，去重后记录总数）
- 新闻/文章链接（Opinion 区域、For Newbee 区域等）
- 页脚社交媒体链接（**必须提取全部**，不能遗漏）
- 页脚其他链接（White Paper / Roles / FAQ / Privacy / Terms）
- Partners 链接

### 第二步：基础页面验证

使用 `browser` 逐个打开以下 **9 个** URL，按「URL 验证标准」检查：

```
[1/9] https://www.bee.com
[2/9] https://www.bee.com/hotnews/
[3/9] https://www.bee.com/gamecenter/
[4/9] https://www.bee.com/dappStore/
[5/9] https://www.bee.com/beeHive/
[6/9] https://www.bee.com/blog
[7/9] https://www.bee.com/download/
[8/9] https://www.bee.com/advertise/
[9/9] https://growing.bee.com
```

**每个页面必须：** navigate → snapshot → 判断状态 → 记录结果
**完成后确认：** "基础页面验证完成：9/9"

### 第三步：分类站点链接验证（全量/快速模式）

#### 全量模式（默认）

🚨 **全量要求：第一步提取的所有 `/sites/XXXX.html` 链接必须逐个验证，一个不能少。**

1. 从第一步提取的链接中筛选所有 `/sites/XXXX.html` 格式的 URL
2. 去重后记录总数 N
3. 逐个使用 `browser navigate` + `snapshot` 验证
4. 格式：`[X/N] https://www.bee.com/sites/XXXX.html → PASS/FAIL/WARN`
5. 每验证 20 个，打印进度：`"站点验证进度：20/N"`
6. **完成后确认：** `"分类站点验证完成：N/N"`

#### 快速模式（`config.quick_mode = true`）

**使用场景**：日常快速检查，时间紧张时

1. 执行 `python scripts/sample_urls.py` 从全量列表中抽样 20%
2. 验证抽样后的 URL 列表（约 23 个）
3. 格式：`[X/N]（快速模式）https://www.bee.com/sites/XXXX.html → PASS/FAIL/WARN`
4. **完成后确认：** `"分类站点验证完成：N/N（快速模式，抽样 20%）"`

**注意**：基础页面（9 个）和社交媒体（8 个）在快速模式下仍需全量验证。

### 第四步：新闻/文章链接验证（全量）

🚨 **全量要求：首页提取的所有文章链接必须逐个验证。**

1. 从第一步提取的链接中筛选所有新闻/文章链接（Opinion 区域、For Newbee 区域、blog 等）
2. 去重后记录总数 N
3. 逐个使用 `browser navigate` + `snapshot` 验证
4. **完成后确认：** `"新闻/文章验证完成：N/N"`

### 第五步：Games 页面深度测试

Games 页面（gamecenter）**没有 iframe**，可以直接在 `https://www.bee.com/gamecenter/` 操作。

#### 5a. TAB 切换与游戏列表
1. `browser navigate url=https://www.bee.com/gamecenter/`
2. `browser snapshot` 识别所有区块：Featured（含子 TAB）、New、Rankings（含子 TAB）、All games（含子 TAB）
3. 逐个点击每个 TAB，验证数据是否切换（snapshot 对比前后内容）
4. 记录每个 TAB 下的游戏数量

#### 5b. 游戏卡片全量点击验证

🚨🚨🚨 **强制要求：必须对当前页面加载出的所有游戏执行点击验证，不能抽样，不能跳过。**

游戏卡片可能是 `<div>` 元素（非 `<a>` 标签），通过 JS 事件处理点击。

**验证步骤（每个游戏必须完整执行）：**
1. 提取所有游戏名称，去重后统计总数 N
2. 逐个点击 → 检查新标签/页面跳转 → snapshot 验证 → 关闭标签/返回
3. 格式：`[X/N] 游戏名 → PASS/FAIL/WARN - 详情`
4. **每验证 20 个游戏，打印进度并 `browser screenshot`**

**完成后确认：** `"Games 全量验证完成：N/N"`

**禁止行为：**
- ❌ 不能抽样验证（如"抽 5 个代表"）
- ❌ 不能只验证页面级不点击卡片
- ❌ 不能跳过任何游戏
- ❌ 不能用 "其余游戏同上" 概括

#### 5c. 游戏详情页交互（抽样 3 个）
Play 按钮、收藏/点赞、描述、评分

### 第六步：DApp Store 全量测试

🚨🚨🚨 **必须测试首页展示的所有 DApp，不能跳过任何一个。**

#### 6a. 获取完整列表
1. `browser navigate url=https://wp.bee.com/en/dappStore`（iframe 源地址）
2. `browser snapshot` 提取所有分类和 DApp 卡片
3. 如果有分页/加载更多，必须全部加载
4. 记录总数 N

#### 6b. 逐个点击验证（全量）

🚨🚨🚨 **强制要求：必须对每一个 DApp 卡片执行点击验证，不能抽样，不能跳过。**

**验证步骤（每个 DApp 必须完整执行）：**
1. `browser act kind=click` 点击卡片
2. `browser tabs` 检查新标签
3. 切换到新标签 → `snapshot` 验证内容 → 按「URL 验证标准」判断
4. 如果是站内详情页（`/sites/XXXX.html`），额外检查 Website 外链、描述、评论区
5. **必须关闭标签页** → 回到列表继续下一个
6. 格式：`[X/N] DApp 名 → PASS/FAIL/WARN - 详情`

**进度汇报要求：**
- 每验证 20 个 DApp，打印进度：`"DApp 验证进度：20/N"`
- **完成后确认：** `"DApp Store 全量验证完成：N/N"`

**禁止行为：**
- ❌ 不能抽样验证
- ❌ 不能只验证页面级不点击卡片
- ❌ 不能跳过任何 DApp
- ❌ 不能用 "其余 DApp 同上" 概括

#### 6c. 搜索功能测试

**验证 DApp Store 搜索功能是否正常：**

1. **搜索存在的 DApp**（至少测试 3 个）：
   - 在搜索框输入已知 DApp 名称（如 "SushiSwap"、"Uniswap"、"Pump.fun"）
   - 验证搜索结果是否正确显示该 DApp
   - `browser screenshot` 截图保存

2. **搜索不存在的 DApp**（至少测试 2 个）：
   - 在搜索框输入随机不存在的名称（如 "NotExistTest12345"、"FakeAppXYZ"）
   - 验证页面是否正常显示"无结果"或空状态
   - **不能出现**：500 错误、404 错误、页面崩溃、空白页
   - `browser screenshot` 截图保存

3. **记录结果**：
   ```
   搜索测试 | 搜索词 | 预期结果 | 实际结果 | 状态 (PASS/FAIL)
   ```

#### 6d. 深度交互（抽样 5 个）
Website 外链验证、收藏/评分/描述/评论区/安全标识

### 第七步：Bee Hive 页面测试

`browser navigate url=https://wp.bee.com/en/beeHive`（iframe 源地址）

#### 7a. 页面基础验证
- 英雄区域：注册用户数
- 页面结构完整性

#### 7b. 新闻轮播切换测试

🚨 **必须实际操作轮播按钮，不能只看初始状态。**

1. `browser snapshot` 记录当前新闻列表（标题和日期）
2. `browser screenshot` 截图保存（`beehive_news_initial.png`）
3. 找到 **Next slide / Previous slide 按钮**
4. 点击 **Next slide** 按钮 **3 次**：
   - 每次点击后 `browser snapshot` 获取切换后的内容
   - **验证数据是否发生变化**（新闻标题/日期与切换前不同）
   - `browser screenshot` 截图保存
5. 点击 **Previous slide** 按钮 **1-2 次**：
   - 验证是否能回退到之前的新闻
   - `browser screenshot` 截图保存
6. **记录结果**：切换按钮是否存在、点击后数据是否正确变化、是否能前后切换

#### 7c. 新闻链接验证（前 10 条）

🚨 **必须逐个点击，不能只看列表。**

1. 提取 Bee Hive 页面上的新闻标题和链接
2. 前 10 条逐个点击 → 新标签 → snapshot 验证详情页 → 关闭标签
3. 格式：`[X/10] "新闻标题" → PASS/FAIL/WARN`
4. **完成后确认：** `"Bee Hive 新闻验证完成：10/10"`

#### 7d. DApp Store 入口验证
"Discover now >" 是导航栏切换（非新标签），验证正确跳转

#### 7e. 其他链接
登录帮助、Download 等（新标签）→ 逐个验证

### 第八步：AD 页面表单测试

`browser navigate url=https://wp.bee.com/en/advertise`（iframe 源地址）

#### 8a. 页面渲染 + Media Kit 下载验证

1. `browser snapshot` 验证页面内容渲染
2. 提取 Media Kit 下载链接
3. `exec curl -sI <Media Kit URL>` 检查链接可达性（HTTP 状态码）
4. 记录 Media Kit 链接状态

#### 8b. 表单交互

1. 找到表单字段（Name / Email / Note）
2. 填入测试数据 `openclaw test lee`
3. 点击 Submit 按钮
4. `browser snapshot` 检查提交后反馈
5. 记录表单提交状态

### 第九步：下载功能验证

#### 9a. APK 下载
`exec curl -sI <APK 链接>` 检查 APK 链接可达性（不实际下载完整文件）

#### 9b. App Store / Google Play
`browser` 打开以下链接并验证：
- `https://apps.apple.com/app/bee-games/id1529988919`
- `https://play.google.com/store/apps/details?id=network.bee.app`

#### 9c. 清理下载文件
```bash
find /home -name "*.apk" -delete 2>/dev/null
find /tmp -name "*.apk" -mmin -120 -delete 2>/dev/null
```

### 第十步：外部链接测试

`browser` 验证以下链接：
- `https://open.bee.com/recharge/bee-recharge-coins/index.html`

### 第十一步：社交媒体链接验证（全量）

🚨🚨🚨 **必须验证页脚的所有社媒链接，一个不能漏！上次只测了 2/8，这是不可接受的。**

**社媒链接清单（以第一步从页脚实际提取为准，至少包含以下 8 个）：**

| # | 平台 | URL（参考） | 验证要点 |
|---|------|------------|---------|
| 1 | Twitter/X | twitter.com/beenetworkintl | 账号存在、未被封禁、发帖数、粉丝数 |
| 2 | TikTok | tiktok.com/@beenetwork_official | 账号存在、粉丝数、视频数 |
| 3 | Medium | beenetworkintl.medium.com | 博客存在、有文章 |
| 4 | Facebook | facebook.com/beenetworkinternational | 页面存在、未被移除 |
| 5 | YouTube | youtube.com/channel/UCrV507pXDtPFkLx_9iesEfw | 频道存在、未被终止 |
| 6 | LinkedIn | linkedin.com/company/bee-network-international | 公司页面存在 |
| 7 | Telegram | t.me/+Hvaxi0mydVQ2ZjA1 | 群组/频道存在、邀请有效 |
| 8 | Discord | discord.gg/zPkYTHfyrZ | 邀请有效、服务器存在 |

**验证方法：**
1. 逐个使用 `browser navigate` 打开链接
2. `browser snapshot` 检查页面内容
3. 提取关键数据（粉丝数、发帖数等）
4. 按封禁特征判断状态

---

## 📊 社交媒体详细验证标准

### 1️⃣ Twitter/X 验证标准

**✅ PASS（正常）：**
- 账号页面正常加载
- 显示账号名、@handle、粉丝数、关注数、发帖数
- 时间线显示推文（至少能看到几条推文）
- 无封禁关键词

**⚠️ WARN（可疑但非封禁）：**
- 粉丝数 < 100（可能是新号或不活跃）
- 发帖数 = 0（从未发过推文）
- 账号存在但时间线为空（可能删光了）
- 需要登录才能查看完整内容（但账号基本信息可见）

**❌ FAIL（封禁/不存在）：**
- 页面包含以下任一关键词：
  - `Account suspended`（账号被封禁）
  - `doesn't exist` / `This account doesn't exist`（账号不存在）
  - `Account does not exist`（账号不存在）
  - `suspended`（在页面标题或显眼位置）
- HTTP 404（账号页面不存在）
- 页面显示"Sorry, that page doesn't exist!"

**数据提取要求：**
- 粉丝数（Followers）
- 关注数（Following）
- 发帖数（Posts/Tweets）
- 账号创建时间（如果有）

---

### 2️⃣ TikTok 验证标准

**✅ PASS（正常）：**
- 账号页面正常加载
- 显示账号名、@handle、粉丝数、关注数、点赞数、视频数
- 能看到视频列表（至少几个视频封面）
- 无封禁关键词

**⚠️ WARN（可疑但非封禁）：**
- 粉丝数 < 100（可能是新号）
- 视频数 = 0（从未发过视频）
- 账号存在但内容为空

**❌ FAIL（封禁/不存在）：**
- 页面包含以下任一关键词：
  - `Couldn't find this account`（找不到账号）
  - `account was banned`（账号被封禁）
  - `This account is unavailable`（账号不可用）
  - `User not found`（用户不存在）
- HTTP 404
- 页面只显示一个错误图标 + 错误文案

**数据提取要求：**
- 粉丝数（Followers）
- 关注数（Following）
- 点赞数（Likes）
- 视频数（Videos）

---

### 3️⃣ Medium 验证标准

**✅ PASS（正常）：**
- 博客主页正常加载
- 显示博客名称、简介
- 能看到文章列表（至少几篇文章）
- 显示关注者数量（如果有）

**⚠️ WARN（可疑但非失效）：**
- 文章数 = 0（从未发过文章）
- 关注者 < 10（可能是新号）
- 最新文章发布时间 > 6 个月前（可能已废弃）

**❌ FAIL（不存在/失效）：**
- HTTP 404
- 页面显示 `404`、`Page not found`、`doesn't have a page`
- 页面显示 `This story is no longer available`
- 页面完全空白（无内容）

**数据提取要求：**
- 文章数量
- 关注者数量（如果有）
- 最新文章发布时间

---

### 4️⃣ Facebook 验证标准

**✅ PASS（正常）：**
- 页面正常加载
- 显示页面名称、简介、粉丝数（如果有）
- 能看到页面内容（帖子、照片等）
- 无封禁关键词

**⚠️ WARN（可疑但非失效）：**
- 粉丝数 < 100（可能是新页面）
- 帖子数 = 0（从未发过帖）
- 内容对未登录用户有限制（但基本信息可见）

**❌ FAIL（不存在/被移除）：**
- 页面包含以下任一关键词：
  - `content isn't available`（内容不可用）
  - `page has been removed`（页面已被移除）
  - `This page isn't available`（页面不可用）
  - `The requested URL was not found`（404）
  - `This content is currently unavailable`（内容不可用）
- HTTP 404
- 页面只显示错误图标 + 错误文案

**数据提取要求：**
- 粉丝数/喜欢数（如果有）
- 帖子数量（如果能看见）

---

### 5️⃣ YouTube 验证标准

**✅ PASS（正常）：**
- 频道页面正常加载
- 显示频道名称、头像、订阅者数、视频数
- 能看到视频列表（至少几个视频）
- 无封禁关键词

**⚠️ WARN（可疑但非封禁）：**
- 订阅者数 < 100（可能是新频道）
- 视频数 = 0（从未发过视频）
- 频道存在但内容为空

**❌ FAIL（封禁/不存在）：**
- 页面包含以下任一关键词：
  - `channel is not available`（频道不可用）
  - `account has been terminated`（账号已被终止）
  - `This channel doesn't exist`（频道不存在）
  - `Unable to find the channel`（找不到频道）
- HTTP 404
- 页面显示"Something went wrong"且无频道信息

**数据提取要求：**
- 订阅者数（Subscribers）
- 视频数（Videos）
- 总观看次数（如果有）

---

### 6️⃣ LinkedIn 验证标准

**✅ PASS（正常）：**
- 公司页面正常加载
- 显示公司名称、简介、行业、公司规模
- 显示员工数、关注者数（如果有）
- 能看到公司动态（Posts）

**⚠️ WARN（可疑但非失效）：**
- 关注者数 < 50（可能是新公司）
- 员工数显示很少（< 5）
- 公司动态为空（从未发过帖）
- 部分内容需要登录才能查看（但基本信息可见）

**❌ FAIL（不存在/被移除）：**
- 页面包含以下任一关键词：
  - `page not found`（页面不存在）
  - `This page is not available`（页面不可用）
  - `The page you're looking for doesn't exist`（页面不存在）
  - `Page unavailable`（页面不可用）
- HTTP 404
- 页面只显示错误图标 + 错误文案

**数据提取要求：**
- 员工数范围
- 关注者数（如果有）
- 行业、公司规模（如果有）

---

### 7️⃣ Telegram 验证标准

**✅ PASS（正常）：**
- 群组/频道页面正常加载
- 显示群组/频道名称、头像、简介
- 显示成员数（在线数/总数）
- 能看到最近消息列表（即使未加入）

**⚠️ WARN（可疑但非失效）：**
- 成员数 < 100（可能是新群组）
- 群组/频道为空（无消息）
- 显示"If you have Telegram, you can view..."（需要 Telegram 客户端，但链接有效）

**❌ FAIL（不存在/邀请失效）：**
- 页面完全空白（无任何内容）
- 页面显示 `If you have Telegram, you can view...` 但**看不到群组名称和成员数**
- 页面显示 `Invalid invite link`、`Invite expired`
- 页面显示 `This channel doesn't exist`
- HTTP 404

**注意**：Telegram 的"If you have Telegram, you can view..."提示**本身不是错误**，这是正常行为（针对未登录用户）。关键是要能看到群组名称和成员数。

**数据提取要求：**
- 成员总数
- 在线成员数（如果有）
- 群组/频道类型（公开/私有）

---

### 8️⃣ Discord 验证标准

**✅ PASS（正常）：**
- 邀请页面正常加载
- 显示服务器名称、头像、图标
- 显示在线成员数、总成员数
- 显示"Accept Invite"按钮或类似内容

**⚠️ WARN（可疑但非失效）：**
- 成员数 < 100（可能是新服务器）
- 在线成员数很少（< 10）
- 邀请链接显示需要登录（但服务器信息可见）

**❌ FAIL（不存在/邀请失效）：**
- 页面包含以下任一关键词：
  - `Invite Invalid`（邀请无效）
  - `invite may be expired`（邀请可能已过期）
  - `This invite is expired`（邀请已过期）
  - `Server not found`（服务器不存在）
  - `You don't have access to this server`（无访问权限）
- HTTP 404
- 页面只显示错误图标 + 错误文案

**数据提取要求：**
- 服务器名称
- 总成员数
- 在线成员数

---

## 📋 社交媒体验证结果格式

**每条结果必须包含：**
```
[X/8] 平台名 → 状态 - 关键数据
```

**示例：**
```
[1/8] Twitter/X → PASS - @beenetworkintl, 831.1K followers, 4,688 posts
[2/8] TikTok → PASS - @beenetwork_official, 13.4K followers, 10.3K likes, 45 videos
[3/8] Medium → WARN - beenetworkintl.medium.com, 0 articles (从未发布)
[4/8] Facebook → PASS - 261K followers, 页面活跃
[5/8] YouTube → PASS - 152K subscribers, 23 videos
[6/8] LinkedIn → PASS - Bee Network International, 员工 11-50 人
[7/8] Telegram → PASS - 179,207 members, 2,796 online
[8/8] Discord → PASS - Invite valid, server "Bee Network", 70,990 members, 563 online
```

**完成后确认：** `"社交媒体验证完成：8/8"`

### 第十二步：页脚其他链接验证

🚨 **页脚不只有社媒，还有其他链接也要验证。**

验证以下页脚链接：
- White Paper: `https://www.bee.com/white-paper/`
- Roles: `https://www.bee.com/roles/`
- FAQ: `https://www.bee.com/faq/`
- Privacy Policy: `https://www.bee.com/privacy/`
- Terms of Services: `https://www.bee.com/terms/`

Partners 链接（以实际提取为准）：
- CoinCarp, Binance, CoinMarketCap, CoinGecko, Coinlive, Armors

逐个 `browser navigate` + `snapshot` 验证。

### 第十三步：登录功能验证

1. 在首页找到 Login 按钮
2. 验证按钮存在且可点击
3. 点击后验证是否弹出登录弹窗/跳转登录页
4. **不执行实际登录**
5. 记录状态

### 第十四步：悬浮按钮测试

验证首页的悬浮/固定按钮：
1. 置顶按钮（Back to top）：是否存在、点击是否回到顶部
2. 推特跳转按钮：是否存在、点击是否跳转到 Bee 的 Twitter
3. 任务版按钮（如果存在）：点击行为

### 第十五步：与前一天对比

1. 从 `data_dir`（默认 `<skill 目录>/data/`）读取 `bee-test-previous.json`
2. 对比内容：
   - 新增失败（上次 PASS 这次 FAIL → 🔴 回归）
   - 已修复（上次 FAIL 这次 PASS → 🟢 修复）
   - 新增 URL（本次有上次没有）
   - 消失 URL（上次有本次没有）
3. 保存本次结果到 `bee-test-previous.json`

### 第十六步半：JSON 结果导出（新增）

**目的**：导出标准化 JSON 结果，便于程序处理、对比和历史分析。

1. 使用 `exec` 执行 `scripts/export_results.py`：
   ```bash
   python scripts/export_results.py \
     <测试结果 JSON 文件> \
     <data_dir>/bee-test-result-YYYY-MM-DD.json \
     <data_dir>/bee-test-previous.json
   ```

2. 导出内容包含：
   - 测试概览（PASS/FAIL/WARN 统计、通过率）
   - 覆盖度（各分类测试数量）
   - 问题项列表（FAIL/WARN 详情）
   - 对比分析（回归问题、已修复问题、新增问题）

3. 保存本次 JSON 结果到 `data_dir/`，用于下次对比

### 第十六步：生成报告

使用 `feishu_create_doc` 创建飞书云文档：
- **文件夹**：从 `config.json` 的 `report_folder_token` 读取
- **标题**：`Bee.com 网站测试报告 - YYYY-MM-DD`

**⚠️ 生成报告前，必须先核对「完成度检查清单」（见顶部），确认所有项目都已完成。**

**报告结构：**

1. **测试概览**
   - PASS / FAIL / WARN 统计
   - 测试时间、覆盖范围

2. **🚨 关键问题（与前一天对比）**
   - 回归问题（前一天 PASS 今天 FAIL）
   - 已修复问题
   - 持续异常

3. **基础页面测试**（9 个 URL 的结果表格）

4. **分类站点测试**（全量结果，标注 FAIL/WARN 的详情）

5. **新闻/文章链接测试**（全量结果）

6. **Games 全量测试**
   - TAB 切换结果
   - 游戏卡片全量点击结果（列表）
   - 详情页交互结果

7. **DApp Store 全量测试**
   - 分类列表
   - 全部 DApp 点击结果（列表）
   - 搜索功能测试结果
   - 深度交互结果

8. **Bee Hive 测试**
   - 页面基础验证
   - 轮播切换测试结果
   - 新闻链接验证结果

9. **AD 表单测试**

10. **下载功能验证**

11. **外部链接测试**

12. **📱 社交媒体链接验证**（**全部 8 个平台的详细结果**）

13. **页脚链接验证**（White Paper / Roles / FAQ / Privacy / Terms / Partners）

14. **登录功能 + 悬浮按钮**

15. **已知限制与建议**

### 第十七步：发送通知

根据 `config.json` 的 `webhook_url` 配置发送通知：

- **如果 `webhook_url` 是飞书 Webhook 地址**：通过 `exec` 使用 `curl` 发送 POST 请求到 Webhook
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -d '{"msg_type":"text","content":{"text":"🐝 Bee.com 测试完成\n✅ PASS: X | ❌ FAIL: Y | ⚠️ WARN: Z\n报告：<链接>"}}' \
    <webhook_url>
  ```
- **如果 `webhook_url` 为 `"direct"`**：直接在当前对话中回复测试结果（使用 `message` 工具）

**通知内容必须包含：**
- PASS/FAIL/WARN 数量
- 失败项详细列表
- 社交媒体验证数量（X/8）
- DApp 验证数量（X/N）
- Games 验证数量（X/N）
- 报告链接

---

## 执行约束

- **超时**：
  - 全量模式：不超过 90 分钟
  - 快速模式：不超过 30 分钟（抽样 20%）
- **单页超时**：browser 加载等待最多 15 秒
- **验证方式**：全部使用 browser 渲染验证，不使用 web_fetch
- **DApp Store + Games**：
  - 全量模式：全量测试，不跳过
  - 快速模式：抽样 20% 测试
- **社交媒体**：全部 8 个平台，不跳过（任何模式）
- **基础页面**：全部 9 个，不跳过（任何模式）
- **标签页管理**：每次验证完必须关闭新标签页
- **文件清理**：测试结束后删除所有下载文件
- **容错**：单个失败不影响整体
- **准确性优先**：宁可慢也要确保结果真实可靠
- **计数器**：全量测试必须维护 `[X/N]` 计数器
- **JSON 导出**：每次测试必须导出 JSON 结果到 `data_dir/`

## 状态标记

- ✅ PASS — 正常渲染，有实质内容
- ❌ FAIL — 错误页面（403/404/500/空白/超时）
- ⚠️ WARN — 有异常（需登录/重定向/加载慢）
