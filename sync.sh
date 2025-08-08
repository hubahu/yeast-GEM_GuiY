#!/bin/bash

cd "/e/22_CodeProjects/yeast-GEM_GuiY" || { echo "❌ 无法进入目录"; exit 1; }

# 确保在 main 分支
git checkout main

# 先提交本地更改
git add .
git commit -m "自动提交: $(date '+%Y-%m-%d %H:%M:%S')" || echo "无新更改"

# 普通拉取（避免 rebase 冲突）
git pull origin main

# 推送更改
git push origin main

echo "✅ 同步完成"