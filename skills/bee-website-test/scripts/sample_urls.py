#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bee.com 测试 - 快速模式抽样脚本
用于从全量列表中抽样 20% 进行测试，加快日常检查速度
"""

import json
import random
import sys
from pathlib import Path

def sample_urls(input_file: str, output_file: str, sample_rate: float = 0.2, seed: int = 42):
    """
    从 URL 列表中抽样指定比例
    
    Args:
        input_file: 输入 JSON 文件路径，格式：{"urls": ["url1", "url2", ...]}
        output_file: 输出 JSON 文件路径
        sample_rate: 抽样比例（0.0-1.0），默认 0.2（20%）
        seed: 随机种子，保证可复现
    """
    random.seed(seed)
    
    # 读取输入
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    urls = data.get('urls', [])
    if not urls:
        print(f"错误：输入文件中没有找到 URL 列表")
        sys.exit(1)
    
    # 计算抽样数量
    sample_count = max(1, int(len(urls) * sample_rate))
    
    # 随机抽样
    sampled = random.sample(urls, sample_count)
    
    # 输出结果
    output_data = {
        "total_count": len(urls),
        "sample_count": sample_count,
        "sample_rate": sample_rate,
        "sampled_urls": sampled,
        "note": f"快速模式：从 {len(urls)} 个 URL 中抽样 {sample_count} 个（{sample_rate*100:.0f}%）进行测试"
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"抽样完成：{sample_count}/{len(urls)} ({sample_rate*100:.0f}%)")
    print(f"输出文件：{output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法：python sample_urls.py <输入文件> <输出文件> [抽样比例]")
        print("示例：python sample_urls.py all_sites.json sampled_sites.json 0.2")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    sample_rate = float(sys.argv[3]) if len(sys.argv) > 3 else 0.2
    
    sample_urls(input_file, output_file, sample_rate)
