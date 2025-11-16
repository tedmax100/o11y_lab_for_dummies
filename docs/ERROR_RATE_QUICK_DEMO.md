# Error Rate 快速演示

## 🎯 5 分鐘快速演示如何產生和觀察 HTTP 錯誤

### 準備工作

```bash
# 1. 確保服務正在運行
make start
make status

# 2. 打開 Grafana
# 瀏覽器訪問: http://localhost:3000
# 導航到 Dashboard 找到 "Error Rate" Panel
```

---

## 演示 1: 觀察 503 錯誤 (2 分鐘)

### 終端操作

```bash
# 終端 1: 執行負載測試
make k6-load

# 終端 2: 注入 503 錯誤（在測試運行 30 秒後）
make chaos-503-errors
```

### 在 Grafana 中觀察

1. **Error Rate Panel** 應該顯示：
   - 5xx 錯誤率開始上升
   - 可能達到 50% 或更高（因為 Service D 不斷被殺死）

2. **切換到 Explore → Loki**:
   ```logql
   {container_name="api-gateway"} |= "503"
   ```
   應該看到大量 503 錯誤日誌

3. **切換到 Explore → Tempo**:
   - 搜索失敗的 traces
   - 查看哪個服務調用失敗了

### 停止測試

```bash
make chaos-stop
```

---

## 演示 2: 觀察 500 錯誤 (2 分鐘)

### 終端操作

```bash
# 終端 1: 執行負載測試
make k6-load

# 終端 2: 注入 500 錯誤
make chaos-500-errors
```

### 在 Grafana 中觀察

1. **Error Rate Panel** 應該顯示：
   - 週期性的錯誤尖峰（每 45 秒一次）
   - 當資料庫暫停時錯誤率飆升

2. **查看日誌**:
   ```logql
   {container_name="service-a"} |= "database"
   ```
   應該看到資料庫連接錯誤

### 停止測試

```bash
make chaos-stop
```

---

## 演示 3: 級聯錯誤（混合模式）(3 分鐘)

### 終端操作

```bash
# 終端 1: 執行負載測試
make k6-load

# 終端 2: 注入級聯錯誤
make chaos-cascading-errors

# 終端 3: 即時查看日誌
docker compose logs -f api-gateway service-a | grep -E "ERROR|error"
```

### 在 Grafana 中觀察

1. **Error Rate Panel** 應該顯示：
   - 混合的錯誤類型
   - 不規則的錯誤模式
   - 整體錯誤率較高

2. **響應時間增加**:
   - 因為多個服務同時受到影響

### 停止測試

```bash
make chaos-stop
```

---

## 📊 關於 4xx 錯誤的說明

### 為什麼你可能看到 4xx 錯誤？

#### 1. 健康檢查 404（最常見）

```bash
# 查看健康檢查日誌
docker compose logs api-gateway | grep health | tail -20
```

如果服務啟動時健康檢查端點還未就緒，可能返回 404。

#### 2. 服務重啟期間

```bash
# 查看服務重啟次數
docker compose ps -a
```

服務重啟時的短暫 404 或 503。

#### 3. 排除健康檢查的錯誤

在 Grafana Prometheus 查詢中過濾：

```promql
# 只看非健康檢查的 4xx 錯誤
sum(rate(http_server_requests_seconds_count{
  status=~"4..",
  uri!~"/health"
}[1m]))
```

---

## 🎓 完整測試流程

```bash
# Step 1: 建立基準線
make k6-smoke
# 記錄正常的 Error Rate

# Step 2: 測試 503 錯誤
make chaos-503-errors
make k6-load
# 在 Grafana 觀察
make chaos-stop

# Step 3: 等待恢復
sleep 30

# Step 4: 測試 500 錯誤
make chaos-500-errors
make k6-load
# 在 Grafana 觀察
make chaos-stop

# Step 5: 測試級聯錯誤
make chaos-cascading-errors
make k6-load
# 在 Grafana 觀察
make chaos-stop
```

---

## 🔍 調查 4xx 錯誤的步驟

```bash
# 1. 查看最近的 4xx 錯誤
docker compose logs --tail=200 | grep "4[0-9][0-9]"

# 2. 查看是哪個端點產生的
docker compose logs api-gateway | grep -E "GET|POST" | grep "4[0-9][0-9]"

# 3. 檢查是否是健康檢查
docker compose logs | grep -E "health|4[0-9][0-9]" | tail -50

# 4. 查看服務狀態
docker compose ps

# 5. 在 Grafana Loki 中查詢
# {container_name=~".*"} |= "4" | json | status=~"4.."
```

---

## 💡 提示

1. **測試前先打開 Grafana**
   這樣可以即時看到錯誤率的變化

2. **使用多個終端**
   - 終端 1: K6 測試
   - 終端 2: Pumba 混沌
   - 終端 3: 日誌監控

3. **記錄測試結果**
   在 Grafana 中截圖保存

4. **測試後清理**
   ```bash
   make chaos-stop
   make chaos-clean
   ```

---

## 📚 相關命令

```bash
# 混沌測試
make chaos-help              # 查看所有選項
make chaos-503-errors        # 503 錯誤
make chaos-504-errors        # 504 超時
make chaos-500-errors        # 500 錯誤
make chaos-cascading-errors  # 級聯錯誤
make chaos-stop              # 停止混沌
make chaos-status            # 查看狀態

# K6 測試
make k6-help                 # 查看所有選項
make k6-smoke                # 煙霧測試
make k6-load                 # 負載測試

# 服務管理
make status                  # 查看服務狀態
make logs                    # 查看日誌
```
