# 系统架构说明

## 总体架构

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│                    (Python/FastAPI)                          │
│                 Auto Instrumentation                         │
└──────┬──────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service A                               │
│                    (Python/FastAPI)                          │
│                 Auto Instrumentation                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │Service D │  │Service B │  │3rd Party │   │
│  │  Query   │  │   Call   │  │   Call   │  │API Call  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────┬────────────────┬────────────────┬─────────────────────┘
       │                │                │
       ▼                ▼                ▼
  ┌─────────┐    ┌──────────┐    ┌──────────┐
  │PostgreSQL   │ Service D│    │Service B │
  │         │    │ (Python/ │    │(Go/Gin)  │
  │         │    │  Flask)  │    │Manual    │
  └─────────┘    │   Auto   │    │Instrument│
                 │Instrument│    └────┬─────┘
                 └──────────┘         │
                                      ▼
                                 ┌─────────┐
                                 │  Kafka  │
                                 │  Queue  │
                                 └────┬────┘
                                      │
                                      ▼
                                 ┌──────────┐
                                 │Service C │
                                 │(Go/Gin)  │
                                 │Manual    │
                                 │Instrument│
                                 └──────────┘
```

## 可观测性架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Services                      │
│  API Gateway │ Service A │ Service B │ Service C │ Service D│
└──────────────────────┬──────────────────────────────────────┘
                       │ OTLP (gRPC/HTTP)
                       │ - Traces
                       │ - Metrics
                       │ - Logs
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            OpenTelemetry Collector                           │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐                │
│  │Receivers │→ │Processors │→ │Exporters │                │
│  └──────────┘  └───────────┘  └──────────┘                │
│       │              │               │                       │
│     OTLP          Batch          OTLP/Prom/Loki            │
└───────┼──────────────┼───────────────┼──────────────────────┘
        │              │               │
        ▼              ▼               ▼
  ┌─────────┐   ┌───────────┐   ┌─────────┐
  │  Tempo  │   │Prometheus │   │  Loki   │
  │(Traces) │   │ (Metrics) │   │ (Logs)  │
  └────┬────┘   └─────┬─────┘   └────┬────┘
       │              │               │
       └──────────────┼───────────────┘
                      ▼
              ┌──────────────┐
              │   Grafana    │
              │  Dashboard   │
              └──────────────┘
```

## 数据流

### 1. Traces 流

```
Service → OTLP Exporter → Collector → Tempo → Grafana
                                         ↓
                                   Service Graph
                                      Metrics
                                         ↓
                                   Prometheus
```

### 2. Metrics 流

```
Service → OTLP Exporter → Collector → Prometheus → Grafana
            ↓
     Custom Metrics
    (Counter, Histogram)
```

### 3. Logs 流

```
Service → Structured Log → OTLP Exporter → Collector → Loki → Grafana
            (JSON)              ↓
                        含 trace_id
                          span_id
```

## Context Propagation

### HTTP 调用链

```
API Gateway
    └─ trace_id: abc123
       span_id: 001
           │
           ├─→ Service A
           │    └─ trace_id: abc123 (继承)
           │       span_id: 002
           │           │
           │           ├─→ Service D
           │           │    └─ trace_id: abc123
           │           │       span_id: 003
           │           │
           │           ├─→ Service B
           │           │    └─ trace_id: abc123
           │           │       span_id: 004
           │           │           │
           │           │           └─→ Kafka Message
           │           │                Headers: traceparent
           │           │
           │           └─→ Database
           │                └─ trace_id: abc123
           │                   span_id: 005
           │
           └─→ Kafka Consumer (Service C)
                └─ trace_id: abc123 (从 headers 提取)
                   span_id: 006
```

### W3C Trace Context Headers

```
traceparent: 00-{trace_id}-{span_id}-{flags}
示例: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01

tracestate: vendor1=value1,vendor2=value2
```

## 关联机制

### 1. Logs ↔ Traces

通过在日志中注入 `trace_id` 和 `span_id`:

```json
{
  "time": "2024-01-01T12:00:00Z",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "message": "Processing request"
}
```

在 Grafana Loki 中配置 derived fields:
- 从日志中提取 `trace_id`
- 生成链接到 Tempo 的 URL

### 2. Metrics ↔ Traces

通过 Exemplars:

```
# Metric with Exemplar
http_request_duration_seconds_bucket{le="0.5"} 100 # {trace_id="abc123"} 0.234
```

在 Grafana 中:
- Prometheus 图表显示 exemplar 点
- 点击可跳转到对应的 trace

### 3. Traces ↔ Metrics

