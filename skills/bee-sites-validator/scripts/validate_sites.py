#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bee.com Sites 验证脚本 - 被 bee-sites-validator skill 调用

流程：
1. 分页拉取 WordPress sites API
2. HTTP 初步检测（快速筛选非 200）
3. 返回 JSON 结果给 skill，由 skill 进行 Browser 深度验证
"""

import json
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


DEFAULT_API = "https://www.bee.com/wp-json/wp/v2/sites"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"


@dataclass
class SiteInfo:
    id: int
    wp_link: str
    site_go_url: Optional[str]
    twitter_links: List[str]
    http_status: Optional[int]
    http_error: Optional[str]


def build_session(timeout: int = 15) -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": UA})
    adapter = requests.adapters.HTTPAdapter(pool_connections=50, pool_maxsize=50, max_retries=2)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.request_timeout = timeout
    return session


def fetch_sites_page(session: requests.Session, api_url: str, page: int, per_page: int) -> List[Dict]:
    try:
        resp = session.get(api_url, params={"per_page": per_page, "page": page}, timeout=15)
        if resp.status_code == 400:
            return []
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[ERROR] 获取第{page}页失败：{e}", file=sys.stderr)
        return []


def normalize_url(url: str) -> str:
    return url.strip()


def extract_site_go_url(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    container = soup.select_one("div.site-go.mt-3.flex-row")
    if not container:
        return None
    node = container.select_one("span.site-go-url a[href]")
    if not node:
        return None
    href = node.get("href", "").strip()
    return href or None


def is_twitter_host(host: str) -> bool:
    host = host.lower()
    return host == "x.com" or host.endswith(".x.com") or host == "twitter.com" or host.endswith(".twitter.com")


def extract_twitter_links(html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    container = soup.select_one("div.site-go.mt-3.flex-row")
    if not container:
        return []
    links: List[str] = []
    seen: Set[str] = set()

    for a in container.select("a[href]"):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        parsed = urlparse(href)
        if parsed.scheme not in {"http", "https"}:
            continue
        if not is_twitter_host(parsed.netloc):
            continue
        if href in seen:
            continue
        seen.add(href)
        links.append(href)
    return links


def check_http_status(session: requests.Session, url: str, timeout: int = 10) -> Tuple[Optional[int], Optional[str]]:
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        return resp.status_code, None
    except requests.Timeout:
        return None, "请求超时"
    except requests.ConnectionError:
        return None, "连接失败"
    except Exception as e:
        return None, str(e)


def process_single_site(session: requests.Session, site_data: Dict, skip_domains: Set[str]) -> SiteInfo:
    site_id = site_data.get("id", 0)
    wp_link = normalize_url(site_data.get("link", ""))
    
    # 获取 WP 详情页 HTML
    html = ""
    wp_status, wp_error = check_http_status(session, wp_link)
    try:
        resp = session.get(wp_link, timeout=10)
        html = resp.text
    except:
        pass
    
    # 提取 site-go-url
    site_go_url = extract_site_go_url(html) if html else None
    
    # 检查主跳转链接的 HTTP 状态（关键！）
    site_go_status = None
    site_go_error = None
    site_go_skipped = False
    
    if site_go_url:
        domain = urlparse(site_go_url).netloc.lower()
        if any(domain == d or domain.endswith("." + d) for d in skip_domains):
            site_go_skipped = True  # 标记为跳过
        else:
            site_go_status, site_go_error = check_http_status(session, site_go_url)
    
    # 跳过指定域名的 site_go_url 设为 None
    if site_go_skipped:
        site_go_url = None
    
    twitter_links = extract_twitter_links(html) if html else []
    
    return SiteInfo(
        id=site_id,
        wp_link=wp_link,
        site_go_url=site_go_url,
        twitter_links=twitter_links,
        http_status=site_go_status,  # 返回主跳转链接的状态（不是 WP 详情页）
        http_error=site_go_error
    )


def fetch_all_sites(api_url: str, per_page: int = 100, max_pages: int = 0) -> List[Dict]:
    session = build_session()
    sites = []
    page = 1
    
    while True:
        if max_pages > 0 and page > max_pages:
            break
        rows = fetch_sites_page(session, api_url, page=page, per_page=per_page)
        if not rows:
            break
        
        for row in rows:
            if row.get("status") != "publish":
                continue
            link = row.get("link")
            if isinstance(link, str) and link.strip():
                sites.append(row)
        
        page += 1
        print(f"[INFO] 已获取第{page-1}页，累计{len(sites)}个 sites", file=sys.stderr)
    
    return sites


def run(api_url: str, skip_domains: Optional[Set[str]] = None, per_page: int = 100, max_pages: int = 0) -> Dict:
    start_at = datetime.now()
    session = build_session()
    _skip = skip_domains or {"t.me"}
    
    print(f"[INFO] 开始获取 sites 列表，API: {api_url}", file=sys.stderr)
    all_sites = fetch_all_sites(api_url, per_page=per_page, max_pages=max_pages)
    print(f"[INFO] 获取到 {len(all_sites)} 个 publish 状态的 sites", file=sys.stderr)
    
    results = []
    for idx, site_data in enumerate(all_sites):
        if (idx + 1) % 50 == 0:
            print(f"[INFO] 处理进度 {idx+1}/{len(all_sites)}", file=sys.stderr)
        
        site_info = process_single_site(session, site_data, _skip)
        results.append(asdict(site_info))
    
    end_at = datetime.now()
    duration = (end_at - start_at).total_seconds()
    
    # 统计
    total = len(results)
    with_site_go = sum(1 for r in results if r["site_go_url"])
    with_twitter = sum(1 for r in results if r["twitter_links"])
    http_non_200 = sum(1 for r in results if r["http_status"] and r["http_status"] != 200)
    
    report = {
        "start_at": start_at.isoformat(),
        "end_at": end_at.isoformat(),
        "duration_seconds": duration,
        "total_sites": total,
        "with_site_go_url": with_site_go,
        "with_twitter_links": with_twitter,
        "http_non_200_count": http_non_200,
        "sites": results
    }
    
    print(f"[INFO] 处理完成，耗时 {duration:.1f}s", file=sys.stderr)
    print(f"[INFO] 总计：{total} | 有主跳转：{with_site_go} | 有推特：{with_twitter} | HTTP 非 200: {http_non_200}", file=sys.stderr)
    
    return report


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Bee.com Sites 获取脚本")
    parser.add_argument("--api-url", default=DEFAULT_API, help="WordPress sites API 地址")
    parser.add_argument("--per-page", type=int, default=100, help="每页数量")
    parser.add_argument("--max-pages", type=int, default=0, help="最大页数，0 表示不限")
    parser.add_argument("--skip-domains", default="t.me", help="跳过检测的域名，逗号分隔")
    parser.add_argument("--output", default="", help="输出 JSON 文件路径")
    args = parser.parse_args()
    
    skip_set = {d.strip().lower() for d in args.skip_domains.split(",") if d.strip()} if args.skip_domains else {"t.me"}
    
    report = run(args.api_url, skip_set, args.per_page, args.max_pages)
    
    if args.output:
        Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[INFO] 报告已保存：{args.output}", file=sys.stderr)
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
