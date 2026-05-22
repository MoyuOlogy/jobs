#!/usr/bin/env python3
"""
复旦大学就业信息网 - 招聘会/宣讲会爬虫
"""
import requests
import json
import time
from datetime import datetime, timezone, timedelta

BASE_URL = "https://career.fudan.edu.cn/mobile.php"
HEADERS = {"Content-Type": "application/x-www-form-urlencoded", "auth": "Baisc MTAyNDY6MTAyNDY="}
tz = timezone(timedelta(hours=8))
FILTER_DATE = datetime.now(tz=tz).strftime("%Y-%m-%d")
MAX_RETRIES = 3
RETRY_DELAY = 2


def api_post(endpoint, data, timeout=30):
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


print("=" * 60)
print(f"复旦就业网 - 招聘会/宣讲会 | 举办日期 >= {FILTER_DATE}")
print("=" * 60)

# 获取宣讲会列表
data = {"login_user_id": "1", "isunion": "2", "page": "1", "size": "20", "isorder": "1", "isair": "3"}
result = api_post("/preach/getlist", data)

if not result:
    print("[ERROR] 无法获取宣讲会列表，退出")
    exit(1)

items = result.get("data", {}).get("list", [])
print(f"API 返回 {len(items)} 条记录")

all_records = []
for i, item in enumerate(items):
    hold_date = item.get("hold_date", "")
    if hold_date < FILTER_DATE:
        continue

    addtime = item.get("addtime", 0)
    publish_dt = datetime.fromtimestamp(addtime, tz=tz)

    all_records.append({
        "title": item.get("title", ""),
        "company": item.get("com_id_name", ""),
        "hold_date": hold_date,
        "hold_time": f"{item.get('hold_starttime','')}-{item.get('hold_endtime','')}",
        "location": item.get("tmp_field_name", "") or item.get("address", ""),
        "publish_date": publish_dt.strftime("%Y-%m-%d %H:%M"),
        "url": f"https://career.fudan.edu.cn/Zhaopin/zuijin.html?id={item.get('id','')}&hold_date={hold_date}",
    })

    # 请求间隔，避免被限流
    if i < len(items) - 1:
        time.sleep(1)  # 请求间隔

print(f"\n共获取 {len(all_records)} 条记录\n")

for i, r in enumerate(all_records, 1):
    print(f"--- {i} ---")
    print(f"  标题: {r['title']}")
    print(f"  公司: {r['company']}")
    print(f"  举办: {r['hold_date']} {r['hold_time']}")
    print(f"  地点: {r['location']}")
    print(f"  发布: {r['publish_date']}")
    print(f"  链接: {r['url']}")
    print()

output_file = "/root/.openclaw/workspace/output/fudan_daily/fudan_talk_results.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_records, f, ensure_ascii=False, indent=2)
print(f"结果已保存到: {output_file}")
