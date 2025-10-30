#!/bin/bash

# Docker 镜像加速器配置脚本（适用于 Colima）

set -e

echo "========================================="
echo "  Docker 镜像加速器配置工具"
echo "========================================="
echo ""

# 检查是否使用 Colima
if ! command -v colima &> /dev/null; then
    echo "❌ 未检测到 Colima"
    echo "此脚本仅适用于 Colima 用户"
    echo ""
    echo "如果你使用 Docker Desktop，请手动配置镜像加速器："
    echo "1. 打开 Docker Desktop 设置"
    echo "2. 进入 Docker Engine"
    echo "3. 添加以下配置："
    echo '   "registry-mirrors": ['
    echo '     "https://docker.mirrors.ustc.edu.cn",'
    echo '     "https://hub-mirror.c.163.com",'
    echo '     "https://mirror.baidubce.com"'
    echo '   ]'
    exit 1
fi

echo "✅ 检测到 Colima"
echo ""

# 检查 Colima 是否运行
if colima status &> /dev/null; then
    echo "⚠️  Colima 正在运行，需要停止后重新配置"
    read -p "是否停止 Colima? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 停止 Colima..."
        colima stop
    else
        echo "❌ 已取消"
        exit 1
    fi
fi

# 配置文件路径
CONFIG_FILE="$HOME/.colima/default/colima.yaml"

# 检查配置文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "⚠️  配置文件不存在，需要先初始化 Colima"
    echo "🚀 启动 Colima 以创建配置文件..."
    colima start
    sleep 5
    colima stop
fi

# 备份原配置文件
echo "💾 备份原配置文件..."
cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"

# 检查是否已配置镜像加速器
if grep -q "registry-mirrors" "$CONFIG_FILE"; then
    echo "⚠️  检测到已有镜像加速器配置"
    read -p "是否覆盖现有配置? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 已取消"
        exit 1
    fi
fi

# 添加镜像加速器配置
echo "📝 配置镜像加速器..."

# 使用 Python 或 yq 来修改 YAML（这里使用简单的文本处理）
if ! grep -q "registry-mirrors:" "$CONFIG_FILE"; then
    # 在 docker 部分添加 registry-mirrors
    cat >> "$CONFIG_FILE" << 'EOF'

  # Docker 镜像加速器配置
  registry-mirrors:
    - https://docker.mirrors.ustc.edu.cn
    - https://hub-mirror.c.163.com
    - https://mirror.baidubce.com
EOF
else
    echo "⚠️  配置已存在，请手动编辑 $CONFIG_FILE"
fi

echo ""
echo "✅ 配置完成！"
echo ""
echo "🚀 启动 Colima..."
colima start

echo ""
echo "🔍 验证配置..."
sleep 3
docker info | grep -A 5 "Registry Mirrors" || echo "⚠️  无法验证镜像配置，但已写入配置文件"

echo ""
echo "========================================="
echo "  配置完成！"
echo "========================================="
echo ""
echo "📝 配置文件位置: $CONFIG_FILE"
echo "💾 备份文件: $CONFIG_FILE.backup.*"
echo ""
echo "现在可以运行: ./start.sh"
echo ""
