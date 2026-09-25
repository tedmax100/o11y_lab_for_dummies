#!/usr/bin/env bash
# ==============================================================================
# 錄影 / 現場 Demo 預檢腳本 (Recording Preflight)
# ==============================================================================
#
# 用途：開錄前 5 分鐘跑一次，確認每章 Live Demo 的相依服務都在、腳本的 Exit Code
#       與逐字稿講的一致。任何一項 FAIL 就先別按錄影鍵。
#
# 用法：
#   ./k6/demos/preflight.sh              # 全部章節：環境檢查 + 實際跑一次 demo
#   ./k6/demos/preflight.sh ch2 ch3      # 只檢查指定章節
#   ./k6/demos/preflight.sh --check-only # 只檢查環境與相依服務，不跑 k6
#
# 可覆寫的環境變數：
#   EXPECTED_K6_VERSION  預期的 k6 版本前綴 (預設 v2.2)，與投影片 / codelab 截圖一致
#   BASE_URL_CH1         Ch1 目標 (預設 http://localhost:8080，需 docker compose up)
#   PROM_URL             Prometheus (預設 http://localhost:9090)
#   GRAFANA_URL          Grafana (預設 http://localhost:3000)
#
# Demo 產出的 summary.json / HTML 報表都寫到暫存目錄，不會弄髒專案。
# ==============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPECTED_K6_VERSION="${EXPECTED_K6_VERSION:-v2.2}"
BASE_URL_CH1="${BASE_URL_CH1:-http://localhost:8080}"
PROM_URL="${PROM_URL:-http://localhost:9090}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
QUICKPIZZA_URL="https://quickpizza.grafana.com"
ASTRONOMY_URL="https://appenvdev.field-eng-demo.grafana.net"

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/k6-preflight.XXXXXX")"
LOG_DIR="${WORK_DIR}/logs"
mkdir -p "${LOG_DIR}"

CHECK_ONLY=false
CHAPTERS=()
for arg in "$@"; do
  case "${arg}" in
    --check-only) CHECK_ONLY=true ;;
    ch[1-6]) CHAPTERS+=("${arg}") ;;
    -h|--help) sed -n '2,22p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "未知參數：${arg}"; exit 2 ;;
  esac
done
[[ ${#CHAPTERS[@]} -eq 0 ]] && CHAPTERS=(ch1 ch2 ch3 ch4 ch5 ch6)

if [[ -t 1 ]]; then
  GREEN=$'\e[32m'; YELLOW=$'\e[33m'; RED=$'\e[31m'; BOLD=$'\e[1m'; RESET=$'\e[0m'
else
  GREEN=''; YELLOW=''; RED=''; BOLD=''; RESET=''
fi

PASS_COUNT=0; WARN_COUNT=0; FAIL_COUNT=0
RUN_IDX=0; LAST_LOG=""
RESULTS=()

record() { # record <PASS|WARN|FAIL> <項目> <說明>
  local status="$1" item="$2" note="$3" color
  case "${status}" in
    PASS) color="${GREEN}"; PASS_COUNT=$((PASS_COUNT + 1)) ;;
    WARN) color="${YELLOW}"; WARN_COUNT=$((WARN_COUNT + 1)) ;;
    FAIL) color="${RED}"; FAIL_COUNT=$((FAIL_COUNT + 1)) ;;
  esac
  printf '  %s%-4s%s  %-42s %s\n' "${color}" "${status}" "${RESET}" "${item}" "${note}"
  RESULTS+=("${status}|${item}|${note}")
}

section() { printf '\n%s== %s ==%s\n' "${BOLD}" "$1" "${RESET}"; }

http_code() { curl -s -m "${2:-5}" -o /dev/null -w '%{http_code}' "$1" 2>/dev/null; }

check_http() { # check_http <項目> <url> <FAIL|WARN> [修復提示]
  local code
  code="$(http_code "$2")"
  if [[ "${code}" =~ ^[23] ]]; then
    record PASS "$1" "HTTP ${code}"
  else
    record "$3" "$1" "HTTP ${code} ← ${4:-無法連線}"
  fi
}

