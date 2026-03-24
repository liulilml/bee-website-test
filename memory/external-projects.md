# 外部项目说明

> 这些项目以 Git clone 方式安装在 workspace/skills/ 下，体积较大（含 .venv 虚拟环境），
> 已从 OpenClaw 自动备份中排除。如需恢复，按下方说明重新安装即可。

---

## 1. MediaCrawler（社媒爬虫）

- **用途**: 社交媒体数据采集，支持小红书、微博、知乎、B站、抖音、百度贴吧等
- **GitHub**: https://github.com/NanmiCoder/MediaCrawler.git
- **作者**: 程序员阿江 (Relakkes)
- **本地路径**: `~/.openclaw/workspace/skills/mediacrawler/`
- **占用空间**: ~837MB（其中 .venv 740MB, .git 29MB, browser_data 59MB）
- **Python 版本**: 需要 Python 3.10+
- **安装时间**: 2026-03-23

### 恢复/重装步骤

```bash
cd ~/.openclaw/workspace/skills/
git clone https://github.com/NanmiCoder/MediaCrawler.git mediacrawler
cd mediacrawler
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # 或 pip install -e .
```

### 配置要点
- 需要配置小红书 Cookie 登录（待完成）
- browser_data/ 目录存放浏览器用户数据（爬虫运行时自动生成）
- 配置文件在 config/ 目录下

### 关联
- 训练营第 4 课内容：社媒引流——小红书自动化运营
- 小红书内容生产库多维表格: ArcRbxwmIaXT8usfzmdcIxM3npd

---

## 2. Agent Reach（互联网搜索/阅读能力）

- **用途**: 给 AI Agent 增加互联网搜索和阅读能力，支持 10+ 平台
- **GitHub**: https://github.com/Panniantong/agent-reach.git
- **作者**: Neo Reid (Panniantong)
- **版本**: 1.3.0
- **本地路径**: `~/.openclaw/workspace/skills/agent-reach/`
- **占用空间**: ~65MB（其中 .venv 62MB, .git 1.6MB）
- **Python 版本**: 需要 Python 3.10+
- **许可证**: MIT
- **安装时间**: 2026-03-23

### 恢复/重装步骤

```bash
cd ~/.openclaw/workspace/skills/
git clone https://github.com/Panniantong/agent-reach.git agent-reach
cd agent-reach
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 配置要点
- 配置文件在 config/ 目录下
- 支持 MCP 协议接入

---

## 备份排除说明

这两个项目因为包含 `.venv`（Python 虚拟环境）和 `.git` 历史，
体积过大（合计 ~900MB），会导致备份文件从 7MB 暴涨到 344MB。

已在备份脚本中排除：
- `skills/mediacrawler/`
- `skills/agent-reach/`

恢复时只需重新 `git clone` + 安装依赖即可，无需备份。
