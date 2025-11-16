# 可观测性实战演示：使用 Grafana 诊断混沌工程问题

## 演讲时长：15-20 分钟

---

## 📋 演示准备清单

### 提前准备（演讲前 5 分钟）

```bash
# 1. 启动所有服务
make start

# 2. 确认服务健康
make status

# 3. 打开浏览器标签页
# Tab 1: Grafana Dashboard (http://localhost:3000)
#        登录: admin/admin
#        找到 "4 Golden Signals" Dashboard
# Tab 2: Grafana Explore - Tempo (追踪)
# Tab 3: Grafana Explore - Loki (日志)
# Tab 4: Grafana Explore - Prometheus (指标)

# 4. 准备终端窗口
# Terminal 1: K6 负载测试
# Terminal 2: Pumba 混沌工程
# Terminal 3: 日志监控
```

---

## 🎤 演讲大纲

### 第一部分：开场和背景介绍 (2 分钟)

#### 演讲要点

> "今天我要展示的是，当系统出现问题时，如何使用可观测性工具快速定位和诊断问题。"

**三个关键要素：**

1. **Grafana Dashboard** - 统一的可视化平台
   - Metrics (Prometheus) - 系统指标
   - Logs (Loki) - 日志分析
   - Traces (Tempo) - 分布式追踪

2. **K6** - 负载测试工具
   - 模拟真实用户流量
   - 验证系统性能

3. **Pumba** - 混沌工程工具
   - 模拟真实故障场景
   - 测试系统韧性

---

### 第二部分：系统架构介绍 (2 分钟)

#### 演讲要点

> "这是一个典型的微服务架构系统"

```
用户请求 → API Gateway → Service A → Service D
                           ↓         ↓
                      Third-Party  Service B → Kafka → Service C
                           ↓
                      PostgreSQL
```

**关键点：**
- 4 个微服务 (API Gateway, Service A, B, C, D)
- 1 个数据库 (PostgreSQL)
- 1 个消息队列 (Kafka)
- OpenTelemetry 统一采集遥测数据

**展示 Dashboard：**
- 打开 Grafana "4 Golden Signals" Dashboard
- 简单介绍 4 个核心指标：
  1. Traffic (流量) - 请求率
  2. Errors (错误) - 错误率
  3. Latency (延迟) - 响应时间
  4. Saturation (饱和度) - 资源使用率

---

## 🎬 第三部分：核心演示场景 (10-12 分钟)

### 场景 1：建立基准线 - 正常系统状态 (2 分钟)

#### 操作步骤

```bash
# Terminal 1: 执行烟雾测试
make k6-smoke
```

#### 演讲要点

> "首先，我们要建立一个基准线，看看系统在正常状态下的表现"

**在 Grafana Dashboard 观察：**

1. **Traffic Panel (流量)**
   - "你可以看到请求率稳定在 1-2 RPS"

2. **Error Rate Panel (错误率)**
   - "错误率接近 0%，这是健康的"

3. **Latency Panel (延迟)**
   - "P95 响应时间约 200-500ms"

4. **切换到 Explore → Loki**
   ```logql
   {container_name="api-gateway"} | json
   ```
   - "可以看到正常的访问日志"

**关键信息：**
- 记录下正常的性能指标
- 这些数据将作为后续对比的基准

---

### 场景 2：网络延迟问题诊断 (3-4 分钟)

#### 操作步骤

```bash
# Terminal 1: 启动持续负载测试
make k6-load

# 等待 30 秒，让负载稳定...

# Terminal 2: 注入网络延迟
make chaos-network-delay
```

#### 演讲要点

> "现在我们模拟一个常见的问题：网络延迟。Pumba 会给所有服务注入 500ms ± 100ms 的延迟"

**在 Grafana Dashboard 实时观察：**

1. **Latency Panel 响应时间飙升** (30-60 秒后)
   - "看！P95 延迟从 500ms 暴增到 1.5-2 秒"
   - "这表示系统响应明显变慢"

2. **Error Rate 可能增加**
   - "部分请求可能因为超时而失败"

3. **Traffic 可能下降**
   - "因为响应变慢，请求处理速度下降"

#### 根因分析演示

> "现在我们来分析根因，找出到底是哪个服务变慢了"

**步骤 1：查看 Traces**

```bash
# 切换到 Grafana Explore → Tempo
# 搜索条件：duration > 1s
```

- "我们找到一个慢的 trace，点进去看详情"
- "展开后可以看到每个 span 的耗时"
- "注意看！Service A → Service B 的调用耗时超过 500ms"
- "Service B → Database 的调用也很慢"

**步骤 2：关联日志**

```bash
# 从 Trace 详情页面，点击 "Logs for this span"
# 或在 Loki 中查询：
{container_name="service-a"} | json | trace_id="<复制的trace_id>"
```

- "通过 trace_id 我们可以找到所有相关日志"
- "日志中可能会显示网络超时或重试的信息"

**步骤 3：查看 Metrics**

