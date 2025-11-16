# K6 負載測試快速開始

## 🚀 最簡單的使用方式（推薦）

使用 Makefile 命令，**完全不需要安裝 K6**！

```bash
# 1️⃣ 查看所有測試選項
make k6-help

# 2️⃣ 快速驗證系統（1分鐘）
make k6-smoke

# 3️⃣ 標準負載測試（3.5分鐘）
make k6-load

# 4️⃣ 突發流量測試（4分鐘）
make k6-spike

# 5️⃣ 壓力極限測試（6分鐘，可選）
make k6-stress
```

## 📊 在 Grafana 中觀察測試結果

### 步驟 1: 開啟 Grafana
```bash
# 在瀏覽器中打開
http://localhost:3000
```

### 步驟 2: 執行測試並觀察
```bash
# 終端 1: 執行測試
make k6-load

# 終端 2: 查看即時日誌（可選）
docker compose logs -f api-gateway service-a
```

### 步驟 3: 在 Grafana Explore 中查看

**查看 Metrics (指標)**:
1. 點擊左側的 **Explore** 圖示
2. 選擇資料來源: **Prometheus**
3. 輸入查詢:
   ```promql
   rate(http_server_requests_seconds_count[1m])
   ```

**查看 Traces (追蹤)**:
1. 切換資料來源為: **Tempo**
2. 選擇 **Search** 標籤
3. 選擇 Service: `api-gateway`
4. 點擊任一 Trace 查看詳情

**查看 Logs (日誌)**:
1. 切換資料來源為: **Loki**
2. 輸入查詢:
   ```logql
   {container_name=~"api-gateway|service-a"}
   ```

## 🎯 推薦的測試流程

```bash
# 1. 確保服務已啟動
make start
make status

# 2. 煙霧測試 - 驗證基本功能
make k6-smoke
# ✅ 確認所有檢查通過

# 3. 負載測試 - 測試正常負載
make k6-load
# 📊 在 Grafana 中觀察 metrics 和 traces

# 4. 尖峰測試 - 測試突發流量（可選）
make k6-spike
# 👀 觀察系統如何應對和恢復

# 5. 壓力測試 - 找出極限（可選）
make k6-stress
# ⚠️  可能導致系統資源耗盡
```

## 🔧 進階用法

### 自訂 API Gateway URL
```bash
make k6-load BASE_URL=http://your-gateway:8080
```

### 結合混沌工程
```bash
# 終端 1: 持續負載
make k6-load

# 終端 2: 注入網路延遲
make chaos-network-delay

# 在 Grafana 中觀察系統在故障下的表現
```

### 清理測試結果
```bash
make k6-clean
```

## 💡 測試結果解讀

測試完成後，終端會顯示摘要：

```
📊 測試結果摘要
==================================================

總請求數: 1250
平均響應時間: 156.23 ms
P95 響應時間: 425.67 ms
P99 響應時間: 892.34 ms
請求失敗率: 0.24%

==================================================
```

**關鍵指標**：
- **http_req_duration**: 請求響應時間
  - `avg`: 平均值
  - `p(95)`: 95% 的請求完成時間
  - `p(99)`: 99% 的請求完成時間
- **http_req_failed**: 請求失敗率
- **checks**: 檢查項目通過率

## ❓ 常見問題

### Q: 不需要安裝 K6 嗎？
A: 是的！使用 `make k6-*` 命令會自動使用 Docker 運行 K6，完全不需要本地安裝。

### Q: 如何停止正在運行的測試？
A: 按 `Ctrl+C` 即可停止測試。

### Q: 測試結果保存在哪裡？
A: 終端會顯示詳細結果。部分測試會生成 JSON 報告到 `k6/` 目錄。

### Q: 可以同時運行多個測試嗎？
A: 不建議。同時運行會互相影響測試結果，建議按順序執行。

### Q: 為什麼測試失敗率很高？
A: 檢查以下項目：
1. 服務是否正常運行：`make status`
2. 資源是否充足：`docker stats`
3. 在 Grafana Loki 中查看錯誤日誌

## 📚 更多資訊

- 完整文檔: [k6/README.md](README.md)
- Codelab 教程: [../codelabs/tutorials/observability-lab.md](../codelabs/tutorials/observability-lab.md)
- 專案 README: [../README.md](../README.md)

---

**快速測試一下**：
```bash
make start && sleep 30 && make k6-smoke
```

🎉 開始探索可觀測性的世界！
