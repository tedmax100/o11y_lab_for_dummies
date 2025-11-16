# Service C P99 延迟异常诊断指南

## 问题：P99 延迟显示 4.95 秒

**预期值：** 100-300ms（代码中 `time.Sleep(100-300ms)`）
**实际值：** 4.95 秒
**结论：** 🔴 **严重异常，需要立即诊断！**

---

## 诊断步骤

### 步骤 1：检查是否有混沌测试正在运行 ⚡

混沌测试会注入延迟或杀死服务，这是最常见的原因！

```bash
# 检查运行中的 Pumba 容器
docker ps --filter "name=pumba-*"

# 如果有输出，说明混沌测试还在运行！
# 停止所有混沌测试
make chaos-stop
```

**常见混沌测试及其影响：**

| Pumba 命令 | 影响 | 预期 P99 延迟 |
|-----------|------|-------------|
| `chaos-network-delay` | 注入 500ms ± 100ms 延迟 | ~800ms - 1s |
| `chaos-504-errors` | 注入 35 秒延迟 | **35+ 秒** 🔴 |
| `chaos-database-outage` | 数据库延迟 2 秒 | ~2.5s |
| `chaos-cascading-errors` | Service B 延迟 5 秒 | 影响间接 |

**如果你刚运行过 `chaos-504-errors` 或类似命令，这就是根因！**

---

### 步骤 2：检查服务健康状态 🏥

```bash
# 查看所有服务状态
make status
# 或
docker compose ps

# 检查 Service C 是否在不断重启
docker compose logs service-c --tail=50 | grep -E "Starting|Stopping|Error"
```

**异常信号：**
- Service C 的 STATUS 不是 `Up`
- RESTART COUNT 不断增加
- 日志中有大量错误

---

### 步骤 3：查看实时日志 📋

```bash
# Terminal 1: 实时查看 Service C 日志
docker compose logs -f service-c

# Terminal 2: 发送测试请求
curl http://localhost:8080/api/process
```

**观察日志中的：**

1. **处理时间记录**
   ```json
   {"level":"INFO","msg":"Message processed successfully in 0.123s"}
   ```
   如果看到 `in 4.950s`，说明确实处理慢了。

2. **错误信息**
   ```
   Error fetching message: context deadline exceeded
   Failed to unmarshal message
   ```

3. **Kafka 连接问题**
   ```
   Error fetching message: kafka: broker connection lost
   ```

---

### 步骤 4：检查 Kafka 服务状态 📨

Service C 是 Kafka 消费者，如果 Kafka 有问题会导致延迟：

```bash
# 检查 Kafka 容器状态
docker compose ps kafka zookeeper

# 查看 Kafka 日志
docker compose logs kafka --tail=100

# 检查 Kafka 是否可连接
docker compose exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092
```

**常见问题：**
- Kafka 容器重启中
- Zookeeper 连接失败
- Topic `o11y-lab-events` 不存在

---

### 步骤 5：验证 Prometheus 数据 📊

在 Grafana Explore → Prometheus 中运行以下查询：

#### 查询 1：查看原始 bucket 分布

```promql
service_c_processing_duration_seconds_bucket
```

**正常输出：**
```
{le="0.1"}   → 100
{le="0.25"}  → 500
{le="0.5"}   → 500
{le="1"}     → 500
{le="+Inf"}  → 500
```

**异常输出：**
```
{le="0.1"}   → 0      ← 没有请求 < 0.1s！
{le="5"}     → 100
{le="10"}    → 500    ← 大部分请求都在 5-10 秒！
{le="+Inf"}  → 500
```

#### 查询 2：查看消息处理总数

```promql
service_c_messages_processed_total
```

**如果值是 0 或很小，说明：**
- Service C 没有收到 Kafka 消息
- 或者 Kafka 消费者没有启动

#### 查询 3：对比不同分位数

