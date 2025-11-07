author: Your Name
summary: OpenTelemetry 可观测性实验室完整教程
id: o11y-lab-tutorial
categories: observability,opentelemetry,docker
environments: Web
status: Published
feedback link: https://github.com/yourusername/o11y_lab_for_dummies
analytics account: Google Analytics ID

# OpenTelemetry 可观测性实验室教程

## 课程简介
Duration: 2

### 你将学到什么

在这个实验室中，你将学习如何：

- 搭建完整的可观测性环境（Grafana + Prometheus + Loki + Tempo）
- 使用 Docker Compose 快速部署微服务架构
- 理解 Python 自动埋点（Auto Instrumentation）
- 实践 Python 手动埋点（Manual Instrumentation）
- 使用 K6 生成测试流量
- 使用 Pumba 进行混沌工程（延迟注入）
- 在 Grafana 中关联 Logs、Metrics、Traces

### 前置要求

- 基本的 Linux 命令行知识
- 理解 Docker 基础概念
- Python 或 Go 编程基础

### 实验环境

- Ubuntu/MacOS/Windows (WSL2)
- 至少 8GB RAM
- 20GB 可用磁盘空间

---

## 环境准备 - Docker & Docker Compose
Duration: 10

### 安装 Docker

#### Linux (Ubuntu/Debian)

```bash
# 更新软件包索引
sudo apt-get update

# 安装依赖
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 添加 Docker 官方 GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 设置仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 将当前用户加入 docker 组
sudo usermod -aG docker $USER
newgrp docker
```

#### MacOS

```bash
# 使用 Homebrew 安装
brew install --cask docker

# 或者直接下载 Docker Desktop
# https://www.docker.com/products/docker-desktop/
```

#### Windows

下载并安装 Docker Desktop for Windows:
https://www.docker.com/products/docker-desktop/

### 验证安装

```bash
# 检查 Docker 版本
docker --version
# 应显示: Docker version 24.0.0 或更高

# 检查 Docker Compose
docker compose version
# 应显示: Docker Compose version v2.20.0 或更高

# 测试 Docker 运行
docker run hello-world
```

Positive
: 如果看到 "Hello from Docker!" 消息，说明 Docker 安装成功！

---

## 环境准备 - Python & Go
Duration: 8

### 安装 Python 3.11+

#### Linux (Ubuntu/Debian)

```bash
# 添加 deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update

# 安装 Python 3.11
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev

# 安装 pip
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# 验证安装
python3.11 --version
pip3.11 --version
```

#### MacOS

```bash
brew install python@3.11

# 验证
python3.11 --version
```

#### Windows

下载并安装 Python 3.11:
https://www.python.org/downloads/

### 安装 Go 1.21+

#### Linux

```bash
# 下载 Go
wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz

# 解压到 /usr/local
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz

# 添加到 PATH (加入 ~/.bashrc 或 ~/.zshrc)
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc

# 验证
go version
```

#### MacOS

```bash
brew install go@1.21

# 验证
go version
```

#### Windows

下载并安装 Go:
https://go.dev/dl/

### 安装 K6

K6 是一个现代化的负载测试工具。

#### Linux

```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# 验证
k6 version
```

#### MacOS

```bash
brew install k6

# 验证
k6 version
```

#### 使用 Docker (跨平台)

```bash
docker pull grafana/k6:latest
docker run --rm -i grafana/k6 version
```

Positive
: 所有工具安装完成！现在可以开始实验了。

---

## 克隆项目并启动环境
Duration: 5

### 获取项目代码

```bash
# 克隆仓库
git clone https://github.com/yourusername/o11y_lab_for_dummies.git
cd o11y_lab_for_dummies

# 查看项目结构
ls -la
```

### 启动所有服务

```bash
# 使用 Docker Compose 启动
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志（可选）
docker compose logs -f
```

你应该看到以下服务启动：

