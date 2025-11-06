# 最终可观测性配置总结

## 🎯 当前配置状态

### ✅ Span Metrics 配置

**单一来源**: OTel Collector spanmetrics connector

```yaml
# otel-collector/config.yaml
connectors:
  spanmetrics:
    histogram:
      explicit:
        buckets: [1ms, 5ms, 10ms, 100ms, 250ms, 500ms, 1s, 5s]
    exemplars:
      enabled: true  # 包含 trace_id
```

**Metrics 名称**: `otel_traces_span_metrics_*`
**Exemplar 标签**: `trace_id` (下划线格式)

### ✅ Service Graphs 配置

**来源**: Tempo metrics generator

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
  metrics_generator_processors: [service-graphs]  # 只保留 service-graphs
```

**Metrics 名称**: `traces_service_graph_*`

## 📊 可用的 Metrics

### 1. Span Metrics (来自 OTel Collector)

用于监控单个服务的性能：

```promql
# 请求速率
rate(otel_traces_span_metrics_duration_count{service_name="service-a-hybrid"}[5m])

# 延迟分布 (P95)
histogram_quantile(0.95,
  rate(otel_traces_span_metrics_duration_bucket{service_name="service-a-hybrid"}[5m])
)

# 错误率
rate(otel_traces_span_metrics_duration_count{
  service_name="service-a-hybrid",
  status_code="STATUS_CODE_ERROR"
}[5m])
```

**特点**:
- ✅ 包含 exemplars (trace_id)
- ✅ 可点击跳转到 Tempo trace
- ✅ 详细的维度 (span_name, span_kind, http_method, http_status_code)
- ✅ 自定义 buckets

### 2. Service Graph Metrics (来自 Tempo)

用于监控服务间的调用关系：

```promql
# 服务间调用次数
traces_service_graph_request_total{
  client="service-a-hybrid",
  server="service-b"
}

# 服务间调用延迟
histogram_quantile(0.95,
  rate(traces_service_graph_request_server_seconds_bucket{
    client="service-a-hybrid",
    server="service-b"
  }[5m])
)

# 服务间调用失败数
traces_service_graph_request_failed_total{
  client="service-a-hybrid",
  server="service-b"
}
```

**特点**:
- ✅ 显示服务依赖关系
- ✅ Client 和 Server 视角的延迟
- ✅ 失败请求统计
- ✅ 自动生成服务拓扑图

## 🔗 三大支柱关联

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

**使用方式**:
1. 在 Grafana 中查询 span metrics
2. 图表显示 exemplar 点 (⚫)
3. 点击 exemplar → 跳转到 Tempo trace

### Traces → Logs ✅

```yaml
# Tempo datasource
tracesToLogsV2:
  datasourceUid: loki
  tags: ['service_name']
  filterByTraceID: true
  query: '{service_name="${__span.tags["service.name"]}"} |="${__span.traceId}"'
```

**使用方式**:
1. 在 Tempo 中查看 trace
2. 点击 span 旁边的 "Logs" 按钮
3. 自动跳转到 Loki 显示相关日志

### Logs → Traces ✅

```yaml
# Loki datasource
derivedFields:
  - datasourceUid: tempo
    name: TraceID
    matcherRegex: 'trace_id'
    matcherType: label
```

**使用方式**:
1. 在 Loki 中查看日志
2. 日志行包含 trace_id 标签
3. 点击 trace_id → 跳转到 Tempo trace

### Traces → Metrics ✅

```yaml
# Tempo datasource
tracesToMetrics:
  datasourceUid: prometheus
  queries:
    - name: 'Request Rate'
      query: 'rate(duration_count{$$__tags}[5m])'
```

**使用方式**:
1. 在 Tempo 中查看 trace
2. 切换到 "Metrics" 标签
3. 查看相关的 span metrics

## 📈 推荐 Grafana 查询

### Service-A 性能概览

```promql
# 请求速率
sum(rate(otel_traces_span_metrics_duration_count{
  service_name="service-a-hybrid",
  span_kind="SPAN_KIND_SERVER"
}[5m])) by (span_name)

# P50, P90, P95, P99 延迟
histogram_quantile(0.50, sum(rate(otel_traces_span_metrics_duration_bucket{
  service_name="service-a-hybrid",
  span_kind="SPAN_KIND_SERVER"
}[5m])) by (le, span_name))

# 错误率
sum(rate(otel_traces_span_metrics_duration_count{
  service_name="service-a-hybrid",
  status_code="STATUS_CODE_ERROR"
}[5m])) / sum(rate(otel_traces_span_metrics_duration_count{
  service_name="service-a-hybrid"
}[5m]))
```

### 服务依赖图

```promql
# Service-A 的下游服务
traces_service_graph_request_total{client="service-a-hybrid"}

# Service-A 的上游服务
traces_service_graph_request_total{server="service-a-hybrid"}

