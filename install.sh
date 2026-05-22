#!/bin/bash
# ============================================================
# 高校就业信息网爬虫技能集 - 一键安装脚本
# 支持 复旦/北大/清华/浙大/交大 五大高校
# ============================================================
set -e

echo ""
echo "  🎓 高校就业信息网爬虫技能集"
echo "  ==================================="
echo "  复旦 · 北大 · 清华 · 浙大 · 交大"
echo ""

# 检测 OpenClaw workspace 目录
if [ -f "${HOME}/.openclaw/workspace/SOUL.md" ]; then
  WORKSPACE="${HOME}/.openclaw/workspace"
elif [ -n "${OPENCLAW_WORKSPACE}" ]; then
  WORKSPACE="${OPENCLAW_WORKSPACE}"
else
  WORKSPACE=""
fi

# 交互式选择安装目录
if [ -z "${WORKSPACE}" ]; then
  echo "未检测到 OpenClaw workspace，请手动指定："
  read -rp "目标 skills 目录路径: " SKILLS_DIR
  SKILLS_DIR="${SKILLS_DIR%/}"
  if [ ! -d "${SKILLS_DIR}" ]; then
    echo "目录 ${SKILLS_DIR} 不存在，将自动创建"
  fi
else
  SKILLS_DIR="${WORKSPACE}/skills"
fi

mkdir -p "${SKILLS_DIR}"

echo "目标目录：${SKILLS_DIR}"
echo ""

# 临时克隆
TMPDIR=$(mktemp -d)
echo "正在下载…"
git clone --depth 1 https://github.com/MoyuOlogy/jobs.git "${TMPDIR}" 2>/dev/null

# 安装所有 skills
SKILLS=(fudanjobs pkujobs qinghuajobs zjujobs sjtujobs)
for skill in "${SKILLS[@]}"; do
  if [ -d "${TMPDIR}/${skill}" ]; then
    echo -n "  安装 ${skill} ... "
    rm -rf "${SKILLS_DIR}/${skill}"
    cp -r "${TMPDIR}/${skill}" "${SKILLS_DIR}/${skill}"
    echo "✅"
  fi
done

# 清理
rm -rf "${TMPDIR}"

echo ""
echo "========================================="
echo "  ✅ 安装完成！"
echo ""
echo "  已安装技能："
for skill in fudanjobs pkujobs qinghuajobs zjujobs sjtujobs; do
  if [ -f "${SKILLS_DIR}/${skill}/SKILL.md" ]; then
    echo "    📂 ${SKILLS_DIR}/${skill}/"
  fi
done
echo ""
echo "  每日定时同步脚本："
echo "    python3 ${SKILLS_DIR}/fudanjobs/scripts/fudan_fulltime.py"
echo "    python3 ${SKILLS_DIR}/pkujobs/scripts/pku_recruit.py"
echo "    python3 ${SKILLS_DIR}/qinghuajobs/scripts/qinghua_recruit.py"
echo "    python3 ${SKILLS_DIR}/zjujobs/scripts/zju_recruit.py"
echo "    python3 ${SKILLS_DIR}/sjtujobs/scripts/sjtu_recruit.py"
echo ""
echo "  或使用交互式脚本（支持 --today --date --pages 等参数）："
echo "    python3 ${SKILLS_DIR}/qinghuajobs/qinghuajobs.py --today"
echo "    python3 ${SKILLS_DIR}/sjtujobs/sjtujobs.py --today"
echo ""
echo "  ⚠️  部分脚本中硬编码了 DEFAULT 输出路径，"
echo "     如需修改请编辑对应 SKILL.md 中的 OUTPUT_DIR 路径。"
echo ""
echo "  GitHub: https://github.com/MoyuOlogy/jobs"
echo "========================================="