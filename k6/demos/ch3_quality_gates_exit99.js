/**
 * Chapter 3 Live Demo: 品質門禁、自訂指標與 Exit Code 99 CI/CD 卡關 (Quality Gates)
 * 
 * 核心教學亮點：
 * 1. 四大自訂指標型態 (Custom Metrics)：
 *    - Counter: 累計計數器 (如：訂單成交數、退票數)
 *    - Gauge: 瞬時狀態規 (如：當前連線數、記憶體水位)
 *    - Rate: 成功率/比率 (如：業務邏輯成功率)
 *    - Trend: 統計趨勢 (如：自訂後端處理時間、資料庫查詢耗時)
 * 2. 標籤篩選與精準 SLO 門檻 (Tagged Thresholds)：
 *    - 為關鍵端點設定獨立 SLO：'http_req_duration{type:critical}': ['p(99)<200']
 * 3. 熔斷機制 (abortOnFail: true)：
 *    - 當錯誤率超過閥值時，立即中止壓測，避免無謂消耗 CI/CD 資源或把測試環境打掛。
 * 4. Exit Code 99 驗證：
 *    - 當 Threshold 未通過時，k6 自動以代碼 99 退出，讓 GitLab CI / GitHub Actions 立即判定失敗卡關！
 * 
 * 執行範例：
 * - 模擬通過情境：k6 run -e FAIL_SLO=false k6/demos/ch3_quality_gates_exit99.js
 * - 模擬卡關失敗：k6 run -e FAIL_SLO=true k6/demos/ch3_quality_gates_exit99.js ; echo "CI Exit Code: $?"
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Gauge, Rate, Trend } from 'k6/metrics';

const FAIL_SLO = __ENV.FAIL_SLO === 'true';

// ----------------------------------------------------
// 1. 定義 4 大自訂業務指標
// ----------------------------------------------------
const orderCount = new Counter('orders_submitted_total');
const activeVUGauge = new Gauge('active_workers_gauge');
const businessSuccessRate = new Rate('business_transaction_success');
const customDbTrend = new Trend('custom_db_processing_duration');

export const options = {
  vus: 3,
  iterations: 6,

  // ----------------------------------------------------
  // 2. 品質門禁 (Quality Gates / Thresholds)
  // ----------------------------------------------------
  thresholds: {
    // 全域 HTTP 指標
    'http_req_failed': ['rate<0.05'], // 系統 HTTP 錯誤率 < 5%

    // 依據標籤 (Tag) 精準過濾特定端點的 SLO
    'http_req_duration{api_type:critical}': [
      // 若 FAIL_SLO 為 true，故意設定一個不可能達成的 1ms 門檻觸發 Exit Code 99
      FAIL_SLO ? 'p(95)<1' : 'p(95)<1500',
    ],

    // 自訂指標門禁
    'business_transaction_success': [
      {
        threshold: 'rate>=0.95',
        abortOnFail: true,       // 熔斷機制：一旦失敗立即腰斬終止測試！
        delayAbortEval: '5s',    // 緩衝 5 秒再開始評估熔斷，避免冷啟動誤判
      },
    ],
    'custom_db_processing_duration': ['p(90)<500'],
  },
};

export default function () {
  // 記錄 Gauge 狀態
  activeVUGauge.add(__VU);

  // 發送請求並打上標籤
  const res = http.get('https://test.k6.io/contacts.php', {
    tags: { api_type: 'critical', feature: 'checkout' },
  });

  // 模擬自訂 Trend (如解析後端標頭或內部計時)
  const simulatedDbTime = Math.random() * 80 + 20; // 20ms ~ 100ms
  customDbTrend.add(simulatedDbTime);

  // 業務檢核與自訂指標推進
  const ok = check(res, {
    '狀態碼為 200': (r) => r.status === 200,
  });

  if (ok) {
    orderCount.add(1);
    businessSuccessRate.add(1);
  } else {
    businessSuccessRate.add(0);
  }

  sleep(0.3);
}
