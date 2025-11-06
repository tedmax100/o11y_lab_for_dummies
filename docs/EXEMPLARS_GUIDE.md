# Exemplars 配置和问题诊断指南

## 什么是 Exemplars？

Exemplars 是 OpenMetrics 的一个功能，用于将 **metrics（指标）** 和 **traces（追踪）** 关联起来。每个 exemplar 包含：
- **Trace ID**: 关联到具体的 trace
- **Span ID**: 关联到具体的 span
- **Timestamp**: 采样时间
- **Value**: metric 的值

## 当前配置状态

### ✅ 已正确配置

1. **OTel Collector spanmetrics connector**:
   ```yaml
   connectors:
     spanmetrics:
       histogram:
         explicit:
           buckets: [1ms, 5ms, 10ms, 100ms, 250ms, 500ms, 1s, 5s]
       exemplars:
         enabled: true  # ✅ 已启用
   ```

2. **OTel Collector Prometheus exporter**:
   ```yaml
   exporters:
     prometheus:
       endpoint: "0.0.0.0:8889"
       enable_open_metrics: true  # ✅ 已启用 OpenMetrics 格式
   ```

3. **Prometheus exemplar storage**:
   ```yaml
   # docker-compose.yaml
   command:
     - '--enable-feature=exemplar-storage'  # ✅ 已启用
   ```

### 🔍 验证结果

#### OTel Collector Debug 输出中有 Exemplars

```bash
# 在 OTel Collector 日志中可以看到：
Exemplar #0
     -> Trace ID: f8fdce18f91361f5b9da0d88969b7592
     -> Span ID: 03f192b44343aade
     -> Timestamp: 2025-11-05 17:10:36.040829564 +0000 UTC
     -> Value: 0.000152
```

**✅ 这证明 exemplars 确实被生成并包含了 trace_id！**

## 问题诊断

### 为什么在 Prometheus exporter 端点看不到 Exemplars？

**原因**: Prometheus exporter 在 **纯文本格式** 中 **不会显示 exemplars**。

Exemplars 只在以下情况下可见：

1. **OTel Collector Debug exporter**: ✅ 可以看到（已验证）
2. **Prometheus TSDB**: ✅ Exemplars 被存储（通过 scrape）
3. **Grafana 查询**: ✅ 可以在 Grafana 中看到（通过 Prometheus 数据源）

### 验证 Exemplars 的方法

#### 方法 1: 检查 OTel Collector Debug 输出

```bash
docker logs otel-collector 2>&1 | grep -B 5 -A 10 "Exemplar #0" | grep -E "Trace ID|Span ID"
```

**预期输出**:
```
-> Trace ID: f8fdce18f91361f5b9da0d88969b7592
-> Span ID: 03f192b44343aade
```

#### 方法 2: 在 Grafana 中查询（推荐）

1. 打开 Grafana: http://localhost:3000
2. 进入 Explore
3. 选择 Prometheus 数据源
4. 查询:
   ```promql
   rate(otel_traces_span_metrics_duration_count{service_name="service-a-hybrid"}[1m])
   ```
5. 在图表上点击数据点，应该能看到 "View Trace" 链接

#### 方法 3: Prometheus API 查询 Exemplars

```bash
curl -s -G 'http://localhost:9090/api/v1/query_exemplars' \
  --data-urlencode 'query=otel_traces_span_metrics_duration_bucket{service_name="service-a-hybrid"}' \
  --data-urlencode 'start=2024-01-01T00:00:00Z' \
  --data-urlencode 'end=2025-12-31T23:59:59Z' | python3 -m json.tool
```

## 配置文件总结

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
      enabled: true  # 关键配置
    dimensions_cache_size: 1000
    aggregation_temporality: "AGGREGATION_TEMPORALITY_CUMULATIVE"

exporters:
  prometheus:
    endpoint: "0.0.0.0:8889"
    namespace: "otel"
    enable_open_metrics: true  # 启用 OpenMetrics 格式

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, resourcedetection, resource, batch]
      exporters: [otlp/tempo, spanmetrics, debug]  # spanmetrics 作为 exporter

    metrics:
      receivers: [otlp, prometheus, spanmetrics]  # spanmetrics 作为 receiver
      processors: [memory_limiter, resourcedetection, resource, batch]
      exporters: [prometheus, otlphttp/prometheus, debug]
