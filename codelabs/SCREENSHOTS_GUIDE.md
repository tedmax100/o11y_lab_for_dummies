# 螢幕截圖新增指南

本指南將協助你為教學新增實際的螢幕截圖，以替換目前的佔位符圖片。

## 需要的螢幕截圖清單

### 1. Grafana 首頁 (grafana-home.png)

**何時截圖**: 完成「存取 Grafana 平台」步驟後

**操作步驟**:
1. 啟動所有服務: `docker compose up -d`
2. 存取 http://localhost:3000
3. 使用 admin/admin 登入
4. 在首頁截圖，包含左側選單列和主面板

**截圖要點**:
- 顯示完整的 Grafana 介面
- 確保左側選單清晰可見
- 包含頂部導覽列

---

### 2. 資料來源配置 (grafana-datasources.png)

**何時截圖**: 在 Grafana 首頁登入後

**操作步驟**:
1. 點擊左側齒輪圖示 (Configuration)
2. 選擇 "Data sources"
3. 截圖顯示已配置的資料來源清單

**截圖要點**:
- 顯示 Prometheus、Loki、Tempo 三個資料來源
- 每個資料來源應顯示為 "working" 狀態
- 包含資料來源類型和名稱

---

### 3. Dashboard 清單 (grafana-dashboards.png)

**何時截圖**: 查看預先配置的 Dashboard

**操作步驟**:
1. 點擊左側 Dashboard 圖示
2. 顯示所有可用的 Dashboard
3. 截圖

**截圖要點**:
- 顯示預先配置的 Dashboard 清單
- 包含 Dashboard 名稱和標籤

---

### 4. K6 流量圖表 (k6-traffic.png)

**何時截圖**: K6 測試執行期間

**操作步驟**:
1. 執行 K6 測試:
   ```bash
   k6 run k6/load-test.js
   ```
2. 在 Grafana Explore 中:
   - 選擇 Prometheus 資料來源
   - 查詢: `rate(http_requests_total[1m])`
   - 點擊 "Run query"
3. 等待資料顯示後截圖

**截圖要點**:
- 顯示請求速率的時間序列圖表
- 圖表應顯示明顯的流量增長
- 包含查詢語句和時間範圍選擇器

---

### 5. Pumba 延遲效果 (pumba-delay.png)

**何時截圖**: 注入延遲並觀察影響

**操作步驟**:
1. 啟動 K6 持續流量:
   ```bash
   k6 run --duration 5m k6/load-test.js &
   ```
2. 注入延遲:
   ```bash
   pumba netem --duration 2m delay --time 500 o11y_lab_for_dummies-service-a-1
   ```
3. 在 Grafana 中查詢 P95 延遲:
   ```promql
   histogram_quantile(0.95,
     rate(http_server_duration_milliseconds_bucket[1m])
   )
   ```
4. 截圖顯示延遲注入前後的變化

**截圖要點**:
- 圖表應顯示明顯的延遲增加（從 ~100ms 到 ~600ms）
- 包含時間範圍，顯示注入前後的對比
- 標註出延遲注入的時間點

---

### 6. 自動埋點 Trace (auto-trace.png)

**何時截圖**: 查看自動生成的 Trace

**操作步驟**:
1. 觸發請求:
   ```bash
   curl http://localhost:8080/api/process
   ```
2. 在 Grafana Explore 中:
   - 選擇 Tempo 資料來源
   - 選擇 Service: service-a
   - 點擊 "Run query"
3. 點擊任意 trace 查看詳情
4. 截圖顯示 span 樹狀結構

**截圖要點**:
- 顯示完整的 trace waterfall 視圖
- 清晰顯示自動生成的 spans（HTTP、資料庫等）
- 包含 span 的時間和屬性資訊

---

### 7. 手動埋點 Trace (manual-trace.png)

**何時截圖**: 查看包含手動埋點的 Trace

**操作步驟**:
1. 觸發請求到 service-d
2. 在 Tempo 中搜尋 service-d 的 traces
3. 找到包含自訂 span 的 trace（如 "business_logic"）
4. 截圖顯示自訂的 span 和屬性

**截圖要點**:
- 顯示自訂的 span 名稱（如 business_logic）
- 展開 span 顯示自訂屬性（user.id, request.size 等）
- 顯示 span events（如 "Processing started"）

---

