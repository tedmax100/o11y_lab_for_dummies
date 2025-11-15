.PHONY: help start stop restart logs clean build test \
	k6-help k6-smoke k6-load k6-stress k6-spike k6-clean \
	chaos-help chaos-kill-random chaos-kill-all chaos-network-delay chaos-network-loss \
	chaos-network-corrupt chaos-stress-cpu chaos-kill-gateway chaos-delay-service-a \
	chaos-loss-service-b chaos-stress-postgres chaos-pause-kafka chaos-microservice-chain \
	chaos-database-outage chaos-network-partition chaos-stop chaos-clean chaos-status chaos-logs

# Default target
help:
	@echo "OpenTelemetry Observability Lab - Available Commands:"
	@echo ""
	@echo "  make start       - Start all services"
	@echo "  make stop        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View all service logs"
	@echo "  make build       - Build all service images"
	@echo "  make clean       - Clean all containers and data"
	@echo "  make test        - Send test requests"
	@echo "  make status      - View service status"
	@echo "  make k6-help     - 📊 View K6 load testing commands"
	@echo "  make chaos-help  - 🌪️  View chaos testing commands (Pumba)"
	@echo ""

# Start services
start:
	@echo "🚀 Starting all services..."
	docker-compose up -d
	@echo "✅ Services started"
	@echo "Access Grafana: http://localhost:3000"
	@echo "Access API Gateway: http://localhost:8080"

# Stop services
stop:
	@echo "🛑 Stopping all services..."
	docker-compose down
	@echo "✅ Services stopped"

# Restart services
restart: stop start

# View logs
logs:
	docker-compose logs -f

# View specific service logs
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

# Build images
build:
	@echo "🏗️  Building all service images..."
	docker-compose build
	@echo "✅ Image build complete"

# Clean
clean:
	@echo "🧹 Cleaning containers and data..."
	docker-compose down -v
	@echo "✅ Clean complete"

# View status
status:
	@echo "📊 Service Status:"
	@docker-compose ps

# Test
test:
	@echo "🧪 Sending test requests..."
	@for i in 1 2 3 4 5 6 7 8 9; do \
		echo "Request $$i:"; \
		curl -s http://localhost:8080/api/process | jq -r '.status'; \
		sleep 1; \
	done
	@echo "✅ Test complete"

# Check health status
health:
	@echo "🏥 Checking service health status..."
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

# Dev mode - only start infrastructure
infra:
	@echo "🏗️  Starting infrastructure (DB, Kafka, Observability Stack)..."
	docker-compose up -d postgres kafka zookeeper otel-collector tempo loki prometheus grafana
	@echo "✅ Infrastructure started"

# Initialize database
init-db:
	@echo "🗄️  Initializing database..."
	docker-compose exec postgres psql -U postgres -d o11ylab -c "SELECT version();"
	@echo "✅ Database initialization complete"

# ==================== K6 Load Testing ====================

# K6 testing help
k6-help:
	@echo "📊 K6 Load Testing Commands:"
	@echo ""
	@echo "  Quick Start:"
	@echo "  make k6-smoke        - 🔍 Smoke test (1 min, 1 VU) - Quick validation"
	@echo "  make k6-load         - 📈 Load test (3.5 min, 5→20→50 VUs) - Standard load"
	@echo "  make k6-spike        - ⚡ Spike test (4 min, 10→100→150 VUs) - Sudden traffic"
	@echo "  make k6-stress       - 💪 Stress test (6 min, 10→200 VUs) - Find limits"
	@echo ""
	@echo "  Advanced:"
	@echo "  make k6-load BASE_URL=http://your-host:8080  - Custom API Gateway URL"
	@echo "  make k6-clean        - 🧹 Clean K6 test results"
	@echo ""
	@echo "  Test Results:"
	@echo "  - Terminal output shows real-time metrics"
	@echo "  - JSON reports saved to k6/*.json files"
	@echo "  - View live metrics in Grafana (http://localhost:3000)"
	@echo ""
	@echo "  Recommended Order:"
	@echo "  1️⃣  make k6-smoke   - Verify system health"
	@echo "  2️⃣  make k6-load    - Baseline performance"
	@echo "  3️⃣  make k6-spike   - Test resilience"
	@echo "  4️⃣  make k6-stress  - Find bottlenecks (optional)"
	@echo ""
	@echo "  💡 Tip: Open Grafana Explore before running tests to watch live metrics!"
	@echo ""

# Smoke test - Quick validation
k6-smoke:
	@echo "🔍 Running K6 Smoke Test (1 min, 1 VU)..."
	@echo "📌 This test validates basic system functionality"
	@docker run --rm -i --network=host \
		-v $(PWD)/k6:/scripts \
		grafana/k6:latest run /scripts/smoke-test.js
	@echo ""
	@echo "✅ Smoke test complete! Check output above for results."