Tempo 配置了 metrics generator:
- 自动生成 service graph metrics
- 生成 span metrics (duration, count)
- 推送到 Prometheus

## 服务间通信

### 同步调用 (HTTP)

```python
# Python 示例
async with httpx.AsyncClient() as client:
    response = await client.get(url)
    # OpenTelemetry 自动注入 traceparent header
```

```go
// Go 示例
req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
// 使用 otelhttp 自动注入 header
response, err := otelhttp.DefaultClient.Do(req)
```

### 异步调用 (Kafka)

**生产者 (Service B)**:

```go
// 注入 trace context 到 Kafka headers
carrier := &kafkaHeaderCarrier{headers: &msg.Headers}
otel.GetTextMapPropagator().Inject(ctx, carrier)

kafkaWriter.WriteMessages(ctx, msg)
```

**消费者 (Service C)**:

```go
// 从 Kafka headers 提取 trace context
carrier := &kafkaHeaderCarrier{headers: msg.Headers}
ctx = otel.GetTextMapPropagator().Extract(ctx, carrier)

// 继续使用提取的 context
ctx, span := tracer.Start(ctx, "process_message")
```

## 自动埋点 vs 手动埋点

### 自动埋点 (Service A, D)

**优点**:
- 零代码侵入
- 快速开始
- 自动覆盖常见框架和库

**实现**:
- Python: `opentelemetry-instrumentation-{framework}`
- 自动拦截 HTTP 请求/响应
- 自动拦截数据库调用
- 自动注入/提取 context

### 手动埋点 (Service B, C)

**优点**:
- 精细控制
- 业务指标
- 自定义 attributes

**实现**:
```go
// 创建 span
ctx, span := tracer.Start(ctx, "operation_name")
defer span.End()

// 添加 attributes
span.SetAttributes(
    attribute.String("key", "value"),
)

// 记录 metrics
counter.Add(ctx, 1, metric.WithAttributes(...))
```

## 数据存储

### PostgreSQL
- 用途: 业务数据存储
- Service A 连接
- 自动埋点数据库操作

### Kafka
- 用途: 异步消息队列
- Service B 生产消息
- Service C 消费消息
- 支持 trace context 传播

### Tempo
- 用途: 分布式追踪存储
- 存储格式: Parquet
- 查询: TraceQL

### Loki
- 用途: 日志聚合
- 存储: 压缩的日志流
- 查询: LogQL

### Prometheus
- 用途: 时序数据库
- 存储: TSDB
- 查询: PromQL

## 扩展性考虑

### 水平扩展

```
API Gateway (多副本)
    ↓
Load Balancer
    ↓
Service A (多副本)
    ↓
PostgreSQL (主从)
```

### Collector 高可用

```
Services
    ↓
Load Balancer
    ↓
Collector (多副本)
    ↓
Backend Storage
```

### 采样策略

1. **Head-based Sampling** (在服务端)
   - 根据 trace_id 决定
   - 适合降低数据量

2. **Tail-based Sampling** (在 Collector)
   - 根据整个 trace 特征决定
   - 保留错误和慢请求

## 安全考虑

### 1. 敏感数据脱敏

```go
// 不要记录敏感信息
span.SetAttributes(
    attribute.String("user.id", userID),
    // ❌ attribute.String("password", password),
    // ❌ attribute.String("credit_card", cc),
)
```

### 2. 网络隔离

```
┌─────────────────────────────────────┐
│  Application Network                │
│  - Services                         │
│  - Collector                        │
└──────────────┬──────────────────────┘
               │ Controlled Access
               ▼
┌─────────────────────────────────────┐
│  Observability Network              │
│  - Tempo                            │
│  - Loki                             │
│  - Prometheus                       │
│  - Grafana                          │
└─────────────────────────────────────┘
```

## 性能影响

### Instrumentation 开销

- **自动埋点**: 约 1-5% CPU 开销
- **手动埋点**: 约 0.5-2% CPU 开销
- **采样率**: 建议生产环境 1-10%

### 优化建议

1. 使用 Batch Processor
2. 配置合理的采样率
3. 异步导出数据
4. 限制 span attributes 数量
5. 使用 memory limiter

## 故障隔离

### Circuit Breaker 模式

```
Service A → (Circuit Breaker) → Service B
              ↓ 失败次数过多
            Open (拒绝请求)
              ↓ 超时后
            Half-Open (尝试)
              ↓ 成功
            Closed (正常)
```

### Graceful Degradation

```
Service A
    ├─ Primary: Service B
    └─ Fallback: Cache/Default Value
```

即使某些服务失败，trace 仍然完整记录。
