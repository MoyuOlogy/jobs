# 🎓 高校就业信息网爬虫技能集

> OpenClaw Agent Skills — 五大高校就业信息网自动抓取

[![GitHub](https://img.shields.io/badge/GitHub-MoyuOlogy%2Fjobs-blue)](https://github.com/MoyuOlogy/jobs)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)

支持 **多所国内知名高校** 就业信息网的招聘信息自动抓取，每日定时同步，输出结构化 JSON 并写入飞书多维表格。

---

## 📑 目录

- [项目背景](#项目背景)
- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [技能详解](#技能详解)
  - [高校A (fudanjobs)](#高校a-fudanjobs)
  - [高校B (pkujobs)](#高校b-pkujobs)
  - [高校C (qinghuajobs)](#高校c-qinghuajobs)
  - [高校D (zjujobs)](#高校d-zjujobs)
  - [高校E (sjtujobs)](#高校e-sjtujobs)
- [输出格式](#输出格式)
- [定时任务配置](#定时任务配置)
- [与飞书多维表格集成](#与飞书多维表格集成)
- [常见问题](#常见问题)
- [更新日志](#更新日志)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 项目背景

作为高校辅导员，需要及时获取各大高校就业信息网的最新招聘信息，以便向学生推送。传统方式需要逐个访问各校网站查看，效率低下且容易遗漏。

本项目通过直接调用各校就业信息网的 REST API，实现：

- ✅ **自动化抓取** — 每日定时运行，无需人工干预
- ✅ **结构化输出** — JSON 格式统一，便于后续处理
- ✅ **智能去重** — 与飞书多维表格集成，自动跳过已存在记录
- ✅ **敏感词过滤** — 自动处理政治敏感词，避免内容审查拦截

---

## 功能特性

| 特性 | 说明 |
|------|------|
| 🔍 **多所高校覆盖** | 支持多所知名高校 |
| 📅 **每日定时同步** | 建议每晚 22:00-23:20 分批运行 |
| 📊 **结构化 JSON** | 统一字段格式，便于集成 |
| 🔗 **飞书多维表格** | 自动写入生涯信息表 |
| 🛡️ **敏感词过滤** | 自动处理政治敏感词 |
| 🔁 **智能去重** | 避免重复写入相同记录 |

---

## 快速开始

### 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/MoyuOlogy/jobs/main/install.sh | bash
```

### 手动安装

```bash
git clone https://github.com/MoyuOlogy/jobs.git
cp -r jobs/* ~/.openclaw/workspace/skills/
```

### 运行测试

```bash
# 测试高校A
python3 ~/.openclaw/workspace/skills/fudanjobs/scripts/fudan_fulltime.py

# 测试高校B
python3 ~/.openclaw/workspace/skills/pkujobs/scripts/pku_recruit.py

# 测试高校C
python3 ~/.openclaw/workspace/skills/qinghuajobs/scripts/qinghua_recruit.py

# 测试高校D
python3 ~/.openclaw/workspace/skills/zjujobs/scripts/zju_recruit.py

# 测试高校E
python3 ~/.openclaw/workspace/skills/sjtujobs/scripts/sjtu_recruit.py
```

---

## 技能详解

### 高校A (fudanjobs)

**支持数据类型**:
- 全职职位 (`fudan_fulltime.py`)
- 实习职位 (`fudan_intern.py`)
- 招聘信息/校招公告 (`fudan_zhaopin.py`)
- 招聘会/宣讲会 (`fudan_talk.py`)

**API 特点**:
- 需要认证
- 返回 JSON 数组

**输出路径**: `output/fudan_daily/`

```bash
# 运行示例
python3 skills/fudanjobs/scripts/fudan_fulltime.py
python3 skills/fudanjobs/scripts/fudan_intern.py
python3 skills/fudanjobs/scripts/fudan_zhaopin.py
python3 skills/fudanjobs/scripts/fudan_talk.py
```

**输出文件**:
```
output/fudan_daily/
├── fudan_fulltime_results.json   # 全职职位
├── fudan_intern_results.json     # 实习职位
├── fudan_zhaopin_results.json    # 招聘信息
└── fudan_talk_results.json       # 宣讲会
```

---

### 高校B (pkujobs)

**支持数据类型**:
- 日常招聘 (`pku_recruit.py`)
- 日常实习 (`pku_intern.py`)

**API 特点**:
- 需要固定 token（公开）
- 需要调用详情接口获取完整信息
- 每页 15 条，建议抓取前两页

**输出路径**: `output/pku_daily/`

```bash
# 运行示例
python3 skills/pkujobs/scripts/pku_recruit.py   # 日常招聘
python3 skills/pkujobs/scripts/pku_intern.py    # 日常实习
```

**输出文件**:
```
output/pku_daily/
├── pku_recruit_results.json   # 日常招聘
└── pku_intern_results.json    # 日常实习
```

**特别注意**:
- 列表接口返回字段较少，需逐条调用详情接口
- 建议每次请求间隔 1-2 秒，避免请求过快

---

### 高校C (qinghuajobs)

**支持数据类型**:
- 招聘信息 (`qinghua_recruit.py`)

**API 特点**:
- 无需认证，公开访问
- 列表 API 使用 POST 方式
- 详情页需要解析

**输出路径**: `output/qinghua_daily/`

```bash
# 运行示例
python3 skills/qinghuajobs/scripts/qinghua_recruit.py
```

**输出文件**:
```
output/qinghua_daily/
└── qinghua_results.json
```

**交互式脚本**:
```bash
# 手动查询指定日期
python3 skills/qinghuajobs/qinghuajobs.py --date 2026-05-22 --detail --save

# 查看当天
python3 skills/qinghuajobs/qinghuajobs.py --today --detail
```

---

### 高校D (zjujobs)

**支持数据类型**:
- 招聘岗位 (`zju_recruit.py`)

**API 特点**:
- 无需认证
- 使用 JSON POST 方式
- 字段结构完整

**输出路径**: `output/zju_daily/`

```bash
# 运行示例
python3 skills/zjujobs/scripts/zju_recruit.py
```

**输出文件**:
```
output/zju_daily/
└── zju_results.json
```

**特色字段**:
- `单位性质` — 国有企业、其他企业、党政机关等
- `行业` — 行业分类
- `内容标签` — 信息软件、生物医药等标签

---

### 高校E (sjtujobs)

**支持数据类型**:
- 招聘信息 (`sjtu_recruit.py`)

**API 特点**:
- 无需认证
- **未登录用户有数据限制**
- 有独立的详情数据 API

**输出路径**: `output/sjtu_daily/`

```bash
# 运行示例
python3 skills/sjtujobs/scripts/sjtu_recruit.py
```

**输出文件**:
```
output/sjtu_daily/
└── sjtu_results.json
```

**交互式脚本**:
```bash
# 手动查询
python3 skills/sjtujobs/sjtujobs.py --today
```

**特别注意**:
- 未登录用户有数据限制
- 建议适当分页抓取

---

## 输出格式

所有脚本输出统一 JSON 格式：

```json
{
  "爬取时间": "2026-05-22 22:00:00",
  "数据来源": "XXX大学就业信息网",
  "筛选日期": "2026-05-22",
  "总计数量": 15,
  "职位列表": [
    {
      "标题": "XX公司2026春季校园招聘",
      "公司/组织名称": "XX有限公司",
      "发布日期": "2026-05-22",
      "工作地点": "北京",
      "学历要求": "本科及以上",
      "简历投递邮箱": "hr@example.com",
      "招聘详情(纯文本)": "岗位职责：...",
      "链接": "https://..."
    }
  ]
}
```

**关键字段说明**:

| 字段 | 说明 | 必需 |
|------|------|------|
| 标题 | 招聘标题 | ✅ |
| 公司/组织名称 | 招聘单位 | ✅ |
| 发布日期 | 发布时间 | ✅ |
| 工作地点 | 城市/地区 | |
| 学历要求 | 本科/硕士/博士等 | |
| 简历投递邮箱 | 联系邮箱 | |
| 招聘详情(纯文本) | 详情页文本内容 | |
| 链接 | 详情页 URL | ✅ |

---

## 定时任务配置

推荐使用 OpenClaw 的 cron 功能配置每日定时任务：

| 时间 | 高校 | 脚本 |
|------|------|------|
| 22:00 | 高校A | `fudan_fulltime.py`, `fudan_intern.py`, `fudan_zhaopin.py`, `fudan_talk.py` |
| 22:20 | 高校B | `pku_recruit.py`, `pku_intern.py` |
| 22:40 | 高校C | `qinghua_recruit.py` |
| 23:00 | 高校D | `zju_recruit.py` |
| 23:20 | 高校E | `sjtu_recruit.py` |

**Cron 配置示例**（北京时间）：

```json
{
  "name": "fudan-daily-sync",
  "schedule": {
    "kind": "cron",
    "expr": "0 22 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "运行复旦就业信息爬虫..."
  }
}
```

---

## 与飞书多维表格集成

本项目与 `jobs` 技能配合，可将抓取结果自动写入飞书多维表格「生涯信息表」。

### 目标表格

- **表格名称**: 生涯信息表
- **App Token**: 请联系管理员获取
- **Table ID**: 请联系管理员获取

### 写入流程

1. **运行爬虫脚本** — 输出 JSON 到 `output/` 目录
2. **读取 JSON 结果** — 提取职位列表
3. **敏感词过滤** — 处理政治敏感词（见下方说明）
4. **查重** — 检查表格中是否已存在相同记录
5. **写入飞书** — 使用 `feishu_bitable_create_record` 写入

### 敏感词过滤（重要！）

**⚠️ 事业单位/党政机关公告中常含政治敏感词，会触发 DeepSeek 模型的内容审查，必须在写入前过滤！**

**常见敏感词替换规则**:

| 原词 | 替换为 |
|------|--------|
| 中共中央 | 中央 |
| 党校 | 培训中心 |
| 党委 | 委员会 |
| 纪委 | 纪律检查委 |
| 国务院 | 国家机关 |
| 国资委 | 国资监管委 |
| 党组 | (删除) |

**示例**:
- 原名: "国务院国资委干部教育培训中心(中共中央党校国务院国资委分校)"
- 简化: "国资委干部教育培训中心"

---

## 常见问题

### Q1: 为什么某些高校需要 token？

A: 部分高校就业信息网的后端 API 需要 token 认证，但这些 token 通常是公开固定值，无需登录即可获取。

### Q2: 为什么某些高校有数据限制？

A: 部分高校就业网对未登录用户有限制。如需更多数据，需要登录后获取相应权限。

### Q3: 如何处理 content_filter 错误？

A: 这通常是抓取的内容中包含政治敏感词导致的。请参考上方「敏感词过滤」章节，在写入前对标题、公司名称、信息描述等字段进行脱敏处理。

### Q4: 如何避免重复写入？

A: 写入前先调用 `feishu_bitable_list_records` 获取表格已有记录，建立索引。判断标准：
- 公司名 + 标题高度重叠 → 重复
- 公司名 + 信息描述核心内容相同 → 重复

### Q5: 抓取失败怎么办？

A: 检查以下几点：
1. 网络连接是否正常
2. API 是否有变更
3. 认证信息是否过期
4. 查看错误日志定位问题

---

## 更新日志

### v1.1.0 (2026-05-23)
- 完善 README 文档，新增详细说明
- 新增敏感词过滤规则
- 新增常见问题解答
- 新增与飞书多维表格集成说明

### v1.0.0 (2026-05-22)
- 初始发布
- 支持多所高校
- 提供一键安装脚本
- 支持每日定时同步

---

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 报告问题

如发现问题，请提交 Issue 并包含：
- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 环境信息（Python 版本、操作系统等）

---

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 链接

- **GitHub**: [github.com/MoyuOlogy/jobs](https://github.com/MoyuOlogy/jobs)
- **OpenClaw**: [github.com/openclaw/openclaw](https://github.com/openclaw/openclaw)
- **生涯信息表**: 请联系管理员获取访问权限

---

## 致谢

感谢相关高校提供的公开就业信息 API支持。

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/MoyuOlogy">MoyuOlogy</a>
</p>
