# 🚀 快速开始 - 5 分钟启动教程平台

## 第一步：启动教程服务器

```bash
cd codelabs
./serve.sh
```

你会看到：

```
================================================
OpenTelemetry 可观测性实验室教程服务器
================================================

启动 HTTP 服务器在端口: 8000

访问教程：
  主页: http://localhost:8000
  教程: http://localhost:8000/o11y-lab-tutorial/

按 Ctrl+C 停止服务器
================================================
```

## 第二步：打开浏览器

访问: **http://localhost:8000**

你会看到一个漂亮的教程主页，点击 "开始学习" 按钮即可开始！

## 第三步（可选）：添加截图

当前教程使用的是占位符图片。按照以下步骤添加实际截图：

### 简化版（推荐新手）

1. 按照教程操作每一步
2. 在关键界面截图
3. 将截图保存到 `tutorials/assets/images/` 目录
4. 重新生成 HTML:
   ```bash
   ./claat export -o generated tutorials/observability-lab.md
   ```
5. 刷新浏览器

### 详细指南

查看 `SCREENSHOTS_GUIDE.md` 获取详细的截图指南，包括：
- 每个截图的具体要求
- 截图工具推荐
- 优化和压缩方法
- 故障排查

## 目录导航

```
codelabs/
├── 📖 README.md              # 完整文档
├── 🚀 QUICKSTART.md          # 本文件 - 快速开始
├── 📸 SCREENSHOTS_GUIDE.md   # 截图添加指南
├── 🛠️ serve.sh               # 启动脚本
├── 🔧 claat                   # 转换工具
├── tutorials/                 # 教程源文件
│   └── observability-lab.md  # 主教程（Markdown）
└── generated/                 # 生成的网站
    ├── index.html            # 主页
    └── o11y-lab-tutorial/    # 教程 HTML
```

## 常见问题

### Q: 端口 8000 被占用？

```bash
./serve.sh 9000  # 使用其他端口
```

### Q: 如何修改教程内容？

1. 编辑 `tutorials/observability-lab.md`
2. 重新生成:
   ```bash
   ./claat export -o generated tutorials/observability-lab.md
   ```
3. 刷新浏览器

### Q: 如何添加新教程？

1. 在 `tutorials/` 创建新的 `.md` 文件
2. 使用相同的格式和元数据
3. 生成 HTML:
   ```bash
   ./claat export -o generated tutorials/新教程.md
   ```
4. 编辑 `generated/index.html` 添加新教程卡片

### Q: 可以部署到线上吗？

可以！`generated/` 目录是纯静态 HTML，可以部署到：
- GitHub Pages
- Netlify
- Vercel
- 任何静态网站托管服务

简单方法：
```bash
# 使用 GitHub Pages
git add codelabs/generated/
git commit -m "Add codelabs tutorials"
git subtree push --prefix codelabs/generated origin gh-pages
```

## 下一步

1. ✅ 启动教程服务器
2. ✅ 在浏览器中浏览教程
3. 📝 按照教程操作实验室环境
4. 📸 在操作过程中截图
5. 🔄 更新教程中的截图
6. 🌍 （可选）部署到线上供他人使用

## 需要帮助？

- 查看 `README.md` 获取完整文档
- 查看 `SCREENSHOTS_GUIDE.md` 了解如何添加截图
- 查看 [Google Codelabs 官方文档](https://github.com/googlecodelabs/tools)

祝你学习愉快！🎉