### 8. 關聯 Dashboard (correlated-dashboard.png)

**何時截圖**: 展示 Logs/Traces/Metrics 的關聯

**操作步驟**:
1. 建立或開啟一個包含三者的 dashboard
2. 或者在 Explore 中使用分屏顯示：
   - 上方: Prometheus metrics
   - 中間: Tempo traces
   - 下方: Loki logs
3. 確保顯示相同時間範圍的資料
4. 截圖

**截圖要點**:
- 同時顯示 metrics、traces、logs
- 顯示它們之間的關聯（透過 trace_id）
- 展示如何從一個跳轉到另一個

---

## 螢幕截圖工具推薦

### Linux
- **Flameshot**: `sudo apt install flameshot`
- **GNOME Screenshot**: 系統內建
- **Spectacle** (KDE): `sudo apt install spectacle`

### MacOS
- **系統截圖**: Cmd + Shift + 4
- **CleanShot X**: 付費但功能強大

### Windows
- **Snipping Tool**: 系統內建
- **Greenshot**: 免費開源
- **ShareX**: 功能豐富

## 螢幕截圖最佳實踐

1. **解析度**: 至少 1920x1080，保證清晰度
2. **格式**: PNG 格式，保證品質
3. **內容**:
   - 移除個人敏感資訊
   - 確保介面完整，不要裁剪關鍵部分
   - 包含必要的情境（如 URL、時間等）
4. **檔案大小**:
   - 盡量控制在 500KB 以內
   - 可使用 `optipng` 或 `pngquant` 壓縮
5. **命名**: 使用上述指定的檔案名稱

## 新增螢幕截圖到教學

### 方法 1: 新增到原始檔案（推薦）

1. 將螢幕截圖儲存到:
   ```
   codelabs/tutorials/assets/images/
   ```

2. 重新生成 HTML:
   ```bash
   cd codelabs
   ./claat export -o generated tutorials/observability-lab.md
   ```

### 方法 2: 直接新增到生成的教學

1. 將螢幕截圖儲存到:
   ```
   codelabs/generated/o11y-lab-tutorial/img/
   ```

2. 檔案會直接顯示在教學中

## 最佳化螢幕截圖

### 壓縮 PNG

```bash
# 安裝 optipng
sudo apt install optipng

# 壓縮單個檔案
optipng -o7 image.png

# 批次壓縮
find codelabs/tutorials/assets/images/ -name "*.png" -exec optipng -o7 {} \;
```

### 調整尺寸

```bash
# 安裝 ImageMagick
sudo apt install imagemagick

# 調整寬度為 1200px（保持比例）
convert input.png -resize 1200x output.png

# 批次調整
for img in *.png; do
  convert "$img" -resize 1200x "resized_$img"
done
```

## 範例工作流程

```bash
# 1. 截取所有需要的圖片
# 2. 儲存到 tutorials/assets/images/
cd codelabs

# 3. 最佳化圖片
optipng -o7 tutorials/assets/images/*.png

# 4. 重新生成教學
./claat export -o generated tutorials/observability-lab.md

# 5. 啟動伺服器預覽
./serve.sh

# 6. 在瀏覽器中檢查 http://localhost:8000
```

## 故障排除

### 圖片不顯示

檢查：
1. 檔案名稱是否完全符合（區分大小寫）
2. 檔案格式是否為 PNG
3. 路徑是否正確
4. 重新生成 HTML 後是否重新整理了瀏覽器快取

### 圖片太大

```bash
# 查看檔案大小
ls -lh codelabs/tutorials/assets/images/

# 如果超過 1MB，進行壓縮
pngquant --quality=65-80 image.png -o image.png
```

## 完成檢查清單

- [ ] grafana-home.png - Grafana 首頁
- [ ] grafana-datasources.png - 資料來源配置
- [ ] grafana-dashboards.png - Dashboard 清單
- [ ] k6-traffic.png - K6 流量圖表
- [ ] pumba-delay.png - 延遲注入效果
- [ ] auto-trace.png - 自動埋點 Trace
- [ ] manual-trace.png - 手動埋點 Trace
- [ ] correlated-dashboard.png - 關聯 Dashboard
- [ ] 所有圖片已最佳化壓縮
- [ ] 重新生成 HTML
- [ ] 本機預覽確認無誤

完成後，你的教學將擁有完整的視覺指導！
