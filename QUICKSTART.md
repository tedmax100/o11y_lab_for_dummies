# 快速开始指南

本指南帮助你在 **5 分钟内** 启动并运行 OpenTelemetry Observability Lab。

## 前置要求

- ✅ Docker 和 Docker Compose
- ✅ curl (用于测试)
- ✅ 至少 4GB 可用内存

## 步骤 1: 启动服务 (2分钟)

```bash
# 克隆仓库 (如果还没有)
cd o11y_lab_for_dummies

# 启动所有服务
docker-compose up -d

# 等待服务启动
sleep 30

# 检查服务状态
docker-compose ps
```

你应该看到所有服务都是 `Up` 状态。

## 步骤 2: 发送测试请求 (1分钟)

```bash
# 发送单个请求
curl http://localhost:8080/api/process

# 应该返回类似这样的 JSON:
# {
#   "status": "success",
#   "message": "Request processed through gateway",
#   "data": { ... }
# }

# 发送多个请求以生成更多数据
for i in {1..10}; do
  curl http://localhost:8080/api/process
  echo ""
  sleep 1
done
```

## 步骤 3: 访问 Grafana (2分钟)

1. 打开浏览器访问: **http://localhost:3000**

2. 登录 (默认凭据):
   - 用户名: `admin`
   - 密码: `admin`

3. 进入 **Explore** 页面 (左侧菜单的指南针图标)

## 验证 Traces

1. 在 Explore 页面，选择 **Tempo** 数据源

2. 点击 **Search** 按钮

3. 你会看到最近的 traces 列表

4. 点击任意一个 trace 查看详情，你会看到:
   ```
   API Gateway
   └─ Service A
      ├─ PostgreSQL Query
      ├─ Service D
      ├─ Service B
      │  └─ Kafka Publish
      └─ Third Party API

   Service C (来自 Kafka)
   └─ Process Message
   ```

## 验证 Logs

1. 在 Explore 页面，选择 **Loki** 数据源

2. 输入查询:
   ```
   {service_name="service-a"} | json
   ```

3. 你会看到结构化的日志输出

4. 找到一条日志，点击日志中的 **TraceID** 链接

5. 自动跳转到 Tempo 查看完整的 trace - **这就是关联！**

## 验证 Metrics

1. 在 Explore 页面，选择 **Prometheus** 数据源

2. 输入查询:
   ```
   rate(otel_http_server_duration_count[5m])
   ```

3. 你会看到各服务的请求速率

4. 查看图表上的小圆点 (**Exemplars**)

5. 点击一个 exemplar，跳转到对应的 trace - **又一个关联！**

## 🎉 成功！

你已经成功运行了完整的 OpenTelemetry 可观测性栈！

### 你看到了什么？

- ✅ **Traces**: 完整的分布式追踪
- ✅ **Logs**: 结构化日志，包含 trace_id
- ✅ **Metrics**: 时序指标，带 exemplars
- ✅ **关联**: 三者通过 trace_id 完美关联

## 下一步

### 学习更多

- 📖 阅读 [USAGE.md](USAGE.md) 了解详细用法
- 🏗️ 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 理解系统架构
- 💻 查看各服务的源代码，了解实现细节

### 实验场景

1. **场景 1**: 模拟错误
   ```bash
   # 停止 Service D
   docker-compose stop service-d

   # 发送请求
   curl http://localhost:8080/api/process

   # 在 Tempo 中查看错误 trace (红色标记)
   ```

2. **场景 2**: 查看数据库操作
   ```bash
   # 在 Tempo 中找到一个 trace
   # 展开 Service A 的 spans
   # 你会看到 PostgreSQL 查询的详细信息
   ```

3. **场景 3**: 追踪 Kafka 消息
   ```bash
   # 发送请求
   curl http://localhost:8080/api/process

   # 在 trace 中观察:
   # Service A → Service B → Kafka → Service C
   # 整个链路在同一个 trace 中！
   ```

## 常用命令

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f service-a

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 清理所有数据
docker-compose down -v
```

## 故障排查

### 服务无法启动

```bash
# 检查端口占用
lsof -i :8080  # API Gateway
lsof -i :3000  # Grafana
lsof -i :9090  # Prometheus

# 查看详细日志
docker-compose logs <service-name>
```

### Grafana 看不到数据

1. 等待 30 秒让数据传播
2. 发送更多测试请求
3. 检查数据源配置 (Configuration → Data Sources)

### Collector 错误

```bash
# 查看 Collector 日志
docker-compose logs otel-collector

# 检查 Collector 配置
cat otel-collector/config.yaml
```

## 获取帮助

- 📝 创建 GitHub Issue
- 💬 查看 [常见问题](USAGE.md#常见问题)
- 📚 阅读 [OpenTelemetry 文档](https://opentelemetry.io/docs/)

---

**Have Fun with Observability! 🚀**
