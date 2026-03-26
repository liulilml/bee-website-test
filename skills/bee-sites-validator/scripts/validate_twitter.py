#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bee Sites 验证 - 推特账号验证脚本
验证推特账号是否被封禁、是否存在、最近是否有更新
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 封禁关键词列表
BANNED_KEYWORDS = [
    "Account suspended",
    "doesn't exist",
    "账号不存在",
    "已被封禁",
    "已被冻结",
    "This account doesn't exist",
    "Account does not exist",
    " suspended",
]

def check_twitter_status(snapshot_content: str) -> dict:
    """
    检查推特账号状态
    
    Args:
        snapshot_content: Browser snapshot 内容
    
    Returns:
        {
            "status": "PASS" | "FAIL" | "WARN",
            "reason": "原因说明",
            "banned": True/False,
            "last_tweet_date": "2026-03-20" | None
        }
    """
    result = {
        "status": "PASS",
        "reason": "",
        "banned": False,
        "last_tweet_date": None
    }
    
    # 检查封禁关键词
    for keyword in BANNED_KEYWORDS:
        if keyword.lower() in snapshot_content.lower():
            result["status"] = "FAIL"
            result["banned"] = True
            result["reason"] = f"检测到封禁关键词：{keyword}"
            return result
    
    # 检查 404
    if "404" in snapshot_content or "Not Found" in snapshot_content:
        result["status"] = "FAIL"
        result["reason"] = "账号页面返回 404"
        return result
    
    # 尝试提取最近推文时间（简化版，实际需要根据 snapshot 结构解析）
    # 这里假设 snapshot 包含时间信息，如 "2h"、"Mar 20"、"2026 年 3 月"
    last_tweet_date = extract_tweet_date(snapshot_content)
    result["last_tweet_date"] = last_tweet_date
    
    # 检查是否超过 2 个月未更新
    if last_tweet_date:
        try:
            tweet_date = datetime.strptime(last_tweet_date, "%Y-%m-%d")
            days_diff = (datetime.now() - tweet_date).days
            if days_diff > 60:
                result["status"] = "WARN"
                result["reason"] = f"超过 2 个月未更新（{days_diff}天前）"
        except ValueError:
            pass  # 日期格式解析失败，保持 PASS
    
    if result["status"] == "PASS":
        result["reason"] = "账号正常，近期有更新"
    
    return result

def extract_tweet_date(snapshot_content: str) -> str | None:
    """
    从 snapshot 内容中提取最近推文时间
    
    这是一个简化实现，实际使用时需要根据 Twitter 页面结构优化
    """
    # 尝试匹配常见日期格式
    import re
    
    # 格式：2026 年 3 月 20 日
    match = re.search(r'(\d{4}) 年 (\d{1,2}) 月 (\d{1,2}) 日', snapshot_content)
    if match:
        return f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"
    
    # 格式：Mar 20, 2026
    match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})', snapshot_content)
    if match:
        month_map = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        }
        month = month_map.get(match.group(1), "01")
        return f"{match.group(3)}-{month}-{match.group(2).zfill(2)}"
    
    # 格式：2h、5d 等相对时间（需要结合当前时间计算）
    match = re.search(r'(\d+)\s*(h|d|w|m) ago', snapshot_content)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        now = datetime.now()
        if unit == "h":
            date = now - timedelta(hours=value)
        elif unit == "d":
            date = now - timedelta(days=value)
        elif unit == "w":
            date = now - timedelta(weeks=value)
        elif unit == "m":
            date = now - timedelta(days=value * 30)
        else:
            return None
        return date.strftime("%Y-%m-%d")
    
    return None

def validate_twitter_accounts(input_file: str, output_file: str):
    """
    批量验证推特账号
    
    Args:
        input_file: 输入 JSON 文件，格式：
            {
                "accounts": [
                    {"id": 123, "twitter_url": "https://twitter.com/xxx", "snapshot": "..."},
                    ...
                ]
            }
        output_file: 输出 JSON 文件
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    accounts = data.get('accounts', [])
    results = []
    
    for account in accounts:
        twitter_url = account.get('twitter_url', '')
        snapshot = account.get('snapshot', '')
        
        if not twitter_url or not snapshot:
            continue
        
        status = check_twitter_status(snapshot)
        
        results.append({
            "id": account.get('id'),
            "twitter_url": twitter_url,
            "status": status["status"],
            "reason": status["reason"],
            "banned": status["banned"],
            "last_tweet_date": status["last_tweet_date"]
        })
    
    # 统计
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    warned = sum(1 for r in results if r["status"] == "WARN")
    banned = sum(1 for r in results if r["banned"])
    
    output_data = {
        "validation_date": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "warned": warned,
            "banned": banned
        },
        "results": results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"推特验证完成：{total} 个账号")
    print(f"  ✅ PASS: {passed}")
    print(f"  ❌ FAIL: {failed} (封禁：{banned})")
    print(f"  ⚠️ WARN: {warned}")
    print(f"输出文件：{output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法：python validate_twitter.py <输入文件> <输出文件>")
        print("示例：python validate_twitter.py twitter_accounts.json twitter_results.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    validate_twitter_accounts(input_file, output_file)