- **api-gateway**: Python FastAPI 网关
- **service-a**: Python FastAPI 服务（自动埋点）
- **service-b**: Go 服务（手动埋点）
- **service-c**: Go 服务（手动埋点）
- **service-d**: Python Flask 服务（自动埋点）
- **grafana**: 可视化平台
- **prometheus**: Metrics 存储
- **loki**: 日志存储
- **tempo**: Trace 存储
- **otel-collector**: OpenTelemetry 收集器
- **postgres**: 数据库
- **kafka**: 消息队列

### 等待服务就绪

```bash
# 检查所有容器是否健康
docker compose ps

# 等待约 30-60 秒让所有服务启动完成
```

Positive
: 所有服务启动后，我们就可以访问 Grafana 了！

---

## 访问 Grafana 平台
Duration: 10

### 登录 Grafana

1. 打开浏览器访问: **http://localhost:3000**

2. 使用默认凭证登录:
   - **用户名**: `admin`
   - **密码**: `admin`

3. 首次登录会提示修改密码，可以选择跳过（Skip）

### Grafana 界面介绍

登录后你会看到 Grafana 主界面：

![Grafana Home](assets/images/grafana-home.png)

#### 左侧菜单栏

- **Home**: 主页
- **Dashboards**: 仪表板列表
- **Explore**: 数据探索界面（我们主要使用这个）
- **Alerting**: 告警配置
- **Configuration**: 配置选项

### 查看数据源

1. 点击左侧菜单的齿轮图标 (Configuration)
2. 选择 **Data sources**
3. 你应该看到以下数据源已配置:
   - **Prometheus**: Metrics 数据
   - **Loki**: 日志数据
   - **Tempo**: Trace 数据

![Data Sources](assets/images/grafana-datasources.png)

### 探索预配置的 Dashboard

1. 点击左侧菜单的 Dashboard 图标
2. 你会看到预配置的仪表板:
   - **OpenTelemetry Overview**: 整体概览
   - **Service Performance**: 服务性能监控
   - **Distributed Tracing**: 分布式追踪

![Dashboards](assets/images/grafana-dashboards.png)

Positive
: Grafana 平台已经准备好了！接下来我们将使用 K6 生成流量。

---

## 使用 K6 生成测试流量
Duration: 8

### K6 测试脚本

项目中已经包含了 K6 测试脚本。让我们查看并运行它：

```bash
# 查看 K6 脚本（如果存在）
cat k6/load-test.js
```

如果项目中没有，创建一个简单的 K6 脚本：

```bash
mkdir -p k6
cat > k6/load-test.js << 'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },  // 爬升到 10 个用户
    { duration: '1m', target: 10 },   // 保持 10 个用户
    { duration: '30s', target: 0 },   // 降到 0
  ],
};

export default function () {
  const response = http.get('http://localhost:8080/api/process');

  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
EOF
```

### 运行 K6 测试

```bash
# 运行负载测试
k6 run k6/load-test.js
```

你会看到类似这样的输出：

```
     ✓ status is 200
     ✓ response time < 500ms

     checks.........................: 100.00% ✓ 200  ✗ 0
     data_received..................: 1.2 MB  20 kB/s
     data_sent......................: 24 kB   400 B/s
     http_req_duration..............: avg=125ms min=50ms med=120ms max=300ms
```

### 在 Grafana 中观察流量

1. 在 Grafana 中打开 **Explore**
2. 选择数据源: **Prometheus**
3. 输入查询:
   ```promql
   rate(http_requests_total[1m])
   ```
4. 点击 **Run query**

你应该看到请求速率的图表：

![K6 Traffic](assets/images/k6-traffic.png)

### 持续流量生成（可选）

如果想要持续生成流量用于后续实验：

```bash
# 后台运行 K6
k6 run --duration 30m k6/load-test.js &
```

Positive
: 现在我们有流量数据了！接下来注入一些混沌。

---

## 使用 Pumba 注入延迟
Duration: 10

### 什么是 Pumba？

Pumba 是一个混沌工程工具，可以对 Docker 容器进行各种故障注入：
- 网络延迟
- 网络丢包
- 容器停止/杀死
- 资源限制

### 安装 Pumba

#### Linux

