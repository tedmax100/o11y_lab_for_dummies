#!/bin/bash

# OpenTelemetry Codelabs 服务器启动脚本

PORT=${1:-8000}

echo "================================================"
echo "OpenTelemetry 可观测性实验室教程服务器"
echo "================================================"
echo ""
echo "启动 HTTP 服务器在端口: $PORT"
echo ""
echo "访问教程："
echo "  主页: http://localhost:$PORT"
echo "  教程: http://localhost:$PORT/o11y-lab-tutorial/"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "================================================"
echo ""

cd generated

# 检查 Python 版本并启动相应的 HTTP 服务器
if command -v python3 &> /dev/null; then
    python3 -m http.server $PORT
elif command -v python &> /dev/null; then
    python -m http.server $PORT
else
    echo "错误: 未找到 Python。请安装 Python 3 后重试。"
    exit 1
fi
