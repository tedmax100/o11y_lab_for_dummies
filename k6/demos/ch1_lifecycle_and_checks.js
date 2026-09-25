/**
 * Chapter 1 Live Demo: k6 四階段生命週期與宣告式斷言 (Lifecycle & Checks)
 * 
 * 演示要點：
 * 1. 四階段生命週期執行順序：Init -> setup() -> default (VU code) -> teardown()
 * 2. 宣告式軟斷言：check() 不會中斷測試，僅記錄 Rate 指標
 * 3. 邏輯交易分組：group() 建立階層式壓測維度
 * 4. 避免高基數 (Cardinality) 爆炸：使用 http.url 或 tags 聚合動態 URL
 * 
 * 目標服務：Grafana 公開的 QuickPizza (https://quickpizza.grafana.com)，不需啟動本機環境。
 * 要打其他環境時用 -e BASE_URL=... 覆寫。
 *
 * 執行指令：
 * k6 run k6/demos/ch1_lifecycle_and_checks.js
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';

// ----------------------------------------------------
// 1. Init Context (每個 VU 初始化時執行一次，不可發送 HTTP 請求)
// ----------------------------------------------------
console.log(`[Init] VU ${__VU} 初始化腳本與載入設定...`);

export const options = {
  vus: 2,
  iterations: 4, // 總共跑 4 次 iteration，方便在終端機觀察生命週期
  thresholds: {
    // 基本門檻：確認請求成功率與延遲
    http_req_failed: ['rate<0.05'], // 失敗率小於 5%
    http_req_duration: ['p(95)<1000'], // 95% 請求在 1 秒內
    checks: ['rate>0.9'], // check() 成功率大於 90%
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://quickpizza.grafana.com';

// ----------------------------------------------------
// 2. Setup Context (全域執行一次，通常用於準備測試資料或取得 Auth Token)
// ----------------------------------------------------
export function setup() {
  console.log('>>> [Setup] 正在準備全域測試環境...');
  
  // 準備全域狀態：QuickPizza 公開的示範 token，查詢披薩 API 需要帶上它
  const authToken = 'abcdef0123456789';
  return { token: authToken, startedAt: new Date().toISOString() };
}

// ----------------------------------------------------
// 3. VU Code (Default function，每個 VU 每個 iteration 反覆執行)
// ----------------------------------------------------
export default function (data) {
  // data 參數由 setup() 回傳
  const iteration = __ITER;
  const vuId = __VU;

  group('01_健康檢查交易', () => {
    // 使用 tags 標籤避免動態 URL 造成基數爆炸
    const res = http.get(`${BASE_URL}/healthz`, {
      tags: { name: 'health_check' },
    });

    // check() 軟斷言演示：即便失敗也不會中斷測試
    const isOk = check(res, {
      '健康檢查狀態碼為 200': (r) => r.status === 200,
    });

    if (!isOk) {
      console.warn(`[VU ${vuId} Iter ${iteration}] 健康檢查軟斷言未通過，但腳本繼續執行`);
    }
  });

  group('02_核心業務流程', () => {
    // 模擬動態路由標籤化 (解決 /api/pizza/1, /api/pizza/42 的高基數問題)
    const pizzaId = Math.floor(Math.random() * 100) + 1;
    const url = http.url`${BASE_URL}/api/pizza/${pizzaId}`;

    const headers = {
      'Authorization': `token ${data.token}`,
      'Content-Type': 'application/json',
    };

    const res = http.get(url, {
      headers: headers,
      tags: { name: 'get_pizza' },
    });

    // 除了狀態碼，也驗證 Response Body 內容
    check(res, {
      '查詢披薩狀態碼為 200': (r) => r.status === 200,
      '回應的披薩 id 與請求一致': (r) => r.json('id') === pizzaId,
    });
  });

  sleep(0.5); // 模擬真實使用者思考時間 (Pacing / Think Time)
}

// ----------------------------------------------------
// 4. Teardown Context (全域執行一次，清理環境或寄送測試摘要)
// ----------------------------------------------------
export function teardown(data) {
  console.log(`<<< [Teardown] 壓測完成！測試始於：${data.startedAt}，清理暫存狀態...`);
}
