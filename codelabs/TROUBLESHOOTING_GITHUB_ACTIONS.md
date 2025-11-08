# 🔧 GitHub Actions 部署故障排除

## 錯誤：Get Pages site failed

### 錯誤訊息
```
Error: Get Pages site failed. Please verify that the repository has Pages enabled
and configured to build using GitHub Actions, or consider exploring the `enablement`
parameter for this action.
Error: HttpError: Not Found
```

### 原因
這個錯誤表示 GitHub Pages 還沒有被啟用或配置。

---

## ✅ 解決方案（按順序嘗試）

### 方案 1: 啟用 GitHub Pages（必須）

**步驟**：

1. 進入你的 GitHub 儲存庫
2. 點擊 **Settings**（設定）
3. 在左側選單找到 **Pages**
4. 在 **Build and deployment** 下：
   - **Source**: 選擇 **GitHub Actions** ⚠️ 重要！
   - 不要選擇 "Deploy from a branch"
   - 不要選擇 "None"

5. 儲存變更

**截圖位置參考**：
```
Settings (頂部標籤)
  └─ Pages (左側選單)
      └─ Source: [選擇] GitHub Actions
```

### 方案 2: 確認儲存庫是 Public 或有 Pro 帳戶

GitHub Pages 要求：
- **Public 儲存庫**: 免費使用 Pages
- **Private 儲存庫**: 需要 GitHub Pro、Team 或 Enterprise 帳戶

**檢查方法**：
1. 儲存庫首頁右上角查看是否顯示 "Public" 或 "Private"
2. 如果是 Private 且沒有 Pro 帳戶，需要：
   - 升級到 Pro 帳戶，或
   - 將儲存庫改為 Public

**將儲存庫改為 Public**：
```
Settings → Danger Zone → Change visibility → Make public
```

### 方案 3: 更新 Workflow（已修復）

我已經更新了 workflow 檔案，新增了 `enablement: true` 參數：

```yaml
- name: Setup Pages
  uses: actions/configure-pages@v4
  with:
    enablement: true  # 自動啟用 Pages
```

### 方案 4: 配置 Repository Settings

確保 Actions 有正確的權限：

1. 進入 **Settings** → **Actions** → **General**
2. 找到 **Workflow permissions**
3. 選擇: ✅ **Read and write permissions**
4. 勾選: ✅ **Allow GitHub Actions to create and approve pull requests**
5. 儲存

### 方案 5: 手動觸發 Workflow

有時首次執行需要手動觸發：

1. 進入儲存庫的 **Actions** 標籤
2. 選擇 "Deploy Codelabs to GitHub Pages" workflow
3. 點擊 **Run workflow** 按鈕
4. 選擇 `main` 分支
5. 點擊 **Run workflow**

---

## 🔄 完整操作流程（推薦）

### 步驟 1: 推送更新的 Workflow

```bash
git add .github/workflows/deploy-codelabs.yml
git commit -m "fix: enable GitHub Pages in workflow"
git push origin main
```

### 步驟 2: 啟用 GitHub Pages

1. GitHub 儲存庫 → **Settings** → **Pages**
2. **Source** 選擇: **GitHub Actions**
3. 等待幾秒，頁面會顯示：
   ```
   Your site is ready to be published at https://使用者名稱.github.io/儲存庫名稱/
   ```

### 步驟 3: 配置 Actions 權限

1. **Settings** → **Actions** → **General**
2. **Workflow permissions**: **Read and write permissions**
3. 儲存

### 步驟 4: 重新執行 Workflow

由於之前失敗了，需要重新執行：

#### 選項 A: 推送一個空提交（觸發重新建置）
```bash
git commit --allow-empty -m "chore: trigger workflow"
git push origin main
```

#### 選項 B: 手動執行
1. GitHub 儲存庫 → **Actions**
2. 選擇失敗的 workflow run
3. 點擊右上角 **Re-run all jobs**

### 步驟 5: 驗證部署

1. 等待 workflow 完成（綠色 ✅）
2. 存取: `https://你的使用者名稱.github.io/o11y_lab_for_dummies/`
3. 應該能看到教學首頁

---

## 🎯 快速檢查清單

完成以下所有項目：

- [ ] 儲存庫是 Public（或有 Pro 帳戶）
- [ ] Settings → Pages → Source: **GitHub Actions**
- [ ] Settings → Actions → Workflow permissions: **Read and write**
- [ ] Workflow 檔案包含 `enablement: true`
- [ ] 已推送最新的 workflow 檔案
- [ ] 已重新執行失敗的 workflow
- [ ] Workflow 執行成功（綠色 ✅）
- [ ] 可以存取 `https://使用者名稱.github.io/儲存庫名稱/`

