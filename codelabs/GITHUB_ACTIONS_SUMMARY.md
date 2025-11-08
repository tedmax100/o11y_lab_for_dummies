# 🎉 GitHub Actions 自動部署配置完成！

## ✅ 已完成的配置

### 1. GitHub Actions Workflow
檔案: `.github/workflows/deploy-codelabs.yml`

**功能**:
- ✅ 自動偵測 `codelabs/` 目錄的變更
- ✅ 下載並安裝 claat 工具
- ✅ 從 Markdown 生成 HTML
- ✅ 自動部署到 GitHub Pages
- ✅ 支援手動觸發

### 2. 快速部署腳本
檔案: `codelabs/deploy-quick.sh`

**功能**:
- ✅ 一鍵新增、提交、推送變更
- ✅ 自動顯示部署狀態連結
- ✅ 顯示最終存取 URL

### 3. 完整文件
- ✅ `codelabs/DEPLOYMENT.md` - 詳細部署指南
- ✅ `codelabs/QUICKSTART.md` - 快速開始
- ✅ `codelabs/SCREENSHOTS_GUIDE.md` - 螢幕截圖指南
- ✅ `codelabs/README.md` - 完整文件

---

## 🚀 三種部署方式

### 方式 1: 自動部署（推薦）

**適用場景**: 日常更新教學

```bash
# 1. 編輯教學
vim codelabs/tutorials/observability-lab.md

# 2. 推送到 GitHub（自動觸發部署）
git add codelabs/
git commit -m "docs: update tutorial"
git push origin main

# 3. 等待 1-2 分鐘，自動部署完成
```

存取: `https://你的使用者名稱.github.io/o11y_lab_for_dummies/`

### 方式 2: 使用快速部署腳本

**適用場景**: 快速更新並部署

```bash
cd codelabs
./deploy-quick.sh

# 按提示輸入提交訊息，腳本會自動：
# - 新增所有變更
# - 提交
# - 推送
# - 顯示部署連結
```

### 方式 3: 手動觸發

**適用場景**: 不想推送程式碼，只想重新部署

1. 存取儲存庫的 Actions 頁面
2. 選擇 "Deploy Codelabs to GitHub Pages"
3. 點擊 "Run workflow"
4. 選擇分支，點擊 "Run workflow"

---

## ⚙️ GitHub 設定（首次部署需要）

### 步驟 1: 啟用 GitHub Pages

1. 進入儲存庫 → **Settings** → **Pages**
2. Source 選擇: **GitHub Actions**
3. 儲存

### 步驟 2: 配置 Actions 權限

1. 進入儲存庫 → **Settings** → **Actions** → **General**
2. 在 **Workflow permissions** 選擇:
   - ✅ Read and write permissions
3. 勾選:
   - ✅ Allow GitHub Actions to create and approve pull requests
4. 儲存

### 步驟 3: 首次推送

```bash
git add .
git commit -m "feat: add Codelabs with auto-deployment"
git push origin main
```

### 步驟 4: 等待部署

1. 存取: `https://github.com/你的使用者名稱/o11y_lab_for_dummies/actions`
2. 查看 workflow 執行狀態
3. 等待綠色 ✅ 出現
4. 存取: `https://你的使用者名稱.github.io/o11y_lab_for_dummies/`

---

## 📊 監控部署狀態

### 查看 Actions 執行日誌

```
https://github.com/你的使用者名稱/o11y_lab_for_dummies/actions
```

### 新增狀態徽章到 README

在主 README.md 中新增：

```markdown
[![Deploy Codelabs](https://github.com/你的使用者名稱/o11y_lab_for_dummies/actions/workflows/deploy-codelabs.yml/badge.svg)](https://github.com/你的使用者名稱/o11y_lab_for_dummies/actions/workflows/deploy-codelabs.yml)
```

---

## 🔧 Workflow 配置說明

### 觸發條件

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'codelabs/**'
  workflow_dispatch:
```

**含義**:
- 當推送到 `main` 分支
- 且 `codelabs/` 目錄有變更時
- 自動觸發部署
- 也可以手動觸發

### 建置步驟

1. **Checkout**: 檢出程式碼
2. **Install claat**: 下載 Codelabs 轉換工具
3. **Generate HTML**: 從 Markdown 生成 HTML
4. **Upload artifact**: 上傳建置產物
5. **Deploy**: 部署到 GitHub Pages

### 權限設定

```yaml
permissions:
  contents: read    # 讀取程式碼
  pages: write      # 寫入 Pages
  id-token: write   # 寫入 ID token
