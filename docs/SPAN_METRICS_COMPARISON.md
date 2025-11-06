# Span Metrics 双重生成器对比指南

## 问题发现

你的系统中有 **两个** span metrics 生成器在同时工作：

1. **OTel Collector spanmetrics connector**
2. **Tempo metrics generator**

## 📊 详细对比

| 特性 | OTel Collector | Tempo |
|------|----------------|-------|
| **Metric 名称** | `otel_traces_span_metrics_*` | `traces_spanmetrics_*` |
| **Exemplar 标签** | `trace_id` (下划线) | `traceID` (驼峰) |
| **配置位置** | `otel-collector/config.yaml` | `grafana/tempo-config.yaml` |
| **数据流** | Traces → Collector → Prometheus | Traces → Tempo → Prometheus |
| **Namespace** | `otel` | (无) |
| **额外标签** | `otel_scope_name` | `source=tempo` |

## 🔍 示例数据

### OTel Collector 生成的 Metrics

```promql
otel_traces_span_metrics_duration_bucket{
  service_name="service-a-hybrid",
  span_name="GET /process",
  span_kind="SPAN_KIND_SERVER"
}
```

**Exemplar 标签**:
```json
{
  "trace_id": "0377cf00a2cea91b15ef388eb3ea620e",
  "span_id": "88e7924afe5df5bf"
}
```

### Tempo 生成的 Metrics

```promql
traces_spanmetrics_latency_bucket{
  service="service-a-hybrid",
  span_name="GET",
  span_kind="SPAN_KIND_SERVER",
  source="tempo"
}
```

**Exemplar 标签**:
```json
{
  "traceID": "db0b5ccf7808ff07595164fd633d01fb"
}
```

## ⚙️ 当前配置

### Tempo Metrics Generator (tempo-config.yaml)

```yaml
metrics_generator:
  registry:
    external_labels:
      source: tempo          # 标识来源
      cluster: o11y-lab
  storage:
    path: /tmp/tempo/generator/wal
    remote_write:
      - url: http://prometheus:9090/api/v1/write
        send_exemplars: true  # 启用 exemplars

overrides:
  metrics_generator_processors:
    - service-graphs         # 生成服务依赖图
    - span-metrics          # 生成 span metrics
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
      exporters: [otlp/tempo, spanmetrics]  # 同时发送到 Tempo 和 spanmetrics
    metrics:
      receivers: [spanmetrics]               # 从 spanmetrics 接收
```

### Grafana Datasource (datasources.yaml) - 已更新 ✅

```yaml
datasources:
  - name: Prometheus
    jsonData:
      exemplarTraceIdDestinations:
        # 支持两种格式
        - name: trace_id      # OTel Collector 格式
          datasourceUid: tempo
        - name: traceID       # Tempo 格式
          datasourceUid: tempo
```

## 🤔 应该使用哪一个？

### 选项 1: 只使用 OTel Collector (推荐) ✅

**优点**:
- 统一的配置和管理
- 可以在 Collector 中添加自定义处理器
- 更灵活的 dimensions 配置
- 支持更多自定义 buckets
- 与其他 OTLP 数据流一致

**缺点**:
- 需要额外配置 Collector

**如何禁用 Tempo metrics generator**:

```yaml
# tempo-config.yaml
# 注释掉或删除以下部分：
# metrics_generator:
#   ...
# overrides:
#   metrics_generator_processors: [service-graphs, span-metrics]
```

### 选项 2: 只使用 Tempo Metrics Generator

**优点**:
- 配置简单（在 Tempo 中一站式）
- 自动生成 service graph metrics
- 减少 Collector 的负载

**缺点**:
- 较少的自定义选项
- buckets 固定
- 不能在生成前处理数据

**如何禁用 OTel Collector spanmetrics**:

```yaml
# otel-collector/config.yaml
service:
  pipelines:
    traces:
      exporters: [otlp/tempo, debug]  # 移除 spanmetrics
    # 移除或注释 metrics pipeline 中的 spanmetrics receiver
```

### 选项 3: 同时使用两者 (当前配置)

**优点**:
- 可以对比两种实现
- Tempo 的 service graphs 很有用
- OTel 的 span metrics 更详细

**缺点**:
- 重复的 metrics（占用存储空间）
- 可能造成混淆
- 额外的计算开销

**当前状态**: ✅ Grafana 已配置支持两种格式

## 📝 推荐方案

### 方案 A: OTel Collector 为主，Tempo Service Graphs 为辅

保留 OTel Collector 的 span metrics，但也保留 Tempo 的 service-graphs：

```yaml
# tempo-config.yaml
overrides:
  metrics_generator_processors:
    - service-graphs       # 保留：生成服务依赖图
    # - span-metrics       # 移除：使用 OTel Collector 生成
```

**为什么**:
- Service graphs 是 Tempo 的特色功能
- Span metrics 由 OTel Collector 统一管理更灵活
- 避免重复的 span metrics

### 方案 B: 完全使用 Tempo (简化架构)

如果你想简化架构：

```yaml
# otel-collector/config.yaml
# 移除 spanmetrics connector
service:
  pipelines:
    traces:
      exporters: [otlp/tempo, debug]  # 只发送到 Tempo
```

```yaml
# tempo-config.yaml
overrides:
  metrics_generator_processors:
    - service-graphs
    - span-metrics
```

## 🔧 如何验证

### 查看 OTel Collector Metrics

```bash
curl -s http://localhost:8889/metrics | grep "otel_traces_span_metrics_duration_count"
```

### 查看 Tempo Metrics

```bash
curl -s http://localhost:9090/api/v1/query -G \
  --data-urlencode 'query=traces_spanmetrics_latency_count{service="service-a-hybrid"}' \
  | python3 -m json.tool
```

### 在 Grafana 中查看

**OTel Collector metrics**:
```promql
rate(otel_traces_span_metrics_duration_count{service_name="service-a-hybrid"}[5m])
```

**Tempo metrics**:
```promql
rate(traces_spanmetrics_latency_count{service="service-a-hybrid"}[5m])
```

## 📊 Service Graphs (Tempo 独有)

Tempo 的 service-graphs 功能生成服务间的调用关系 metrics：

```promql
# 服务间调用次数
traces_service_graph_request_total{
  client="service-a-hybrid",
  server="service-b"
}

# 服务间调用延迟
traces_service_graph_request_server_seconds_bucket{
  client="service-a-hybrid",
  server="service-b"
}
```

**这个功能很有用**，建议保留！

## 🎯 最终建议

**推荐配置** (方案 A):

1. **保留 OTel Collector spanmetrics** → 主要的 span metrics
2. **保留 Tempo service-graphs** → 服务依赖图
3. **禁用 Tempo span-metrics** → 避免重复

### 具体操作

编辑 `grafana/tempo-config.yaml`:

```yaml
overrides:
  metrics_generator_processors:
    - service-graphs    # 保留
    # - span-metrics    # 注释掉或删除
```

然后重启 Tempo:

```bash
docker compose restart tempo
```

### 好处

- ✅ 统一使用 OTel Collector 的 span metrics (更灵活)
- ✅ 保留 Tempo 的 service graphs (独特功能)
- ✅ Grafana 配置支持两种 exemplar 格式 (兼容性好)
- ✅ 减少重复数据
- ✅ 清晰的职责分工

## 📚 参考资料

- [Tempo Metrics Generator](https://grafana.com/docs/tempo/latest/metrics-generator/)
- [OTel Spanmetrics Connector](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/connector/spanmetricsconnector)
- [Grafana Exemplars](https://grafana.com/docs/grafana/latest/fundamentals/exemplars/)
