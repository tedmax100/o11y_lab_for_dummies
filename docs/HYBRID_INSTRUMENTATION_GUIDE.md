# OpenTelemetry Python 混合 Instrumentation 配置指南

## 什么是混合模式？

混合模式结合了 **Auto Instrumentation（自动插桩）** 和 **Manual Instrumentation（手动插桩）**：

- **Auto Instrumentation**: 使用 `opentelemetry-instrument` 命令启动，自动为框架和库添加遥测
- **Manual Instrumentation**: 在代码中手动创建 span、metrics 和配置 providers

## Service-A 的混合模式架构

### 1. Auto Instrumentation 负责（通过 opentelemetry-instrument）

```bash
CMD ["opentelemetry-instrument", "python", "main.py"]
```

**自动插桩的组件**：
- ✅ **TracerProvider**: 自动创建并配置
- ✅ **MeterProvider**: 自动创建并配置
- ✅ **FastAPI**: HTTP 请求/响应自动追踪
- ✅ **httpx**: HTTP 客户端调用自动追踪
- ✅ **psycopg2**: 数据库查询自动追踪

### 2. Manual Instrumentation 负责（代码中手动配置）

```python
# 手动配置的组件
- LoggerProvider: 需要手动创建和配置
- 自定义业务 span
- 自定义 metrics
- 自定义 attributes
```

---

## 关键配置决策

### ❌ 不要同时启用自动和手动日志配置

**问题环境变量**:
```bash
# ❌ 错误：会导致冲突
OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
```

**为什么会冲突？**
- 当设置为 `true` 时，`opentelemetry-instrument` 会自动将 OTLP handler 附加到 root logger
- 但你的代码中也手动创建了 LoggerProvider 并添加了 LoggingHandler
- 结果：两个 handler 争夺控制权，导致日志无法正确发送

**✅ 正确做法**：
```bash
# 注释掉或删除这个环境变量
# OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
```

然后在代码中完全手动控制日志配置。

---

## 完整的环境变量配置

### docker-compose.yaml 中的配置

```yaml
services:
  service-a:
    environment:
      # ============ 应用配置 ============
      - SERVICE_B_URL=http://service-b:8002
      - DB_HOST=postgres

      # ============ OpenTelemetry 基础配置 ============
      - OTEL_SERVICE_NAME=service-a-hybrid
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
      - OTEL_EXPORTER_OTLP_INSECURE=true

      # ============ 信号配置 ============
      - OTEL_TRACES_EXPORTER=otlp    # ✅ Auto instrumentation 处理
      - OTEL_METRICS_EXPORTER=otlp   # ✅ Auto instrumentation 处理
      - OTEL_LOGS_EXPORTER=otlp      # ✅ 告诉 SDK 使用 OTLP，但不自动配置

      # ============ 重要：不要启用自动日志配置 ============
      # ❌ 注释掉以避免冲突
      # - OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true

      # ============ Resource Attributes ============
      - OTEL_RESOURCE_ATTRIBUTES=service.namespace=o11y-lab,deployment.environment=lab,instrumentation.type=hybrid
```

---

## 代码中的正确配置模式

### 1. 日志配置（完全手动）

```python
import logging
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

# Step 1: 配置基础 logging（输出到控制台）
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s", "level":"%(levelname)s", "service":"service-a-hybrid", "trace_id":"%(otelTraceID)s", "span_id":"%(otelSpanID)s", "message":"%(message)s"}',
    handlers=[
        logging.StreamHandler()  # 确保日志输出到控制台
    ]
)

# Step 2: 创建 LoggerProvider
resource = Resource.create({
    SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "service-a-hybrid")
})
logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)

# Step 3: 添加 OTLP Exporter
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(
        OTLPLogExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
            insecure=True
        )
    )
)

# Step 4: 将 LoggingHandler 附加到 root logger
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
```

### 2. Traces 和 Metrics（使用 Auto 创建的 Provider）

```python
from opentelemetry import trace, metrics

# 获取由 opentelemetry-instrument 自动创建的 provider
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# 创建自定义 metrics
process_counter = meter.create_counter(
    name="service_a_process_total",
    description="Total number of process requests",
    unit="1"
)

# 创建自定义 span
with tracer.start_as_current_span("my_business_logic") as span:
    span.set_attribute("custom.attribute", "value")
    # 你的业务逻辑
```

---

## 为什么这样设计？

### Auto Instrumentation 的优势
1. **零代码修改**: 自动为框架（FastAPI、httpx、psycopg2）添加插桩
2. **标准化**: 使用 OpenTelemetry 的标准语义约定
3. **维护简单**: 框架更新时自动获得新功能

