#!/usr/bin/env python3
"""
清华大学就业信息网 - 招聘信息每日同步爬虫
==========================================
功能：获取招聘信息列表及详情，筛选当日数据，输出JSON
API:
  - 列表: POST https://career.cic.tsinghua.edu.cn/xsglxt/b/jyxt/anony/xxfbForWx
  - 详情: GET https://career.cic.tsinghua.edu.cn/xsglxt/f/jyxt/anony/showZwxxForWx
无需认证，公开访问
"""

import requests
import json
import time
import re
from datetime import datetime, timezone, timedelta

# ==================== 配置 ====================
BASE_URL = "https://career.cic.tsinghua.edu.cn"
LIST_API = f"{BASE_URL}/xsglxt/b/jyxt/anony/xxfbForWx"
DETAIL_URL = f"{BASE_URL}/xsglxt/f/jyxt/anony/showZwxxForWx"

CST = timezone(timedelta(hours=8))
FILTER_DATE = datetime.now(CST).replace(hour=0, minute=0, second=0, microsecond=0)
FILTER_DATE_STR = FILTER_DATE.strftime("%Y-%m-%d")

MAX_PAGES = 2              # 每天前两页
MAX_DETAIL_CHARS = 2000    # 详情页最多提取字符数
MAX_RETRIES = 3
RETRY_DELAY = 2

OUTPUT_DIR = "/root/.openclaw/workspace/output/qinghua_daily"
OUTPUT_FILE = f"{OUTPUT_DIR}/qinghua_results.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded",
}


def api_post(url, data, timeout=15):
    """带重试的POST请求"""
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(url, headers=HEADERS, data=data, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            print(f"[WARN] 请求失败 (第{attempt+1}次): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                print(f"[ERROR] 请求彻底失败")
                return None
        except json.JSONDecodeError:
            print(f"[ERROR] JSON解析失败")
            return None
    return None


def fetch_list(page=1):
    """获取招聘信息列表"""
    return api_post(LIST_API, {"type": "ZPXX", "pgno": page})


def fetch_detail(zpxxid):
    """爬取单个职位的详情页"""
    url = f"{DETAIL_URL}?zpxxid={zpxxid}&type=ZPXX"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        html = resp.text

        # 取 #xxfb 区域
        body = re.search(r'id="xxfb"[^>]*>(.*?)</div>', html, re.DOTALL)
        if not body:
            body = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)

        text = ""
        if body:
            text = body.group(1)
            text = re.sub(r'<script[^>]*>.*?</script>', "", text, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', "", text, flags=re.DOTALL)
            text = re.sub(r'<br\s*/?>', "\n", text)
            text = re.sub(r'<[^>]+>', "", text)
            text = re.sub(r'\n{3,}', "\n\n", text)
            text = re.sub(r'&nbsp;', " ", text)
            text = text.strip()

        # 提取关键字段
        detail = {
            "学历要求": "",
            "专业要求": "",
            "联系邮箱": "",
            "联系电话": "",
            "详情全文": text[:MAX_DETAIL_CHARS],
        }

        # 从文本中提取邮箱
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        if emails:
            detail["联系邮箱"] = " / ".join(emails[:3])

        # 从文本中提取电话
        phones = re.findall(r'1[3-9]\d{9}', text)
        if phones:
            detail["联系电话"] = " / ".join(phones[:3])

        # 学历要求
        edu_match = re.search(r'(?:学历|学位)[要求：:]\s*([^\n]{2,30})', text)
        if edu_match:
            detail["学历要求"] = edu_match.group(1).strip()

        # 专业要求
        major_match = re.search(r'(?:专业|学科)[要求：:]\s*([^\n]{2,50})', text)
        if major_match:
            detail["专业要求"] = major_match.group(1).strip()

        return detail

    except Exception as e:
        print(f"[WARN] 详情页请求异常 {zpxxid}: {e}")
        return {"学历要求": "", "专业要求": "", "联系邮箱": "", "联系电话": "", "详情全文": ""}


def get_detail_url(zpxxid):
    return f"{DETAIL_URL}?zpxxid={zpxxid}&type=ZPXX"


def main():
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("清华大学就业信息网 - 每日同步爬虫")
    print(f"筛选日期：{FILTER_DATE_STR} (北京时间)")
    print("=" * 60)

    all_jobs = []
    seen_ids = set()

    for page in range(1, MAX_PAGES + 1):
        print(f"\n[INFO] 正在获取第 {page} 页...")
        result = fetch_list(page)

        if not result or not isinstance(result, list):
            print(f"[ERROR] 获取列表失败或格式异常")
            break

        matched = 0
        for item in result:
            # 筛选当天
            fbsj = item.get("fbsj", "")
            if not fbsj or not fbsj.startswith(FILTER_DATE_STR):
                continue

            zpxxid = str(item.get("id", ""))
            if zpxxid in seen_ids:
                continue
            seen_ids.add(zpxxid)

            matched += 1
            title = item.get("zwmc", "")
            company = item.get("dwmc", "")
            detail_url = get_detail_url(zpxxid)

            print(f"  [{matched}] {title[:40]} - {company[:30]}")

            # 获取详情
            detail = fetch_detail(zpxxid)

            all_jobs.append({
                "id": zpxxid,
                "标题": title,
                "公司/组织名称": company,
                "工作地点": item.get("gzdqmc", ""),
                "单位性质": item.get("dwxz", ""),
                "发布日期": fbsj,
                "是否置顶": item.get("sfzd", ""),
                "学历要求": detail.get("学历要求", ""),
                "专业要求": detail.get("专业要求", ""),
                "联系邮箱": detail.get("联系邮箱", ""),
                "联系电话": detail.get("联系电话", ""),
                "招聘详情(纯文本)": detail.get("详情全文", ""),
                "链接": detail_url,
            })
            time.sleep(0.5)  # 详情请求间隔

        print(f"[INFO] 第{page}页当日匹配: {matched} 条")
        time.sleep(1)  # 翻页间隔

    # 输出结果
    output = {
        "爬取时间": datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S"),
        "数据来源": "清华大学学生职业发展指导中心",
        "筛选日期": FILTER_DATE_STR,
        "总计数量": len(all_jobs),
        "职位列表": all_jobs,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"完成！共获取 {len(all_jobs)} 条今日招聘信息")
    print(f"结果已保存到: {OUTPUT_FILE}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()