# Service-A → Service-B 调用延迟
histogram_quantile(0.95, rate(traces_service_graph_request_server_seconds_bucket{
  client="service-a-hybrid",
  server="service-b"
}[5m]))
```

## 🔧 配置文件位置

| 配置项 | 文件路径 |
|--------|----------|
| OTel Collector spanmetrics | `otel-collector/config.yaml` |
| Tempo metrics generator | `grafana/tempo-config.yaml` |
| Grafana datasources | `grafana/datasources/datasources.yaml` |
| Prometheus config | `grafana/prometheus.yaml` |
| Loki config | `grafana/loki-config.yaml` |

## 📝 关键配置摘要

### OTel Collector Pipelines

```yaml
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, resourcedetection, resource, batch]
      exporters: [otlp/tempo, spanmetrics, debug]  # 发送到 Tempo 和 spanmetrics

    metrics:
      receivers: [otlp, prometheus, spanmetrics]    # 从 spanmetrics 接收
      processors: [memory_limiter, resourcedetection, resource, batch]
      exporters: [prometheus, otlphttp/prometheus, debug]

    logs:
      receivers: [otlp]
      processors: [memory_limiter, resourcedetection, resource, batch]
      exporters: [otlphttp/loki, debug/logs]
```

### Prometheus Scrape 配置

```yaml
scrape_configs:
  # OTel Collector 内部 metrics
  - job_name: 'otel-collector'
    static_configs:
      - targets: ['otel-collector:8888']

  # OTel Collector 应用 metrics (包含 exemplars)
  - job_name: 'otel-collector-metrics'
    scrape_interval: 15s
    static_configs:
      - targets: ['otel-collector:8889']
```

## 🎨 Grafana Service Graph

Tempo 的 service-graphs 可以在 Grafana 中可视化：

1. **打开 Grafana**: http://localhost:3000
2. **Explore → Tempo**
3. **切换到 "Service Graph" 标签**
4. **查看服务依赖拓扑图**

Service Graph 显示：
- 🔵 服务节点
- ➡️ 调用关系
- 📊 请求速率
- ⏱️ 延迟
- ❌ 错误率

## 🧪 验证配置

### 1. 验证 Span Metrics

```bash
# 查询 OTel Collector span metrics
curl -s -G 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=otel_traces_span_metrics_duration_count{service_name="service-a-hybrid"}' \
  | python3 -m json.tool
```

### 2. 验证 Service Graphs

```bash
# 查询 Tempo service graph metrics
curl -s -G 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=traces_service_graph_request_total{client="service-a-hybrid"}' \
  | python3 -m json.tool
```

### 3. 验证 Exemplars

```bash
# 查询 exemplars
curl -s -G 'http://localhost:9090/api/v1/query_exemplars' \
  --data-urlencode 'query=otel_traces_span_metrics_duration_bucket{service_name="service-a-hybrid"}' \
  --data-urlencode 'start=2025-01-01T00:00:00Z' \
  --data-urlencode 'end=2025-12-31T23:59:59Z' \
  | python3 -m json.tool | grep "trace_id"
```

## 🎉 配置优势

### 为什么选择这个配置？

1. **清晰的职责分工**:
   - OTel Collector: 统一处理所有遥测数据 + 生成 span metrics
   - Tempo: 存储 traces + 生成 service graphs

2. **避免重复**:
   - 只有一个 span metrics 来源
   - 没有重复的数据存储

3. **最大化功能**:
   - ✅ Span metrics with exemplars (OTel Collector)
   - ✅ Service dependency graphs (Tempo)
   - ✅ 完整的三大支柱关联

4. **灵活性**:
   - OTel Collector 可以自定义 buckets
   - 可以添加更多 dimensions
   - 易于扩展和修改

## 🚀 下一步

### 建议的 Grafana Dashboards

1. **RED Metrics Dashboard** (Rate, Errors, Duration)
   - 使用 `otel_traces_span_metrics_*`
   - 按服务、端点、方法分组

2. **Service Map Dashboard**
   - 使用 `traces_service_graph_*`
   - 可视化服务依赖关系

3. **SLO Dashboard**
   - 基于 span metrics 计算 SLI
   - 设置 SLO 目标和告警

### 推荐的告警规则

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

## 📚 参考文档

项目文档：
- `docs/HYBRID_INSTRUMENTATION_GUIDE.md` - Python 混合模式配置
- `docs/EXEMPLARS_GUIDE.md` - Exemplars 详细说明
- `docs/SPAN_METRICS_COMPARISON.md` - Span metrics 对比
- `docs/FINAL_CONFIGURATION.md` - 本文档

外部资源：
- [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/)
- [Tempo Metrics Generator](https://grafana.com/docs/tempo/latest/metrics-generator/)
- [Prometheus Exemplars](https://prometheus.io/docs/prometheus/latest/feature_flags/#exemplars-storage)
- [Grafana Exemplars](https://grafana.com/docs/grafana/latest/fundamentals/exemplars/)
