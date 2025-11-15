#!/bin/bash

# OpenTelemetry Hybrid Instrumentation Test Script

echo "==================================================="
echo "OpenTelemetry Hybrid Instrumentation Test"
echo "==================================================="
echo ""

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Test Steps:${NC}"
echo "1. Build service-a hybrid instrumentation image"
echo "2. Start service temporarily"
echo "3. Send test requests"
echo "4. View results"
echo ""

cd services/service-a

# 1. Build image
echo -e "${YELLOW}Step 1: Building image...${NC}"
docker build -f Dockerfile.hybrid -t service-a-hybrid:test . 2>&1 | tail -5

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Image built successfully${NC}"
else
    echo "❌ Image build failed"
    exit 1
fi

echo ""

# 2. Start service
echo -e "${YELLOW}Step 2: Starting service...${NC}"
docker run -d --name service-a-hybrid-test \
    --network o11y_lab_for_dummies_o11y-lab \
    -p 8091:8001 \
    -e OTEL_COLLECTOR_ENDPOINT=http://otel-collector:4317 \
    -e DB_HOST=postgres \
    -e SERVICE_B_URL=http://service-b:8002 \
    -e SERVICE_D_URL=http://service-d:8004 \
    service-a-hybrid:test

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Service started successfully (port 8091)${NC}"
    echo "   Waiting for service to be ready..."
    sleep 5
else
    echo "❌ Service startup failed"
    exit 1
fi

echo ""

# 3. Test service info
echo -e "${YELLOW}Step 3: Testing service info...${NC}"
echo -e "${BLUE}GET http://localhost:8091/info${NC}"
curl -s http://localhost:8091/info | jq .

echo ""
echo ""

# 4. Test health check
echo -e "${YELLOW}Step 4: Testing health check...${NC}"
echo -e "${BLUE}GET http://localhost:8091/health${NC}"
curl -s http://localhost:8091/health | jq .

echo ""
echo ""

# 5. Test business endpoint (generates traces)
echo -e "${YELLOW}Step 5: Testing business endpoint (generating traces)...${NC}"
echo -e "${BLUE}GET http://localhost:8091/process${NC}"
response=$(curl -s http://localhost:8091/process)
echo "$response" | jq .

# Extract trace_id
trace_id=$(echo "$response" | jq -r '.trace_id')

echo ""
echo ""

# 6. Display results
echo -e "${GREEN}==================================================="
echo "✅ Test Complete!"
echo "===================================================${NC}"
echo ""
echo -e "${BLUE}📊 View Observability Data:${NC}"
echo ""
echo "1️⃣  Tempo (Traces):"
echo "   http://localhost:3000/explore"
echo "   Search trace_id: ${trace_id}"
echo ""
echo "2️⃣  Loki (Logs):"
echo "   http://localhost:3000/explore"
echo "   Query: {service_name=\"service-a-hybrid\"} |= \"${trace_id}\""
echo ""
echo "3️⃣  Prometheus (Metrics):"
echo "   http://localhost:3000/explore"
echo "   Query: service_a_process_total{instrumentation=\"hybrid\"}"
echo ""

echo -e "${YELLOW}🔍 View Auto-Instrumented Span Hierarchy:${NC}"
echo "In Tempo you will see:"
echo "  GET /process                              [auto]"
echo "  ├── service_a.business_logic              [manual]"
echo "  │   ├── service_a.database_business_logic [manual]"
echo "  │   │   ├── INSERT INTO request_logs      [auto]"
echo "  │   │   └── SELECT COUNT(*)               [auto]"
echo "  │   ├── service_a.external_api_business   [manual]"
echo "  │   │   └── GET https://api.github.com    [auto]"
echo "  │   ├── service_a.call_service_d_business [manual]"
echo "  │   │   └── GET http://service-d:8004     [auto]"
echo "  │   └── service_a.call_service_b_business [manual]"
echo "  │       └── POST http://service-b:8002    [auto]"
echo ""

echo -e "${BLUE}🧹 Cleanup Test Container:${NC}"
echo "docker stop service-a-hybrid-test"
echo "docker rm service-a-hybrid-test"
echo ""

read -p "Clean up test container now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker stop service-a-hybrid-test >/dev/null 2>&1
    docker rm service-a-hybrid-test >/dev/null 2>&1
    echo -e "${GREEN}✅ Test container cleaned up${NC}"
fi