# Load test - Standard performance test
k6-load:
	@echo "📈 Running K6 Load Test (3.5 min, 5→20→50 VUs)..."
	@echo "📌 This test measures system performance under normal load"
	@echo "💡 Open Grafana (http://localhost:3000) to watch live metrics"
	@docker run --rm -i --network=host \
		-v $(PWD)/k6:/scripts \
		-e BASE_URL=$(or $(BASE_URL),http://localhost:8080) \
		-e SERVICE_A_URL=$(or $(SERVICE_A_URL),http://localhost:8001) \
		grafana/k6:latest run /scripts/load-test.js
	@echo ""
	@echo "✅ Load test complete! Results saved to k6/summary.json"

# Stress test - Find system limits
k6-stress:
	@echo "💪 Running K6 Stress Test (6 min, 10→50→100→200 VUs)..."
	@echo "📌 This test finds system performance limits and bottlenecks"
	@echo "⚠️  WARNING: This may cause high resource usage!"
	@echo "💡 Monitor system resources and Grafana dashboards"
	@docker run --rm -i --network=host \
		-v $(PWD)/k6:/scripts \
		-e BASE_URL=$(or $(BASE_URL),http://localhost:8080) \
		grafana/k6:latest run /scripts/stress-test.js
	@echo ""
	@echo "✅ Stress test complete! Results saved to k6/stress-test-results.json"

# Spike test - Test sudden traffic surge
k6-spike:
	@echo "⚡ Running K6 Spike Test (4 min, 10→100→10→150 VUs)..."
	@echo "📌 This test simulates sudden traffic spikes"
	@echo "💡 Watch how the system handles and recovers from traffic surges"
	@docker run --rm -i --network=host \
		-v $(PWD)/k6:/scripts \
		-e BASE_URL=$(or $(BASE_URL),http://localhost:8080) \
		-e SERVICE_A_URL=$(or $(SERVICE_A_URL),http://localhost:8001) \
		grafana/k6:latest run /scripts/spike-test.js
	@echo ""
	@echo "✅ Spike test complete! Results saved to k6/spike-test-results.json"

# Clean K6 test results
k6-clean:
	@echo "🧹 Cleaning K6 test results..."
	@rm -f k6/summary.json k6/stress-test-results.json k6/spike-test-results.json
	@echo "✅ K6 test results cleaned"

# ==================== Chaos Testing (Pumba) ====================

# Chaos testing help
chaos-help:
	@echo "🌪️  Pumba Chaos Testing Commands:"
	@echo ""
	@echo "  Basic Chaos Tests:"
	@echo "  make chaos-kill-random       - Randomly kill an application service"
	@echo "  make chaos-kill-all          - Kill all application services (loop)"
	@echo "  make chaos-network-delay     - Add network delay to all services"
	@echo "  make chaos-network-loss      - Add network packet loss to all services"
	@echo "  make chaos-network-corrupt   - Add packet corruption to all services"
	@echo "  make chaos-stress-cpu        - CPU stress test on all services"
	@echo ""
	@echo "  Service-Specific Chaos Tests:"
	@echo "  make chaos-kill-gateway      - Kill API Gateway"
	@echo "  make chaos-delay-service-a   - Add delay to Service A"
	@echo "  make chaos-loss-service-b    - Add packet loss to Service B"
	@echo "  make chaos-stress-postgres   - Stress test PostgreSQL"
	@echo "  make chaos-pause-kafka       - Pause Kafka container"
	@echo ""
	@echo "  Complex Scenarios:"
	@echo "  make chaos-microservice-chain - Simulate microservice chain failure"
	@echo "  make chaos-database-outage    - Simulate database outage"
	@echo "  make chaos-network-partition  - Simulate network partition"
	@echo ""
	@echo "  Management Commands:"
	@echo "  make chaos-stop              - Stop all running Pumba containers"
	@echo "  make chaos-clean             - Clean all Pumba containers"
	@echo ""

# Basic chaos test - randomly kill an application service
chaos-kill-random:
	@echo "💥 Randomly killing an application service (every 30 seconds)"
	@docker rm -f pumba-kill-random 2>/dev/null || true
	docker run -d --name pumba-kill-random \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		--interval 30s --random --log-level info \
		kill --signal SIGKILL "re2:^(service-[b-d])$$"
	@echo "✅ Pumba started, use 'make chaos-stop' to stop"

# Kill all application services (loop test)
chaos-kill-all:
	@echo "💥 Killing all application services every 20 seconds"
	@docker rm -f pumba-kill-all 2>/dev/null || true
	docker run -d --name pumba-kill-all \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		--interval 20s --log-level info \
		kill --signal SIGTERM "re2:^(api-gateway|service-[a-d])$$"
	@echo "✅ Pumba started"

# Network delay - add 500ms delay to all application services
chaos-network-delay:
	@echo "🐌 Adding network delay (500ms ± 100ms) to all application services for 5 minutes"
	@docker rm -f pumba-delay 2>/dev/null || true
	docker run -d --name pumba-delay \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		--log-level info \
		netem --duration 5m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
		delay --time 500 --jitter 100 --distribution normal \
		"re2:^(api-gateway|service-[a-d])$$"
	@echo "✅ Network delay applied for 5 minutes"

# Network packet loss - 20% loss rate
chaos-network-loss:
	@echo "📉 Adding 20% network packet loss to all application services for 5 minutes"
	@docker rm -f pumba-loss 2>/dev/null || true
	docker run -d --name pumba-loss \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		--log-level info \
		netem --duration 5m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
		loss --percent 20 \
		"re2:^(api-gateway|service-[a-d])$$"
	@echo "✅ Network packet loss applied for 5 minutes"

# Network packet corruption - 10% corruption rate
chaos-network-corrupt:
	@echo "🔨 Adding 10% network packet corruption to all application services for 5 minutes"
	@docker rm -f pumba-corrupt 2>/dev/null || true
	docker run -d --name pumba-corrupt \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		--log-level info \
		netem --duration 5m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
		corrupt --percent 10 \
		"re2:^(api-gateway|service-[a-d])$$"
	@echo "✅ Network packet corruption applied for 5 minutes"

# CPU stress test
chaos-stress-cpu:
	@echo "💪 Running CPU stress test on all application services for 2 minutes"
	@docker rm -f pumba-stress 2>/dev/null || true
	docker run -d --name pumba-stress \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		--log-level info \
		stress --duration 2m \
		--stressors "--cpu 2 --timeout 120s" \
		"re2:^(api-gateway|service-[a-d])$$"
	@echo "✅ CPU stress test started for 2 minutes"

# ==================== Service-Specific Chaos Tests ====================

# Kill API Gateway
chaos-kill-gateway:
	@echo "💥 Killing API Gateway"
	docker run --rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		kill --signal SIGKILL api-gateway
	@echo "✅ API Gateway killed"

# Add delay to Service A
chaos-delay-service-a:
	@echo "🐌 Adding 1000ms delay to Service A for 3 minutes"
	@docker rm -f pumba-delay-service-a 2>/dev/null || true
	docker run -d --name pumba-delay-service-a \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		netem --duration 3m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
		delay --time 1000 --jitter 200 service-a
	@echo "✅ Service A delay applied"

# Add packet loss to Service B
chaos-loss-service-b:
	@echo "📉 Adding 30% packet loss to Service B for 3 minutes"
	@docker rm -f pumba-loss-service-b 2>/dev/null || true
	docker run -d --name pumba-loss-service-b \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		netem --duration 3m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
		loss --percent 30 service-b
	@echo "✅ Service B packet loss applied"

# Stress test PostgreSQL
chaos-stress-postgres:
	@echo "💪 Running stress test on PostgreSQL for 2 minutes"
	@docker rm -f pumba-stress-postgres 2>/dev/null || true
	docker run -d --name pumba-stress-postgres \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		stress --duration 2m \
		--stressors "--cpu 2 --io 1 --timeout 120s" postgres
	@echo "✅ PostgreSQL stress test started"

# Pause Kafka
chaos-pause-kafka:
	@echo "⏸️  Pausing Kafka container for 30 seconds"
	@docker rm -f pumba-pause-kafka 2>/dev/null || true
	docker run -d --name pumba-pause-kafka \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		pause --duration 30s kafka
	@echo "✅ Kafka paused for 30 seconds"

# ==================== Complex Chaos Scenarios ====================

# Simulate microservice chain failure
chaos-microservice-chain:
	@echo "⛓️  Simulating microservice chain failure:"
	@echo "  - Service A: Network delay 800ms"
	@echo "  - Service B: 15% packet loss"
	@echo "  - Service C: CPU stress"
	@echo "  Duration: 5 minutes"
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
	@echo "✅ Microservice chain chaos test started"

# Simulate database outage
chaos-database-outage:
	@echo "🗄️  Simulating database outage scenario:"
	@echo "  - PostgreSQL: Network delay 2000ms"
	@echo "  - Duration: 3 minutes"
	@docker rm -f pumba-db-outage 2>/dev/null || true
	docker run -d --name pumba-db-outage \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		netem --duration 3m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
		delay --time 2000 --jitter 500 postgres
	@echo "✅ Database outage scenario started"

# Simulate network partition (between Service A and Service B)
chaos-network-partition:
	@echo "🌐 Simulating network partition:"
	@echo "  - Service A: 90% packet loss"
	@echo "  - Service B: 90% packet loss"
	@echo "  - Duration: 2 minutes"
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
	@echo "✅ Network partition scenario started"

# ==================== Management Commands ====================

# Stop all Pumba containers
chaos-stop:
	@echo "🛑 Stopping all running Pumba containers..."
	@docker ps --filter "name=pumba-*" -q | xargs -r docker stop
	@echo "✅ All Pumba containers stopped"

# Clean all Pumba containers
chaos-clean: chaos-stop
	@echo "🧹 Cleaning all Pumba containers..."
	@docker ps -a --filter "name=pumba-*" -q | xargs -r docker rm
	@echo "✅ Pumba containers cleaned"

# View Pumba container status
chaos-status:
	@echo "📊 Pumba Container Status:"
	@docker ps -a --filter "name=pumba-*" --format "table {{.Names}}\t{{.Status}}\t{{.Command}}"

# View specific Pumba container logs
chaos-logs:
	@echo "📋 Select Pumba container to view logs:"
	@docker ps -a --filter "name=pumba-*" --format "{{.Names}}"
	@echo ""
	@echo "Usage: docker logs <container-name>"
