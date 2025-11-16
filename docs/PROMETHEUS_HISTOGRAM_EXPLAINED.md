# Prometheus Histogram 与 P99 延迟查询详解

## 问题：为什么 P99 延迟查询是这样的？

```promql
histogram_quantile(0.99, sum by(le) (rate(service_c_processing_duration_seconds_bucket[5m])))
```

---

## 第一部分：Histogram 的工作原理

### 1. 什么是 Histogram？

Histogram（直方图）是 Prometheus 中用于统计**数值分布**的指标类型，特别适合测量延迟、请求大小等。

在你的项目中，Service C 定义了这个 histogram：

```go
// services/service-c/main.go:526
processingDuration, err = meter.Float64Histogram(
    "service_c_processing_duration_seconds",
    metric.WithDescription("Duration of message processing"),
    metric.WithUnit("s"),
)
```

每次处理消息后，记录耗时：

```go
// services/service-c/main.go:381
duration := time.Since(start).Seconds()  // 例如: 0.234 秒
processingDuration.Record(ctx, duration, ...)
```

---

### 2. Histogram 如何存储数据？

当你创建一个 histogram 后，Prometheus 实际上会生成 **3 个时间序列**：

| 指标名称 | 类型 | 含义 | 示例值 |
|---------|------|------|--------|
| `service_c_processing_duration_seconds_bucket{le="0.005"}` | Counter | 耗时 ≤ 0.005秒 的请求数 | 10 |
| `service_c_processing_duration_seconds_bucket{le="0.01"}` | Counter | 耗时 ≤ 0.01秒 的请求数 | 25 |
| `service_c_processing_duration_seconds_bucket{le="0.025"}` | Counter | 耗时 ≤ 0.025秒 的请求数 | 50 |
| `service_c_processing_duration_seconds_bucket{le="0.05"}` | Counter | 耗时 ≤ 0.05秒 的请求数 | 80 |
| `service_c_processing_duration_seconds_bucket{le="0.1"}` | Counter | 耗时 ≤ 0.1秒 的请求数 | 150 |
| `service_c_processing_duration_seconds_bucket{le="0.25"}` | Counter | 耗时 ≤ 0.25秒 的请求数 | 300 |
| `service_c_processing_duration_seconds_bucket{le="0.5"}` | Counter | 耗时 ≤ 0.5秒 的请求数 | 450 |
| `service_c_processing_duration_seconds_bucket{le="1"}` | Counter | 耗时 ≤ 1秒 的请求数 | 480 |
| `service_c_processing_duration_seconds_bucket{le="+Inf"}` | Counter | 所有请求（无限大） | 500 |
| `service_c_processing_duration_seconds_sum` | Counter | 所有请求耗时总和 | 123.45 |
| `service_c_processing_duration_seconds_count` | Counter | 请求总数 | 500 |

**关键点：**
- `le` 标签表示 "less than or equal to"（小于等于）
- 每个 bucket 是**累积的**（累计计数）
- `+Inf` bucket 的值 = 总请求数

---

### 3. 可视化示例

假设处理了 10 个 Kafka 消息，耗时分别为（秒）：
```
0.003, 0.008, 0.015, 0.032, 0.067, 0.123, 0.234, 0.456, 0.678, 1.234
```

Histogram 的 bucket 统计结果：

```
le="0.005":  1  ← 1 个请求 ≤ 0.005s (0.003)
le="0.01":   2  ← 2 个请求 ≤ 0.01s  (0.003, 0.008)
le="0.025":  3  ← 3 个请求 ≤ 0.025s (0.003, 0.008, 0.015)
le="0.05":   4  ← 4 个请求 ≤ 0.05s  (前面 3 个 + 0.032)
le="0.1":    5  ← 5 个请求 ≤ 0.1s   (前面 4 个 + 0.067)
le="0.25":   7  ← 7 个请求 ≤ 0.25s  (前面 5 个 + 0.123, 0.234)
le="0.5":    8  ← 8 个请求 ≤ 0.5s   (前面 7 个 + 0.456)
le="1":      9  ← 9 个请求 ≤ 1s     (前面 8 个 + 0.678)
le="+Inf":  10  ← 所有 10 个请求
```

---

## 第二部分：逐步拆解查询

现在我们来拆解这个查询的每一部分：

