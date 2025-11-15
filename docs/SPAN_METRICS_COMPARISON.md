# Span Metrics Dual Generator Comparison Guide

## Problem Discovery

Your system has **two** span metrics generators working simultaneously:

1. **OTel Collector spanmetrics connector**
2. **Tempo metrics generator**

## 📊 Detailed Comparison

| Feature | OTel Collector | Tempo |
|---------|----------------|-------|
| **Metric Name** | `otel_traces_span_metrics_*` | `traces_spanmetrics_*` |
| **Exemplar Label** | `trace_id` (underscore) | `traceID` (camelCase) |
| **Configuration Location** | `otel-collector/config.yaml` | `grafana/tempo-config.yaml` |
| **Data Flow** | Traces → Collector → Prometheus | Traces → Tempo → Prometheus |
| **Namespace** | `otel` | (none) |
| **Additional Labels** | `otel_scope_name` | `source=tempo` |

## 🔍 Example Data

### OTel Collector Generated Metrics

```promql
otel_traces_span_metrics_duration_bucket{
  service_name="service-a-hybrid",
  span_name="GET /process",
  span_kind="SPAN_KIND_SERVER"
}
```

**Exemplar Labels**:
```json
{
  "trace_id": "0377cf00a2cea91b15ef388eb3ea620e",
  "span_id": "88e7924afe5df5bf"
}
```

### Tempo Generated Metrics

```promql
traces_spanmetrics_latency_bucket{
  service="service-a-hybrid",
  span_name="GET",
  span_kind="SPAN_KIND_SERVER",
  source="tempo"
}
```

**Exemplar Labels**:
```json
{
  "traceID": "db0b5ccf7808ff07595164fd633d01fb"
}
```

## ⚙️ Current Configuration

### Tempo Metrics Generator (tempo-config.yaml)

```yaml
metrics_generator:
  registry:
    external_labels:
      source: tempo          # Identifies source
      cluster: o11y-lab
  storage:
    path: /tmp/tempo/generator/wal
    remote_write:
      - url: http://prometheus:9090/api/v1/write
        send_exemplars: true  # Enable exemplars

overrides:
  metrics_generator_processors:
    - service-graphs         # Generate service dependency graph
    - span-metrics          # Generate span metrics
```

### OTel Collector Spanmetrics (otel-collector/config.yaml)

```yaml
connectors:
  spanmetrics:
    histogram:
      explicit:
        buckets: [1ms, 5ms, 10ms, 100ms, 250ms, 500ms, 1s, 5s]
    exemplars:
      enabled: true

service:
  pipelines:
    traces:
      exporters: [otlp/tempo, spanmetrics]  # Send to both Tempo and spanmetrics
    metrics:
      receivers: [spanmetrics]               # Receive from spanmetrics
```

### Grafana Datasource (datasources.yaml) - Updated ✅

```yaml
datasources:
  - name: Prometheus
    jsonData:
      exemplarTraceIdDestinations:
        # Support both formats
        - name: trace_id      # OTel Collector format
          datasourceUid: tempo
        - name: traceID       # Tempo format
          datasourceUid: tempo
```

## 🤔 Which One Should I Use?

### Option 1: OTel Collector Only (Recommended) ✅

**Advantages**:
- Unified configuration and management
- Can add custom processors in Collector
- More flexible dimensions configuration
- Support for more custom buckets
- Consistent with other OTLP data flows

**Disadvantages**:
- Requires additional Collector configuration

**How to disable Tempo metrics generator**:

```yaml
# tempo-config.yaml
# Comment out or remove the following section:
# metrics_generator:
#   ...
# overrides:
#   metrics_generator_processors: [service-graphs, span-metrics]
```

### Option 2: Tempo Metrics Generator Only

**Advantages**:
- Simple configuration (one-stop in Tempo)
- Automatically generates service graph metrics
- Reduces Collector load

**Disadvantages**:
- Fewer customization options
- Fixed buckets
- Cannot process data before generation

