# HTTP 錯誤模擬指南

## 📊 目的

本指南說明如何使用 Pumba 混沌工程工具來模擬不同的 HTTP 錯誤，以便在 Grafana Error Rate Panel 中觀察錯誤率。

---

## 🎯 HTTP 錯誤類型與模擬方式

### 5xx 錯誤（服務端錯誤）✅ Pumba 可以模擬

| HTTP 狀態碼 | 錯誤類型 | 產生原因 | Pumba 模擬方式 |
|------------|---------|---------|---------------|
| **503** | Service Unavailable | 服務無法處理請求 | 殺死目標服務 |
| **504** | Gateway Timeout | 上游服務超時 | 注入極端網路延遲 |
| **500** | Internal Server Error | 服務內部錯誤 | 破壞資料庫/依賴服務 |

### 4xx 錯誤（客戶端錯誤）❌ Pumba 難以直接模擬

| HTTP 狀態碼 | 錯誤類型 | 產生原因 |
|------------|---------|---------|
| **400** | Bad Request | 請求參數錯誤 |
| **401** | Unauthorized | 未授權 |
| **403** | Forbidden | 禁止訪問 |
| **404** | Not Found | 資源不存在 |

**為什麼 Pumba 無法直接模擬 4xx？**
- 4xx 錯誤是應用邏輯層面的問題
- Pumba 是基礎設施層面的混沌工具
- 需要修改應用程式碼或發送錯誤請求才能產生 4xx

---

## 🚀 使用方式

### 方式一：模擬特定錯誤類型

#### 1. 模擬 503 Service Unavailable

```bash
# 終端 1: 執行負載測試
make k6-load

# 終端 2: 注入 503 錯誤
make chaos-503-errors
```

**工作原理**：
- 每 15 秒殺死 Service D 一次
- Service A 調用 Service D 時會失敗
- API Gateway 返回 503 錯誤給客戶端

**預期結果**：
- Error Rate Panel 顯示 503 錯誤
- 請求失敗率上升

---

#### 2. 模擬 504 Gateway Timeout

```bash
# 終端 1: 執行負載測試
make k6-load

# 終端 2: 注入 504 錯誤
make chaos-504-errors
```

**工作原理**：
- 給 Service A 注入 35 秒延遲
- API Gateway 等待超時（通常 30 秒）
- 返回 504 Gateway Timeout

**預期結果**：
- Error Rate Panel 顯示超時錯誤
- 響應時間大幅增加

---

#### 3. 模擬 500 Internal Server Error

```bash
# 終端 1: 執行負載測試
make k6-load

# 終端 2: 注入 500 錯誤
make chaos-500-errors
```

**工作原理**：
- 每 45 秒暫停 PostgreSQL 30 秒
- Service A 資料庫查詢失敗
- 返回 500 Internal Server Error

**預期結果**：
- Error Rate Panel 顯示 500 錯誤
- 日誌中看到資料庫連接錯誤

---

#### 4. 模擬級聯錯誤（混合錯誤）

```bash
# 終端 1: 執行負載測試
make k6-load

# 終端 2: 注入級聯錯誤
make chaos-cascading-errors
```

**工作原理**：
- Service D: 70% 封包遺失（間歇性失敗）
- Service B: 5 秒延遲（可能超時）
- PostgreSQL: CPU 壓力（查詢變慢）

**預期結果**：
- Error Rate Panel 顯示混合錯誤類型
- 系統整體性能下降

---

### 方式二：結合 K6 負載測試

**推薦測試流程**：

```bash
# Step 1: 建立基準線（無混沌）
make k6-load
# 觀察正常情況下的 Error Rate（應該接近 0%）

# Step 2: 注入 503 錯誤
make chaos-503-errors
make k6-load
# 觀察 Error Rate 上升

# Step 3: 停止混沌
make chaos-stop

# Step 4: 等待系統恢復
sleep 30

# Step 5: 注入 500 錯誤
make chaos-500-errors
make k6-load
# 觀察不同的錯誤模式

# Step 6: 清理
make chaos-stop
```

---

## 📊 在 Grafana 中觀察錯誤

### 1. Error Rate Panel

1. 打開 Grafana: http://localhost:3000
2. 導航到預配置的 Dashboard
3. 查看 "Error Rate" Panel

**Panel 查詢範例**：
```promql
# 5xx 錯誤率
sum(rate(http_server_requests_seconds_count{status=~"5.."}[1m]))
/
sum(rate(http_server_requests_seconds_count[1m]))

# 4xx 錯誤率
sum(rate(http_server_requests_seconds_count{status=~"4.."}[1m]))
/
sum(rate(http_server_requests_seconds_count[1m]))
```

### 2. 在 Explore 中詳細分析

**查看錯誤日誌**：
```logql
# 查看所有錯誤
{container_name=~"api-gateway|service-a"} |= "ERROR"

# 查看特定錯誤碼
{container_name=~"api-gateway|service-a"} |= "503"
```