```promql
histogram_quantile(0.99, sum by(le) (rate(service_c_processing_duration_seconds_bucket[5m])))
```

---

### 步骤 1: `service_c_processing_duration_seconds_bucket[5m]`

**含义：** 获取最近 5 分钟内的所有 bucket 时间序列。

**输出：** 原始的 counter 值（累计计数）

```
service_c_processing_duration_seconds_bucket{le="0.005"} → [120, 122, 125, 128, ...]
service_c_processing_duration_seconds_bucket{le="0.01"}  → [245, 250, 255, 260, ...]
service_c_processing_duration_seconds_bucket{le="0.025"} → [500, 510, 520, 530, ...]
...
```

---

### 步骤 2: `rate(...[5m])`

**含义：** 计算每秒的增长率（即每秒处理多少请求落在每个 bucket）

**为什么需要 rate？**
- Histogram bucket 是 **Counter** 类型，值只增不减
- 我们需要知道的是"最近的速率"，而不是从程序启动以来的累计值
- `rate()` 会自动处理 counter 重置（如服务重启）

**公式：**
```
rate(metric[5m]) = (当前值 - 5分钟前的值) / 时间间隔（秒）
```

**输出：** 每秒的请求分布

```
service_c_processing_duration_seconds_bucket{le="0.005"} → 2.3  (每秒 2.3 个请求 ≤ 0.005s)
service_c_processing_duration_seconds_bucket{le="0.01"}  → 5.1  (每秒 5.1 个请求 ≤ 0.01s)
service_c_processing_duration_seconds_bucket{le="0.025"} → 8.7  (每秒 8.7 个请求 ≤ 0.025s)
...
service_c_processing_duration_seconds_bucket{le="+Inf"} → 10.0 (每秒总共 10 个请求)
```

---

### 步骤 3: `sum by(le) (...)`

**含义：** 按 `le` 标签分组求和，合并其他所有标签。

**为什么需要 sum by(le)？**

如果你的 histogram 有多个标签维度（如 `operation` 标签），会产生多个时间序列：

```
service_c_processing_duration_seconds_bucket{le="0.1", operation="process_message"} → 5.0
service_c_processing_duration_seconds_bucket{le="0.1", operation="validate"}        → 3.0
```

`sum by(le)` 会把相同 `le` 的所有时间序列合并：

```
service_c_processing_duration_seconds_bucket{le="0.1"} → 8.0  (5.0 + 3.0)
```

**在你的项目中：**
- Service C 的 histogram 记录时带了 `operation="process_message"` 标签
- 如果未来有多种操作类型，`sum by(le)` 会合并它们
- 如果只有一个操作，这一步不会改变结果

**输出：** 按 bucket 聚合后的速率

```
{le="0.005"} → 2.3
{le="0.01"}  → 5.1
{le="0.025"} → 8.7
{le="0.05"}  → 9.2
{le="0.1"}   → 9.8
{le="+Inf"}  → 10.0
```

---

### 步骤 4: `histogram_quantile(0.99, ...)`

**含义：** 计算 P99 分位数（99% 的请求延迟小于等于这个值）

**工作原理：**

`histogram_quantile` 使用 **线性插值** 估算分位数：

1. 确定目标排名：`0.99 × 总请求数 = 0.99 × 10 = 9.9`（即第 9.9 个请求）

2. 找到包含第 9.9 个请求的 bucket 区间：
   ```
   le="0.5":  8 个请求  ← 第 8 个请求在这里
   le="1":    9 个请求  ← 第 9 个请求在这里
   le="+Inf": 10 个请求 ← 第 10 个请求在这里
   ```

   第 9.9 个请求在 `le="1"` 和 `le="+Inf"` 之间

3. 线性插值计算精确值：
   ```
   下界 = 1 秒 (le="1" 的上限)
   上界 = +Inf (实际取前一个 bucket 的上限，这里简化处理)

   P99 ≈ 1 + (9.9 - 9) / (10 - 9) × (上界 - 1)
   ```

**注意：** 这是**估算**，不是精确值！因为我们丢失了原始数据，只保留了分布统计。

---

## 第三部分：完整示例

### 场景：观察 Service C 的 Kafka 消息处理延迟

#### 数据收集（5 分钟内）

