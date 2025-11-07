# 🎉 GitHub Actions 自动部署配置完成！

## ✅ 已完成的配置

### 1. GitHub Actions Workflow
文件: `.github/workflows/deploy-codelabs.yml`

**功能**:
- ✅ 自动检测 `codelabs/` 目录的变更
- ✅ 下载并安装 claat 工具
- ✅ 从 Markdown 生成 HTML
- ✅ 自动部署到 GitHub Pages
- ✅ 支持手动触发

### 2. 快速部署脚本
文件: `codelabs/deploy-quick.sh`

**功能**:
- ✅ 一键添加、提交、推送更改
- ✅ 自动显示部署状态链接
- ✅ 显示最终访问 URL

### 3. 完整文档
- ✅ `codelabs/DEPLOYMENT.md` - 详细部署指南
- ✅ `codelabs/QUICKSTART.md` - 快速开始
- ✅ `codelabs/SCREENSHOTS_GUIDE.md` - 截图指南
- ✅ `codelabs/README.md` - 完整文档

---

## 🚀 三种部署方式

### 方式 1: 自动部署（推荐）

**适用场景**: 日常更新教程

```bash
# 1. 编辑教程
vim codelabs/tutorials/observability-lab.md

# 2. 推送到 GitHub（自动触发部署）
git add codelabs/
git commit -m "docs: update tutorial"
git push origin main

# 3. 等待 1-2 分钟，自动部署完成
```

访问: `https://你的用户名.github.io/o11y_lab_for_dummies/`

### 方式 2: 使用快速部署脚本

**适用场景**: 快速更新并部署

```bash
cd codelabs
./deploy-quick.sh

# 按提示输入提交信息，脚本会自动：
# - 添加所有更改
# - 提交
# - 推送
# - 显示部署链接
```

### 方式 3: 手动触发

**适用场景**: 不想推送代码，只想重新部署

1. 访问仓库的 Actions 页面
2. 选择 "Deploy Codelabs to GitHub Pages"
3. 点击 "Run workflow"
4. 选择分支，点击 "Run workflow"

---

## ⚙️ GitHub 设置（首次部署需要）

### 步骤 1: 启用 GitHub Pages

1. 进入仓库 → **Settings** → **Pages**
2. Source 选择: **GitHub Actions**
3. 保存

### 步骤 2: 配置 Actions 权限

1. 进入仓库 → **Settings** → **Actions** → **General**
2. 在 **Workflow permissions** 选择:
   - ✅ Read and write permissions
3. 勾选:
   - ✅ Allow GitHub Actions to create and approve pull requests
4. 保存

### 步骤 3: 首次推送

```bash
git add .
git commit -m "feat: add Codelabs with auto-deployment"
git push origin main
```

### 步骤 4: 等待部署

1. 访问: `https://github.com/你的用户名/o11y_lab_for_dummies/actions`
2. 查看 workflow 运行状态
3. 等待绿色 ✅ 出现
4. 访问: `https://你的用户名.github.io/o11y_lab_for_dummies/`

---

## 📊 监控部署状态

### 查看 Actions 运行日志

```
https://github.com/你的用户名/o11y_lab_for_dummies/actions
```

### 添加状态徽章到 README

在主 README.md 中添加：

```markdown
[![Deploy Codelabs](https://github.com/你的用户名/o11y_lab_for_dummies/actions/workflows/deploy-codelabs.yml/badge.svg)](https://github.com/你的用户名/o11y_lab_for_dummies/actions/workflows/deploy-codelabs.yml)
```

---

## 🔧 Workflow 配置说明

### 触发条件

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'codelabs/**'
  workflow_dispatch:
```

**含义**:
- 当推送到 `main` 分支
- 且 `codelabs/` 目录有变更时
- 自动触发部署
- 也可以手动触发

### 构建步骤

1. **Checkout**: 检出代码
2. **Install claat**: 下载 Codelabs 转换工具
3. **Generate HTML**: 从 Markdown 生成 HTML
4. **Upload artifact**: 上传构建产物
5. **Deploy**: 部署到 GitHub Pages

### 权限设置

```yaml
permissions:
  contents: read    # 读取代码
  pages: write      # 写入 Pages
  id-token: write   # 写入 ID token
