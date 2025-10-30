# 使用指南

本文档详细介绍如何使用 OpenTelemetry Observability Lab 进行可观测性学习和实验。

## 目录

- [快速开始](#快速开始)
- [核心概念](#核心概念)
- [实验场景](#实验场景)
- [Grafana 使用](#grafana-使用)
- [进阶主题](#进阶主题)

## 快速开始

### 1. 启动所有服务

```bash
# 使用启动脚本（推荐）
chmod +x start.sh
./start.sh

# 或者手动启动
docker-compose up -d
```

### 2. 验证服务

```bash
# 检查所有容器是否运行
docker-compose ps

# 查看日志
docker-compose logs -f api-gateway
```

### 3. 发送测试请求

```bash
# 触发完整的请求链路
curl http://localhost:8080/api/process

# 多次请求以生成更多数据
for i in {1..10}; do curl http://localhost:8080/api/process; done
```

### 4. 访问 Grafana

打开浏览器访问 http://localhost:3000
- 用户名: `admin`
- 密码: `admin`

## 核心概念

### 三大支柱的关联

本项目的核心价值在于展示 Logs、Metrics、Traces 如何相互关联：

#### 1. Trace ID 作为关联键

每个请求都会生成一个唯一的 Trace ID，它会：
- 在所有 spans 中传递
- 注入到结构化日志中
- 作为 exemplar 关联到 metrics

#### 2. 结构化日志格式

所有服务的日志都采用 JSON 格式，包含：

```json
{
  "time": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "service": "service-a",
  "trace_id": "abc123...",
  "span_id": "def456...",
  "message": "Processing request"
}
```

#### 3. Context Propagation

使用 W3C Trace Context 标准，通过 HTTP Headers 传播：
- `traceparent`: 包含 trace_id 和 span_id
- `tracestate`: 附加的追踪状态

## 实验场景

### 场景 1: 追踪完整的请求链路

**目标**: 理解分布式追踪如何工作

1. 发送请求:
```bash
curl http://localhost:8080/api/process
```

2. 在 Grafana 中打开 **Explore**

3. 选择 **Tempo** 数据源

4. 点击 **Search**，查看最近的 traces

5. 点击一个 trace 查看详细信息，你会看到：
   - API Gateway → Service A → Service D
   - API Gateway → Service A → Service B
   - Service A → Database
   - Service A → Third-Party API

6. 观察每个 span 的：
   - Duration (持续时间)
   - Attributes (属性)
   - Events (事件)

### 场景 2: 从日志跳转到 Trace

**目标**: 理解日志和追踪的关联

1. 在 Grafana Explore 中选择 **Loki** 数据源

2. 使用查询:
```logql
{service_name="service-a"} | json
```

3. 找到一条日志，点击日志中的 **TraceID** 链接

4. 自动跳转到 Tempo 查看完整的 trace

### 场景 3: 从 Metrics 到 Traces

**目标**: 理解 Exemplars 的作用

1. 在 Grafana 中选择 **Prometheus** 数据源

2. 查询请求延迟:
```promql
histogram_quantile(0.95, rate(http_server_duration_bucket[5m]))
```

3. 在图表中查看 **Exemplars**（小圆点）

4. 点击 Exemplar 可以直接跳转到对应的 trace

### 场景 4: Kafka 消息追踪

**目标**: 理解异步消息的追踪

1. 发送请求触发 Kafka 消息:
```bash
curl http://localhost:8080/api/process
```

2. 在 Tempo 中查找 trace

3. 观察:
   - Service A 调用 Service B (生产者)
   - Service B 将消息写入 Kafka
   - Service C 从 Kafka 消费消息
   - **整个链路在同一个 trace 中！**

4. 查看 Service C 的日志:
```bash
docker-compose logs service-c | grep trace_id
```

### 场景 5: 错误追踪

**目标**: 理解如何追踪和定位错误

1. 模拟错误（修改代码或关闭某个服务）:
```bash
docker-compose stop service-d
```

2. 发送请求:
```bash
curl http://localhost:8080/api/process
```

3. 在 Tempo 中查找错误的 trace（红色标记）

4. 查看错误详情：
   - 哪个 span 失败了
   - 错误信息
   - Stack trace

5. 从 trace 跳转到日志查看详细错误信息

## Grafana 使用

### 数据源配置

项目已经预配置了三个数据源：

1. **Prometheus** (Metrics)
   - URL: http://prometheus:9090
   - 用于查询 metrics 和 exemplars

2. **Loki** (Logs)
   - URL: http://loki:3100
   - 配置了 derived fields 自动提取 trace_id

3. **Tempo** (Traces)
   - URL: http://tempo:3200
   - 配置了到 Loki 和 Prometheus 的关联

### 常用查询

#### Loki 查询

```logql
# 查看特定服务的日志
{service_name="service-a"}

# 过滤错误日志
{service_name="service-a"} | json | level="ERROR"

# 根据 trace_id 查询
{service_name="service-a"} | json | trace_id="your-trace-id"

# 查看包含特定关键词的日志
{service_name="service-a"} | json | message =~ "database"
```

#### PromQL 查询

```promql
# 请求速率
rate(http_server_requests_total[5m])

# 按服务分组的请求速率
sum by(service_name) (rate(http_server_requests_total[5m]))

# P95 延迟
histogram_quantile(0.95, rate(http_server_duration_bucket[5m]))

# 错误率
rate(http_server_requests_total{status_code=~"5.."}[5m])
```

#### Tempo 查询

- 按服务名搜索: `service.name = "service-a"`
- 按状态搜索: `status = error`
- 按时间范围搜索
- 按 trace ID 精确搜索

### Explore 工作流

**典型的故障排查流程**:

1. **从 Metrics 开始**: 发现某个服务的延迟突然升高
2. **查看 Exemplars**: 点击图表上的点，获取示例 trace
3. **分析 Trace**: 在 Tempo 中查看详细的调用链，定位慢的 span
4. **查看日志**: 从 trace 跳转到日志，查看详细的错误信息
5. **关联分析**: 在日志中根据 trace_id 查找所有相关日志

## 进阶主题

### 1. 自定义 Instrumentation

#### 添加自定义 Span

Python 示例:
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("my_custom_operation") as span:
    span.set_attribute("custom.key", "value")
    # 你的业务逻辑
    result = do_something()
    span.set_attribute("custom.result", result)
```

Go 示例:
```go
ctx, span := tracer.Start(ctx, "my_custom_operation")
defer span.End()

span.SetAttributes(
    attribute.String("custom.key", "value"),
)
```

#### 添加自定义 Metrics

Python 示例:
```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)
counter = meter.create_counter(
    "my_custom_counter",
    description="Description of counter",
    unit="1"
)

counter.add(1, {"label": "value"})
```

### 2. Sampling 策略

修改 `otel-collector/config.yaml`:

```yaml
processors:
  probabilistic_sampler:
    sampling_percentage: 10  # 10% 采样

service:
  pipelines:
    traces:
      processors: [probabilistic_sampler, batch]
```

### 3. 性能优化

#### Batch 处理

```yaml
processors:
  batch:
    timeout: 10s
    send_batch_size: 1024
    send_batch_max_size: 2048
```

#### 内存限制

```yaml
processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 512
    spike_limit_mib: 128
```

### 4. 生产环境建议

1. **使用适当的采样率**
   - 高流量系统: 1-10%
   - 关键路径: 100%
   - 通过 Head-based 或 Tail-based sampling

2. **配置资源限制**
   - Collector 内存和 CPU 限制
   - 存储保留策略

3. **高可用配置**
   - Collector 多副本
   - 后端存储的高可用配置

4. **监控 Collector 本身**
   - Collector 的 metrics
   - Collector 的健康检查

### 5. 故障排查

#### Collector 问题

```bash
# 查看 Collector 日志
docker-compose logs otel-collector

# 检查 Collector health
curl http://localhost:13133/health

# 查看 Collector metrics
curl http://localhost:8888/metrics
```

#### 服务未收到数据

1. 检查服务配置的 Collector endpoint
2. 检查网络连接
3. 查看 Collector 日志中的错误
4. 验证 Collector 配置正确

#### Grafana 看不到数据

1. 检查数据源配置
2. 验证后端存储（Tempo/Loki/Prometheus）运行正常
3. 检查时间范围选择
4. 查看浏览器控制台的错误

## 学习资源

- [OpenTelemetry 官方文档](https://opentelemetry.io/docs/)
- [W3C Trace Context 规范](https://www.w3.org/TR/trace-context/)
- [Grafana 文档](https://grafana.com/docs/)
- [PromQL 教程](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [LogQL 教程](https://grafana.com/docs/loki/latest/logql/)

## 常见问题

### Q: 为什么需要 OpenTelemetry Collector？

A: Collector 提供了：
- 统一的数据收集点
- 数据处理和转换能力
- 与后端解耦，易于切换
- 采样、批处理等性能优化

### Q: 自动埋点 vs 手动埋点？

A:
- **自动埋点**: 快速开始，零代码侵入，覆盖常见框架
- **手动埋点**: 更精细的控制，业务指标，自定义 span

建议：先用自动埋点快速开始，然后在关键路径添加手动埋点。

### Q: 如何确保 Context 传播？

A:
1. 使用支持 context 传播的 HTTP 客户端
2. 在日志中注入 trace context
3. 异步任务中显式传递 context
4. 使用标准的 propagator（W3C Trace Context）

### Q: 生产环境采样率如何设置？

A: 建议：
- 从 1-10% 开始
- 关键业务路径 100%
- 使用 Tail-based sampling 保留错误和慢请求
- 监控采样后的数据量和成本
