# Final Observability Configuration Summary

## 🎯 Current Configuration Status

### ✅ Span Metrics Configuration

**Single Source**: OTel Collector spanmetrics connector

```yaml
# otel-collector/config.yaml
connectors:
  spanmetrics:
    histogram:
      explicit:
        buckets: [1ms, 5ms, 10ms, 100ms, 250ms, 500ms, 1s, 5s]
    exemplars:
      enabled: true  # Includes trace_id
```

**Metrics Name**: `otel_traces_span_metrics_*`
**Exemplar Label**: `trace_id` (underscore format)

### ✅ Service Graphs Configuration

**Source**: Tempo metrics generator

```yaml
# grafana/tempo-config.yaml
metrics_generator:
  registry:
    external_labels:
      source: tempo
      cluster: o11y-lab
  storage:
    remote_write:
      - url: http://prometheus:9090/api/v1/write
        send_exemplars: true

overrides:
  metrics_generator_processors: [service-graphs]  # Only keep service-graphs
```

**Metrics Name**: `traces_service_graph_*`

## 📊 Available Metrics

### 1. Span Metrics (from OTel Collector)

For monitoring individual service performance:

```promql
# Request rate
rate(otel_traces_span_metrics_duration_count{service_name="service-a-hybrid"}[5m])

# Latency distribution (P95)
histogram_quantile(0.95,
  rate(otel_traces_span_metrics_duration_bucket{service_name="service-a-hybrid"}[5m])
)

# Error rate
rate(otel_traces_span_metrics_duration_count{
  service_name="service-a-hybrid",
  status_code="STATUS_CODE_ERROR"
}[5m])
```

**Features**:
- ✅ Includes exemplars (trace_id)
- ✅ Clickable to jump to Tempo trace
- ✅ Detailed dimensions (span_name, span_kind, http_method, http_status_code)
- ✅ Custom buckets

### 2. Service Graph Metrics (from Tempo)

For monitoring inter-service call relationships:

```promql
# Service-to-service call count
traces_service_graph_request_total{
  client="service-a-hybrid",
  server="service-b"
}

# Service-to-service call latency
histogram_quantile(0.95,
  rate(traces_service_graph_request_server_seconds_bucket{
    client="service-a-hybrid",
    server="service-b"
  }[5m])
)

# Service-to-service call failures
traces_service_graph_request_failed_total{
  client="service-a-hybrid",
  server="service-b"
}
```

**Features**:
- ✅ Shows service dependencies
- ✅ Client and Server perspective latency
- ✅ Failed request statistics
- ✅ Auto-generated service topology

## 🔗 Three Pillars Correlation

### Metrics → Traces (Exemplars) ✅

```yaml
# grafana/datasources/datasources.yaml
datasources:
  - name: Prometheus
    jsonData:
      exemplarTraceIdDestinations:
        - name: trace_id
          datasourceUid: tempo
```

**Usage**:
1. Query span metrics in Grafana
2. Chart displays exemplar points (⚫)
3. Click exemplar → Jump to Tempo trace

### Traces → Logs ✅

```yaml
# Tempo datasource
tracesToLogsV2:
  datasourceUid: loki
  tags: ['service_name']
  filterByTraceID: true
  query: '{service_name="${__span.tags["service.name"]}"} |="${__span.traceId}"'
```

**Usage**:
1. View trace in Tempo
2. Click "Logs" button next to span
3. Auto-jump to Loki showing related logs

### Logs → Traces ✅

```yaml
# Loki datasource
derivedFields:
  - datasourceUid: tempo
    name: TraceID
    matcherRegex: 'trace_id'
    matcherType: label
```

**Usage**:
1. View logs in Loki
2. Log line contains trace_id label
3. Click trace_id → Jump to Tempo trace

### Traces → Metrics ✅

```yaml
# Tempo datasource
tracesToMetrics:
  datasourceUid: prometheus
  queries:
    - name: 'Request Rate'
      query: 'rate(duration_count{$$__tags}[5m])'
```

**Usage**:
1. View trace in Tempo
2. Switch to "Metrics" tab
3. View related span metrics

## 📈 Recommended Grafana Queries

### Service-A Performance Overview

```promql
# Request rate
sum(rate(otel_traces_span_metrics_duration_count{
  service_name="service-a-hybrid",
  span_kind="SPAN_KIND_SERVER"
}[5m])) by (span_name)

# P50, P90, P95, P99 latency
histogram_quantile(0.50, sum(rate(otel_traces_span_metrics_duration_bucket{
  service_name="service-a-hybrid",
  span_kind="SPAN_KIND_SERVER"
}[5m])) by (le, span_name))

# Error rate
sum(rate(otel_traces_span_metrics_duration_count{
  service_name="service-a-hybrid",
  status_code="STATUS_CODE_ERROR"
}[5m])) / sum(rate(otel_traces_span_metrics_duration_count{
  service_name="service-a-hybrid"
}[5m]))
```

### Service Dependency Graph

```promql
# Service-A downstream services
traces_service_graph_request_total{client="service-a-hybrid"}

# Service-A upstream services
traces_service_graph_request_total{server="service-a-hybrid"}

# Service-A → Service-B call latency
histogram_quantile(0.95, rate(traces_service_graph_request_server_seconds_bucket{
  client="service-a-hybrid",
  server="service-b"
}[5m]))
```

