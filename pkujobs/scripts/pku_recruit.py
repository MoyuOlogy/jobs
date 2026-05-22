#!/usr/bin/env python3
"""
北京大学就业信息网 - 日常招聘爬虫
==========================================
功能：获取日常招聘信息列表及详情（前两页）
API:
  - 列表: POST /f/recruitmentinfo/ajax_frontRecruitinfo (positionType=1)
  - 详情: POST /f/recruitmentinfo/ajax_show
认证: token: 111
"""

import requests
import json
import time
import re
from datetime import datetime, timezone, timedelta

# ==================== 配置 ====================
BASE_URL = "https://scc.pku.edu.cn/"
TOKEN = "111"
HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "token": TOKEN,
}

PAGE_SIZE = 15  # 北大就业网每页15条
MAX_PAGES = 2   # 抓取前两页

MAX_RETRIES = 3
RETRY_DELAY = 2

CST = timezone(timedelta(hours=8))
FILTER_DATE = datetime.now(CST).replace(hour=0, minute=0, second=0, microsecond=0)


def api_post(endpoint, data=None, timeout=15):
    """带重试的POST请求"""
    url = f"{BASE_URL}{endpoint}"
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(url, headers=HEADERS, data=data, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            print(f"[WARN] 请求失败 (第{attempt+1}次) {endpoint}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                print(f"[ERROR] 请求彻底失败 {endpoint}")
                return None
        except json.JSONDecodeError:
            print(f"[ERROR] JSON解析失败 {endpoint}")
            return None
    return None


def strip_html(html_text):
    """去除HTML标签，提取纯文本"""
    if not html_text:
        return ""
    text = re.sub(r'<[^>]+>', '', html_text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_recruit_list(page=1, position_type=1):
    """获取招聘/实习列表"""
    data = {
        "pageNo": page,
        "pageSize": PAGE_SIZE,
        "positionType": position_type,
    }
    return api_post("f/recruitmentinfo/ajax_frontRecruitinfo", data)


def get_recruit_detail(recruitment_id):
    """获取招聘详情"""
    data = {
        "recruitmentId": recruitment_id,
    }
    return api_post("f/recruitmentinfo/ajax_show", data)


def extract_ids_from_list(list_result):
    """从列表结果中提取招聘ID和标题"""
    if not list_result or list_result.get("state") != 1:
        return []

    obj = list_result.get("object", {})
    items = obj.get("list", [])
    results = []

    for item in items:
        rid = item.get("recruitmentId") or item.get("id") or item.get("recruitmentinfo", {}).get("id", "")
        title = item.get("recruitmentinfo", {}).get("title", "") or item.get("title", "")
        start_time = item.get("recruitmentinfo", {}).get("startTime", "") or item.get("startTime", "")
        results.append({
            "id": rid,
            "title": title,
            "startTime": start_time,
        })

    return results


def format_detail(detail_result):
    """格式化详情数据"""
    if not detail_result or detail_result.get("state") != 1:
        return {}

    obj = detail_result.get("object", {})
    info = obj.get("recruitmentinfo", {})

    title = info.get("title", "")
    corp_name = info.get("corporationName", "")
    content_html = info.get("content", "")
    content_text = strip_html(content_html)
    email = info.get("resumeReceiveEmail", "")
    start_time = info.get("startTime", "")
    position_type = info.get("positionType", 1)

    # 职位列表
    positions = []
    for pos in info.get("recruitmentPositionList", []):
        positions.append({
            "职位名称": pos.get("positionName", ""),
            "学历": pos.get("studentType", ""),
            "需求人数": pos.get("demandNumber", ""),
            "专业": pos.get("majorName", ""),
            "工作地点": pos.get("cityName", ""),
        })

    return {
        "标题": title,
        "公司/组织名称": corp_name,
        "发布日期": start_time[:10] if start_time else "",
        "简历投递邮箱": email,
        "招聘详情(纯文本)": content_text[:2000],
        "职位列表": positions,
    }


def main():
    now = datetime.now(CST)
    print("=" * 60)
    print("北京大学就业信息网 - 日常招聘爬虫")
    print(f"运行时间：{now.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
    print(f"筛选日期：{FILTER_DATE.strftime('%Y-%m-%d')} (北京时间) 及以后")
    print(f"数据类型：日常招聘信息 (positionType=1)")
    print("=" * 60)

    all_jobs = []

    for page in range(1, MAX_PAGES + 1):
        print(f"\n[INFO] 正在获取第 {page} 页...")
        list_result = get_recruit_list(page=page, position_type=1)

        if not list_result or list_result.get("state") != 1:
            print(f"[ERROR] 获取列表失败: {list_result}")
            break

        items = extract_ids_from_list(list_result)
        total = list_result.get("object", {}).get("total", "?")
        print(f"[INFO] 总计 {total} 条记录，当前页获取 {len(items)} 条")

        if not items:
            print("[INFO] 当前页无数据，停止")
            break

        # 检查是否还有今日数据
        earliest_start = None
        for item in items:
            st = item.get("startTime", "")
            if st:
                try:
                    dt = datetime.strptime(st[:10], "%Y-%m-%d").replace(tzinfo=CST)
                    if earliest_start is None or dt < earliest_start:
                        earliest_start = dt
                except ValueError:
                    pass

        if earliest_start and earliest_start < FILTER_DATE:
            print(f"[INFO] 已到达筛选日期之前的记录，停止分页")
            # 过滤掉筛选日期之前的
            filtered_items = []
            for item in items:
                st = item.get("startTime", "")
                if st:
                    try:
                        dt = datetime.strptime(st[:10], "%Y-%m-%d").replace(tzinfo=CST)
                        if dt >= FILTER_DATE:
                            filtered_items.append(item)
                    except ValueError:
                        pass
            items = filtered_items
            if not items:
                break

        for item in items:
            rid = item["id"]
            if not rid:
                print(f"  [SKIP] 无ID: {item.get('title', '?')}")
                continue

            print(f"  -> 获取详情: {item.get('title', '?')}")
            detail_result = get_recruit_detail(rid)
            detail = format_detail(detail_result)

            job_entry = {
                "id": rid,
                "列表标题": item.get("title", ""),
                "链接": f"https://scc.pku.edu.cn/f/recruitmentinfo/show?recruitmentId={rid}",
                **detail,
            }
            all_jobs.append(job_entry)
            time.sleep(1)  # 详情请求间隔

        time.sleep(2)  # 翻页间隔

    # 输出结果
    output = {
        "爬取时间": now.strftime("%Y-%m-%d %H:%M:%S"),
        "数据来源": "北京大学就业信息网 - 日常招聘信息",
        "总计数量": len(all_jobs),
        "职位列表": all_jobs,
    }

    output_file = "/root/.openclaw/workspace/output/pku_daily/pku_recruit_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"完成！共获取 {len(all_jobs)} 条日常招聘信息")
    print(f"结果已保存到: {output_file}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
