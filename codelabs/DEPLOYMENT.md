# 📦 部署 Codelabs 到 GitHub Pages

本指南将帮助你使用 GitHub Actions 自动部署 Codelabs 教程到 GitHub Pages。

## 🚀 快速部署（3 步完成）

### 第 1 步：启用 GitHub Pages

1. 进入你的 GitHub 仓库
2. 点击 **Settings** (设置)
3. 在左侧菜单找到 **Pages**
4. 在 **Source** 下选择：
   - Source: **GitHub Actions**

   ![GitHub Pages Settings](https://docs.github.com/assets/cb-158234/images/help/pages/publishing-source-drop-down.png)

### 第 2 步：推送代码

```bash
# 添加所有文件
git add .github/workflows/deploy-codelabs.yml
git add codelabs/

# 提交
git commit -m "feat: add Codelabs with GitHub Actions deployment"

# 推送到 GitHub
git push origin main
```

### 第 3 步：等待部署完成

1. 进入仓库的 **Actions** 标签页
2. 你会看到 "Deploy Codelabs to GitHub Pages" workflow 正在运行
3. 等待约 1-2 分钟，直到显示绿色 ✅
4. 访问你的网站：`https://<你的用户名>.github.io/<仓库名>/`

**例如**：`https://yourname.github.io/o11y_lab_for_dummies/`

---

## 📋 详细配置说明

### GitHub Actions Workflow 解析

我们创建的 `.github/workflows/deploy-codelabs.yml` 文件做了以下事情：

#### 触发条件
```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'codelabs/**'
  workflow_dispatch:
```

- **自动触发**：当 `codelabs/` 目录有变更并推送到 `main` 分支时
- **手动触发**：可以在 Actions 页面手动运行

#### 构建流程

1. **检出代码**
   ```yaml
   - uses: actions/checkout@v4
   ```

2. **下载 claat 工具**
   ```yaml
   - name: Download and install claat
     run: |
       curl -LO https://github.com/googlecodelabs/tools/releases/download/v2.2.6/claat-linux-amd64
       chmod +x claat-linux-amd64
   ```

3. **生成 HTML**
   ```yaml
   - name: Generate HTML from Markdown
     run: |
       ./claat export -o generated tutorials/*.md
   ```

4. **上传到 Pages**
   ```yaml
   - uses: actions/upload-pages-artifact@v3
     with:
       path: './codelabs/generated'
   ```

5. **部署**
   ```yaml
   - uses: actions/deploy-pages@v4
   ```

---

## 🔧 自定义配置

### 修改分支

如果你使用的是其他分支（如 `master` 或 `develop`）：

```yaml
on:
  push:
    branches:
      - master  # 改成你的分支名
```

### 只在特定文件变更时触发

```yaml
on:
  push:
    paths:
      - 'codelabs/tutorials/**'        # 只监控教程文件
      - 'codelabs/generated/index.html' # 和主页
```

### 添加构建通知

在 workflow 末尾添加通知步骤：

```yaml
      - name: Notify on success
        if: success()
        run: echo "✅ Deployment successful!"

      - name: Notify on failure
        if: failure()
        run: echo "❌ Deployment failed!"
```

---

## 🌐 自定义域名

### 使用自定义域名

1. **购买域名**（如 `codelabs.example.com`）

2. **配置 DNS**

   在你的域名提供商处添加 CNAME 记录：
   ```
   类型: CNAME
   名称: codelabs (或 www)
   值: <你的用户名>.github.io
   ```

3. **在 GitHub 配置**

   - 进入仓库 Settings → Pages
   - 在 **Custom domain** 输入你的域名
   - 保存

4. **添加 CNAME 文件**

   创建 `codelabs/generated/CNAME`：
   ```bash
   echo "codelabs.example.com" > codelabs/generated/CNAME
   git add codelabs/generated/CNAME
   git commit -m "Add custom domain"
   git push
   ```

---

## 🔍 故障排查

### 问题 1：Actions 权限错误

**错误信息**：
```
Error: Resource not accessible by integration
```

**解决方法**：
1. 进入 Settings → Actions → General
2. 找到 **Workflow permissions**
3. 选择 **Read and write permissions**
4. 勾选 **Allow GitHub Actions to create and approve pull requests**
5. 保存

### 问题 2：Pages 没有启用

**错误信息**：
```
Error: Pages is not enabled for this repository
```

**解决方法**：
1. 进入 Settings → Pages
2. 确保 Source 选择了 **GitHub Actions**
3. 不要选择 "None"

### 问题 3：404 错误

**症状**：访问网站显示 404

**可能原因和解决**：

1. **URL 错误**
   - ✅ 正确：`https://用户名.github.io/仓库名/`
   - ❌ 错误：`https://用户名.github.io/`（除非仓库名是 `用户名.github.io`）

2. **路径问题**
   - 确保 workflow 中 upload 的路径是 `./codelabs/generated`
   - 检查 `generated/index.html` 是否存在

3. **等待时间**
   - 首次部署可能需要 5-10 分钟
   - 查看 Actions 标签确认部署成功

### 问题 4：样式丢失

**症状**：页面显示但没有样式

**解决方法**：

检查 `generated/index.html` 中的资源路径是否正确：

```html
<!-- 如果使用子目录部署，可能需要修改路径 -->
<link rel="stylesheet" href="./o11y-lab-tutorial/styles.css">
```

或在教程 Markdown 的 metadata 中添加：

```markdown
id: o11y-lab-tutorial
url: https://yourusername.github.io/o11y_lab_for_dummies
```

---

## 🔄 工作流程

### 开发流程

```bash
# 1. 本地编辑教程
vim codelabs/tutorials/observability-lab.md

# 2. 本地预览
cd codelabs
./serve.sh

# 3. 确认无误后提交
git add codelabs/tutorials/observability-lab.md
git commit -m "docs: update observability lab tutorial"

# 4. 推送到 GitHub（自动触发部署）
git push origin main

# 5. 查看部署状态
# 访问 https://github.com/用户名/仓库名/actions

# 6. 部署完成后访问
# https://用户名.github.io/仓库名/
```

### 快速更新流程

```bash
# 一行命令完成所有操作
git add codelabs/ && \
git commit -m "docs: update codelabs" && \
git push && \
echo "✅ Pushed! Check https://github.com/$(git config user.name)/$(basename $(git rev-parse --show-toplevel))/actions"
```

---

## 📊 监控部署

### 查看构建日志

1. 进入仓库的 **Actions** 标签
2. 点击最新的 workflow run
3. 点击 **build** 或 **deploy** 查看详细日志

### 部署状态徽章

在 README.md 中添加状态徽章：

```markdown
[![Deploy Codelabs](https://github.com/用户名/仓库名/actions/workflows/deploy-codelabs.yml/badge.svg)](https://github.com/用户名/仓库名/actions/workflows/deploy-codelabs.yml)
```

示例：
![Deploy Status](https://github.com/yourusername/o11y_lab_for_dummies/actions/workflows/deploy-codelabs.yml/badge.svg)

---

## 🎯 高级配置

### 多环境部署

部署到不同环境（开发、生产）：

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [development, production]
    steps:
      - name: Build for ${{ matrix.environment }}
        run: |
          # 根据环境构建不同版本
          ./claat export -o generated tutorials/*.md
```

### 添加构建缓存

加速构建过程：

```yaml
      - name: Cache claat
        uses: actions/cache@v3
        with:
          path: codelabs/claat
          key: claat-${{ runner.os }}-v2.2.6
```

### 自动更新截图

使用 Playwright 自动截图（高级）：

```yaml
      - name: Setup Playwright
        run: npm install playwright

      - name: Take screenshots
        run: |
          node scripts/auto-screenshot.js
```

---

## 📱 移动端优化

确保教程在移动设备上显示良好：

1. **测试响应式**
   - 在 Chrome DevTools 中测试不同设备
   - 使用 `responsive-check.sh` 脚本测试

2. **优化图片**
   ```bash
   # 自动优化所有图片
   find codelabs/tutorials/assets/images/ -name "*.png" -exec optipng -o7 {} \;
   ```

3. **检查加载速度**
   - 使用 [PageSpeed Insights](https://pagespeed.web.dev/)
   - 目标：移动端分数 > 80

---

## 🔐 安全最佳实践

1. **不要提交敏感信息**
   ```bash
   # 添加到 .gitignore
   echo "*.env" >> .gitignore
   echo "secrets/" >> .gitignore
   ```

2. **使用 Secrets 存储敏感配置**
   - 在 GitHub Settings → Secrets 添加
   - 在 workflow 中引用：`${{ secrets.SECRET_NAME }}`

3. **限制 workflow 权限**
   ```yaml
   permissions:
     contents: read    # 只读代码
     pages: write      # 只写 Pages
     id-token: write   # 只写 ID token
   ```

---

## 📈 分析和监控

### 添加 Google Analytics

在 `codelabs/generated/index.html` 中添加：

```html
<head>
  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-XXXXXXXXXX');
  </script>
</head>
```

或在教程 metadata 中配置：

```markdown
analytics account: G-XXXXXXXXXX
```

---

## ✅ 部署检查清单

部署前确认：

- [ ] `.github/workflows/deploy-codelabs.yml` 已创建
- [ ] GitHub Pages 已启用（Source: GitHub Actions）
- [ ] Actions 权限已设置（Read and write）
- [ ] 本地测试教程无误（`./serve.sh`）
- [ ] 图片路径正确
- [ ] 提交并推送到 main 分支
- [ ] Actions 运行成功（绿色 ✅）
- [ ] 访问网站确认显示正常
- [ ] 移动端显示正常
- [ ] （可选）自定义域名已配置
- [ ] （可选）Analytics 已添加

---

## 🎓 示例仓库

参考完整配置示例：
- [Google Codelabs 官方示例](https://github.com/googlecodelabs/tools)
- [Firebase Codelabs](https://github.com/firebase/codelab-friendlyeats-web)

---

## 📞 需要帮助？

遇到问题？
1. 查看 [GitHub Actions 文档](https://docs.github.com/en/actions)
2. 查看 [GitHub Pages 文档](https://docs.github.com/en/pages)
3. 查看仓库的 Actions 运行日志
4. 提交 Issue 到项目仓库

---

恭喜！你的 Codelabs 教程现已自动部署到 GitHub Pages！🎉

每次更新教程并推送到 GitHub，都会自动重新构建和部署。
