# OpenTelemetry Observability Lab for Dummies

这是一个完整的 OpenTelemetry 可观测性实验室，展示如何使用 OpenTelemetry 实现 **Logs、Metrics、Traces 三者的关联**。

## 架构概览

```
API Gateway → Service A → Service D
              ↓         ↓
         Third-Party  Service B → Message Queue → Service C
              ↓
          Database (PostgreSQL)
```

## 技术栈

### 可观测性组件
- **OpenTelemetry Collector**: 统一收集和导出遥测数据
- **OpenTelemetry Operator**: Kubernetes 自动注入 (auto-instrumentation)
- **Grafana**: 统一可视化 Dashboard
- **Loki**: 日志存储和查询
- **Prometheus**: Metrics 存储和查询
- **Tempo**: 分布式追踪存储和查询

### 服务组件
- **API Gateway**: Python/FastAPI - 请求入口
- **Service A**: Python/FastAPI - 自动埋点示例 (OpenTelemetry Operator)
- **Service D**: Python/Flask - 自动埋点示例
- **Service B**: Go + Gin - 手动埋点示例
- **Service C**: Go + Gin - 手动埋点示例
- **PostgreSQL**: 数据库
- **Kafka**: 消息队列

## 核心特性

### 1. Context Propagation (上下文传播)
所有服务间的调用都会传播 Trace Context，确保整个请求链路可追踪。

### 2. 三大支柱关联
- **Trace ID** 关联所有相关的 logs 和 spans
- **Span ID** 精确定位日志产生的位置
- **Service Name** 和 **Resource Attributes** 关联 metrics

### 3. 两种埋点方式
- **自动埋点**: Service A/D 使用 OpenTelemetry Operator 或 SDK 自动埋点
- **手动埋点**: Service B/C 展示如何手动添加 spans、metrics 和结构化日志

## 📚 交互式教程

我们提供了基于 Google Codelabs 格式的**交互式动手教程**！

### 🚀 启动教程

```bash
cd codelabs
./serve.sh
```

然后访问: **http://localhost:8000**

### 🌐 在线访问

教程已部署到 GitHub Pages：[在线教程链接]

教程涵盖：
- ✅ 环境搭建（Docker、Python、Go、K6）
- ✅ Grafana 平台使用
- ✅ K6 负载测试
- ✅ Pumba 混沌工程
- ✅ Python 自动和手动埋点
- ✅ 分布式追踪、日志、指标关联

详细说明请查看 [codelabs/README.md](codelabs/README.md)

---

## 快速开始

### 前置要求
- Docker & Docker Compose
- Kubernetes (可选，用于 Operator 示例)
- kubectl (可选)
- Go 1.21+ (开发用)
- Python 3.11+ (开发用)

### 使用 Docker Compose (推荐入门)

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 访问服务
# API Gateway: http://localhost:8080
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

### 使用 Kubernetes + Operator

```bash
# 1. 部署 cert-manager (OpenTelemetry Operator 依赖)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# 2. 部署 OpenTelemetry Operator
kubectl apply -f k8s/operator/

# 3. 部署可观测性栈
kubectl apply -f k8s/observability/

# 4. 部署应用服务
kubectl apply -f k8s/services/

# 5. 访问 Grafana
kubectl port-forward svc/grafana 3000:3000 -n observability
```

## 目录结构

```
.
├── services/                    # 微服务代码
│   ├── api-gateway/            # API 网关 (Python/FastAPI)
│   ├── service-a/              # Service A (Python - Auto Instrument)
│   ├── service-b/              # Service B (Go - Manual Instrument)
│   ├── service-c/              # Service C (Go - Manual Instrument)
│   └── service-d/              # Service D (Python - Auto Instrument)
├── otel-collector/             # OpenTelemetry Collector 配置
│   └── config.yaml
├── k8s/                        # Kubernetes manifests
│   ├── operator/               # OpenTelemetry Operator 部署
│   ├── services/               # 应用服务部署
│   └── observability/          # 可观测性栈部署
├── grafana/                    # Grafana 配置
│   ├── datasources/            # 数据源配置
│   ├── dashboards/             # Dashboard JSON
│   └── provisioning/           # 自动配置
├── codelabs/                   # 📚 交互式教程 (Google Codelabs 格式)
│   ├── tutorials/              # Markdown 格式教程源文件
│   ├── generated/              # 生成的 HTML 教程
│   ├── serve.sh                # 启动教程服务器
│   ├── QUICKSTART.md           # 快速开始指南
│   ├── DEPLOYMENT.md           # GitHub Pages 部署指南
│   └── README.md               # 教程文档
├── .github/
│   └── workflows/
│       └── deploy-codelabs.yml # 自动部署 Codelabs 到 GitHub Pages
├── docker-compose.yaml         # Docker Compose 配置
└── README.md                   # 本文件
```

## 实验场景

### 场景 1: 追踪完整请求链路
```bash
curl http://localhost:8080/api/process
```
在 Grafana 中查看：
1. Tempo: 查看完整的 trace
2. Loki: 通过 trace_id 过滤相关日志
3. Prometheus: 查看各服务的 metrics

### 场景 2: 日志关联追踪
在 Grafana Explore 中：
```
{service_name="service-a"} | json | trace_id="xxx"
```

### 场景 3: Metrics 告警关联
当 Service A 延迟过高时：
1. Prometheus 触发告警
2. 通过 service_name 查找 traces
3. 通过 trace_id 查找相关 logs

## 学习要点

### 1. Context Propagation
- 查看各服务如何通过 HTTP Headers 传播 trace context
- 理解 W3C Trace Context 标准

### 2. 自动埋点 vs 手动埋点
- Service A/D: 零代码侵入的自动埋点
- Service B/C: 精细控制的手动埋点

### 3. 结构化日志
- 所有日志都包含 trace_id、span_id、service_name
- 使用 JSON 格式便于解析和查询

### 4. Semantic Conventions
- 遵循 OpenTelemetry 语义约定
- 统一的 attribute 命名

## 常见问题

### Q: 为什么需要 OpenTelemetry Collector?
A: Collector 作为中间层可以：
- 统一数据收集和导出
- 减少服务对后端系统的依赖
- 提供数据处理和采样能力

### Q: Auto-instrument 和 Manual instrument 如何选择?
A:
- Auto-instrument: 快速开始，覆盖常见框架
- Manual instrument: 业务逻辑埋点，自定义 metrics

### Q: 如何确保 logs/traces/metrics 关联?
A: 关键在于：
1. 统一的 Resource Attributes (service.name, etc.)
2. 在日志中注入 trace_id 和 span_id
3. 使用同一个 OpenTelemetry SDK/Agent

## 参考资料

- [OpenTelemetry 官方文档](https://opentelemetry.io/docs/)
- [OpenTelemetry Operator](https://github.com/open-telemetry/opentelemetry-operator)
- [Grafana Tempo](https://grafana.com/docs/tempo/)
- [Grafana Loki](https://grafana.com/docs/loki/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)

## License

MIT
