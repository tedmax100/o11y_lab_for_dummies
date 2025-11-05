# Loki 查询指南 - 找到 service-a 的日志

## ✅ 问题确认

Loki 中**确实有** service-a 的日志！检查发现以下服务都有日志数据：

```
api-gateway
service-a              ← 旧版本（纯手动 instrumentation）
service-a-hybrid       ← 新版本（混合 instrumentation）✅
service-b
service-c
service-d
```

---

## 🔍 正确的查询方式

### 1️⃣ 在 Grafana Explore 中

1. 打开 **http://localhost:3000/explore**
2. 选择数据源：**Loki**
3. 使用以下查询：

#### 查询所有 service-a-hybrid 的日志：
```logql
{service_name="service-a-hybrid"}
```

#### 查询包含 trace_id 的日志：
```logql
{service_name="service-a-hybrid"} |= "trace_id"
```

#### 查询特定 trace_id：
```logql
{service_name="service-a-hybrid"} |= "4e2dd74300bc975f5a3ca603e467fc9a"
```

#### 查询 INFO 级别的日志：
```logql
{service_name="service-a-hybrid"} |= "INFO"
```

#### 查询业务处理日志：
```logql
{service_name="service-a-hybrid"} |= "process request"
```

---

## ⚠️ 常见错误

### ❌ 错误 1：使用错误的 service_name

```logql
{service_name="service-a"}  # ❌ 这是旧版本的服务
```

**正确：**
```logql
{service_name="service-a-hybrid"}  # ✅ 新的混合模式服务
```

---

### ❌ 错误 2：使用 JSON 字段作为 label

```logql
{service="service-a"}  # ❌ service 是日志内容中的字段，不是 label
```

**Loki 中的 label：**
- `service_name` ✅（由 OTEL Collector 添加）
- `service_namespace` ✅
- `deployment_environment` ✅

**日志内容中的字段：**
- `service`（在 JSON 内容中）
- `level`（在 JSON 内容中）
- `trace_id`（在 JSON 内容中）

**正确查询：**
```logql
{service_name="service-a-hybrid"} | json | service="service-a"
```

---

### ❌ 错误 3：时间范围太小

确保 Grafana 右上角的时间范围设置正确：
- 推荐：**Last 15 minutes** 或 **Last 1 hour**
- 避免：Last 5 minutes（可能没有足够的数据）

---

## 📊 高级查询示例

### 1. 按日志级别过滤

```logql
# 只看 ERROR 日志
{service_name="service-a-hybrid"} |= "ERROR"

# 只看 WARNING 和 ERROR
{service_name="service-a-hybrid"} |~ "ERROR|WARNING"
```

### 2. JSON 解析

```logql
# 解析 JSON 并过滤
{service_name="service-a-hybrid"}
| json
| level="INFO"
```

### 3. 统计查询

```logql
# 每分钟的日志数量
sum(count_over_time({service_name="service-a-hybrid"}[1m]))

# 按级别统计
sum by (level) (count_over_time({service_name="service-a-hybrid"} | json [1m]))
```

### 4. 关联 Trace ID

```logql
# 查找包含特定 trace_id 的所有日志
{service_name="service-a-hybrid"}
|= "4e2dd74300bc975f5a3ca603e467fc9a"
```

---

## 🧪 验证日志是否存在

### 使用命令行验证：

```bash
# 1. 检查所有可用的 service_name
docker exec loki wget -qO- "http://localhost:3100/loki/api/v1/label/service_name/values" | jq '.data'

# 2. 发送测试请求
curl -s http://localhost:8001/process

# 3. 查询最新日志
docker exec loki wget -qO- 'http://localhost:3100/loki/api/v1/query?query={service_name="service-a-hybrid"}&limit=5' | jq -r '.data.result[0].values[] | .[1]'
```

---

## 🔄 如果仍然看不到日志

### 1. 检查服务是否在运行

```bash
docker ps | grep service-a
```

### 2. 查看容器日志

```bash
docker logs service-a --tail 50
```

### 3. 发送测试请求

```bash
curl http://localhost:8001/process
```

### 4. 检查 OTEL Collector

```bash
docker logs otel-collector --tail 50
```

### 5. 刷新 Grafana 页面

- 按 `Cmd+Shift+R` (Mac) 或 `Ctrl+Shift+R` (Windows/Linux)
- 或者清除浏览器缓存

---

## 📝 日志格式说明

service-a-hybrid 的日志格式：

```json
{
  "time": "2025-11-05 17:20:26",
  "level": "INFO",
  "service": "service-a",
  "trace_id": "4e2dd74300bc975f5a3ca603e467fc9a",
  "span_id": "b6621f0c4b025d3a",
  "message": "Starting process request in Service A (Hybrid)"
}
```

**Labels（由 OTEL Collector 添加）：**
- `service_name="service-a-hybrid"`
- `service_namespace="o11y-lab"`
- `deployment_environment="lab"`

---

## 🎯 快速测试步骤

1. **发送请求产生日志：**
   ```bash
   curl http://localhost:8001/process
   ```

2. **在 Grafana 中查询：**
   - 打开：http://localhost:3000/explore
   - 数据源：Loki
   - 查询：
     ```logql
     {service_name="service-a-hybrid"}
     ```
   - 时间范围：Last 15 minutes
   - 点击 "Run query"

3. **应该看到：**
   - 启动日志（"Service A starting up..."）
   - 请求处理日志（"Starting process request..."）
   - 数据库查询日志
   - 外部调用日志

---

## 💡 提示

### 查看所有服务的日志：

```logql
{service_name=~".+"}
```

### 过滤多个服务：

```logql
{service_name=~"service-a-hybrid|service-b|service-d"}
```

### 排除某些日志：

```logql
{service_name="service-a-hybrid"} != "metrics"
```

---

## 📚 参考资源

- [LogQL 语法](https://grafana.com/docs/loki/latest/query/)
- [Loki Label 最佳实践](https://grafana.com/docs/loki/latest/get-started/labels/)
- [JSON 解析](https://grafana.com/docs/loki/latest/query/log_queries/#json)

---

## ✅ 总结

| 问题 | 解决方案 |
|------|----------|
| 看不到 service-a 日志 | 使用 `service_name="service-a-hybrid"` |
| service_name 不对 | 检查是否用了旧的 `service-a` |
| 时间范围太小 | 设置为 Last 15 minutes |
| Label vs 字段混淆 | `service_name` 是 label，`service` 在 JSON 中 |

**Loki 中确实有日志，只是需要用正确的 service_name 查询！** ✨
