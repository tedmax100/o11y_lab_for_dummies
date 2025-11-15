# OpenTelemetry Observability Lab for Dummies

這是一個完整的 OpenTelemetry 可觀測性實驗室，展示如何使用 OpenTelemetry 實現 **Logs、Metrics、Traces 三者的關聯**。

## 架構概覽

```
API Gateway → Service A → Service D
              ↓         ↓
         Third-Party  Service B → Message Queue → Service C
              ↓
          Database (PostgreSQL)
```

## 技術堆疊

### 可觀測性元件

- **OpenTelemetry Collector**: 統一收集和匯出遙測資料
- **OpenTelemetry Operator**: Kubernetes 自動注入 (auto-instrumentation)
- **Grafana**: 統一視覺化 Dashboard
- **Loki**: 日誌儲存和查詢
- **Prometheus**: Metrics 儲存和查詢
- **Tempo**: 分散式追蹤儲存和查詢

### 服務元件

- **API Gateway**: Python/FastAPI - 請求入口
- **Service A**: Python/FastAPI - 混合監測範例 (OpenTelemetry Operator)
- **Service D**: Python/Flask - 自動監測範例
- **Service B**: Go + Gin - 手動監測範例
- **Service C**: Go + Gin - 手動監測範例
- **PostgreSQL**: 資料庫
- **Kafka**: 訊息佇列

## 核心特性

### 1. Context Propagation (情境傳播)

所有服務間的呼叫都會傳播 Trace Context，確保整個請求鏈路可追蹤。

### 2. 三大支柱關聯

- **Trace ID** 關聯所有相關的 logs 和 spans
- **Span ID** 精確定位日誌產生的位置
- **Service Name** 和 **Resource Attributes** 關聯 metrics

### 3. 兩種監測方式

- **自動監測**: Service A/D 使用 OpenTelemetry Operator 或 SDK 自動監測
- **手動監測**: Service B/C 展示如何手動新增 spans、metrics 和結構化日誌

## 📚 互動式教學

我們提供了基於 Google Codelabs 格式的**互動式實作教學**！

### 🚀 啟動教學

```bash
cd codelabs
./serve.sh
```

然後存取: **http://localhost:8000**

### 🌐 線上存取

教學已部署到 GitHub Pages：https://tedmax100.github.io/o11y_lab_for_dummies/

教學涵蓋：

- ✅ 環境搭建（Docker、Python、Go、K6）
- ✅ Grafana 平台使用
- ✅ K6 負載測試
- ✅ Pumba 混沌工程
- ✅ Python 自動和手動監測
- ✅ 分散式追蹤、日誌、指標關聯

詳細說明請查看 [codelabs/README.md](codelabs/README.md)

---

## 快速開始

### 前置要求

- Docker & Docker Compose
- kubectl (選用)
- Go 1.21+ (開發用)
- Python 3.11+ (開發用)

### 使用 Docker Compose (推薦入門)

```bash
# 啟動所有服務
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 存取服務
# API Gateway: http://localhost:8080
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

## 目錄結構

```
.
├── services/                    # 微服務程式碼
│   ├── api-gateway/            # API 閘道器 (Python/FastAPI)
│   ├── service-a/              # Service A (Python - Auto Instrument)
│   ├── service-b/              # Service B (Go - Manual Instrument)
│   ├── service-c/              # Service C (Go - Manual Instrument)
│   └── service-d/              # Service D (Python - Auto Instrument)
├── otel-collector/             # OpenTelemetry Collector 配置
│   └── config.yaml
├── grafana/                    # Grafana 配置
│   ├── datasources/            # 資料來源配置
│   ├── dashboards/             # Dashboard JSON
│   └── provisioning/           # 自動配置
├── docker-compose.yaml         # Docker Compose 配置
└── README.md                   # 本文件
```

## 實驗場景

### 場景 1: 追蹤完整請求鏈路

```bash
curl http://localhost:8080/api/process
```

在 Grafana 中查看：

1. Tempo: 查看完整的 trace
2. Loki: 透過 trace_id 篩選相關日誌
3. Prometheus: 查看各服務的 metrics

### 場景 2: 日誌關聯追蹤

在 Grafana Explore 中：

```
{service_name="service-a"} | json | trace_id="xxx"
```

### 場景 3: Metrics 告警關聯

當 Service A 延遲過高時：

1. Prometheus 觸發告警
2. 透過 service_name 查找 traces
3. 透過 trace_id 查找相關 logs

## 學習要點

### 1. Context Propagation

- 查看各服務如何透過 HTTP Headers 傳播 trace context
- 理解 W3C Trace Context 標準

### 2. 自動監測 vs 手動監測

- Service A/D: 零程式碼侵入的自動監測
- Service B/C: 按業務所需，精細控制的手動監測

### 3. 結構化日誌

- 所有日誌都包含 trace_id、span_id、service_name
- 使用 JSON 格式便於解析和查詢

### 4. Semantic Conventions

- 遵循 OpenTelemetry 語義約定
- 統一的 attribute 命名

## 常見問題

### Q: 為什麼需要 OpenTelemetry Collector?

A: Collector 作為中間層可以：

- 統一資料收集和匯出
- 減少服務對後端系統的相依性
- 提供資料處理和採樣能力

### Q: Auto-instrument 和 Manual instrument 如何選擇?

A:

- Auto-instrument: 快速開始，覆蓋常見框架
- Manual instrument: 業務邏輯埋點，自訂 metrics

### Q: 如何確保 logs/traces/metrics 關聯?

A: 關鍵在於：

1. 統一的 Resource Attributes (service.name, etc.)
2. 在日誌中注入 trace_id 和 span_id
3. 使用同一個 OpenTelemetry SDK/Agent

## 參考資料

- [OpenTelemetry 官方文件](https://opentelemetry.io/docs/)
- [OpenTelemetry Operator](https://github.com/open-telemetry/opentelemetry-operator)
- [Grafana Tempo](https://grafana.com/docs/tempo/)
- [Grafana Loki](https://grafana.com/docs/loki/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)

## License

MIT
