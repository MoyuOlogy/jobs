#!/usr/bin/env python3
"""
复旦大学就业信息网 - 全职职位爬虫
==========================================
功能：获取全职职位列表及详情，筛选指定日期及以后发布的职位
API:
  - 列表: POST /mobile.php/job/getlist (jobtype=1)
  - 详情: POST /mobile.php/job/detail
认证: auth: Baisc MTAyNDY6MTAyNDY=
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


def get_fulltime_list(page=1, size=PAGE_SIZE):
    """获取全职职位列表"""
    data = {
        "jobtype": 1,        # 1=全职
        "isunion": 2,
        "page": page,
        "size": size,
        "login_user_id": 1,
    }
    return api_post("/job/getlist", data)


def get_job_detail(job_id):
    """获取职位详情"""
    data = {
        "id": job_id,
        "login_user_id": 1,
    }
    return api_post("/job/detail", data)


def format_job_summary(item):
    """从列表项提取摘要信息"""
    addtime_ts = item.get("addtime", 0)
    addtime_str = datetime.fromtimestamp(
        addtime_ts, tz=timezone(timedelta(hours=8))
    ).strftime("%Y-%m-%d %H:%M") if addtime_ts else "未知"

    salary_floor = item.get("salary_floor", 0)
    salary_ceil = item.get("salay_ceil", 0)
    if salary_floor == 0 and salary_ceil == 0:
        salary = "面议"
    elif salary_floor > 0 and salary_ceil > 0:
        salary = f"{salary_floor}-{salary_ceil}"
    else:
        salary = str(salary_floor or salary_ceil)

    return {
        "list_id": item.get("id"),
        "job_id": item.get("job_id"),
        "职位名称": item.get("work_name", ""),
        "公司名称": item.get("com_id_name", ""),
        "工作地点": f"{item.get('province_id_name', '')}{item.get('city_id_name', '')}",
        "学历要求": item.get("xueli_id_name", ""),
        "招聘人数": item.get("person_count", ""),
        "薪资范围": salary,
        "发布时间": addtime_str,
        "职位类别": item.get("dalei_id_name", ""),
        "浏览量": item.get("viewcount", 0),
    }


def format_job_detail(detail_data):
    """格式化职位详情"""
    if not detail_data or "data" not in detail_data:
        return {}

    d = detail_data["data"]
    job_info = d.get("jobInfo", {})

    addtime_ts = job_info.get("addtime", 0)
    addtime_str = datetime.fromtimestamp(
        addtime_ts, tz=timezone(timedelta(hours=8))
    ).strftime("%Y-%m-%d %H:%M") if addtime_ts else "未知"

    salary_floor = job_info.get("salary_floor", 0)
    salary_ceil = job_info.get("salay_ceil", 0)
    if salary_floor == 0 and salary_ceil == 0:
        salary = "面议"
    elif salary_floor > 0 and salary_ceil > 0:
        salary = f"{salary_floor}-{salary_ceil}"
    else:
        salary = str(salary_floor or salary_ceil)

    return {
        "职位名称": job_info.get("work_name", ""),
        "公司名称": job_info.get("com_id_name", ""),
        "工作地点": f"{job_info.get('province_id_name', '')}{job_info.get('city_id_name', '')}{job_info.get('address', '')}",
        "详细地址": job_info.get("address", ""),
        "学历要求": job_info.get("xueli_id_name", ""),
        "招聘人数": job_info.get("person_count", ""),
        "薪资范围": salary,
        "职位类别": job_info.get("dalei_id_name", ""),
        "联系人": job_info.get("contacts", ""),
        "联系电话": job_info.get("tel", ""),
        "手机号": job_info.get("phone", ""),
        "投递邮箱": job_info.get("deliver_email", ""),
        "职位描述(HTML)": job_info.get("remarks", ""),
        "浏览量": job_info.get("viewcount", 0),
        "发布时间": addtime_str,
    }


def main():
    print("=" * 60)
    print("复旦大学就业信息网 - 全职职位爬虫")
    print(f"筛选日期：{FILTER_DATE.strftime('%Y-%m-%d %H:%M')} (北京时间) 及以后")
    print("=" * 60)

    all_jobs = []
    page = 1
    total_count = None

    while True:
        print(f"\n[INFO] 正在获取第 {page} 页...")
        result = get_fulltime_list(page=page)

        if not result or result.get("code") != 0:
            print(f"[ERROR] 获取列表失败: {result}")
            break

        data = result["data"]
        job_list = data.get("list", [])
        if total_count is None:
            total_count = data.get("count", 0)
            all_pages = data.get("allpage", 0)
            print(f"[INFO] 总计 {total_count} 条记录，共 {all_pages} 页")

        if not job_list:
            print("[INFO] 当前页无数据，结束分页")
            break

        # 检查是否还有数据在筛选日期之后
        earliest_ts = min(item.get("addtime", 0) for item in job_list)
        if earliest_ts < FILTER_TIMESTAMP:
            print(f"[INFO] 已到达筛选日期之前的记录，停止分页")
            # 过滤掉筛选日期之前的
            job_list = [item for item in job_list if item.get("addtime", 0) >= FILTER_TIMESTAMP]
            if not job_list:
                break

        for item in job_list:
            addtime_ts = item.get("addtime", 0)
            if addtime_ts < FILTER_TIMESTAMP:
                continue

            summary = format_job_summary(item)
            print(f"  -> 获取详情: {summary['职位名称']} ({summary['公司名称']})")

            # 获取详情
            detail_result = get_job_detail(item["id"])
            detail = format_job_detail(detail_result)

            # 合并摘要和详情
            job_entry = {**summary, **detail}
            all_jobs.append(job_entry)

            # 避免请求过快
            time.sleep(1)  # 详情请求间隔

        # 只取前两页（每天更新不超过两页）
        if page >= 2:
            print("[INFO] 已取前两页，停止翻页")
            break

        page += 1
        time.sleep(2)  # 翻页间隔

    # 输出结果
    output = {
        "爬取时间": datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"),
        "筛选条件": f"{FILTER_DATE.strftime('%Y-%m-%d')} 及以后发布的全职职位",
        "总计数量": len(all_jobs),
        "职位列表": all_jobs,
    }

    output_file = "/root/.openclaw/workspace/output/fudan_daily/fudan_fulltime_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"完成！共获取 {len(all_jobs)} 条全职职位")
    print(f"结果已保存到: {output_file}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
