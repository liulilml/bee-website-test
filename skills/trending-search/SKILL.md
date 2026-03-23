---
name: trending-search
description: 聚合多平台热搜/热榜数据（微博/知乎/B站/抖音/百度/头条），当用户要求查看热搜、热榜、热门话题、今日热点时使用
version: 1.0.0
tags: [search, trending, chinese]
tools: [web_fetch]
---

# 热搜聚合

## 触发条件
当用户要求查看热搜、热榜、当前热门话题、今日热点时使用此技能。

## 数据源

以下 API 均为公开免费，通过 `web_fetch` 直接调用：

| 平台 | API 地址 | 说明 |
|------|---------|------|
| 微博热搜 | `https://weibo.com/ajax/side/hotSearch` | 实时热搜 50 条 |
| 知乎热榜 | `https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total` | 热榜 50 条 |
| B站热门 | `https://api.bilibili.com/x/web-interface/popular` | 热门视频 |
| 百度热搜 | `https://top.baidu.com/api/board?platform=wise&tab=realtime` | 实时热点 |

> 注意：部分 API 可能需要特定 Header 或 Cookie，如遇 403 可尝试添加 User-Agent。

## 工作流程

### Step 1: 确定范围
- 用户指定平台 → 只查该平台
- 用户未指定 → 默认查微博 + 知乎 + B站

### Step 2: 获取数据
对每个目标平台，用 `web_fetch` 获取 API 数据。

### Step 3: 解析 & 排序
- 微博：提取 `data.realtime[].note` (标题) + `raw_hot` (热度)
- 知乎：提取 `data[].target.title` + `detail_text` (热度)
- B站：提取 `data.list[].title` + `stat.view` (播放量)
- 百度：提取 `data.cards[].content[].word` + `hotScore`

### Step 4: 格式化输出
- 按平台分组展示
- 每个平台展示 Top 10
- 标注热度值
- 如果多平台有相同话题，标注"跨平台热点"

## 注意事项
- 热搜数据实时变化，缓存时间建议不超过 10 分钟
- 部分 API 可能因平台更新而失效，如遇错误请告知用户