**How to disable OTel Collector spanmetrics**:

```yaml
# otel-collector/config.yaml
service:
  pipelines:
    traces:
      exporters: [otlp/tempo, debug]  # Remove spanmetrics
    # Remove or comment out spanmetrics receiver in metrics pipeline
```

### Option 3: Use Both (Current Configuration)

**Advantages**:
- Can compare both implementations
- Tempo's service graphs are useful
- OTel's span metrics are more detailed

**Disadvantages**:
- Duplicate metrics (storage overhead)
- May cause confusion
- Additional computational overhead

**Current Status**: ✅ Grafana configured to support both formats

## 📝 Recommended Solutions

### Solution A: OTel Collector Primary, Tempo Service Graphs Secondary

Keep OTel Collector's span metrics, but also keep Tempo's service-graphs:

```yaml
# tempo-config.yaml
overrides:
  metrics_generator_processors:
    - service-graphs       # Keep: generates service dependency graph
    # - span-metrics       # Remove: use OTel Collector to generate
```

**Why**:
- Service graphs are Tempo's signature feature
- Span metrics managed by OTel Collector are more flexible
- Avoid duplicate span metrics

### Solution B: Fully Use Tempo (Simplified Architecture)

If you want to simplify the architecture:

```yaml
# otel-collector/config.yaml
# Remove spanmetrics connector
service:
  pipelines:
    traces:
      exporters: [otlp/tempo, debug]  # Only send to Tempo
```

```yaml
# tempo-config.yaml
overrides:
  metrics_generator_processors:
    - service-graphs
    - span-metrics
```

## 🔧 How to Verify

### View OTel Collector Metrics

```bash
curl -s http://localhost:8889/metrics | grep "otel_traces_span_metrics_duration_count"
```

### View Tempo Metrics

```bash
curl -s http://localhost:9090/api/v1/query -G \
  --data-urlencode 'query=traces_spanmetrics_latency_count{service="service-a-hybrid"}' \
  | python3 -m json.tool
```

### View in Grafana

**OTel Collector metrics**:
```promql
rate(otel_traces_span_metrics_duration_count{service_name="service-a-hybrid"}[5m])
```

**Tempo metrics**:
```promql
rate(traces_spanmetrics_latency_count{service="service-a-hybrid"}[5m])
```

## 📊 Service Graphs (Tempo Exclusive)

Tempo's service-graphs feature generates inter-service call relationship metrics:

```promql
# Inter-service call count
traces_service_graph_request_total{
  client="service-a-hybrid",
  server="service-b"
}

# Inter-service call latency
traces_service_graph_request_server_seconds_bucket{
  client="service-a-hybrid",
  server="service-b"
}
```

**This feature is useful**, recommend keeping it!

## 🎯 Final Recommendation

**Recommended Configuration** (Solution A):

1. **Keep OTel Collector spanmetrics** → Primary span metrics
2. **Keep Tempo service-graphs** → Service dependency graph
3. **Disable Tempo span-metrics** → Avoid duplication

### Specific Actions

Edit `grafana/tempo-config.yaml`:

```yaml
overrides:
  metrics_generator_processors:
    - service-graphs    # Keep
    # - span-metrics    # Comment out or remove
```

Then restart Tempo:

```bash
docker compose restart tempo
```

### Benefits

- ✅ Unified use of OTel Collector's span metrics (more flexible)
- ✅ Keep Tempo's service graphs (unique feature)
- ✅ Grafana configuration supports both exemplar formats (good compatibility)
- ✅ Reduce duplicate data
- ✅ Clear division of responsibilities

## 📚 Reference Materials

- [Tempo Metrics Generator](https://grafana.com/docs/tempo/latest/metrics-generator/)
- [OTel Spanmetrics Connector](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/connector/spanmetricsconnector)
- [Grafana Exemplars](https://grafana.com/docs/grafana/latest/fundamentals/exemplars/)