---

## 🔍 其他常見錯誤

### 錯誤 2: Permission denied

**錯誤訊息**：
```
Error: Resource not accessible by integration
```

**解決**：
確保 Workflow permissions 設定為 "Read and write permissions"

### 錯誤 3: 404 Not Found

**原因**: 部署成功但存取不到

**解決**：
1. 確認 URL 正確: `https://使用者名稱.github.io/儲存庫名稱/`（注意儲存庫名稱）
2. 等待 5-10 分鐘（首次部署可能較慢）
3. 清除瀏覽器快取或使用隱私模式

### 錯誤 4: 樣式遺失

**原因**: 路徑問題

**解決**：
檢查生成的 HTML 檔案中的資源路徑

---

## 🧪 測試部署

### 1. 本機測試

在推送之前，先本機測試：

```bash
cd codelabs

# 測試生成過程
./claat export -o generated tutorials/*.md

# 啟動本機伺服器
./serve.sh

# 存取 http://localhost:8000
# 確認一切正常後再推送
```

### 2. 檢查 Actions 日誌

如果還是失敗，查看詳細日誌：

1. GitHub 儲存庫 → **Actions**
2. 點擊失敗的 workflow run
3. 點擊 **build** 或 **deploy** job
4. 查看每個步驟的詳細輸出
5. 複製錯誤訊息進行搜尋或提問

---

## 📸 配置截圖參考

### GitHub Pages 設定（正確配置）

```
Settings → Pages

┌─────────────────────────────────────────┐
│ Build and deployment                    │
│                                         │
│ Source                                  │
│ ┌─────────────────────┐                │
│ │ GitHub Actions    ▼ │  ← 選擇這個！  │
│ └─────────────────────┘                │
│                                         │
│ Visit site                              │
│ Your site is live at                    │
│ https://user.github.io/repo/            │
└─────────────────────────────────────────┘
```

### Actions 權限設定（正確配置）

```
Settings → Actions → General

┌─────────────────────────────────────────┐
│ Workflow permissions                    │
│                                         │
│ ◉ Read and write permissions  ← 選這個  │
│ ○ Read repository contents and         │
│   packages permissions                  │
│                                         │
│ ☑ Allow GitHub Actions to create and   │
│   approve pull requests      ← 勾選這個 │
│                                         │
│ [ Save ]                                │
└─────────────────────────────────────────┘
```

---

## 🆘 還是不行？

### 除錯步驟

1. **確認基本資訊**：
   ```bash
   # 確認儲存庫資訊
   git remote -v

   # 確認目前分支
   git branch --show-current

   # 確認最新提交已推送
   git status
   ```

2. **檢查檔案是否存在**：
   ```bash
   # 確認 workflow 檔案存在
   ls -la .github/workflows/deploy-codelabs.yml

   # 確認教學檔案存在
   ls -la codelabs/tutorials/
   ls -la codelabs/generated/
   ```

3. **查看完整的 workflow 內容**：
   ```bash
   cat .github/workflows/deploy-codelabs.yml
   ```

4. **驗證 YAML 格式**：
   使用線上工具驗證 YAML 格式是否正確：
   https://www.yamllint.com/

### 取得協助

如果以上方法都不行，請提供：

1. 你的儲存庫是 Public 還是 Private？
2. Settings → Pages 目前的配置截圖
3. Actions 失敗日誌的完整截圖
4. 你的 GitHub 帳戶類型（Free/Pro/Team）

---

## ✅ 驗證部署成功

部署成功的標誌：

1. **Actions 頁面**：
   - Workflow run 顯示綠色 ✅
   - "Deploy to GitHub Pages" 步驟成功

2. **Pages 設定**：
   - 顯示 "Your site is live at..."
   - 有存取連結

3. **存取網站**：
   - 可以開啟 `https://使用者名稱.github.io/儲存庫名稱/`
   - 顯示教學首頁
   - 點擊「開始學習」可以進入教學

4. **測試功能**：
   - 導覽正常
   - 樣式正確
   - 圖片載入（如果已新增）
   - 行動裝置顯示正常

---

## 🎓 相關資源

- [GitHub Pages 官方文件](https://docs.github.com/en/pages)
- [GitHub Actions 文件](https://docs.github.com/en/actions)
- [configure-pages Action](https://github.com/actions/configure-pages)
- [deploy-pages Action](https://github.com/actions/deploy-pages)

---

祝你部署成功！如果還有問題，歡迎繼續提問。🚀
