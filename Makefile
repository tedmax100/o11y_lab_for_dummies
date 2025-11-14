.PHONY: help start stop restart logs clean build test \
	chaos-help chaos-kill-random chaos-kill-all chaos-network-delay chaos-network-loss \
	chaos-network-corrupt chaos-stress-cpu chaos-kill-gateway chaos-delay-service-a \
	chaos-loss-service-b chaos-stress-postgres chaos-pause-kafka chaos-microservice-chain \
	chaos-database-outage chaos-network-partition chaos-stop chaos-clean chaos-status chaos-logs

# 默认目标
help:
	@echo "OpenTelemetry Observability Lab - 可用命令:"
	@echo ""
	@echo "  make start       - 启动所有服务"
	@echo "  make stop        - 停止所有服务"
	@echo "  make restart     - 重启所有服务"
	@echo "  make logs        - 查看所有服务日志"
	@echo "  make build       - 构建所有服务镜像"
	@echo "  make clean       - 清理所有容器和数据"
	@echo "  make test        - 发送测试请求"
	@echo "  make status      - 查看服务状态"
	@echo "  make chaos-help  - 🌪️  查看混沌测试命令 (Pumba)"
	@echo ""

# 启动服务
start:
	@echo "🚀 启动所有服务..."
	docker-compose up -d
	@echo "✅ 服务已启动"
	@echo "访问 Grafana: http://localhost:3000"
	@echo "访问 API Gateway: http://localhost:8080"

# 停止服务
stop:
	@echo "🛑 停止所有服务..."
	docker-compose down
	@echo "✅ 服务已停止"

# 重启服务
restart: stop start

# 查看日志
logs:
	docker-compose logs -f

# 查看特定服务日志
logs-api-gateway:
	docker-compose logs -f api-gateway

logs-service-a:
	docker-compose logs -f service-a

logs-service-b:
	docker-compose logs -f service-b

logs-service-c:
	docker-compose logs -f service-c

logs-service-d:
	docker-compose logs -f service-d

logs-collector:
	docker-compose logs -f otel-collector

# 构建镜像
build:
	@echo "🏗️  构建所有服务镜像..."
	docker-compose build
	@echo "✅ 镜像构建完成"

# 清理
clean:
	@echo "🧹 清理容器和数据..."
	docker-compose down -v
	@echo "✅ 清理完成"

# 查看状态
status:
	@echo "📊 服务状态:"
	@docker-compose ps

# 测试
test:
	@echo "🧪 发送测试请求..."
	@for i in 1 2 3 4 5 6 7 8 9; do \
		echo "Request $$i:"; \
		curl -s http://localhost:8080/api/process | jq -r '.status'; \
		sleep 1; \
	done
	@echo "✅ 测试完成"

# 检查健康状态
health:
	@echo "🏥 检查服务健康状态..."
	@echo "API Gateway:"
	@curl -s http://localhost:8080/health | jq
	@echo ""
	@echo "Service A:"
	@curl -s http://localhost:8001/health | jq
	@echo ""
	@echo "Service B:"
	@curl -s http://localhost:8002/health | jq
	@echo ""
	@echo "Service C:"
	@curl -s http://localhost:8003/health | jq
	@echo ""
	@echo "Service D:"
	@curl -s http://localhost:8004/health | jq

# 开发模式 - 只启动基础设施
infra:
	@echo "🏗️  启动基础设施 (DB, Kafka, 可观测性栈)..."
	docker-compose up -d postgres kafka zookeeper otel-collector tempo loki prometheus grafana
	@echo "✅ 基础设施已启动"

# 初始化数据库
init-db:
	@echo "🗄️  初始化数据库..."
	docker-compose exec postgres psql -U postgres -d o11ylab -c "SELECT version();"
	@echo "✅ 数据库初始化完成"

# ==================== 混沌测试 (Pumba) ====================

