#!/bin/bash

# 生成 Go 服务的依赖文件脚本

set -e

echo "========================================="
echo "  生成 Go 依赖文件"
echo "========================================="
echo ""

# 检查 Go 是否安装
if ! command -v go &> /dev/null; then
    echo "❌ Go 未安装"
    echo ""
    echo "有两个选择:"
    echo ""
    echo "1. 安装 Go (推荐):"
    echo "   brew install go"
    echo ""
    echo "2. 使用 Docker 生成依赖:"
    echo "   继续执行，我们将使用 Docker..."
    echo ""
    read -p "按回车继续使用 Docker，或 Ctrl+C 退出安装 Go: "
    USE_DOCKER=true
else
    echo "✅ 检测到 Go: $(go version)"
    USE_DOCKER=false
fi

echo ""

if [ "$USE_DOCKER" = true ]; then
    echo "🐳 使用 Docker 生成 go.sum 文件..."
    echo ""

    # Service B
    echo "📦 生成 Service B 依赖..."
    docker run --rm -v "$(pwd)/services/service-b:/app" -w /app golang:1.21-alpine sh -c "go mod tidy && go mod download"

    # Service C
    echo "📦 生成 Service C 依赖..."
    docker run --rm -v "$(pwd)/services/service-c:/app" -w /app golang:1.21-alpine sh -c "go mod tidy && go mod download"

else
    echo "📦 生成依赖文件..."
    echo ""

    # Service B
    echo "  - Service B..."
    cd services/service-b
    go mod tidy
    go mod download
    cd ../..

    # Service C
    echo "  - Service C..."
    cd services/service-c
    go mod tidy
    go mod download
    cd ../..
fi

echo ""
echo "✅ 依赖文件生成完成！"
echo ""
echo "📁 生成的文件:"
echo "  - services/service-b/go.sum"
echo "  - services/service-c/go.sum"
echo ""
echo "现在可以运行: ./start.sh"
echo ""
