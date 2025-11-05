# OpenTelemetry 混合 Instrumentation 指南

## 🎯 什么是混合 Instrumentation？

混合 Instrumentation 结合了两种方式的优点：

1. **Auto Instrumentation（自动埋点）**
   - 通过 `opentelemetry-instrument` CLI 自动埋点常见库
   - 零代码侵入
   - 自动发现和埋点 FastAPI、httpx、psycopg2 等

2. **Programmatic Instrumentation（编程式埋点）**
   - 在代码中添加自定义 span、attributes、metrics
   - 完全控制业务逻辑的可观测性
   - 添加业务相关的 context

---

## 📊 三种方式对比

| 特性 | 纯手动 | 纯自动 | **混合模式** |
|------|--------|--------|--------------|
| 代码侵入性 | ❌ 高 | ✅ 零 | ✅ 中等 |
| 自定义能力 | ✅ 完全 | ❌ 有限 | ✅ 完全 |
| 维护成本 | ❌ 高 | ✅ 低 | ✅ 中等 |
| 业务 context | ✅ 丰富 | ❌ 基础 | ✅ 丰富 |
| 框架更新 | ❌ 需手动更新 | ✅ 自动支持 | ✅ 自动支持 |

---

## 🔧 实现步骤

### 1. 修改 `requirements.txt`

```txt
# 添加 auto instrumentation 支持
opentelemetry-instrumentation==0.42b0
opentelemetry-distro==0.42b0

# 保留所有 instrumentation libraries
opentelemetry-instrumentation-fastapi==0.42b0
opentelemetry-instrumentation-httpx==0.42b0
opentelemetry-instrumentation-psycopg2==0.42b0
```

### 2. 简化代码

**之前（纯手动）：**
```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

app = FastAPI()

# ❌ 需要手动调用 instrumentor
FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()
Psycopg2Instrumentor().instrument()
```

**现在（混合模式）：**
```python
from opentelemetry import trace, metrics

app = FastAPI()

# ✅ 不需要手动调用 instrumentor
# 由 opentelemetry-instrument 自动处理

# ✅ 只需要添加自定义业务逻辑
tracer = trace.get_tracer(__name__)

@app.get("/process")
async def process():
    # 框架埋点自动完成
    # 自定义业务 span
    with tracer.start_as_current_span("business_logic") as span:
        span.set_attribute("custom.attribute", "value")
        # 业务代码...
```

### 3. 修改 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ 自动发现并安装 instrumentation libraries
RUN opentelemetry-bootstrap -a install

COPY main.py .

EXPOSE 8001

# ✅ 使用 opentelemetry-instrument 启动
CMD ["opentelemetry-instrument", \
     "--traces_exporter", "otlp", \
     "--metrics_exporter", "otlp", \
     "--service_name", "service-a", \
     "python", "main.py"]
```

### 4. 环境变量配置（可选）

```yaml
# docker-compose.yaml
environment:
  # OpenTelemetry 配置
  - OTEL_SERVICE_NAME=service-a
  - OTEL_TRACES_EXPORTER=otlp
  - OTEL_METRICS_EXPORTER=otlp
  - OTEL_LOGS_EXPORTER=otlp
  - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
  - OTEL_EXPORTER_OTLP_INSECURE=true

  # 可选：日志级别
  - OTEL_LOG_LEVEL=info
```

---

## 📝 代码示例

### 完整示例：Service A (Hybrid)

查看 `services/service-a/main_hybrid.py` 了解完整实现。

**关键点：**

1. **自动埋点的部分（无需代码）：**
   ```python
   # FastAPI 框架的 HTTP request/response
   # httpx 的所有 HTTP 调用
   # psycopg2 的所有数据库查询
   ```

2. **自定义埋点的部分：**
   ```python
   # 业务逻辑的 span
   with tracer.start_as_current_span("service_a.business_logic") as span:
       span.set_attribute("trace_id", trace_id)
       span.set_attribute("service.operation", "process")

       # 业务代码...
   ```

3. **自定义 Metrics：**
   ```python
   # 创建自定义 metrics
   process_counter = meter.create_counter(
       name="service_a_process_total",
       description="Total number of process requests"
   )

   # 使用
   process_counter.add(1, {"endpoint": "/process"})
   ```

---

## 🚀 启动方式

### 本地开发

```bash
# 安装依赖
pip install -r requirements_hybrid.txt

# 自动发现 instrumentation
opentelemetry-bootstrap -a install

# 启动（使用 auto instrumentation）
opentelemetry-instrument \
  --traces_exporter otlp \
  --metrics_exporter otlp \
  --service_name service-a-hybrid \
  --exporter_otlp_endpoint http://localhost:4317 \
  python main_hybrid.py
