# System Architecture Documentation

## Overall Architecture

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

## Observability Architecture

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

## Data Flow

### 1. Traces Flow

```
Service → OTLP Exporter → Collector → Tempo → Grafana
                                         ↓
                                   Service Graph
                                      Metrics
                                         ↓
                                   Prometheus
```

### 2. Metrics Flow

```
Service → OTLP Exporter → Collector → Prometheus → Grafana
            ↓
     Custom Metrics
    (Counter, Histogram)
```

### 3. Logs Flow

```
Service → Structured Log → OTLP Exporter → Collector → Loki → Grafana
            (JSON)              ↓
                        Contains trace_id
                           span_id
```

## Context Propagation

### HTTP Call Chain

```
API Gateway
    └─ trace_id: abc123
       span_id: 001
           │
           ├─→ Service A
           │    └─ trace_id: abc123 (inherited)
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
                └─ trace_id: abc123 (extracted from headers)
                   span_id: 006
```

### W3C Trace Context Headers

```
traceparent: 00-{trace_id}-{span_id}-{flags}
Example: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01

tracestate: vendor1=value1,vendor2=value2
```

## Correlation Mechanisms

### 1. Logs ↔ Traces

By injecting `trace_id` and `span_id` into logs:

```json
{
  "time": "2024-01-01T12:00:00Z",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "message": "Processing request"
}
```

Configure derived fields in Grafana Loki:
- Extract `trace_id` from logs
- Generate URL to link to Tempo

### 2. Metrics ↔ Traces

Through Exemplars:

```
# Metric with Exemplar
http_request_duration_seconds_bucket{le="0.5"} 100 # {trace_id="abc123"} 0.234
```

In Grafana:
- Prometheus charts display exemplar points
- Click to jump to corresponding trace

### 3. Traces ↔ Metrics

Tempo configured with metrics generator:
- Automatically generate service graph metrics
- Generate span metrics (duration, count)
- Push to Prometheus

## Inter-Service Communication

### Synchronous Calls (HTTP)

```python
# Python example
async with httpx.AsyncClient() as client:
    response = await client.get(url)
    # OpenTelemetry automatically injects traceparent header
```

```go
// Go example
req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
// otelhttp automatically injects header
response, err := otelhttp.DefaultClient.Do(req)
```

### Asynchronous Calls (Kafka)

**Producer (Service B)**:

```go
// Inject trace context into Kafka headers
carrier := &kafkaHeaderCarrier{headers: &msg.Headers}
otel.GetTextMapPropagator().Inject(ctx, carrier)

kafkaWriter.WriteMessages(ctx, msg)
```

**Consumer (Service C)**:

```go
// Extract trace context from Kafka headers
carrier := &kafkaHeaderCarrier{headers: msg.Headers}
ctx = otel.GetTextMapPropagator().Extract(ctx, carrier)

// Continue using extracted context
ctx, span := tracer.Start(ctx, "process_message")
```

## Auto Instrumentation vs Manual Instrumentation

### Auto Instrumentation (Service A, D)

**Advantages**:
- Zero code intrusion
- Quick start
- Automatic coverage for common frameworks and libraries

**Implementation**:
- Python: `opentelemetry-instrumentation-{framework}`
- Automatically intercept HTTP requests/responses
- Automatically intercept database calls
- Automatically inject/extract context

### Manual Instrumentation (Service B, C)

**Advantages**:
- Fine-grained control
- Business metrics
- Custom attributes

**Implementation**:
```go
// Create span
ctx, span := tracer.Start(ctx, "operation_name")
defer span.End()

// Add attributes
span.SetAttributes(
    attribute.String("key", "value"),
)

// Record metrics
counter.Add(ctx, 1, metric.WithAttributes(...))
```

## Data Storage

### PostgreSQL
- Purpose: Business data storage
- Connected by Service A
- Auto-instrumented database operations

### Kafka
- Purpose: Asynchronous message queue
- Service B produces messages
- Service C consumes messages
- Supports trace context propagation

### Tempo
- Purpose: Distributed tracing storage
- Storage format: Parquet
- Query: TraceQL

### Loki
- Purpose: Log aggregation
- Storage: Compressed log streams
- Query: LogQL

### Prometheus
- Purpose: Time-series database
- Storage: TSDB
- Query: PromQL

## Scalability Considerations

### Horizontal Scaling

```
API Gateway (multiple replicas)
    ↓
Load Balancer
    ↓
Service A (multiple replicas)
    ↓
PostgreSQL (primary-replica)
```

### Collector High Availability

```
Services
    ↓
Load Balancer
    ↓
Collector (multiple replicas)
    ↓
Backend Storage
```

### Sampling Strategies

1. **Head-based Sampling** (at service level)
   - Decided based on trace_id
   - Suitable for reducing data volume

2. **Tail-based Sampling** (at Collector)
   - Decided based on entire trace characteristics
   - Preserve errors and slow requests

## Security Considerations

### 1. Sensitive Data Masking

```go
// Do not log sensitive information
span.SetAttributes(
    attribute.String("user.id", userID),
    // ❌ attribute.String("password", password),
    // ❌ attribute.String("credit_card", cc),
)
```

### 2. Network Isolation

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

## Performance Impact

### Instrumentation Overhead

- **Auto instrumentation**: Approximately 1-5% CPU overhead
- **Manual instrumentation**: Approximately 0.5-2% CPU overhead
- **Sampling rate**: Recommend 1-10% for production

### Optimization Recommendations

1. Use Batch Processor
2. Configure reasonable sampling rate
3. Asynchronous data export
4. Limit number of span attributes
5. Use memory limiter

## Fault Isolation

### Circuit Breaker Pattern

```
Service A → (Circuit Breaker) → Service B
              ↓ Too many failures
            Open (reject requests)
              ↓ After timeout
            Half-Open (try)
              ↓ Success
            Closed (normal)
```

### Graceful Degradation

```
Service A
    ├─ Primary: Service B
    └─ Fallback: Cache/Default Value
```

Even if some services fail, traces are still completely recorded.
