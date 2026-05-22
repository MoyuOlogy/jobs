#!/usr/bin/env python3
"""
浙江大学就业服务平台 - 招聘信息每日同步爬虫
==========================================
功能：获取招聘岗位信息列表，筛选当日数据，输出JSON
API:
  - 列表: POST /jyxt/wzsy/getZpztzwList.zf
详情页链接: GET /recruitment/jobDetails?zpxxbh=xxx&lmid=xxx
无需认证，公开访问
"""

import requests
import json
import time
from datetime import datetime, timezone, timedelta

# ==================== 配置 ====================
BASE_URL = "https://www.career.zju.edu.cn"
LIST_API = f"{BASE_URL}/jyxt/wzsy/getZpztzwList.zf"
DETAIL_PAGE = f"{BASE_URL}/recruitment/jobDetails"

CST = timezone(timedelta(hours=8))
FILTER_DATE = datetime.now(CST).replace(hour=0, minute=0, second=0, microsecond=0)
FILTER_DATE_STR = FILTER_DATE.strftime("%Y-%m-%d")

MAX_PAGES = 3              # 前3页
MAX_RETRIES = 3
RETRY_DELAY = 2

OUTPUT_DIR = "/root/.openclaw/workspace/output/zju_daily"
OUTPUT_FILE = f"{OUTPUT_DIR}/zju_results.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
}

# 默认查询参数
DEFAULT_BODY = {
    "current": 1,
    "size": 15,
    "xxdm": "00000",
    "lmid": "2B2921EE10ED2DE8E0653A68DD0E9B18",
    "keyword": "",
    "byzd4": "",
    "dwxzdm": "",
    "zpdxdm": "",
    "zpxldm": "",
    "nrbq": "",
}


def api_post(data, timeout=15):
    """带重试的POST请求"""
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(LIST_API, headers=HEADERS, json=data, timeout=timeout)
            resp.raise_for_status()
            result = resp.json()
            if result.get("code") == 0:
                return result.get("result", {})
            else:
                print(f"[ERROR] API返回错误: {result.get('message', 'unknown')}")
                return None
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


def get_detail_url(zpxxbh, lmid="2B2921EE10ED2DE8E0653A68DD0E9B18"):
    """生成职位详情页链接"""
    return f"{DETAIL_PAGE}?zpxxbh={zpxxbh}&lmid={lmid}"


def main():
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("浙江大学就业服务平台 - 每日同步爬虫")
    print(f"筛选日期：{FILTER_DATE_STR} (北京时间)")
    print("=" * 60)

    all_jobs = []
    seen_ids = set()

    for page in range(1, MAX_PAGES + 1):
        print(f"\n[INFO] 正在获取第 {page} 页...")

        body = {**DEFAULT_BODY, "current": page}
        result = api_post(body)

        if not result:
            print(f"[ERROR] 获取第{page}页失败")
            break

        records = result.get("records", [])
        total = result.get("total", 0)
        print(f"[INFO] 总记录 {total} 条，当前页 {len(records)} 条")

        matched = 0
        for item in records:
            fbsj = item.get("fbsj", "")
            if not fbsj or not fbsj.startswith(FILTER_DATE_STR):
                continue

            zpxxbh = item.get("zpxxbh", "")
            ztid = item.get("ztid", "")
            # 用 zpxxbh 去重
            unique_id = zpxxbh or ztid
            if unique_id in seen_ids:
                continue
            seen_ids.add(unique_id)

            matched += 1
            title = item.get("zwmc", "")
            company = item.get("dwmc", "")
            detail_url = get_detail_url(zpxxbh)

            print(f"  [{matched}] {title[:50]} - {company[:30]}")

            all_jobs.append({
                "ztid": ztid,
                "zpxxbh": zpxxbh,
                "dwxxid": item.get("dwxxid", ""),
                "标题": title,
                "招聘主题": item.get("zpzt", ""),
                "公司/组织名称": company,
                "发布日期": fbsj,
                "学历要求": item.get("zpxlmc", ""),
                "工作地点": item.get("gzddmc", ""),
                "招聘人数": item.get("zprs", ""),
                "职位数量": item.get("zwsl", ""),
                "单位性质": item.get("dwxzmc", ""),
                "行业": item.get("dwhymc", ""),
                "单位所在地": item.get("dwszdmc", ""),
                "内容标签": item.get("nrbqmc", ""),
                "链接": detail_url,
            })

        print(f"[INFO] 第{page}页当日匹配: {matched} 条")

        # 如果整页当天数据匹配为0且非首页，可能已经翻过头了
        if matched == 0 and page > 1:
            print("[INFO] 当前页无当日数据，停止翻页")
            break

        time.sleep(1)  # 翻页间隔

    # 输出结果
    output = {
        "爬取时间": datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S"),
        "数据来源": "浙江大学就业服务平台 - 招聘岗位信息",
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