```promql
# P50 (中位数)
histogram_quantile(0.50, sum by(le) (rate(service_c_processing_duration_seconds_bucket[5m])))

# P95
histogram_quantile(0.95, sum by(le) (rate(service_c_processing_duration_seconds_bucket[5m])))

# P99
histogram_quantile(0.99, sum by(le) (rate(service_c_processing_duration_seconds_bucket[5m])))
```

**场景分析：**

| P50 | P95 | P99 | 诊断 |
|-----|-----|-----|------|
| 0.15s | 0.25s | **4.95s** | 极少数请求极慢（异常值/outlier） |
| 4.5s | 4.8s | **4.95s** | 所有请求都很慢（系统性问题） |
| 0.15s | 4.0s | **4.95s** | 约 5-10% 请求很慢（间歇性问题） |

---

### 步骤 6：检查网络和依赖服务 🌐

Service C 的处理流程：

```
Kafka → Service C → (无外部调用)
```

Service C 本身不调用其他服务，所以问题可能在：

1. **Kafka 网络延迟**
   ```bash
   # 检查 Kafka 到 Service C 的网络
   docker compose exec service-c ping -c 3 kafka
   ```

2. **Kafka 消息堆积**
   ```bash
   # 检查 Consumer Group Lag
   docker compose exec kafka kafka-consumer-groups.sh \
     --bootstrap-server localhost:9092 \
     --group service-c-consumer \
     --describe
   ```

   **如果 LAG 很大（如 10000+），说明消费跟不上生产速度。**

---

## 快速诊断命令集合

运行这个脚本快速收集信息：

```bash
#!/bin/bash
echo "=== 1. 检查混沌测试 ==="
docker ps --filter "name=pumba-*"

echo -e "\n=== 2. 服务状态 ==="
docker compose ps service-c kafka

echo -e "\n=== 3. Service C 最新日志 ==="
docker compose logs service-c --tail=20

echo -e "\n=== 4. 检查 Kafka Consumer Lag ==="
docker compose exec -T kafka kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group service-c-consumer \
  --describe 2>/dev/null || echo "Kafka 不可用"

echo -e "\n=== 5. Prometheus 数据检查 ==="
echo "手动在 Grafana Explore 中运行："
echo "  service_c_processing_duration_seconds_bucket"
```

保存为 `diagnose_p99.sh`，然后运行：

```bash
chmod +x diagnose_p99.sh
./diagnose_p99.sh
```

---

## 常见根因和解决方案

### 根因 1：混沌测试未停止 ⚡

**现象：**
- `docker ps` 看到 `pumba-504-errors` 或类似容器
- 日志中有 `35000ms delay` 等信息

**解决：**
```bash
make chaos-stop
make chaos-clean

# 等待 30 秒让系统恢复
sleep 30

# 重新查看 Grafana
```

---

### 根因 2：Kafka 连接问题 📨

**现象：**
- Service C 日志：`Error fetching message`
- Kafka 容器状态：`Restarting` 或 `Unhealthy`

**解决：**
```bash
# 重启 Kafka
docker compose restart kafka zookeeper

# 等待服务就绪
sleep 30

# 重启 Service C
docker compose restart service-c
```

---

### 根因 3：Histogram Bucket 配置问题 📊

**现象：**
- Prometheus 查询返回 `NaN` 或异常大的值
- Bucket 分布不合理

**检查代码（不太可能，但可以验证）：**

```go
// services/service-c/main.go:526
processingDuration, err = meter.Float64Histogram(
    "service_c_processing_duration_seconds",
    metric.WithDescription("Duration of message processing"),
    metric.WithUnit("s"),  // ← 确认单位是"秒"，不是"毫秒"
)
```

**验证记录逻辑：**

```go
// services/service-c/main.go:373-383
duration := time.Since(start).Seconds()  // ← 应该是 0.1-0.3 秒

processingDuration.Record(ctx, duration, ...)
```

如果这里记录的是毫秒（如 `123.45`），但单位标记为秒，就会导致 P99 异常高。

---

