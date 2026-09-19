#!/bin/bash

# OpenTelemetry & k6 Codelabs 服务器启动脚本

REQUESTED_PORT=${1:-8088}

# 使用 Python 测试实际可 bind 的端口（100% 精准检测并自动避开已被占用的端口）
ACTUAL_PORT=$(python3 -c "
import socket

requested = int('$REQUESTED_PORT') if '$REQUESTED_PORT'.isdigit() else 8088
candidates = [requested, 8088, 9000, 8888, 9999, 8081, 8082, 8000]
seen = set()
order = []
for c in candidates:
    if c not in seen:
        seen.add(c)
        order.append(c)

selected = None
for p in order:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', p))
        s.close()
        selected = p
        break
    except OSError:
        continue

print(selected if selected is not None else requested)
" 2>/dev/null || echo "${REQUESTED_PORT}")

if [ "$ACTUAL_PORT" != "$REQUESTED_PORT" ]; then
    echo "⚠️  端口 $REQUESTED_PORT 已被其他服务（如 k3d 容器）占用。"
    echo "🔄 自动切换至可用端口: $ACTUAL_PORT"
fi

PORT=$ACTUAL_PORT

echo "================================================"
echo "🔭 可观测性实验室与 k6 Codelabs 本地服务器"
echo "================================================"
echo ""
echo "🚀 HTTP 服务器启动于端口: $PORT"
echo ""
echo "🌐 访问教程："
echo "  📌 课程首页 (含 k6 专栏): http://localhost:$PORT"
echo "  🔥 Grafana k6 效能测试:  http://localhost:$PORT/k6-performance-testing/"
echo "  🔭 OpenTelemetry 教程:   http://localhost:$PORT/o11y-lab-tutorial/"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/generated"

# 启动 HTTP 服务器
python3 -m http.server "$PORT"
