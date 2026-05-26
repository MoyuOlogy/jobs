---
name: zjujobs
description: zju就业服务平台招聘信息获取技能 — 爬取zju就业信息网招聘岗位信息，支持列表获取、按日期筛选、JSON/Excel 输出
---

# zju就业服务平台 — 招聘信息获取技能

通过zju就业信息网 API 获取最新招聘信息，支持每日定时同步。

## 文件结构

```
workspace/skills/zjujobs/
├── SKILL.md            ← 本文档
├── scripts/
│   └── zju_recruit.py  ← 每日定时同步脚本（JSON输出）
└── _meta.json          ← 技能元信息
```

## 每日定时同步 (zju_recruit.py)

`scripts/zju_recruit.py` 是专为 cron job 设计的每日同步脚本：
- 自动筛选当日数据（前3页）
- 输出 JSON 到 `output/zju_daily/zju_results.json`
- 每天 23:00 (北京时间) 由 cron job 触发，按 jobs 技能规范写入飞书多维表格

```bash
python3 scripts/zju_recruit.py
```

## API

| 项目 | 内容 |
|------|------|
| **列表 API** | `POST /jyxt/wzsy/getZpztzwList.zf` |
| **Content-Type** | `application/json` |
| **参数** | `{"current": 页码, "size": 15, "xxdm": "00000", "lmid": "2B2921EE10ED2DE8E0653A68DD0E9B18", ...}` |
| **返回** | JSON，records 数组 |
| **详情页** | `GET /recruitment/jobDetails?zpxxbh={zpxxbh}&lmid={lmid}` |

## 输出字段

| 字段 | 说明 |
|------|------|
| ztid | 职位主题ID |
| zpxxbh | 招聘信息编号（用于拼详情链接） |
| 标题 | 职位名称 |
| 招聘主题 | 招聘主题 |
| 公司/组织名称 | 招聘单位 |
| 发布日期 | 如 2026-05-21 17:18:54 |
| 学历要求 | 本科/硕士/博士 |
| 工作地点 | 省市 |
| 招聘人数 | 计划招聘人数 |
| 单位性质 | 国有企业/其他企业等 |
| 行业 | 行业分类 |
| 内容标签 | 信息软件、生物医药等标签 |
| 链接 | 职位详情页URL |