# run_demo <項目> <預期 exit code> <指令...>
# 在暫存目錄執行，計時並比對 exit code
run_demo() {
  local item="$1" expected="$2"; shift 2
  RUN_IDX=$((RUN_IDX + 1))
  local log="${LOG_DIR}/$(printf '%02d' "${RUN_IDX}").log"
  LAST_LOG="${log}"
  printf '# %s\n# %s\n\n' "${item}" "$*" >"${log}"
  if ${CHECK_ONLY}; then
    printf '  %-4s  %-42s %s\n' "SKIP" "${item}" "(--check-only)"
    return
  fi
  local start end rc
  start=$(date +%s)
  (cd "${WORK_DIR}" && "$@") >>"${log}" 2>&1
  rc=$?
  end=$(date +%s)
  if [[ "${rc}" == "${expected}" ]]; then
    record PASS "${item}" "exit ${rc}，耗時 $((end - start))s"
  else
    record FAIL "${item}" "exit ${rc} (預期 ${expected}) → ${log}"
  fi
}

# ------------------------------------------------------------------------------
section "共通環境"
# ------------------------------------------------------------------------------
if command -v k6 >/dev/null; then
  K6_VER="$(k6 version 2>/dev/null | awk '{print $2}')"
  if [[ "${K6_VER}" == ${EXPECTED_K6_VERSION}* ]]; then
    record PASS "k6 版本" "${K6_VER}"
  else
    record WARN "k6 版本" "${K6_VER} ≠ 預期 ${EXPECTED_K6_VERSION}.x (畫面輸出可能與投影片不同)"
  fi
else
  record FAIL "k6 版本" "找不到 k6，請先安裝"
fi
check_http "外網：QuickPizza" "${QUICKPIZZA_URL}/api/quotes" FAIL "Ch2~Ch6 都依賴它，請檢查網路"

need_ch() { [[ " ${CHAPTERS[*]} " == *" $1 "* ]]; }

# ------------------------------------------------------------------------------
if need_ch ch1; then
  section "Ch1：生命週期與 check()"
  check_http "api-gateway ${BASE_URL_CH1}/health" "${BASE_URL_CH1}/health" FAIL "請先 docker compose up -d"
  run_demo "ch1_lifecycle_and_checks.js" 0 \
    env BASE_URL="${BASE_URL_CH1}" k6 run "${SCRIPT_DIR}/ch1_lifecycle_and_checks.js"
fi

# ------------------------------------------------------------------------------
if need_ch ch2; then
  section "Ch2：流量建模"
  run_demo "ch2 閉環模型 (MODEL=closed)" 0 \
    k6 run -e MODEL=closed "${SCRIPT_DIR}/ch2_closed_vs_open_model.js"
  run_demo "ch2 開放模型 (MODEL=open)" 0 \
    k6 run -e MODEL=open "${SCRIPT_DIR}/ch2_closed_vs_open_model.js"
  if ! ${CHECK_ONLY}; then
    dropped="$(grep -E '^\s*dropped_iterations\.' "${LAST_LOG}" 2>/dev/null | awk '{print $2}')"
    if [[ -z "${dropped}" || "${dropped}" == "0" ]]; then
      record PASS "ch2 開放模型 dropped_iterations" "${dropped:-0} (Slide 預期 = 0)"
    else
      record WARN "ch2 開放模型 dropped_iterations" "${dropped} ← QuickPizza 延遲偏高，對比效果會打折"
    fi
  fi
  run_demo "ch2 delay/3 過載 (預期 Exit 99)" 99 \
    k6 run -e MODEL=open -e TARGET_URL="${QUICKPIZZA_URL}/api/delay/3" "${SCRIPT_DIR}/ch2_closed_vs_open_model.js"
  run_demo "ch2_shared_array.js" 0 k6 run "${SCRIPT_DIR}/ch2_shared_array.js"
fi