```bash
# 在 Prometheus 中查询：
histogram_quantile(0.95,
  sum(rate(http_server_duration_milliseconds_bucket{job=~"o11y-lab/service-a"}[5m]))
  by (le)
)
```

- "Metrics 也证实了 Service A 的响应时间增加"

#### 结论

> "通过 Logs、Metrics、Traces 三者关联，我们确认了是网络延迟导致的性能问题"

```bash
# 停止混沌测试
make chaos-stop
```

---

### 场景 3：服务崩溃和 503 错误 (3-4 分钟)

#### 操作步骤

```bash
# Terminal 1: 负载测试继续运行
make k6-load

# Terminal 2: 模拟服务崩溃
make chaos-503-errors

# Terminal 3: 实时查看日志
docker compose logs -f api-gateway | grep -E "ERROR|503"
```

#### 演讲要点

> "这个场景更严重：Service D 每 15 秒被强制杀死一次，模拟服务崩溃"

**在 Grafana Dashboard 观察：**

1. **Error Rate Panel 暴增**
   - "错误率从 0% 飙升到 40-60%！"
   - "这是严重的生产事故级别"

2. **Traffic Panel 可能波动**
   - "请求处理出现间歇性中断"

3. **Terminal 3 日志输出**
   - "可以看到大量的 503 Service Unavailable 错误"

#### 根因分析演示

**步骤 1：查看错误分布**

```bash
# Grafana Explore → Loki
{container_name="api-gateway"} |= "503" | json | line_format "{{.timestamp}} {{.level}} {{.msg}}"
```

- "所有 503 错误都来自 API Gateway"
- "错误信息显示：调用 Service A → Service D 失败"

**步骤 2：查看失败的 Traces**

```bash
# Tempo 搜索条件：
# status = error
# 或 duration > 0ms AND error = true
```

- "找到一个失败的 trace"
- "展开后可以清楚看到：Service D 的 span 标记为错误"
- "错误信息：Connection refused 或 Service Unavailable"

**步骤 3：关联系统事件**

```bash
# 查看容器状态
docker compose ps service-d
# 会看到 service-d 不断重启
```

- "从容器状态可以确认 Service D 确实在崩溃重启"

**步骤 4：查看级联影响**

```bash
# Prometheus 查询所有服务的错误率
sum by (service_name) (
  rate(http_server_duration_milliseconds_count{http_status_code=~"5.."}[5m])
)
```

- "可以看到虽然 Service D 崩溃，但错误传播到了上游服务"
- "API Gateway 和 Service A 都受到影响"

#### 结论

> "通过 Grafana 的三大支柱，我们快速定位到：
> 1. 问题源头：Service D 崩溃
> 2. 影响范围：整个请求链路
> 3. 错误类型：503 Service Unavailable"

```bash
# 停止混沌测试
make chaos-stop
```

---

### 场景 4：数据库故障和级联错误 (3-4 分钟)

#### 操作步骤

```bash
# Terminal 1: 负载测试
make k6-load

# Terminal 2: 模拟数据库故障
make chaos-500-errors
```

#### 演讲要点

> "最后一个场景：数据库故障。PostgreSQL 每 45 秒暂停 30 秒"

**在 Grafana Dashboard 观察：**

1. **Error Rate Panel 呈现周期性尖峰**
   - "注意！错误率呈现规律的波动"
   - "每 45 秒出现一次错误高峰"

2. **Latency Panel 也呈现周期性**
   - "数据库暂停时，查询会卡住导致延迟飙升"

#### 根因分析演示

**步骤 1：观察错误模式**

```bash
# Loki 查询
{container_name="service-a"} |= "database" |= "error" | json
```

- "可以看到 'database connection timeout' 错误"
- "错误周期性出现，说明是间歇性故障"

**步骤 2：查看 Traces 的错误 Span**

- "失败的 trace 显示：Service A → PostgreSQL 的调用失败"
- "Span 上有明确的错误标签：db.operation timeout"

**步骤 3：验证数据库指标**

```bash
# 检查数据库容器状态
docker compose logs postgres --tail=50
```

- "日志可能显示连接被拒绝或超时"

#### 结论

> "这是一个典型的级联故障：
> - 根因：数据库不可用
> - 影响：Service A 的所有需要数据库的操作失败
> - 传播：API Gateway 返回 500 错误给客户端"

```bash
# 停止混沌测试
make chaos-stop
```

---

## 🎯 第四部分：总结和要点 (2 分钟)

### 核心要点

#### 1. 可观测性三大支柱的协同价值

| 支柱 | 作用 | 示例 |
|------|------|------|
| **Metrics** | 发现问题 | 错误率飙升、延迟增加 |
| **Traces** | 定位问题 | 哪个服务、哪个调用慢/失败 |
| **Logs** | 诊断细节 | 具体错误信息、堆栈追踪 |

> "三者缺一不可：Metrics 告诉你有问题，Traces 告诉你在哪里，Logs 告诉你为什么"

