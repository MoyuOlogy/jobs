# 🎓 高校就业信息网爬虫技能集

> OpenClaw Agent Skills — 五大高校就业信息网自动抓取

支持 **复旦大学 · 北京大学 · 清华大学 · 浙江大学 · 上海交通大学** 就业信息网的招聘信息自动抓取，每日定时同步，输出结构化 JSON 并写入飞书多维表格。

---

## 🚀 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/MoyuOlogy/jobs/main/install.sh | bash
```

或手动克隆：

```bash
git clone https://github.com/MoyuOlogy/jobs.git
cp -r jobs/* ~/.openclaw/workspace/skills/
```

> 安装脚本会自动检测 OpenClaw workspace 路径，将 5 个技能复制到 `skills/` 目录。

---

## 📂 技能列表

| 技能 | 学校 | API 类型 | 脚本 |
|------|------|----------|------|
| `fudanjobs` | 复旦大学 | REST (auth Basic) | 全职 / 实习 / 招聘信息 / 宣讲会 4 个 |
| `pkujobs` | 北京大学 | REST (token: 111) | 日常招聘 / 日常实习 2 个 |
| `qinghuajobs` | 清华大学 | REST (无需认证) | 交互式 + 每日同步 2 个 |
| `zjujobs` | 浙江大学 | REST (JSON) | 每日同步 1 个 |
| `sjtujobs` | 上海交通大学 | REST (无需认证，限10条/页) | 交互式 + 每日同步 2 个 |

---

## 📖 使用方式

### 交互式（手动查询）

```bash
# 查看今天的清华/交大招聘，前3页
python3 skills/qinghuajobs/qinghuajobs.py --today --detail
python3 skills/sjtujobs/sjtujobs.py --today

# 指定日期，保存为文件
python3 skills/qinghuajobs/qinghuajobs.py --date 2026-05-20 --detail --save
```

### 每日定时同步（cron）

```bash
# 各校每日同步脚本，输出 JSON 到 output/ 目录
python3 skills/fudanjobs/scripts/fudan_fulltime.py
python3 skills/pkujobs/scripts/pku_recruit.py
python3 skills/qinghuajobs/scripts/qinghua_recruit.py
python3 skills/zjujobs/scripts/zju_recruit.py
python3 skills/sjtujobs/scripts/sjtu_recruit.py
```

配合 OpenClaw cron 定时任务（推荐节奏）：

| 时间 | 学校 |
|------|------|
| 22:00 | 复旦大学 |
| 22:20 | 北京大学 |
| 22:40 | 清华大学 |
| 23:00 | 浙江大学 |
| 23:20 | 上海交通大学 |

---

## 🔧 输出格式

每个脚本输出 JSON 文件，包含：

```json
{
  "爬取时间": "2026-05-22 23:50:00",
  "数据来源": "xxx大学就业信息网",
  "筛选日期": "2026-05-22",
  "总计数量": 10,
  "职位列表": [
    {
      "标题": "xxx校招",
      "公司/组织名称": "xxx有限公司",
      "发布日期": "2026-05-22",
      "工作地点": "北京",
      "学历要求": "本科及以上",
      "简历投递邮箱": "hr@example.com",
      "招聘详情(纯文本)": "...",
      "链接": "https://..."
    }
  ]
}
```

与 OpenClaw `jobs` 技能配合，可自动写入飞书多维表格「生涯信息表」。

---

## ⚙️ 配置说明

各校 API 特点和注意事项：

- **复旦**：需要 `auth: Basic MTAyNDY6MTAyNDY=` 认证头
- **北大**：需要 `token: 111` 公开 token，API 分招聘/实习两接口
- **清华**：无认证，列表 API 用 POST form，详情页是 HTML 需解析
- **浙大**：无认证，API 用 JSON POST，字段结构较完整
- **交大**：无认证，但**未登录用户每页限制 10 条**（其他页大小返回 403）

---

## 📄 许可证

MIT

---

## 🔗 链接

- GitHub: [github.com/MoyuOlogy/jobs](https://github.com/MoyuOlogy/jobs)
- OpenClaw: [github.com/openclaw/openclaw](https://github.com/openclaw/openclaw)