### 根因 4：数据样本不足 📉

**现象：**
- `service_c_messages_processed_total` = 0 或很小
- Grafana 显示 "No data"

**原因：**
- Service B 没有向 Kafka 发送消息
- Service C 的 Kafka 消费者没有启动

**验证：**
```bash
# 检查 Service B 是否正常
curl http://localhost:8002/health

# 手动触发一次完整流程
curl http://localhost:8080/api/process

# 查看 Service C 日志，应该看到 "Processing message from Kafka"
docker compose logs service-c --tail=10 | grep "Processing message"
```

---

### 根因 5：时间窗口问题 ⏱️

**现象：**
- P99 反映的是**过去 5 分钟**的数据
- 如果 3 分钟前运行了 `chaos-504-errors`，即使现在已停止，P99 仍然很高

**解决：**
- **等待 5-10 分钟**让旧数据滚出时间窗口
- 或修改查询时间窗口：
  ```promql
  # 改用 1 分钟窗口，更快反映当前状态
  histogram_quantile(0.99, sum by(le) (rate(service_c_processing_duration_seconds_bucket[1m])))
  ```

---

## 推荐诊断流程（按优先级）

### 🔴 紧急检查（1 分钟）

```bash
# 1. 停止所有混沌测试
make chaos-stop

# 2. 检查服务状态
docker compose ps
```

### 🟡 详细诊断（5 分钟）

```bash
# 3. 查看实时日志
docker compose logs -f service-c | grep -E "processed successfully|Error"

# 4. 在新终端发送测试请求
curl http://localhost:8080/api/process

# 5. 观察日志中的处理时间
```

### 🟢 深度分析（10 分钟）

```bash
# 6. 在 Grafana Explore 中查询
# - service_c_processing_duration_seconds_bucket
# - 对比 P50/P95/P99

# 7. 检查 Kafka Consumer Lag

# 8. 查看 Tempo Traces，找到慢的 trace 分析
```

---

## 预防措施

### 1. 添加告警

在 Grafana 或 Prometheus 中配置告警：

```yaml
- alert: ServiceCHighP99Latency
  expr: |
    histogram_quantile(0.99,
      sum by(le) (rate(service_c_processing_duration_seconds_bucket[5m]))
    ) > 1.0
  for: 2m
  annotations:
    summary: "Service C P99 延迟异常"
    description: "P99 延迟 {{ $value | humanizeDuration }}，预期 < 1s"
```

### 2. 监控 Kafka Consumer Lag

添加 Kafka Exporter 监控消费延迟：

```promql
kafka_consumergroup_lag{topic="o11y-lab-events"} > 1000
```

### 3. 定期清理混沌测试

```bash
# 在测试后立即运行
make chaos-stop
make chaos-clean
```

### 4. 使用混沌测试的超时机制

修改 Makefile 中的混沌测试，添加自动停止：

```makefile
chaos-network-delay:
	@echo "注入 5 分钟延迟，之后自动停止"
	docker run -d --name pumba-delay \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gaiaadm/pumba:latest \
		netem --duration 5m \  # ← 5 分钟后自动停止
		delay --time 500 ...
```

---

## 总结

**4.95 秒的 P99 延迟是严重异常，可能的原因：**

1. ⚡ **混沌测试未停止**（最可能，优先检查）
2. 📨 **Kafka 服务问题**
3. 🌐 **网络延迟或分区**
4. 📊 **Histogram 配置错误**（不太可能）
5. ⏱️ **时间窗口包含旧的异常数据**

**立即执行：**
```bash
make chaos-stop
docker compose ps
docker compose logs service-c --tail=20
```

**然后在 Grafana 中等待 5-10 分钟，观察 P99 是否恢复正常（< 0.5s）。**

如果问题持续，请分享：
1. `docker compose ps` 的输出
2. `docker compose logs service-c --tail=50` 的输出
3. Grafana Prometheus 查询 `service_c_processing_duration_seconds_bucket` 的结果
