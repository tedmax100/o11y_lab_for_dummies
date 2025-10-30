# 快速测试指南

## ✅ 系统已启动！

所有服务都在运行中：

### 📍 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| **API Gateway** | http://localhost:8080 | 入口服务 |
| **Grafana** | http://localhost:3000 | 可视化平台 (admin/admin) |
| **Prometheus** | http://localhost:9090 | Metrics 查询 |
| **Tempo** | http://localhost:3200 | Traces 查询 |
| **Loki** | http://localhost:3100 | Logs 查询 |
| **Service A** | http://localhost:8001 | 核心服务 |
| **Service B** | http://localhost:8002 | Kafka 生产者 |
| **Service C** | http://localhost:8003 | Kafka 消费者 |
| **Service D** | http://localhost:8004 | 计算服务 |

## 🧪 快速测试步骤

### 1. 测试健康检查

```bash
# 测试所有服务的健康状态
curl http://localhost:8080/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

### 2. 发送测试请求

```bash
# 发送单个请求
curl http://localhost:8080/api/process

# 发送多个请求生成更多数据
for i in {1..5}; do
  echo "Request $i:"
  curl http://localhost:8080/api/process
  echo ""
  sleep 1
done
```

### 3. 访问 Grafana 查看数据

1. 打开浏览器访问 http://localhost:3000
2. 使用默认凭据登录:
   - 用户名: `admin`
   - 密码: `admin`

### 4. 在 Grafana 中查看 Traces

1. 点击左侧菜单的 **Explore** (指南针图标)
2. 选择数据源: **Tempo**
3. 点击 **Search** 或 **Run query**
4. 你会看到最近的 traces 列表
5. 点击任意一个 trace 查看详细的调用链路

**你应该看到的调用链:**
```
API Gateway (8080)
└─ Service A (8001)
   ├─ PostgreSQL (查询和插入)
   ├─ Service D (8004) - 计算服务
   ├─ Service B (8002) - Kafka 生产者
   │  └─ Kafka (发布消息)
   └─ Third Party API (GitHub Zen API)

Service C (8003) - 单独的 trace
└─ Kafka (消费消息)
   └─ 业务处理逻辑
```

### 5. 查看 Metrics

1. 在 Grafana Explore 中选择 **Prometheus** 数据源
2. 尝试以下查询:

```promql
# 请求速率
rate(otel_http_server_duration_count[5m])

# 按服务分组的请求速率
sum by(service_name) (rate(otel_http_server_duration_count[5m]))

# P95 延迟
histogram_quantile(0.95, rate(otel_http_server_duration_bucket[5m]))
```

### 6. 查看日志

1. 在 Grafana Explore 中选择 **Loki** 数据源
2. 使用以下查询:

```logql
# 查看所有日志
{service_name=~".+"}

# 查看 Service A 的日志
{service_name="service-a"}

# 过滤错误日志
{service_name="service-a"} | json | level="ERROR"

# 查看包含 "database" 的日志
{service_name="service-a"} | json | message =~ "(?i)database"
```

3. **关键特性**: 点击日志中的 **TraceID** 可以直接跳转到相关的 trace！

### 7. 查看服务状态

```bash
# 查看所有容器状态
docker-compose ps

# 查看特定服务的日志
docker-compose logs service-a
docker-compose logs -f api-gateway  # 实时查看

# 查看 OpenTelemetry Collector 日志
docker-compose logs otel-collector
```

## 🔍 验证三大支柱关联

### 验证 Logs → Traces

1. 在 Loki 中查询日志: `{service_name="service-a"}`
2. 找到一条日志记录
3. 点击日志中的 **TraceID** 字段（如果配置正确会有链接）
4. 自动跳转到 Tempo 查看完整的 trace

### 验证 Metrics → Traces (Exemplars)

1. 在 Prometheus 中查询 metrics
2. 查看图表上的小圆点 (**Exemplars**)
3. 点击 exemplar 可以跳转到对应的 trace

### 验证 Traces → Logs

1. 在 Tempo 中查看一个 trace
2. 在 span 详情中可以看到关联的日志
3. 或者手动复制 trace_id 到 Loki 中查询

## 📊 查看数据库数据

```bash
# 连接到 PostgreSQL
docker-compose exec postgres psql -U postgres -d o11ylab

# 查询请求日志
SELECT * FROM request_logs ORDER BY timestamp DESC LIMIT 10;

# 按状态统计
SELECT status, COUNT(*) FROM request_logs GROUP BY status;

# 退出
\q
```

## 🛠️ 故障排查

### 如果服务无法访问

```bash
# 检查服务状态
docker-compose ps

# 检查服务日志
docker-compose logs <service-name>

# 重启特定服务
docker-compose restart <service-name>

# 重启所有服务
docker-compose restart
```

### 如果看不到数据

1. **等待30秒** - 数据需要时间传播
2. **发送更多请求** - 确保有足够的数据
3. **检查时间范围** - 在 Grafana 中选择正确的时间范围
4. **检查 OTel Collector**:
   ```bash
   docker-compose logs otel-collector | grep -i error
   ```

### 查看 OTel Collector 状态

```bash
# 健康检查
curl http://localhost:13133/health

# 查看 metrics
curl http://localhost:8888/metrics

# zpages - pipeline 状态
open http://localhost:55679/debug/pipelinez
```

## 🎯 下一步

### 学习实验

1. **修改代码** - 尝试在服务中添加自定义 span 和 metrics
2. **模拟故障** - 停止某个服务，观察错误如何传播
3. **性能测试** - 使用 `ab` 或 `hey` 进行压力测试
4. **采样配置** - 修改 OTel Collector 的采样率

### 高级功能

1. **添加告警规则** - 在 Prometheus 中配置告警
2. **创建 Dashboard** - 在 Grafana 中创建自定义仪表板
3. **Tail-based Sampling** - 配置智能采样
4. **Service Graph** - 查看服务依赖关系图

## 📝 常用命令

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 重新构建并启动
docker-compose up -d --build

# 查看资源使用
docker stats

# 清理未使用的资源
docker system prune -a
```

## 🌟 成功指标

如果看到以下内容，说明系统运行正常：

- ✅ 所有 13 个容器都是 `Up` 状态
- ✅ API Gateway 返回成功响应
- ✅ Grafana 可以访问并看到数据源
- ✅ Tempo 中可以看到完整的 traces
- ✅ Prometheus 中有 metrics 数据
- ✅ 日志中包含 trace_id 和 span_id
- ✅ PostgreSQL 中有请求记录
- ✅ Kafka 消息被正常消费

---

**Happy Observability! 🚀**

如有问题，请查看 `TROUBLESHOOTING.md` 或 `USAGE.md`
