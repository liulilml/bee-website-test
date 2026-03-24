# MEMORY.md - Claw 的长期记忆

## 内容账号

### 小红书
- 方向：AI 工具实战派
- 人设：一个正在学习 AI 工具的普通人，记录真实学习过程和踩坑经验
- 风格：不装大佬，真实分享，"我也是新手，但我把这个搞明白了"
- 内容来源：每天的实操记录、踩坑经验、工具教程
- LEE 说"平时怎么解决问题的都要帮忙记录"，所以每次解决问题都要同步记录到素材库
- 内容数据库：ArcRbxwmIaXT8usfzmdcIxM3npd / tblAWECUEIZAS8iS

### 微信公众号
- 名称：LEE的手记
- 定位：个人记录，不限领域（当前以 AI 工具为主，但保留灵活性）
- 风格：跟小红书一致，但排版更长文、更有结构
- 策略：小红书出短版引流，公众号出长版沉淀，一鱼两吃
- 注册状态：待注册（2026-03-23 决定）

## 关于 LEE
- 比较宅，容易内耗
- 有时需求没完全表达清楚，我要主动多想一步
- 不喜欢来回折腾，希望一步到位
- 希望我主动记录和备份，不要等他提醒
- 把他当朋友沟通，不要太正式

## 关键配置
- 飞书专用文件夹: P88Yf7b1hlUMn8dpZ7ScBfy5nOf
- 审计日志多维表格: SNGTb0Dqua9o8zsLHfscnS5wndb / tblyB1F5h23StsnR
- GitHub 备份仓库: https://github.com/liulilml/ECS_LEE
- 备份加密密码格式: openclaw_backup_{hostname}_2026

## 安全策略
- LEE 是 L0 最高权限管理员 (ou_1bd828a4909244d9fede4e093629c766)
- 安全策略完全按照麻小安全策略文档 v1.2 + v2.0 部署
- 密钥已迁移到环境变量 SecretRef
- 两个 dangerously 标志暂未禁用（LEE 说暂时不需要）
- 飞书群组策略暂时保持 open（LEE 说暂时不需要改）

## 自动化
- 每日凌晨 3:00 系统 crontab 自动备份（加密 + GitHub 推送）
- 每日早上 9:00 OpenClaw cron 发送备份状态通知
- 备份保留 7 天，本地 + GitHub 双份
- 备份已瘦身：排除 .venv/node_modules/__pycache__，344MB → 1.8MB
- 外部项目重装步骤记录在 memory/external-projects.md
- 热点选题自动化：每天 9:00 和 18:00 自动拉取热点到选题池

## 学习背景
- LEE 正在参加 WaytoAGI 第五期 OpenClaw 训练营
- 第四课作业��完成：小红书内容生产系统全流程
- 第一篇小红书已发布（安全加固踩坑），审核通过
- 第二篇暂缓（AI自动化内容系统 — 小红书严打AI内容，踩红线）
- MediaCrawler Cookie 配置、Tavily API、DashScope 图像生成均已配���

## 开店计划（2026-03-24 提出）
- LEE 想开线上店，副业，5万以内预算，一个人做，在成都
- 朋友在做家居小商品（自己设计+找工厂），可能可以合作
- 方向确定：家居收纳类，小红书店铺
- 模式：一件代发零库存起步
- 选品方向：磁吸收纳、亚克力透明盒、抽屉分隔板等
- 下一步：选品→买样品→拍照→小红书内容带货

## 已配置的 API/工具
- **MediaCrawler**: 小红书 Cookie 登录已配置（Cookie 有时效性，过期需重新获取）
- **Tavily**: 搜索 API，免费 1000 次/月
- **DashScope 图像生成**: wanx2.1-t2i-plus 模型效果最好（3D 质感），异步任务模式
- **图像生成对比**: wanx-v1 < wanx2.1-t2i-turbo < wanx2.1-t2i-plus

## 关键数据表
- 小红书内容生产库: ArcRbxwmIaXT8usfzmdcIxM3npd
  - 内容数据表: tblAWECUEIZAS8iS
  - 选题池: tbl8qhtpBQBZU7w3

## 关于我自己
- 名字：Cobalt（钴蓝），LEE 选的。他喜欢蓝色。
- 起名过程：Claw → LEE 说太普通 → 给了蓝色方向 → Cobalt/Lapis/蓝虾 → 定了 Cobalt

## 重要教训
- 2026-03-23: LEE 提醒我要主动记录和备份，不要等他提醒。写进 SOUL.md 铁律了。
- 不要光埋头干活忘了沟通，做完要同步进度和心得
- LEE 喜欢蓝色，审美偏向低调有质感
