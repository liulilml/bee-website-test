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
  (4) 用户提到"bee测试"、"bee.com测试"、"网站测试"、"bee网站检查"
  (5) 需要验证 bee.com 的 DApp、游戏、新闻等内容是否正常加载
  即使用户没有明确说"测试"，只要涉及检查 bee.com 页面是否正常，都应使用此 Skill。
---

# Bee.com 网站自动化测试

## 概述

对 www.bee.com 进行全面的自动化测试，覆盖页面可达性、内容渲染、导航链接、分类站点、
深度交互（点击跳转、表单、轮播、下载）等，生成结构化的飞书云文档报告，并与前一天结果对比。

---

## ⚙️ 配置（首次使用必须确认）

**首次执行此 Skill 时，必须先向用户确认以下配置项。** 确认后保存到配置文件中，后续执行自动读取。

### 配置文件

路径：`<skill目录>/config.json`（与 SKILL.md 同级）

```json
{
  "report_folder_token": "",
  "webhook_url": "",
  "data_dir": ""
}
```

### 配置项说明

| 配置项 | 必填 | 说明 |
|--------|------|------|
| `report_folder_token` | ✅ | 飞书云盘文件夹 Token，测试报告将创建在此文件夹中。用户需要提供一个飞书云盘文件夹链接或 Token。 |
| `webhook_url` | ✅ | 飞书机器人 Webhook 地址，用于发送测试结果通知。格式：`https://open.feishu.cn/open-apis/bot/v2/hook/xxx`。如果用户在当前对话中直接使用（非 cron 定时），可以填 `"direct"` 表示直接在当前对话回复结果。 |
| `data_dir` | 可选 | 对比数据文件 `bee-test-previous.json` 的存放目录。默认为 skill 目录下的 `data/`。 |

### 首次使用流程

1. 读取 `<skill目录>/config.json`
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

### 为什么要直接访问 iframe 源地址？

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
3. 切换到新标签页（`browser snapshot targetId=<新标签ID>`）验证内容
4. 验证完成后关闭标签页（`browser act kind=close targetId=<新标签ID>`）
5. **每次验证完必须关闭标签页**，防止堆积导致浏览器性能下降

---

## URL 验证标准（全局适用）

```
browser navigate url=<URL> → 等待加载(最多15秒) → browser snapshot → 判断规则
```

**❌ FAIL：** DOM 含错误关键词（403/404/500/Access Denied/Not Found/Forbidden 等）、DOM 几乎为空、页面空白、导航超时/报错

**⚠️ WARN：** 需登录、重定向到非预期 URL、加载超 10 秒

**✅ PASS：** 正常标题 + 实质业务内容 + 无错误关键词 + 10 秒内加载

---

## 测试执行流程

### 第零步：加载配置

1. 读取 `<skill目录>/config.json`
2. 如果不存在或关键配置为空 → 暂停，向用户询问（见「配置」章节）
3. 配置就绪后继续

### 第一步：动态抓取首页结构

使用 `browser` 访问 https://www.bee.com，通过 `snapshot` 提取：
导航链接、侧边栏分类、站点卡片（`/sites/XXXX.html`）、新闻/文章链接、页脚链接、悬浮按钮。
首页内容很长，可能需要多次 snapshot 或滚动。

### 第二步：基础页面验证

使用 `browser` 逐个打开以下页面，按「URL 验证标准」检查：
```
https://www.bee.com
https://www.bee.com/hotnews/
https://www.bee.com/gamecenter/
https://www.bee.com/dappStore/
https://www.bee.com/beeHive/
https://growing.bee.com
https://www.bee.com/advertise/
https://www.bee.com/blog
https://www.bee.com/download/
```

### 第三步：分类站点链接验证

对第一步抓取到的所有站点详情链接（`/sites/XXXX.html`），使用 `browser` 逐个验证。
数量可能较多（50-80 个），耐心逐个验证，不要跳过。

### 第四步：新闻/文章链接验证

对抓取到的文章链接，使用 `browser` 逐个验证。

### 第五步：Games 页面深度测试

Games 页面（gamecenter）**没有 iframe**，直接在主页面操作。

#### 5a. TAB 切换与游戏列表
1. `browser navigate url=https://www.bee.com/gamecenter/`
2. 识别所有区块：Featured（含子 TAB）、New、Rankings（含子 TAB）、All games（含子 TAB）
3. 逐个点击每个 TAB，验证数据是否切换

#### 5b. 游戏卡片全量点击验证
⚠️ **必须测试当前页面加载出的所有游戏，不能跳过任何一个。**

游戏卡片是 `<div>` 元素（非 `<a>` 标签），通过 JS 事件处理点击：
1. 提取所有游戏名称，去重后统计总数
2. 逐个点击 → 检查新标签/页面跳转 → snapshot 验证 → 关闭标签/返回

#### 5c. 游戏详情页交互（抽样 3 个）
Play 按钮、收藏/点赞、描述、评分

### 第六步：DApp Store 全量测试

