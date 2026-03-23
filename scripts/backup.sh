#!/bin/bash
# OpenClaw 每日自动备份脚本
# 用法: bash ~/.openclaw/workspace/scripts/backup.sh

set -e

BACKUP_DIR="$HOME/openclaw-backups"
MAX_BACKUPS=7
LOG_FILE="$HOME/.openclaw/workspace/backups/backup.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

echo "[$TIMESTAMP] 开始备份..." >> "$LOG_FILE"

# 加载环境变量
if [ -f "$HOME/.openclaw/env.sh" ]; then
  source "$HOME/.openclaw/env.sh" 2>/dev/null || true
fi

# 执行完整备份（不停止 Gateway）
OUTPUT=$(openclaw backup create --verify --output "$BACKUP_DIR/openclaw_full_${TIMESTAMP}.tar.gz" 2>&1) || true
echo "[$TIMESTAMP] 备份输出: $OUTPUT" >> "$LOG_FILE"

# 检查备份文件
BACKUP_FILE="$BACKUP_DIR/openclaw_full_${TIMESTAMP}.tar.gz"
if [ -f "$BACKUP_FILE" ]; then
  SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
  echo "[$TIMESTAMP] ✅ 备份成功: $BACKUP_FILE ($SIZE)" >> "$LOG_FILE"
else
  # 如果官方命令失败，使用手动备份
  echo "[$TIMESTAMP] ⚠️ 官方备份命令失败，使用手动备份..." >> "$LOG_FILE"
  cd "$HOME"
  tar -czf "$BACKUP_DIR/openclaw_manual_${TIMESTAMP}.tar.gz" \
    --exclude='.openclaw/extensions' \
    --exclude='.openclaw/media' \
    --exclude='.openclaw/delivery-queue' \
    .openclaw/ 2>&1 || true
  
  BACKUP_FILE="$BACKUP_DIR/openclaw_manual_${TIMESTAMP}.tar.gz"
  if [ -f "$BACKUP_FILE" ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "[$TIMESTAMP] ✅ 手动备份成功: $BACKUP_FILE ($SIZE)" >> "$LOG_FILE"
  else
    echo "[$TIMESTAMP] ❌ 备份失败！" >> "$LOG_FILE"
    exit 1
  fi
fi

# 清理过期备份（保留最近 MAX_BACKUPS 个）
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/openclaw_*.tar.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
  DELETE_COUNT=$((BACKUP_COUNT - MAX_BACKUPS))
  ls -1t "$BACKUP_DIR"/openclaw_*.tar.gz | tail -n "$DELETE_COUNT" | while read f; do
    echo "[$TIMESTAMP] 🗑️ 删除过期备份: $f" >> "$LOG_FILE"
    rm -f "$f"
  done
fi

echo "[$TIMESTAMP] 备份完成，当前保留 $(ls -1 "$BACKUP_DIR"/openclaw_*.tar.gz 2>/dev/null | wc -l) 个备份" >> "$LOG_FILE"
