#!/usr/bin/env bash
# ==============================================================================
# Chapter 5 Live Demo: Prometheus Remote Write 串接與 Git Commit Tag 綁定
# ==============================================================================
# 
# 核心教學亮點：
# 1. 解除壓測孤島：將 k6 壓測指標直接以時序數據 (Time-series) 即時推送到 Prometheus。
# 2. Commit Tag 綁定追蹤：
#    - 加上 --tag commit_id=$(git rev-parse --short HEAD)
#    - 在 Grafana 上可精準篩選特定發布版本或 PR 分支的壓測數據。
# 3. Native Histogram：
#    - K6_FEATURES=native-histograms 讓 Trend 指標以 Prometheus native histogram 推送，
#      Grafana 用 histogram_quantile() 算出真正的 P95，而不是把多條序列的 P95 再平均。
# 4. 前置依賴：
#    - 本 Lab Docker Compose 中的 Prometheus 已啟用 --web.enable-remote-write-receiver
#      與 --enable-feature=native-histograms（缺少後者時 remote write 會回 HTTP 500）。
#    - 接收端點：http://localhost:9090/api/v1/write
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_SCRIPT="${SCRIPT_DIR}/ch3_quality_gates_exit99.js"

# 取得目前 Git Commit ID 與分支名稱
COMMIT_ID=$(git rev-parse --short HEAD 2>/dev/null || echo "demo-rev1")
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
PROMETHEUS_URL="${K6_PROMETHEUS_RW_SERVER_URL:-http://localhost:9090/api/v1/write}"

echo "=========================================================="
echo "🚀 啟動 k6 Prometheus Remote Write 串流推播"
echo "📡 目標 Prometheus: ${PROMETHEUS_URL}"
echo "🏷️  注入標籤: commit_id=${COMMIT_ID}, git_branch=${BRANCH_NAME}"
echo "=========================================================="

# 執行 k6 並以 Prometheus Remote Write 輸出
K6_PROMETHEUS_RW_SERVER_URL="${PROMETHEUS_URL}" \
K6_FEATURES=native-histograms \
k6 run \
  -o experimental-prometheus-rw \
  --tag "commit_id=${COMMIT_ID}" \
  --tag "git_branch=${BRANCH_NAME}" \
  --tag "environment=lab" \
  "${TARGET_SCRIPT}"

echo "=========================================================="
echo "✅ 推播完成！請開啟 Grafana (http://localhost:3000)"
echo "   查詢 P95 例如：histogram_quantile(0.95, sum(rate(k6_http_req_duration_seconds{commit_id=\"${COMMIT_ID}\"}[1m])))"
echo "=========================================================="
