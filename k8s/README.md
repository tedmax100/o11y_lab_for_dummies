# Kubernetes 部署指南

本目录包含在 Kubernetes 上部署 O11y Lab 的所有资源文件。

## 目录结构

```
k8s/
├── namespace.yaml              # 命名空间定义
├── operator/                   # OpenTelemetry Operator 配置
│   ├── README.md              # Operator 安装指南
│   └── instrumentation.yaml   # 自动埋点配置
├── observability/             # 可观测性栈部署
│   └── otel-collector.yaml   # OpenTelemetry Collector
├── services/                  # 应用服务部署
│   ├── service-a.yaml
│   ├── service-b.yaml
│   └── ...
└── README.md                  # 本文件
```

## 快速开始

### 1. 创建命名空间

```bash
kubectl apply -f namespace.yaml
```

### 2. 安装 OpenTelemetry Operator

按照 `operator/README.md` 中的说明安装 Operator。

```bash
# 安装 cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# 等待 cert-manager 就绪
kubectl wait --for=condition=available --timeout=300s deployment/cert-manager -n cert-manager

# 安装 OpenTelemetry Operator
kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml

# 部署 Instrumentation 资源
kubectl apply -f operator/instrumentation.yaml
```

### 3. 部署可观测性栈

```bash
# 部署 OpenTelemetry Collector
kubectl apply -f observability/otel-collector.yaml

# 部署 Tempo (Traces)
# kubectl apply -f observability/tempo.yaml

# 部署 Loki (Logs)
# kubectl apply -f observability/loki.yaml

# 部署 Prometheus (Metrics)
# kubectl apply -f observability/prometheus.yaml

# 部署 Grafana
# kubectl apply -f observability/grafana.yaml
```

> 注意：完整的可观测性栈部署文件需要根据你的 K8s 环境进行调整。
> 建议使用 Helm Charts 来部署这些组件：
> - Tempo: https://github.com/grafana/helm-charts/tree/main/charts/tempo
> - Loki: https://github.com/grafana/helm-charts/tree/main/charts/loki
> - Prometheus: https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack

### 4. 部署应用服务

```bash
# 构建镜像 (需要先推送到镜像仓库)
docker build -t your-registry/service-a:latest services/service-a/
docker push your-registry/service-a:latest

# 部署服务
kubectl apply -f services/service-a.yaml
kubectl apply -f services/service-b.yaml
kubectl apply -f services/service-c.yaml
kubectl apply -f services/service-d.yaml
kubectl apply -f services/api-gateway.yaml
```

### 5. 部署数据存储

```bash
# PostgreSQL
kubectl apply -f storage/postgres.yaml

# Kafka
kubectl apply -f storage/kafka.yaml
```

## 验证部署

### 检查 Pod 状态

```bash
# 可观测性栈
kubectl get pods -n observability

# 应用服务
kubectl get pods -n o11y-lab
```

### 检查自动埋点

查看 Pod 是否已注入 OpenTelemetry instrumentation:

```bash
kubectl describe pod <pod-name> -n o11y-lab | grep -A 10 "Init Containers"
```

你应该看到一个 `opentelemetry-auto-instrumentation` 的 init container。

### 查看日志

```bash
# OpenTelemetry Collector
kubectl logs -n observability deployment/otel-collector -f

# 应用服务
kubectl logs -n o11y-lab deployment/service-a -f
```

## 访问服务

### Port Forward 到 Grafana

```bash
kubectl port-forward -n observability svc/grafana 3000:3000
```

访问 http://localhost:3000 (admin/admin)

### Port Forward 到 API Gateway

```bash
kubectl port-forward -n o11y-lab svc/api-gateway 8080:8080
```

测试请求:

```bash
curl http://localhost:8080/api/process
```

## 自动埋点 vs 手动埋点

### 使用自动埋点 (推荐用于快速开始)

在 Deployment 的 Pod template 中添加 annotation:

```yaml
metadata:
  annotations:
    instrumentation.opentelemetry.io/inject-python: "true"  # Python
    # instrumentation.opentelemetry.io/inject-go: "true"    # Go
    # instrumentation.opentelemetry.io/inject-java: "true"  # Java
```

### 使用手动埋点 (更精细的控制)

Service B 和 Service C 已经包含了手动埋点代码，不需要添加 annotation。

## 使用 Helm 部署 (推荐生产环境)

建议使用 Helm 部署可观测性栈:

```bash
# 添加 Helm repositories
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# 安装 Tempo
helm install tempo grafana/tempo -n observability

# 安装 Loki
helm install loki grafana/loki -n observability

# 安装 Prometheus Stack (包含 Grafana)
helm install prometheus prometheus-community/kube-prometheus-stack -n observability
```

## 故障排查

### Operator 问题

```bash
# 查看 Operator 日志
kubectl logs -n opentelemetry-operator-system deployment/opentelemetry-operator-controller-manager

# 查看 Instrumentation 状态
kubectl get instrumentation -n o11y-lab
kubectl describe instrumentation o11y-lab-instrumentation -n o11y-lab
```

### Collector 问题

```bash
# 查看 Collector 日志
kubectl logs -n observability deployment/otel-collector

# 查看 Collector 配置
kubectl get configmap otel-collector-config -n observability -o yaml
```

### 应用问题

```bash
# 查看 Pod events
kubectl describe pod <pod-name> -n o11y-lab

# 查看应用日志
kubectl logs -n o11y-lab <pod-name>
```

## 清理

```bash
# 删除应用服务
kubectl delete -f services/

# 删除可观测性栈
kubectl delete -f observability/

# 删除 Operator 和 Instrumentation
kubectl delete -f operator/instrumentation.yaml

# 删除命名空间
kubectl delete -f namespace.yaml
```

## 参考资料

- [OpenTelemetry Operator](https://github.com/open-telemetry/opentelemetry-operator)
- [Grafana on Kubernetes](https://grafana.com/docs/grafana/latest/setup-grafana/installation/kubernetes/)
- [Prometheus Operator](https://prometheus-operator.dev/)