# ------------------------------------------------------------------------------
if need_ch ch3; then
  section "Ch3：Quality Gates"
  run_demo "ch3 正常門檻 (預期通過)" 0 k6 run "${SCRIPT_DIR}/ch3_quality_gates_exit99.js"
  run_demo "ch3 FAIL_SLO=true (預期 Exit 99)" 99 \
    k6 run -e FAIL_SLO=true "${SCRIPT_DIR}/ch3_quality_gates_exit99.js"
  run_demo "ch3 ABORT_TEST=true 熔斷 (預期 Exit 99)" 99 \
    k6 run -e ABORT_TEST=true "${SCRIPT_DIR}/ch3_quality_gates_exit99.js"
fi

# ------------------------------------------------------------------------------
if need_ch ch4; then
  section "Ch4：Browser 與混合壓測"
  if [[ -n "${K6_BROWSER_EXECUTABLE_PATH:-}" && -x "${K6_BROWSER_EXECUTABLE_PATH}" ]]; then
    record PASS "Chromium 執行檔" "${K6_BROWSER_EXECUTABLE_PATH}"
  elif BROWSER_BIN="$(command -v chromium chromium-browser google-chrome google-chrome-stable 2>/dev/null | head -1)"; [[ -n "${BROWSER_BIN}" ]]; then
    record PASS "Chromium 執行檔" "${BROWSER_BIN}"
  else
    record FAIL "Chromium 執行檔" "找不到 Chrome/Chromium，k6/browser 無法啟動"
  fi
  [[ -f "${SCRIPT_DIR}/recording.har" ]] \
    && record PASS "recording.har (HAR 轉譯素材)" "存在" \
    || record FAIL "recording.har (HAR 轉譯素材)" "檔案遺失"
  run_demo "recording_cleaned.js (HAR 清理後)" 0 k6 run "${SCRIPT_DIR}/recording_cleaned.js"
  # 第一次啟動 Chromium 較慢，這一輪同時當作暖機
  run_demo "ch4_browser_quickpizza.js (兼暖機)" 0 k6 run "${SCRIPT_DIR}/ch4_browser_quickpizza.js"
  run_demo "ch4_hybrid_99_to_1.js" 0 k6 run "${SCRIPT_DIR}/ch4_hybrid_99_to_1.js"
fi

