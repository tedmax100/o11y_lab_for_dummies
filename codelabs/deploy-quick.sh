#!/bin/bash

# 快速部署脚本 - 自动提交并推送到 GitHub

set -e

echo "================================================"
echo "🚀 Codelabs 快速部署到 GitHub Pages"
echo "================================================"
echo ""

# 检查是否有未提交的更改
if [[ -z $(git status -s) ]]; then
    echo "⚠️  没有检测到更改，无需部署"
    exit 0
fi

# 显示即将提交的更改
echo "📝 检测到以下更改："
git status -s
echo ""

# 询问提交信息
read -p "📄 输入提交信息（留空使用默认）: " commit_msg
if [[ -z "$commit_msg" ]]; then
    commit_msg="docs: update codelabs tutorials"
fi

# 添加所有 codelabs 相关文件
echo "➕ 添加文件..."
git add codelabs/
git add .github/workflows/deploy-codelabs.yml 2>/dev/null || true

# 提交
echo "💾 提交更改..."
git commit -m "$commit_msg"

# 获取当前分支
current_branch=$(git branch --show-current)

# 推送
echo "🚢 推送到 GitHub (分支: $current_branch)..."
git push origin $current_branch

# 获取仓库信息
repo_url=$(git config --get remote.origin.url)
repo_name=$(basename -s .git "$repo_url")
user_name=$(dirname "$repo_url" | xargs basename)

if [[ "$repo_url" == *"github.com"* ]]; then
    # 提取 GitHub 用户名和仓库名
    if [[ "$repo_url" == *":"* ]]; then
        # SSH URL: git@github.com:user/repo.git
        user_name=$(echo "$repo_url" | sed 's/.*:\(.*\)\/.*/\1/')
        repo_name=$(echo "$repo_url" | sed 's/.*\/\(.*\)\.git/\1/')
    else
        # HTTPS URL: https://github.com/user/repo.git
        user_name=$(echo "$repo_url" | sed 's/.*github.com\/\(.*\)\/.*/\1/')
        repo_name=$(echo "$repo_url" | sed 's/.*\/\(.*\)\.git/\1/')
    fi

    echo ""
    echo "================================================"
    echo "✅ 推送成功！"
    echo "================================================"
    echo ""
    echo "📊 查看部署状态："
    echo "   https://github.com/$user_name/$repo_name/actions"
    echo ""
    echo "🌐 部署完成后访问："
    echo "   https://$user_name.github.io/$repo_name/"
    echo ""
    echo "⏳ 通常需要 1-2 分钟完成部署"
    echo "================================================"
else
    echo ""
    echo "✅ 推送成功！"
    echo ""
    echo "请手动检查部署状态"
fi
