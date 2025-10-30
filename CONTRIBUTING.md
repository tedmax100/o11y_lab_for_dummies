# 贡献指南

感谢你对 OpenTelemetry Observability Lab 项目感兴趣！

## 如何贡献

### 报告问题

如果你发现了 bug 或有功能建议：

1. 检查是否已有类似的 issue
2. 创建新的 issue，包含：
   - 清晰的标题
   - 详细的描述
   - 复现步骤（如果是 bug）
   - 期望的行为
   - 实际的行为
   - 环境信息（操作系统、Docker 版本等）

### 提交代码

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的改动 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范

#### Python

- 遵循 PEP 8
- 使用类型注解
- 添加 docstrings

#### Go

- 遵循 Go 官方代码规范
- 使用 `gofmt` 格式化代码
- 添加注释

#### 提交信息

使用清晰的提交信息：

```
feat: 添加新功能
fix: 修复 bug
docs: 更新文档
refactor: 重构代码
test: 添加测试
chore: 其他改动
```

## 开发环境设置

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/your-username/o11y_lab_for_dummies.git
cd o11y_lab_for_dummies

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 测试

```bash
# Python 服务
cd services/service-a
pip install -r requirements.txt
pytest

# Go 服务
cd services/service-b
go test ./...
```

## 项目结构

```
.
├── services/           # 微服务代码
├── otel-collector/    # Collector 配置
├── k8s/               # Kubernetes manifests
├── grafana/           # Grafana 配置
├── docker-compose.yaml
└── README.md
```

## 需要帮助？

如果你有任何问题，欢迎：
- 创建 issue
- 发起 discussion
- 联系维护者

感谢你的贡献！
