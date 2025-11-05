#!/bin/bash

# OpenTelemetry 混合 Instrumentation 测试脚本

echo "==================================================="
echo "OpenTelemetry Hybrid Instrumentation Test"
echo "==================================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 测试步骤：${NC}"
echo "1. 构建 service-a 的混合 instrumentation 镜像"
echo "2. 临时启动服务"
echo "3. 发送测试请求"
echo "4. 查看结果"
echo ""

cd services/service-a

# 1. 构建镜像
echo -e "${YELLOW}Step 1: 构建镜像...${NC}"
docker build -f Dockerfile.hybrid -t service-a-hybrid:test . 2>&1 | tail -5

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 镜像构建成功${NC}"
else
    echo "❌ 镜像构建失败"
    exit 1
fi

echo ""

# 2. 启动服务
echo -e "${YELLOW}Step 2: 启动服务...${NC}"
docker run -d --name service-a-hybrid-test \
    --network o11y_lab_for_dummies_o11y-lab \
    -p 8091:8001 \
    -e OTEL_COLLECTOR_ENDPOINT=http://otel-collector:4317 \
    -e DB_HOST=postgres \
    -e SERVICE_B_URL=http://service-b:8002 \
    -e SERVICE_D_URL=http://service-d:8004 \
    service-a-hybrid:test

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 服务启动成功 (端口 8091)${NC}"
    echo "   等待服务就绪..."
    sleep 5
else
    echo "❌ 服务启动失败"
    exit 1
fi

echo ""

# 3. 测试服务信息
echo -e "${YELLOW}Step 3: 测试服务信息...${NC}"
echo -e "${BLUE}GET http://localhost:8091/info${NC}"
curl -s http://localhost:8091/info | jq .

echo ""
echo ""

# 4. 测试健康检查
echo -e "${YELLOW}Step 4: 测试健康检查...${NC}"
echo -e "${BLUE}GET http://localhost:8091/health${NC}"
curl -s http://localhost:8091/health | jq .

echo ""
echo ""

# 5. 测试业务端点（会产生 traces）
echo -e "${YELLOW}Step 5: 测试业务端点（生成 traces）...${NC}"
echo -e "${BLUE}GET http://localhost:8091/process${NC}"
response=$(curl -s http://localhost:8091/process)
echo "$response" | jq .

# 提取 trace_id
trace_id=$(echo "$response" | jq -r '.trace_id')

echo ""
echo ""

# 6. 显示结果
echo -e "${GREEN}==================================================="
echo "✅ 测试完成！"
echo "===================================================${NC}"
echo ""
echo -e "${BLUE}📊 查看 Observability 数据：${NC}"
echo ""
echo "1️⃣  Tempo (Traces):"
echo "   http://localhost:3000/explore"
echo "   搜索 trace_id: ${trace_id}"
echo ""
echo "2️⃣  Loki (Logs):"
echo "   http://localhost:3000/explore"
echo "   查询: {service_name=\"service-a-hybrid\"} |= \"${trace_id}\""
echo ""
echo "3️⃣  Prometheus (Metrics):"
echo "   http://localhost:3000/explore"
echo "   查询: service_a_process_total{instrumentation=\"hybrid\"}"
echo ""

echo -e "${YELLOW}🔍 查看自动埋点的 Span 层级：${NC}"
echo "在 Tempo 中你会看到："
echo "  GET /process                              [自动]"
echo "  ├── service_a.business_logic              [手动]"
echo "  │   ├── service_a.database_business_logic [手动]"
echo "  │   │   ├── INSERT INTO request_logs      [自动]"
echo "  │   │   └── SELECT COUNT(*)               [自动]"
echo "  │   ├── service_a.external_api_business   [手动]"
echo "  │   │   └── GET https://api.github.com    [自动]"
echo "  │   ├── service_a.call_service_d_business [手动]"
echo "  │   │   └── GET http://service-d:8004     [自动]"
echo "  │   └── service_a.call_service_b_business [手动]"
echo "  │       └── POST http://service-b:8002    [自动]"
echo ""

echo -e "${BLUE}🧹 清理测试容器：${NC}"
echo "docker stop service-a-hybrid-test"
echo "docker rm service-a-hybrid-test"
echo ""

read -p "是否现在清理测试容器？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker stop service-a-hybrid-test >/dev/null 2>&1
    docker rm service-a-hybrid-test >/dev/null 2>&1
    echo -e "${GREEN}✅ 测试容器已清理${NC}"
fi
