#!/usr/bin/env python3
"""
上海交通大学就业信息网 - 招聘信息交互式获取脚本
==========================================
功能：获取招聘信息列表及详情，支持日期筛选和详情爬取
用法：
  python3 sjtujobs.py               # 前3页（含详情）
  python3 sjtujobs.py --pages 5     # 指定翻页数
  python3 sjtujobs.py --today       # 仅当天
  python3 sjtujobs.py --date 2026-05-22  # 指定日期
"""

import requests
import json
import time
import re
import argparse
import os
from datetime import datetime, timezone, timedelta

# ==================== 配置 ====================
BASE_URL = "https://www.job.sjtu.edu.cn/career"
LIST_API = f"{BASE_URL}/zpxx/search/zpxx"
DETAIL_API = f"{BASE_URL}/zpxx/data/zpxx"
DETAIL_URL_BASE = f"{BASE_URL}/zpxx/view/zpxx"

CST = timezone(timedelta(hours=8))
PAGE_SIZE = 10              # SJTU 仅允许未登录用户使用 10 条/页
MAX_DETAIL_CHARS = 2000
MAX_RETRIES = 3
RETRY_DELAY = 2

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://www.job.sjtu.edu.cn/career/zpxx/zpxx",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}


def strip_html(html_text):
    if not html_text:
        return ""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_text, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', html_text, flags=re.DOTALL)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def api_post(url, data=None, timeout=15):
    for attempt in range(MAX_RETRIES):
        try:
            if data:
                resp = requests.post(url, headers=HEADERS, data=data, timeout=timeout)
            else:
                resp = requests.post(url, headers=HEADERS, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            print(f"[WARN] 请求失败 (第{attempt+1}次): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                return None
        except json.JSONDecodeError:
            return None
    return None


def fetch_list(page=1, size=PAGE_SIZE, filters=None):
    url = f"{LIST_API}/{page}/{size}"
    return api_post(url, data=filters)


def fetch_detail(zpxxid):
    url = f"{DETAIL_API}/{zpxxid}"
    result = api_post(url)
    if result and result.get("code") == 200:
        return result.get("data", {})
    return None


def main():
    parser = argparse.ArgumentParser(description="上海交通大学就业信息网招聘信息爬虫")
    parser.add_argument("--pages", type=int, default=3, help="翻页数 (默认: 3)")
    parser.add_argument("--date", type=str, help="筛选日期 (格式: YYYY-MM-DD)")
    parser.add_argument("--today", action="store_true", help="筛选当天")
    parser.add_argument("--detail", action="store_true", help="获取详情（默认开启）")
    parser.add_argument("--save", action="store_true", help="保存到文件")
    parser.add_argument("--no-detail", action="store_true", help="不获取详情")
    args = parser.parse_args()

    # 筛选日期
    if args.today or not args.date:
        filter_date_str = datetime.now(CST).strftime("%Y-%m-%d")
    else:
        filter_date_str = args.date

    filter_date = datetime.strptime(filter_date_str, "%Y-%m-%d").replace(tzinfo=CST)

    print("=" * 60)
    print("上海交通大学就业信息网 - 招聘信息获取")
    print(f"筛选日期：{filter_date_str}")
    if args.no_detail:
        print("模式：仅列表（无详情）")
    else:
        print("模式：含详情爬取")
    print("=" * 60)

    all_jobs = []
    seen_ids = set()

    for page in range(1, args.pages + 1):
        print(f"\n[INFO] 正在获取第 {page} 页...")
        result = fetch_list(page)

        if not result or result.get("code") != 200:
            print(f"[ERROR] 获取列表失败")
            break

        data = result.get("data", {})
        items = data.get("list", [])
        total = data.get("total", "?")
        print(f"[INFO] 总记录 {total} 条，当前页 {len(items)} 条")

        if not items:
            break

        matched = 0
        earliest_date = None

        for item in items:
            fbrq = item.get("fbrq", "")
            if not fbrq:
                continue

            try:
                dt = datetime.strptime(fbrq, "%Y-%m-%d").replace(tzinfo=CST)
                if earliest_date is None or dt < earliest_date:
                    earliest_date = dt
            except ValueError:
                pass

            if not fbrq.startswith(filter_date_str):
                continue

            zpxxid = str(item.get("zpxxid", ""))
            if not zpxxid or zpxxid in seen_ids:
                continue
            seen_ids.add(zpxxid)

            matched += 1
            title = item.get("zpzt", "")
            company = item.get("dwmc", "")
            detail_url = f"{DETAIL_URL_BASE}/{zpxxid}"

            print(f"  [{matched:3d}] {title[:40]:40s} | {company[:25]:25s} | {fbrq}")

            # 获取详情
            if not args.no_detail:
                detail_data = fetch_detail(zpxxid) or item
            else:
                detail_data = item

            zpxx_editor = detail_data.get("zpxxEditor", "") or ""
            dwjs = detail_data.get("dwjs", "") or ""
            info_text = strip_html(zpxx_editor or dwjs)[:MAX_DETAIL_CHARS]

            emails = []
            email_raw = detail_data.get("jltdyx", "") or item.get("jltdyx", "") or ""
            if email_raw and '@' in email_raw and 'login' not in email_raw.lower():
                emails.append(email_raw)
            if zpxx_editor:
                found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', zpxx_editor)
                emails.extend(found)
            emails = list(dict.fromkeys(emails))[:3]

            location = ((detail_data.get("szssmc", "") or item.get("szssmc", "") or "") +
                       (detail_data.get("szxmc", "") or item.get("szxmc", "") or "").replace("市辖区", ""))

            job_entry = {
                "zpxxid": zpxxid,
                "标题": title,
                "公司/组织名称": company,
                "发布日期": fbrq,
                "截止日期": detail_data.get("zpjzrq", "") or item.get("zpjzrq", ""),
                "行业": detail_data.get("hyyjmc", "") or item.get("hyyjmc", ""),
                "单位性质": (detail_data.get("xzyjmc", "") or item.get("xzyjmc", "") or
                          detail_data.get("xzsjmc", "") or item.get("xzsjmc", "")),
                "工作地点": location,
                "公司规模": detail_data.get("rsgmmc", "") or item.get("rsgmmc", ""),
                "需求人数": detail_data.get("xqrsmc", "") or item.get("xqrsmc", "") or "",
                "学历要求": detail_data.get("xqxlmc", "") or item.get("xqxlmc", "") or "",
                "专业要求": detail_data.get("xqzymc", "") or item.get("xqzymc", "") or "",
                "网申网址": detail_data.get("zpxxwz", "") or item.get("zpxxwz", "") or "",
                "简历投递邮箱": " / ".join(emails),
                "招聘详情(纯文本)": info_text,
                "链接": detail_url,
            }
            all_jobs.append(job_entry)

            if not args.no_detail:
                time.sleep(0.3)

        print(f"[INFO] 第{page}页当日匹配: {matched} 条")

        if earliest_date and earliest_date < filter_date:
            print(f"[INFO] 已到达筛选日期之前的记录，停止翻页")
            break

        time.sleep(1)

    print(f"\n{'=' * 60}")
    print(f"完成！共获取 {len(all_jobs)} 条招聘信息")

    if args.save:
        output_dir = "/root/.openclaw/workspace/output/sjtu_daily"
        os.makedirs(output_dir, exist_ok=True)
        output_file = f"{output_dir}/sjtu_results.json"
        output = {
            "爬取时间": datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S"),
            "数据来源": "上海交通大学学生就业服务和职业发展中心 - 招聘信息",
            "筛选日期": filter_date_str,
            "总计数量": len(all_jobs),
            "职位列表": all_jobs,
        }
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {output_file}")
    else:
        print(json.dumps(all_jobs, ensure_ascii=False, indent=2))

    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()