# OpenTelemetry Observability Lab - 项目总结

## 项目概述

这是一个完整的 OpenTelemetry 可观测性实验室，用于学习和演示如何实现 **Logs、Metrics、Traces 三大支柱的完整关联**。

## 核心价值

### 1. 完整的端到端演示

- ✅ 从请求入口到多层服务调用
- ✅ 同步调用 (HTTP) 和异步调用 (Kafka) 的追踪
- ✅ 数据库操作的自动埋点
- ✅ 第三方 API 调用的追踪

### 2. 两种埋点方式对比

- **自动埋点**: Service A, D (Python) - 零代码侵入
- **手动埋点**: Service B, C (Go) - 精细控制

### 3. 真实的 Context Propagation

- HTTP Headers 传播 (W3C Trace Context)
- Kafka Messages 传播
- 跨语言传播 (Python ↔ Go)

### 4. 三大支柱关联

```
Trace ID = 统一标识符
    │
    ├─→ Traces (Tempo)
    │    └─ 完整的调用链路
    │
    ├─→ Logs (Loki)
    │    └─ 结构化日志含 trace_id
    │
    └─→ Metrics (Prometheus)
         └─ Exemplars 关联到 traces
```

## 技术栈

### 应用层
- **Python**: FastAPI (API Gateway, Service A), Flask (Service D)
- **Go**: Gin (Service B, Service C)
- **PostgreSQL**: 关系型数据库
- **Kafka**: 消息队列

### 可观测性层
- **OpenTelemetry Collector**: 数据收集和处理
- **Tempo**: 分布式追踪后端
- **Loki**: 日志聚合后端
- **Prometheus**: 时序数据库
- **Grafana**: 统一可视化平台

### 编排层
- **Docker Compose**: 本地开发
- **Kubernetes**: 生产环境 (with Operator)

## 项目结构

```
.
├── services/                    # 微服务代码
│   ├── api-gateway/            # 入口网关
│   ├── service-a/              # 核心业务服务 (Python)
│   ├── service-b/              # 消息生产者 (Go)
│   ├── service-c/              # 消息消费者 (Go)
│   └── service-d/              # 计算服务 (Python)
│
├── otel-collector/             # Collector 配置
│   └── config.yaml
│
├── k8s/                        # Kubernetes 部署
│   ├── namespace.yaml
│   ├── operator/               # OpenTelemetry Operator
│   ├── services/               # 服务部署
│   └── observability/          # 可观测性栈
│
├── grafana/                    # Grafana 配置
│   ├── datasources/            # 数据源配置
│   ├── dashboards/             # Dashboard 配置
│   ├── tempo-config.yaml
│   └── prometheus.yaml
│
├── docker-compose.yaml         # Docker Compose 配置
├── Makefile                    # 常用命令
├── start.sh                    # 快速启动脚本
│
├── README.md                   # 项目介绍
├── USAGE.md                    # 使用指南
├── ARCHITECTURE.md             # 架构说明
└── CONTRIBUTING.md             # 贡献指南
```

## 核心特性

### 1. 自动埋点 (Service A, D)

```python
# 只需添加几行配置代码
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

FastAPIInstrumentor.instrument_app(app)
# 自动追踪所有 HTTP 请求
# 自动追踪数据库查询
# 自动注入和提取 trace context
```

### 2. 手动埋点 (Service B, C)

```go
// 精细控制业务逻辑的埋点
ctx, span := tracer.Start(ctx, "business_operation")
defer span.End()

span.SetAttributes(
    attribute.String("business.key", "value"),
)

// 自定义 metrics
counter.Add(ctx, 1, metric.WithAttributes(...))
```

### 3. 结构化日志

所有服务统一使用 JSON 格式日志:

```json
{
  "time": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "service": "service-a",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "message": "Processing request"
}
```

### 4. Kafka 追踪

完整追踪异步消息:

```
Service A → Service B → Kafka → Service C
          (producer)   (queue)   (consumer)
                 └──── 同一个 trace ────┘
```

### 5. Grafana 关联跳转

- **从日志跳转到 Trace**: 点击日志中的 trace_id
- **从 Metric 跳转到 Trace**: 点击图表上的 exemplar
- **从 Trace 跳转到日志**: 在 span 详情中查看相关日志