**查看錯誤的 Traces**：
1. 切換到 Tempo
2. 搜索失敗的 traces
3. 分析錯誤發生的位置

---

## ❓ 常見問題

### Q1: 為什麼我看到 4xx 錯誤率有值？

**可能原因**：

1. **健康檢查失敗**
   ```bash
   # 查看健康檢查日誌
   docker compose logs api-gateway | grep health
   ```

2. **服務啟動期間的探測失敗**
   - 服務重啟時的暫時性錯誤
   - Docker 健康檢查失敗

3. **K6 測試期間的錯誤**
   - 某些測試請求參數不正確
   - 檢查 K6 測試腳本的 checks

4. **依賴服務未就緒**
   ```bash
   # 檢查所有服務狀態
   make status
   docker compose ps
   ```

**如何調查**：

```bash
# 1. 查看最近的 4xx 錯誤
docker compose logs --tail=100 | grep "4[0-9][0-9]"

# 2. 查看 API Gateway 的訪問日誌
docker compose logs api-gateway | grep -E "GET|POST" | tail -50

# 3. 檢查是否有服務重啟
docker compose ps -a

# 4. 查看 Prometheus metrics
curl http://localhost:9090/api/v1/query?query=http_server_requests_seconds_count
```

---

### Q2: 如何只看到純粹的應用錯誤（排除健康檢查）？

**方法 1：在 Prometheus 查詢中過濾**：
```promql
# 排除健康檢查的錯誤
sum(rate(http_server_requests_seconds_count{
  status=~"4..|5..",
  uri!~"/health"
}[1m]))
```

**方法 2：修改應用程式**：
- 在健康檢查端點不記錄錯誤
- 或使用不同的 metrics 標籤

---

### Q3: Pumba 模擬的錯誤會持續多久？

**持續時間**：
- `chaos-503-errors`: 持續直到手動停止
- `chaos-504-errors`: 5 分鐘
- `chaos-500-errors`: 持續直到手動停止
- `chaos-cascading-errors`: 5 分鐘

**停止方式**：
```bash
# 停止所有 Pumba 容器
make chaos-stop

# 查看當前運行的混沌測試
docker ps --filter "name=pumba-*"
```

---

### Q4: 如何模擬特定的錯誤率（例如 5% 錯誤率）？

Pumba 不支援精確的錯誤率控制，但可以通過調整參數接近目標：

**方法 1：調整殺死服務的頻率**：
```bash
# 更低頻率 = 更低錯誤率
docker run -d --name pumba-low-error-rate \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gaiaadm/pumba:latest \
  --interval 60s \  # 每 60 秒而非 15 秒
  kill --signal SIGKILL service-d
```

**方法 2：使用封包遺失率**：
```bash
# 10% 封包遺失 ≈ 10% 錯誤率（間歇性）
docker run -d --name pumba-10-percent-error \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gaiaadm/pumba:latest \
  netem --duration 5m --tc-image ghcr.io/alexei-led/pumba-alpine-nettools:latest \
  loss --percent 10 service-d
```

---

## 🎓 最佳實踐

### 1. 測試前建立基準線

```bash
# 先觀察正常情況
make k6-smoke
# 記錄正常的 Error Rate（應該接近 0%）
```

### 2. 一次只測試一種錯誤

```bash
# ❌ 不建議
make chaos-503-errors
make chaos-504-errors  # 同時運行

# ✅ 建議
make chaos-503-errors
# 觀察和分析
make chaos-stop
# 等待恢復
make chaos-504-errors
```

### 3. 結合日誌和 Traces 分析

```bash
# 終端 1: 運行測試
make k6-load

# 終端 2: 注入錯誤
make chaos-503-errors

# 終端 3: 即時查看日誌
docker compose logs -f api-gateway service-a | grep -E "ERROR|5[0-9]{2}"
```

### 4. 記錄測試結果

在 Grafana 中：
1. 截圖 Error Rate Panel
2. 導出相關的 Traces
3. 保存查詢的日誌

---

## 📚 相關命令速查

```bash
# 查看所有混沌測試命令
make chaos-help

# HTTP 錯誤模擬
make chaos-503-errors        # 503 Service Unavailable
make chaos-504-errors        # 504 Gateway Timeout
make chaos-500-errors        # 500 Internal Server Error
make chaos-cascading-errors  # 混合錯誤

# 管理命令
make chaos-stop              # 停止所有混沌測試
make chaos-clean             # 清理混沌容器
make chaos-status            # 查看混沌容器狀態

# K6 測試
make k6-load                 # 負載測試
make k6-smoke                # 煙霧測試
```

---

## 🔗 相關資源

- [Pumba 官方文檔](https://github.com/alexei-led/pumba)
- [HTTP 狀態碼說明](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [Grafana Prometheus 查詢](https://prometheus.io/docs/prometheus/latest/querying/basics/)
