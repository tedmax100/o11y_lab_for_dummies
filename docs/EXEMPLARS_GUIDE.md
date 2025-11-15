# Exemplars Configuration and Troubleshooting Guide

## What are Exemplars?

Exemplars are a feature of OpenMetrics used to correlate **metrics** with **traces**. Each exemplar contains:
- **Trace ID**: Links to a specific trace
- **Span ID**: Links to a specific span
- **Timestamp**: Sampling time
- **Value**: Metric value

## Current Configuration Status

### ✅ Correctly Configured

1. **OTel Collector spanmetrics connector**:
   ```yaml
   connectors:
     spanmetrics:
       histogram:
         explicit:
           buckets: [1ms, 5ms, 10ms, 100ms, 250ms, 500ms, 1s, 5s]
       exemplars:
         enabled: true  # ✅ Enabled
   ```

2. **OTel Collector Prometheus exporter**:
   ```yaml
   exporters:
     prometheus:
       endpoint: "0.0.0.0:8889"
       enable_open_metrics: true  # ✅ OpenMetrics format enabled
   ```

3. **Prometheus exemplar storage**:
   ```yaml
   # docker-compose.yaml
   command:
     - '--enable-feature=exemplar-storage'  # ✅ Enabled
   ```

### 🔍 Verification Results

#### Exemplars in OTel Collector Debug Output

```bash
# In OTel Collector logs you can see:
Exemplar #0
     -> Trace ID: f8fdce18f91361f5b9da0d88969b7592
     -> Span ID: 03f192b44343aade
     -> Timestamp: 2025-11-05 17:10:36.040829564 +0000 UTC
     -> Value: 0.000152
```

**✅ This proves exemplars are indeed generated and contain trace_id!**

## Problem Diagnosis

### Why can't I see Exemplars at the Prometheus exporter endpoint?

**Reason**: The Prometheus exporter **does not display exemplars** in **plain text format**.

Exemplars are only visible in the following scenarios:

1. **OTel Collector Debug exporter**: ✅ Visible (verified)
2. **Prometheus TSDB**: ✅ Exemplars are stored (via scrape)
3. **Grafana queries**: ✅ Visible in Grafana (via Prometheus data source)

### Methods to Verify Exemplars

#### Method 1: Check OTel Collector Debug Output

```bash
docker logs otel-collector 2>&1 | grep -B 5 -A 10 "Exemplar #0" | grep -E "Trace ID|Span ID"
```

**Expected output**:
```
-> Trace ID: f8fdce18f91361f5b9da0d88969b7592
-> Span ID: 03f192b44343aade
```

#### Method 2: Query in Grafana (Recommended)

1. Open Grafana: http://localhost:3000
2. Go to Explore
3. Select Prometheus data source
4. Query:
   ```promql
   rate(otel_traces_span_metrics_duration_count{service_name="service-a-hybrid"}[1m])
   ```
5. Click on data points in the chart, you should see a "View Trace" link

#### Method 3: Prometheus API Query for Exemplars

```bash
curl -s -G 'http://localhost:9090/api/v1/query_exemplars' \
  --data-urlencode 'query=otel_traces_span_metrics_duration_bucket{service_name="service-a-hybrid"}' \
  --data-urlencode 'start=2024-01-01T00:00:00Z' \
  --data-urlencode 'end=2025-12-31T23:59:59Z' | python3 -m json.tool
```

## Configuration File Summary

### otel-collector/config.yaml

```yaml
connectors:
  spanmetrics:
    histogram:
      explicit:
        buckets: [1ms, 5ms, 10ms, 100ms, 250ms, 500ms, 1s, 5s]
    dimensions:
      - name: http.method
        default: GET
      - name: http.status_code
    exemplars:
      enabled: true  # Key configuration
    dimensions_cache_size: 1000
    aggregation_temporality: "AGGREGATION_TEMPORALITY_CUMULATIVE"

exporters:
  prometheus:
    endpoint: "0.0.0.0:8889"
    namespace: "otel"
    enable_open_metrics: true  # Enable OpenMetrics format

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, resourcedetection, resource, batch]
      exporters: [otlp/tempo, spanmetrics, debug]  # spanmetrics as exporter

    metrics:
      receivers: [otlp, prometheus, spanmetrics]  # spanmetrics as receiver
      processors: [memory_limiter, resourcedetection, resource, batch]
      exporters: [prometheus, otlphttp/prometheus, debug]
```