## 学习路径

### 入门 (Day 1)

1. 运行 `./start.sh` 启动所有服务
2. 发送测试请求: `curl http://localhost:8080/api/process`
3. 在 Grafana 中查看 traces、logs、metrics
4. 理解三者如何通过 trace_id 关联

### 进阶 (Day 2-3)

1. 查看各服务的代码实现
2. 理解自动埋点和手动埋点的差异
3. 学习如何添加自定义 span 和 metrics
4. 理解 context propagation 的机制

### 高级 (Day 4-5)

1. 修改采样率，观察数据量变化
2. 添加新的服务并集成 OpenTelemetry
3. 在 Kubernetes 中部署 (使用 Operator)
4. 自定义 Collector 的 processors

## 实际应用场景

### 1. 性能优化

- 找出最慢的服务调用
- 识别数据库查询瓶颈
- 优化关键路径

### 2. 故障排查

- 通过 trace 定位错误发生的位置
- 查看错误时的完整上下文
- 从 metrics 告警追溯到具体请求

### 3. 业务分析

- 统计各接口的调用量
- 分析用户行为路径
- 监控业务指标

## 生产环境建议

### 1. 采样策略

```yaml
# 在 Collector 中配置 tail-based sampling
processors:
  tail_sampling:
    policies:
      - name: error-traces
        type: status_code
        status_code: {status_codes: [ERROR]}
      - name: slow-traces
        type: latency
        latency: {threshold_ms: 1000}
      - name: random-sample
        type: probabilistic
        probabilistic: {sampling_percentage: 10}
```

### 2. 资源配置

```yaml
# OpenTelemetry Collector
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### 3. 数据保留

- **Tempo**: 保留 7-30 天
- **Loki**: 保留 7-14 天
- **Prometheus**: 保留 15-30 天

### 4. 高可用部署

```
┌────────────────────────────────┐
│  Application Services (N)      │
└────────────┬───────────────────┘
             ▼
┌────────────────────────────────┐
│  Collector Instances (N)       │
│  with Load Balancer            │
└────────────┬───────────────────┘
             ▼
┌────────────────────────────────┐
│  Backend Storage (HA)          │
│  - Tempo (S3/GCS)             │
│  - Loki (S3/GCS)              │
│  - Prometheus (HA Pair)        │
└────────────────────────────────┘
```

## 性能影响

### 轻量级

- 自动埋点: ~1-5% CPU 开销
- 手动埋点: ~0.5-2% CPU 开销
- 推荐采样率: 1-10%

### 优化技巧

1. 使用 Batch Processor 批量发送
2. 启用 Memory Limiter 防止 OOM
3. 合理设置采样率
4. 异步导出数据

## 扩展建议

### 1. 添加更多服务

- gRPC 服务
- WebSocket 服务
- 定时任务

### 2. 集成更多工具

- APM 工具 (Jaeger, Zipkin)
- 告警系统 (Alertmanager)
- 可视化工具 (Kibana)

### 3. 高级特性

- Baggage 传播业务上下文
- Custom Sampler 实现
- Dynamic Configuration

## 常见问题

### Q: 为什么选择 OpenTelemetry？

A:
- **厂商中立**: 避免供应商锁定
- **标准化**: W3C 标准支持
- **完整性**: 覆盖 logs/metrics/traces
- **社区活跃**: CNCF 孵化项目

### Q: 生产环境成本如何？

A:
- **开源方案**: 本项目展示的栈完全免费
- **云服务**: Grafana Cloud, AWS X-Ray 等按量付费
- **混合方案**: 本地 Collector + 云端存储

### Q: 如何从现有监控迁移？

A:
1. 并行运行新旧系统
2. 逐步迁移服务
3. 验证数据一致性
4. 切换并下线旧系统

## 贡献者

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License

## 参考资料

- [OpenTelemetry 官方文档](https://opentelemetry.io/docs/)
- [OpenTelemetry Operator](https://github.com/open-telemetry/opentelemetry-operator)
- [Grafana Documentation](https://grafana.com/docs/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)

---

**Happy Observability! 🚀**