```go
// Service C 每处理一条消息都会记录：
processingDuration.Record(ctx, 0.123, ...)  // 第 1 条消息: 0.123 秒
processingDuration.Record(ctx, 0.089, ...)  // 第 2 条消息: 0.089 秒
processingDuration.Record(ctx, 0.234, ...)  // 第 3 条消息: 0.234 秒
// ... 总共处理了 5000 条消息
```

#### Prometheus 查询

```promql
histogram_quantile(0.99,
  sum by(le) (
    rate(service_c_processing_duration_seconds_bucket[5m])
  )
)
```

#### 执行过程

1. **rate()** 计算每秒的请求分布：
   ```
   {le="0.1"}   → 8.5  req/s
   {le="0.25"}  → 16.3 req/s
   {le="0.5"}   → 16.5 req/s  ← P99 可能在这里
   {le="1"}     → 16.6 req/s
   {le="+Inf"}  → 16.67 req/s (总速率)
   ```

2. **计算 P99 位置：** `0.99 × 16.67 = 16.5033`

3. **插值计算：** P99 在 `le="0.5"` 附近，最终结果可能是 **0.48 秒**

#### 在 Grafana 中的显示

```
Kafka Processing P99 Latency: 480ms
```

这意味着：**99% 的 Kafka 消息处理时间 ≤ 480ms**

---

## 第四部分：常见问题

### Q1: 为什么不直接用平均值？

平均值会被极端值（outliers）严重影响，不能反映大多数用户的体验。

**示例：**
- 99 个请求耗时 100ms
- 1 个请求耗时 10 秒（超时）

平均值 = (99 × 0.1 + 1 × 10) / 100 = **0.199 秒 (199ms)**
P99 = **100ms** ← 更能反映 99% 用户的真实体验

---

### Q2: 为什么不用 `_sum` 和 `_count` 计算？

`_sum / _count` 只能算平均值，无法得到分位数（P95、P99）。

要计算分位数，必须知道数值分布，这就是为什么需要 `_bucket`。

---

### Q3: bucket 边界如何确定？

OpenTelemetry SDK 默认使用**指数分桶**（exponential buckets）：

```
[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, 7.5, 10, ...]
```

你也可以自定义 bucket：

```go
processingDuration, err = meter.Float64Histogram(
    "service_c_processing_duration_seconds",
    metric.WithExplicitBucketBoundaries(0.01, 0.05, 0.1, 0.5, 1, 2, 5),
)
```

**建议：** 根据业务场景调整 bucket，确保覆盖大部分请求的延迟范围。

---

### Q4: `[5m]` 时间窗口如何选择？

| 时间窗口 | 优点 | 缺点 | 适用场景 |
|---------|------|------|---------|
| `[1m]` | 快速反应最新变化 | 数据波动大、不平滑 | 实时故障检测 |
| `[5m]` | 平衡响应速度和稳定性 | 中等延迟 | **推荐：一般监控** |
| `[15m]` | 平滑、稳定 | 反应慢，可能错过短暂问题 | 长期趋势分析 |

**你的项目使用 `[5m]`，这是最常见的选择。**

---

### Q5: P99 vs P95 vs P50，该用哪个？

| 分位数 | 含义 | 适用场景 |
|-------|------|---------|
| **P50 (中位数)** | 50% 的请求 ≤ 该值 | 了解典型用户体验 |
| **P95** | 95% 的请求 ≤ 该值 | 平衡性能和成本 |
| **P99** | 99% 的请求 ≤ 该值 | 严格 SLA、关键业务 |
| **P99.9** | 99.9% 的请求 ≤ 该值 | 极端性能要求（金融交易等） |

**建议：**
- 日常监控：**P95**
- SLA 承诺：**P99**
- 用户体验优化：同时看 **P50 + P95 + P99**

---

## 第五部分：在你的项目中验证

### 实验 1：查看原始 bucket 数据

```bash
# 启动服务
make start

# 运行负载测试
make k6-load

# 在 Grafana Explore → Prometheus 中查询：
```

**查询 1：查看所有 bucket**
```promql
service_c_processing_duration_seconds_bucket
```

你会看到类似：
```
service_c_processing_duration_seconds_bucket{le="0.005"} 12
service_c_processing_duration_seconds_bucket{le="0.01"}  45
service_c_processing_duration_seconds_bucket{le="0.025"} 123
...
```

