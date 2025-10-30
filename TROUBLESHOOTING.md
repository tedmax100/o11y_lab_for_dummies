# 故障排查指南

## Docker 镜像拉取超时

### 问题表现

```
ERROR load metadata for docker.io/library/python:3.11-slim
failed to resolve source metadata: dial tcp: i/o timeout
```

### 解决方案

#### 方案 1: 配置 Docker 镜像加速器（推荐 - 中国用户）

由于你使用的是 Colima，需要在 Colima 配置中设置镜像加速器。

**1. 停止 Colima**
```bash
colima stop
```

**2. 编辑 Colima 配置**
```bash
# 编辑配置文件
nano ~/.colima/default/colima.yaml
```

**3. 添加/修改 Docker registry 镜像**

在配置文件中添加：
```yaml
docker:
  registry-mirrors:
    - https://docker.mirrors.ustc.edu.cn
    - https://hub-mirror.c.163.com
    - https://mirror.baidubce.com
```

**4. 重启 Colima**
```bash
colima start
```

**5. 验证配置**
```bash
docker info | grep -A 5 "Registry Mirrors"
```

#### 方案 2: 使用阿里云镜像加速器

1. 注册阿里云账号并获取专属加速地址: https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors

2. 配置 Colima:
```yaml
docker:
  registry-mirrors:
    - https://your-id.mirror.aliyuncs.com  # 替换为你的加速地址
```

#### 方案 3: 临时解决 - 使用代理

如果你有 HTTP 代理：

```bash
# 停止 Colima
colima stop

# 使用代理启动
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
colima start

# 构建镜像
docker-compose build
```

#### 方案 4: 手动拉取镜像（最慢但最稳定）

```bash
# 逐个拉取基础镜像
docker pull python:3.11-slim
docker pull golang:1.21-alpine
docker pull alpine:latest

# 拉取其他必需镜像
docker pull otel/opentelemetry-collector-contrib:0.91.0
docker pull grafana/tempo:2.3.1
docker pull grafana/loki:2.9.3
docker pull prom/prometheus:v2.48.0
docker pull grafana/grafana:10.2.2
docker pull postgres:16-alpine
docker pull confluentinc/cp-zookeeper:7.5.0
docker pull confluentinc/cp-kafka:7.5.0

# 然后构建服务
docker-compose build
```

#### 方案 5: 使用国内镜像源的基础镜像

我已经为你创建了一个使用国内镜像的配置文件。

### 快速修复脚本

运行以下脚本自动配置镜像加速器：

```bash
./fix-docker-mirrors.sh
```

## 其他常见问题

### 问题: 端口已被占用

```
Error: port 8080 is already allocated
```

**解决方案:**
```bash
# 查找占用端口的进程
lsof -i :8080

# 停止占用的进程或修改 docker-compose.yaml 中的端口映射
```

### 问题: 磁盘空间不足

```
Error: no space left on device
```

**解决方案:**
```bash
# 清理未使用的 Docker 资源
docker system prune -a --volumes

# 查看磁盘使用
docker system df
```

### 问题: 内存不足

```
Error: Cannot allocate memory
```

**解决方案:**
```bash
# 增加 Colima 内存限制
colima stop
colima start --memory 8

# 或修改 ~/.colima/default/colima.yaml
# memory: 8
```

### 问题: 服务无法启动

**检查步骤:**

1. 查看服务日志
```bash
docker-compose logs <service-name>
```

2. 检查服务状态
```bash
docker-compose ps
```

3. 验证网络连接
```bash
docker-compose exec service-a ping service-b
```

### 问题: Grafana 看不到数据

**解决方案:**

1. 等待 30-60 秒让数据传播

2. 发送测试请求
```bash
curl http://localhost:8080/api/process
```

3. 检查 OpenTelemetry Collector
```bash
docker-compose logs otel-collector | grep -i error
```

4. 验证数据源配置
- 访问 Grafana: http://localhost:3000
- Configuration → Data Sources
- 测试每个数据源的连接

### 问题: 服务之间无法通信

**解决方案:**

1. 检查网络
```bash
docker network ls
docker network inspect o11y_lab_for_dummies_o11y-lab
```

2. 验证 DNS 解析
```bash
docker-compose exec api-gateway ping service-a
```

3. 检查环境变量
```bash
docker-compose exec api-gateway env | grep SERVICE
```

## 性能优化

### 问题: 构建太慢

**解决方案:**

1. 使用 BuildKit
```bash
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
docker-compose build
```

2. 使用缓存
```bash
docker-compose build --parallel
```

### 问题: 启动太慢

**解决方案:**

1. 只启动必需的服务
```bash
# 先启动基础设施
docker-compose up -d postgres kafka zookeeper otel-collector tempo loki prometheus grafana

# 等待就绪后启动应用服务
docker-compose up -d api-gateway service-a service-b service-c service-d
```

2. 调整健康检查
```yaml
healthcheck:
  interval: 30s  # 增加间隔
  timeout: 10s
  retries: 3
```

## 日志和调试

### 查看实时日志

```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f service-a

# 最近 100 行
docker-compose logs --tail=100 service-a
```

### 进入容器调试

```bash
# 进入容器
docker-compose exec service-a sh

# 查看环境变量
docker-compose exec service-a env

# 测试网络连接
docker-compose exec service-a curl http://otel-collector:4317
```

### OpenTelemetry Collector 调试

```bash
# 查看 Collector 配置
docker-compose exec otel-collector cat /etc/otel-collector-config.yaml

# 查看 zpages (调试端点)
curl http://localhost:55679/debug/tracez
curl http://localhost:55679/debug/pipelinez
```

## 获取帮助

如果以上方法都无法解决你的问题：

1. 查看完整日志
```bash
docker-compose logs > debug.log
```

2. 创建 GitHub Issue，包含：
   - 错误信息
   - `docker-compose logs` 输出
   - 系统信息 (`docker version`, `docker-compose version`)
   - 环境信息（操作系统、网络环境等）

3. 查看 OpenTelemetry 官方文档
   - https://opentelemetry.io/docs/
   - https://github.com/open-telemetry/opentelemetry-collector/issues