### Manual Instrumentation 的必要性
1. **日志配置**: Python 的日志系统需要手动连接到 OTLP
2. **业务逻辑**: 添加特定于业务的 span 和 attributes
3. **自定义 metrics**: 创建业务级别的指标

---

## 环境变量参考

### 基础配置
| 变量 | 用途 | 示例 |
|------|------|------|
| `OTEL_SERVICE_NAME` | 服务名称 | `service-a-hybrid` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Collector 地址 | `http://otel-collector:4317` |
| `OTEL_EXPORTER_OTLP_INSECURE` | 是否使用非加密连接 | `true` |

### 信号配置
| 变量 | 用途 | 推荐值 |
|------|------|--------|
| `OTEL_TRACES_EXPORTER` | Traces 导出器 | `otlp` |
| `OTEL_METRICS_EXPORTER` | Metrics 导出器 | `otlp` |
| `OTEL_LOGS_EXPORTER` | Logs 导出器 | `otlp` |

### Python 特定配置
| 变量 | 用途 | 混合模式建议 |
|------|------|-------------|
| `OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED` | 自动配置日志 | ❌ **不要设置**（手动配置） |
| `OTEL_PYTHON_LOG_CORRELATION` | 日志关联 trace context | `true` |
| `OTEL_PYTHON_DISABLED_INSTRUMENTATIONS` | 禁用特定插桩 | `redis,kafka` |
| `OTEL_PYTHON_EXCLUDED_URLS` | 排除特定 URL | `healthcheck,metrics` |

---

## 诊断问题的方法

### 1. 检查日志是否发送到 OTel Collector

```bash
# 查看 service-a 的日志
docker logs service-a 2>&1 | grep "service-a-hybrid"

# 查看 OTel Collector 是否收到日志
docker logs otel-collector 2>&1 | grep "service-a-hybrid"
```

### 2. 检查环境变量

```bash
docker exec service-a env | grep OTEL
```

### 3. 验证 Loki 配置

```bash
# 查看 Loki 是否启用了 OTLP
curl http://localhost:3100/ready

# 查询 service-a 的日志
curl 'http://localhost:3100/loki/api/v1/query' \
  --data-urlencode 'query={service_name="service-a-hybrid"}' \
  --data-urlencode 'limit=10'
```

---

## 最佳实践

### ✅ 推荐做法

1. **清晰分工**：
   - Auto instrumentation 负责框架和库
   - Manual instrumentation 负责业务逻辑和日志

2. **避免重复配置**：
   - 不要同时使用 `OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true` 和手动 LoggerProvider

3. **统一 Resource**：
   - 手动创建的 LoggerProvider 应该使用与 auto instrumentation 相同的 resource attributes

4. **日志格式**：
   - 使用结构化日志（JSON）
   - 包含 trace_id 和 span_id 以便关联

### ❌ 避免的做法

1. **不要混合日志配置方式**
2. **不要忘记配置 StreamHandler**（否则日志只发送到 OTLP，控制台看不到）
3. **不要在混合模式下重新创建 TracerProvider**（会覆盖 auto instrumentation）

---

## 常见问题

### Q1: 为什么日志没有出现在 Loki？
**A**: 检查：
1. `OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED` 是否被注释掉
2. 代码中是否正确配置了 LoggerProvider
3. Loki 是否启用了 OTLP 接收（需要配置 `distributor.otlp_config`）

### Q2: 可以完全使用 Auto Instrumentation 吗？
**A**:
- ✅ **Traces 和 Metrics**: 可以完全自动
- ❌ **Logs**: Python 需要手动配置才能发送到 OTLP

### Q3: 什么时候需要手动 instrumentation？
**A**:
- 添加业务特定的 span
- 创建自定义 metrics
- 配置日志发送到 OTLP
- 添加自定义 attributes

### Q4: 如何验证 Auto Instrumentation 工作？
**A**:
```bash
# 查看启动日志，应该看到类似输出：
# "Instrumenting fastapi"
# "Instrumenting httpx"
# "Instrumenting psycopg2"
docker logs service-a 2>&1 | grep -i "instrumenting"
```

---

## 参考资源

- [OpenTelemetry Python Auto-Instrumentation](https://opentelemetry.io/docs/zero-code/python/)
- [OpenTelemetry Python Configuration](https://opentelemetry.io/docs/zero-code/python/configuration/)
- [Python SDK Documentation](https://opentelemetry-python.readthedocs.io/)