**查询 2：查看速率**
```promql
rate(service_c_processing_duration_seconds_bucket[5m])
```

**查询 3：计算 P99**
```promql
histogram_quantile(0.99, sum by(le) (rate(service_c_processing_duration_seconds_bucket[5m])))
```

---

### 实验 2：观察 Pumba 混沌测试对 P99 的影响

```bash
# Terminal 1: 负载测试
make k6-load

# Terminal 2: 注入网络延迟
make chaos-network-delay

# 在 Grafana Dashboard 观察 "Kafka Processing P99 Latency" Panel
# 你应该看到 P99 从 ~200ms 飙升到 ~700ms (500ms 延迟 + 原本的处理时间)
```

---

### 实验 3：对比不同分位数

在 Grafana 中创建多个查询：

```promql
# P50
histogram_quantile(0.50, sum by(le) (rate(service_c_processing_duration_seconds_bucket[5m])))

# P95
histogram_quantile(0.95, sum by(le) (rate(service_c_processing_duration_seconds_bucket[5m])))

# P99
histogram_quantile(0.99, sum by(le) (rate(service_c_processing_duration_seconds_bucket[5m])))
```

**观察：**
- 正常情况：P50 < P95 < P99，差距不大
- 出现问题：P99 飙升，但 P50 可能仍然正常（说明只有少数请求受影响）

---

## 第六部分：总结

### 查询结构总结

```
histogram_quantile(0.99,              ← 步骤 4: 计算 P99 分位数
  sum by(le) (                        ← 步骤 3: 按 bucket 聚合
    rate(                             ← 步骤 2: 计算每秒速率
      service_c_processing_duration_seconds_bucket  ← 步骤 1: 获取 bucket 数据
      [5m]                            ← 时间窗口
    )
  )
)
```

### 核心概念

1. **Histogram = 分布统计**
   - 用 buckets 记录数值分布
   - 牺牲精确度换取高性能（vs. 保存所有原始值）

2. **`_bucket` 后缀**
   - Histogram 的核心数据
   - Counter 类型，累积计数
   - 必须配合 `le` 标签使用

3. **`rate()` 函数**
   - 将累积值转换为速率
   - 处理 counter 重置
   - 反映最近的趋势

4. **`sum by(le)`**
   - 合并不同维度的 buckets
   - 保留 `le` 标签用于分位数计算

5. **`histogram_quantile()`**
   - 线性插值估算分位数
   - 精度取决于 bucket 划分

---

### 最佳实践

1. **监控黄金组合**
   ```promql
   # P50 - 中位数
   histogram_quantile(0.50, sum by(le) (rate(metric_bucket[5m])))

   # P95 - 日常监控
   histogram_quantile(0.95, sum by(le) (rate(metric_bucket[5m])))

   # P99 - SLA 告警
   histogram_quantile(0.99, sum by(le) (rate(metric_bucket[5m])))
   ```

2. **告警规则示例**
   ```yaml
   - alert: HighP99Latency
     expr: |
       histogram_quantile(0.99,
         sum by(le) (rate(service_c_processing_duration_seconds_bucket[5m]))
       ) > 1.0
     for: 5m
     annotations:
       summary: "Service C P99 延迟过高"
       description: "P99 延迟 {{ $value }}s，超过 1 秒阈值"
   ```

3. **Grafana Panel 配置**
   ```json
   {
     "targets": [
       {
         "expr": "histogram_quantile(0.99, sum by(le) (rate(service_c_processing_duration_seconds_bucket[5m])))",
         "legendFormat": "P99",
         "refId": "A"
       }
     ],
     "unit": "s",
     "thresholds": [
       { "value": 0.5, "color": "green" },
       { "value": 1.0, "color": "yellow" },
       { "value": 2.0, "color": "red" }
     ]
   }
   ```

---

## 延伸阅读

- [Prometheus Histogram 官方文档](https://prometheus.io/docs/concepts/metric_types/#histogram)
- [Histograms and Summaries](https://prometheus.io/docs/practices/histograms/)
- [OpenTelemetry Metrics SDK](https://opentelemetry.io/docs/specs/otel/metrics/sdk/)
- 你的项目中的实现：`services/service-c/main.go:526-533`

---

**希望这个文档帮助你理解了 Histogram 的工作原理！🎉**