## 🔧 Configuration File Locations

| Configuration | File Path |
|---------------|-----------|
| OTel Collector spanmetrics | `otel-collector/config.yaml` |
| Tempo metrics generator | `grafana/tempo-config.yaml` |
| Grafana datasources | `grafana/datasources/datasources.yaml` |
| Prometheus config | `grafana/prometheus.yaml` |
| Loki config | `grafana/loki-config.yaml` |

## 📝 Key Configuration Summary

### OTel Collector Pipelines

```yaml
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, resourcedetection, resource, batch]
      exporters: [otlp/tempo, spanmetrics, debug]  # Send to Tempo and spanmetrics

    metrics:
      receivers: [otlp, prometheus, spanmetrics]    # Receive from spanmetrics
      processors: [memory_limiter, resourcedetection, resource, batch]
      exporters: [prometheus, otlphttp/prometheus, debug]

    logs:
      receivers: [otlp]
      processors: [memory_limiter, resourcedetection, resource, batch]
      exporters: [otlphttp/loki, debug/logs]
```

### Prometheus Scrape Configuration

```yaml
scrape_configs:
  # OTel Collector internal metrics
  - job_name: 'otel-collector'
    static_configs:
      - targets: ['otel-collector:8888']

  # OTel Collector application metrics (includes exemplars)
  - job_name: 'otel-collector-metrics'
    scrape_interval: 15s
    static_configs:
      - targets: ['otel-collector:8889']
```

## 🎨 Grafana Service Graph

Tempo's service-graphs can be visualized in Grafana:

1. **Open Grafana**: http://localhost:3000
2. **Explore → Tempo**
3. **Switch to "Service Graph" tab**
4. **View service dependency topology**

Service Graph displays:
- 🔵 Service nodes
- ➡️ Call relationships
- 📊 Request rate
- ⏱️ Latency
- ❌ Error rate

## 🧪 Verify Configuration

### 1. Verify Span Metrics

```bash
# Query OTel Collector span metrics
curl -s -G 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=otel_traces_span_metrics_duration_count{service_name="service-a-hybrid"}' \
  | python3 -m json.tool
```

### 2. Verify Service Graphs

```bash
# Query Tempo service graph metrics
curl -s -G 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=traces_service_graph_request_total{client="service-a-hybrid"}' \
  | python3 -m json.tool
```

### 3. Verify Exemplars

```bash
# Query exemplars
curl -s -G 'http://localhost:9090/api/v1/query_exemplars' \
  --data-urlencode 'query=otel_traces_span_metrics_duration_bucket{service_name="service-a-hybrid"}' \
  --data-urlencode 'start=2025-01-01T00:00:00Z' \
  --data-urlencode 'end=2025-12-31T23:59:59Z' \
  | python3 -m json.tool | grep "trace_id"
```

## 🎉 Configuration Advantages

### Why Choose This Configuration?

1. **Clear Division of Responsibilities**:
   - OTel Collector: Unified processing of all telemetry data + generate span metrics
   - Tempo: Store traces + generate service graphs

2. **Avoid Duplication**:
   - Only one span metrics source
   - No duplicate data storage

3. **Maximize Functionality**:
   - ✅ Span metrics with exemplars (OTel Collector)
   - ✅ Service dependency graphs (Tempo)
   - ✅ Complete three pillars correlation

4. **Flexibility**:
   - OTel Collector can customize buckets
   - Can add more dimensions
   - Easy to extend and modify

## 🚀 Next Steps

### Recommended Grafana Dashboards

1. **RED Metrics Dashboard** (Rate, Errors, Duration)
   - Use `otel_traces_span_metrics_*`
   - Group by service, endpoint, method

2. **Service Map Dashboard**
   - Use `traces_service_graph_*`
   - Visualize service dependencies

3. **SLO Dashboard**
   - Calculate SLI based on span metrics
   - Set SLO targets and alerts

### Recommended Alert Rules

```yaml
# High Error Rate
- alert: HighErrorRate
  expr: |
    sum(rate(otel_traces_span_metrics_duration_count{
      status_code="STATUS_CODE_ERROR"
    }[5m])) by (service_name)
    /
    sum(rate(otel_traces_span_metrics_duration_count[5m])) by (service_name)
    > 0.05
  for: 5m

# High Latency
- alert: HighLatency
  expr: |
    histogram_quantile(0.95,
      sum(rate(otel_traces_span_metrics_duration_bucket[5m])) by (le, service_name)
    ) > 1000  # 1 second
  for: 5m
```

## 📚 Reference Documentation

Project Documentation:
- `docs/HYBRID_INSTRUMENTATION_GUIDE.md` - Python hybrid mode configuration
- `docs/EXEMPLARS_GUIDE.md` - Exemplars detailed explanation
- `docs/SPAN_METRICS_COMPARISON.md` - Span metrics comparison
- `docs/FINAL_CONFIGURATION.md` - This document

External Resources:
- [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/)
- [Tempo Metrics Generator](https://grafana.com/docs/tempo/latest/metrics-generator/)
- [Prometheus Exemplars](https://prometheus.io/docs/prometheus/latest/feature_flags/#exemplars-storage)
- [Grafana Exemplars](https://grafana.com/docs/grafana/latest/fundamentals/exemplars/)
