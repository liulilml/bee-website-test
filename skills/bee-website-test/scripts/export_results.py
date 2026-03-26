#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bee.com 测试结果 JSON 导出脚本
将测试结果导出为标准 JSON 格式，便于程序处理和对比
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def export_results(test_results: dict, output_file: str, previous_file: str = None):
    """
    导出测试结果到 JSON 文件
    
    Args:
        test_results: 测试结果字典，格式：
            {
                "test_date": "2026-03-25",
                "test_time": "01:00 ~ 01:40",
                "summary": {
                    "pass": 256,
                    "fail": 0,
                    "warn": 9,
                    "total": 265
                },
                "sections": {
                    "base_pages": [...],
                    "sites": [...],
                    "articles": [...],
                    "games": [...],
                    "dapps": [...],
                    "social_media": [...],
                    ...
                }
            }
        output_file: 输出 JSON 文件路径
        previous_file: 前一天结果文件路径（可选，用于对比）
    """
    
    # 构建标准格式输出
    export_data = {
        "validation_date": datetime.now().isoformat(),
        "test_date": test_results.get("test_date", ""),
        "test_time": test_results.get("test_time", ""),
        "summary": {
            "pass_count": test_results.get("summary", {}).get("pass", 0),
            "fail_count": test_results.get("summary", {}).get("fail", 0),
            "warn_count": test_results.get("summary", {}).get("warn", 0),
            "total_count": test_results.get("summary", {}).get("total", 0),
            "pass_rate": round(
                test_results.get("summary", {}).get("pass", 0) / 
                max(1, test_results.get("summary", {}).get("total", 1)) * 100, 
                2
            )
        },
        "coverage": {
            "base_pages": {"total": 9, "tested": 0},
            "sites": {"total": 0, "tested": 0},
            "articles": {"total": 0, "tested": 0},
            "games": {"total": 0, "tested": 0},
            "dapps": {"total": 0, "tested": 0},
            "social_media": {"total": 8, "tested": 0}
        },
        "problem_sites": {
            "fail": [],
            "warn": []
        },
        "comparison": None
    }
    
    # 填充覆盖数据
    sections = test_results.get("sections", {})
    for section_name, items in sections.items():
        if isinstance(items, list):
            count = len(items)
            if section_name in export_data["coverage"]:
                export_data["coverage"][section_name]["tested"] = count
                export_data["coverage"][section_name]["total"] = count
    
    # 提取问题项
    for section_name, items in sections.items():
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    status = item.get("status", "")
                    if status == "FAIL":
                        export_data["problem_sites"]["fail"].append({
                            "section": section_name,
                            "url": item.get("url", ""),
                            "reason": item.get("reason", "")
                        })
                    elif status == "WARN":
                        export_data["problem_sites"]["warn"].append({
                            "section": section_name,
                            "url": item.get("url", ""),
                            "reason": item.get("reason", "")
                        })
    
    # 对比分析（如果有前一天数据）
    if previous_file and Path(previous_file).exists():
        with open(previous_file, 'r', encoding='utf-8') as f:
            previous = json.load(f)
        
        comparison = {
            "previous_date": previous.get("test_date", ""),
            "regressions": [],  # 昨天 PASS 今天 FAIL
            "fixed": [],  # 昨天 FAIL 今天 PASS
            "new_fail": [],  # 新增失败
            "new_warn": []  # 新增警告
        }
        
        # 简单对比逻辑（实际使用时需要更复杂的匹配）
        prev_fail_urls = set()
        prev_warn_urls = set()
        
        for section_name, items in previous.get("sections", {}).items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        status = item.get("status", "")
                        url = item.get("url", "")
                        if status == "FAIL":
                            prev_fail_urls.add(url)
                        elif status == "WARN":
                            prev_warn_urls.add(url)
        
        # 找出回归和新增问题
        for section_name, items in sections.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        status = item.get("status", "")
                        url = item.get("url", "")
                        
                        if status == "FAIL":
                            if url in prev_fail_urls:
                                pass  # 持续失败
                            else:
                                comparison["new_fail"].append({
                                    "section": section_name,
                                    "url": url,
                                    "reason": item.get("reason", "")
                                })
                        elif status == "WARN":
                            if url not in prev_warn_urls:
                                comparison["new_warn"].append({
                                    "section": section_name,
                                    "url": url,
                                    "reason": item.get("reason", "")
                                })
        
        export_data["comparison"] = comparison
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"JSON 导出完成：{output_file}")
    print(f"通过率：{export_data['summary']['pass_rate']}%")
    print(f"失败项：{len(export_data['problem_sites']['fail'])}")
    print(f"警告项：{len(export_data['problem_sites']['warn'])}")
    
    return export_data

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法：python export_results.py <输入文件> <输出文件> [前一天文件]")
        print("示例：python export_results.py test_results.json result_2026-03-25.json result_2026-03-24.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    previous_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    # 读取输入
    with open(input_file, 'r', encoding='utf-8') as f:
        test_results = json.load(f)
    
    export_results(test_results, output_file, previous_file)
