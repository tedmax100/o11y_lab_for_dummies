# OpenTelemetry Operator 部署指南

OpenTelemetry Operator 提供 Kubernetes 原生的自动埋点能力。

## 前置要求

### 1. 安装 cert-manager

OpenTelemetry Operator 依赖 cert-manager 来管理证书。

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

等待 cert-manager 就绪:

```bash
kubectl wait --for=condition=available --timeout=300s deployment/cert-manager -n cert-manager
kubectl wait --for=condition=available --timeout=300s deployment/cert-manager-webhook -n cert-manager
kubectl wait --for=condition=available --timeout=300s deployment/cert-manager-cainjector -n cert-manager
```

## 2. 安装 OpenTelemetry Operator

```bash
kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml
```

验证安装:

```bash
kubectl get pods -n opentelemetry-operator-system
```

## 3. 部署 Instrumentation 资源

Instrumentation CRD 定义了自动埋点的配置:

```bash
kubectl apply -f k8s/operator/instrumentation.yaml
```

## 4. 使用自动埋点

在 Pod 的 annotations 中添加自动埋点配置:

### Python 自动埋点

```yaml
annotations:
  instrumentation.opentelemetry.io/inject-python: "true"
```

### Go 自动埋点

```yaml
annotations:
  instrumentation.opentelemetry.io/inject-go: "true"
```

### Java 自动埋点

```yaml
annotations:
  instrumentation.opentelemetry.io/inject-java: "true"
```

## 验证

查看 Pod 是否已注入 init container:

```bash
kubectl describe pod <pod-name> -n o11y-lab
```

你应该看到一个 `opentelemetry-auto-instrumentation` 的 init container。

## 故障排查

### Operator 日志

```bash
kubectl logs -n opentelemetry-operator-system deployment/opentelemetry-operator-controller-manager
```

### Instrumentation 状态

```bash
kubectl get instrumentation -n o11y-lab
kubectl describe instrumentation o11y-lab-instrumentation -n o11y-lab
```