```

### docker-compose.yaml (Prometheus)

```yaml
prometheus:
  image: prom/prometheus:v3.7.3
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--enable-feature=exemplar-storage'  # 必须启用
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

## Grafana 配置

### 配置 Tempo 作为 Exemplar 数据源

1. 进入 Grafana: http://localhost:3000
2. Configuration → Data Sources → Prometheus
3. 找到 "Exemplars" 部分
4. 配置:
   - **Internal link**: 启用
   - **Data source**: Tempo
   - **URL Label**: `traceID`

这样当你在 Prometheus metrics 图表中点击数据点时，Grafana 会自动创建一个链接到 Tempo 中对应的 trace。

## 工作流程

```
Application (service-a)
    ↓ traces
OTel Collector
    ↓
spanmetrics connector
    ├─→ Generates metrics with exemplars
    │   (包含 trace_id 和 span_id)
    ↓
Prometheus exporter (port 8889)
    ↓ scrape
Prometheus
    ├─→ 存储 metrics
    └─→ 存储 exemplars
    ↓
Grafana
    ├─→ 显示 metrics 图表
    └─→ 点击数据点 → 跳转到 Tempo trace
```

## 常见问题

### Q1: 为什么 `curl http://localhost:8889/metrics` 看不到 trace_id？

**A**: 这是正常的。Prometheus 文本格式不包含 exemplars 的详细信息。Exemplars 通过 Prometheus 的 scrape 机制被采集并存储在 TSDB 中，然后在 Grafana 中查询时可见。

### Q2: 如何确认 exemplars 真的在工作？

**A**: 最可靠的方法：
1. 在 Grafana Explore 中查询 span metrics
2. 查看图表上是否有小点（exemplars）
3. 点击数据点，检查是否有 "View Trace" 按钮

### Q3: Exemplars 在什么情况下会生成？

**A**:
- 当有 **traces** 通过 OTel Collector 时
- spanmetrics connector 会从这些 traces 生成 metrics
- 同时为每个 histogram bucket 采样生成 exemplar
- Exemplar 包含该 span 的 trace_id 和 span_id

### Q4: 为什么有些 metrics 没有 exemplars？

**A**: 可能的原因：
- Counter metrics 不支持 exemplars（只有 histogram 支持）
- Exemplar 采样率（默认每个 bucket 只保留最后一个）
- Traces 和 metrics 的时间窗口不匹配

## 验证清单

- [x] spanmetrics connector 配置中 `exemplars.enabled: true`
- [x] Prometheus exporter 配置中 `enable_open_metrics: true`
- [x] Prometheus 启动参数包含 `--enable-feature=exemplar-storage`
- [x] Traces pipeline 包含 `spanmetrics` exporter
- [x] Metrics pipeline 包含 `spanmetrics` receiver
- [x] OTel Collector debug 日志中能看到 Exemplar 和 Trace ID
- [ ] Grafana 中 Prometheus 数据源配置了 Tempo 作为 exemplar 链接目标
- [ ] 在 Grafana 图表中能看到 exemplar 点并跳转到 trace

## 下一步

1. **在 Grafana 中验证**:
   ```bash
   # 访问 Grafana
   open http://localhost:3000

   # 查询示例
   rate(otel_traces_span_metrics_duration_count{service_name="service-a-hybrid"}[5m])
   ```

2. **配置 Grafana Tempo 数据源链接**（如果还没配置）

3. **创建 Dashboard 展示 exemplars**

## 参考资料

- [OpenTelemetry spanmetrics connector](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/connector/spanmetricsconnector)
- [Prometheus Exemplars](https://prometheus.io/docs/prometheus/latest/feature_flags/#exemplars-storage)
- [Grafana Exemplars](https://grafana.com/docs/grafana/latest/fundamentals/exemplars/)
