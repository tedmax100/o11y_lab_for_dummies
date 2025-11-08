# 🚀 快速開始 - 5 分鐘啟動教學平台

## 第一步：啟動教學伺服器

```bash
cd codelabs
./serve.sh
```

你會看到：

```
================================================
OpenTelemetry 可觀測性實驗室教學伺服器
================================================

啟動 HTTP 伺服器在連接埠: 8000

存取教學：
  首頁: http://localhost:8000
  教學: http://localhost:8000/o11y-lab-tutorial/

按 Ctrl+C 停止伺服器
================================================
```

## 第二步：開啟瀏覽器

存取: **http://localhost:8000**

你會看到一個漂亮的教學首頁，點擊「開始學習」按鈕即可開始！

## 第三步（選用）：新增螢幕截圖

目前教學使用的是佔位符圖片。按照以下步驟新增實際螢幕截圖：

### 簡化版（推薦新手）

1. 按照教學操作每一步
2. 在關鍵介面截圖
3. 將螢幕截圖儲存到 `tutorials/assets/images/` 目錄
4. 重新生成 HTML:
   ```bash
   ./claat export -o generated tutorials/observability-lab.md
   ```
5. 重新整理瀏覽器

### 詳細指南

查看 `SCREENSHOTS_GUIDE.md` 取得詳細的螢幕截圖指南，包括：
- 每個螢幕截圖的具體要求
- 螢幕截圖工具推薦
- 最佳化和壓縮方法
- 故障排除

## 目錄導覽

```
codelabs/
├── 📖 README.md              # 完整文件
├── 🚀 QUICKSTART.md          # 本文件 - 快速開始
├── 📸 SCREENSHOTS_GUIDE.md   # 螢幕截圖新增指南
├── 🛠️ serve.sh               # 啟動腳本
├── 🔧 claat                   # 轉換工具
├── tutorials/                 # 教學原始檔案
│   └── observability-lab.md  # 主教學（Markdown）
└── generated/                 # 生成的網站
    ├── index.html            # 首頁
    └── o11y-lab-tutorial/    # 教學 HTML
```

## 常見問題

### Q: 連接埠 8000 被佔用？

```bash
./serve.sh 9000  # 使用其他連接埠
```

### Q: 如何修改教學內容？

1. 編輯 `tutorials/observability-lab.md`
2. 重新生成:
   ```bash
   ./claat export -o generated tutorials/observability-lab.md
   ```
3. 重新整理瀏覽器

### Q: 如何新增新教學？

1. 在 `tutorials/` 建立新的 `.md` 檔案
2. 使用相同的格式和後設資料
3. 生成 HTML:
   ```bash
   ./claat export -o generated tutorials/新教學.md
   ```
4. 編輯 `generated/index.html` 新增新教學卡片

### Q: 可以部署到線上嗎？

可以！`generated/` 目錄是純靜態 HTML，可以部署到：
- GitHub Pages
- Netlify
- Vercel
- 任何靜態網站託管服務

簡單方法：
```bash
# 使用 GitHub Pages
git add codelabs/generated/
git commit -m "Add codelabs tutorials"
git subtree push --prefix codelabs/generated origin gh-pages
```

## 下一步

1. ✅ 啟動教學伺服器
2. ✅ 在瀏覽器中瀏覽教學
3. 📝 按照教學操作實驗室環境
4. 📸 在操作過程中截圖
5. 🔄 更新教學中的螢幕截圖
6. 🌍 （選用）部署到線上供他人使用

## 需要協助？

- 查看 `README.md` 取得完整文件
- 查看 `SCREENSHOTS_GUIDE.md` 了解如何新增螢幕截圖
- 查看 [Google Codelabs 官方文件](https://github.com/googlecodelabs/tools)

祝你學習愉快！🎉
