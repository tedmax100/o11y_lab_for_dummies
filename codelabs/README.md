# OpenTelemetry 可观测性实验室 - Codelabs 教程

这是一个基于 Google Codelabs 格式的交互式教程平台，帮助你学习 OpenTelemetry 和可观测性技术。

## 快速开始

### 1. 启动教程服务器

```bash
cd codelabs
./serve.sh
```

默认在端口 8000 启动，或者指定端口：

```bash
./serve.sh 9000
```

### 2. 访问教程

在浏览器中打开：
- **主页**: http://localhost:8000
- **完整教程**: http://localhost:8000/o11y-lab-tutorial/

## 添加截图

教程中有一些占位符图片需要替换为实际截图：

### 需要的截图列表

1. **grafana-home.png** - Grafana 主页界面
2. **grafana-datasources.png** - 数据源配置页面
3. **grafana-dashboards.png** - Dashboard 列表
4. **k6-traffic.png** - K6 生成流量后的 Grafana 图表
5. **pumba-delay.png** - 注入延迟后的性能影响图表
6. **auto-trace.png** - 自动埋点生成的 Trace 示例
7. **manual-trace.png** - 手动埋点的 Trace 示例
8. **correlated-dashboard.png** - Logs/Traces/Metrics 关联的 Dashboard

### 如何添加截图

1. 按照教程操作，在相应步骤截图
2. 将截图保存到对应位置：

```bash
# 截图保存位置
codelabs/tutorials/assets/images/

# 或者在生成后的教程中替换
codelabs/generated/o11y-lab-tutorial/img/
```

3. 重新生成教程（如果修改了 Markdown）：

```bash
cd codelabs
./claat export -o generated tutorials/observability-lab.md
```

## 目录结构

```
codelabs/
├── tutorials/              # Markdown 格式的教程源文件
│   ├── observability-lab.md
│   └── assets/
│       └── images/        # 教程中使用的图片
├── generated/             # 生成的 HTML 教程
│   ├── index.html         # 教程主页
│   └── o11y-lab-tutorial/ # 生成的教程内容
├── claat                  # Codelabs 转换工具
├── serve.sh              # 启动 Web 服务器脚本
└── README.md             # 本文件
```

## 创建新教程

### 1. 创建 Markdown 文件

在 `tutorials/` 目录下创建新的 `.md` 文件，格式如下：

```markdown
author: 作者名
summary: 教程简介
id: unique-tutorial-id
categories: category1,category2
environments: Web
status: Published
feedback link: https://github.com/your-repo
analytics account: Google Analytics ID

# 教程标题

## 第一步
Duration: 5

这是第一步的内容...

## 第二步
Duration: 10

这是第二步的内容...
```

### 2. 生成 HTML

```bash
./claat export -o generated tutorials/your-tutorial.md
```

### 3. 更新主页

编辑 `generated/index.html`，添加新教程的卡片。

## Markdown 语法特性

### Duration (时长)

在每个步骤下方指定预计完成时间（分钟）：

```markdown
## 步骤标题
Duration: 10
```

### 提示框

```markdown
Positive
: 这是一个成功/正面的提示

Negative
: 这是一个警告/负面的提示
```

### 代码块

```markdown
\`\`\`bash
# 命令示例
docker compose up -d
\`\`\`

\`\`\`python
# Python 代码
print("Hello World")
\`\`\`
```

### 图片

```markdown
![图片描述](assets/images/image-name.png)
```

### 链接

```markdown
[链接文本](https://example.com)
```

## 自定义样式

如需自定义教程外观，可以修改：

1. **主页样式**: `generated/index.html` 中的 `<style>` 部分
2. **教程样式**: claat 生成的默认样式在生成的 HTML 中

## 部署到生产环境

### 使用 GitHub Pages

1. 将 `generated/` 目录内容推送到 `gh-pages` 分支
2. 在仓库设置中启用 GitHub Pages

### 使用 Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/codelabs/generated;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

### 使用 Docker

创建 `Dockerfile`:

```dockerfile
FROM nginx:alpine
COPY generated/ /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

构建并运行：

```bash
docker build -t o11y-codelabs .
docker run -d -p 8080:80 o11y-codelabs
```

## 工具说明

### claat (Codelabs As A Thing)

这是 Google 开发的工具，用于将 Markdown 转换为 Codelabs HTML 格式。

- **官方仓库**: https://github.com/googlecodelabs/tools
- **文档**: https://github.com/googlecodelabs/tools/blob/main/claat/README.md

### 常用命令

```bash
# 导出为 HTML
./claat export tutorials/your-tutorial.md

# 预览（启动开发服务器）
./claat serve

# 更新已存在的教程
./claat update o11y-lab-tutorial

# 查看版本
./claat version
```

## 故障排查

### 图片无法显示

检查图片路径是否正确：
- Markdown 中: `assets/images/image.png`
- 生成后: `img/image.png`

### 样式异常

清除浏览器缓存或使用隐私模式重新访问。

### 端口被占用

修改启动脚本中的端口：

```bash
./serve.sh 9000
```

## 贡献

欢迎提交新教程或改进现有教程！

1. Fork 本项目
2. 创建新的 Markdown 教程
3. 生成 HTML 并测试
4. 提交 Pull Request

## 许可证

MIT License

## 参考资源

- [Google Codelabs 官方文档](https://github.com/googlecodelabs/tools)
- [Markdown 语法指南](https://www.markdownguide.org/)
- [OpenTelemetry 官方文档](https://opentelemetry.io/docs/)