# 混沌测试帮助
chaos-help:
	@echo "🌪️  Pumba 混沌测试命令:"
	@echo ""
	@echo "  基础混沌测试:"
	@echo "  make chaos-kill-random       - 随机杀死一个应用服务"
	@echo "  make chaos-kill-all          - 杀死所有应用服务 (循环)"
	@echo "  make chaos-network-delay     - 对所有服务添加网络延迟"
	@echo "  make chaos-network-loss      - 对所有服务添加网络丢包"
	@echo "  make chaos-network-corrupt   - 对所有服务添加包损坏"
	@echo "  make chaos-stress-cpu        - 对所有服务进行 CPU 压力测试"
	@echo ""
	@echo "  服务特定混沌测试:"
	@echo "  make chaos-kill-gateway      - 杀死 API Gateway"
	@echo "  make chaos-delay-service-a   - 给 Service A 添加延迟"
	@echo "  make chaos-loss-service-b    - 给 Service B 添加丢包"
	@echo "  make chaos-stress-postgres   - 对 PostgreSQL 进行压力测试"
	@echo "  make chaos-pause-kafka       - 暂停 Kafka 容器"
	@echo ""
	@echo "  复杂场景:"
	@echo "  make chaos-microservice-chain - 模拟微服务链路故障"
	@echo "  make chaos-database-outage    - 模拟数据库中断"
	@echo "  make chaos-network-partition  - 模拟网络分区"
	@echo ""
	@echo "  管理命令:"
	@echo "  make chaos-stop              - 停止所有运行中的 Pumba 容器"
	@echo "  make chaos-clean             - 清理所有 Pumba 容器"
	@echo ""

# 基础混沌测试 - 随机杀死一个应用服务
chaos-kill-random:
	@echo "💥 随机杀死一个应用服务 (每 30 秒)"
	@docker rm -f pumba-kill-random 2>/dev/null || true
	docker run -d --name pumba-kill-random \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		--interval 30s --random --log-level info \
		kill --signal SIGKILL "re2:^(api-gateway|service-[a-d])$$"
	@echo "✅ Pumba 已启动，使用 'make chaos-stop' 停止"

# 杀死所有应用服务（循环测试）
chaos-kill-all:
	@echo "💥 每 20 秒杀死所有应用服务"
	@docker rm -f pumba-kill-all 2>/dev/null || true
	docker run -d --name pumba-kill-all \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		--interval 20s --log-level info \
		kill --signal SIGTERM "re2:^(api-gateway|service-[a-d])$$"
	@echo "✅ Pumba 已启动"

# 网络延迟 - 给所有应用服务添加 500ms 延迟
chaos-network-delay:
	@echo "🐌 添加网络延迟 (500ms ± 100ms) 到所有应用服务，持续 5 分钟"
	@docker rm -f pumba-delay 2>/dev/null || true
	docker run -d --name pumba-delay \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		--log-level info \
		netem --duration 5m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
		delay --time 500 --jitter 100 --distribution normal \
		"re2:^(api-gateway|service-[a-d])$$"
	@echo "✅ 网络延迟已应用 5 分钟"

# 网络丢包 - 20% 丢包率
chaos-network-loss:
	@echo "📉 添加 20% 网络丢包率到所有应用服务，持续 5 分钟"
	@docker rm -f pumba-loss 2>/dev/null || true
	docker run -d --name pumba-loss \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		--log-level info \
		netem --duration 5m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
		loss --percent 20 \
		"re2:^(api-gateway|service-[a-d])$$"
	@echo "✅ 网络丢包已应用 5 分钟"

# 网络包损坏 - 10% 损坏率
chaos-network-corrupt:
	@echo "🔨 添加 10% 网络包损坏率到所有应用服务，持续 5 分钟"
	@docker rm -f pumba-corrupt 2>/dev/null || true
	docker run -d --name pumba-corrupt \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		--log-level info \
		netem --duration 5m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
		corrupt --percent 10 \
		"re2:^(api-gateway|service-[a-d])$$"
	@echo "✅ 网络包损坏已应用 5 分钟"

# CPU 压力测试
chaos-stress-cpu:
	@echo "💪 对所有应用服务进行 CPU 压力测试，持续 2 分钟"
	@docker rm -f pumba-stress 2>/dev/null || true
	docker run -d --name pumba-stress \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		--log-level info \
		stress --duration 2m \
		--stressors "--cpu 2 --timeout 120s" \
		"re2:^(api-gateway|service-[a-d])$$"
	@echo "✅ CPU 压力测试已启动 2 分钟"

# ==================== 服务特定混沌测试 ====================

# 杀死 API Gateway
chaos-kill-gateway:
	@echo "💥 杀死 API Gateway"
	docker run --rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		kill --signal SIGKILL api-gateway
	@echo "✅ API Gateway 已被杀死"

# 给 Service A 添加延迟
chaos-delay-service-a:
	@echo "🐌 给 Service A 添加 1000ms 延迟，持续 3 分钟"
	@docker rm -f pumba-delay-service-a 2>/dev/null || true
	docker run -d --name pumba-delay-service-a \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		netem --duration 3m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
		delay --time 1000 --jitter 200 service-a
	@echo "✅ Service A 延迟已应用"