# ------------------------------------------------------------------------------
if need_ch ch5; then
  section "Ch5：可觀測性與 xk6"
  if (exec 3<>/dev/tcp/127.0.0.1/5665) 2>/dev/null; then
    record FAIL "Port 5665 (Web Dashboard)" "已被佔用，Dashboard 會啟動失敗"
  else
    record PASS "Port 5665 (Web Dashboard)" "可用"
  fi
  check_http "jslib.k6.io (textSummary)" "https://jslib.k6.io/k6-summary/0.0.2/index.js" FAIL
  check_http "Prometheus ${PROM_URL}" "${PROM_URL}/-/ready" FAIL "請先 docker compose up -d"
  # Remote Write receiver 開啟時，空 POST 會回 400/415；沒開則回 404
  rw_code="$(curl -s -m 5 -o /dev/null -w '%{http_code}' -X POST "${PROM_URL}/api/v1/write" 2>/dev/null)"
  if [[ "${rw_code}" == "404" || "${rw_code}" == "000" ]]; then
    record FAIL "Prometheus Remote Write receiver" "HTTP ${rw_code} ← 需 --web.enable-remote-write-receiver"
  else
    record PASS "Prometheus Remote Write receiver" "已啟用 (HTTP ${rw_code})"
  fi
  # ch5_prometheus_remote_write.sh 以 native histogram 推送 Trend；Prometheus 沒開這個 feature 會回 HTTP 500
  prom_features="$(curl -s -m 5 "${PROM_URL}/api/v1/status/flags" 2>/dev/null | grep -o '"enable-feature":"[^"]*"')"
  if [[ "${prom_features}" == *native-histograms* ]]; then
    record PASS "Prometheus native histograms" "已啟用"
  else
    record FAIL "Prometheus native histograms" "未啟用 ← 需 --enable-feature=native-histograms（docker compose up -d prometheus 重建）"
  fi
  check_http "Grafana ${GRAFANA_URL}" "${GRAFANA_URL}/api/health" FAIL "請先 docker compose up -d"
  if command -v docker >/dev/null && docker info >/dev/null 2>&1; then
    record PASS "Docker daemon" "運作中"
    if docker image inspect grafana/xk6 >/dev/null 2>&1; then
      record PASS "grafana/xk6 映像檔" "已快取"
    else
      record WARN "grafana/xk6 映像檔" "未快取 ← 錄影前先 docker pull grafana/xk6"
    fi
  else
    record FAIL "Docker daemon" "無法連線"
  fi
  if [[ -x "$(pwd)/bin/k6-custom" ]]; then
    record PASS "預先編譯的 bin/k6-custom" "可直接展示結果，不必現場等編譯"
  else
    record WARN "預先編譯的 bin/k6-custom" "尚未編譯 ← 錄影前先跑一次 ch5_xk6_docker_build.sh"
  fi
  run_demo "ch5_dashboard_and_html_summary.js" 0 \
    env K6_WEB_DASHBOARD=true K6_WEB_DASHBOARD_EXPORT="${WORK_DIR}/k6_test_report.html" \
    k6 run "${SCRIPT_DIR}/ch5_dashboard_and_html_summary.js"
  if ! ${CHECK_ONLY}; then
    for f in summary.json custom_report.html k6_test_report.html; do
      [[ -s "${WORK_DIR}/${f}" ]] \
        && record PASS "ch5 產出 ${f}" "OK" \
        || record FAIL "ch5 產出 ${f}" "沒有產生"
    done
  fi
  # Prometheus 沒起來時 k6 只會印 error 但仍 exit 0，所以要先擋掉
  if [[ "$(http_code "${PROM_URL}/-/ready")" =~ ^2 ]]; then
    run_demo "ch5_prometheus_remote_write.sh" 0 "${SCRIPT_DIR}/ch5_prometheus_remote_write.sh"
    if ! ${CHECK_ONLY} && grep -q "Failed to send the time series" "${LAST_LOG}"; then
      record FAIL "ch5 Remote Write 推送" "k6 有送出失敗紀錄 → ${LAST_LOG}"
    fi
  else
    record FAIL "ch5_prometheus_remote_write.sh" "略過：Prometheus 未就緒"
  fi
fi

# ------------------------------------------------------------------------------
if need_ch ch6; then
  section "Ch6：k6 x agent"
  if k6 x agent --help >/dev/null 2>&1; then
    record PASS "k6 x agent 子命令" "可用"
  else
    record FAIL "k6 x agent 子命令" "無法載入 (首次需下載擴充，請先手動跑一次)"
  fi
  if k6 x mcp --help >/dev/null 2>&1; then
    record PASS "k6 x mcp 子命令" "可用"
  else
    record FAIL "k6 x mcp 子命令" "無法載入"
  fi
  # --dry-run 只列出會寫入的檔案，不動磁碟；在暫存目錄跑，確保 init 流程本身正常
  run_demo "k6 x agent init cursor --dry-run" 0 k6 x agent init cursor --dry-run
  check_http "Astronomy Shop 測試環境" "${ASTRONOMY_URL}" WARN "外部 demo 環境，掛掉就改播預錄片段"
  run_demo "ch6_quickpizza_smoke_agent.js" 0 k6 run "${SCRIPT_DIR}/ch6_quickpizza_smoke_agent.js"
  run_demo "ch6_otel_astronomy_shop.js" 0 k6 run "${SCRIPT_DIR}/ch6_otel_astronomy_shop.js"
fi

# ------------------------------------------------------------------------------
section "總結"
printf '  %sPASS %d%s   %sWARN %d%s   %sFAIL %d%s\n' \
  "${GREEN}" "${PASS_COUNT}" "${RESET}" "${YELLOW}" "${WARN_COUNT}" "${RESET}" "${RED}" "${FAIL_COUNT}" "${RESET}"
printf '  完整 k6 輸出：%s\n' "${LOG_DIR}"

if [[ ${FAIL_COUNT} -gt 0 ]]; then
  printf '\n%s✋ 有 FAIL 項目，先修好再開錄（或改用預錄 Demo 片段）。%s\n' "${RED}" "${RESET}"
  exit 1
fi
printf '\n%s🎬 全部就緒，可以開錄！%s\n' "${GREEN}" "${RESET}"