```

### Docker 方式

```bash
# 构建镜像
docker build -f Dockerfile.hybrid -t service-a-hybrid .

# 运行
docker run -p 8001:8001 \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317 \
  service-a-hybrid
```

---

## 🔍 验证效果

### 1. 查看自动埋点的 Span

访问 Tempo，查看一个 trace，你会看到：

```
GET /process                          # FastAPI 自动埋点
├── service_a.business_logic          # 自定义 span
│   ├── service_a.database_business_logic  # 自定义 span
│   │   └── INSERT INTO request_logs  # psycopg2 自动埋点
│   │   └── SELECT COUNT(*)           # psycopg2 自动埋点
│   ├── service_a.external_api_business  # 自定义 span
│   │   └── GET https://api.github.com  # httpx 自动埋点
│   ├── service_a.call_service_d_business  # 自定义 span
│   │   └── GET http://service-d:8004   # httpx 自动埋点
│   └── service_a.call_service_b_business  # 自定义 span
│       └── POST http://service-b:8002  # httpx 自动埋点
```

### 2. 查看自定义 Attributes

在 Tempo 中点击自定义 span，可以看到：

```json
{
  "trace_id": "a7f942bc9960274d835fb00bfc2319ee",
  "service.operation": "process",
  "instrumentation.type": "hybrid",
  "db.log_id": 123,
  "db.recent_requests": 45,
  "response.status": "success"
}
```

### 3. 查看自定义 Metrics

在 Prometheus 中查询：

```promql
# 自定义业务 metrics
service_a_process_total{instrumentation="hybrid"}
service_a_db_query_duration_seconds_bucket
service_a_external_calls_total
```

---

## ✅ 优势总结

### 1. **代码更简洁**
- ❌ 移除了 `FastAPIInstrumentor.instrument_app(app)`
- ❌ 移除了 `HTTPXClientInstrumentor().instrument()`
- ❌ 移除了 `Psycopg2Instrumentor().instrument()`
- ✅ 保留了自定义的 span、attributes、metrics

### 2. **更好的维护性**
- ✅ 框架更新时，auto instrumentation 自动适配
- ✅ 新增依赖库时，`opentelemetry-bootstrap` 自动发现
- ✅ 代码侵入性降低，业务逻辑更清晰

### 3. **最佳的可观测性**
- ✅ 框架层面：自动捕获所有 HTTP、DB 调用
- ✅ 业务层面：自定义 span 提供业务 context
- ✅ 指标层面：自定义 metrics 反映业务状态

---

## 🎓 最佳实践

### 1. 何时使用 Auto Instrumentation？
- ✅ 框架层面的操作（HTTP request/response）
- ✅ 数据库查询
- ✅ HTTP 客户端调用
- ✅ 消息队列操作

### 2. 何时使用 Programmatic Instrumentation？
- ✅ 业务逻辑的关键步骤
- ✅ 自定义 attributes（用户ID、订单号等）
- ✅ 业务 metrics（订单数、支付金额等）
- ✅ 复杂的错误处理

### 3. Span 命名规范
```python
# ✅ 好的命名
"service_a.process_order"
"service_a.validate_payment"
"service_a.send_notification"

# ❌ 不好的命名
"function1"
"do_something"
"process"
```

### 4. Attribute 命名规范
```python
# ✅ 遵循 OpenTelemetry 语义约定
span.set_attribute("http.method", "GET")
span.set_attribute("db.system", "postgresql")
span.set_attribute("service.name", "service-a")

# ✅ 自定义业务 attributes
span.set_attribute("business.order_id", order_id)
span.set_attribute("business.user_id", user_id)
```

---

## 🔗 参考资源

- [OpenTelemetry Python Automatic Instrumentation](https://opentelemetry.io/docs/languages/python/automatic/)
- [OpenTelemetry Python API](https://opentelemetry.io/docs/languages/python/api/)
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)

---

## 🆚 迁移指南

### 从纯手动迁移到混合模式

**步骤 1：更新依赖**
```bash
# 添加到 requirements.txt
opentelemetry-instrumentation
opentelemetry-distro
```

**步骤 2：移除手动 instrumentor 调用**
```python
# ❌ 移除这些
# FastAPIInstrumentor.instrument_app(app)
# HTTPXClientInstrumentor().instrument()
# Psycopg2Instrumentor().instrument()
```

**步骤 3：更新启动命令**
```bash
# 之前
python main.py

# 现在
opentelemetry-instrument python main.py
```

**步骤 4：验证**
- ✅ 查看 Tempo，确认 span 仍然完整
- ✅ 查看 Prometheus，确认 metrics 正常
- ✅ 查看 Loki，确认日志包含 trace_id

---

🎉 **现在你的服务使用混合 Instrumentation，既享受了 auto instrumentation 的便利，又保留了自定义埋点的灵活性！**