# 给 Service B 添加丢包
chaos-loss-service-b:
	@echo "📉 给 Service B 添加 30% 丢包率，持续 3 分钟"
	@docker rm -f pumba-loss-service-b 2>/dev/null || true
	docker run -d --name pumba-loss-service-b \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		netem --duration 3m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
		loss --percent 30 service-b
	@echo "✅ Service B 丢包已应用"

# 对 PostgreSQL 进行压力测试
chaos-stress-postgres:
	@echo "💪 对 PostgreSQL 进行压力测试，持续 2 分钟"
	@docker rm -f pumba-stress-postgres 2>/dev/null || true
	docker run -d --name pumba-stress-postgres \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		stress --duration 2m \
		--stressors "--cpu 2 --io 1 --timeout 120s" postgres
	@echo "✅ PostgreSQL 压力测试已启动"

# 暂停 Kafka
chaos-pause-kafka:
	@echo "⏸️  暂停 Kafka 容器 30 秒"
	@docker rm -f pumba-pause-kafka 2>/dev/null || true
	docker run -d --name pumba-pause-kafka \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		pause --duration 30s kafka
	@echo "✅ Kafka 已暂停 30 秒"

# ==================== 复杂混沌场景 ====================

# 模拟微服务链路故障
chaos-microservice-chain:
	@echo "⛓️  模拟微服务链路故障："
	@echo "  - Service A: 网络延迟 800ms"
	@echo "  - Service B: 15% 丢包"
	@echo "  - Service C: CPU 压力"
	@echo "  持续 5 分钟"
	@docker rm -f pumba-chain-delay-a pumba-chain-loss-b pumba-chain-stress-c 2>/dev/null || true
	@docker run -d --name pumba-chain-delay-a \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		netem --duration 5m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
		delay --time 800 --jitter 150 service-a
	@docker run -d --name pumba-chain-loss-b \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		netem --duration 5m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
		loss --percent 15 service-b
	@docker run -d --name pumba-chain-stress-c \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		stress --duration 5m \
		--stressors "--cpu 2 --timeout 300s" service-c
	@echo "✅ 微服务链路混沌测试已启动"

# 模拟数据库中断
chaos-database-outage:
	@echo "🗄️  模拟数据库中断场景："
	@echo "  - PostgreSQL: 网络延迟 2000ms"
	@echo "  - 持续 3 分钟"
	@docker rm -f pumba-db-outage 2>/dev/null || true
	docker run -d --name pumba-db-outage \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		netem --duration 3m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
		delay --time 2000 --jitter 500 postgres
	@echo "✅ 数据库中断场景已启动"

# 模拟网络分区（Service A 和 Service B 之间）
chaos-network-partition:
	@echo "🌐 模拟网络分区："
	@echo "  - Service A: 90% 丢包"
	@echo "  - Service B: 90% 丢包"
	@echo "  - 持续 2 分钟"
	@docker rm -f pumba-partition-a pumba-partition-b 2>/dev/null || true
	@docker run -d --name pumba-partition-a \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		netem --duration 2m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
		loss --percent 90 service-a
	@docker run -d --name pumba-partition-b \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		netem --duration 2m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
		loss --percent 90 service-b
	@echo "✅ 网络分区场景已启动"

# ==================== 管理命令 ====================

# 停止所有 Pumba 容器
chaos-stop:
	@echo "🛑 停止所有运行中的 Pumba 容器..."
	@docker ps --filter "name=pumba-*" -q | xargs -r docker stop
	@echo "✅ 所有 Pumba 容器已停止"

# 清理所有 Pumba 容器
chaos-clean: chaos-stop
	@echo "🧹 清理所有 Pumba 容器..."
	@docker ps -a --filter "name=pumba-*" -q | xargs -r docker rm
	@echo "✅ Pumba 容器已清理"

# 查看 Pumba 容器状态
chaos-status:
	@echo "📊 Pumba 容器状态:"
	@docker ps -a --filter "name=pumba-*" --format "table {{.Names}}\t{{.Status}}\t{{.Command}}"

# 查看特定 Pumba 容器日志
chaos-logs:
	@echo "📋 选择要查看日志的 Pumba 容器:"
	@docker ps -a --filter "name=pumba-*" --format "{{.Names}}"
	@echo ""
	@echo "使用: docker logs <container-name>"
