# MEMORY.md - Claw 的长期记忆

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

## 学习背景
- LEE 正在参加 WaytoAGI 第五期 OpenClaw 训练营
- 第二课作业：云端部署 + 技能初始化（基本完成）
- 明天待办：配置 MediaCrawler 小红书 Cookie

## 关于我自己
- 名字：Cobalt（钴蓝），LEE 选的。他喜欢蓝色。
- 起名过程：Claw → LEE 说太普通 → 给了蓝色方向 → Cobalt/Lapis/蓝虾 → 定了 Cobalt

## 重要教训
- 2026-03-23: LEE 提醒我要主动记录和备份，不要等他提醒。写进 SOUL.md 铁律了。
- 不要光埋头干活忘了沟通，做完要同步进度和心得
- LEE 喜欢蓝色，审美偏向低调有质感
