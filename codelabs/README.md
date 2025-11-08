# OpenTelemetry 可觀測性實驗室 - Codelabs 教學

這是一個基於 Google Codelabs 格式的互動式教學平台，幫助你學習 OpenTelemetry 和可觀測性技術。

## 快速開始

### 1. 啟動教學伺服器

```bash
cd codelabs
./serve.sh
```

預設在連接埠 8000 啟動，或者指定連接埠：

```bash
./serve.sh 9000
```

### 2. 存取教學

在瀏覽器中開啟：
- **首頁**: http://localhost:8000
- **完整教學**: http://localhost:8000/o11y-lab-tutorial/

## 新增螢幕截圖

教學中有一些佔位符圖片需要替換為實際螢幕截圖：

### 需要的螢幕截圖清單

1. **grafana-home.png** - Grafana 首頁介面
2. **grafana-datasources.png** - 資料來源配置頁面
3. **grafana-dashboards.png** - Dashboard 清單
4. **k6-traffic.png** - K6 生成流量後的 Grafana 圖表
5. **pumba-delay.png** - 注入延遲後的效能影響圖表
6. **auto-trace.png** - 自動埋點生成的 Trace 範例
7. **manual-trace.png** - 手動埋點的 Trace 範例
8. **correlated-dashboard.png** - Logs/Traces/Metrics 關聯的 Dashboard

### 如何新增螢幕截圖

1. 按照教學操作，在相應步驟截圖
2. 將螢幕截圖儲存到對應位置：

```bash
# 螢幕截圖儲存位置
codelabs/tutorials/assets/images/

# 或者在生成後的教學中替換
codelabs/generated/o11y-lab-tutorial/img/
```

3. 重新生成教學（如果修改了 Markdown）：

```bash
cd codelabs
./claat export -o generated tutorials/observability-lab.md
```

## 目錄結構

```
codelabs/
├── tutorials/              # Markdown 格式的教學原始檔案
│   ├── observability-lab.md
│   └── assets/
│       └── images/        # 教學中使用的圖片
├── generated/             # 生成的 HTML 教學
│   ├── index.html         # 教學首頁
│   └── o11y-lab-tutorial/ # 生成的教學內容
├── claat                  # Codelabs 轉換工具
├── serve.sh              # 啟動 Web 伺服器腳本
└── README.md             # 本文件
```

## 建立新教學

### 1. 建立 Markdown 檔案

在 `tutorials/` 目錄下建立新的 `.md` 檔案，格式如下：

```markdown
author: 作者名
summary: 教學簡介
id: unique-tutorial-id
categories: category1,category2
environments: Web
status: Published
feedback link: https://github.com/your-repo
analytics account: Google Analytics ID

# 教學標題

## 第一步
Duration: 5

這是第一步的內容...

## 第二步
Duration: 10

這是第二步的內容...
```

### 2. 生成 HTML

```bash
./claat export -o generated tutorials/your-tutorial.md
```

### 3. 更新首頁

編輯 `generated/index.html`，新增新教學的卡片。

## Markdown 語法特性

### Duration (時長)

在每個步驟下方指定預計完成時間（分鐘）：

```markdown
## 步驟標題
Duration: 10
```

### 提示框

```markdown
Positive
: 這是一個成功/正面的提示

Negative
: 這是一個警告/負面的提示
```

### 程式碼區塊

```markdown
\`\`\`bash
# 命令範例
docker compose up -d
\`\`\`

\`\`\`python
# Python 程式碼
print("Hello World")
\`\`\`
```

### 圖片

```markdown
![圖片描述](assets/images/image-name.png)
```

### 連結

```markdown
[連結文字](https://example.com)
```

## 自訂樣式

如需自訂教學外觀，可以修改：

1. **首頁樣式**: `generated/index.html` 中的 `<style>` 部分
2. **教學樣式**: claat 生成的預設樣式在生成的 HTML 中

## 部署到生產環境

### 使用 GitHub Pages

1. 將 `generated/` 目錄內容推送到 `gh-pages` 分支
2. 在儲存庫設定中啟用 GitHub Pages

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

建立 `Dockerfile`:

```dockerfile
FROM nginx:alpine
COPY generated/ /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

建置並執行：

```bash
docker build -t o11y-codelabs .
docker run -d -p 8080:80 o11y-codelabs
```

## 工具說明

### claat (Codelabs As A Thing)

這是 Google 開發的工具，用於將 Markdown 轉換為 Codelabs HTML 格式。

- **官方儲存庫**: https://github.com/googlecodelabs/tools
- **文件**: https://github.com/googlecodelabs/tools/blob/main/claat/README.md

### 常用命令

```bash
# 匯出為 HTML
./claat export tutorials/your-tutorial.md

# 預覽（啟動開發伺服器）
./claat serve

# 更新已存在的教學
./claat update o11y-lab-tutorial

# 查看版本
./claat version
```

## 故障排除

### 圖片無法顯示

檢查圖片路徑是否正確：
- Markdown 中: `assets/images/image.png`
- 生成後: `img/image.png`

### 樣式異常

清除瀏覽器快取或使用隱私模式重新存取。

### 連接埠被佔用

修改啟動腳本中的連接埠：

```bash
./serve.sh 9000
```

## 貢獻

歡迎提交新教學或改進現有教學！

1. Fork 本專案
2. 建立新的 Markdown 教學
3. 生成 HTML 並測試
4. 提交 Pull Request

## 授權條款

MIT License

## 參考資源

- [Google Codelabs 官方文件](https://github.com/googlecodelabs/tools)
- [Markdown 語法指南](https://www.markdownguide.org/)
- [OpenTelemetry 官方文件](https://opentelemetry.io/docs/)