```

---

## 🎯 工作流程示例

### 场景 1: 更新教程内容

```bash
# 1. 编辑教程
vim codelabs/tutorials/observability-lab.md

# 2. 本地预览（可选）
cd codelabs
./serve.sh
# 访问 http://localhost:8000 确认

# 3. 提交并推送
git add codelabs/tutorials/observability-lab.md
git commit -m "docs: update observability tutorial"
git push

# 4. 自动部署触发！
# 访问 Actions 页面查看进度
# 1-2 分钟后，访问在线 URL 查看更新
```

### 场景 2: 添加新教程

```bash
# 1. 创建新教程
vim codelabs/tutorials/new-tutorial.md

# 2. 生成 HTML（本地测试）
cd codelabs
./claat export -o generated tutorials/new-tutorial.md

# 3. 更新主页，添加新教程卡片
vim generated/index.html

# 4. 提交并推送
git add codelabs/
git commit -m "docs: add new tutorial"
git push

# 5. 自动部署！
```

### 场景 3: 添加截图

```bash
# 1. 按照教程截图
# 2. 保存到 tutorials/assets/images/

# 3. 快速部署
cd codelabs
./deploy-quick.sh
# 输入: "docs: add screenshots"

# 4. 自动推送并部署！
```

---

## 🐛 常见问题和解决方法

### Q1: Actions 失败 - 权限错误

**错误**: `Resource not accessible by integration`

**解决**:
1. Settings → Actions → General
2. Workflow permissions 选择 "Read and write permissions"
3. 重新运行 workflow

### Q2: Pages 404 错误

**原因**: Pages 未启用或配置错误

**解决**:
1. Settings → Pages
2. Source 确保选择 "GitHub Actions"
3. 不要选择 "None"

### Q3: 样式丢失

**原因**: 路径问题

**解决**:
检查 `generated/index.html` 中的相对路径是否正确

### Q4: 部署成功但没有更新

**原因**: 浏览器缓存

**解决**:
- 硬刷新: Ctrl+Shift+R (Windows/Linux) 或 Cmd+Shift+R (Mac)
- 或使用隐私模式访问

---

## 📈 进阶配置

### 1. 添加自定义域名

```bash
# 创建 CNAME 文件
echo "codelabs.yourdomain.com" > codelabs/generated/CNAME
git add codelabs/generated/CNAME
git commit -m "Add custom domain"
git push

# 在 Settings → Pages 配置自定义域名
```

### 2. 添加构建缓存（加速构建）

在 workflow 中添加：

```yaml
- name: Cache claat
  uses: actions/cache@v3
  with:
    path: codelabs/claat
    key: claat-${{ runner.os }}-v2.2.6
```

### 3. 多环境部署

修改 workflow 支持 staging 和 production：

```yaml
on:
  push:
    branches:
      - main        # 生产环境
      - develop     # 测试环境
```

### 4. 添加通知

部署完成后发送通知（如 Slack）：

```yaml
- name: Notify Slack
  if: success()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 🎓 学习资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [GitHub Pages 文档](https://docs.github.com/en/pages)
- [Google Codelabs 工具](https://github.com/googlecodelabs/tools)

---

## ✅ 部署检查清单

完成以下步骤确保部署成功：

- [ ] `.github/workflows/deploy-codelabs.yml` 已创建
- [ ] GitHub Pages 已启用 (Settings → Pages → Source: GitHub Actions)
- [ ] Actions 权限已配置 (Read and write)
- [ ] 本地测试教程正常 (`./serve.sh`)
- [ ] 代码已推送到 main 分支
- [ ] Workflow 运行成功（绿色 ✅）
- [ ] 访问 `https://用户名.github.io/仓库名/` 确认显示正常
- [ ] 移动端显示正常
- [ ] 所有链接可点击
- [ ] 图片正常加载

---

## 🎉 下一步

1. ✅ 按照教程操作，进行实际截图
2. ✅ 替换教程中的占位符图片
3. ✅ 推送更新，自动部署
4. ✅ 分享给团队或社区
5. ✅ 收集反馈，持续改进

恭喜！你的 Codelabs 教程平台已经配置完成，现在每次更新都会自动部署到 GitHub Pages！🚀