```bash
# 下载 Pumba
curl -L https://github.com/alexei-led/pumba/releases/download/0.9.9/pumba_linux_amd64 -o pumba
chmod +x pumba
sudo mv pumba /usr/local/bin/
```

#### MacOS

```bash
curl -L https://github.com/alexei-led/pumba/releases/download/0.9.9/pumba_darwin_amd64 -o pumba
chmod +x pumba
sudo mv pumba /usr/local/bin/
```

#### 验证安装

```bash
pumba --version
```

### 注入网络延迟到 Service-A

```bash
# 对 service-a 注入 500ms 延迟，持续 2 分钟
pumba netem \
  --duration 2m \
  delay \
  --time 500 \
  o11y_lab_for_dummies-service-a-1
```

参数说明：
- `--duration 2m`: 故障持续 2 分钟
- `delay`: 延迟类型
- `--time 500`: 延迟 500 毫秒
- 最后是容器名称

### 查看容器名称

如果不确定容器名称：

```bash
# 列出所有容器
docker compose ps

# 或者
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### 在 Grafana 中观察延迟影响

1. 在注入延迟的同时，运行 K6 测试:
   ```bash
   k6 run k6/load-test.js
   ```

2. 在 Grafana Explore 中查询:
   ```promql
   histogram_quantile(0.95,
     rate(http_server_duration_milliseconds_bucket[1m])
   )
   ```

3. 你应该看到 service-a 的 P95 延迟从 ~100ms 上升到 ~600ms

![Pumba Delay Effect](assets/images/pumba-delay.png)

### 其他 Pumba 示例

```bash
# 注入随机延迟（100-500ms）
pumba netem --duration 2m delay --time 300 --jitter 200 service-a

# 注入 10% 丢包
pumba netem --duration 2m loss --percent 10 service-a

# 限制带宽到 1Mbps
pumba netem --duration 2m rate --rate 1mbit service-a
```

Negative
: 注意：Pumba 会真实影响服务性能，实验完成后记得停止故障注入！

---

## Python Auto Instrumentation 详解
Duration: 15

### 什么是自动埋点？

自动埋点（Auto Instrumentation）是指**无需修改代码**，通过 OpenTelemetry Agent 或 SDK 自动捕获遥测数据。

### Service-A 的自动埋点配置

查看 Service-A 的 Dockerfile：

```bash
cat services/service-a/Dockerfile
```

你会看到类似这样的配置：

```dockerfile
FROM python:3.11-slim

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 安装 OpenTelemetry 自动埋点包
RUN pip install opentelemetry-distro \
                opentelemetry-exporter-otlp

# 自动检测并安装相关库的埋点
RUN opentelemetry-bootstrap -a install

COPY . /app
WORKDIR /app

