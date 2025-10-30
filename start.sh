#!/bin/bash

# OpenTelemetry Observability Lab 启动脚本

set -e

echo "========================================="
echo "  OpenTelemetry Observability Lab"
echo "========================================="
echo ""

# 检查 Docker 和 Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 和 Docker Compose 已安装"
echo ""

# 检查是否有正在运行的容器
if [ "$(docker ps -q -f name=o11y)" ]; then
    echo "⚠️  检测到正在运行的容器，正在停止..."
    docker-compose down
    echo ""
fi

# 构建和启动服务
echo "🏗️  构建服务镜像..."
docker-compose build

echo ""
echo "🚀 启动所有服务..."
docker-compose up -d

echo ""
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "📊 服务状态:"
docker-compose ps

echo ""
echo "========================================="
echo "  启动完成！"
echo "========================================="
echo ""
echo "📍 访问地址:"
echo "  - API Gateway:  http://localhost:8080"
echo "  - Grafana:      http://localhost:3000 (admin/admin)"
echo "  - Prometheus:   http://localhost:9090"
echo "  - Tempo:        http://localhost:3200"
echo "  - Loki:         http://localhost:3100"
echo ""
echo "🧪 测试请求:"
echo "  curl http://localhost:8080/api/process"
echo ""
echo "📝 查看日志:"
echo "  docker-compose logs -f"
echo ""
echo "🛑 停止服务:"
echo "  docker-compose down"
echo ""
echo "========================================="