⚠️ **必须测试首页展示的所有 DApp，不能跳过任何一个。**

#### 6a. 获取完整列表
`browser navigate url=https://wp.bee.com/en/dappStore`（iframe 源地址）
提取所有分类和 DApp 卡片

#### 6b. 逐个点击验证（全量）
点击卡片 → 检查新标签 → 切换验证 → 关闭标签

#### 6c. 深度交互（抽样 5 个）
Website 外链验证、收藏/评分/描述/评论区/安全标识

### 第七步：Bee Hive 页面测试

`browser navigate url=https://wp.bee.com/en/beeHive`（iframe 源地址）

#### 7b. 新闻轮播切换测试
Next/Previous slide 按钮点击 → 验证数据切换

#### 7c. 新闻链接验证（前 10 条）
逐个点击 → 新标签 → 验证详情页 → 关闭标签

#### 7d. DApp Store 入口验证
"Discover now >" 是导航栏切换（非新标签），验证正确跳转

#### 7e. 其他链接
登录帮助、Download 等（新标签）→ 逐个验证

### 第八步：AD 页面表单测试

`browser navigate url=https://wp.bee.com/en/advertise`（iframe 源地址）

#### 8a. 页面渲染 + Media Kit 下载验证
`curl -sI` 检查 Media Kit 下载链接

#### 8b. 表单交互
填入 `openclaw test lee` → 提交 → 检查反馈

### 第九步：下载功能验证

#### 9a. APK 下载
`curl -sI` 检查 APK 链接可达性（不实际下载）

#### 9b. App Store / Google Play
`browser` 打开验证

#### 9c. 清理下载文件
```bash
find /home -name "*.apk" -delete 2>/dev/null
find /tmp -name "*.apk" -mmin -120 -delete 2>/dev/null
```

### 第十步：外部链接测试

`browser` 验证 `https://open.bee.com/recharge/bee-recharge-coins/index.html`

### 第十一步：社交媒体链接验证

验证页脚所有社媒链接跳转后页面正常、**账号未被封禁**。

社媒链接（以页面实际提取为准）：TikTok、Medium、Facebook、YouTube、LinkedIn、Twitter/X、Telegram、Discord

**封禁特征（FAIL）：**
- Twitter: "Account suspended"、"doesn't exist"
- Facebook: "content isn't available"、"page has been removed"
- TikTok: "Couldn't find this account"、"account was banned"
- YouTube: "channel is not available"、"account has been terminated"
- Telegram: 页面完全无内容
- Discord: "Invite Invalid"、"invite may be expired"

### 第十二步：登录功能验证

确认 Login 按钮存在且可点击。不执行实际登录。

### 第十三步：悬浮按钮测试

置顶按钮、推特跳转、任务版按钮

### 第十四步：与前一天对比

1. 从 `data_dir`（默认 `<skill目录>/data/`）读取 `bee-test-previous.json`
2. 对比：新增失败、已修复、新增 URL、消失 URL
3. 保存本次结果

### 第十五步：生成报告

使用 `feishu_create_doc` 创建飞书云文档：
- **文件夹**：从 `config.json` 的 `report_folder_token` 读取
- **标题**：`Bee.com 网站测试报告 - YYYY-MM-DD`

报告内容：
1. 测试概览（PASS/FAIL/WARN 四宫格）
2. 与前一天对比
3. 基础页面 + 分类站点 + 新闻/文章
4. Games 全量测试
5. DApp Store 全量测试
6. AD 表单测试
7. Bee Hive 测试
8. 下载功能 + 外部链接
9. 社交媒体链接验证
10. 登录 + 悬浮按钮
11. 已知限制与建议

### 第十六步：发送通知

根据 `config.json` 的 `webhook_url` 配置发送通知：

- **如果 `webhook_url` 是飞书 Webhook 地址**：通过 `exec` 使用 `curl` 发送 POST 请求到 Webhook
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -d '{"msg_type":"text","content":{"text":"🐝 Bee.com 测试完成\n✅ PASS: X | ❌ FAIL: Y | ⚠️ WARN: Z\n报告: <链接>"}}' \
    <webhook_url>
  ```
- **如果 `webhook_url` 为 `"direct"`**：直接在当前对话中回复测试结果（使用 `message` 工具）

通知内容：PASS/FAIL/WARN 数量、失败项列表、报告链接

---

## 执行约束

- **超时**：整体不超过 60 分钟
- **单页超时**：browser 加载等待最多 15 秒
- **验证方式**：全部使用 browser 渲染验证，不使用 web_fetch
- **DApp Store + Games**：全量测试，不跳过
- **标签页管理**：每次验证完必须关闭新标签页
- **文件清理**：测试结束后删除所有下载文件
- **容错**：单个失败不影响整体
- **准确性优先**：宁可慢也要确保结果真实可靠

## 状态标记

- ✅ PASS — 正常渲染，有实质内容
- ❌ FAIL — 错误页面（403/404/500/空白/超时）
- ⚠️ WARN — 有异常（需登录/重定向/加载慢）
