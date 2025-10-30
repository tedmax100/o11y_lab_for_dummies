.PHONY: help start stop restart logs clean build test

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
	@for i in 1 2 3 4 5; do \
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
