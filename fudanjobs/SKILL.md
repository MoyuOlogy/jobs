---
name: fudanjobs
description: fdu就业信息网爬虫技能。每日抓取fdu就业指导与生涯发展处网站的最新招聘信息，包括全职职位、实习职位、招聘信息、招聘会/宣讲会。当用户需要获取fdu最新招聘信息、宣讲会安排、校招职位时使用。
---

# fdu就业信息网爬虫

每日抓取fdu就业信息网（career.fudan.edu.cn）的最新招聘数据。

## 使用方式

运行脚本获取**当日最新**信息，结果自动保存到 `output/fudan_daily/` 目录：

```bash
python3 scripts/fudan_talk.py       # 招聘会/宣讲会（推荐每日运行）
python3 scripts/fudan_fulltime.py   # 全职职位
python3 scripts/fudan_intern.py     # 实习职位
python3 scripts/fudan_zhaopin.py    # 招聘信息（校招公告）
```

## 脚本说明

| 脚本 | API 端点 | 数据类型 |
|------|----------|----------|
| `fudan_fulltime.py` | `/recruit/fulltime/getlist` | 全职职位列表 |
| `fudan_intern.py` | `/recruit/intern/getlist` | 实习职位列表 |
| `fudan_zhaopin.py` | `/companyjob/getlist` | 校招公告/招聘信息 |
| `fudan_talk.py` | `/preach/getlist` + `/preach/detail` | 招聘会/宣讲会 |

## 输出路径

所有脚本统一输出到：`/root/.openclaw/workspace/output/fudan_daily/`

```
output/fudan_daily/
├── fudan_fulltime_results.json
├── fudan_intern_results.json
├── fudan_zhaopin_results.json
└── fudan_talk_results.json
```

## 链接格式

- 全职/实习职位详情页：`https://career.fudan.edu.cn/Zhaopin/zhiweiDetail.html?jobtype={1|2}&id={uuid}`
- 校招公告详情页：`https://career.fudan.edu.cn/Zhaopin/xiaozhao.html?id={uuid}&type=1`
- 宣讲会详情页：`https://career.fudan.edu.cn/Zhaopin/zuijin.html?id={uuid}&hold_date={YYYY-MM-DD}`

## 配置

- Base URL: `https://career.fudan.edu.cn/mobile.php`
- 认证 Header: `auth: Baisc MTAyNDY6MTAyNDY=`
- Content-Type: `application/x-www-form-urlencoded`
- 筛选日期：自动取当天日期（北京时间）
