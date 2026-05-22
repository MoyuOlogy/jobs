---
name: sjtujobs
description: 上海交通大学就业信息网爬虫技能。每日抓取上海交通大学学生就业服务和职业发展中心网站的最新招聘信息。当用户需要获取上海交通大学最新招聘信息、校招职位时使用。
---

# 上海交通大学就业信息网爬虫

每日抓取上海交通大学就业信息网（job.sjtu.edu.cn）的最新招聘数据。

## 使用方式

运行脚本获取当日最新信息，结果自动保存到 `output/sjtu_daily/` 目录：

```bash
python3 scripts/sjtu_recruit.py   # 招聘信息（前3页）
```

## 脚本说明

| 脚本 | 说明 |
|------|------|
| `sjtu_recruit.py` | 招聘信息每日同步 |

## 输出路径

```
output/sjtu_daily/
└── sjtu_results.json
```

## 链接格式

- 职位详情页：`https://www.job.sjtu.edu.cn/career/zpxx/view/zpxx/{zpxxid}`

## API 详情

### 列表接口

```
POST https://www.job.sjtu.edu.cn/career/zpxx/search/zpxx/{pageNum}/{pageSize}
Content-Type: application/x-www-form-urlencoded

参数（均可选，通过 POST body 传递）：
  dwmc: 单位名称（搜索）
  ksySzx: 开始时间筛选
  dwbq: 单位标签
  （不传参数则返回全部最新列表）
```

返回的分页数据：
- `code`: 200 表示成功
- `data.list`: 招聘列表数组
- `data.total`: 总记录数
- `data.pageNum` / `data.pageSize`: 分页信息

每条记录关键字段：

| 字段 | 说明 |
|------|------|
| zpxxid | 招聘信息唯一ID（用于拼详情链接） |
| zpzt | 职位主题/标题 |
| dwmc | 单位名称 |
| fbrq | 发布日期 |
| zpjzrq | 截止日期 |
| hyyjmc | 行业 |
| xzyjmc | 单位性质 |
| szssmc / szxmc | 工作地点（省/区县） |
| jltdyx | 简历投递邮箱 |
| zpxxwz | 网申/校招网址 |
| dwjs | 单位介绍 |
| xqrsmc | 需求人数 |
| xqxlmc | 学历要求 |
| xqzymc | 专业要求 |
| rsgmmc | 公司规模 |

### 详情接口

```
POST https://www.job.sjtu.edu.cn/career/zpxx/data/zpxx/{zpxxid}
Content-Type: application/x-www-form-urlencoded
```

返回字段与列表接口基本相同，额外包含：
- `zpxxEditor`: 完整职位描述（HTML格式，含岗位职责、要求等）

## 配置

- Base URL: `https://www.job.sjtu.edu.cn/career/`
- 无需认证，公开访问
- 默认每页 10 条（未登录限制，其他页数需登录）
- 默认抓取前 3 页

## 与 jobs 技能配合

脚本输出的 JSON 可直接用于 jobs 技能写入飞书多维表格。关键字段映射：

| JSON 字段 | 飞书字段 |
|-----------|---------|
| 标题 | 标题 |
| 公司/组织名称 | 公司/组织名称 |
| 招聘详情(纯文本) | 信息描述 |
| 链接 | 链接 |
| 简历投递邮箱 | 联系方式 |

## 特点

- **无需认证** — 上海交通大学就业信息网公开访问
- **API 直达** — 直接调用后端 REST API，无需解析 HTML
- **详情接口** — 有独立的数据 API 返回全量结构化数据
- **数据丰富** — 包含单位介绍、职位描述、网申链接、联系方式等