### docker-compose.yaml (Prometheus)

```yaml
prometheus:
  image: prom/prometheus:v3.7.3
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--enable-feature=exemplar-storage'  # Must be enabled
    - '--web.enable-otlp-receiver'
```

### grafana/prometheus.yaml

```yaml
scrape_configs:
  - job_name: 'otel-collector-metrics'
    scrape_interval: 15s
    static_configs:
      - targets: ['otel-collector:8889']
```

## Grafana Configuration

### Configure Tempo as Exemplar Data Source

1. Go to Grafana: http://localhost:3000
2. Configuration → Data Sources → Prometheus
3. Find "Exemplars" section
4. Configure:
   - **Internal link**: Enable
   - **Data source**: Tempo
   - **URL Label**: `traceID`

This way, when you click on data points in Prometheus metrics charts, Grafana will automatically create a link to the corresponding trace in Tempo.

## Workflow

```
Application (service-a)
    ↓ traces
OTel Collector
    ↓
spanmetrics connector
    ├─→ Generates metrics with exemplars
    │   (contains trace_id and span_id)
    ↓
Prometheus exporter (port 8889)
    ↓ scrape
Prometheus
    ├─→ Store metrics
    └─→ Store exemplars
    ↓
Grafana
    ├─→ Display metrics charts
    └─→ Click data point → Jump to Tempo trace
```

## Common Questions

### Q1: Why can't I see trace_id when running `curl http://localhost:8889/metrics`?

**A**: This is normal. Prometheus text format does not include detailed exemplar information. Exemplars are collected and stored in TSDB through Prometheus's scrape mechanism, and become visible when queried in Grafana.

### Q2: How can I confirm exemplars are really working?

**A**: Most reliable method:
1. Query span metrics in Grafana Explore
2. Check if there are small dots (exemplars) on the chart
3. Click on data points, check if there's a "View Trace" button

### Q3: When are exemplars generated?

**A**:
- When **traces** pass through OTel Collector
- spanmetrics connector generates metrics from these traces
- Simultaneously samples and generates exemplars for each histogram bucket
- Exemplars contain the trace_id and span_id of that span

### Q4: Why don't some metrics have exemplars?

**A**: Possible reasons:
- Counter metrics don't support exemplars (only histograms support them)
- Exemplar sampling rate (by default only the last one per bucket is kept)
- Traces and metrics time windows don't match

## Verification Checklist

- [x] spanmetrics connector config has `exemplars.enabled: true`
- [x] Prometheus exporter config has `enable_open_metrics: true`
- [x] Prometheus startup parameters include `--enable-feature=exemplar-storage`
- [x] Traces pipeline includes `spanmetrics` exporter
- [x] Metrics pipeline includes `spanmetrics` receiver
- [x] OTel Collector debug logs show Exemplar and Trace ID
- [ ] Grafana Prometheus data source configured with Tempo as exemplar link target
- [ ] Exemplar points visible in Grafana charts and can jump to trace

## Next Steps

1. **Verify in Grafana**:
   ```bash
   # Access Grafana
   open http://localhost:3000

   # Query example
   rate(otel_traces_span_metrics_duration_count{service_name="service-a-hybrid"}[5m])
   ```

2. **Configure Grafana Tempo data source link** (if not yet configured)

3. **Create Dashboard to display exemplars**

## References

- [OpenTelemetry spanmetrics connector](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/connector/spanmetricsconnector)
- [Prometheus Exemplars](https://prometheus.io/docs/prometheus/latest/feature_flags/#exemplars-storage)
- [Grafana Exemplars](https://grafana.com/docs/grafana/latest/fundamentals/exemplars/)