#### 2. 关联性是关键

- **Trace ID** - 串联整个请求的所有日志和 spans
- **Service Name** - 关联同一服务的所有 metrics
- **Timestamp** - 时间对齐，查看同一时刻的不同信号

> "OpenTelemetry 的自动注入确保了这些关联字段的一致性"

#### 3. 混沌工程验证系统韧性

今天演示的故障场景都是生产环境的真实写照：
- 网络延迟 → 跨数据中心调用、网络拥塞
- 服务崩溃 → OOM、Panic、资源耗尽
- 数据库故障 → 主从切换、连接池耗尽

> "通过 Pumba 在测试环境提前发现问题，避免生产事故"

#### 4. 快速响应的工作流

```
监控告警 → 查看 Dashboard → 识别异常指标
    ↓
查找相关 Traces → 定位慢/失败的服务
    ↓
关联 Logs → 查看具体错误信息
    ↓
验证修复 → 再次观察 Metrics 恢复
```

---

## 💡 观众 Q&A 准备

### 常见问题

**Q1: 如果没有 OpenTelemetry，能实现这样的关联吗？**

A: 可以，但需要手动在每个服务中：
- 传播 trace context (通过 HTTP headers)
- 在日志中注入 trace_id
- 统一 metrics 标签命名

OpenTelemetry 的价值在于标准化和自动化这些流程。

**Q2: Grafana Dashboard 需要手动配置吗？**

A: 这个项目使用了 Grafana Provisioning，Dashboard 和数据源配置都是代码化的，服务启动时自动加载。

**Q3: 实际生产环境的 trace 量会很大吗？**

A: 是的，所以需要采样策略：
- 头部采样：只采集部分请求 (如 1%)
- 尾部采样：只保留慢请求和错误请求
- 这个项目使用 100% 采样，仅用于演示

**Q4: Pumba 会不会影响生产环境？**

A: Pumba 只应该在测试环境使用！它是通过 Docker API 控制容器，生产环境应该：
- 使用 Chaos Mesh、Litmus 等 Kubernetes 原生工具
- 有更细粒度的权限控制和安全防护

---

## 🎬 演示后的清理

```bash
# 停止所有混沌测试
make chaos-stop
make chaos-clean

# 可选：重启所有服务确保干净状态
make restart

# 或完全停止
make stop
```

---

## 📚 补充材料（演讲后分享）

### 在线资源
- 项目 GitHub: https://github.com/tedmax100/o11y_lab_for_dummies
- 互动教学: https://tedmax100.github.io/o11y_lab_for_dummies/

### 快速入门文档
- `docs/ERROR_RATE_QUICK_DEMO.md` - 5 分钟错误演示
- `docs/HTTP_ERROR_SIMULATION_GUIDE.md` - 完整 HTTP 错误模拟指南
- `k6/QUICKSTART.md` - K6 负载测试快速入门

### 实践建议

1. **Clone 项目后按顺序尝试：**
   ```bash
   make start          # 启动服务
   make k6-smoke       # 烟雾测试
   make k6-load        # 负载测试
   make chaos-network-delay  # 混沌测试
   ```

2. **在 Grafana 中探索：**
   - 熟悉 4 Golden Signals Dashboard
   - 尝试自定义查询
   - 练习 Logs/Metrics/Traces 之间的跳转

3. **修改代码实验：**
   - 添加自定义 metrics
   - 增加业务日志
   - 调整 trace 采样率

---

## ⏱️ 时间控制建议

| 环节 | 时间 | 可压缩 |
|------|------|--------|
| 开场 + 架构介绍 | 4 分钟 | 可压缩至 2 分钟 |
| 场景 1: 基准线 | 2 分钟 | 可跳过直接进场景 2 |
| 场景 2: 网络延迟 | 4 分钟 | 核心场景，不建议压缩 |
| 场景 3: 服务崩溃 | 4 分钟 | 核心场景，不建议压缩 |
| 场景 4: 数据库故障 | 3 分钟 | 可压缩至 2 分钟或跳过 |
| 总结 | 2 分钟 | 必须保留 |
| Q&A | 弹性 | 根据时间调整 |

**建议：** 根据观众技术背景调整深度
- 技术新手：重点展示现象，少讲原理
- 资深工程师：深入根因分析，讲解关联机制

---

## 🎤 演讲技巧

1. **提前彩排**
   - 完整跑一遍流程，确保时间控制
   - 测试网络连接和投影效果

2. **备用方案**
   - 如果演示出错，准备截图作为备份
   - 提前录制演示视频

3. **互动技巧**
   - "大家可以看到..." - 引导观众注意屏幕重点
   - "注意这里的变化..." - 创造悬念和期待
   - "这是不是很神奇？" - 与观众互动

4. **故事化叙述**
   - 不要只是操作命令，要讲故事：
     "假设现在是凌晨 3 点，你接到告警电话，生产环境错误率飙升..."

---

祝演讲成功！
