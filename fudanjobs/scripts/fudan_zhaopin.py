#!/usr/bin/env python3
"""
复旦大学就业信息网 - 招聘信息爬虫
==========================================
功能：获取校招公告/招聘信息列表及详情，筛选指定日期及以后发布的信息
API:
  - 列表: POST /mobile.php/enrollment/getlist
  - 详情: POST /mobile.php/enrollment/detail
认证: auth: Baisc MTAyNDY6MTAyNDY=

招聘类型 (type参数):
  - type=1: 企招 (企业招聘公告)
  - type=2: 公招 (公务员/事业单位)
  - type=3: 事招 (事业单位招聘)
"""

import requests
import json
import time
from datetime import datetime, timezone, timedelta

# ==================== 配置 ====================
BASE_URL = "https://career.fudan.edu.cn/mobile.php"
AUTH_HEADER = "Baisc MTAyNDY6MTAyNDY="
HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "auth": AUTH_HEADER,
}
# 筛选日期：2026-04-28 00:00:00 CST (北京时间)
FILTER_DATE = datetime.now(tz=timezone(timedelta(hours=8))).replace(hour=0, minute=0, second=0, microsecond=0)
FILTER_TIMESTAMP = int(FILTER_DATE.timestamp())
PAGE_SIZE = 20  # 每页条数

# 招聘类型映射
ENROLLMENT_TYPES = {
    1: "企招",
    2: "公招",
    3: "事招",
}


MAX_RETRIES = 3
RETRY_DELAY = 2


def api_post(endpoint, data, timeout=15):
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


def get_enrollment_list(enrollment_type=1, page=1, size=PAGE_SIZE):
    """获取招聘信息列表"""
    data = {
        "type": enrollment_type,
        "page": page,
        "size": size,
        "login_user_id": 1,
    }
    return api_post("/enrollment/getlist", data)


def get_enrollment_detail(enrollment_id):
    """获取招聘信息详情"""
    data = {
        "id": enrollment_id,
        "login_user_id": 1,
    }
    return api_post("/enrollment/detail", data)


def format_enrollment_summary(item):
    """从列表项提取摘要信息"""
    addtime_ts = item.get("addtime", 0)
    addtime_str = datetime.fromtimestamp(
        addtime_ts, tz=timezone(timedelta(hours=8))
    ).strftime("%Y-%m-%d %H:%M") if addtime_ts else "未知"

    enrollment_type = item.get("enrollment_type", 0)
    type_name = ENROLLMENT_TYPES.get(enrollment_type, "未知")

    return {
        "list_id": item.get("id"),
        "enrollment_id": item.get("enrollment_id"),
        "标题": item.get("title", ""),
        "类型": type_name,
        "发布机构": item.get("create_name", ""),
        "关联公司": item.get("com_id_name", ""),
        "发布时间": addtime_str,
        "浏览量": item.get("viewcount", 0),
        "是否置顶": "是" if item.get("istop") == 1 else "否",
    }


def format_enrollment_detail(detail_data):
    """格式化招聘信息详情"""
    if not detail_data or "data" not in detail_data:
        return {}

    d = detail_data["data"]

    addtime_ts = d.get("addtime", 0)
    addtime_str = datetime.fromtimestamp(
        addtime_ts, tz=timezone(timedelta(hours=8))
    ).strftime("%Y-%m-%d %H:%M") if addtime_ts else "未知"

    enrollment_type = d.get("enrollment_type", 0)
    type_name = ENROLLMENT_TYPES.get(enrollment_type, "未知")

    # 提取附件信息
    attachments = []
    for i in range(1, 6):
        attach = d.get(f"attach{i}")
        attach_src = d.get(f"attach{i}_src")
        if attach and attach_src:
            attachments.append({
                "文件名": attach,
                "链接": attach_src.get("linkpath", "") if isinstance(attach_src, dict) else str(attach_src),
            })

    return {
        "标题": d.get("title", ""),
        "类型": type_name,
        "发布机构": d.get("create_name", ""),
        "关联公司": d.get("com_id_name", ""),
        "学校名称": d.get("school_id_name", ""),
        "内容简介": d.get("remarks", ""),
        "外部链接": d.get("httpurl", ""),
        "附件列表": attachments,
        "就业提醒": d.get("schoolwarn", ""),
        "发布时间": addtime_str,
        "浏览量": d.get("viewcount", 0),
        "是否置顶": "是" if d.get("istop") == 1 else "否",
    }


def crawl_by_type(enrollment_type, type_name):
    """按类型爬取招聘信息"""
    print(f"\n{'─' * 40}")
    print(f"开始爬取: {type_name} (type={enrollment_type})")
    print(f"{'─' * 40}")

    all_items = []
    page = 1

    while True:
        print(f"\n[INFO] 正在获取第 {page} 页...")
        result = get_enrollment_list(enrollment_type=enrollment_type, page=page)

        if not result or result.get("code") != 0:
            print(f"[ERROR] 获取列表失败: {result}")
            break

        data = result["data"]
        item_list = data.get("list", [])
        total_count = data.get("count", 0)
        all_pages = data.get("allpage", 0)

        if page == 1:
            print(f"[INFO] {type_name} 总计 {total_count} 条记录，共 {all_pages} 页")

        if not item_list:
            print("[INFO] 当前页无数据，结束分页")
            break

        # 检查是否还有数据在筛选日期之后
        earliest_ts = min(item.get("addtime", 0) for item in item_list)
        if earliest_ts < FILTER_TIMESTAMP:
            print(f"[INFO] 已到达筛选日期之前的记录，停止分页")
            item_list = [item for item in item_list if item.get("addtime", 0) >= FILTER_TIMESTAMP]
            if not item_list:
                break

        for item in item_list:
            addtime_ts = item.get("addtime", 0)
            if addtime_ts < FILTER_TIMESTAMP:
                continue

            summary = format_enrollment_summary(item)
            print(f"  -> 获取详情: {summary['标题']}")

            # 获取详情
            detail_result = get_enrollment_detail(item["id"])
            detail = format_enrollment_detail(detail_result)

            # 合并摘要和详情
            entry = {**summary, **detail}
            all_items.append(entry)

            # 避免请求过快
            time.sleep(1)  # 详情请求间隔

        # 只取前两页（每天更新不超过两页）
        if page >= 2:
            print("[INFO] 已取前两页，停止翻页")
            break

        page += 1
        time.sleep(2)  # 翻页间隔

    return all_items


def main():
    print("=" * 60)
    print("复旦大学就业信息网 - 招聘信息爬虫")
    print(f"筛选日期：{FILTER_DATE.strftime('%Y-%m-%d %H:%M')} (北京时间) 及以后")
    print("=" * 60)

    all_results = {}

    # 爬取所有招聘类型
    for type_id, type_name in ENROLLMENT_TYPES.items():
        items = crawl_by_type(type_id, type_name)
        all_results[type_name] = items
        time.sleep(3)  # 不同类型之间间隔

    # 汇总
    total_count = sum(len(v) for v in all_results.values())

    output = {
        "爬取时间": datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"),
        "筛选条件": f"{FILTER_DATE.strftime('%Y-%m-%d')} 及以后发布的招聘信息",
        "总计数量": total_count,
        "分类统计": {k: len(v) for k, v in all_results.items()},
        "招聘信息": all_results,
    }

    output_file = "/root/.openclaw/workspace/output/fudan_daily/fudan_zhaopin_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"完成！共获取 {total_count} 条招聘信息")
    for type_name, items in all_results.items():
        print(f"  - {type_name}: {len(items)} 条")
    print(f"结果已保存到: {output_file}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
