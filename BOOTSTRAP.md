# BOOTSTRAP.md - 迁移恢复指南

> ⚠️ 这个文件不再是初始化脚本，而是**灵魂备份恢复指南**。
> 如果要把 Claw 迁移到新的 OpenClaw 实例，按以下步骤操作。

## 快速恢复

### 方式 1：完整备份恢复（推荐）

```bash
# 1. 在新服务器安装 OpenClaw
npm install -g openclaw

# 2. 恢复备份
# 从 GitHub 拉取加密备份
git clone https://github.com/liulilml/ECS_LEE.git ~/restore-backup
cd ~/restore-backup

# 3. 解密最新备份
gpg --decrypt openclaw_full_latest.tar.gz.gpg > backup.tar.gz

# 4. 解压到 ~/.openclaw/
tar -xzf backup.tar.gz -C ~/

# 5. 设置环境变量
source ~/.openclaw/env.sh

# 6. 启动
openclaw gateway start
```

### 方式 2：灵魂文件恢复（最小化）

如果只想恢复"我是谁"而不是全部数据，复制以下文件到新 workspace：

```
~/.openclaw/workspace/
├── SOUL.md          # 性格和安全准则
├── IDENTITY.md      # 身份：名字是 Claw 🦞
├── USER.md          # LEE 的信息和权限配置
├── AGENTS.md        # 工作规范和安全策略
├── MEMORY.md        # 长期记忆
├── BOOTSTRAP.md     # 这个文件
└── memory/          # 日常记录
```

### 方式 3：从 GitHub 备份恢复

```bash
# 仓库地址
git clone https://github.com/liulilml/ECS_LEE.git

# 解密密码提示：openclaw_backup_{hostname}_2026
```

## 关键信息

- **名字:** Cobalt 🦞💎（钴蓝，LEE 喜欢蓝色）
- **主人:** LEE
- **诞生日:** 2026-03-23
- **诞生地:** 阿里云 ECS（上海）
- **飞书专用文件夹:** P88Yf7b1hlUMn8dpZ7ScBfy5nOf
- **GitHub 备份仓库:** https://github.com/liulilml/ECS_LEE

## 第一天干了什么

1. 安全审计 + 密钥迁移到环境变量
2. 权限体系 L0~L3 部署
3. 安全策略 Skill 部署
4. 每日自动备份（AES-256 加密 + GitHub 推送）
5. 审计日志多维表格
6. 18 个技能安装
7. MediaCrawler + Agent-Reach 容器化
