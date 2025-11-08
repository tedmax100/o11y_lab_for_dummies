# 📦 部署 Codelabs 到 GitHub Pages

本指南將協助你使用 GitHub Actions 自動部署 Codelabs 教學到 GitHub Pages。

## 🚀 快速部署（3 步完成）

### 第 1 步：啟用 GitHub Pages

1. 進入你的 GitHub 儲存庫
2. 點擊 **Settings** (設定)
3. 在左側選單找到 **Pages**
4. 在 **Source** 下選擇：
   - Source: **GitHub Actions**

   ![GitHub Pages Settings](https://docs.github.com/assets/cb-158234/images/help/pages/publishing-source-drop-down.png)

### 第 2 步：推送程式碼

```bash
# 新增所有檔案
git add .github/workflows/deploy-codelabs.yml
git add codelabs/

# 提交
git commit -m "feat: add Codelabs with GitHub Actions deployment"

# 推送到 GitHub
git push origin main
```

### 第 3 步：等待部署完成

1. 進入儲存庫的 **Actions** 標籤頁
2. 你會看到 "Deploy Codelabs to GitHub Pages" workflow 正在執行
3. 等待約 1-2 分鐘，直到顯示綠色 ✅
4. 存取你的網站：`https://<你的使用者名稱>.github.io/<儲存庫名稱>/`

**例如**：`https://yourname.github.io/o11y_lab_for_dummies/`

---

## 📋 詳細配置說明

### GitHub Actions Workflow 解析

我們建立的 `.github/workflows/deploy-codelabs.yml` 檔案做了以下事情：

#### 觸發條件
```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'codelabs/**'
  workflow_dispatch:
```

- **自動觸發**：當 `codelabs/` 目錄有變更並推送到 `main` 分支時
- **手動觸發**：可以在 Actions 頁面手動執行

#### 建置流程

1. **檢出程式碼**
   ```yaml
   - uses: actions/checkout@v4
   ```

2. **下載 claat 工具**
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

4. **上傳到 Pages**
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

## 🔧 自訂配置

### 修改分支

如果你使用的是其他分支（如 `master` 或 `develop`）：

```yaml
on:
  push:
    branches:
      - master  # 改成你的分支名
```

### 只在特定檔案變更時觸發

```yaml
on:
  push:
    paths:
      - 'codelabs/tutorials/**'        # 只監控教學檔案
      - 'codelabs/generated/index.html' # 和首頁
```

### 新增建置通知

在 workflow 末尾新增通知步驟：

```yaml
      - name: Notify on success
        if: success()
        run: echo "✅ Deployment successful!"

      - name: Notify on failure
        if: failure()
        run: echo "❌ Deployment failed!"
```

---

## 🌐 自訂網域

### 使用自訂網域

1. **購買網域**（如 `codelabs.example.com`）

2. **配置 DNS**

   在你的網域提供商處新增 CNAME 記錄：
   ```
   類型: CNAME
   名稱: codelabs (或 www)
   值: <你的使用者名稱>.github.io
   ```

3. **在 GitHub 配置**

   - 進入儲存庫 Settings → Pages
   - 在 **Custom domain** 輸入你的網域
   - 儲存

4. **新增 CNAME 檔案**

   建立 `codelabs/generated/CNAME`：
   ```bash
   echo "codelabs.example.com" > codelabs/generated/CNAME
   git add codelabs/generated/CNAME
   git commit -m "Add custom domain"
   git push
   ```

---

## 🔍 故障排除

### 問題 1：Actions 權限錯誤

**錯誤訊息**：
```
Error: Resource not accessible by integration
```

**解決方法**：
1. 進入 Settings → Actions → General
2. 找到 **Workflow permissions**
3. 選擇 **Read and write permissions**
4. 勾選 **Allow GitHub Actions to create and approve pull requests**
5. 儲存

### 問題 2：Pages 沒有啟用

**錯誤訊息**：
```
Error: Pages is not enabled for this repository
```

**解決方法**：
1. 進入 Settings → Pages
2. 確保 Source 選擇了 **GitHub Actions**
3. 不要選擇 "None"

### 問題 3：404 錯誤

**症狀**：存取網站顯示 404

**可能原因和解決**：

1. **URL 錯誤**
   - ✅ 正確：`https://使用者名稱.github.io/儲存庫名稱/`
   - ❌ 錯誤：`https://使用者名稱.github.io/`（除非儲存庫名稱是 `使用者名稱.github.io`）

2. **路徑問題**
   - 確保 workflow 中 upload 的路徑是 `./codelabs/generated`
   - 檢查 `generated/index.html` 是否存在

3. **等待時間**
   - 首次部署可能需要 5-10 分鐘
   - 查看 Actions 標籤確認部署成功

### 問題 4：樣式遺失

**症狀**：頁面顯示但沒有樣式

**解決方法**：

檢查 `generated/index.html` 中的資源路徑是否正確：

```html
<!-- 如果使用子目錄部署，可能需要修改路徑 -->
<link rel="stylesheet" href="./o11y-lab-tutorial/styles.css">
```

或在教學 Markdown 的 metadata 中新增：

```markdown
id: o11y-lab-tutorial
url: https://yourusername.github.io/o11y_lab_for_dummies
```

---

## 🔄 工作流程

### 開發流程

```bash
# 1. 本機編輯教學
vim codelabs/tutorials/observability-lab.md

# 2. 本機預覽
cd codelabs
./serve.sh

# 3. 確認無誤後提交
git add codelabs/tutorials/observability-lab.md
git commit -m "docs: update observability lab tutorial"

# 4. 推送到 GitHub（自動觸發部署）
git push origin main

# 5. 查看部署狀態
# 存取 https://github.com/使用者名稱/儲存庫名稱/actions

# 6. 部署完成後存取
# https://使用者名稱.github.io/儲存庫名稱/
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

## 📊 監控部署

### 查看建置日誌

1. 進入儲存庫的 **Actions** 標籤
2. 點擊最新的 workflow run
3. 點擊 **build** 或 **deploy** 查看詳細日誌

### 部署狀態徽章

在 README.md 中新增狀態徽章：

```markdown
[![Deploy Codelabs](https://github.com/使用者名稱/儲存庫名稱/actions/workflows/deploy-codelabs.yml/badge.svg)](https://github.com/使用者名稱/儲存庫名稱/actions/workflows/deploy-codelabs.yml)
```

示例：
![Deploy Status](https://github.com/yourusername/o11y_lab_for_dummies/actions/workflows/deploy-codelabs.yml/badge.svg)

---

## 🎯 進階配置

### 多環境部署

部署到不同環境（開發、生產）：

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
          # 根據環境建置不同版本
          ./claat export -o generated tutorials/*.md
```

### 新增建置快取

加速建置過程：

```yaml
      - name: Cache claat
        uses: actions/cache@v3
        with:
          path: codelabs/claat
          key: claat-${{ runner.os }}-v2.2.6
```

### 自動更新螢幕截圖

使用 Playwright 自動截圖（進階）：

```yaml
      - name: Setup Playwright
        run: npm install playwright

      - name: Take screenshots
        run: |
          node scripts/auto-screenshot.js
```

---

## 📱 行動裝置最佳化

確保教學在行動裝置上顯示良好：

1. **測試響應式設計**
   - 在 Chrome DevTools 中測試不同裝置
   - 使用 `responsive-check.sh` 腳本測試

2. **最佳化圖片**
   ```bash
   # 自動最佳化所有圖片
   find codelabs/tutorials/assets/images/ -name "*.png" -exec optipng -o7 {} \;
   ```

3. **檢查載入速度**
   - 使用 [PageSpeed Insights](https://pagespeed.web.dev/)
   - 目標：行動裝置分數 > 80

---

## 🔐 安全最佳實踐

1. **不要提交敏感資訊**
   ```bash
   # 新增到 .gitignore
   echo "*.env" >> .gitignore
   echo "secrets/" >> .gitignore
   ```

2. **使用 Secrets 儲存敏感配置**
   - 在 GitHub Settings → Secrets 新增
   - 在 workflow 中引用：`${{ secrets.SECRET_NAME }}`

3. **限制 workflow 權限**
   ```yaml
   permissions:
     contents: read    # 只讀程式碼
     pages: write      # 只寫 Pages
     id-token: write   # 只寫 ID token
   ```

---

## 📈 分析和監控

### 新增 Google Analytics

在 `codelabs/generated/index.html` 中新增：

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

或在教學 metadata 中配置：

```markdown
analytics account: G-XXXXXXXXXX
```

---

## ✅ 部署檢查清單

部署前確認：

- [ ] `.github/workflows/deploy-codelabs.yml` 已建立
- [ ] GitHub Pages 已啟用（Source: GitHub Actions）
- [ ] Actions 權限已設定（Read and write）
- [ ] 本機測試教學無誤（`./serve.sh`）
- [ ] 圖片路徑正確
- [ ] 提交並推送到 main 分支
- [ ] Actions 執行成功（綠色 ✅）
- [ ] 存取網站確認顯示正常
- [ ] 行動裝置顯示正常
- [ ] （選用）自訂網域已配置
- [ ] （選用）Analytics 已新增

---

## 🎓 範例儲存庫

參考完整配置範例：
- [Google Codelabs 官方範例](https://github.com/googlecodelabs/tools)
- [Firebase Codelabs](https://github.com/firebase/codelab-friendlyeats-web)

---

## 📞 需要協助？

遇到問題？
1. 查看 [GitHub Actions 文件](https://docs.github.com/en/actions)
2. 查看 [GitHub Pages 文件](https://docs.github.com/en/pages)
3. 查看儲存庫的 Actions 執行日誌
4. 提交 Issue 到專案儲存庫

---

恭喜！你的 Codelabs 教學現已自動部署到 GitHub Pages！🎉

每次更新教學並推送到 GitHub，都會自動重新建置和部署。
