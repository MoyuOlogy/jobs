#!/usr/bin/env python3
"""
上海交通大学就业信息网 - 招聘信息每日同步爬虫
==========================================
功能：获取招聘信息列表及详情，筛选当日数据，输出JSON
API:
  - 列表: POST /career/zpxx/search/zpxx/{pageNum}/{pageSize}
  - 详情: POST /career/zpxx/data/zpxx/{zpxxid}
无需认证，公开访问
"""

import requests
import json
import time
import re
import os
from datetime import datetime, timezone, timedelta

# ==================== 配置 ====================
BASE_URL = "https://www.job.sjtu.edu.cn/career"
LIST_API = f"{BASE_URL}/zpxx/search/zpxx"  # 后面拼 /{pageNum}/{pageSize}
DETAIL_API = f"{BASE_URL}/zpxx/data/zpxx"  # 后面拼 /{zpxxid}
DETAIL_URL_BASE = f"{BASE_URL}/zpxx/view/zpxx"  # 前端详情页

CST = timezone(timedelta(hours=8))
FILTER_DATE = datetime.now(CST).replace(hour=0, minute=0, second=0, microsecond=0)
FILTER_DATE_STR = FILTER_DATE.strftime("%Y-%m-%d")

PAGE_SIZE = 10              # SJTU 仅允许未登录用户使用 10 条/页
MAX_PAGES = 3               # 前3页
MAX_DETAIL_CHARS = 2000     # 详情页最多提取字符数
MAX_RETRIES = 3
RETRY_DELAY = 2

OUTPUT_DIR = "/root/.openclaw/workspace/output/sjtu_daily"
OUTPUT_FILE = f"{OUTPUT_DIR}/sjtu_results.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://www.job.sjtu.edu.cn/career/zpxx/zpxx",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}


def strip_html(html_text):
    """去除HTML标签，提取纯文本"""
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
    text = text.strip()
    return text


def api_post(url, data=None, timeout=15):
    """带重试的POST请求"""
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
                print(f"[ERROR] 请求彻底失败")
                return None
        except json.JSONDecodeError:
            print(f"[ERROR] JSON解析失败")
            return None
    return None


def fetch_list(page=1, size=PAGE_SIZE):
    """获取招聘信息列表"""
    url = f"{LIST_API}/{page}/{size}"
    return api_post(url)


def fetch_detail(zpxxid):
    """获取职位详情（通过数据API）"""
    url = f"{DETAIL_API}/{zpxxid}"
    result = api_post(url)
    if result and result.get("code") == 200:
        return result.get("data", {})
    return None


def get_detail_url(zpxxid):
    """生成职位详情页链接"""
    return f"{DETAIL_URL_BASE}/{zpxxid}"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    now = datetime.now(CST)
    print("=" * 60)
    print("上海交通大学就业信息网 - 每日同步爬虫")
    print(f"运行时间：{now.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
    print(f"筛选日期：{FILTER_DATE_STR}")
    print("=" * 60)

    all_jobs = []
    seen_ids = set()

    for page in range(1, MAX_PAGES + 1):
        print(f"\n[INFO] 正在获取第 {page} 页...")
        result = fetch_list(page)

        if not result or result.get("code") != 200:
            print(f"[ERROR] 获取列表失败: {result}")
            break

        data = result.get("data", {})
        items = data.get("list", [])
        total = data.get("total", "?")
        print(f"[INFO] 总记录 {total} 条，当前页 {len(items)} 条")

        if not items:
            print("[INFO] 当前页无数据，停止")
            break

        matched = 0
        earliest_date = None

        for item in items:
            fbrq = item.get("fbrq", "")
            if not fbrq:
                continue

            # 跟踪最早日期，用于决定是否继续翻页
            try:
                dt = datetime.strptime(fbrq, "%Y-%m-%d").replace(tzinfo=CST)
                if earliest_date is None or dt < earliest_date:
                    earliest_date = dt
            except ValueError:
                pass

            # 只筛选当天
            if not fbrq.startswith(FILTER_DATE_STR):
                continue

            zpxxid = str(item.get("zpxxid", ""))
            if not zpxxid or zpxxid in seen_ids:
                continue
            seen_ids.add(zpxxid)

            matched += 1
            title = item.get("zpzt", "")
            company = item.get("dwmc", "")
            print(f"  [{matched}] {title[:50]} - {company[:30]}")

            # 获取详情数据
            detail_data = fetch_detail(zpxxid) or item

            # 提取纯文本描述
            zpxx_editor = detail_data.get("zpxxEditor", "") or ""
            dwjs = detail_data.get("dwjs", "") or ""
            info_text = strip_html(zpxx_editor or dwjs)[:MAX_DETAIL_CHARS]

            # 提取邮箱
            email_raw = detail_data.get("jltdyx", "") or item.get("jltdyx", "") or ""
            emails = []
            if email_raw and '@' in email_raw and 'login' not in email_raw.lower():
                emails.append(email_raw)
            # 也从详情HTML中提取
            if zpxx_editor:
                found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', zpxx_editor)
                emails.extend(found)
            emails = list(dict.fromkeys(emails))[:3]  # 去重，最多3个

            detail_url = get_detail_url(zpxxid)

            all_jobs.append({
                "zpxxid": zpxxid,
                "标题": title,
                "公司/组织名称": company,
                "发布日期": fbrq,
                "截止日期": detail_data.get("zpjzrq", "") or item.get("zpjzrq", ""),
                "行业": detail_data.get("hyyjmc", "") or item.get("hyyjmc", ""),
                "单位性质": (detail_data.get("xzyjmc", "") or item.get("xzyjmc", "") or
                          detail_data.get("xzsjmc", "") or item.get("xzsjmc", "")),
                "工作地点": ((detail_data.get("szssmc", "") or item.get("szssmc", "") or "") +
                          (detail_data.get("szxmc", "") or item.get("szxmc", "") or "").replace("市辖区", "")),
                "公司规模": detail_data.get("rsgmmc", "") or item.get("rsgmmc", ""),
                "需求人数": detail_data.get("xqrsmc", "") or item.get("xqrsmc", "") or "",
                "学历要求": detail_data.get("xqxlmc", "") or item.get("xqxlmc", "") or "",
                "专业要求": detail_data.get("xqzymc", "") or item.get("xqzymc", "") or "",
                "网申网址": detail_data.get("zpxxwz", "") or item.get("zpxxwz", "") or "",
                "简历投递邮箱": " / ".join(emails),
                "公司地址": detail_data.get("xxdz", "") or item.get("xxdz", "") or "",
                "公司网址": detail_data.get("dwwz", "") or item.get("dwwz", "") or "",
                "单位介绍": strip_html(detail_data.get("dwjs", "") or item.get("dwjs", ""))[:1000],
                "招聘详情(纯文本)": info_text,
                "链接": detail_url,
            })
            time.sleep(0.3)  # 详情请求间隔

        print(f"[INFO] 第{page}页当日匹配: {matched} 条")

        # 如果整页都已经是旧数据，停止翻页
        if earliest_date and earliest_date < FILTER_DATE:
            print(f"[INFO] 第{page}页最早日期 {earliest_date.strftime('%Y-%m-%d')} 已早于筛选日期，停止翻页")
            break

        time.sleep(1)  # 翻页间隔

    # 输出结果
    output = {
        "爬取时间": now.strftime("%Y-%m-%d %H:%M:%S"),
        "数据来源": "上海交通大学学生就业服务和职业发展中心 - 招聘信息",
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