# 使用 opentelemetry-instrument 启动应用
CMD ["opentelemetry-instrument", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 关键组件说明

#### 1. `opentelemetry-distro`
OpenTelemetry 的完整发行版，包含所有核心功能。

#### 2. `opentelemetry-bootstrap`
自动检测应用依赖的库，并安装相应的埋点包：
- FastAPI → `opentelemetry-instrumentation-fastapi`
- Requests → `opentelemetry-instrumentation-requests`
- SQLAlchemy → `opentelemetry-instrumentation-sqlalchemy`

#### 3. `opentelemetry-instrument`
启动时的包装器，自动启用所有埋点。

### 环境变量配置

在 `docker-compose.yaml` 中，Service-A 配置了以下环境变量：

```yaml
environment:
  OTEL_SERVICE_NAME: service-a
  OTEL_TRACES_EXPORTER: otlp
  OTEL_METRICS_EXPORTER: otlp
  OTEL_LOGS_EXPORTER: otlp
  OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
  OTEL_EXPORTER_OTLP_PROTOCOL: grpc
  OTEL_RESOURCE_ATTRIBUTES: service.name=service-a,service.version=1.0.0
```

### 查看自动生成的 Traces

1. 触发一个请求:
   ```bash
   curl http://localhost:8080/api/process
   ```

2. 在 Grafana 中:
   - 打开 **Explore**
   - 选择数据源: **Tempo**
   - 选择 **Service**: `service-a`
   - 点击 **Run query**

3. 点击任意 trace，你会看到自动生成的 spans:
   - HTTP 请求 span
   - 数据库查询 span
   - 下游服务调用 span

![Auto Instrumentation Trace](assets/images/auto-trace.png)

### 自动埋点的优势

✅ **零代码侵入**: 不需要修改业务代码
✅ **快速启用**: 几分钟内完成配置
✅ **覆盖广泛**: 自动支持常见框架和库
✅ **标准化**: 遵循 OpenTelemetry 规范

### 自动埋点的局限

❌ **缺乏业务上下文**: 无法捕获业务特定的指标
❌ **精细度有限**: 无法自定义 span 属性
❌ **性能开销**: 可能捕获不必要的信息

Positive
: 自动埋点适合快速开始和通用场景，但复杂业务需要手动埋点！

---

## Python Manual Instrumentation 详解
Duration: 15

### 为什么需要手动埋点？

手动埋点允许你：
- 添加业务特定的 metrics 和 traces
- 自定义 span 属性和事件
- 优化性能（只记录需要的数据）
- 添加业务语义

### Service-D 的手动埋点示例

查看 Service-D 的代码：

```bash
cat services/service-d/app.py
```

#### 1. 初始化 OpenTelemetry

```python
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# 定义服务资源
resource = Resource.create({
    "service.name": "service-d",
    "service.version": "1.0.0",
    "deployment.environment": "production"
})

# 配置 Trace Provider
trace_provider = TracerProvider(resource=resource)
span_processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://otel-collector:4317")
)
trace_provider.add_span_processor(span_processor)
trace.set_tracer_provider(trace_provider)

# 配置 Metrics Provider
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="http://otel-collector:4317")
)
meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[metric_reader]
)
metrics.set_meter_provider(meter_provider)

# 获取 tracer 和 meter
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)
```

#### 2. 创建自定义 Span

```python
from flask import Flask, request
from opentelemetry import trace

app = Flask(__name__)
tracer = trace.get_tracer(__name__)

@app.route('/process')
def process():
    # 创建一个自定义 span
    with tracer.start_as_current_span("business_logic") as span:
        # 添加自定义属性
        span.set_attribute("user.id", request.headers.get("X-User-ID", "anonymous"))
        span.set_attribute("request.size", len(request.data))

        # 添加事件
        span.add_event("Processing started", {
            "items": 10,
            "priority": "high"
        })

        # 业务逻辑
        result = do_business_logic()

        # 添加结果属性
        span.set_attribute("result.count", len(result))

        return result
```

#### 3. 创建自定义 Metrics

```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)

# 创建计数器
request_counter = meter.create_counter(
    name="business.requests.total",
    description="Total number of business requests",
    unit="1"
)

# 创建直方图
processing_time = meter.create_histogram(
    name="business.processing.duration",
    description="Processing duration in milliseconds",
    unit="ms"
)

# 使用 metrics
@app.route('/process')
def process():
    start_time = time.time()

    # 增加计数器
    request_counter.add(1, {"endpoint": "/process", "method": "GET"})

    # 处理请求
    result = do_work()

    # 记录处理时间
    duration = (time.time() - start_time) * 1000
    processing_time.record(duration, {"status": "success"})

    return result
```

#### 4. 结构化日志与 Trace 关联

```python
import logging
from opentelemetry import trace

# 配置 JSON 日志
import json_log_formatter

formatter = json_log_formatter.JSONFormatter()
json_handler = logging.StreamHandler()
json_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(json_handler)
logger.setLevel(logging.INFO)

@app.route('/process')
def process():
    # 获取当前 span context
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, '032x')
    span_id = format(span.get_span_context().span_id, '016x')

    # 记录包含 trace 信息的日志
    logger.info("Processing request", extra={
        "trace_id": trace_id,
        "span_id": span_id,
        "user_id": request.headers.get("X-User-ID"),
        "endpoint": "/process"
    })

    return result
```

### 在 Grafana 中查看手动埋点数据

#### 查看自定义 Span

1. Grafana → Explore → Tempo
2. 搜索 service-d 的 traces
3. 你会看到自定义的 `business_logic` span
4. 点击查看详细属性:
   - `user.id`
   - `request.size`
   - `result.count`

#### 查看自定义 Metrics

1. Grafana → Explore → Prometheus
2. 查询:
   ```promql
   rate(business_requests_total[1m])
   ```
3. 或者:
   ```promql
   histogram_quantile(0.95,
     rate(business_processing_duration_bucket[1m])
   )
   ```

#### 关联日志

1. Grafana → Explore → Loki
2. 查询:
   ```logql
   {service_name="service-d"} | json
   ```
3. 点击任意日志行的 trace_id，直接跳转到对应的 trace

![Manual Instrumentation](assets/images/manual-trace.png)

### 手动埋点最佳实践

1. **有意义的 Span 名称**: 使用业务术语，如 `checkout_cart` 而不是 `process`
2. **添加上下文属性**: 用户ID、订单ID、产品类型等
3. **记录关键事件**: 支付开始、库存检查、第三方调用等
4. **控制基数**: 避免高基数属性（如时间戳、UUID）作为 metric 标签
5. **性能考虑**: 使用采样、避免在热路径创建过多 span

Positive
: 手动埋点给你完全控制权，但需要更多代码和维护工作！

---

## 混合使用 Auto 和 Manual Instrumentation
Duration: 10

### 最佳实践：结合两者

在实际项目中，通常会**混合使用**自动埋点和手动埋点：

```python
# app.py
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from fastapi import FastAPI

app = FastAPI()

# 1. 启用自动埋点（框架级别）
FastAPIInstrumentor.instrument_app(app)

# 2. 获取 tracer 用于手动埋点（业务级别）
tracer = trace.get_tracer(__name__)

@app.get("/checkout")
async def checkout(cart_id: str):
    # 自动埋点已经创建了 HTTP span

    # 添加业务级别的 span
    with tracer.start_as_current_span("validate_cart") as span:
        span.set_attribute("cart.id", cart_id)
        cart = await validate_cart(cart_id)

    with tracer.start_as_current_span("calculate_total") as span:
        total = calculate_total(cart)
        span.set_attribute("cart.total", total)

    with tracer.start_as_current_span("process_payment") as span:
        span.set_attribute("payment.method", "credit_card")
        result = await process_payment(total)

    return result
```

### 在 Grafana 中查看混合埋点

生成的 trace 会显示：
```
HTTP POST /checkout (auto)              [200ms]
├─ validate_cart (manual)               [50ms]
│  └─ SELECT FROM carts (auto)          [20ms]
├─ calculate_total (manual)             [30ms]
└─ process_payment (manual)             [120ms]
   └─ HTTP POST /api/charge (auto)      [100ms]
```

### 决策树：何时使用哪种方式？

```
是否是标准框架/库（HTTP、DB、消息队列）？
├─ 是 → 使用自动埋点
└─ 否 → 是否是业务核心逻辑？
   ├─ 是 → 使用手动埋点
   └─ 否 → 可能不需要埋点
```

Positive
: 自动埋点打基础，手动埋点加深度！

---

## Grafana 高级功能：关联 Logs-Traces-Metrics
Duration: 12

### Trace to Logs

在查看 trace 时，直接跳转到相关日志：

1. 在 Tempo 中打开一个 trace
2. 点击任意 span
3. 在右侧面板找到 **Logs for this span**
4. 点击后自动跳转到 Loki，显示该 span 的日志

### Logs to Traces

从日志跳转到 trace：

1. 在 Loki 中查询:
   ```logql
   {service_name="service-a"} | json
   ```
2. 在日志行中找到 `trace_id` 字段
3. 点击 trace_id 旁的图标，跳转到 Tempo

### Metrics to Traces

从 metrics 告警定位到具体请求：

1. 在 Prometheus 中发现异常:
   ```promql
   rate(http_requests_total{status="500"}[1m]) > 0
   ```
2. 记下时间范围和服务名称
3. 在 Tempo 中按时间和服务搜索 traces
4. 找到失败的请求，查看详细信息

### 创建关联 Dashboard

创建一个包含三者的 dashboard：

```json
{
  "dashboard": {
    "title": "Service Overview",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Recent Traces",
        "type": "traces",
        "datasource": "Tempo"
      },
      {
        "title": "Error Logs",
        "type": "logs",
        "datasource": "Loki",
        "targets": [
          {
            "expr": "{service_name=\"service-a\"} |= \"ERROR\""
          }
        ]
      }
    ]
  }
}
```

![Correlated Dashboard](assets/images/correlated-dashboard.png)

Positive
: 三大支柱的关联是可观测性的精髓！

---

## 实战演练：完整调试流程
Duration: 15

让我们通过一个完整的场景来演练：

### 场景：发现并定位性能问题

#### 步骤 1: 注入延迟

```bash
# 对 service-b 注入 1 秒延迟
pumba netem --duration 5m delay --time 1000 o11y_lab_for_dummies-service-b-1
```

#### 步骤 2: 生成流量

```bash
# 运行 K6 测试
k6 run k6/load-test.js
```

#### 步骤 3: 在 Prometheus 发现问题

1. Grafana → Explore → Prometheus
2. 查询:
   ```promql
   histogram_quantile(0.95,
     rate(http_server_duration_milliseconds_bucket[1m])
   )
   ```
3. 发现 P95 延迟从 100ms 跳到 1100ms

#### 步骤 4: 在 Tempo 定位慢请求

1. 切换到 Tempo
2. 设置过滤:
   - Service: `service-b`
   - Min Duration: `1s`
3. 找到慢 trace，查看详情

#### 步骤 5: 在 Loki 查看相关日志

1. 在 trace 详情中点击 "Logs for this span"
2. 或者手动查询:
   ```logql
   {service_name="service-b"}
   | json
   | trace_id="<your-trace-id>"
   ```
3. 查看错误日志和上下文

#### 步骤 6: 根因分析

通过 trace waterfall 图，你会看到：
- service-b 的某个内部操作耗时 1000ms
- 这正是我们注入的延迟

#### 步骤 7: 验证修复（移除延迟）

```bash
# Pumba 注入会自动过期，或手动重启容器
docker compose restart service-b
```

再次运行 K6，确认延迟恢复正常。

### 总结工作流

```
Metrics (发现异常)
  → Traces (定位具体请求)
    → Logs (查看详细上下文)
      → 根因分析
        → 修复验证
```

Positive
: 这就是现代可观测性的威力！

---

## 清理和后续学习
Duration: 5

### 停止所有服务

```bash
# 停止并删除所有容器
docker compose down

# 同时删除 volumes（清理数据）
docker compose down -v
```

### 后续学习资源

#### 官方文档
- [OpenTelemetry 文档](https://opentelemetry.io/docs/)
- [Grafana 文档](https://grafana.com/docs/)
- [Prometheus 文档](https://prometheus.io/docs/)

#### 进阶主题
- **采样策略**: 减少数据量，控制成本
- **尾部采样**: 只保留有价值的 traces
- **告警配置**: 基于 metrics 设置告警规则
- **SLO/SLI**: 服务水平目标和指标
- **分布式追踪的高级模式**: Baggage、Context Propagation

#### 社区资源
- [OpenTelemetry GitHub](https://github.com/open-telemetry)
- [CNCF Slack](https://slack.cncf.io/) - #opentelemetry 频道
- [Grafana Community](https://community.grafana.com/)

### 你学到了什么

恭喜！你已经完成了整个实验室。你现在掌握了：

✅ 搭建完整的可观测性栈
✅ Docker Compose 部署微服务
✅ Python 自动和手动埋点
✅ K6 负载测试
✅ Pumba 混沌工程
✅ Grafana 三大支柱关联
✅ 完整的问题定位流程

### 下一步

- 尝试在自己的项目中应用这些技术
- 探索 Go 服务的手动埋点（service-b/c）
- 配置自定义告警规则
- 实验不同的采样策略

Positive
: 感谢完成本教程！可观测性之旅才刚刚开始！