```

---

## 🎯 工作流程範例

### 場景 1: 更新教學內容

```bash
# 1. 編輯教學
vim codelabs/tutorials/observability-lab.md

# 2. 本機預覽（選用）
cd codelabs
./serve.sh
# 存取 http://localhost:8000 確認

# 3. 提交並推送
git add codelabs/tutorials/observability-lab.md
git commit -m "docs: update observability tutorial"
git push

# 4. 自動部署觸發！
# 存取 Actions 頁面查看進度
# 1-2 分鐘後，存取線上 URL 查看更新
```

### 場景 2: 新增新教學

```bash
# 1. 建立新教學
vim codelabs/tutorials/new-tutorial.md

# 2. 生成 HTML（本機測試）
cd codelabs
./claat export -o generated tutorials/new-tutorial.md

# 3. 更新首頁，新增新教學卡片
vim generated/index.html

# 4. 提交並推送
git add codelabs/
git commit -m "docs: add new tutorial"
git push

# 5. 自動部署！
```

### 場景 3: 新增螢幕截圖

```bash
# 1. 按照教學截圖
# 2. 儲存到 tutorials/assets/images/

# 3. 快速部署
cd codelabs
./deploy-quick.sh
# 輸入: "docs: add screenshots"

# 4. 自動推送並部署！
```

---

## 🐛 常見問題和解決方法

### Q1: Actions 失敗 - 權限錯誤

**錯誤**: `Resource not accessible by integration`

**解決**:
1. Settings → Actions → General
2. Workflow permissions 選擇 "Read and write permissions"
3. 重新執行 workflow

### Q2: Pages 404 錯誤

**原因**: Pages 未啟用或配置錯誤

**解決**:
1. Settings → Pages
2. Source 確保選擇 "GitHub Actions"
3. 不要選擇 "None"

### Q3: 樣式遺失

**原因**: 路徑問題

**解決**:
檢查 `generated/index.html` 中的相對路徑是否正確

### Q4: 部署成功但沒有更新

**原因**: 瀏覽器快取

**解決**:
- 硬重新整理: Ctrl+Shift+R (Windows/Linux) 或 Cmd+Shift+R (Mac)
- 或使用隱私模式存取

---

## 📈 進階配置

### 1. 新增自訂網域

```bash
# 建立 CNAME 檔案
echo "codelabs.yourdomain.com" > codelabs/generated/CNAME
git add codelabs/generated/CNAME
git commit -m "Add custom domain"
git push

# 在 Settings → Pages 配置自訂網域
```

### 2. 新增建置快取（加速建置）

在 workflow 中新增：

```yaml
- name: Cache claat
  uses: actions/cache@v3
  with:
    path: codelabs/claat
    key: claat-${{ runner.os }}-v2.2.6
```

### 3. 多環境部署

修改 workflow 支援 staging 和 production：

```yaml
on:
  push:
    branches:
      - main        # 生產環境
      - develop     # 測試環境
```

### 4. 新增通知

部署完成後發送通知（如 Slack）：

```yaml
- name: Notify Slack
  if: success()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 🎓 學習資源

- [GitHub Actions 文件](https://docs.github.com/en/actions)
- [GitHub Pages 文件](https://docs.github.com/en/pages)
- [Google Codelabs 工具](https://github.com/googlecodelabs/tools)

---

## ✅ 部署檢查清單

完成以下步驟確保部署成功：

- [ ] `.github/workflows/deploy-codelabs.yml` 已建立
- [ ] GitHub Pages 已啟用 (Settings → Pages → Source: GitHub Actions)
- [ ] Actions 權限已配置 (Read and write)
- [ ] 本機測試教學正常 (`./serve.sh`)
- [ ] 程式碼已推送到 main 分支
- [ ] Workflow 執行成功（綠色 ✅）
- [ ] 存取 `https://使用者名稱.github.io/儲存庫名稱/` 確認顯示正常
- [ ] 行動裝置顯示正常
- [ ] 所有連結可點擊
- [ ] 圖片正常載入

---

## 🎉 下一步

1. ✅ 按照教學操作，進行實際截圖
2. ✅ 替換教學中的佔位符圖片
3. ✅ 推送更新，自動部署
4. ✅ 分享給團隊或社群
5. ✅ 收集回饋，持續改進

恭喜！你的 Codelabs 教學平台已經配置完成，現在每次更新都會自動部署到 GitHub Pages！🚀
