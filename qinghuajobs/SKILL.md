---
name: qinghuajobs
description: 清华就业信息网招聘信息获取技能 — 爬取清华大学学生职业发展指导中心招聘信息，支持列表获取、按日期筛选、详情页全文爬取、Excel 输出
---

# 清华就业信息网 — 招聘信息获取技能

通过清华大学就业信息网 API 获取最新招聘信息，支持列表查询、日期筛选、详情页爬取、Excel 导出。

## 文件结构

```
workspace/skills/qinghuajobs/
├── SKILL.md            ← 本文档
├── qinghuajobs.py      ← 交互式Python脚本（支持Excel导出）
├── scripts/
│   └── qinghua_recruit.py  ← 每日定时同步脚本（JSON输出）
├── config.json         ← 配置（默认翻页数等）
└── _meta.json          ← 技能元信息
```

## 每日定时同步 (qinghua_recruit.py)

`scripts/qinghua_recruit.py` 是专为 cron job 设计的每日同步脚本，与复旦/北大保持一致：
- 自动筛选当日数据（前两页）
- 抓取详情页全文
- 输出 JSON 到 `output/qinghua_daily/qinghua_results.json`
- 每天 22:40 (北京时间) 由 cron job 触发，按 jobs 技能规范写入飞书多维表格

```bash
python3 scripts/qinghua_recruit.py
```

## API 发现

通过分析页面 JavaScript 找到的列表 API：

| 项目 | 内容 |
|------|------|
| **URL** | `POST https://career.cic.tsinghua.edu.cn/xsglxt/b/jyxt/anony/xxfbForWx` |
| **Content-Type** | `application/x-www-form-urlencoded` |
| **参数** | `type=ZPXX`, `pgno=页码` |
| **返回** | JSON 数组（每页 20 条） |

每个字段：

| 字段 | 说明 |
|------|------|
| `zwmc` | 职位名称 |
| `dwmc` | 单位名称 |
| `gzdqmc` | 工作地点 |
| `dwxz` | 单位性质（国企/民企/高校等） |
| `fbsj` | 发布日期 |
| `sfzd` | 是否置顶 |
| `id` | 详情 ID（用于拼详情链接） |

**详情页**无单独 API，是服务端渲染的 HTML，需要爬取解析。

**详情链接格式：**
```
https://career.cic.tsinghua.edu.cn/xsglxt/f/jyxt/anony/showZwxxForWx?zpxxid={id}&type=ZPXX
```

## 使用方法

```bash
# 查看前 3 页招聘信息
python3 qinghuajobs.py

# 指定翻页数
python3 qinghuajobs.py --pages 5

# 筛选指定日期
python3 qinghuajobs.py --date 2026-05-15

# 筛选当天
python3 qinghuajobs.py --today

# 带详情爬取（每个职位去详情页抓取全文）
python3 qinghuajobs.py --date 2026-05-15 --detail

# 保存 Excel
python3 qinghuajobs.py --date 2026-05-15 --detail --save
```

## Excel 输出

保存到 `workspace/output/tsinghua/` 目录。

**基础模式（不带 `--detail`）：**

| 列名 | 说明 |
|------|------|
| 序号 | 1..N |
| 职位名称 | 招聘岗位 |
| 单位名称 | 招聘单位 |
| 工作地点 | 城市/区 |
| 单位性质 | 国企/民企/外资/高校等 |
| 发布日期 | 如 2026-05-15 |
| 是否置顶 | ⭐ 标记 |
| 详情链接 | 可点击打开 |

**详情模式（带 `--detail`）：**

| 列名 | 说明 |
|------|------|
| 序号 | 1..N |
| 职位名称 | 招聘岗位 |
| 单位名称 | 招聘单位 |
| 工作地点 | 城市/区 |
| 单位性质 | 国企/民企/外资/高校等 |
| 发布日期 | 如 2026-05-15 |
| 学历要求 | 从详情页提取 |
| 专业要求 | 从详情页提取 |
| 联系邮箱 | 从详情页提取 |
| 职位摘要 | 详情页正文前 2000 字 |
| 详情链接 | 可点击打开 |

## 特点

- **无需认证** — 清华就业信息网是公开访问的，不需要登录
- **速度较快** — 服务器在国内，网络延迟低，无反爬
- **按日期筛选** — 灵活查看指定日期的招聘信息
- **翻页支持** — 默认 3 页（60 条），可通过 `--pages` 调整
