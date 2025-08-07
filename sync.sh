#!/bin/bash

# 可选：进入你的项目目录
cd /e/22_CodeProjects/yeast-GEM_GuiY || exit E:\22_CodeProjects\yeast-GEM_GuiY

echo "🔄 拉取远程变更..."
git pull --rebase

echo "📦 添加更改..."
git add .

# 生成提交信息（时间戳）
msg="更新于 $(date '+%Y-%m-%d %H:%M:%S')"

echo "📝 提交中：$msg"
git commit -m "$msg"

echo "🚀 推送到远程仓库..."
git push

echo "✅ 同步完成。"
