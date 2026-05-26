---
name: pkujobs
description: pku就业信息网爬虫技能。每日抓取pku学生就业指导服务中心网站的最新招聘信息，包括日常招聘和日常实习。当用户需要获取pku最新招聘信息、校招职位、实习机会时使用。
---

# pku就业信息网爬虫

每日抓取pku就业信息网（scc.pku.edu.cn）的最新招聘数据。

## 使用方式

运行脚本获取信息，结果自动保存到 `output/pku_daily/` 目录：

```bash
python3 scripts/pku_recruit.py   # 日常招聘信息（前两页）
python3 scripts/pku_intern.py    # 日常实习信息（前两页）
```

## 脚本说明

| 脚本 | API 端点 | 数据类型 | positionType |
|------|----------|----------|-------------|
| `pku_recruit.py` | `/f/recruitmentinfo/ajax_frontRecruitinfo` | 日常招聘信息 | 1 |
| `pku_intern.py` | `/f/recruitmentinfo/ajax_frontRecruitinfo` | 日常实习信息 | 2 |

两个脚本均会自动获取每条招聘的**详细信息**（公司简介、招聘简章、职位列表等）。

## 输出路径

所有脚本统一输出到：`/root/.openclaw/workspace/output/pku_daily/`

```
output/pku_daily/
├── pku_recruit_results.json   # 日常招聘
└── pku_intern_results.json    # 日常实习
```

## 链接格式

- 招聘详情页：`https://scc.pku.edu.cn/f/recruitmentinfo/show?recruitmentId={id}`

## API 详情

### 列表接口

```
POST https://scc.pku.edu.cn/f/recruitmentinfo/ajax_frontRecruitinfo
Headers: token: 111
Content-Type: application/x-www-form-urlencoded

参数：
  pageNo: 页码（从1开始）
  pageSize: 每页条数（默认15）
  positionType: 1=日常招聘, 2=日常实习
```

### 详情接口

```
POST https://scc.pku.edu.cn/f/recruitmentinfo/ajax_show
Headers: token: 111
Content-Type: application/x-www-form-urlencoded

参数：
  recruitmentId: 招聘信息ID
```

## 配置

- Base URL: `https://scc.pku.edu.cn/`
- Token: `111`（公开固定值）
- 每页条数：15
- 默认抓取：前两页（共30条）

## 与 jobs 技能配合

脚本输出的 JSON 可直接用于 jobs 技能写入飞书多维表格。关键字段映射：

| JSON 字段 | 飞书字段 |
|-----------|---------|
| 标题 | 标题 |
| 公司/组织名称 | 公司/组织名称 |
| 招聘详情(纯文本) | 信息描述 |
| 链接 | 链接 |
| 简历投递邮箱 | 联系方式 |

## 注意事项

- 北大就业网为 JS 动态渲染页面，无法通过 web_fetch 直接抓取，必须使用 API
- Token 为公开固定值 `111`，无需登录
- 列表接口返回的字段较少，需逐条调用详情接口获取完整信息
- 建议每次运行间隔 1-2 秒，避免请求过快
