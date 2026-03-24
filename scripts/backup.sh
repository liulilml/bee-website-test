#!/bin/bash
# OpenClaw 每日自动备份脚本（加密 + GitHub 推送版）
# 用法: bash ~/.openclaw/workspace/scripts/backup.sh

set -e

BACKUP_DIR="$HOME/openclaw-backups"
GITHUB_REPO_DIR="$HOME/openclaw-backups/git-repo"
MAX_BACKUPS=7
LOG_FILE="$HOME/.openclaw/workspace/backups/backup.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
GPG_PASSPHRASE="openclaw_backup_$(hostname)_2026"

mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
  echo "[$(date +%Y%m%d_%H%M%S)] $1" >> "$LOG_FILE"
}

log "========== 开始备份 =========="

# 加载环境变量
if [ -f "$HOME/.openclaw/env.sh" ]; then
  source "$HOME/.openclaw/env.sh" 2>/dev/null || true
fi

# ===== Step 1: 执行完整备份 =====
BACKUP_FILE="$BACKUP_DIR/openclaw_full_${TIMESTAMP}.tar.gz"

# 手动 tar 备份，排除大型外部项目（有独立 Git 仓库，可随时重装）
# 排除列表见 memory/external-projects.md
log "📦 开始打包备份（排除大型外部项目）..."
cd "$HOME"
tar -czf "$BACKUP_FILE" \
  --exclude='.openclaw/extensions' \
  --exclude='.openclaw/media' \
  --exclude='.openclaw/delivery-queue' \
  --exclude='.openclaw/workspace/skills/mediacrawler' \
  --exclude='.openclaw/workspace/skills/agent-reach' \
  --exclude='*/.venv' \
  --exclude='*/node_modules' \
  --exclude='*/__pycache__' \
  .openclaw/ 2>&1 || true

if [ ! -f "$BACKUP_FILE" ]; then
  log "❌ 备份失败！"
  exit 1
fi

SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
log "✅ 备份成功: $BACKUP_FILE ($SIZE)"

# ===== Step 2: GPG 加密 =====
ENCRYPTED_FILE="${BACKUP_FILE}.gpg"
echo "$GPG_PASSPHRASE" | gpg --batch --yes --passphrase-fd 0 --symmetric --cipher-algo AES256 -o "$ENCRYPTED_FILE" "$BACKUP_FILE" 2>&1

if [ -f "$ENCRYPTED_FILE" ]; then
  ENC_SIZE=$(du -h "$ENCRYPTED_FILE" | cut -f1)
  log "🔐 加密成功: $ENCRYPTED_FILE ($ENC_SIZE)"
  # 删除未加密的原始文件
  rm -f "$BACKUP_FILE"
  log "🗑️ 已删除未加密备份文件"
else
  log "⚠️ 加密失败，保留未加密备份"
  ENCRYPTED_FILE="$BACKUP_FILE"
fi

# ===== Step 3: 推送到 GitHub =====
if [ -n "$GITHUB_BACKUP_TOKEN" ] && [ -n "$GITHUB_BACKUP_REPO" ]; then
  log "📤 开始推送到 GitHub..."

  # 初始化或更新 Git 仓库
  if [ ! -d "$GITHUB_REPO_DIR/.git" ]; then
    mkdir -p "$GITHUB_REPO_DIR"
    cd "$GITHUB_REPO_DIR"
    git init
    git config user.email "openclaw@backup"
    git config user.name "OpenClaw Backup"
    # 从 GITHUB_BACKUP_REPO 提取仓库路径
    REPO_PATH=$(echo "$GITHUB_BACKUP_REPO" | sed 's|https://github.com/||')
    git remote add origin "https://x-access-token:${GITHUB_BACKUP_TOKEN}@github.com/${REPO_PATH}.git"
    echo "# OpenClaw Encrypted Backups" > README.md
    echo "" >> README.md
    echo "This repository contains AES-256 encrypted backups of OpenClaw." >> README.md
    echo "" >> README.md
    echo "⚠️ All backup files are GPG encrypted. You need the passphrase to decrypt." >> README.md
    echo "" >> README.md
    echo "## Decrypt" >> README.md
    echo '```bash' >> README.md
    echo 'gpg --decrypt backup_file.tar.gz.gpg > backup.tar.gz' >> README.md
    echo '```' >> README.md
    git add README.md
    git commit -m "Initial: encrypted backup repository"
  else
    cd "$GITHUB_REPO_DIR"
  fi

  # 复制加密备份到 Git 仓库
  BACKUP_FILENAME=$(basename "$ENCRYPTED_FILE")
  cp "$ENCRYPTED_FILE" "$GITHUB_REPO_DIR/$BACKUP_FILENAME"

  # 清理旧备份（保留最近 MAX_BACKUPS 个）
  REPO_BACKUP_COUNT=$(ls -1 "$GITHUB_REPO_DIR"/openclaw_*.gpg 2>/dev/null | wc -l)
  if [ "$REPO_BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
    DELETE_COUNT=$((REPO_BACKUP_COUNT - MAX_BACKUPS))
    ls -1t "$GITHUB_REPO_DIR"/openclaw_*.gpg | tail -n "$DELETE_COUNT" | while read f; do
      log "🗑️ 删除 Git 仓库中的过期备份: $(basename $f)"
      rm -f "$f"
    done
  fi

  # 提交并推送
  git add -A
  git commit -m "Backup: $TIMESTAMP (encrypted, $ENC_SIZE)" 2>&1 || true

  # 推送（首次用 -u 设置上游）
  if git push origin main 2>&1; then
    log "✅ GitHub 推送成功 (main)"
  elif git push origin master 2>&1; then
    log "✅ GitHub 推送成功 (master)"
  elif git branch -M main && git push -u origin main 2>&1; then
    log "✅ GitHub 首次推送成功 (main)"
  else
    log "⚠️ GitHub 推送失败"
  fi
else
  log "⚠️ GitHub 未配置，跳过远程推送"
fi

# ===== Step 4: 清理本地过期备份 =====
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/openclaw_*.gpg 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
  DELETE_COUNT=$((BACKUP_COUNT - MAX_BACKUPS))
  ls -1t "$BACKUP_DIR"/openclaw_*.gpg | tail -n "$DELETE_COUNT" | while read f; do
    log "🗑️ 删除本地过期备份: $(basename $f)"
    rm -f "$f"
  done
fi

FINAL_COUNT=$(ls -1 "$BACKUP_DIR"/openclaw_*.gpg 2>/dev/null | wc -l)
log "✅ 备份完成！本地保留 $FINAL_COUNT 个加密备份"
log "========== 备份结束 =========="
