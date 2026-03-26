#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
禅道测试用例 CSV 生成器
根据确认的测试点生成禅道可导入的 CSV 文件

禅道 CSV 格式规范：
- 28 个字段
- UTF-8 with BOM 编码
- 所有字段用双引号包裹
- 换行符在字段内用实际换行（\n）
"""

import csv
import sys
import json
from datetime import datetime
from pathlib import Path

# 禅道 CSV 字段名（28 个）
CSV_FIELDNAMES = [
    "用例编号", "所属产品", "所属模块", "相关软件需求", "所属场景",
    "用例标题", "前置条件", "步骤", "预期", "实际情况",
    "关键词", "优先级", "用例类型", "适用阶段", "用例状态",
    "B", "R", "S", "执行人", "执行时间",
    "结果", "由谁创建", "创建日期", "最后修改者",
    "修改日期", "用例版本", "相关用例", "附件"
]

def expand_test_point_to_cases(test_point: dict, product_name: str, module_name: str, creator: str) -> list:
    """
    将一个测试点展开为一个或多个测试用例
    
    Args:
        test_point: 测试点字典，格式：
            {
                "id": "TP-001",
                "title": "未订阅用户点击订阅按钮",
                "type": "正向",  # 正向/反向/边界/特殊
                "precondition": "用户未登录",
                "steps": ["1. 打开会员页", "2. 点击订阅按钮"],
                "expected": ["1. 显示登录弹窗", "2. 跳转支付页"],
                "priority": 2  # 1-4
            }
        product_name: 产品名称（如 "Bee-Flutter3(#24)"）
        module_name: 模块名称（如 "/会员订阅 (#380)"）
        creator: 创建者姓名
    
    Returns:
        测试用例列表
    """
    cases = []
    
    # 根据测试点类型决定优先级
    priority = test_point.get("priority", 2)
    if test_point.get("type") == "正向":
        priority = min(priority, 2)  # 正向测试优先级不低于 2
    elif test_point.get("type") == "反向":
        priority = max(priority, 2)  # 反向测试优先级不高于 3
    elif test_point.get("type") == "边界":
        priority = max(priority, 3)  # 边界测试优先级不高于 3
    
    # 生成用例编号
    case_id = test_point.get("id", "TP-001").replace("TP-", "CASE-")
    
    # 提取关键词（从标题中提取 2-4 个）
    keywords = extract_keywords(test_point.get("title", ""))
    
    # 构建用例
    case = {
        "用例编号": case_id,
        "所属产品": product_name,
        "所属模块": module_name,
        "相关软件需求": "",
        "所属场景": "/(#0)",
        "用例标题": test_point.get("title", ""),
        "前置条件": test_point.get("precondition", ""),
        "步骤": "\n".join(test_point.get("steps", [])),
        "预期": "\n".join(test_point.get("expected", [])),
        "实际情况": "\n".join([f"{i+1}. " for i in range(len(test_point.get("steps", [])))]),
        "关键词": keywords,
        "优先级": str(priority),
        "用例类型": "功能测试",
        "适用阶段": "功能测试阶段",
        "用例状态": "正常",
        "B": "0",
        "R": "0",
        "S": str(len(test_point.get("steps", []))),
        "执行人": "",
        "执行时间": "",
        "结果": "",
        "由谁创建": creator,
        "创建日期": datetime.now().strftime("%Y-%m-%d"),
        "最后修改者": "",
        "修改日期": "",
        "用例版本": "1",
        "相关用例": "",
        "附件": ""
    }
    
    cases.append(case)
    return cases

def extract_keywords(title: str) -> str:
    """
    从用例标题中提取关键词（2-4 个）
    简化实现：按空格/标点分割，取前 4 个有意义的词
    """
    import re
    
    # 移除常见停用词
    stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个"}
    
    # 按标点/空格分割
    words = re.split(r'[,\s.，。、]+', title)
    
    # 过滤停用词和空词
    keywords = [w for w in words if w and w not in stop_words and len(w) > 1]
    
    # 取前 4 个
    keywords = keywords[:4]
    
    return ",".join(keywords)

def generate_csv(test_points: list, output_file: str, config: dict):
    """
    生成禅道 CSV 文件
    
    Args:
        test_points: 测试点列表
        output_file: 输出文件路径
        config: 配置字典
            {
                "product_name": "Bee-Flutter3(#24)",
                "module_name": "/会员订阅 (#380)",
                "creator": "李茂林"
            }
    """
    product_name = config.get("product_name", "")
    module_name = config.get("module_name", "")
    creator = config.get("creator", "李茂林")
    
    # 展开所有测试点为用例
    all_cases = []
    for tp in test_points:
        cases = expand_test_point_to_cases(tp, product_name, module_name, creator)
        all_cases.extend(cases)
    
    # 重新编号（从 1 开始）
    for i, case in enumerate(all_cases, 1):
        case["用例编号"] = str(i)
    
    # 写入 CSV（UTF-8 with BOM）
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(all_cases)
    
    # 统计
    total = len(all_cases)
    p1 = sum(1 for c in all_cases if c["优先级"] == "1")
    p2 = sum(1 for c in all_cases if c["优先级"] == "2")
    p3 = sum(1 for c in all_cases if c["优先级"] == "3")
    p4 = sum(1 for c in all_cases if c["优先级"] == "4")
    
    print(f"CSV 生成完成：{output_file}")
    print(f"  总用例数：{total}")
    print(f"  P1: {p1} | P2: {p2} | P3: {p3} | P4: {p4}")
    print(f"  产品：{product_name}")
    print(f"  模块：{module_name}")
    print(f"  创建者：{creator}")

def load_test_points(input_file: str) -> list:
    """
    从 JSON 文件加载测试点
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("test_points", [])

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法：python generate_csv.py <输入文件> <输出文件> <产品名> <模块名> [创建者]")
        print("示例：python generate_csv.py test_points.json testcases.csv 'Bee-Flutter3(#24)' '/会员订阅 (#380)' '李茂林'")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    product_name = sys.argv[3]
    module_name = sys.argv[4] if len(sys.argv) > 4 else ""
    creator = sys.argv[5] if len(sys.argv) > 5 else "李茂林"
    
    test_points = load_test_points(input_file)
    
    config = {
        "product_name": product_name,
        "module_name": module_name,
        "creator": creator
    }
    
    generate_csv(test_points, output_file, config)
